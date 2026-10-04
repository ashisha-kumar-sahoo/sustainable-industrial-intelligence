import pandas as pd

from ai.operations.environment.data_loader import prepare_environment_data
from ai.operations.environment.preprocessing import create_environment_features
from ai.operations.environment.anomaly_detection import detect_environment_anomalies
from ai.operations.environment.analysis import (
    calculate_environment_risk,
    build_environment_results,
)
from ai.operations.environment.forecasting import forecast_aqi


def sample_environment_data():
    return pd.DataFrame(
        {
            "reading_ts": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="h",
            ),
            "facility_id": [1, 1, 1, 1, 1, 1],
            "sensor_id": [101, 101, 101, 101, 101, 101],
            "aqi": [60, 65, 70, 75, 110, 120],
            "pm25": [20, 22, 25, 28, 55, 60],
            "pm10": [35, 38, 40, 45, 80, 90],
            "co": [0.5, 0.5, 0.6, 0.6, 0.8, 0.9],
            "co2": [400, 410, 420, 430, 450, 460],
            "no2": [20, 22, 24, 26, 45, 50],
            "so2": [5, 5, 6, 6, 8, 9],
        }
    )


def test_environment_data_loading():
    df = sample_environment_data()

    result = prepare_environment_data(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "sensor_id" in result.columns


def test_environment_features():
    df = sample_environment_data()

    result = create_environment_features(df)

    assert "pollution_index" in result.columns
    assert "high_aqi_flag" in result.columns
    assert "pm_ratio" in result.columns


def test_environment_anomaly_detection():
    df = sample_environment_data()

    result = detect_environment_anomalies(df)

    assert "anomaly_prediction" in result.columns
    assert "anomaly_score" in result.columns
    assert "anomaly_status" in result.columns


def test_environment_risk_analysis():
    df = sample_environment_data()

    result = calculate_environment_risk(df)

    assert "risk_score" in result.columns
    assert "risk_level" in result.columns


def test_environment_forecasting():
    df = sample_environment_data()

    result = forecast_aqi(df, horizon=3)

    assert "forecast_aqi" in result.columns
    assert "facility_id" in result.columns


def test_environment_structured_results():
    df = sample_environment_data()

    df = create_environment_features(df)
    df = detect_environment_anomalies(df)
    df = calculate_environment_risk(df)

    result = build_environment_results(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "aqi" in result.columns
    assert "risk_level" in result.columns