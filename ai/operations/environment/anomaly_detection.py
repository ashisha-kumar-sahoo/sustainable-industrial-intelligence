"""Anomaly detection for Environment Operations AI."""

import pandas as pd
from sklearn.ensemble import IsolationForest

from ai.operations.environment.config import (
    AQI_COLUMN,
    PM25_COLUMN,
    PM10_COLUMN,
    CO_COLUMN,
    CO2_COLUMN,
    NO2_COLUMN,
    SO2_COLUMN,
    ANOMALY_CONTAMINATION,
)


DEFAULT_FEATURES = [
    AQI_COLUMN,
    PM25_COLUMN,
    PM10_COLUMN,
    CO_COLUMN,
    CO2_COLUMN,
    NO2_COLUMN,
    SO2_COLUMN,
]


def detect_environment_anomalies(
    df: pd.DataFrame,
    features: list[str] | None = None,
    contamination: float = ANOMALY_CONTAMINATION,
    random_state: int = 42,
) -> pd.DataFrame:
    """Detect unusual environmental readings."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    data = df.copy()

    selected_features = features or DEFAULT_FEATURES

    available_features = [
        column
        for column in selected_features
        if column in data.columns
    ]

    if not available_features:
        raise ValueError(
            "No valid environment anomaly features were found."
        )

    feature_data = data[available_features].apply(
        pd.to_numeric,
        errors="coerce",
    )

    valid_mask = feature_data.notna().all(axis=1)

    if valid_mask.sum() < 2:
        raise ValueError(
            "At least two valid observations are required."
        )

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
    )

    predictions = model.fit_predict(
        feature_data.loc[valid_mask]
    )

    scores = model.decision_function(
        feature_data.loc[valid_mask]
    )

    data["anomaly_prediction"] = pd.NA
    data["anomaly_score"] = pd.NA
    data["anomaly_status"] = "Insufficient Data"

    data.loc[valid_mask, "anomaly_prediction"] = predictions
    data.loc[valid_mask, "anomaly_score"] = scores
    data.loc[valid_mask, "anomaly_status"] = [
        "Anomaly" if value == -1 else "Normal"
        for value in predictions
    ]

    return data