import pandas as pd


NUMERIC_COLUMNS = [
    "people_affected",
    "response_time",
]


def preprocess_safety_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Preprocess safety incident data.

    The function works with any compatible DataFrame
    and does not depend on a specific dataset or file.
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

    # Remove invalid numeric observations
    available_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    if available_columns:
        df = df.dropna(
            subset=available_columns
        ).reset_index(drop=True)

    # Standardize text fields
    if "location" in df.columns:
        df["location"] = df["location"].astype(str).str.strip()

    if "incident_type" in df.columns:
        df["incident_type"] = (
            df["incident_type"]
            .astype(str)
            .str.strip()
        )

    if "severity" in df.columns:
        df["severity"] = (
            df["severity"]
            .astype(str)
            .str.strip()
            .str.title()
        )

    # Sort chronologically by location
    if "location" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(
            by=["location", "timestamp"]
        ).reset_index(drop=True)

    return df


def create_safety_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create general-purpose safety monitoring features.
    """

    df = df.copy()

    # High severity indicator
    if "severity" in df.columns:
        df["high_severity_flag"] = (
            df["severity"].isin(
                ["High", "Critical"]
            )
        ).astype(int)

    # Large impact indicator
    if "people_affected" in df.columns:
        df["high_impact_flag"] = (
            df["people_affected"] >= 3
        ).astype(int)

    # Slow response indicator
    if "response_time" in df.columns:
        df["slow_response_flag"] = (
            df["response_time"] >= 15
        ).astype(int)

    return df