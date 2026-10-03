# Water Intelligence AI

The Water Intelligence module detects abnormal water consumption
and identifies possible water wastage in industrial facilities.

## Features

- Temporary water data input through PowerShell
- Water data loading
- Data preprocessing
- Expected water consumption calculation
- Deviation percentage calculation
- Abnormal usage detection
- Water wastage detection
- Threshold-based detection
- Severity classification
- Structured output for integration
- Support for multiple facilities and zones
- Model evaluation using MAE, RMSE and R²

## Detection Logic

Water usage is compared with the expected water consumption.

| Deviation | Severity | Anomaly |
|-----------|----------|---------|
| 0% - 10% | NORMAL | False |
| >10% - 20% | MEDIUM | True |
| >20% | HIGH | True |

Both positive and negative deviations are considered.

## Input Format

Temporary data can be provided through PowerShell.

Format:

    FACILITY,ZONE,DATE,WATER_LITERS,FLOW_RATE

Example:

    "F001,Z001,2028-09-01,18000,750"

Multiple records can be provided in one command.

Example:

    python -m ml.water.predict "F001,Z001,2028-09-01,18000,750" "F001,Z001,2028-09-02,18100,755"

## Output Status

The module provides three main statuses:

### WATER OK

Normal water consumption.

### WATER ABNORMAL

Medium-level abnormal water consumption.

### WATER WASTAGE

High-level abnormal water consumption.

## Folder Structure

```text
water/
├── __init__.py
├── data_loader.py
├── preprocessing.py
├── anomaly_detection.py
├── threshold_detection.py
├── evaluation.py
├── predict.py
├── test_database.py
└── README.md