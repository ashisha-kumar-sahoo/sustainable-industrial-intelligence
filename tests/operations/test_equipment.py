import pandas as pd

from ai.operations.equipment.data_loader import prepare_equipment_data
from ai.operations.equipment.preprocessing import create_equipment_features
from ai.operations.equipment.anomaly_detection import detect_equipment_anomalies
from ai.operations.equipment.analysis import (
    calculate_equipment_risk,
    build_equipment_results,
)


def sample_equipment_data():
    return pd.DataFrame(
        {
            "reading_ts": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="h",
            ),
            "facility_id": [1, 1, 1, 2, 2, 2],
            "sensor_id": [101, 101, 101, 102, 102, 102],
            "temperature_c": [60, 65, 70, 82, 85, 88],
            "vibration": [1.5, 2.0, 2.5, 4.2, 4.5, 5.0],
            "energy_consumption_kwh": [40, 45, 50, 62, 65, 70],
        }
    )


def test_equipment_data_loading():
    df = sample_equipment_data()

    result = prepare_equipment_data(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "sensor_id" in result.columns


def test_equipment_features():
    df = sample_equipment_data()

    result = create_equipment_features(df)

    assert "high_temperature_flag" in result.columns
    assert "high_vibration_flag" in result.columns
    assert "high_energy_flag" in result.columns


def test_equipment_anomaly_detection():
    df = sample_equipment_data()

    result = detect_equipment_anomalies(df)

    assert "anomaly_prediction" in result.columns
    assert "anomaly_score" in result.columns
    assert "anomaly_status" in result.columns


def test_equipment_risk_analysis():
    df = sample_equipment_data()

    result = calculate_equipment_risk(df)

    assert "risk_score" in result.columns
    assert "maintenance_priority" in result.columns


def test_equipment_structured_results():
    df = sample_equipment_data()

    df = create_equipment_features(df)
    df = detect_equipment_anomalies(df)
    df = calculate_equipment_risk(df)

    result = build_equipment_results(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "temperature_c" in result.columns
    assert "maintenance_priority" in result.columns