import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb


# Load variables from the .env file.
load_dotenv()


def get_database_connection():
    """
    Create and return a connection to the STATS19 PostgreSQL database.
    """

    connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    return connection
def get_active_model_version():
    """
    Return the currently active model version from PostgreSQL.
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    model_version_id,
                    model_name,
                    version
                FROM model_versions
                WHERE is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )

            result = cursor.fetchone()

    if result is None:
        raise ValueError(
            "No active model version exists in the database."
        )

    return {
        "model_version_id": result[0],
        "model_name": result[1],
        "version": result[2],
    }
def save_prediction(
    input_data: dict,
    severe_probability: float,
    predicted_class: int,
    api_version: str,
):
    """
    Save one model prediction in PostgreSQL.
    """

    # Find which model version is currently active.
    active_model = get_active_model_version()

    with get_database_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO prediction_logs (
                    input_data,
                    severe_probability,
                    predicted_class,
                    api_version,
                    model_version_id
                )
                VALUES (%s, %s, %s, %s, %s)

                RETURNING prediction_id;
                """,
                (
                    Jsonb(input_data),
                    severe_probability,
                    predicted_class,
                    api_version,
                    active_model["model_version_id"],
                ),
            )

            prediction_id = cursor.fetchone()[0]

    return {
        "prediction_id": prediction_id,
        "model_version": active_model["version"],
    }

def get_recent_predictions(limit: int = 10):
    """
    Return the most recent prediction records.
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    p.prediction_id,
                    p.created_at,
                    p.severe_probability,
                    p.predicted_class,
                    m.model_name,
                    m.version
                FROM prediction_logs AS p
                JOIN model_versions AS m
                    ON p.model_version_id = m.model_version_id
                ORDER BY p.created_at DESC
                LIMIT %s;
                """,
                (limit,),
            )

            rows = cursor.fetchall()

    predictions = []

    for row in rows:
        predictions.append(
            {
                "prediction_id": row[0],
                "created_at": row[1],
                "severe_probability": row[2],
                "predicted_class": row[3],
                "model_name": row[4],
                "model_version": row[5],
            }
        )

    return predictions

def save_batch_predictions(
    source_filename,
    input_records,
    severe_probabilities,
    predicted_classes,
    api_version,
):
    row_count = len(input_records)

    if not (
        len(severe_probabilities) == row_count
        and len(predicted_classes) == row_count
    ):
        raise ValueError(
            "Batch inputs, probabilities, and predictions must have the same length."
        )

    with get_database_connection() as connection:
        with connection.cursor() as cursor:

            # 1. Find the active model
            cursor.execute(
                """
                SELECT
                    model_version_id,
                    version
                FROM model_versions
                WHERE is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )

            active_model = cursor.fetchone()

            if active_model is None:
                raise RuntimeError("No active model version found.")

            model_version_id = active_model[0]
            model_version = active_model[1]

            # 2. Create one record representing the whole batch
            cursor.execute(
                """
                INSERT INTO prediction_batches (
                    source_filename,
                    row_count,
                    model_version_id
                )
                VALUES (%s, %s, %s)
                RETURNING batch_id;
                """,
                (
                    source_filename,
                    row_count,
                    model_version_id,
                ),
            )

            batch_id = cursor.fetchone()[0]

            # 3. Prepare every individual prediction
            prediction_rows = []

            for record, probability, predicted_class in zip(
                input_records,
                severe_probabilities,
                predicted_classes,
            ):
                prediction_rows.append(
                    (
                        Jsonb(record),
                        float(probability),
                        int(predicted_class),
                        api_version,
                        batch_id,
                        model_version_id,
                    )
                )

            # 4. Save all predictions
            cursor.executemany(
                """
                INSERT INTO prediction_logs (
                    input_data,
                    severe_probability,
                    predicted_class,
                    api_version,
                    batch_id,
                    model_version_id
                )
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                prediction_rows,
            )

    return {
        "batch_id": batch_id,
        "row_count": row_count,
        "model_version": model_version,
    }