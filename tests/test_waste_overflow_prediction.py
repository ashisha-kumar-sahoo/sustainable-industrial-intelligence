"""Tests for waste telemetry validation and overflow-estimator behavior."""

import pandas as pd
import pytest

from ml.waste.overflow_prediction import (
    prepare_waste_data,
    predict_waste_overflow,
)


def make_waste_data(rows_per_bin=12, bin_count=2):
    records = []
    start = pd.Timestamp("2026-01-01 00:00:00")
    for bin_number in range(bin_count):
        for hour in range(rows_per_bin):
            records.append(
                {
                    "reading_ts": start + pd.Timedelta(hours=hour),
                    "facility_id": bin_number + 1,
                    "sensor_id": f"BIN-{bin_number + 1}",
                    "fill_level_percent": 30 + hour * 3,
                    "fill_rate_percent_per_hour": 3,
                }
            )
    return pd.DataFrame(records)


def test_waste_preprocessing_sorts_each_bin_chronologically():
    data = make_waste_data()
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)

    prepared = prepare_waste_data(data)

    assert not prepared.empty
    for _, bin_data in prepared.groupby("sensor_id"):
        assert bin_data["reading_ts"].is_monotonic_increasing


def test_small_waste_dataset_uses_explainable_fill_rate_projection():
    predictions = predict_waste_overflow(make_waste_data(rows_per_bin=4))

    assert not predictions.empty
    assert predictions["prediction_method"].eq("fill-rate projection").all()
    assert predictions["predicted_fill_level_percent"].between(0, 100).all()
    assert set(predictions["overflow_risk"]).issubset({"LOW", "MEDIUM", "HIGH"})


def test_larger_waste_dataset_trains_with_per_bin_future_targets():
    predictions = predict_waste_overflow(make_waste_data(rows_per_bin=40))

    assert not predictions.empty
    assert predictions["prediction_method"].eq(
        "Random Forest with per-bin future targets"
    ).all()
    assert predictions["predicted_fill_level_percent"].between(0, 100).all()


def test_waste_preprocessing_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="Missing required waste columns"):
        prepare_waste_data(pd.DataFrame({"facility_id": [1]}))


def test_dashboard_adapter_translates_database_column_names():
    from dashboard.services.waste_service import predict_overflow

    dashboard_rows = make_waste_data(rows_per_bin=4).rename(
        columns={
            "reading_ts": "timestamp",
            "fill_level_percent": "fill_pct",
        }
    )
    predictions, note = predict_overflow(dashboard_rows)

    assert note is None
    assert not predictions.empty
    assert "predicted_fill_level_percent" in predictions.columns


def test_dashboard_adapter_explains_when_fill_rate_is_missing():
    from dashboard.services.waste_service import predict_overflow

    dashboard_rows = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2026-01-01")],
            "facility_id": [1],
            "fill_pct": [60],
        }
    )
    predictions, note = predict_overflow(dashboard_rows)

    assert predictions.empty
    assert note is not None
    assert "fill-rate telemetry" in note


def test_assistant_waste_decision_uses_available_fill_telemetry():
    from ai.assistant.service import _build_decision

    waste_rows = [
        {
            "facility_id": 1,
            "facility_name": "Facility A",
            "sensor_id": "BIN-1",
            "reading_ts": pd.Timestamp("2026-01-01 10:00:00"),
            "waste_type": "general",
            "waste_quantity_kg": 12.0,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "fill_level_percent": 88.0,
            "fill_rate_percent_per_hour": 2.0,
        },
        {
            "facility_id": 2,
            "facility_name": "Facility B",
            "sensor_id": "BIN-2",
            "reading_ts": pd.Timestamp("2026-01-01 10:00:00"),
            "waste_type": "general",
            "waste_quantity_kg": 8.0,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "fill_level_percent": 40.0,
            "fill_rate_percent_per_hour": 1.0,
        },
    ]

    decision, _recommendations, _explanations, answer = _build_decision(
        "waste",
        "What is the waste overflow risk?",
        {"data": {"waste": waste_rows}},
    )

    assert decision["overflow_risk"]["status"] == "available"
    assert decision["overflow_risk"]["horizon_hours"] == 6
    assert "fill-rate projection" in decision["overflow_risk"]["prediction_method"]
    assert "overflow" in answer["summary"].lower() or "risk" in answer["summary"].lower()
