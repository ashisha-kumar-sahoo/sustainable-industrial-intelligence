import pandas as pd


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "water_consumption_liters",
    "flow_rate",
]


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare water data for AI processing.
    """

    df = data.copy()

    # Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing water columns: {missing_columns}"
        )

    # Convert timestamp
    df["reading_ts"] = pd.to_datetime(
        df["reading_ts"],
        errors="coerce"
    )

    # Convert numeric columns
    df["water_consumption_liters"] = pd.to_numeric(
        df["water_consumption_liters"],
        errors="coerce"
    )

    df["flow_rate"] = pd.to_numeric(
        df["flow_rate"],
        errors="coerce"
    )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "facility_id",
            "sensor_id",
            "reading_ts",
            "water_consumption_liters",
            "flow_rate",
        ]
    )

    # Remove negative values
    df = df[
        (df["water_consumption_liters"] >= 0)
        & (df["flow_rate"] >= 0)
    ]

    # Sort by timestamp
    df = df.sort_values("reading_ts").reset_index(drop=True)

    return df