import pandas as pd


REQUIRED_COLUMNS = [
    "facility_id",
    "zone_id",
    "timestamp",
    "water_liters",
    "flow_rate"
]


def validate_columns(data):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    return True


def preprocess_water_data(data):

    data = data.copy()

    # Check required columns
    validate_columns(data)

    # Convert timestamp
    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce"
    )

    # Convert water consumption to numeric
    data["water_liters"] = pd.to_numeric(
        data["water_liters"],
        errors="coerce"
    )

    # Convert flow rate to numeric
    data["flow_rate"] = pd.to_numeric(
        data["flow_rate"],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "timestamp",
            "water_liters",
            "flow_rate"
        ]
    )

    # Sort by time
    data = data.sort_values(
        by="timestamp"
    )

    # Reset index
    return data.reset_index(drop=True)