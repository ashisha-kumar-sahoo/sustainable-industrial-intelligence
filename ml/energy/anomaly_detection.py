import pandas as pd


def detect_anomalies(
    data: pd.DataFrame,
    threshold: float = 0.20
) -> pd.DataFrame:
    """
    Detect abnormal energy consumption using percentage deviation
    from the average consumption.
    """

    df = data.copy()

    if "energy_consumption_kwh" not in df.columns:
        raise ValueError(
            "Missing column: energy_consumption_kwh"
        )

    if df.empty:
        df["expected_energy_kwh"] = pd.Series(dtype=float)
        df["anomaly_score"] = pd.Series(dtype=float)
        df["is_anomaly"] = pd.Series(dtype=bool)
        return df

    # Expected consumption
    expected = df["energy_consumption_kwh"].mean()

    df["expected_energy_kwh"] = expected

    # Percentage deviation
    if expected == 0:
        df["anomaly_score"] = 0.0
    else:
        df["anomaly_score"] = (
            (df["energy_consumption_kwh"] - expected).abs()
            / expected
        )

    # Anomaly flag
    df["is_anomaly"] = df["anomaly_score"] > threshold

    return df