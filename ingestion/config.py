"""
Data ingestion configuration.
"""
import os
from typing import Dict, Any

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# Database configuration (reuse existing config)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'smart_industrial_estate'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

# Simulator settings
SIMULATOR_CONFIG: Dict[str, Any] = {
    'interval_seconds': int(os.getenv('SIM_INTERVAL', '60')),
    'batch_size': int(os.getenv('SIM_BATCH_SIZE', '10')),
    'start_date': os.getenv('SIM_START_DATE'),
    'end_date': os.getenv('SIM_END_DATE'),
    'window_days': int(os.getenv('SIM_WINDOW_DAYS', '7')),
    'num_sensors': int(os.getenv('SIM_NUM_SENSORS', '50'))
}