import sys
import pandas as pd

from .data_loader import load_data, validate_columns
from .preprocessing import preprocess_data
from .anomaly_detection import detect_anomalies


def run_energy_intelligence(data=None):
    """Run the energy anomaly pipeline on a DataFrame or PostgreSQL loader data."""
    if data is None:
        data = load_data()
    validate_columns(data)
    data = preprocess_data(data)
    data = detect_anomalies(data)
    return data


def create_energy_output(data):
    """Create a stable assistant/dashboard-friendly anomaly contract."""
    results = []
    if data is None or data.empty:
        return results

    for _, row in data.iterrows():
        actual = float(row["energy_consumption_kwh"])
        expected = float(row["expected_energy_kwh"])
        deviation = ((actual - expected) / expected * 100) if expected else 0.0
        score = float(row.get("anomaly_score", 0.0))
        severity = "HIGH" if score >= 0.30 else "MEDIUM" if score >= 0.20 else "NORMAL"
        results.append({
            "source": "energy",
            "facility_id": row["facility_id"],
            "sensor_id": row["sensor_id"],
            "timestamp": str(row["reading_ts"]),
            "metric": "energy_kwh",
            "actual_value": actual,
            "expected_value": round(expected, 2),
            "deviation_pct": round(deviation, 2),
            "severity": severity,
            "anomaly": bool(row.get("is_anomaly", False)),
        })
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: No data provided.")
        print('Example: python -m ml.energy.predict "1,1,2026-09-01,5000"')
        sys.exit(1)

    try:
        rows = []
        for value in sys.argv[1:]:
            parts = value.split(",")
            if len(parts) != 4:
                raise ValueError("Each record must contain: facility_id,sensor_id,date,energy_kwh")
            rows.append({
                "facility_id": int(parts[0]),
                "sensor_id": int(parts[1]),
                "reading_ts": parts[2],
                "energy_consumption_kwh": float(parts[3]),
            })

        result = run_energy_intelligence(pd.DataFrame(rows))
        output = create_energy_output(result)
        high = any(x["severity"] == "HIGH" for x in output)
        anomaly = any(x["anomaly"] for x in output)
        print("=" * 55)
        print("ENERGY INTELLIGENCE")
        print("=" * 55)
        print("Energy Status:", "ENERGY HIGH" if high else "ENERGY ABNORMAL" if anomaly else "ENERGY OK")
        print("Risk:", "HIGH" if high else "MEDIUM" if anomaly else "LOW")
        print("=" * 55)
    except Exception as error:
        print("ERROR:", error)
        sys.exit(1)
