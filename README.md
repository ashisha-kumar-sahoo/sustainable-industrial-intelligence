# Sustainable Industrial Intelligence

AI-powered decision dashboard for sustainable industrial estate management.

The system combines sensor-style data, open data, synthetic data, PostgreSQL, machine learning, anomaly detection, forecasting, scenario simulation, and Generative AI to support data-driven facility management.

## Problem

Industrial estates generate large amounts of operational and environmental data related to:

* Energy consumption
* Water usage
* Waste generation
* Air quality
* Traffic and parking
* Equipment utilization
* Safety incidents
* Sustainability indicators

Managing these different data sources separately makes it difficult for administrators to identify problems, understand trends, prioritize inspections, and take timely action.

This project provides a centralized intelligence dashboard that converts these data sources into actionable insights for facility administrators.

## Objectives

* Monitor industrial estate operations through a unified dashboard.
* Detect abnormal energy, water, waste, environmental, and equipment patterns.
* Forecast short-term operational trends.
* Identify environmental, traffic, equipment, and safety hotspots.
* Generate actionable recommendations.
* Provide a Facility AI Assistant for administrators.
* Provide what-if scenario simulation.
* Provide access to the underlying raw data.
* Support configurable facility and zone-level monitoring.

## Key Features

### 1. Resource Intelligence

* Energy monitoring
* Energy anomaly detection
* Energy forecasting
* Water abnormal-usage detection
* Waste-bin overflow prediction
* Resource consumption analysis

### 2. Environmental & Operational Intelligence

* AQI monitoring
* PM2.5 / PM10 / CO2 / NO2 analysis
* Environmental hotspot detection
* Traffic and parking hotspot analysis
* Equipment utilization and anomaly detection
* Safety incident trend analysis

### 3. AI Decision Support

* Facility AI Assistant
* Automated recommendations
* Priority alerts
* Inspection prioritization
* What-if scenario simulation
* Natural-language facility summaries

### 4. Raw Data Explorer

Administrators can inspect the raw data behind dashboard metrics, alerts, forecasts, and AI insights.

## System Architecture

```text
Industrial Estate
       |
       v
Sensor / IoT / Open / Synthetic / CSV Data
       |
       v
Data Ingestion
Python + Pandas + NumPy
       |
       v
PostgreSQL
Source of Truth
       |
       v
+-------------------------------+
|       Analytics / AI          |
|                               |
| Anomaly Detection             |
| Forecasting                   |
| Prediction                    |
| Hotspot Detection             |
| Priority Analysis             |
+-------------------------------+
       |
       v
Decision & Recommendation Engine
       |
       +-------------------+
       |                   |
       v                   v
   Rule Engine          GenAI / LLM
       |                   |
       +---------+---------+
                 |
                 v
       Decision Intelligence
                 |
       +---------+---------+
       |                   |
       v                   v
 Scenario Simulation   Facility AI Assistant
       |                   |
       +---------+---------+
                 |
                 v
          Streamlit Dashboard
                 |
       +---------+----------+
       |         |          |
       v         v          v
     KPIs      Maps       Alerts
       |
       v
 Forecasts / Recommendations / Raw Data
```

## Technology Stack

### Data

* Python
* Pandas
* NumPy
* CSV / Excel
* Synthetic / sensor-style data

### Database

* PostgreSQL

### Machine Learning

* Scikit-learn
* Statistical analysis
* Time-series forecasting
* Clustering where required

### AI

* Generative AI / LLM
* PostgreSQL and analytical results as evidence
* Recommendation and explanation layer

### Dashboard

* Streamlit
* Plotly
* Geospatial visualization where required

## Project Structure

```text
sustainable-industrial-intelligence/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│
├── ingestion/
│
├── ml/
│   ├── energy/
│   ├── water/
│   ├── waste/
│   ├── environment/
│   ├── traffic/
│   ├── equipment/
│   └── safety/
│
├── ai/
│   ├── assistant/
│   ├── recommendations/
│   └── simulation/
│
├── dashboard/
├── backend/
│
└── docs/
    ├── architecture/
    ├── database/
    └── api/
```

## Team Responsibilities

| Member   | Responsibility                                                                            |
| -------- | ----------------------------------------------------------------------------------------- |
| Member 1 | Project leadership, integration, backend/API coordination, GitHub, testing and final demo |
| Member 2 | Data generation, sensor simulator, data ingestion and PostgreSQL                          |
| Member 3 | Energy, water and waste intelligence                                                      |
| Member 4 | Environment, traffic, equipment and safety intelligence                                   |
| Member 5 | Streamlit dashboard and Raw Data Explorer                                                 |
| Member 6 | AI Assistant, recommendations and scenario simulation                                     |

## Development Principle

**PostgreSQL is the source of truth.**

Machine learning analyzes the data.

Rules provide deterministic decision and priority logic.

Generative AI explains analytical results and communicates recommendations.

The dashboard visualizes the results.

## Data Assumption

This prototype may use synthetic, open, CSV, and/or sensor-style data where real industrial sensor data is unavailable.

The system is intended for decision-support and demonstration purposes and does not represent official industrial, environmental, safety, or regulatory measurements.

## Future Scope

* Real IoT sensor integration
* MQTT-based streaming
* Live industrial estate deployment
* More advanced forecasting models
* Role-based access control
* Mobile interface
* Integration with facility management systems
* Automated maintenance and work-order systems


## Quick Start

1. Create and activate `.venv`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set the PostgreSQL password. Never commit `.env`.
4. Start PostgreSQL and apply `database/migrations/001_add_waste_bin_telemetry.sql` to an existing installation.
5. Install/start Ollama separately and pull the configured Qwen model.
6. Run the Streamlit dashboard from the project root with `streamlit run dashboard/app.py`.
7. Use `python -m ingestion.sensor_simulator` / the documented ingestion entry point when fresh sensor-style readings are required.

## Roles

The dashboard supports `ADMIN`, `OPERATIONS`, and `SUSTAINABILITY` views. Registration is local prototype authentication; production deployments should use enterprise identity and secure session management.

## Hospital configuration

Use the sidebar **Facility profile** selector to demonstrate the same application architecture configured for a hospital. The supplied database remains industrial-estate data; hospital mode is a configuration path, not a claim of hospital measurements.

## Validation

Run:

```powershell
python -m compileall -q .
pytest -q
```

The current automated suite covers the operations/integration tests. Dashboard and database smoke tests additionally depend on a reachable PostgreSQL instance.


## Model Folder Ownership

The overlap between `ai/operations/` and `ml/` is documented in [`docs/architecture/model-folder-audit.md`](docs/architecture/model-folder-audit.md). Do not delete either tree without migrating its data contracts, unique functionality, and tests.


## Local database upgrade for equipment and safety

The existing PostgreSQL database is preserved. Back up `smart_industrial_estate`, then apply `database/migrations/002_add_equipment_safety_telemetry.sql` from PowerShell before running the simulator/loader. See [`FINAL_SETUP.md`](FINAL_SETUP.md) and [`database/README.md`](database/README.md) for exact commands. This migration adds equipment/safety telemetry storage and complete JSONB raw payload capture; it does not drop or recreate the database.

## Model folder ownership

`ml/` is the runtime canonical model tree used by the dashboard. `ai/operations/` contains a parallel research/legacy implementation with some distinct functions; see [`docs/AI_MODEL_FOLDER_AUDIT.md`](docs/AI_MODEL_FOLDER_AUDIT.md). These folders are not byte-for-byte copies and must not be bulk-deleted without reconciling their different contracts and tests.
