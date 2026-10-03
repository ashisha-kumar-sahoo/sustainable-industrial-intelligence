import pandas as pd


def detect_traffic_hotspots(
    df: pd.DataFrame,
    group_column="location",
    vehicle_column="vehicle_count",
    speed_column="average_speed",
    occupancy_column="occupancy",
    vehicle_threshold=100,
    speed_threshold=30,
    occupancy_threshold=70,
):
    """
    Detect potential traffic hotspots by location.

    A location is considered a potential hotspot when
    its average traffic indicators satisfy the supplied
    thresholds.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    required_columns = [
        group_column,
        vehicle_column,
        speed_column,
        occupancy_column,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    data = df.copy()

    for column in [
        vehicle_column,
        speed_column,
        occupancy_column,
    ]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(
        subset=required_columns
    )

    if data.empty:
        raise ValueError(
            "No valid observations available."
        )

    summary = (
        data
        .groupby(group_column)
        .agg(
            average_vehicle_count=(
                vehicle_column,
                "mean"
            ),
            average_speed=(
                speed_column,
                "mean"
            ),
            average_occupancy=(
                occupancy_column,
                "mean"
            ),
        )
        .reset_index()
    )

    summary["hotspot_status"] = (
        (
            (summary["average_vehicle_count"]
             >= vehicle_threshold)
            &
            (summary["average_speed"]
             < speed_threshold)
            &
            (summary["average_occupancy"]
             >= occupancy_threshold)
        )
        .map({
            True: "Potential Hotspot",
            False: "Normal"
        })
    )

    return summary


def get_traffic_hotspots(
    hotspot_summary: pd.DataFrame,
):
    """
    Return only locations identified as
    potential traffic hotspots.
    """

    if "hotspot_status" not in hotspot_summary.columns:
        raise ValueError(
            "Hotspot summary must contain "
            "'hotspot_status'."
        )

    return hotspot_summary[
        hotspot_summary["hotspot_status"]
        == "Potential Hotspot"
    ].copy()