# Sustainable Industrial Intelligence
## Data Flow Architecture

### 1. Purpose

This document describes how data moves through the Sustainable Industrial Intelligence platform, from its original source to the final decision-support interface.

The data flow is designed around a common pipeline:

**Source → Ingestion → Validation → Cleaning → Storage → Analytics → Intelligence → Decision**

The architecture separates data collection, storage, analysis, and presentation so that each layer can operate independently and reliably.

---

## 2. Overall Data Flow

```text
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
│                                                             │
│ IoT / Sensors │ Sensor Simulator │ Historical Data         │
│ Open Data     │ CSV / Excel      │ Synthetic Data          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA INGESTION                            │
│                                                             │
│ Receive / Generate → Validate → Clean → Transform           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL                               │
│                   SOURCE OF TRUTH                           │
│                                                             │
│ Raw Data → Cleaned Data → Domain Tables → Views             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI / ANALYTICS                             │
│                                                             │
│ Energy │ Water │ Waste │ Environment │ Traffic              │
│ Equipment │ Safety │ Anomaly │ Forecast │ Prediction         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              DECISION INTELLIGENCE                          │
│                                                             │
│ Recommendations │ Priorities │ Simulation │ AI Assistant    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION / DASHBOARD                     │
│                                                             │
│ KPIs │ Trends │ Alerts │ Forecasts │ Recommendations        │
│ Raw Data │ Simulation │ AI Assistant                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    DECISION MAKER
```

---

## 3. Data Source Layer

The platform supports multiple categories of input data.

### 3.1 Sensor and IoT Data

Future production deployments can provide measurements from real industrial sensors and IoT devices.

Examples include:

- Energy meters
- Water meters
- Waste-bin sensors
- Air-quality sensors
- Environmental sensors
- Traffic sensors
- Equipment sensors
- Safety-related sensors

The prototype does not require physical sensors.

---

### 3.2 Sensor Simulator

The sensor simulator provides sensor-style data for the prototype.

It can generate new readings that resemble continuous facility measurements.

The simulator is useful for:

- Live demonstrations
- Testing ingestion
- Testing validation
- Testing anomaly detection
- Testing dashboard updates
- Demonstrating the architecture without physical hardware

The simulated stream follows the same general ingestion path as future real sensor data.

---

### 3.3 Historical and Existing Data

Existing project data stored in PostgreSQL provides historical information for:

- Analysis
- Trend identification
- Model development
- Testing
- Dashboard visualization

Historical data also allows AI modules to operate without waiting for new sensor readings.

---

### 3.4 Open and Synthetic Data

Additional open or synthetic datasets can be introduced where appropriate.

These sources should be transformed into the project's expected structure before entering the common analytical pipeline.

---

## 4. Data Ingestion Flow

The ingestion layer receives data and prepares it for storage.

```text
Incoming Data
      ↓
Schema / Format Check
      ↓
Validation
      ↓
Cleaning
      ↓
Normalization
      ↓
Database Loading
```

The ingestion layer should preserve data traceability wherever practical.

---

## 5. Raw Data Processing

Incoming readings may initially contain:

- Missing values
- Invalid values
- Incorrect formats
- Duplicate records
- Out-of-range measurements
- Inconsistent timestamps
- Unexpected sensor values

The ingestion pipeline handles these issues before analytical processing.

A simplified processing flow is:

```text
Incoming Reading
       │
       ▼
   Raw Storage
       │
       ▼
   Validation
       │
   ┌───┴───────────────┐
   │                   │
 Valid                Invalid
   │                   │
   ▼                   ▼
Cleaning          Rejected Records
   │
   ▼
Cleaned Data
   │
   ▼
Domain Tables
```

---

## 6. PostgreSQL Data Flow

PostgreSQL is the central source of truth.

The current database architecture separates different stages of the data lifecycle.

```text
raw.raw_sensor_data
          │
          ▼
Validation / Cleaning
          │
     ┌────┴─────┐
     │          │
     ▼          ▼
etl.cleaned   etl.rejected
_sensor_data  _readings
     │
     ▼
Public Domain Tables
     │
     ├── energy_readings
     ├── water_readings
     ├── waste_readings
     ├── air_quality_readings
     ├── environmental_readings
     └── traffic_readings
     │
     ▼
Database Views
```

This separation allows the system to maintain raw information while providing clean data for analytics.

---

## 7. Domain Data Flow

### 7.1 Energy

```text
Energy Reading
      ↓
Validation / Cleaning
      ↓
PostgreSQL
      ↓
Energy Analytics
      ↓
Consumption Trends
      ↓
Anomaly / Forecast
      ↓
Recommendation
```

Potential outputs include:

- Consumption trends
- Abnormal consumption
- Forecasted consumption
- Efficiency insights
- Optimization recommendations

---

### 7.2 Water

```text
Water Reading
      ↓
Validation / Cleaning
      ↓
PostgreSQL
      ↓
Water Analytics
      ↓
Usage Analysis
      ↓
Anomaly / Forecast
      ↓
Recommendation
```

Potential outputs include:

- Usage trends
- Unusual consumption
- Forecasts
- Water-management recommendations

---

### 7.3 Waste

```text
Waste Reading
      ↓
Validation / Cleaning
      ↓
PostgreSQL
      ↓
Waste Analytics
      ↓
Waste Pattern Analysis
      ↓
Priority / Prediction
      ↓
Recommendation
```

Potential outputs include:

- Waste trends
- Collection priorities
- Overflow-related insights
- Operational recommendations

---

### 7.4 Environment

```text
Environmental / AQI Data
          ↓
Validation / Cleaning
          ↓
PostgreSQL
          ↓
Environmental Analytics
          ↓
Condition Analysis
          ↓
Anomaly / Hotspot Detection
          ↓
Alerts / Recommendations
```

Potential outputs include:

- Environmental trends
- Air-quality conditions
- Pollution-related hotspots
- Alerts
- Priority areas

---

### 7.5 Traffic

```text
Traffic Reading
      ↓
Validation / Cleaning
      ↓
PostgreSQL
      ↓
Traffic Analytics
      ↓
Pattern Analysis
      ↓
Hotspot / Prediction
      ↓
Operational Recommendation
```

Potential outputs include:

- Traffic trends
- Congestion patterns
- Hotspots
- Priority areas
- Operational suggestions

---

### 7.6 Equipment and Safety

Equipment and safety intelligence are part of the target operational intelligence layer.

Their detailed database structures should follow the actual project schema as these modules are integrated.

The intended flow is:

```text
Equipment / Safety Data
          ↓
Validation / Cleaning
          ↓
PostgreSQL
          ↓
Operations AI
          ↓
Detection / Prediction
          ↓
Priority / Recommendation
```

The system must not assume database tables or fields that do not exist in the current schema.

---

## 8. AI Analytics Flow

Once data is available in PostgreSQL, the AI modules retrieve the required data.

```text
PostgreSQL
     ↓
Domain Data Query
     ↓
Preprocessing
     ↓
Feature Preparation
     ↓
AI / Statistical Analysis
     ↓
Result Generation
```

Depending on the domain, the analytical process may include:

- Descriptive analysis
- Trend analysis
- Anomaly detection
- Forecasting
- Prediction
- Hotspot identification
- Priority scoring

---

## 9. Standardized AI Output

AI modules should return structured outputs that can be consumed by the dashboard and decision layer.

A conceptual output structure is:

```text
{
    domain,
    metric,
    timestamp,
    facility,
    current_value,
    status,
    prediction,
    confidence,
    priority,
    explanation
}
```

The exact implementation may vary between modules, but outputs should remain consistent enough for integration.

---

## 10. Decision Intelligence Flow

AI results are passed to the decision intelligence layer.

```text
AI Result
    ↓
Interpretation
    ↓
Condition / Priority
    ↓
Recommended Action
    ↓
Optional Scenario Simulation
    ↓
Decision Support
```

For example:

```text
High Energy Consumption
          ↓
Anomaly Detected
          ↓
Facility Prioritized
          ↓
Recommendation Generated
          ↓
"What if operating hours are reduced?"
          ↓
Scenario Simulation
          ↓
Estimated Impact
```

---

## 11. Recommendation Flow

Recommendations should connect analytical findings to practical actions.

```text
Data
 ↓
Insight
 ↓
Problem / Opportunity
 ↓
Recommended Action
 ↓
Expected Impact
 ↓
Decision
```

A recommendation should ideally communicate:

- What happened?
- Where did it happen?
- Why is it important?
- What should be done?
- What impact is expected?

---

## 12. Scenario Simulation Flow

Scenario simulation extends the normal analytics pipeline.

```text
Current Data
     ↓
Current State
     ↓
User Proposed Change
     ↓
Simulation Logic
     ↓
Estimated New State
     ↓
Comparison
     ↓
Expected Impact
```

The purpose is not simply to display a prediction, but to allow users to compare possible decisions.

---

## 13. AI Assistant Data Flow

The AI assistant provides a natural-language interface to project intelligence.

```text
User Question
      ↓
Question Understanding
      ↓
Relevant Data / Analytics
      ↓
Context Construction
      ↓
AI Response
      ↓
User
```

Example:

```text
User:
"Which facility has the highest energy consumption?"

        ↓

Assistant retrieves relevant energy data

        ↓

Analytics identifies the highest consumer

        ↓

Assistant explains the result

        ↓

User receives data-grounded answer
```

The assistant should rely on actual project data rather than unsupported assumptions.

---

## 14. Dashboard Data Flow

The dashboard consumes outputs from the application and intelligence layers.

```text
PostgreSQL
     │
     ├───────────────┐
     │               │
     ▼               ▼
Analytics        Direct Data
     │               │
     └───────┬───────┘
             ▼
       Application Layer
             │
             ▼
      Streamlit Dashboard
             │
             ├── KPIs
             ├── Charts
             ├── Alerts
             ├── Forecasts
             ├── Recommendations
             ├── Simulation
             └── AI Assistant
```

The dashboard should focus on presentation and user interaction rather than duplicating core AI logic.

---

## 15. Alert Flow

Alerts can originate from detected abnormal conditions.

```text
Incoming Data
      ↓
Analytics
      ↓
Threshold / Anomaly Detection
      ↓
Alert Generated
      ↓
Alert Stored
      ↓
Dashboard
      ↓
User Action
```

An alert should provide enough context for the user to understand why attention is required.

---

## 16. End-to-End Example

A complete example of the system flow is energy anomaly detection.

```text
Energy Sensor / Simulator
          ↓
Raw Reading
          ↓
Validation
          ↓
Cleaning
          ↓
PostgreSQL
          ↓
Energy AI
          ↓
Historical Pattern Analysis
          ↓
Anomaly Detection
          ↓
High Consumption Detected
          ↓
Priority Assessment
          ↓
Recommendation
          ↓
Scenario Simulation
          ↓
Expected Energy Saving
          ↓
Streamlit Dashboard
          ↓
Decision Maker
```

This demonstrates the project's central concept of moving from raw operational data to actionable decisions.

---

## 17. Data Ownership

| Data Stage | Primary Responsibility |
|---|---|
| Data generation / ingestion | M2 |
| PostgreSQL storage | M2 |
| Resource analysis | M3 |
| Operations analysis | M4 |
| Recommendations | M6 |
| Scenario simulation | M6 |
| AI assistant | M6 |
| Dashboard presentation | M5 |
| Cross-module integration | M1 |

All modules should follow the shared project architecture.

---

## 18. Data Integrity Principles

The data flow follows these principles:

### Preserve Raw Data

Raw information should be retained where required for traceability and debugging.

### Validate Before Analysis

Invalid or malformed data should not directly enter analytical workflows.

### Clean Before Modeling

AI models should operate on appropriately cleaned and prepared data.

### Centralize Shared Data

Common project data should remain in PostgreSQL.

### Avoid Schema Assumptions

Modules must use fields and tables that actually exist.

### Keep Credentials Separate

Database credentials must never be embedded in source code or committed to GitHub.

---

## 19. Prototype Data Strategy

The prototype uses a combination of:

- Existing historical/project data
- PostgreSQL structured data
- Simulated sensor-style readings
- Synthetic or open data where required

This strategy enables demonstration of the complete architecture without requiring physical sensor hardware.

The ingestion and storage architecture remains compatible with future real-time sensor integration.

---

## 20. Summary

The platform transforms raw facility information through a sequence of increasingly intelligent stages:

```text
RAW DATA
   ↓
VALIDATED DATA
   ↓
CLEAN DATA
   ↓
STRUCTURED DATA
   ↓
ANALYTICS
   ↓
INSIGHTS
   ↓
PREDICTIONS
   ↓
RECOMMENDATIONS
   ↓
SIMULATIONS
   ↓
DECISIONS
```

The key principle is:

> **Data should not stop at visualization. It should be transformed into intelligence that supports action.**