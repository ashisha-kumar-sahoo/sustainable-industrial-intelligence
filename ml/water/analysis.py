import pandas as pd


def analyze_water(data: pd.DataFrame) -> dict:
    """
    Calculate basic water consumption analysis metrics.
    """

    if data.empty:
        return {
            "total_water_liters": 0.0,
            "average_water_liters": 0.0,
            "maximum_water_liters": 0.0,
            "minimum_water_liters": 0.0,
            "average_flow_rate": 0.0,
            "reading_count": 0,
        }

    required_columns = [
        "water_consumption_liters",
        "flow_rate",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing water columns: {missing_columns}"
        )

    water = data["water_consumption_liters"]
    flow = data["flow_rate"]

    return {
        "total_water_liters": float(water.sum()),
        "average_water_liters": float(water.mean()),
        "maximum_water_liters": float(water.max()),
        "minimum_water_liters": float(water.min()),
        "average_flow_rate": float(flow.mean()),
        "reading_count": int(len(data)),
    }