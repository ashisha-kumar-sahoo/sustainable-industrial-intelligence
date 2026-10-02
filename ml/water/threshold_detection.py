def detect_threshold(
    actual_value,
    expected_value,
    threshold_percent=20
):

    if expected_value <= 0:

        return {
            "anomaly": False,
            "deviation_pct": None,
            "severity": "UNKNOWN"
        }

    deviation = (
        (actual_value - expected_value)
        / expected_value
    ) * 100

    if deviation > threshold_percent:

        severity = "HIGH"

    elif deviation > 10:

        severity = "MEDIUM"

    else:

        severity = "NORMAL"

    return {
        "anomaly": deviation > threshold_percent,
        "deviation_pct": round(
            deviation,
            2
        ),
        "severity": severity
    }