import pandas as pd


def detect_anomalies(
    data,
    threshold=20
):
    """
    Detect abnormal energy consumption
    using percentage deviation from the
    previous energy consumption.
    """

    data = data.copy()

    # Default values
    data["anomaly"] = False
    data["severity"] = "NORMAL"

    # Medium anomaly
    data.loc[
        data["change_pct"].abs() > 10,
        "severity"
    ] = "MEDIUM"

    # High anomaly
    data.loc[
        data["change_pct"].abs() > threshold,
        "severity"
    ] = "HIGH"

    # Anomaly if change is greater than 10%
    data["anomaly"] = (
        data["change_pct"].abs() > 10
    )

    # Expected energy value
    data["expected_value"] = (
        data["previous_energy"]
    )

    # Deviation percentage
    data["deviation_pct"] = (
        data["change_pct"]
    )

    return data