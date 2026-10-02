import pandas as pd


NUMERIC_COLUMNS = [
    "vehicle_count",
    "average_speed",
    "occupancy",
]


def preprocess_traffic_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean and prepare traffic data.

    Accepts any compatible DataFrame and does not
    depend on a specific dataset.
    """

    df = df.copy()

    # Convert timestamp
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

    # Remove invalid numerical observations
    available_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    df = df.dropna(
        subset=available_columns
    ).reset_index(drop=True)

    # Sort by location and timestamp
    if "location" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(
            by=["location", "timestamp"]
        ).reset_index(drop=True)

    return df


def create_traffic_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create reusable traffic intelligence features.
    """

    df = df.copy()

    # Traffic density indicator
    if {
        "vehicle_count",
        "occupancy"
    }.issubset(df.columns):

        df["traffic_load"] = (
            df["vehicle_count"] *
            df["occupancy"] / 100
        )

    # Low-speed indicator
    if "average_speed" in df.columns:
        df["low_speed_flag"] = (
            df["average_speed"] < 30
        ).astype(int)

    # High occupancy indicator
    if "occupancy" in df.columns:
        df["high_occupancy_flag"] = (
            df["occupancy"] >= 70
        ).astype(int)

    return df