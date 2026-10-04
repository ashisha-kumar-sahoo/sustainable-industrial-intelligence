"""
Shared pytest configuration for Sustainable Industrial Intelligence.

This file provides common test configuration and fixtures that can be
used across unit and integration tests.

The project keeps test infrastructure lightweight so that individual
team modules can add their own fixtures as they are integrated.
"""

import os
import sys
from pathlib import Path

import pytest


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Make the project root importable during tests.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    """Return the absolute path to the project root."""
    return PROJECT_ROOT


@pytest.fixture
def test_environment():
    """
    Return the current test environment configuration.

    Tests should not require production credentials or modify production
    databases. Database-dependent tests should be explicitly configured
    using environment variables.
    """
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "environment": os.getenv("APP_ENV", "test"),
    }


@pytest.fixture
def sample_reading():
    """
    Provide a minimal generic sensor-style reading for unit tests.

    Domain-specific tests should create their own fixtures when they need
    fields specific to energy, water, waste, environment, traffic,
    equipment, or safety data.
    """
    return {
        "sensor_id": "TEST_SENSOR_001",
        "facility_id": "TEST_FACILITY_001",
        "value": 100.0,
    }