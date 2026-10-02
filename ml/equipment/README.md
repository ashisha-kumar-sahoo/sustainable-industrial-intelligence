# Equipment Intelligence Module

This module provides dataset-independent machine learning and
analytics functions for industrial equipment monitoring.

## Purpose

The module can analyze equipment data to identify:

- Equipment anomalies
- Equipment utilization levels
- Inspection priorities
- Abnormal operating conditions

## Input

The module accepts a Pandas DataFrame.

Required columns:

- `timestamp`
- `equipment_id`
- `temperature`
- `vibration`
- `operating_hours`
- `utilization`

The module does not depend on:

- A specific dataset
- A specific CSV file
- A fixed number of records
- A fixed equipment list

## Components

### data_loader.py

Validates incoming equipment data.

### preprocessing.py

Cleans data and creates equipment monitoring features.

### anomaly_detection.py

Uses Isolation Forest to detect unusual equipment operating
conditions.

### utilization_analysis.py

Classifies equipment utilization as:

- Low Utilization
- Normal Utilization
- High Utilization

### inspection_priority.py

Calculates inspection priority using equipment operating
conditions.

### evaluation.py

Provides evaluation and summary statistics.

### predict.py

Runs the complete equipment intelligence pipeline.

## Example

```python
from ml.equipment.predict import predict_equipment_status

result = predict_equipment_status(df)

print(result)