import pandas as pd


def preprocess_energy_data(data):
    """
    Prepare energy data for anomaly detection
    and forecasting.
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

    # Make sure energy values are numeric
    data["energy_kwh"] = pd.to_numeric(
        data["energy_kwh"],
        errors="coerce"
    )

    # Remove invalid energy values
    data = data.dropna(
        subset=["energy_kwh"]
    )

    # Calculate previous energy consumption
    data["previous_energy"] = (
        data.groupby(
            ["facility_id", "zone_id"]
        )["energy_kwh"]
        .shift(1)
    )

    # Calculate percentage change
    data["change_pct"] = (
        (
            data["energy_kwh"]
            - data["previous_energy"]
        )
        / data["previous_energy"]
    ) * 100

    # First record has no previous value
    data["change_pct"] = (
        data["change_pct"].fillna(0)
    )

    return data