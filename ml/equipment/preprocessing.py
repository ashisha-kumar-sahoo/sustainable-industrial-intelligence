import pandas as pd

NUMERIC_COLUMNS = [
    "temperature",
    "vibration",
    "operating_hours",
    "utilization",
]


def preprocess_equipment_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Preprocess equipment data supplied as a Pandas DataFrame.

    The function does not depend on a specific dataset
    or file.
    """

    df = df.copy()

    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    # Convert numeric columns
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Remove rows with invalid numeric values
    available_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    if available_columns:
        df = df.dropna(
            subset=available_columns
        ).reset_index(drop=True)

    # Sort equipment records chronologically
    if "equipment_id" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(
            by=["equipment_id", "timestamp"]
        ).reset_index(drop=True)

    return df


def create_equipment_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create general-purpose equipment monitoring features.
    """

    df = df.copy()

    # High temperature indicator
    if "temperature" in df.columns:
        df["high_temperature_flag"] = (
            df["temperature"] >= 80
        ).astype(int)

    # High vibration indicator
    if "vibration" in df.columns:
        df["high_vibration_flag"] = (
            df["vibration"] >= 5
        ).astype(int)

    # High utilization indicator
    if "utilization" in df.columns:
        df["high_utilization_flag"] = (
            df["utilization"] >= 80
        ).astype(int)

    return df