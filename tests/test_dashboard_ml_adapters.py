"""Tests for the dashboard-to-ML data-contract adapters."""

import pandas as pd

from dashboard.services.operations_ml_service import (
    predict_environment,
    predict_traffic,
    predict_equipment,
    predict_safety,
)


def test_environment_adapter_runs_on_dashboard_column_names():
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "facility_id": [1] * len(timestamps),
            "facility_name": ["Facility A"] * len(timestamps),
            "zone_id": ["Zone A"] * len(timestamps),
            "aqi": [45 + index * 3 for index in range(24)],
            "pm25": [8 + index for index in range(24)],
            "pm10": [15 + index for index in range(24)],
            "no2": [8 + index * 0.5 for index in range(24)],
            "co2": [390 + index * 2 for index in range(24)],
            "temperature": [22 + index * 0.2 for index in range(24)],
        }
    )

    predictions, note = predict_environment(data)

    assert note is None
    assert not predictions.empty
    assert "environment_risk" in predictions.columns
    assert predictions["location"].eq("Zone A").all()


def test_traffic_adapter_maps_dashboard_columns_and_returns_hotspots():
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "facility_id": [1] * len(timestamps),
            "facility_name": ["Facility A"] * len(timestamps),
            "zone_id": ["Zone A"] * len(timestamps),
            "vehicles": [80 + index * 5 for index in range(24)],
            "avg_speed_kmh": [50 - index * 0.7 for index in range(24)],
            "parking_occupancy_pct": [20 + index * 2 for index in range(24)],
        }
    )

    predictions, hotspot_summary, note = predict_traffic(data)

    assert note is None
    assert not predictions.empty
    assert "congestion_status" in predictions.columns
    assert "hotspot_status" in hotspot_summary.columns


def test_equipment_adapter_runs_on_database_contract_columns():
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "facility_id": [1] * len(timestamps),
            "facility_name": ["Facility A"] * len(timestamps),
            "zone_id": ["Zone A"] * len(timestamps),
            "machine_id": ["Machine A"] * len(timestamps),
            "temperature": [45 + index * 1.5 for index in range(24)],
            "vibration_mm_s": [1 + index * 0.1 for index in range(24)],
            "operating_hours": [100 + index for index in range(24)],
            "utilization_pct": [25 + index * 2 for index in range(24)],
        }
    )

    predictions, note = predict_equipment(data)

    assert note is None
    assert not predictions.empty
    assert "anomaly_status" in predictions.columns
    assert "inspection_priority" in predictions.columns


def test_safety_adapter_runs_on_database_contract_columns():
    timestamps = pd.date_range("2026-01-01", periods=24, freq="h")
    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "facility_id": [1] * len(timestamps),
            "facility_name": ["Facility A"] * len(timestamps),
            "zone_id": ["Zone A"] * len(timestamps),
            "incident_type": ["SMOKE_OR_GAS_ALERT"] * 24,
            "severity": ["Low", "Medium", "High"] * 8,
            "people_affected": [index % 4 for index in range(24)],
            "response_time": [5 + index for index in range(24)],
        }
    )

    predictions, hotspots, note = predict_safety(data)

    assert note is None
    assert not predictions.empty
    assert "safety_risk" in predictions.columns
    assert "inspection_priority" in predictions.columns
    assert "hotspot_status" in hotspots.columns


def test_equipment_and_safety_adapters_explain_missing_data():
    equipment_predictions, equipment_note = predict_equipment(pd.DataFrame())
    safety_predictions, safety_hotspots, safety_note = predict_safety(pd.DataFrame())

    assert equipment_predictions.empty
    assert "No equipment telemetry" in equipment_note
    assert safety_predictions.empty
    assert safety_hotspots.empty
    assert "No safety telemetry" in safety_note
