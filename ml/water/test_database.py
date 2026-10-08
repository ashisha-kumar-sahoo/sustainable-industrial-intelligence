from .data_loader import load_data


# ============================================================
# POSTGRESQL CONNECTION SETTINGS
# ============================================================

HOST = "localhost"
PORT = "5432"

DATABASE = "industrial_intelligence"

USER = "postgres"

PASSWORD = "YOUR_POSTGRES_PASSWORD"


# ============================================================
# SQL QUERY
# ============================================================

QUERY = """
SELECT
    facility_id,
    zone_id,
    timestamp,
    water_liters,
    flow_rate
FROM water_consumption
ORDER BY timestamp;
"""


# ============================================================
# TEST DATABASE
# ============================================================

if __name__ == "__main__":

    print("\nConnecting to PostgreSQL...")
    print("=" * 60)

    try:

        data = load_from_postgresql(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            query=QUERY
        )

        print("Database connection successful!")

        print("\nData received:")
        print("=" * 60)

        print(data.head())

        print("\nTotal records:", len(data))

    except Exception as error:

        print("\nDatabase connection failed.")

        print("Error:")
        print(error)