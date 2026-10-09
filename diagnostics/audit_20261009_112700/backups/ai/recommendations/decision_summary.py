from ai.recommendations.priority_engine import get_top_alerts
from ai.recommendations.rule_engine import (
    find_air_quality_issues,
    find_traffic_issues
)

from ai.assistant.data_retriever import (
    get_alerts,
    get_latest_air_quality_data,
    get_latest_traffic_data
)

def prioritize_air_quality_issues(air_quality_issues):
    """
    Assign a decision priority based on the database AQI category.

    The category comes directly from the project's AQI data.
    """

    prioritized = []

    for issue in air_quality_issues:

        category = (
            issue.get("aqi_category") or ""
        ).lower()

        if category == "unhealthy for sensitive groups":
            priority = 2

        elif category == "moderate":
            priority = 1

        else:
            priority = 0

        item = dict(issue)
        item["priority"] = priority

        prioritized.append(item)

    prioritized.sort(
        key=lambda item: item["priority"],
        reverse=True
    )

    return prioritized

def build_decision_summary(
    alerts,
    air_quality_data,
    traffic_data,
    limit=5
):
    """
    Build a clean decision summary for the current
    industrial estate status.
    """

    top_alerts = get_top_alerts(
        alerts,
        limit=limit
    )

    air_quality_issues = find_air_quality_issues(
        air_quality_data
    )

    air_quality_issues = prioritize_air_quality_issues(
        air_quality_issues
    )

    traffic_issues = find_traffic_issues(
        traffic_data
    )

    operational_problems = []

    # Add operational alerts
    for alert in top_alerts:

        alert_type = (
            alert.get("alert_type") or ""
        ).upper()

        # Keep data-quality alerts separate
        if alert_type in [
            "ANOMALY",
            "SENSOR_FAILURE"
        ]:
            continue

        operational_problems.append({
            "type": "alert",
            "alert_type": alert_type,
            "priority": alert["priority"],
            "severity": alert["severity"],
            "facility_id": alert["facility_id"],
            "facility_name": alert["facility_name"],
            "message": alert["message"],
            "reading_ts": alert["reading_ts"]
        })

    # Add serious AQI issues
    for issue in air_quality_issues:

        if issue["priority"] >= 2:

            operational_problems.append({
                "type": "air_quality",
                "priority": issue["priority"],
                "severity": "HIGH",
                "facility_id": issue["facility_id"],
                "facility_name": issue["facility_name"],
                "message": (
                    f"AQI is {issue['aqi']} "
                    f"({issue['aqi_category']})"
                ),
                "reading_ts": issue["reading_ts"]
            })

    # Add traffic issues
    for issue in traffic_issues:

        operational_problems.append({
            "type": "traffic",
            "priority": 2,
            "severity": "HIGH",
            "facility_id": issue["facility_id"],
            "facility_name": issue["facility_name"],
            "message": (
                f"Traffic congestion is "
                f"{issue['congestion_level']}"
            ),
            "reading_ts": issue["reading_ts"]
        })

    # Sort all operational problems
    operational_problems.sort(
        key=lambda item: item["priority"],
        reverse=True
    )

    # Keep only the most important problems
    operational_problems = operational_problems[:limit]

    # Keep data-quality issues separately
    data_quality_issues = []

    for alert in top_alerts:

        alert_type = (
            alert.get("alert_type") or ""
        ).upper()

        if alert_type in [
            "ANOMALY",
            "SENSOR_FAILURE"
        ]:
            data_quality_issues.append({
                "facility_id": alert["facility_id"],
                "facility_name": alert["facility_name"],
                "message": alert["message"],
                "severity": alert["severity"],
                "reading_ts": alert["reading_ts"]
            })

    return {
        "operational_problems": operational_problems,
        "data_quality_issues": data_quality_issues,
        "air_quality_issues": air_quality_issues,
        "traffic_issues": traffic_issues
    }

if __name__ == "__main__":

    alerts = get_alerts()
    air_quality_data = get_latest_air_quality_data()
    traffic_data = get_latest_traffic_data()

    result = build_decision_summary(
        alerts,
        air_quality_data,
        traffic_data
    )

    print("=== OPERATIONAL PROBLEMS ===")

    for problem in result["operational_problems"]:
        print(
            problem["severity"],
            "|",
            problem["facility_name"],
            "|",
            problem["message"]
        )

    print("\n=== DATA QUALITY ISSUES ===")

    for issue in result["data_quality_issues"]:
        print(
            issue["severity"],
            "|",
            issue["facility_name"],
            "|",
            issue["message"]
        )

    print("\n=== ALL AQI ISSUES ===")

    for issue in result["air_quality_issues"]:
        print(
            issue["facility_name"],
            "| AQI:",
            issue["aqi"],
            "|",
            issue["aqi_category"]
        )

    print("\n=== TRAFFIC ISSUES ===")

    for issue in result["traffic_issues"]:
        print(
            issue["facility_name"],
            "|",
            issue["congestion_level"]
        )