from ai.simulation.parameter_validator import (
    validate_reduction_percentage
)

from ai.simulation.scenario_models import (
    create_energy_reduction_scenario
)

from ai.simulation.impact_calculator import (
    calculate_energy_reduction
)


def simulate_energy_reduction(
    facility_id,
    facility_name,
    baseline_value,
    reduction_pct
):
    """
    Run a complete energy-reduction simulation.

    Flow:
    Validate → Create Scenario → Calculate Impact
    """

    # Validate parameters
    if not validate_reduction_percentage(
        reduction_pct
    ):
        raise ValueError(
            "Reduction percentage must be "
            "greater than 0 and less than 100."
        )

    # Create scenario
    scenario = create_energy_reduction_scenario(
        facility_id=facility_id,
        facility_name=facility_name,
        baseline_value=baseline_value,
        reduction_pct=reduction_pct
    )

    # Calculate simulated impact
    impact = calculate_energy_reduction(
        baseline_value=baseline_value,
        reduction_pct=reduction_pct
    )

    # Build final simulation result
    result = {
        "scenario_type": scenario[
            "scenario_type"
        ],

        "facility_id": scenario[
            "facility_id"
        ],

        "facility_name": scenario[
            "facility_name"
        ],

        "parameters": scenario[
            "parameters"
        ],

        "baseline_value": impact[
            "baseline_value"
        ],

        "simulated_value": impact[
            "simulated_value"
        ],

        "estimated_change_pct": impact[
            "estimated_change_pct"
        ],

        "unit": scenario[
            "unit"
        ],

        "status": "SIMULATED",

        "assumptions": [
            "The simulation applies the requested "
            "percentage reduction directly to the "
            "baseline energy value.",
            "The result is an estimate and not a "
            "forecast from an ML model."
        ]
    }

    return result


if __name__ == "__main__":

    result = simulate_energy_reduction(
        facility_id="F001",
        facility_name="BoxCraft Packaging Unit",
        baseline_value=10362.0,
        reduction_pct=15
    )

    print("=== FINAL SIMULATION ===")

    for key, value in result.items():

        print(
            key,
            ":",
            value
        )