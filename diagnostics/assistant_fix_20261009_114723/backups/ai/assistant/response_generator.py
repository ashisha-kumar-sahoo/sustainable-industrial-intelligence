from collections import Counter


def create_response(summary, evidence, recommended_action, data_basis):
    """
    Create a structured response for the AI Assistant.
    """

    return {
        "summary": summary,
        "evidence": evidence,
        "recommended_action": recommended_action,
        "data_basis": data_basis
    }


def create_energy_anomaly_response(
    anomalies,
    recommendations
):
    """
    Create a user-facing response for energy anomalies.
    """

    total = len(anomalies)

    if total == 0:
        return create_response(
            summary="No current energy anomalies were detected.",
            evidence=[],
            recommended_action="No immediate energy action is required.",
            data_basis="M3 energy intelligence results"
        )

    severities = Counter(
        (item.get("severity") or "UNCLASSIFIED").upper()
        for item in anomalies
    )
    critical_count = severities["CRITICAL"]
    high_count = severities["HIGH"]
    medium_count = severities["MEDIUM"]
    low_count = severities["LOW"]
    unclassified_count = total - sum(
        (critical_count, high_count, medium_count, low_count)
    )

    top = recommendations[0] if recommendations else None

    summary = (
        f"{total} facilities currently have energy anomalies. "
        f"{critical_count} are critical, "
        f"{high_count} are high risk, and "
        f"{medium_count} are medium risk, {low_count} are low risk"
        + (f", and {unclassified_count} are unclassified." if unclassified_count else ".")
    )

    evidence = []

    for anomaly in sorted(
            anomalies,
            key=lambda x: abs(x.get("deviation_pct", 0)),
            reverse=True
        )[:5]:
        evidence.append(
            f"{anomaly.get('facility_name')}: "
            f"{anomaly.get('deviation_pct')}% deviation "
            f"({anomaly.get('actual_value')} kWh actual vs "
            f"{anomaly.get('expected_value')} kWh expected); "
            f"severity {anomaly.get('severity', 'unclassified')}."
        )

    recommended_action = (
        f"Prioritize inspection of "
        f"{top.get('facility_name')} because it has the "
        f"highest current energy deviation."
    ) if top else "Review the anomaly evidence and verify the readings."

    return create_response(
        summary=summary,
        evidence=evidence,
        recommended_action=recommended_action,
        data_basis="M3 energy intelligence results"
    )


if __name__ == "__main__":

    response = create_response(
        summary="WeaveWorld Dyeing Unit has an elevated air quality reading.",
        evidence=[
            "AQI: 139",
            "Category: Unhealthy for Sensitive Groups"
        ],
        recommended_action="Inspect the air quality conditions at the facility.",
        data_basis="air_quality_readings"
    )

    print("Response:")
    print(response)
