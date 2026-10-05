import pandas as pd


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "energy_consumption_kwh",
]


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare energy data for AI processing.
    """

    df = data.copy()

    # Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing energy columns: {missing_columns}"
        )

    # Convert timestamp
    df["reading_ts"] = pd.to_datetime(
        df["reading_ts"],
        errors="coerce"
    )

    # Convert energy consumption to numeric
    df["energy_consumption_kwh"] = pd.to_numeric(
        df["energy_consumption_kwh"],
        errors="coerce"
    )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "facility_id",
            "sensor_id",
            "reading_ts",
            "energy_consumption_kwh",
        ]
    )

    # Remove negative energy values
    df = df[df["energy_consumption_kwh"] >= 0]

    # Sort by time
    df = df.sort_values("reading_ts").reset_index(drop=True)

    return df