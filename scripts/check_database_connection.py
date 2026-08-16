from app.database import get_database_connection


with get_database_connection() as connection:
    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT current_database(), current_user;"
        )

        database_name, user_name = cursor.fetchone()

        print("Database connection successful.")
        print("Connected database:", database_name)
        print("Connected user:", user_name)

        cursor.execute(
            "SELECT COUNT(*) FROM prediction_logs;"
        )

        prediction_count = cursor.fetchone()[0]

        print(
            "Rows currently in prediction_logs:",
            prediction_count,
        )