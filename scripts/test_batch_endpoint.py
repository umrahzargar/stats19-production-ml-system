from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEMO_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "X_test_demo_sample.csv"
)

API_URL = "http://127.0.0.1:8000"


# Read only the first two demo records
demo_data = pd.read_csv(DEMO_DATA_PATH).head(2)


def make_json_safe(record):
    clean_record = {}

    for column, value in record.items():
        if pd.isna(value):
            clean_record[column] = None
        elif hasattr(value, "item"):
            clean_record[column] = value.item()
        else:
            clean_record[column] = value

    return clean_record


records = [
    make_json_safe(row)
    for row in demo_data.to_dict(orient="records")
]


payload = {
    "source_filename": "two_row_batch_test.csv",
    "records": records,
}


response = requests.post(
    f"{API_URL}/predict/batch",
    json=payload,
    timeout=30,
)


print("HTTP status:", response.status_code)
print()

if response.ok:
    result = response.json()

    print("Batch ID:", result["batch_id"])
    print("Rows processed:", result["row_count"])
    print("Model version:", result["model_version"])
    print()

    for prediction in result["results"]:
        print(prediction)

else:
    print(response.text)