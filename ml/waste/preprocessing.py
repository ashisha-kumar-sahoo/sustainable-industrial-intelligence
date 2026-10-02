import pandas as pd


def preprocess_waste_data(data):
    """
    Prepare waste data for overflow prediction
    and collection priority.
    """

    data = data.copy()

    # Sort by facility, zone and time
    data = data.sort_values(
        by=[
            "facility_id",
            "zone_id",
            "timestamp"
        ]
    ).reset_index(drop=True)

    # Make sure fill level is numeric
    data["fill_level"] = pd.to_numeric(
        data["fill_level"],
        errors="coerce"
    )

    # Remove invalid fill levels
    data = data.dropna(
        subset=["fill_level"]
    )

    # Calculate previous fill level
    data["previous_fill_level"] = (
        data.groupby(
            ["facility_id", "zone_id"]
        )["fill_level"]
        .shift(1)
    )

    # Calculate time difference in hours
    data["time_diff_hours"] = (
        data.groupby(
            ["facility_id", "zone_id"]
        )["timestamp"]
        .diff()
        .dt.total_seconds()
        / 3600
    )

    # Calculate fill rate (% per hour)
    data["fill_rate"] = (
        (
            data["fill_level"]
            - data["previous_fill_level"]
        )
        / data["time_diff_hours"]
    )

    # First record or invalid time difference
    data["fill_rate"] = (
        data["fill_rate"]
        .replace(
            [float("inf"), -float("inf")],
            0
        )
        .fillna(0)
    )

    return data