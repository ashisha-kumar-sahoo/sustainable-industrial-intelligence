import pandas as pd


def load_from_dataframe(data):
    """
    Load and validate waste data from a pandas DataFrame.
    """

    data = data.copy()

    required_columns = [
        "facility_id",
        "zone_id",
        "timestamp",
        "fill_level",
        "waste_type"
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

    # Convert fill level to numeric
    data["fill_level"] = pd.to_numeric(
        data["fill_level"],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "facility_id",
            "zone_id",
            "timestamp",
            "fill_level",
            "waste_type"
        ]
    )

    # Fill level must be between 0 and 100
    data = data[
        (data["fill_level"] >= 0) &
        (data["fill_level"] <= 100)
    ]

    # Sort by facility, zone and timestamp
    data = data.sort_values(
        by=[
            "facility_id",
            "zone_id",
            "timestamp"
        ]
    ).reset_index(drop=True)
    return data