from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


# Find the main project folder.
project_root = Path(__file__).resolve().parents[1]

# Define all file locations.
model_path = project_root / "model" / "stats19_xgb_pipeline.pkl"
features_path = project_root / "model" / "selected_features.json"
metrics_path = project_root / "model" / "model_metrics.json"

sample_path = project_root / "data" / "X_test_demo_sample.csv"
reference_path = project_root / "data" / "test_predictions.csv"


# Load the trained pipeline.
model = joblib.load(model_path)

# Load the 42 features expected by the model.
with open(features_path, "r") as file:
    selected_features = json.load(file)

# Load the saved classification threshold.
with open(metrics_path, "r") as file:
    model_metrics = json.load(file)

threshold = model_metrics["threshold"]


# Load the sample inputs and the original saved predictions.
X_sample = pd.read_csv(sample_path)
reference_predictions = pd.read_csv(reference_path)


print("Sample rows:", len(X_sample))
print("Sample columns:", len(X_sample.columns))
print("Expected feature count:", len(selected_features))


# Check whether any expected features are missing.
missing_features = [
    feature
    for feature in selected_features
    if feature not in X_sample.columns
]

if missing_features:
    raise ValueError(
        f"The sample data is missing these features: {missing_features}"
    )


# Put the columns in exactly the same order used by the model.
X_sample = X_sample[selected_features]


# Generate probabilities using the saved pipeline.
new_probabilities = model.predict_proba(X_sample)[:, 1]

# Convert probabilities into class predictions using the saved threshold.
new_predictions = (
    new_probabilities >= threshold
).astype(int)


# Take the matching first 100 reference predictions.
reference_predictions = reference_predictions.iloc[:len(X_sample)]

saved_probabilities = reference_predictions[
    "severe_probability"
].to_numpy()

saved_predictions = reference_predictions[
    "predicted_severe"
].to_numpy()


# Compare the new results with the original saved results.
probabilities_match = np.allclose(
    new_probabilities,
    saved_probabilities,
    atol=1e-6
)

predictions_match = np.array_equal(
    new_predictions,
    saved_predictions
)

maximum_probability_difference = np.max(
    np.abs(new_probabilities - saved_probabilities)
)


# Show the first five comparisons.
comparison = pd.DataFrame(
    {
        "saved_probability": saved_probabilities[:5],
        "new_probability": new_probabilities[:5],
        "saved_prediction": saved_predictions[:5],
        "new_prediction": new_predictions[:5],
    }
)

print("\nFirst five prediction comparisons:")
print(comparison)

print("\nProbability values match:", probabilities_match)
print("Class predictions match:", predictions_match)
print(
    "Maximum probability difference:",
    maximum_probability_difference
)