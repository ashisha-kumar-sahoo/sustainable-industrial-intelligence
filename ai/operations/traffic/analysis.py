"""Analysis and structured results for Traffic Operations AI."""

import pandas as pd

from ai.operations.traffic.config import (
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    SENSOR_COLUMN,
    VEHICLE_COUNT_COLUMN,
    HEAVY_VEHICLE_COUNT_COLUMN,
    SPEED_COLUMN,
    CONGESTION_COLUMN,
    OCCUPANCY_COLUMN,
)


def calculate_traffic_risk(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate a row-level traffic risk score."""

    data = df.copy()

    data["risk_score"] = 0

    if VEHICLE_COUNT_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[VEHICLE_COUNT_COLUMN],
                errors="coerce",
            ) >= 200
        ).astype(int)

    if SPEED_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[SPEED_COLUMN],
                errors="coerce",
            ) < 20
        ).astype(int)

    if OCCUPANCY_COLUMN in data.columns:
        data["risk_score"] += (
            pd.to_numeric(
                data[OCCUPANCY_COLUMN],
                errors="coerce",
            ) >= 80
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


def build_traffic_results(
    df: pd.DataFrame,
    hotspots: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return structured traffic results for the M5 dashboard."""

    data = calculate_traffic_risk(df)

    result_columns = [
        TIMESTAMP_COLUMN,
        FACILITY_COLUMN,
        SENSOR_COLUMN,
        VEHICLE_COUNT_COLUMN,
        HEAVY_VEHICLE_COUNT_COLUMN,
        SPEED_COLUMN,
        CONGESTION_COLUMN,
        OCCUPANCY_COLUMN,
        "risk_score",
        "risk_level",
    ]

    available_columns = [
        column
        for column in result_columns
        if column in data.columns
    ]

    results = data[available_columns].copy()

    if hotspots is not None and not hotspots.empty:
        hotspot_columns = [
            FACILITY_COLUMN,
            "hotspot_score",
            "hotspot_status",
        ]

        available_hotspot_columns = [
            column
            for column in hotspot_columns
            if column in hotspots.columns
        ]

        if FACILITY_COLUMN in available_hotspot_columns:
            results = results.merge(
                hotspots[available_hotspot_columns],
                on=FACILITY_COLUMN,
                how="left",
            )

    return results