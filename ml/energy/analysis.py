import pandas as pd


def analyze_energy(data: pd.DataFrame) -> dict:
    """
    Calculate basic energy consumption analysis metrics.
    """

    if data.empty:
        return {
            "total_energy_kwh": 0.0,
            "average_energy_kwh": 0.0,
            "maximum_energy_kwh": 0.0,
            "minimum_energy_kwh": 0.0,
            "reading_count": 0,
        }

    if "energy_consumption_kwh" not in data.columns:
        raise ValueError(
            "Missing column: energy_consumption_kwh"
        )

    energy = data["energy_consumption_kwh"]

    return {
        "total_energy_kwh": float(energy.sum()),
        "average_energy_kwh": float(energy.mean()),
        "maximum_energy_kwh": float(energy.max()),
        "minimum_energy_kwh": float(energy.min()),
        "reading_count": int(len(data)),
    }