import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "location",
    "vehicle_count",
    "average_speed",
    "occupancy",
]


def validate_traffic_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Validate traffic data supplied as a Pandas DataFrame.

    This function does not depend on a specific dataset
    or file.
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
    Return the required traffic data columns.
    """

    return REQUIRED_COLUMNS.copy()