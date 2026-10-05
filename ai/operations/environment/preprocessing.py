"""Preprocessing for Environment Operations AI."""

import pandas as pd

from ai.operations.environment.config import (
    AQI_COLUMN,
    PM25_COLUMN,
    PM10_COLUMN,
    CO_COLUMN,
    CO2_COLUMN,
    NO2_COLUMN,
    SO2_COLUMN,
)


NUMERIC_COLUMNS = [
    AQI_COLUMN,
    PM25_COLUMN,
    PM10_COLUMN,
    CO_COLUMN,
    CO2_COLUMN,
    NO2_COLUMN,
    SO2_COLUMN,
]


def preprocess_environment_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare environment readings."""

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


def create_environment_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create dataset-independent environmental features."""

    data = df.copy()

    if {PM25_COLUMN, PM10_COLUMN}.issubset(data.columns):
        data["pm_ratio"] = (
            data[PM25_COLUMN]
            / data[PM10_COLUMN].replace(0, pd.NA)
        )

    pollution_columns = [
        column
        for column in [
            AQI_COLUMN,
            PM25_COLUMN,
            PM10_COLUMN,
        ]
        if column in data.columns
    ]

    if pollution_columns:
        data["pollution_index"] = data[pollution_columns].mean(
            axis=1
        )

    if AQI_COLUMN in data.columns:
        data["high_aqi_flag"] = (
            data[AQI_COLUMN] >= 100
        ).astype(int)

    return data