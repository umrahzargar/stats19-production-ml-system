from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException

from app.schemas import PredictionInput, BatchPredictionRequest
from app.database import (
    get_database_connection,
    save_prediction,
    save_batch_predictions,
    get_recent_predictions,
)
 
# Project paths
  
project_root = Path(__file__).resolve().parents[1]

model_path = (
    project_root
    / "model"
    / "stats19_xgb_pipeline.pkl"
)

metrics_path = (
    project_root
    / "model"
    / "model_metrics.json"
)

features_path = (
    project_root
    / "model"
    / "selected_features.json"
)

demo_data_path = (
    project_root
    / "data"
    / "X_test_demo_sample.csv"
)
  
# Load model and project files

model = joblib.load(model_path)


with open(
    metrics_path,
    "r",
    encoding="utf-8",
) as file:
    model_metrics = json.load(file)


with open(
    features_path,
    "r",
    encoding="utf-8",
) as file:
    selected_features = json.load(file)


demo_data = pd.read_csv(demo_data_path)

demo_data = demo_data[selected_features]

classification_threshold = model_metrics["threshold"]


  
# Create FastAPI application
  

app = FastAPI(
    title="STATS19 Severity Prediction API",
    version="0.2.0",
)


  
# Basic endpoints
  

@app.get("/")
def root():
    """Display a welcome message."""

    return {
        "message": (
            "Welcome to the STATS19 "
            "Severity Prediction API"
        ),
        "documentation": "/docs",
    }


@app.get("/health")
def health_check():
    """Confirm that the API is running."""

    return {
        "status": "healthy",
        "message": "STATS19 API is running",
    }


@app.get("/model-info")
def model_info():
    """Return information about the deployed model."""

    return {
        "model_file_available": model_path.exists(),
        "model_name": model_metrics["model"],
        "classification_threshold": (
            classification_threshold
        ),
        "macro_f1": model_metrics["macro_f1"],
        "severe_recall": (
            model_metrics["severe_recall"]
        ),
        "severe_precision": (
            model_metrics["severe_precision"]
        ),
        "roc_auc": model_metrics["roc_auc"],
        "average_precision": (
            model_metrics["average_precision"]
        ),
    }


  
# Demo prediction endpoint
  

@app.get("/predict-demo/{row_number}")
def predict_demo(row_number: int):
    """
    Generate a prediction using one saved demo row.
    """

    if (
        row_number < 0
        or row_number >= len(demo_data)
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Demo row {row_number} does not exist. "
                f"Choose a number from 0 to "
                f"{len(demo_data) - 1}."
            ),
        )

    example_input = demo_data.iloc[[row_number]]

    severe_probability = (
        model.predict_proba(example_input)[0, 1]
    )

    predicted_severe = (
        severe_probability
        >= classification_threshold
    )

    return {
        "demo_row_number": row_number,
        "severe_probability": float(
            severe_probability
        ),
        "classification_threshold": (
            classification_threshold
        ),
        "predicted_severe": bool(
            predicted_severe
        ),
        "predicted_class": int(
            predicted_severe
        ),
    }


  
# Real prediction endpoint
  

@app.post("/predict")
def predict(input_data: PredictionInput):
    """
    Generate and save a severity prediction.
    """

    input_dictionary = input_data.model_dump()

    input_dataframe = pd.DataFrame(
        [input_dictionary]
    )

    input_dataframe = input_dataframe.replace(
        {None: np.nan}
    )

    input_dataframe = input_dataframe[
        selected_features
    ]

    severe_probability = (
        model.predict_proba(input_dataframe)[0, 1]
    )

    predicted_severe = (
        severe_probability
        >= classification_threshold
    )

    saved_prediction = save_prediction(
        input_data=input_dictionary,
        severe_probability=float(
            severe_probability
        ),
        predicted_class=int(
            predicted_severe
        ),
        api_version=app.version,
    )

    return {
        "prediction_id": (
            saved_prediction["prediction_id"]
        ),
        "model_version": (
            saved_prediction["model_version"]
        ),
        "severe_probability": float(
            severe_probability
        ),
        "classification_threshold": (
            classification_threshold
        ),
        "predicted_severe": bool(
            predicted_severe
        ),
        "predicted_class": int(
            predicted_severe
        ),
        "model_name": model_metrics["model"],
        "api_version": app.version,
    }



# Predict Batch

@app.post("/predict/batch")
def predict_batch(batch_request: BatchPredictionRequest):

    if len(batch_request.records) == 0:
        raise HTTPException(
            status_code=400,
            detail="Batch must contain at least one record."
        )

    # Convert Pydantic records into normal dictionaries
    input_records = [
        record.model_dump()
        for record in batch_request.records
    ]

    # Create one DataFrame containing the whole batch
    input_dataframe = pd.DataFrame(input_records)

    input_dataframe = input_dataframe.replace({None: np.nan})

    # Force the same feature order used during training
    input_dataframe = input_dataframe[selected_features]

    # ONE model call for the entire batch
    severe_probabilities = model.predict_proba(
        input_dataframe
    )[:, 1]

    predicted_classes = (
        severe_probabilities >= classification_threshold
    ).astype(int)

    # Save batch metadata + individual predictions
    saved_batch = save_batch_predictions(
        source_filename=batch_request.source_filename,
        input_records=input_records,
        severe_probabilities=severe_probabilities,
        predicted_classes=predicted_classes,
        api_version=app.version,
    )

    results = []

    for row_number, (probability, predicted_class) in enumerate(
        zip(severe_probabilities, predicted_classes)
    ):
        results.append(
            {
                "row_number": row_number,
                "severe_probability": float(probability),
                "predicted_class": int(predicted_class),
                "predicted_severe": bool(predicted_class),
            }
        )

    return {
        "batch_id": saved_batch["batch_id"],
        "source_filename": batch_request.source_filename,
        "row_count": saved_batch["row_count"],
        "model_version": saved_batch["model_version"],
        "classification_threshold": classification_threshold,
        "results": results,
    }

  
# Database endpoints
  

@app.get("/database-health")
def database_health():
    """
    Confirm that FastAPI can reach PostgreSQL.
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    current_database(),
                    current_user;
                """
            )

            database_name, user_name = (
                cursor.fetchone()
            )

    return {
        "status": "healthy",
        "database": database_name,
        "user": user_name,
    }


@app.get("/predictions/recent")
def recent_predictions(limit: int = 10):
    """
    Return recently saved predictions.
    """

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Limit must be between 1 and 100."
            ),
        )

    predictions = get_recent_predictions(
        limit
    )

    return {
        "count": len(predictions),
        "predictions": predictions,
    }