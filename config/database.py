"""
Central PostgreSQL database connection for
Sustainable Industrial Intelligence.
"""

import os

from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Configuration is read from environment variables.
    """

    try:
        import psycopg2
    except ImportError as exc:
        raise RuntimeError("PostgreSQL driver is missing. Install requirements.txt first.") from exc

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "smart_industrial_estate"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )