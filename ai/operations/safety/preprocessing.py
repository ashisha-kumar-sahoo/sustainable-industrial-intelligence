"""Preprocessing for Safety Operations AI."""

import pandas as pd

from ai.operations.safety.config import (
    INCIDENT_COUNT_COLUMN,
    RESPONSE_TIME_COLUMN,
)


NUMERIC_COLUMNS = [
    INCIDENT_COUNT_COLUMN,
    RESPONSE_TIME_COLUMN,
]


def preprocess_safety_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Clean and prepare safety data."""

    data = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    if INCIDENT_COUNT_COLUMN in data.columns:
        data = data.dropna(
            subset=[INCIDENT_COUNT_COLUMN],
            how="all",
        )

    return data.reset_index(drop=True)


def create_safety_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create dataset-independent safety features."""

    data = df.copy()

    if INCIDENT_COUNT_COLUMN in data.columns:
        data["high_incident_flag"] = (
            data[INCIDENT_COUNT_COLUMN] >= 3
        ).astype(int)

    if RESPONSE_TIME_COLUMN in data.columns:
        data["high_response_time_flag"] = (
            data[RESPONSE_TIME_COLUMN] >= 10
        ).astype(int)

    return data