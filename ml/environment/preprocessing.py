import pandas as pd


NUMERIC_COLUMNS = [
    "aqi",
    "pm25",
    "pm10",
    "temperature",
    "co2",
    "no2",
]


def preprocess_environment_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare environmental data.

    The function accepts any compatible DataFrame
    and does not load data from a file.
    """

    df = df.copy()

    # Convert timestamp when available
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    # Convert numerical features
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Remove rows with invalid required numeric values
    available_numeric_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    df = df.dropna(
        subset=available_numeric_columns
    ).reset_index(drop=True)

    # Sort by location and timestamp when available
    if "location" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(
            by=["location", "timestamp"]
        ).reset_index(drop=True)

    return df


def create_environment_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create reusable environmental ML features.
    """

    df = df.copy()

    # PM2.5 to PM10 ratio
    if {"pm25", "pm10"}.issubset(df.columns):
        df["pm_ratio"] = (
            df["pm25"] /
            df["pm10"].replace(0, pd.NA)
        )

    # Combined pollution indicator
    available = [
        column
        for column in ["aqi", "pm25", "pm10"]
        if column in df.columns
    ]

    if available:
        df["pollution_index"] = (
            df[available].mean(axis=1)
        )

    # AQI threshold flag
    if "aqi" in df.columns:
        df["high_aqi_flag"] = (
            df["aqi"] >= 100
        ).astype(int)

    return df