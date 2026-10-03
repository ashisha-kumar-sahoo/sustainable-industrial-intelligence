# Energy Intelligence AI

The Energy Intelligence module detects abnormal energy
consumption and provides short-term energy forecasting
for industrial facilities.

## Features

- Temporary energy data input through PowerShell
- Energy data loading
- Data preprocessing
- Expected energy consumption calculation
- Deviation percentage calculation
- Energy anomaly detection
- Severity classification
- Short-term energy forecasting
- Structured output for integration
- Support for multiple facilities and zones
- Model evaluation using MAE, RMSE and R²

## Detection Logic

Energy consumption is compared with the previous
energy consumption value.

| Deviation | Severity | Anomaly |
|-----------|----------|---------|
| 0% - 10% | NORMAL | False |
| >10% - 20% | MEDIUM | True |
| >20% | HIGH | True |

Both positive and negative deviations are considered.

## Input Format

Temporary data can be provided through PowerShell.

Format:

    FACILITY,ZONE,DATE,ENERGY_KWH

Example:

    "F001,Z001,2028-09-01,5000"

Multiple records can be provided in one command.

Example:

    python -m ml.energy.predict "F001,Z001,2028-09-01,5000" "F001,Z001,2028-09-02,5100"

## Output Status

### ENERGY OK

Normal energy consumption.

### ENERGY ABNORMAL

Medium-level abnormal energy consumption.

### ENERGY HIGH

High-level abnormal energy consumption.

## Short-Term Forecasting

The forecasting module calculates the expected
short-term energy consumption using the recent
energy consumption values.

A rolling average of previous values is used.

## Folder Structure

```text
energy/
├── __init__.py
├── data_loader.py
├── preprocessing.py
├── anomaly_detection.py
├── forecasting.py
├── evaluation.py
├── predict.py
└── README.md