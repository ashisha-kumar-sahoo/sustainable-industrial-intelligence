import pandas as pd


def detect_anomalies(
    data: pd.DataFrame,
    threshold: float = 0.20
) -> pd.DataFrame:
    """
    Detect abnormal water consumption using
    percentage deviation from average consumption.
    """

    df = data.copy()

    if "water_consumption_liters" not in df.columns:
        raise ValueError(
            "Missing column: water_consumption_liters"
        )

    if df.empty:
        df["expected_water_liters"] = pd.Series(dtype=float)
        df["anomaly_score"] = pd.Series(dtype=float)
        df["is_anomaly"] = pd.Series(dtype=bool)
        return df

    # Expected water consumption
    expected = df["water_consumption_liters"].mean()

    df["expected_water_liters"] = expected

    # Percentage deviation
    if expected == 0:
        df["anomaly_score"] = 0.0
    else:
        df["anomaly_score"] = (
            (df["water_consumption_liters"] - expected).abs()
            / expected
        )

    # Anomaly flag
    df["is_anomaly"] = df["anomaly_score"] > threshold

    return df