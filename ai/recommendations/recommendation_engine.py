from ai.recommendations.impact_estimator import (
    calculate_excess,
    calculate_excess_quantity
)
from ai.recommendations.risk_score import calculate_risk


def create_recommendation(problem):
    """
    Convert a detected problem into an actionable recommendation.
    """

    problem_type = problem.get("type")

    alert_type = (
        problem.get("alert_type") or ""
    ).upper()

    severity = problem.get(
        "severity",
        "LOW"
    )

    recommendation = {
        "facility_id": problem.get("facility_id"),
        "facility_name": problem.get("facility_name"),
        "problem": problem.get("message"),
        "evidence": problem.get("message"),
        "priority": severity,
        "reason": "",
        "recommended_action": "",
        "estimated_impact": None
    }
    recommendation["risk"] = calculate_risk(problem)

    # Calculate deterministic impact
    percentage_impact = calculate_excess(
        problem
    )

    quantity_impact = calculate_excess_quantity(
        problem
    )

    if percentage_impact or quantity_impact:

        recommendation["estimated_impact"] = {
            "excess_percentage": (
                percentage_impact.get(
                    "excess_percentage"
                )
                if percentage_impact
                else None
            ),
            "actual_value": (
                quantity_impact.get(
                    "actual_value"
                )
                if quantity_impact
                else None
            ),
            "limit_value": (
                quantity_impact.get(
                    "limit_value"
                )
                if quantity_impact
                else None
            ),
            "excess_value": (
                quantity_impact.get(
                    "excess_value"
                )
                if quantity_impact
                else None
            )
        }

    # Alert recommendations
    if problem_type == "alert":

        if "ENERGY" in alert_type:

            recommendation["recommended_action"] = (
                "Inspect major energy-consuming systems "
                "and investigate the cause of the high usage."
            )

            recommendation["reason"] = (
                "Energy consumption is above the recorded "
                "facility budget or limit."
            )

        elif "WATER" in alert_type:

            recommendation["recommended_action"] = (
                "Inspect major water-consuming processes "
                "and check for abnormal water usage."
            )

            recommendation["reason"] = (
                "Water consumption is above the recorded "
                "facility budget or limit."
            )

        elif "WASTE" in alert_type:

            recommendation["recommended_action"] = (
                "Inspect the waste-generating process "
                "and review waste handling at the facility."
            )

            recommendation["reason"] = (
                "Waste generation is above the recorded "
                "facility limit."
            )

        else:

            recommendation["recommended_action"] = (
                "Investigate the reported facility issue."
            )

            recommendation["reason"] = (
                "A high-priority alert was recorded "
                "for the facility."
            )

    # M3 energy anomaly recommendations
    elif problem_type == "energy_anomaly":

        recommendation["recommended_action"] = (
            "Inspect the facility's major energy-consuming "
            "systems and investigate the abnormal energy reading."
        )

        recommendation["reason"] = (
            "M3 detected an energy consumption anomaly "
            "compared with the expected energy value."
        )

        recommendation["estimated_impact"] = {
            "actual_value": problem.get(
                "actual_value"
            ),
            "expected_value": problem.get(
                "expected_value"
            ),
            "deviation_pct": problem.get(
                "deviation_pct"
            )
        }

    # Air quality recommendations
    elif problem_type == "air_quality":

        recommendation["recommended_action"] = (
            "Inspect the affected area and review the "
            "sources contributing to poor air quality."
        )

        recommendation["reason"] = (
            "The recorded AQI category indicates "
            "an environmental concern."
        )

    # Traffic recommendations
    elif problem_type == "traffic":

        recommendation["recommended_action"] = (
            "Inspect the affected traffic zone and "
            "review traffic flow conditions."
        )

        recommendation["reason"] = (
            "The recorded congestion level indicates "
            "a traffic concern."
        )

    elif problem_type == "water_anomaly":
        recommendation["recommended_action"] = (
            "Check for leaks and review water-intensive processes."
        )
        recommendation["reason"] = (
            "PostgreSQL marks this water reading as anomalous."
        )

    elif problem_type == "waste_anomaly":
        recommendation["recommended_action"] = (
            "Review the waste-generating process and collection schedule."
        )
        recommendation["reason"] = (
            "PostgreSQL marks this waste reading as anomalous."
        )

    return recommendation


def generate_recommendations(problems):
    recommendations = []

    for problem in problems:
        recommendations.append(
            create_recommendation(problem)
        )

    risk_order = {
        "CRITICAL": 3,
        "HIGH": 2,
        "MEDIUM": 1,
        "LOW": 0
    }

    recommendations.sort(
        key=lambda item: (
            risk_order.get(item.get("risk", "LOW"), 0),
            abs((item.get("estimated_impact") or {}).get("deviation_pct") or 0)
        ),
        reverse=True
    )

    return recommendations


if __name__ == "__main__":

    from ai.assistant.data_retriever import (
        get_alerts,
        get_latest_air_quality_data,
        get_latest_traffic_data
    )

    from ai.recommendations.decision_summary import (
        build_decision_summary
    )

    # Get real database data
    alerts = get_alerts()

    air_quality_data = (
        get_latest_air_quality_data()
    )

    traffic_data = (
        get_latest_traffic_data()
    )

    # Build real operational problems
    decision = build_decision_summary(
        alerts,
        air_quality_data,
        traffic_data
    )

    operational_problems = (
        decision["operational_problems"]
    )

    # Generate recommendations
   
