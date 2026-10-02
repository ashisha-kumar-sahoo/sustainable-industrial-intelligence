import pandas as pd


def detect_traffic_congestion(
    df: pd.DataFrame,
    speed_threshold=30,
    occupancy_threshold=70,
):
    """
    Detect traffic congestion using speed and occupancy.

    A record is classified as congested when:
    - average speed is below the speed threshold, AND
    - occupancy is at or above the occupancy threshold.
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
        "average_speed",
        "occupancy",
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

    result = df.copy()

    result["average_speed"] = pd.to_numeric(
        result["average_speed"],
        errors="coerce"
    )

    result["occupancy"] = pd.to_numeric(
        result["occupancy"],
        errors="coerce"
    )

    result = result.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    result["congestion_status"] = (
        (result["average_speed"] < speed_threshold)
        &
        (result["occupancy"] >= occupancy_threshold)
    ).map({
        True: "Congested",
        False: "Normal"
    })

    return result


def summarize_congestion(
    df: pd.DataFrame,
    status_column="congestion_status",
):
    """
    Summarize traffic congestion observations.
    """

    if status_column not in df.columns:
        raise ValueError(
            f"Column '{status_column}' not found."
        )

    return (
        df[status_column]
        .value_counts()
        .rename_axis("traffic_status")
        .reset_index(name="observation_count")
    )