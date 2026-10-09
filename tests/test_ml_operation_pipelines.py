"""Offline contract tests for the reusable ML operations pipelines."""

import pandas as pd

from ml.equipment.predict import predict_equipment_status
from ml.environment.predict import predict_environment_status
from ml.safety.predict import predict_safety_status
from ml.traffic.predict import predict_traffic_status


def sample_environment_data(rows=24):
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "location": ["Zone A"] * rows,
            "aqi": [45 + index * 3 for index in range(rows)],
            "pm25": [8 + index for index in range(rows)],
            "pm10": [15 + index for index in range(rows)],
            "temperature": [22 + index * 0.2 for index in range(rows)],
            "co2": [390 + index * 2 for index in range(rows)],
            "no2": [8 + index * 0.5 for index in range(rows)],
        }
    )


def sample_traffic_data(rows=24):
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "location": ["Gate A"] * rows,
            "vehicle_count": [80 + index * 5 for index in range(rows)],
            "average_speed": [50 - index * 0.7 for index in range(rows)],
            "occupancy": [20 + index * 2 for index in range(rows)],
        }
    )


def sample_equipment_data(rows=24):
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "equipment_id": ["Machine A"] * rows,
            "temperature": [45 + index * 2 for index in range(rows)],
            "vibration": [1 + index * 0.3 for index in range(rows)],
            "operating_hours": [100 + index for index in range(rows)],
            "utilization": [25 + index * 2 for index in range(rows)],
        }
    )


def sample_safety_data(rows=24):
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="h")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "location": ["Zone B"] * rows,
            "incident_type": ["injury"] * rows,
            "severity": ["Low", "Medium", "High"] * (rows // 3)
            + ["Low"] * (rows % 3),
            "people_affected": [index % 4 for index in range(rows)],
            "response_time": [5 + index for index in range(rows)],
        }
    )


def test_environment_pipeline_returns_anomaly_and_risk_columns():
    results = predict_environment_status(sample_environment_data())

    assert not results.empty
    assert "anomaly_status" in results.columns
    assert "environment_risk" in results.columns


def test_traffic_pipeline_returns_predictions_and_hotspot_summary():
    results, hotspot_summary = predict_traffic_status(sample_traffic_data())

    assert not results.empty
    assert "congestion_status" in results.columns
    assert hotspot_summary is not None


def test_equipment_pipeline_returns_anomaly_and_inspection_priority():
    results = predict_equipment_status(sample_equipment_data())

    assert not results.empty
    assert "anomaly_status" in results.columns
    assert "inspection_priority" in results.columns


def test_safety_pipeline_returns_risk_and_hotspot_summary():
    results, hotspot_summary = predict_safety_status(sample_safety_data())

    assert not results.empty
    assert "safety_risk" in results.columns
    assert hotspot_summary is not None
