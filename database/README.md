# Database — Sustainable Industrial Intelligence

## Overview

This directory contains the PostgreSQL database structure and reproducible project data for the **Sustainable Industrial Intelligence** hackathon project.

The PostgreSQL database is the project's **source of truth** for facility, sensor, resource, environmental, traffic, alert, ETL, and summary data.

## Database

- **Database name:** `smart_industrial_estate`
- **Database system:** PostgreSQL 18.6
- **Application schema:** `public`
- **Raw-data schema:** `raw`
- **ETL/audit schema:** `etl`

The supplied PostgreSQL dumps were generated with PostgreSQL/`pg_dump` version 18.6.

## Files

### `schema.sql`

Contains the database structure, including schemas, tables, columns, constraints, indexes, sequences/identity definitions, views, comments, and other dumpable database objects.

### `seed.sql`

Contains the existing database data used to reproduce the demonstration environment.

The supplied seed contains approximately **14.1 MB** of SQL data.

### Full backup

A separate full dump such as:

```text
schema_and_data.sql
```

contains both schema and data and should be kept as a private backup unless its contents have been reviewed and approved for sharing.

## Database Architecture

The database is organized into three logical layers:

```text
                    DATA SOURCES
             Sensors / Synthetic / Open Data
                         |
                         v
                 +---------------+
                 |      raw      |
                 | Raw sensor    |
                 | payloads      |
                 +---------------+
                         |
                         v
                 +---------------+
                 |      etl      |
                 | Validation /  |
                 | Cleaning / QA |
                 +---------------+
                         |
                         v
                 +---------------+
                 |    public     |
                 | Clean app data|
                 | & summaries   |
                 +---------------+
                         |
              +----------+----------+
              |          |          |
              v          v          v
            ML/AI     Dashboard   Alerts
```

### `raw` schema

The `raw` schema is the landing zone for sensor payloads exactly as received. New readings retain the complete JSON object in `raw_payload`; existing historical rows receive `{}` because the original incoming JSON was not stored in the old schema.

Main table:

- `raw.raw_sensor_data` — typed common fields plus `raw_payload` JSONB, which retains the complete incoming record.

### `etl` schema

The `etl` schema supports validation, cleaning, rejection/quarantine, and data-quality auditing.

Main tables:

- `etl.cleaned_sensor_data`
- `etl.data_quality_log`
- `etl.rejected_readings`

### `public` schema

The `public` schema contains clean application-facing data, views, alerts, and facility summaries used by the dashboard and AI/ML modules.

## Existing database migration workflow

For an existing local `smart_industrial_estate` database, do not rerun `schema.sql` or `seed.sql`. Back up the database first, then apply the new additive migration from the project root:

```powershell
pg_dump -U postgres -h localhost -p 5432 -d smart_industrial_estate -F c -f "$HOME\smart_industrial_estate_backup.dump"
psql -U postgres -h localhost -p 5432 -d smart_industrial_estate -v ON_ERROR_STOP=1 -f ".\database\migrations\002_add_equipment_safety_telemetry.sql"
```

Migration `002_add_equipment_safety_telemetry.sql` adds `public.equipment_readings` and `public.safety_readings`, expands allowed sensor types, preserves full raw JSON payloads, and inserts missing synthetic equipment/safety sensor registrations without deleting existing rows. Migration `001_add_waste_bin_telemetry.sql` is the earlier waste-bin telemetry migration and should only be applied if that change has not already been applied.

## Tables

### Facility and sensor management

#### `public.facilities`

Stores industrial facility information and domain thresholds.

Important fields include:

- `facility_id`
- `facility_code`
- `facility_name`
- `facility_type`
- `company_name`
- `location`
- `area_sqft`
- `status`
- `energy_threshold_kwh`
- `water_threshold_liters`
- `waste_threshold_kg`
- `aqi_threshold`
- `traffic_threshold_count`
- `sustainability_rating`

Seed data: **20 facilities**

#### `public.sensors`

Stores sensor metadata and operational status.

Important fields include:

- `sensor_id`
- `sensor_code`
- `facility_id`
- `sensor_type`
- `sensor_name`
- `unit`
- `manufacturer`
- `model`
- `installation_date`
- `status`
- `calibration_due_date`
- `last_reading_at`

Seed data: **140 sensors** before the additive equipment/safety migration. Migration 002 registers missing synthetic equipment and safety sensors per facility; it does not rewrite existing sensor identities.

### `public.equipment_readings`

Stores time-series machine telemetry used by equipment anomaly detection and inspection prioritization: equipment identifier, temperature, vibration, operating hours, utilization, and status. Rows are idempotent by `(sensor_id, reading_ts)`.

### `public.safety_readings`

Stores safety telemetry such as gas readings, smoke/fire/emergency signals, plus optional incident-context fields used by the safety risk pipeline. Simulator-provided incident labels and response times are synthetic examples, not real incident records. Rows are idempotent by `(sensor_id, reading_ts)`.

---

## Resource Intelligence Data

### `public.energy_readings`

Stores energy measurements.

Important fields:

- `reading_id`
- `sensor_id`
- `facility_id`
- `reading_ts`
- `energy_consumption_kwh`
- `voltage`
- `current`
- `power_factor`
- `peak_demand_kw`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **12,960 readings**

Supports:

- Energy monitoring
- Anomaly detection
- Forecasting
- Peak-demand analysis
- Energy optimization

### `public.water_readings`

Stores water consumption and flow measurements.

Important fields:

- `reading_id`
- `sensor_id`
- `facility_id`
- `reading_ts`
- `water_consumption_liters`
- `water_pressure`
- `water_temperature`
- `flow_rate`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **12,960 readings**

Supports:

- Water consumption monitoring
- Abnormal-usage detection
- Water alerts
- Trend analysis

### `public.waste_readings`

Stores waste-generation and disposal information.

Important fields:

- `reading_id`
- `sensor_id`
- `facility_id`
- `reading_ts`
- `waste_type`
- `waste_quantity_kg`
- `recyclable_quantity_kg`
- `hazardous_quantity_kg`
- `disposal_method`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **13,680 readings**

Supports:

- Waste monitoring
- Waste trend analysis
- Recycling/hazardous-waste analysis
- Collection and management decisions

---

## Environment and Operations Data

### `public.air_quality_readings`

Stores air-quality and pollutant readings.

Important fields:

- `reading_id`
- `sensor_id`
- `facility_id`
- `reading_ts`
- `aqi`
- `pm25`
- `pm10`
- `co`
- `co2`
- `no2`
- `so2`
- `temperature`
- `humidity`
- `aqi_category`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **12,960 readings**

The `aqi_category` field is generated from AQI values in the database.

Supports:

- AQI monitoring
- Pollution trend analysis
- Environmental anomaly detection
- Environmental hotspot analysis

### `public.environmental_readings`

Stores general environmental/weather-style measurements.

Important fields:

- `reading_id`
- `facility_id`
- `sensor_id`
- `reading_ts`
- `temperature_c`
- `humidity_percent`
- `rainfall_mm`
- `wind_speed_kmph`
- `wind_direction`
- `air_pressure_hpa`
- `solar_irradiance_wm2`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **27,360 readings**

Supports:

- Environmental monitoring
- Weather/context analysis
- Environmental trend and anomaly analysis

### `public.traffic_readings`

Stores vehicle and traffic-flow measurements.

Important fields:

- `reading_id`
- `sensor_id`
- `facility_id`
- `reading_ts`
- `vehicle_count`
- `heavy_vehicle_count`
- `average_speed_kmph`
- `congestion_level`
- `lane_occupancy_percent`
- `data_quality_status`
- `anomaly_flag`
- `anomaly_reason`

Seed data: **12,960 readings**

Supports:

- Traffic monitoring
- Congestion detection
- Heavy-vehicle analysis
- Traffic hotspot analysis

---

## Alerts and Summaries

### `public.alerts`

Stores operational alerts.

Important fields:

- `alert_id`
- `facility_id`
- `sensor_id`
- `alert_type`
- `severity`
- `message`
- `value`
- `threshold`
- `reading_ts`
- `created_at`
- `status`
- `acknowledged_by`
- `acknowledged_at`
- `resolved_at`

Seed data: **374 alerts**

Supported severity levels include:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Supported alert states include:

- `ACTIVE`
- `ACKNOWLEDGED`
- `RESOLVED`

### `public.daily_facility_summary`

Stores daily facility-level aggregated indicators.

Important fields include:

- Total energy
- Total water
- Total waste
- Recyclable waste
- Hazardous waste
- Average/max AQI
- Vehicle counts
- Heavy-vehicle counts
- Average temperature
- Average humidity
- Rainfall
- Energy cost estimate
- Alert count
- Flagged readings

Seed data: **600 daily summaries**

### `public.monthly_facility_summary`

Stores monthly facility-level aggregated indicators.

Seed data: **20 monthly summaries**

---

## ETL and Data Quality

### `raw.raw_sensor_data`

Landing table for uncleaned sensor payloads.

Seed data: **6,940 raw records**

### `etl.cleaned_sensor_data`

Stores validated and cleaned sensor records after ETL processing.

Seed data: **6,314 cleaned records**

### `etl.rejected_readings`

Quarantines readings that should not enter clean application tables.

Seed data: **626 rejected records**

The schema defines rejection categories including:

- `MISSING_TIMESTAMP`
- `DUPLICATE_RECORD`
- `NULL_CORE_MEASUREMENT`
- `IMPOSSIBLE_VALUE`
- `UNKNOWN_SENSOR`

### `etl.data_quality_log`

Stores validation-rule results and ETL actions.

Seed data: **13 quality-log records**

This structure is useful for explaining data quality and model results during the hackathon demo.

---

## Database Views

The supplied schema contains application-facing views including:

- `public.vw_alerts`
- `public.vw_active_alerts`
- `public.vw_air_quality_readings`
- `public.vw_daily_facility_consumption`
- `public.vw_energy_readings`
- `public.vw_environment_readings`
- `public.vw_facilities`
- `public.vw_latest_readings`
- `public.vw_sensor_health`
- `public.vw_sensors`
- `public.vw_traffic_readings`
- `public.vw_waste_readings`
- `public.vw_water_readings`

These views can be used by the dashboard and analytics layer where appropriate instead of repeatedly rebuilding the same SQL queries.

---

## Data Flow

The intended M2 data pipeline is:

```text
Sensor / Synthetic Data
        |
        v
raw.raw_sensor_data
        |
        v
Validation + Cleaning
        |
        +--------------------+
        |                    |
        v                    v
etl.cleaned_sensor_data   etl.rejected_readings
        |
        v
Public domain tables
        |
        +---- energy_readings
        +---- water_readings
        +---- waste_readings
        +---- air_quality_readings
        +---- environmental_readings
        +---- traffic_readings
        |
        v
ML / AI / Dashboard
```

---

## Team Integration

### Member 2 — Data, Sensors and Database

Owns:

- PostgreSQL
- Sensor-style data simulation
- Raw data ingestion
- Data validation
- Data cleaning
- Database documentation

### Member 3 — Resource Intelligence AI

Consumes:

- `public.energy_readings`
- `public.water_readings`
- `public.equipment_readings`
- `public.safety_readings`
- `public.waste_readings`
- Relevant facility/sensor tables and summaries

Responsible for:

- Energy anomaly detection
- Energy forecasting
- Water abnormal-usage detection
- Waste analysis/prediction

### Member 4 — Operations and Environmental Intelligence AI

Consumes:

- `public.air_quality_readings`
- `public.environmental_readings`
- `public.traffic_readings`
- Relevant facility/sensor/alert data

The current supplied database does **not show a dedicated equipment-readings or safety-incidents table**. Those requirements should therefore be handled only after the team agrees on how they will be represented; do not silently invent duplicate schemas.

### Member 5 — Streamlit Dashboard

Uses the clean PostgreSQL data, views, summaries, alerts, and outputs from the AI modules.

### Member 6 — Decision Intelligence

Uses database records and ML outputs for:

- AI Assistant
- Recommendations
- Alerts
- Scenario simulation

### Member 1 — Integration

Connects all modules and validates the final end-to-end application.

---

## Setup

Create the database:

```sql
CREATE DATABASE smart_industrial_estate;
```

Apply the schema:

```powershell
psql -U postgres -d smart_industrial_estate -f schema.sql
```

Load the seed data:

```powershell
psql -U postgres -d smart_industrial_estate -f seed.sql
```

The exact restore order should be kept consistent with the dump generated by PostgreSQL.

## Configuration

Applications should use environment variables for PostgreSQL credentials.

Example:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_industrial_estate
DB_USER=postgres
DB_PASSWORD=<your-password>
```

Never commit the real PostgreSQL password or `.env` file.

## Data Safety

The existing database is valuable project data.

Do not:

- Drop the database
- Drop existing tables without approval
- Replace existing data unnecessarily
- Create duplicate domain tables when an existing table can be reused
- Commit passwords or secrets
- Commit a private full database dump without review

Before structural changes, create a fresh PostgreSQL backup.

## Current Seed Dataset Summary

| Area | Seed records |
|---|---:|
| Facilities | 20 |
| Sensors | 140 |
| Energy readings | 12,960 |
| Water readings | 12,960 |
| Waste readings | 13,680 |
| Air-quality readings | 12,960 |
| Environmental readings | 27,360 |
| Traffic readings | 12,960 |
| Alerts | 374 |
| Daily summaries | 600 |
| Monthly summaries | 20 |
| Raw sensor records | 6,940 |
| Cleaned ETL records | 6,314 |
| Rejected ETL records | 626 |
| Data-quality log records | 13 |

## Source of Truth

PostgreSQL is the authoritative source for the project's underlying measurements and facility data.

ML models should analyze database data and return structured results. The AI Assistant and recommendation layer should use actual database/model outputs rather than inventing measurements.

The dashboard should clearly distinguish:

- Actual database measurements
- Model predictions/forecasts
- Detected anomalies
- Rule-based alerts
- Simulated/estimated scenario results

