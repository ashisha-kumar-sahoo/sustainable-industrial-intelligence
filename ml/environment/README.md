# Environment Intelligence Module

This module provides dataset-independent machine learning
and analytical functions for environmental monitoring.

## Purpose

The module analyzes environmental observations such as:

- AQI
- PM2.5
- PM10
- Temperature
- CO2
- NO2
- Location
- Timestamp

## Architecture

The module contains the following components:

- `data_loader.py` - validates input DataFrames
- `preprocessing.py` - cleans data and creates reusable features
- `anomaly_detection.py` - detects unusual environmental observations
- `hotspot_detection.py` - identifies potential pollution hotspots
- `risk_analysis.py` - classifies environmental operational risk
- `evaluation.py` - evaluates analytical results
- `predict.py` - runs the complete environment intelligence pipeline

## Dataset Independence

This module does not depend on:

- A specific CSV file
- A fixed dataset
- A fixed number of observations
- A particular data source

All functions accept compatible Pandas DataFrames.

Data can therefore come from:

- CSV files
- Databases
- APIs
- IoT sensors
- Industrial monitoring systems
- Real-time data streams

## Main Pipeline

Input DataFrame
        ↓
Data Validation
        ↓
Preprocessing
        ↓
Feature Creation
        ↓
Anomaly Detection
        ↓
Hotspot Detection
        ↓
Risk Analysis
        ↓
Evaluation / Prediction

## Output

The module can produce:

- Anomaly status
- Anomaly score
- Pollution hotspots
- Environmental risk level
- Risk summaries
- Operational environmental indicators