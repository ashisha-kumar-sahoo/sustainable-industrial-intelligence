"""Analysis and structured results for Environment Operations AI."""

import pandas as pd

from ai.operations.environment.config import (
    AQI_COLUMN,
    PM25_COLUMN,
    PM10_COLUMN,
    NO2_COLUMN,
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
    HIGH_AQI_THRESHOLD,
)


def calculate_environment_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate environmental risk from pollution indicators."""

    data = df.copy()

    for column in [
        AQI_COLUMN,
        PM25_COLUMN,
        PM10_COLUMN,
        NO2_COLUMN,
    ]:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    data["risk_score"] = 0

    if AQI_COLUMN in data.columns:
        data["risk_score"] += (
            data[AQI_COLUMN] >= HIGH_AQI_THRESHOLD
        ).astype(int)

    if PM25_COLUMN in data.columns:
        data["risk_score"] += (
            data[PM25_COLUMN] >= 50
        ).astype(int)

    if NO2_COLUMN in data.columns:
        data["risk_score"] += (
            data[NO2_COLUMN] >= 40
        ).astype(int)

    data["risk_level"] = "Low"

    data.loc[
        data["risk_score"] == 1,
        "risk_level",
    ] = "Moderate"

    data.loc[
        data["risk_score"] >= 2,
        "risk_level",
    ] = "High"

    return data


def build_environment_results(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return clean structured results for the M5 dashboard."""

    data = calculate_environment_risk(df)

    result_columns = [
        TIMESTAMP_COLUMN,
        FACILITY_COLUMN,
        SENSOR_COLUMN,
        AQI_COLUMN,
        PM25_COLUMN,
        PM10_COLUMN,
        "anomaly_score",
        "anomaly_prediction",
        "anomaly_status",
        "forecast_aqi",
        "risk_score",
        "risk_level",
    ]

    available_columns = [
        column
        for column in result_columns
        if column in data.columns
    ]

    return data[available_columns].copy()