def calculate_excess(problem):
    """
    Calculate how much a measured value exceeds
    its recorded budget or limit.

    This uses only values already present
    in the alert message.
    """

    message = problem.get("message")

    if not isinstance(message, str) or "over)" not in message:
        return None

    try:
        percentage_part = message.split("(")[-1]
        percentage = percentage_part.split("%")[0]

        return {
            "excess_percentage": float(percentage)
        }

    except (ValueError, IndexError):
        return None

def calculate_excess_quantity(problem):
    """
    Calculate the excess quantity from an alert message.

    Uses the actual value and budget/limit already
    present in the alert message.
    """

    message = problem.get("message")

    if not isinstance(message, str):
        return None

    try:
        import re

        # Find the actual measured value.
        # Examples:
        # "used 105120 litres"
        # "used 10362.0 kWh"
        # "generated 1243.5 kg"

        actual_match = re.search(
            r"\b(?:used|generated)\s+(\d+(?:\.\d+)?)",
            message,
            re.IGNORECASE
        )

        if not actual_match:
            return None

        actual_value = float(
            actual_match.group(1)
        )

        # Find the budget or limit.
        # Examples:
        # "against a budget of 82000 litres"
        # "against a limit of 920.0 kg"

        limit_match = re.search(
            r"against\s+(?:a\s+)?(?:budget|limit)\s+of\s+(\d+(?:\.\d+)?)",
            message,
            re.IGNORECASE
        )

        if not limit_match:
            return None

        limit_value = float(
            limit_match.group(1)
        )

        excess = actual_value - limit_value

        return {
            "actual_value": actual_value,
            "limit_value": limit_value,
            "excess_value": excess
        }

    except (ValueError, IndexError):
        return None

if __name__ == "__main__":

    sample_problem = {
        "message": (
            "BoxCraft Packaging Unit used 10362.0 kWh "
            "in one day against a budget of 760.0 kWh "
            "(1263.4% over)"
        )
    }

    percentage_result = calculate_excess(
        sample_problem
    )

    quantity_result = calculate_excess_quantity(
        sample_problem
    )

    print("=== IMPACT ESTIMATE ===")

    print("Percentage:")
    print(percentage_result)

    print("\nQuantity:")
    print(quantity_result)