import pandas as pd


def load_from_dataframe(data):
    """
    Load and validate energy data from a pandas DataFrame.
    """

    data = data.copy()

    required_columns = [
        "facility_id",
        "zone_id",
        "timestamp",
        "energy_kwh"
    ]

    # Check required columns
    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    # Convert timestamp
    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce"
    )

    # Convert energy value
    data["energy_kwh"] = pd.to_numeric(
        data["energy_kwh"],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "facility_id",
            "zone_id",
            "timestamp",
            "energy_kwh"
        ]
    )

    # Energy cannot be negative
    data = data[
        data["energy_kwh"] >= 0
    ]

    # Sort by facility, zone and time
    data = data.sort_values(
        by=[
            "facility_id",
            "zone_id",
            "timestamp"
        ]
    ).reset_index(drop=True)

    return data