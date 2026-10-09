"""Regression tests for the audit fixes.

Covers:
- Dashboard wide-form chart construction (missing pandas import + mixed dtypes).
- Assistant PostgreSQL retrieval of nullable numeric columns (no float(None)).
- Recommendation rules handling missing optional keys and None measurements
  instead of raising KeyError/TypeError.

All tests are offline: no database, network, or Streamlit runtime is used.
"""

import datetime

import pandas as pd

import ai.assistant.data_retriever as data_retriever
from ai.assistant.service import process_question
from ai.recommendations.decision_summary import build_decision_summary
from ai.recommendations.rule_engine import (
    find_air_quality_issues,
    find_highest_energy_consumer,
    find_highest_water_consumer,
    find_highest_waste_producer,
    find_traffic_issues,
    find_water_anomalies,
    find_waste_anomalies,
)
from dashboard.components.charts import supporting_chart

TS = datetime.datetime(2026, 10, 8, 10, 0)


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, *args, **kwargs):
        return None

    def fetchall(self):
        return self._rows

    def close(self):
        return None


class _FakeConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return _FakeCursor(self._rows)

    def close(self):
        return None


def _patch_connection(monkeypatch, rows):
    monkeypatch.setattr(
        data_retriever,
        "get_connection",
        lambda: _FakeConnection(rows),
    )


def test_supporting_chart_plots_numeric_wide_form():
    data = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-10-01", "2026-10-02"]),
            "utilization_pct": [70.0, 80.0],
            "vibration_mm_s": [1.2, 2.0],
        }
    )

    figure = supporting_chart(data, ["utilization_pct", "vibration_mm_s"], dark=True)

    assert figure is not None
    assert len(figure.data) >= 1


def test_supporting_chart_handles_mixed_dtypes():
    # The original dashboard error happened when wide-form columns had
    # differing dtypes (numeric + categorical). It must not raise.
    data = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-10-01", "2026-10-02", "2026-10-03"]),
            "utilization_pct": [70.0, 80.0, None],
            "severity_level": ["low", "high", "medium"],
        }
    )

    figure = supporting_chart(data, ["utilization_pct", "severity_level"], dark=True)

    assert figure is not None


def test_supporting_chart_handles_empty_and_missing_columns():
    empty = pd.DataFrame(columns=["timestamp", "metric"])
    no_timestamp = pd.DataFrame({"metric": [1.0, 2.0]})

    assert supporting_chart(empty, ["metric"], dark=True) is not None
    assert supporting_chart(no_timestamp, ["metric"], dark=True) is not None


def test_retriever_energy_nullable_columns_do_not_raise(monkeypatch):
    _patch_connection(
        monkeypatch,
        [(1, "Facility A", TS, None, None, False, None)],
    )

    rows = data_retriever.get_latest_energy_data()

    assert rows[0]["energy_consumption_kwh"] is None
    assert rows[0]["peak_demand_kw"] is None


def test_retriever_water_and_waste_nullable_columns_do_not_raise(monkeypatch):
    _patch_connection(
        monkeypatch,
        [(1, "Facility A", TS, None, None, False, None, "S1")],
    )
    water = data_retriever.get_latest_water_data()
    assert water[0]["water_consumption_liters"] is None
    assert water[0]["flow_rate"] is None

    _patch_connection(
        monkeypatch,
        [
            (
                1, "Facility A", TS, "GENERAL", None, None, None,
                None, None, "LANDFILL", False, None, "S1",
            )
        ],
    )
    waste = data_retriever.get_latest_waste_data()
    assert waste[0]["waste_quantity_kg"] is None
    assert waste[0]["recyclable_quantity_kg"] is None
    assert waste[0]["hazardous_quantity_kg"] is None


def test_retriever_traffic_nullable_columns_do_not_raise(monkeypatch):
    _patch_connection(
        monkeypatch,
        [(1, "Facility A", TS, 10, 2, None, "LOW", None)],
    )

    rows = data_retriever.get_latest_traffic_data()

    assert rows[0]["average_speed_kmph"] is None
    assert rows[0]["lane_occupancy_percent"] is None


def test_highest_rankings_ignore_missing_measurements():
    energy = [
        {"facility_id": 1, "facility_name": "A", "energy_consumption_kwh": None, "reading_ts": TS},
        {"facility_id": 2, "facility_name": "B", "energy_consumption_kwh": 500.0, "reading_ts": TS},
    ]
    water = [
        {"facility_id": 1, "facility_name": "A", "water_consumption_liters": None, "reading_ts": TS},
        {"facility_id": 2, "facility_name": "B", "water_consumption_liters": 5.0, "reading_ts": TS},
    ]
    waste = [
        {"facility_id": 1, "facility_name": "A", "waste_quantity_kg": None, "waste_type": "G", "reading_ts": TS},
        {"facility_id": 2, "facility_name": "B", "waste_quantity_kg": 5.0, "waste_type": "G", "reading_ts": TS},
    ]

    assert find_highest_energy_consumer(energy)["facility_name"] == "B"
    assert find_highest_water_consumer(water)["facility_name"] == "B"
    assert find_highest_waste_producer(waste)["facility_name"] == "B"
    # A dataset with only missing measurements yields no ranking, not a crash.
    assert find_highest_energy_consumer([energy[0]]) is None


def test_anomaly_finders_tolerate_missing_optional_keys():
    assert find_water_anomalies([{"facility_id": 1, "reading_ts": TS}]) == []
    assert find_waste_anomalies([{"facility_id": 1, "reading_ts": TS}]) == []
    assert find_air_quality_issues([{"facility_id": 1, "reading_ts": TS}]) == []
    assert find_traffic_issues([{"facility_id": 1, "reading_ts": TS}]) == []


def test_anomaly_finders_still_report_complete_records():
    water = [
        {
            "facility_id": 1,
            "facility_name": "A",
            "water_consumption_liters": 1200.0,
            "anomaly_flag": True,
            "anomaly_reason": "Abnormal usage",
            "reading_ts": TS,
        }
    ]
    waste = [
        {
            "facility_id": 1,
            "facility_name": "A",
            "waste_quantity_kg": 900.0,
            "waste_type": "HAZARDOUS",
            "anomaly_flag": True,
            "anomaly_reason": "Unusual generation",
            "reading_ts": TS,
        }
    ]

    assert len(find_water_anomalies(water)) == 1
    assert len(find_waste_anomalies(waste)) == 1


def test_decision_summary_tolerates_missing_alert_and_reading_keys():
    alerts = [{"facility_id": 1, "alert_type": "ENERGY", "message": "m", "reading_ts": TS}]
    air_quality = [{"facility_id": 1, "aqi": 10, "reading_ts": TS}]
    traffic = [{"facility_id": 1, "congestion_level": "HIGH", "reading_ts": TS}]

    decision = build_decision_summary(alerts, air_quality, traffic)

    assert "operational_problems" in decision


def test_process_question_degrades_without_errors_on_missing_optional_fields(monkeypatch):
    def base(**kwargs):
        record = {"facility_id": 1, "facility_name": "Facility A", "reading_ts": TS}
        record.update(kwargs)
        return record

    monkeypatch.setattr(data_retriever, "get_alerts", lambda: [base(alert_type="ENERGY", message="m")])
    monkeypatch.setattr(
        data_retriever,
        "get_latest_energy_data",
        lambda: [
            base(energy_consumption_kwh=None, peak_demand_kw=None, anomaly_flag=False, anomaly_reason=None),
            base(facility_id=2, facility_name="Facility B", energy_consumption_kwh=500.0, peak_demand_kw=1.0, anomaly_flag=False, anomaly_reason=None),
        ],
    )
    monkeypatch.setattr(data_retriever, "get_m3_energy_intelligence", lambda: [])
    monkeypatch.setattr(data_retriever, "get_latest_water_data", lambda: [base(water_consumption_liters=None, flow_rate=None, anomaly_flag=True)])
    monkeypatch.setattr(data_retriever, "get_latest_waste_data", lambda: [base(waste_quantity_kg=None, waste_type="GENERAL", anomaly_flag=True)])
    monkeypatch.setattr(data_retriever, "get_latest_air_quality_data", lambda: [base(aqi=10, pm25=1.0, pm10=1.0)])
    monkeypatch.setattr(
        data_retriever,
        "get_latest_traffic_data",
        lambda: [base(vehicle_count=1, heavy_vehicle_count=0, average_speed_kmph=50.0, congestion_level="LOW", lane_occupancy_percent=10.0)],
    )
    monkeypatch.setattr(data_retriever, "get_equipment_health", lambda: [base(equipment_id="M1", status="WARNING")])
    monkeypatch.setattr(data_retriever, "get_latest_safety_data", lambda: [base(synthetic_incident_context=True)])
    monkeypatch.setattr(data_retriever, "get_resource_history", lambda metric, days=7: [])

    result = process_question("What are today's biggest problems?", use_llm=False)

    assert result["errors"] == []
    assert result["answer"]
