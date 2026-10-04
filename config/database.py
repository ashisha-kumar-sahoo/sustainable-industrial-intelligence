"""
Central PostgreSQL database connection for
Sustainable Industrial Intelligence.
"""

import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Configuration is read from environment variables.
    """

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "smart_industrial_estate"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )