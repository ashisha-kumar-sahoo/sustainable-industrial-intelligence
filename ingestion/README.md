# Data Ingestion (M2)

This module handles sensor data simulation, validation, cleaning, and loading into PostgreSQL.

## Overview

The ingestion pipeline follows the database architecture (raw → etl → public):
1. **Generate** synthetic sensor data using `sensor_simulator.py`
2. **Validate** readings using `data_validator.py`
3. **Clean** readings using `data_cleaner.py`
4. **Load** into PostgreSQL using `load_to_postgres.py`

## Components

- `sensor_simulator.py` - Generate realistic synthetic readings for all domains
- `data_validator.py` - Validate data types, ranges, required fields
- `data_cleaner.py` - Clean and normalize data
- `db_connection.py` - Bridge to existing `config/database.py` connection
- `load_to_postgres.py` - Load to PostgreSQL (raw + public tables)
- `config.py` - Ingestion configuration

## Usage

### 1. Generate synthetic data
```bash
cd sustainable-industrial-intelligence
python -m ingestion.sensor_simulator
```

### 2. Validate and load
```bash
python -c "
from ingestion import sensor_simulator, data_validator, data_cleaner, load_to_postgres
sim = sensor_simulator.SensorSimulator()
readings = sim.generate_batch(20)
valid, invalid = data_validator.DataValidator().filter_valid_readings(readings)
clean = data_cleaner.DataCleaner().clean_batch(valid)
with load_to_postgres.DataLoader() as loader:
    loader.load_to_raw(clean)
    loader.load_to_public_domain(clean)
"
```

## Configuration

Set environment variables for database:
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: smart_industrial_estate)
- `DB_USER` (default: postgres)
- `DB_PASSWORD`

## Notes

- Reuses `config/database.py` (central connection) - no competing DB system
- Writes to existing schema: `raw.raw_sensor_data`, `public.*_readings`
- Does not modify or reset the existing database
- Generated data saved under `data/raw/` and can be processed to `data/processed/`
