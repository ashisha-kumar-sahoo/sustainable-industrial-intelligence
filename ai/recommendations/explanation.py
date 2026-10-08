def explain_recommendation(recommendation):
    """
    Create a clear administrator-facing explanation
    from an existing recommendation.

    This function only reformats existing data.
    It does not invent measurements or causes.
    """

    facility = recommendation.get(
        "facility_name",
        "Unknown facility"
    )

    priority = recommendation.get(
        "priority",
        "LOW"
    )

    problem = recommendation.get(
        "problem",
        "No problem information available."
    )

    reason = recommendation.get(
        "reason",
        "No reason available."
    )

    action = recommendation.get(
        "recommended_action",
        "No recommended action available."
    )

    impact = recommendation.get(
        "estimated_impact"
    )

    explanation = {
        "facility": facility,
        "priority": priority,
        "problem": problem,
        "why_it_matters": reason,
        "recommended_action": action,
        "impact": impact
    }

    return explanation

if __name__ == "__main__":

    sample_recommendation = {
        "facility_name": "BoxCraft Packaging Unit",
        "priority": "CRITICAL",
        "problem": (
            "BoxCraft Packaging Unit used 10362.0 kWh "
            "in one day against a budget of 760.0 kWh "
            "(1263.4% over)"
        ),
        "reason": (
            "Energy consumption is above the recorded "
            "facility budget or limit."
        ),
        "recommended_action": (
            "Inspect major energy-consuming systems "
            "and investigate the cause of the high usage."
        ),
        "estimated_impact": {
            "excess_percentage": 1263.4,
            "actual_value": 10362.0,
            "limit_value": 760.0,
            "excess_value": 9602.0
        }
    }

    result = explain_recommendation(
        sample_recommendation
    )

    print("=== EXPLANATION ===")

    for key, value in result.items():
        print(f"{key}: {value}")