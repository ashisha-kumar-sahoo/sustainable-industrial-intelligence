import pandas as pd


def detect_safety_hotspots(
    df: pd.DataFrame,
    location_column="location",
    risk_column="safety_risk",
    incident_column="incident_type",
):
    """
    Identify locations with repeated or higher-risk safety incidents.
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
        location_column,
        risk_column,
        incident_column,
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

    data[risk_column] = (
        data[risk_column]
        .astype(str)
        .str.strip()
        .str.title()
    )

    summary = (
        data.groupby(location_column)
        .agg(
            incident_count=(incident_column, "count"),
            high_risk_incidents=(
                risk_column,
                lambda values: (values == "High").sum()
            ),
        )
        .reset_index()
    )

    summary["hotspot_status"] = (
        (
            (summary["incident_count"] >= 2)
            | (summary["high_risk_incidents"] >= 1)
        ).map({
            True: "Potential Hotspot",
            False: "Normal"
        })
    )

    return summary


def get_safety_hotspots(
    hotspot_summary: pd.DataFrame,
):
    """
    Return locations identified as potential safety hotspots.
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