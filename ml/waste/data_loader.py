import pandas as pd

from data.loaders import load_waste_data


REQUIRED_COLUMNS = [
    "facility_id",
    "sensor_id",
    "reading_ts",
    "waste_type",
    "waste_quantity_kg",
    "recyclable_quantity_kg",
    "hazardous_quantity_kg",
]


def load_data() -> pd.DataFrame:
    """
    Load waste data using the common project loader.
    """
    data = load_waste_data()

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Waste loader must return a pandas DataFrame.")

    return data.copy()


def validate_columns(data: pd.DataFrame) -> bool:
    """
    Check that required waste columns exist.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing waste columns: {missing_columns}"
        )

    return True