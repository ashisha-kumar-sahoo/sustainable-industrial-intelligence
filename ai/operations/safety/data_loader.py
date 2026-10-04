"""Data loading and validation for Safety Operations AI."""

import pandas as pd

from ai.operations.safety.config import (
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
)


REQUIRED_COLUMNS = [
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
]


def validate_safety_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the approved safety data contract."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    return df.copy()


def prepare_safety_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare approved safety data for analysis."""

    data = validate_safety_data(df)

    data[TIMESTAMP_COLUMN] = pd.to_datetime(
        data[TIMESTAMP_COLUMN],
        errors="coerce",
    )

    numeric_columns = [
        "incident_count",
        "response_time_minutes",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    data = data.dropna(
        subset=[
            TIMESTAMP_COLUMN,
            FACILITY_COLUMN,
            SENSOR_COLUMN,
        ]
    )

    data = data.sort_values(
        by=[
            FACILITY_COLUMN,
            SENSOR_COLUMN,
            TIMESTAMP_COLUMN,
        ]
    ).reset_index(drop=True)

    return data