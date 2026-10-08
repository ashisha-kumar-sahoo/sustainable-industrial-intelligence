"""
PostgreSQL data loaders for Sustainable Industrial Intelligence.

This module provides a common interface for retrieving domain data
from the project's PostgreSQL database.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine

from config.database import get_connection
import os


def _get_engine():
    """Create a SQLAlchemy engine using the project database settings."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "smart_industrial_estate")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")

    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )


def _read_query(query: str) -> pd.DataFrame:
    """Execute a read-only SQL query and return the result as a DataFrame."""
    engine = _get_engine()

    try:
        return pd.read_sql_query(query, engine)
    finally:
        engine.dispose()


def load_energy_data() -> pd.DataFrame:
    """Load energy readings from PostgreSQL."""
    query = """
        SELECT
            facility_id,
            sensor_id,
            reading_ts,
            energy_consumption_kwh
        FROM public.energy_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_water_data() -> pd.DataFrame:
    """Load water readings from PostgreSQL."""
    query = """
        SELECT
            facility_id,
            sensor_id,
            reading_ts,
            water_consumption_liters,
            flow_rate
        FROM public.water_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_waste_data() -> pd.DataFrame:
    """Load waste readings from PostgreSQL."""
    query = """
        SELECT
            facility_id,
            sensor_id,
            reading_ts,
            waste_type,
            waste_quantity_kg,
            recyclable_quantity_kg,
            hazardous_quantity_kg,
            fill_level_percent,
            fill_rate_percent_per_hour
        FROM public.waste_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_air_quality_data() -> pd.DataFrame:
    """Load air-quality readings from PostgreSQL."""
    query = """
        SELECT *
        FROM public.air_quality_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_environment_data() -> pd.DataFrame:
    """Load environmental readings from PostgreSQL."""
    query = """
        SELECT *
        FROM public.environmental_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_traffic_data() -> pd.DataFrame:
    """Load traffic readings from PostgreSQL."""
    query = """
        SELECT
            facility_id,
            sensor_id,
            reading_ts,
            vehicle_count,
            heavy_vehicle_count,
            average_speed_kmph,
            congestion_level,
            lane_occupancy_percent
        FROM public.traffic_readings
        ORDER BY reading_ts;
    """
    return _read_query(query)


def load_alerts() -> pd.DataFrame:
    """Load alerts from PostgreSQL."""
    query = """
        SELECT *
        FROM public.alerts
        ORDER BY created_at DESC;
    """
    return _read_query(query)


def load_facilities() -> pd.DataFrame:
    """Load facility information from PostgreSQL."""
    query = """
        SELECT *
        FROM public.facilities
        ORDER BY facility_id;
    """
    return _read_query(query)