import sys
import pandas as pd

from .data_loader import load_from_dataframe
from .preprocessing import preprocess_water_data
from .anomaly_detection import detect_anomalies


# ============================================================
# WATER INTELLIGENCE PIPELINE
# ============================================================

def run_water_intelligence(data):

    data = load_from_dataframe(data)
    data = preprocess_water_data(data)
    data = detect_anomalies(data)

    return data


# ============================================================
# STRUCTURED OUTPUT
# ============================================================

def create_water_output(data):

    results = []

    for _, row in data.iterrows():

        results.append({
            "source": "water",
            "facility_id": row["facility_id"],
            "zone_id": row["zone_id"],
            "timestamp": str(row["timestamp"]),
            "metric": "water_liters",
            "actual_value": float(row["water_liters"]),
            "expected_value": round(float(row["expected_value"]), 2),
            "deviation_pct": round(float(row["deviation_pct"]), 2),
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
    # Format:
    # facility,zone,date,water_liters,flow_rate
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print("ERROR: No data provided.")
        print()
        print("Example:")
        print(
            'python -m ml.water.predict '
            '"F001,Z001,2028-09-01,18000,750"'
        )
        sys.exit(1)

    try:

        rows = []

        # Each command-line argument = one water record
        for value in sys.argv[1:]:

            parts = value.split(",")

            if len(parts) != 5:
                raise ValueError(
                    "Each record must contain: "
                    "facility,zone,date,water_liters,flow_rate"
                )

            rows.append({
                "facility_id": parts[0],
                "zone_id": parts[1],
                "timestamp": parts[2],
                "water_liters": float(parts[3]),
                "flow_rate": float(parts[4])
            })

        # Convert temporary data to DataFrame
        input_data = pd.DataFrame(rows)

        # Run model
        result = run_water_intelligence(input_data)

        # Create structured output
        structured_output = create_water_output(result)

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        high_anomaly = (result["severity"] == "HIGH").any()
        any_anomaly = (result["anomaly"] == True).any()

        print()
        print("=" * 55)
        print("              WATER INTELLIGENCE")
        print("=" * 55)

        if high_anomaly:

            print()
            print("Water Status : WATER WASTAGE")
            print("Risk         : HIGH")

        elif any_anomaly:

            print()
            print("Water Status : WATER ABNORMAL")
            print("Risk         : MEDIUM")

        else:

            print()
            print("Water Status : WATER OK")
            print("Risk         : LOW")

        print()
        print("=" * 55)

    except Exception as error:

        print()
        print("ERROR:")
        print(error)
        sys.exit(1)