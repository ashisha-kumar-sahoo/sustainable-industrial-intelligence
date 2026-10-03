import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "location",
    "aqi",
    "pm25",
    "pm10",
    "temperature",
    "co2",
    "no2",
]


def validate_environment_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate environmental data supplied as a Pandas DataFrame.

    This function does NOT load a CSV or depend on
    any specific dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    return df.copy()


def get_required_columns():
    """
    Return the required environmental data columns.
    """

    return REQUIRED_COLUMNS.copy()