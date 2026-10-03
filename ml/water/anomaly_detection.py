import pandas as pd


def detect_anomalies(
    data,
    window=3,
    threshold=20
):
    data = data.copy()

    # Previous values se expected baseline calculate karo
    data["expected_value"] = (
        data["water_liters"]
        .shift(1)
        .rolling(
            window=window,
            min_periods=1
        )
        .mean()
    )

    # First row ke liye current value use karo
    data["expected_value"] = (
        data["expected_value"]
        .fillna(data["water_liters"])
    )

    # Percentage deviation calculate karo
    data["deviation_pct"] = (
        (
            data["water_liters"]
            - data["expected_value"]
        )
        / data["expected_value"]
    ) * 100

    # Default values
    data["anomaly"] = False
    data["severity"] = "NORMAL"

    # Medium anomaly: >10%
    data.loc[
        data["deviation_pct"].abs() > 10,
        "severity"
    ] = "MEDIUM"

    # High anomaly: >20%
    data.loc[
        data["deviation_pct"].abs() > 20,
        "severity"
    ] = "HIGH"

    # >10% deviation ko abnormal/anomaly maana jayega
    data["anomaly"] = (
        data["deviation_pct"].abs() > 10
    )

    return data