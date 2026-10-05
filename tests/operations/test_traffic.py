import pandas as pd

from ai.operations.traffic.data_loader import prepare_traffic_data
from ai.operations.traffic.preprocessing import create_traffic_features
from ai.operations.traffic.hotspot_detection import detect_traffic_hotspots
from ai.operations.traffic.analysis import (
    calculate_traffic_risk,
    build_traffic_results,
)


def sample_traffic_data():
    return pd.DataFrame(
        {
            "reading_ts": pd.date_range(
                "2026-01-01",
                periods=6,
                freq="h",
            ),
            "facility_id": [1, 1, 1, 2, 2, 2],
            "sensor_id": [101, 101, 101, 102, 102, 102],
            "vehicle_count": [100, 150, 220, 80, 90, 100],
            "heavy_vehicle_count": [10, 20, 40, 5, 8, 10],
            "average_speed_kmph": [40, 30, 18, 45, 42, 40],
            "congestion_level": [
                "LOW",
                "MEDIUM",
                "HIGH",
                "LOW",
                "LOW",
                "LOW",
            ],
            "lane_occupancy_percent": [40, 60, 85, 30, 35, 40],
        }
    )


def test_traffic_data_loading():
    df = sample_traffic_data()

    result = prepare_traffic_data(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "vehicle_count" in result.columns


def test_traffic_features():
    df = sample_traffic_data()

    result = create_traffic_features(df)

    assert "heavy_vehicle_ratio" in result.columns
    assert "low_speed_flag" in result.columns
    assert "high_occupancy_flag" in result.columns


def test_traffic_hotspot_detection():
    df = sample_traffic_data()

    result = detect_traffic_hotspots(df)

    assert not result.empty
    assert "facility_id" in result.columns
    assert "hotspot_score" in result.columns
    assert "hotspot_status" in result.columns


def test_traffic_risk_analysis():
    df = sample_traffic_data()

    result = calculate_traffic_risk(df)

    assert "risk_score" in result.columns
    assert "risk_level" in result.columns


def test_traffic_structured_results():
    df = sample_traffic_data()

    df = create_traffic_features(df)
    df = calculate_traffic_risk(df)

    result = build_traffic_results(df)

    assert not result.empty
    assert "reading_ts" in result.columns
    assert "facility_id" in result.columns
    assert "vehicle_count" in result.columns
    assert "risk_level" in result.columns