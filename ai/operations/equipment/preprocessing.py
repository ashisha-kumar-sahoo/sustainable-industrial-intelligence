"""Preprocessing for Equipment Operations AI."""

import pandas as pd

from ai.operations.equipment.config import (
    TEMPERATURE_COLUMN,
    VIBRATION_COLUMN,
    ENERGY_COLUMN,
)


NUMERIC_COLUMNS = [
    TEMPERATURE_COLUMN,
    VIBRATION_COLUMN,
    ENERGY_COLUMN,
]


def preprocess_equipment_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Clean and prepare equipment readings."""

    data = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    available_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in data.columns
    ]

    if available_columns:
        data = data.dropna(
            subset=available_columns,
            how="all",
        )

    return data.reset_index(drop=True)


def create_equipment_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create dataset-independent equipment features."""

    data = df.copy()

    if TEMPERATURE_COLUMN in data.columns:
        data["high_temperature_flag"] = (
            data[TEMPERATURE_COLUMN] >= 80
        ).astype(int)

    if VIBRATION_COLUMN in data.columns:
        data["high_vibration_flag"] = (
            data[VIBRATION_COLUMN] >= 4
        ).astype(int)

    if ENERGY_COLUMN in data.columns:
        data["high_energy_flag"] = (
            data[ENERGY_COLUMN] >= 60
        ).astype(int)

    return data