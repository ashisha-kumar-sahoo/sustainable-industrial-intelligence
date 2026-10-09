import math


def calculate_energy_reduction(
    baseline_value,
    reduction_pct
):
    """
    Calculate the simulated energy value
    after applying a percentage reduction.
    """

    try:
        baseline_value = float(baseline_value)
    except (TypeError, ValueError):
        raise ValueError(
            "A numeric baseline energy value is required."
        )

    if not math.isfinite(baseline_value):
        raise ValueError(
            "A finite baseline energy value is required."
        )

    reduction_pct = float(reduction_pct)

    reduction_amount = (
        baseline_value * reduction_pct / 100
    )

    simulated_value = (
        baseline_value - reduction_amount
    )

    return {
        "baseline_value": baseline_value,
        "reduction_pct": reduction_pct,
        "reduction_amount": reduction_amount,
        "simulated_value": simulated_value,
        "estimated_change_pct": -reduction_pct
    }


if __name__ == "__main__":

    result = calculate_energy_reduction(
        baseline_value=10362.0,
        reduction_pct=15
    )

    print("=== SIMULATION CALCULATION ===")

    print(
        "Baseline:",
        result["baseline_value"],
        "kWh"
    )

    print(
        "Reduction:",
        result["reduction_pct"],
        "%"
    )

    print(
        "Reduction Amount:",
        result["reduction_amount"],
        "kWh"
    )

    print(
        "Simulated Value:",
        result["simulated_value"],
        "kWh"
    )

    print(
        "Estimated Change:",
        result["estimated_change_pct"],
        "%"
    )