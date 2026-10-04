"""Preprocessing for Traffic Operations AI."""

import pandas as pd

from ai.operations.traffic.config import (
    VEHICLE_COUNT_COLUMN,
    HEAVY_VEHICLE_COUNT_COLUMN,
    SPEED_COLUMN,
    OCCUPANCY_COLUMN,
)


NUMERIC_COLUMNS = [
    VEHICLE_COUNT_COLUMN,
    HEAVY_VEHICLE_COUNT_COLUMN,
    SPEED_COLUMN,
    OCCUPANCY_COLUMN,
]


def preprocess_traffic_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Clean and prepare traffic readings."""

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


def create_traffic_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create dataset-independent traffic features."""

    data = df.copy()

    if {
        VEHICLE_COUNT_COLUMN,
        HEAVY_VEHICLE_COUNT_COLUMN,
    }.issubset(data.columns):
        data["heavy_vehicle_ratio"] = (
            data[HEAVY_VEHICLE_COUNT_COLUMN]
            / data[VEHICLE_COUNT_COLUMN].replace(0, pd.NA)
        )

    if SPEED_COLUMN in data.columns:
        data["low_speed_flag"] = (
            data[SPEED_COLUMN] < 20
        ).astype(int)

    if OCCUPANCY_COLUMN in data.columns:
        data["high_occupancy_flag"] = (
            data[OCCUPANCY_COLUMN] >= 80
        ).astype(int)

    return data