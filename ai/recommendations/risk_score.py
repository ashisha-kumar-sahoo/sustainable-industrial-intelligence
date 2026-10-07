def calculate_risk(anomaly):

    deviation = abs(
        anomaly.get("deviation_pct", 0)
    )

    if deviation > 300:
        return "CRITICAL"

    elif deviation > 100:
        return "HIGH"

    elif deviation > 30:
        return "MEDIUM"

    else:
        return "LOW"