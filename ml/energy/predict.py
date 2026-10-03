import sys
import pandas as pd

from .data_loader import load_from_dataframe
from .preprocessing import preprocess_energy_data
from .anomaly_detection import detect_anomalies
from .forecasting import forecast_energy


# ============================================================
# ENERGY INTELLIGENCE PIPELINE
# ============================================================

def run_energy_intelligence(data):

    data = load_from_dataframe(data)
    data = preprocess_energy_data(data)
    data = detect_anomalies(data)
    data = forecast_energy(data)

    return data


# ============================================================
# STRUCTURED OUTPUT
# ============================================================

def create_energy_output(data):

    results = []

    for _, row in data.iterrows():

        results.append({
            "source": "energy",
            "facility_id": row["facility_id"],
            "zone_id": row["zone_id"],
            "timestamp": str(row["timestamp"]),
            "metric": "energy_kwh",
            "actual_value": float(row["energy_kwh"]),
            "expected_value": round(
                float(row["expected_value"]), 2
            ),
            "deviation_pct": round(
                float(row["deviation_pct"]), 2
            ),
            "forecast_energy_kwh": round(
                float(row["forecast_energy_kwh"]), 2
            ),
            "severity": str(row["severity"]),
            "anomaly": bool(row["anomaly"])
        })

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # TEMPORARY DATA FROM POWERSHELL
    #
    # Format:
    # facility,zone,date,energy_kwh
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print("ERROR: No data provided.")
        print()
        print("Example:")
        print(
            'python -m ml.energy.predict '
            '"F001,Z001,2028-09-01,5000"'
        )

        sys.exit(1)

    try:

        rows = []

        # Each command-line argument = one energy record
        for value in sys.argv[1:]:

            parts = value.split(",")

            if len(parts) != 4:

                raise ValueError(
                    "Each record must contain: "
                    "facility,zone,date,energy_kwh"
                )

            rows.append({
                "facility_id": parts[0],
                "zone_id": parts[1],
                "timestamp": parts[2],
                "energy_kwh": float(parts[3])
            })

        # Convert input to DataFrame
        input_data = pd.DataFrame(rows)

        # Run Energy Intelligence
        result = run_energy_intelligence(
            input_data
        )

        # Create structured output
        structured_output = create_energy_output(
            result
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        high_anomaly = (
            result["severity"] == "HIGH"
        ).any()

        any_anomaly = (
            result["anomaly"] == True
        ).any()

        print()
        print("=" * 55)
        print("             ENERGY INTELLIGENCE")
        print("=" * 55)

        if high_anomaly:

            print()
            print("Energy Status : ENERGY HIGH")
            print("Risk          : HIGH")

        elif any_anomaly:

            print()
            print("Energy Status : ENERGY ABNORMAL")
            print("Risk          : MEDIUM")

        else:

            print()
            print("Energy Status : ENERGY OK")
            print("Risk          : LOW")

        print()
        print("=" * 55)

    except Exception as error:

        print()
        print("ERROR:")
        print(error)

        sys.exit(1)