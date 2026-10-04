"""Anomaly detection for Equipment Operations AI."""

import pandas as pd
from sklearn.ensemble import IsolationForest

from ai.operations.equipment.config import (
    TEMPERATURE_COLUMN,
    VIBRATION_COLUMN,
    ENERGY_COLUMN,
    ANOMALY_CONTAMINATION,
)


DEFAULT_FEATURES = [
    TEMPERATURE_COLUMN,
    VIBRATION_COLUMN,
    ENERGY_COLUMN,
]


def detect_equipment_anomalies(
    df: pd.DataFrame,
    features: list[str] | None = None,
    contamination: float = ANOMALY_CONTAMINATION,
    random_state: int = 42,
) -> pd.DataFrame:
    """Detect unusual equipment readings."""

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
            "No valid equipment anomaly features were found."
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

    data.loc[
        valid_mask,
        "anomaly_status",
    ] = [
        "Anomaly" if value == -1 else "Normal"
        for value in predictions
    ]

    return data