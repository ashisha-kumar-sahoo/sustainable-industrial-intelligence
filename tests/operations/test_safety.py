import pandas as pd

from ai.operations.safety.data_loader import prepare_safety_data
from ai.operations.safety.preprocessing import create_safety_features
from ai.operations.safety.risk_analysis import calculate_safety_risk
from ai.operations.safety.analysis import build_safety_results


def sample_safety_data():
    return pd.DataFrame(
        {
            "reading_ts": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="h",
            ),
            "facility_id": [1, 1, 1, 2, 2, 2],
            "sensor_id": [101, 101, 101, 102, 102, 102],
            "incident_count": [1, 2, 4, 0, 1, 3],
            "response_time_minutes": [5, 8, 12, 4, 6, 15],
            "severity": [
                "LOW",
                "MEDIUM",
                "HIGH",
                "LOW",
                "MEDIUM",
                "HIGH",
            ],
        }
    )


def test_safety_data_loading():
    df = sample_safety_data()

    result = prepare_safety_data(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "sensor_id" in result.columns


def test_safety_features():
    df = sample_safety_data()

    result = create_safety_features(df)

    assert "high_incident_flag" in result.columns
    assert "high_response_time_flag" in result.columns


def test_safety_risk_analysis():
    df = sample_safety_data()

    result = calculate_safety_risk(df)

    assert "risk_score" in result.columns
    assert "risk_level" in result.columns
    assert "high_severity_flag" in result.columns


def test_safety_structured_results():
    df = sample_safety_data()

    df = create_safety_features(df)
    df = calculate_safety_risk(df)

    result = build_safety_results(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "incident_count" in result.columns
    assert "risk_level" in result.columns


def test_safety_high_risk_detection():
    df = sample_safety_data()

    result = calculate_safety_risk(df)

    assert "High" in result["risk_level"].values