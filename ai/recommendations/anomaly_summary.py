def get_top_anomalies(anomalies, limit=5):

    sorted_anomalies = sorted(
        anomalies,
        key=lambda x: abs(x.get("deviation_pct", 0)),
        reverse=True
    )

    return sorted_anomalies[:limit]