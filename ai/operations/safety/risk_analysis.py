"""Risk analysis for Safety Operations AI."""

import pandas as pd

from ai.operations.safety.config import (
    INCIDENT_COUNT_COLUMN,
    RESPONSE_TIME_COLUMN,
    SEVERITY_COLUMN,
    HIGH_INCIDENT_COUNT_THRESHOLD,
    HIGH_RESPONSE_TIME_THRESHOLD,
)


def calculate_safety_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate safety risk from incident indicators."""

    data = df.copy()

    data["risk_score"] = 0

    if INCIDENT_COUNT_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[INCIDENT_COUNT_COLUMN],
                errors="coerce",
            ) >= HIGH_INCIDENT_COUNT_THRESHOLD
        ).astype(int)

    if RESPONSE_TIME_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[RESPONSE_TIME_COLUMN],
                errors="coerce",
            ) >= HIGH_RESPONSE_TIME_THRESHOLD
        ).astype(int)

    if SEVERITY_COLUMN in data.columns:
        data["high_severity_flag"] = (
            data[SEVERITY_COLUMN]
            .astype(str)
            .str.upper()
            .eq("HIGH")
            .astype(int)
        )

        data["risk_score"] += data["high_severity_flag"]

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