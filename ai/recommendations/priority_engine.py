def calculate_priority(alert):
    """
    Convert alert severity into a numeric priority.
    Higher number = higher priority.
    """

    severity = alert.get("severity", "").upper()

    if severity == "CRITICAL":
        return 3

    if severity == "HIGH":
        return 2

    if severity == "MEDIUM":
        return 1

    return 0


def prioritize_alerts(alerts):
    """
    Sort alerts from highest priority to lowest priority.
    """

    if not alerts:
        return []

    prioritized = []

    for alert in alerts:
        item = dict(alert)
        item["priority"] = calculate_priority(alert)
        prioritized.append(item)

    prioritized.sort(
        key=lambda item: item["priority"],
        reverse=True
    )

    return prioritized


def get_top_alerts(alerts, limit=5):
    """
    Return the most important alerts from the latest date.
    """

    current_alerts = get_current_alerts(alerts)

    prioritized = prioritize_alerts(current_alerts)

    return prioritized[:limit]

def get_current_alerts(alerts):
    """
    Keep only alerts from the latest available alert date.
    """

    if not alerts:
        return []

    valid_alerts = [
        alert
        for alert in alerts
        if alert.get("reading_ts") is not None
    ]

    if not valid_alerts:
        return []

    latest_date = max(
        alert["reading_ts"].date()
        for alert in valid_alerts
    )

    return [
        alert
        for alert in valid_alerts
        if alert["reading_ts"].date() == latest_date
    ]

if __name__ == "__main__":

    from ai.assistant.data_retriever import get_alerts

    alerts = get_alerts()

    current_alerts = get_current_alerts(alerts)

    top_alerts = get_top_alerts(current_alerts, limit=5)

    print("Current Alerts:")
    print(len(current_alerts))

    print("\nTop Alerts:")

    for alert in top_alerts:
        print(alert)