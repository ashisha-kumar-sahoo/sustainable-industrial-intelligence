import pandas as pd


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "waste_type",
    "waste_quantity_kg",
    "recyclable_quantity_kg",
    "hazardous_quantity_kg",
]


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare waste data for AI processing.
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
            f"Missing waste columns: {missing_columns}"
        )

    # Convert timestamp
    df["reading_ts"] = pd.to_datetime(
        df["reading_ts"],
        errors="coerce"
    )

    # Convert quantity columns to numeric
    numeric_columns = [
        "waste_quantity_kg",
        "recyclable_quantity_kg",
        "hazardous_quantity_kg",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove invalid rows
    df = df.dropna(subset=REQUIRED_COLUMNS)

    # Remove negative quantities
    df = df[
        (df["waste_quantity_kg"] >= 0)
        & (df["recyclable_quantity_kg"] >= 0)
        & (df["hazardous_quantity_kg"] >= 0)
    ]

    # Sort by timestamp
    df = df.sort_values("reading_ts").reset_index(drop=True)

    return df