from pathlib import Path

import joblib


# Find the main project folder.
project_root = Path(__file__).resolve().parents[1]

# Build the path to the saved model file.
model_path = project_root / "model" / "stats19_xgb_pipeline.pkl"

print("Looking for the model here:")
print(model_path)

# Check that the file exists before trying to open it.
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found: {model_path}")

# Load the trained pipeline.
model = joblib.load(model_path)

print("\nModel loaded successfully.")
print("Saved object type:", type(model))

# A scikit-learn pipeline normally contains named steps.
if hasattr(model, "named_steps"):
    print("Pipeline steps:", list(model.named_steps.keys()))