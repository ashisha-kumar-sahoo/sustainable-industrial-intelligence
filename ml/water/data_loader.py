import pandas as pd

from data.loaders import load_water_data


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "water_consumption_liters",
    "flow_rate",
]


def load_data() -> pd.DataFrame:
    """
    Load water data using the common project loader.
    """
    data = load_water_data()

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Water loader must return a pandas DataFrame.")

    return data.copy()


def validate_columns(data: pd.DataFrame) -> bool:
    """
    Check that required water columns exist.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing water columns: {missing_columns}"
        )

    return True