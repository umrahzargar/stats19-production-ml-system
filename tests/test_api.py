from pathlib import Path
import json

import pandas as pd
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app, selected_features


# Test setup

client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEMO_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "X_test_demo_sample.csv"
)


def load_demo_rows(number_of_rows=1):
    """
    Load genuine demo rows and convert them into
    JSON-compatible dictionaries.
    """

    demo_data = pd.read_csv(DEMO_DATA_PATH)

    selected_rows = (
        demo_data[selected_features]
        .head(number_of_rows)
    )

    return json.loads(
        selected_rows.to_json(orient="records")
    )


# 1. Health endpoint

def test_health_endpoint():
    """The API should report that it is healthy."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# 2. Single prediction

def test_verified_single_prediction(monkeypatch):
    """
    The API should reproduce the verified prediction
    for the first genuine demo row.
    """

    # Prevent automated tests from writing to PostgreSQL.
    def fake_save_prediction(
        input_data,
        severe_probability,
        predicted_class,
        api_version,
    ):
        return {
            "prediction_id": 999,
            "model_version": "1.0.0",
        }

    monkeypatch.setattr(
        main_module,
        "save_prediction",
        fake_save_prediction,
    )

    prediction_payload = load_demo_rows(1)[0]

    response = client.post(
        "/predict",
        json=prediction_payload,
    )

    assert response.status_code == 200

    result = response.json()

    expected_probability = 0.004024339374154806

    assert abs(
        result["severe_probability"]
        - expected_probability
    ) < 1e-8

    assert result["predicted_severe"] is False
    assert result["predicted_class"] == 0

    assert result["prediction_id"] == 999
    assert result["model_version"] == "1.0.0"


# 3. Batch prediction

def test_verified_batch_prediction(monkeypatch):
    """
    The batch endpoint should process multiple rows
    together and return one result for each row.
    """

    # Prevent automated tests from writing to PostgreSQL.
    def fake_save_batch_predictions(
        source_filename,
        input_records,
        severe_probabilities,
        predicted_classes,
        api_version,
    ):
        return {
            "batch_id": 999,
            "row_count": len(input_records),
            "model_version": "1.0.0",
        }

    monkeypatch.setattr(
        main_module,
        "save_batch_predictions",
        fake_save_batch_predictions,
    )

    records = load_demo_rows(2)

    payload = {
        "source_filename": "automated_test_batch.csv",
        "records": records,
    }

    response = client.post(
        "/predict/batch",
        json=payload,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["batch_id"] == 999
    assert result["row_count"] == 2
    assert result["source_filename"] == "automated_test_batch.csv"
    assert result["model_version"] == "1.0.0"

    assert len(result["results"]) == 2

    # First row is our previously verified example.
    expected_first_probability = 0.004024339374154806

    assert abs(
        result["results"][0]["severe_probability"]
        - expected_first_probability
    ) < 1e-8

    assert result["results"][0]["predicted_class"] == 0
    assert result["results"][0]["predicted_severe"] is False

    # Second demo row should be classified Severe.
    assert result["results"][1]["predicted_class"] == 1
    assert result["results"][1]["predicted_severe"] is True


# 4. Empty batch validation

def test_empty_batch_is_rejected():
    """
    A batch containing zero records should not
    be accepted.
    """

    payload = {
        "source_filename": "empty.csv",
        "records": [],
    }

    response = client.post(
        "/predict/batch",
        json=payload,
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Batch must contain at least one record."
    )