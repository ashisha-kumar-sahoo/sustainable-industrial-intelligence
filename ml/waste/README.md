# Waste Intelligence AI

The Waste Intelligence module predicts waste bin overflow
risk and determines collection priority for industrial
facilities.

## Features

- Temporary waste data input through PowerShell
- Waste data loading
- Data preprocessing
- Fill level analysis
- Fill rate calculation
- Overflow risk prediction
- Collection priority
- Support for waste types
- Support for multiple facilities and zones
- Structured output for integration
- Model evaluation using MAE, RMSE and R²

## Input Format

Temporary data can be provided through PowerShell.

Format:

    FACILITY,ZONE,DATE,FILL_LEVEL,WASTE_TYPE

Example:

    "F001,Z001,2028-09-01,40,plastic"

Fill level is represented as a percentage from 0 to 100.

## Overflow Risk Logic

| Fill Level | Overflow Risk |
|------------|---------------|
| < 60% | LOW |
| 60% - 79% | MEDIUM |
| >= 80% | HIGH |

A high fill rate can also increase the overflow risk.

## Fill Rate

The system calculates how quickly the bin fill level
is increasing.

Fill rate is calculated using:

    Fill Rate =
    (Current Fill Level - Previous Fill Level)
    / Time Difference

The result represents percentage fill increase
per hour.

## Collection Priority

| Overflow Risk | Collection Priority |
|---------------|---------------------|
| LOW | LOW |
| MEDIUM | MEDIUM |
| HIGH | HIGH |

## Output Status

### WASTE OK

No significant overflow risk.

### WASTE ABNORMAL

Medium-level waste overflow risk.

### OVERFLOW RISK

High-level overflow risk requiring high collection
priority.

## Folder Structure

```text
waste/
├── __init__.py
├── data_loader.py
├── preprocessing.py
├── overflow_prediction.py
├── collection_priority.py
├── evaluation.py
├── predict.py
└── README.md