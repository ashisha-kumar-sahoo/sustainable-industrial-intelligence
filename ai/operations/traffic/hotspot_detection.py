"""Traffic hotspot detection for Operations AI."""

import pandas as pd

from ai.operations.traffic.config import (
    FACILITY_COLUMN,
    VEHICLE_COUNT_COLUMN,
    SPEED_COLUMN,
    OCCUPANCY_COLUMN,
    HIGH_VEHICLE_COUNT_THRESHOLD,
    LOW_SPEED_THRESHOLD,
    HIGH_OCCUPANCY_THRESHOLD,
    HOTSPOT_SCORE_THRESHOLD,
)


def detect_traffic_hotspots(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Identify facilities with potential traffic congestion hotspots."""

    data = df.copy()

    required = [
        FACILITY_COLUMN,
        VEHICLE_COUNT_COLUMN,
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    numeric_columns = [
        VEHICLE_COUNT_COLUMN,
        SPEED_COLUMN,
        OCCUPANCY_COLUMN,
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    grouped = data.groupby(
        FACILITY_COLUMN,
        as_index=False,
    ).agg(
        average_vehicle_count=(
            VEHICLE_COUNT_COLUMN,
            "mean",
        ),
        maximum_vehicle_count=(
            VEHICLE_COUNT_COLUMN,
            "max",
        ),
        average_speed_kmph=(
            SPEED_COLUMN,
            "mean",
        ),
        average_lane_occupancy=(
            OCCUPANCY_COLUMN,
            "mean",
        ),
        observation_count=(
            VEHICLE_COUNT_COLUMN,
            "count",
        ),
    )

    grouped["hotspot_score"] = 0

    grouped.loc[
        grouped["average_vehicle_count"]
        >= HIGH_VEHICLE_COUNT_THRESHOLD,
        "hotspot_score",
    ] += 1

    grouped.loc[
        grouped["average_speed_kmph"]
        < LOW_SPEED_THRESHOLD,
        "hotspot_score",
    ] += 1

    grouped.loc[
        grouped["average_lane_occupancy"]
        >= HIGH_OCCUPANCY_THRESHOLD,
        "hotspot_score",
    ] += 1

    grouped["hotspot_status"] = "Normal"

    grouped.loc[
        grouped["hotspot_score"]
        >= HOTSPOT_SCORE_THRESHOLD,
        "hotspot_status",
    ] = "Potential Hotspot"

    return grouped