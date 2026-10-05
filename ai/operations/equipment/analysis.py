"""Analysis and structured results for Equipment Operations AI."""

import pandas as pd

from ai.operations.equipment.config import (
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
    TEMPERATURE_COLUMN,
    VIBRATION_COLUMN,
    ENERGY_COLUMN,
    HIGH_TEMPERATURE_THRESHOLD,
    HIGH_VIBRATION_THRESHOLD,
    HIGH_ENERGY_THRESHOLD,
)


def calculate_equipment_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate equipment maintenance risk."""

    data = df.copy()

    data["risk_score"] = 0

    if TEMPERATURE_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[TEMPERATURE_COLUMN],
                errors="coerce",
            ) >= HIGH_TEMPERATURE_THRESHOLD
        ).astype(int)

    if VIBRATION_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[VIBRATION_COLUMN],
                errors="coerce",
            ) >= HIGH_VIBRATION_THRESHOLD
        ).astype(int)

    if ENERGY_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[ENERGY_COLUMN],
                errors="coerce",
            ) >= HIGH_ENERGY_THRESHOLD
        ).astype(int)

    data["maintenance_priority"] = "Normal"

    data.loc[
        data["risk_score"] == 1,
        "maintenance_priority",
    ] = "Monitor"

    data.loc[
        data["risk_score"] >= 2,
        "maintenance_priority",
    ] = "High"

    return data


def build_equipment_results(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return structured equipment results for the M5 dashboard."""

    data = calculate_equipment_risk(df)

    result_columns = [
        TIMESTAMP_COLUMN,
        FACILITY_COLUMN,
        SENSOR_COLUMN,
        TEMPERATURE_COLUMN,
        VIBRATION_COLUMN,
        ENERGY_COLUMN,
        "anomaly_score",
        "anomaly_prediction",
        "anomaly_status",
        "risk_score",
        "maintenance_priority",
    ]

    available_columns = [
        column
        for column in result_columns
        if column in data.columns
    ]

    return data[available_columns].copy()