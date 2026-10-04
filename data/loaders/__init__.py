"""
Database data loaders for Sustainable Industrial Intelligence.

The loaders in this package provide a common interface between the
PostgreSQL data platform and the project's AI/analytics modules.
"""

from .postgres_loader import (
    load_air_quality_data,
    load_alerts,
    load_energy_data,
    load_environment_data,
    load_facilities,
    load_traffic_data,
    load_waste_data,
    load_water_data,
)

__all__ = [
    "load_air_quality_data",
    "load_alerts",
    "load_energy_data",
    "load_environment_data",
    "load_facilities",
    "load_traffic_data",
    "load_waste_data",
    "load_water_data",
]