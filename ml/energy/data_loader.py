import pandas as pd

from data.loaders import load_energy_data


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "energy_consumption_kwh",
]


def load_data() -> pd.DataFrame:
    """
    Load energy data using the common project loader.
    """
    data = load_energy_data()

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Energy loader must return a pandas DataFrame.")

    return data.copy()


def validate_columns(data: pd.DataFrame) -> bool:
    """
    Check that required energy columns exist.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing energy columns: {missing_columns}"
        )

    return True