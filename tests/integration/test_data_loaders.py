"""
Integration tests for the PostgreSQL data loaders.

These tests verify that the common data-loader layer can connect to the
project database and retrieve the expected domain data.

Database-dependent tests are skipped automatically when DB credentials
are not configured.
"""

import os

import pytest

from data.loaders import (
    load_air_quality_data,
    load_energy_data,
    load_environment_data,
    load_facilities,
    load_traffic_data,
    load_waste_data,
    load_water_data,
)


def database_configured() -> bool:
    """Return True when the required database password is configured."""
    return bool(os.getenv("DB_PASSWORD"))


pytestmark = pytest.mark.skipif(
    not database_configured(),
    reason="PostgreSQL test credentials are not configured",
)


def test_load_facilities():
    """Verify that facility data can be loaded."""
    data = load_facilities()

    assert not data.empty
    assert "facility_id" in data.columns


def test_load_energy_data():
    """Verify the energy loader and its expected schema."""
    data = load_energy_data()

    assert not data.empty

    expected_columns = {
        "facility_id",
        "sensor_id",
        "reading_ts",
        "energy_consumption_kwh",
    }

    assert expected_columns.issubset(data.columns)


def test_load_water_data():
    """Verify the water loader and its expected schema."""
    data = load_water_data()

    assert not data.empty

    expected_columns = {
        "facility_id",
        "sensor_id",
        "reading_ts",
        "water_consumption_liters",
        "flow_rate",
    }

    assert expected_columns.issubset(data.columns)


def test_load_waste_data():
    """Verify the waste loader and its expected schema."""
    data = load_waste_data()

    assert not data.empty

    expected_columns = {
        "facility_id",
        "sensor_id",
        "reading_ts",
        "waste_type",
        "waste_quantity_kg",
        "recyclable_quantity_kg",
        "hazardous_quantity_kg",
    }

    assert expected_columns.issubset(data.columns)


def test_load_air_quality_data():
    """Verify that air-quality data can be loaded."""
    data = load_air_quality_data()

    assert not data.empty
    assert "facility_id" in data.columns
    assert "reading_ts" in data.columns


def test_load_environment_data():
    """Verify that environmental data can be loaded."""
    data = load_environment_data()

    assert not data.empty
    assert "facility_id" in data.columns
    assert "reading_ts" in data.columns


def test_load_traffic_data():
    """Verify the traffic loader and its expected schema."""
    data = load_traffic_data()

    assert not data.empty

    expected_columns = {
        "facility_id",
        "sensor_id",
        "reading_ts",
        "vehicle_count",
        "heavy_vehicle_count",
        "average_speed_kmph",
        "congestion_level",
        "lane_occupancy_percent",
    }

    assert expected_columns.issubset(data.columns)