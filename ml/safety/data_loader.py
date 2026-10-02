import pandas as pd

REQUIRED_COLUMNS = [
    "timestamp",
    "location",
    "incident_type",
    "severity",
    "people_affected",
    "response_time",
]


def validate_safety_data(
    df: pd.DataFrame
) -> pd.DataFrame:

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
    return REQUIRED_COLUMNS.copy()