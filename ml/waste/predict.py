import sys
import pandas as pd

from .data_loader import load_from_dataframe
from .preprocessing import preprocess_waste_data
from .overflow_prediction import predict_overflow
from .collection_priority import calculate_collection_priority


# ============================================================
# WASTE INTELLIGENCE PIPELINE
# ============================================================

def run_waste_intelligence(data):

    data = load_from_dataframe(data)
    data = preprocess_waste_data(data)
    data = predict_overflow(data)
    data = calculate_collection_priority(data)

    return data


# ============================================================
# STRUCTURED OUTPUT
# ============================================================

def create_waste_output(data):

    results = []

    for _, row in data.iterrows():

        results.append({
            "source": "waste",
            "facility_id": row["facility_id"],
            "zone_id": row["zone_id"],
            "timestamp": str(row["timestamp"]),
            "metric": "fill_level",
            "actual_value": float(row["fill_level"]),
            "fill_rate": round(
                float(row["fill_rate"]), 2
            ),
            "waste_type": str(row["waste_type"]),
            "overflow_risk": str(
                row["overflow_risk"]
            ),
            "overflow_prediction": bool(
                row["overflow_prediction"]
            ),
            "collection_priority": str(
                row["collection_priority"]
            )
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
    # facility,zone,date,fill_level,waste_type
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print("ERROR: No data provided.")
        print()
        print("Example:")
        print(
            'python -m ml.waste.predict '
            '"F001,Z001,2028-09-01,40,plastic"'
        )

        sys.exit(1)

    try:

        rows = []

        # Each command-line argument = one waste record
        for value in sys.argv[1:]:

            parts = value.split(",")

            if len(parts) != 5:

                raise ValueError(
                    "Each record must contain: "
                    "facility,zone,date,fill_level,waste_type"
                )

            rows.append({
                "facility_id": parts[0],
                "zone_id": parts[1],
                "timestamp": parts[2],
                "fill_level": float(parts[3]),
                "waste_type": parts[4]
            })

        # Convert input to DataFrame
        input_data = pd.DataFrame(rows)

        # Run Waste Intelligence
        result = run_waste_intelligence(
            input_data
        )

        # Create structured output
        structured_output = create_waste_output(
            result
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        high_risk = (
            result["overflow_risk"] == "HIGH"
        ).any()

        medium_risk = (
            result["overflow_risk"] == "MEDIUM"
        ).any()

        print()
        print("=" * 55)
        print("              WASTE INTELLIGENCE")
        print("=" * 55)

        if high_risk:

            print()
            print("Waste Status : OVERFLOW RISK")
            print("Priority     : HIGH")

        elif medium_risk:

            print()
            print("Waste Status : WASTE ABNORMAL")
            print("Priority     : MEDIUM")

        else:

            print()
            print("Waste Status : WASTE OK")
            print("Priority     : LOW")

        print()
        print("=" * 55)

    except Exception as error:

        print()
        print("ERROR:")
        print(error)

        sys.exit(1)