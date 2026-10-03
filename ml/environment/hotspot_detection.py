import pandas as pd


def detect_pollution_hotspots(
    df: pd.DataFrame,
    group_column="location",
    aqi_column="aqi",
    threshold=100,
):
    """
    Detect potential pollution hotspots.

    The function groups observations by location and
    calculates the average AQI.

    A location is marked as a potential hotspot when
    its average AQI is greater than or equal to
    the supplied threshold.
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
        aqi_column,
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

    data[aqi_column] = pd.to_numeric(
        data[aqi_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[group_column, aqi_column]
    )

    if data.empty:
        raise ValueError(
            "No valid observations available."
        )

    summary = (
        data
        .groupby(group_column)
        .agg(
            average_aqi=(aqi_column, "mean"),
            maximum_aqi=(aqi_column, "max"),
            observation_count=(aqi_column, "count"),
        )
        .reset_index()
    )

    summary["hotspot_status"] = summary[
        "average_aqi"
    ].apply(
        lambda value:
        "Potential Hotspot"
        if value >= threshold
        else "Normal"
    )

    return summary


def get_hotspot_locations(
    hotspot_summary: pd.DataFrame,
):
    """
    Return only locations identified as
    potential pollution hotspots.
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