def create_energy_reduction_scenario(
    facility_id,
    facility_name,
    baseline_value,
    reduction_pct
):
    """
    Create a validated energy-reduction scenario.

    The actual simulation calculation is handled
    separately by impact_calculator.py.
    """

    return {
        "scenario_type": "energy_reduction",
        "facility_id": facility_id,
        "facility_name": facility_name,
        "parameters": {
            "reduction_pct": reduction_pct
        },
        "baseline_value": baseline_value,
        "unit": "kWh",
        "status": "SIMULATED"
    }


if __name__ == "__main__":

    scenario = create_energy_reduction_scenario(
        facility_id="F001",
        facility_name="BoxCraft Packaging Unit",
        baseline_value=10362.0,
        reduction_pct=15
    )

    print("=== SCENARIO ===")

    for key, value in scenario.items():
        print(key, ":", value)