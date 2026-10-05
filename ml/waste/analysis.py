import pandas as pd


def analyze_waste(data: pd.DataFrame) -> dict:
    """
    Calculate basic waste analysis metrics.
    """

    if data.empty:
        return {
            "total_waste_kg": 0.0,
            "average_waste_kg": 0.0,
            "total_recyclable_kg": 0.0,
            "total_hazardous_kg": 0.0,
            "recyclable_percentage": 0.0,
            "hazardous_percentage": 0.0,
            "reading_count": 0,
        }

    required_columns = [
        "waste_quantity_kg",
        "recyclable_quantity_kg",
        "hazardous_quantity_kg",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing waste columns: {missing_columns}"
        )

    total_waste = data["waste_quantity_kg"].sum()
    total_recyclable = data["recyclable_quantity_kg"].sum()
    total_hazardous = data["hazardous_quantity_kg"].sum()

    if total_waste > 0:
        recyclable_percentage = (
            total_recyclable / total_waste
        ) * 100

        hazardous_percentage = (
            total_hazardous / total_waste
        ) * 100
    else:
        recyclable_percentage = 0.0
        hazardous_percentage = 0.0

    return {
        "total_waste_kg": float(total_waste),
        "average_waste_kg": float(
            data["waste_quantity_kg"].mean()
        ),
        "total_recyclable_kg": float(total_recyclable),
        "total_hazardous_kg": float(total_hazardous),
        "recyclable_percentage": float(recyclable_percentage),
        "hazardous_percentage": float(hazardous_percentage),
        "reading_count": int(len(data)),
    }