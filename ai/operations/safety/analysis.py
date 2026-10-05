"""Analysis and structured results for Safety Operations AI."""

import pandas as pd

from ai.operations.safety.config import (
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
    INCIDENT_COUNT_COLUMN,
    RESPONSE_TIME_COLUMN,
    SEVERITY_COLUMN,
)

from ai.operations.safety.risk_analysis import (
    calculate_safety_risk,
)


def build_safety_results(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return structured safety results for the M5 dashboard."""

    data = calculate_safety_risk(df)

    result_columns = [
        TIMESTAMP_COLUMN,
        FACILITY_COLUMN,
        SENSOR_COLUMN,
        INCIDENT_COUNT_COLUMN,
        RESPONSE_TIME_COLUMN,
        SEVERITY_COLUMN,
        "high_severity_flag",
        "risk_score",
        "risk_level",
    ]

    available_columns = [
        column
        for column in result_columns
        if column in data.columns
    ]

    return data[available_columns].copy()