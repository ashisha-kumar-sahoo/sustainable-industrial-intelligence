# Sustainable Industrial Intelligence
## System Architecture

### 1. Overview

**Sustainable Industrial Intelligence** is an AI-powered decision-support platform designed for industrial estates and large institutional facilities.

The system integrates operational data from multiple domains, stores it in a centralized PostgreSQL database, applies analytics and AI models, and converts the results into actionable insights for facility decision-makers.

The architecture follows a closed-loop approach:

**Data → Analysis → Detection → Prediction → Recommendation → Simulation → Decision**

The platform is designed to support historical data, synthetic/simulated sensor data, and future real IoT sensor streams.

---

## 2. Architectural Objectives

The architecture is designed to:

- Centralize operational data from multiple facility domains.
- Use PostgreSQL as the common source of truth.
- Support sensor-style, synthetic, open, and historical data.
- Validate and clean incoming data before analytical processing.
- Detect abnormal operational conditions.
- Generate short-term forecasts and predictions.
- Identify operational hotspots and priority areas.
- Convert analytical results into actionable recommendations.
- Allow decision-makers to evaluate what-if scenarios.
- Provide an AI assistant grounded in facility data.
- Present operational intelligence through an interactive dashboard.
- Keep the system modular so individual AI modules can evolve independently.

---

## 3. High-Level Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                 INDUSTRIAL ESTATE FACILITIES                 │
│                                                               │
│ Energy │ Water │ Waste │ Environment │ Traffic │ Equipment   │
│ Safety │ Other Operational Data                               │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                           │
│                                                               │
│ IoT / Sensors │ Sensor Simulator │ Open Data │ CSV / Excel   │
│ Historical Data │ Synthetic Data                               │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                       │
│                                                               │
│ Sensor Simulator → Validation → Cleaning → PostgreSQL Loader │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATA PLATFORM                     │
│                     SOURCE OF TRUTH                           │
│                                                               │
│ Raw Data → Cleaned Data → Domain Tables → Views              │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    AI / ANALYTICS ENGINE                      │
│                                                               │
│ Resource AI              Operations AI                        │
│ ├─ Energy               ├─ Environment                       │
│ ├─ Water                ├─ Traffic                            │
│ └─ Waste                ├─ Equipment                          │
│                          └─ Safety                             │
│                                                               │
│ Anomaly Detection │ Forecasting │ Prediction │ Hotspots       │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│              DECISION INTELLIGENCE LAYER                     │
│                                                               │
│ Recommendations │ Priority Analysis │ Scenario Simulation     │
│                         AI Assistant                          │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                          │
│                                                               │
│ Backend / Integration Layer                                   │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                        │
│                                                               │
│ KPIs │ Trends │ Alerts │ Predictions │ Recommendations       │
│ Raw Data │ Scenario Results │ AI Assistant                    │
└───────────────────────────────────────────────────────────────┘
```

---

## 4. Major Components

### 4.1 Data Sources

The system can receive information from multiple sources:

- Industrial sensors
- IoT devices
- Sensor-style simulated streams
- Historical facility records
- Open datasets
- CSV/Excel datasets
- Synthetic data generated for testing and demonstration

The prototype primarily uses historical/project data and simulated sensor-style data.

The architecture remains compatible with real sensor integration in a future deployment.

---

### 4.2 Data Ingestion Layer

The ingestion layer is responsible for bringing incoming data into the platform.

Its major responsibilities are:

1. Generate or receive incoming readings.
2. Validate incoming records.
3. Identify invalid or incomplete records.
4. Clean and normalize valid records.
5. Load processed data into PostgreSQL.
6. Maintain traceability of rejected or processed readings.

The ingestion layer separates data acquisition from analytics so that AI modules operate on structured data.

---

### 4.3 PostgreSQL Data Platform

PostgreSQL acts as the central **source of truth** for the project.

The database currently contains structured operational data for domains including:

- Facilities
- Sensors
- Energy
- Water
- Waste
- Air quality
- Environmental measurements
- Traffic
- Alerts
- Facility summaries

The database also contains raw, cleaned, rejected, and data-quality-related ingestion information.

Database views provide convenient access to commonly required information for dashboards and analytics.

AI modules should consume the common project database rather than creating independent databases.

---

### 4.4 AI and Analytics Layer

The AI and analytics layer is divided according to project responsibilities.

#### Resource Intelligence

Resource AI focuses on:

- Energy
- Water
- Waste

Typical analytical capabilities include:

- Consumption analysis
- Trend analysis
- Anomaly detection
- Forecasting
- Resource optimization
- Operational recommendations

#### Operations Intelligence

Operations AI focuses on:

- Environment
- Traffic
- Equipment
- Safety

Typical capabilities include:

- Environmental condition analysis
- Traffic pattern analysis
- Hotspot identification
- Equipment-related intelligence
- Safety-related trend and priority analysis

The AI modules must use the actual available database schema and must not assume unsupported tables or columns.

---

## 5. Decision Intelligence Layer

The decision intelligence layer converts analytical results into information that can support operational decisions.

It contains three major capabilities.

### 5.1 Recommendations

The recommendation engine converts detected conditions and predictions into actionable suggestions.

Examples include:

- Reduce unnecessary energy consumption.
- Adjust operational schedules.
- Prioritize waste collection.
- Investigate environmental hotspots.
- Prioritize maintenance or inspection.
- Issue operational advisories.

Recommendations should be based on actual analytical outputs rather than generic text.

---

### 5.2 Scenario Simulation

Scenario simulation allows users to evaluate possible actions before making operational decisions.

```text
Current Situation
       ↓
Apply Proposed Change
       ↓
Estimate Expected Impact
       ↓
Compare With Current State
       ↓
Decision
```

Example scenarios may include:

- Changing energy operating schedules.
- Adjusting waste collection frequency.
- Evaluating traffic-management changes.
- Comparing resource-saving strategies.

---

### 5.3 AI Assistant

The AI assistant provides a natural-language interface to facility intelligence.

Users can ask questions such as:

- What is today's energy consumption?
- Which facilities have abnormal consumption?
- What are the major environmental concerns?
- Which area requires attention?
- What actions are recommended?

The assistant should be grounded in the project's actual data and analytical outputs.

---

## 6. Application and Dashboard Layer

The application layer connects the backend, analytics modules, decision intelligence, and user interface.

The Streamlit dashboard provides the primary prototype interface.

The dashboard can present:

- Facility KPIs
- Resource consumption
- Environmental conditions
- Traffic information
- Alerts
- Anomalies
- Forecasts
- Recommendations
- Scenario results
- Raw data exploration
- AI assistant interaction

The dashboard should consume standardized outputs from backend and AI modules instead of duplicating analytical logic.

---

## 7. Data Flow

The overall data flow is:

```text
Data Sources
     ↓
Data Ingestion
     ↓
Validation
     ↓
Cleaning
     ↓
PostgreSQL
     ↓
AI / Analytics
     ↓
Insights
     ↓
Recommendations / Simulation / Assistant
     ↓
Backend Integration
     ↓
Streamlit Dashboard
     ↓
Decision Maker
```

This separation keeps data storage, analytics, decision logic, and presentation modular.

---

## 8. Team-Level Architecture Ownership

| Component | Primary Responsibility |
|---|---|
| Database & ingestion | M2 |
| Resource AI | M3 |
| Operations AI | M4 |
| Dashboard | M5 |
| Recommendations | M6 |
| Scenario simulation | M6 |
| AI assistant | M6 |
| Integration & final architecture | M1 |
| Testing & final integration | M1 + all members |

Team members work independently on their assigned modules while following the common database, interfaces, and project structure.

---

## 9. Integration Principles

### Single Source of Truth

PostgreSQL is the common data source for project modules.

### Modular Development

Each team member develops within their assigned module without unnecessarily modifying another member's component.

### Common Interfaces

AI modules should expose predictable functions and outputs so that the dashboard and decision layer can consume them consistently.

### No Duplicate Databases

Individual modules should not create separate project databases.

### Schema-Driven Development

AI and dashboard code must use the actual database schema.

Unsupported tables, fields, or metrics must not be assumed without formally extending the project design.

### Configuration Through Environment Variables

Database credentials and other environment-specific configuration should not be hard-coded or committed to GitHub.

### Git-Based Integration

Feature branches are integrated into `main` through pull requests and review.

---

## 10. Current Prototype and Future Extension

The current prototype is designed around historical/project data and simulated sensor-style data.

This allows the complete intelligence pipeline to be demonstrated without requiring physical hardware.

The architecture can later be extended with:

- Real IoT sensors
- MQTT or similar messaging systems
- Real-time streaming
- Additional operational domains
- Dedicated equipment data
- Dedicated safety data
- More advanced ML models
- Production deployment infrastructure

These extensions should build on the existing architecture rather than requiring a complete redesign.

---

## 11. Security and Configuration

The prototype should follow basic security practices:

- Never commit database passwords.
- Use environment variables for credentials.
- Keep `.env` files out of Git.
- Validate incoming data.
- Restrict database access according to application requirements.
- Avoid exposing database credentials through the dashboard.
- Keep development and production configuration separate.

---

## 12. Architectural Goal

The ultimate goal of the architecture is to transform fragmented industrial-estate data into actionable decision intelligence.

The system is therefore designed around the principle:

> **From fragmented industrial data to simulated, actionable decisions.**

Rather than functioning only as a visualization dashboard, the platform combines data integration, analytics, AI, recommendations, simulation, and natural-language interaction into a unified decision-support system.