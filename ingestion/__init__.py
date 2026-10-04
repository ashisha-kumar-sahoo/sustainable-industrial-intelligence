"""
Data + Ingestion - M2 Module

This module provides data ingestion capabilities for the Sustainable Industrial Intelligence platform:
- Sensor data simulation
- Data validation and cleaning
- Loading to PostgreSQL database (reusing existing config/database.py)

Usage:
    python -m ingestion.sensor_simulator
    python ingestion/load_to_postgres.py --file data/raw/synthetic_readings.json
"""
__version__ = '1.0.0'
