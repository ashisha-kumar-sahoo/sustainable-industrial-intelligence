"""Regression tests for the AI Assistant repair.

Each test is offline: the PostgreSQL retrievers are monkeypatched with mocked
rows and no network, database, or LLM call is made (``use_llm=False``).

Covered failure modes:
1.  "What are today's biggest problems?"
2.  Empty retrieval results.
3.  Missing dictionary keys.
4.  Numeric fields containing ``None``.
5.  Numeric fields containing pandas null values (NaN / pd.NA).
6.  Missing optional columns.
7.  No recent sensor readings.
8.  Partial data from one or more domains.
9.  Valid data producing a normal assistant response.
10. Internal exceptions reported safely (no raw text / stack traces).
"""

import datetime
import json

import pandas as pd

import ai.assistant.data_retriever as data_retriever
from ai.assistant.response_generator import create_energy_anomaly_response
from ai.assistant.service import process_question
from ai.recommendations.impact_estimator import (
    calculate_excess,
    calculate_excess_quantity,
)
from ai.recommendations.risk_score import calculate_risk
from ai.recommendations.rule_engine import (
    find_highest_energy_consumer,
    find_highest_water_consumer,
    find_highest_waste_producer,
)

TS = datetime.datetime(2026, 10, 8, 10, 0)


def _record(**overrides):
    record = {"facility_id": 1, "facility_name": "Facility A", "reading_ts": TS}
    record.update(overrides)
    return record


def _install(monkeypatch, **overrides):
    """Patch every retriever with a safe default, then apply overrides."""
    defaults = {
        "get_alerts": [],
        "get_latest_energy_data": [],
        "get_m3_energy_intelligence": [],
        "get_latest_water_data": [],
        "get_latest_waste_data": [],
        "get_latest_air_quality_data": [],
        "get_latest_traffic_data": [],
        "get_equipment_health": [],
        "get_latest_safety_data": [],
        "get_resource_history": [],
    }
    defaults.update(overrides)
    for name, value in defaults.items():
        monkeypatch.setattr(
            data_retriever,
            name,
            (lambda v: (lambda *args, **kwargs: v))(value),
        )


def _healthy(monkeypatch):
    _install(
        monkeypatch,
        get_alerts=[_record(alert_type="ENERGY", severity="HIGH", message="high use")],
        get_latest_energy_data=[_record(energy_consumption_kwh=500.0, peak_demand_kw=1.0)],
        get_latest_water_data=[_record(water_consumption_liters=100.0, flow_rate=1.0)],
        get_latest_waste_data=[_record(waste_quantity_kg=5.0, waste_type="GENERAL")],
        get_latest_air_quality_data=[_record(aqi=10, pm25=1.0, pm10=1.0, aqi_category="Good")],
        get_latest_traffic_data=[_record(vehicle_count=1, congestion_level="LOW", lane_occupancy_percent=10.0)],
        get_equipment_health=[_record(equipment_id="M1", status="WARNING")],
        get_latest_safety_data=[_record(synthetic_incident_context=True)],
    )


# 1. The previously failing question.
def test_biggest_problems_question_succeeds(monkeypatch):
    _healthy(monkeypatch)

    result = process_question("What are today's biggest problems?", use_llm=False)

    assert result["route"] == "current_status"
    assert result["errors"] == []
    assert result["answer"]["summary"]


# 2. Empty retrieval results.
def test_empty_retrieval_results_do_not_crash(monkeypatch):
    _install(monkeypatch)

    questions = [
        "What are today's biggest problems?",
        "Which facility has the highest energy consumption?",
        "Which facility has the highest water consumption?",
        "What is the waste status?",
        "How is the traffic?",
        "What is the air quality?",
        "Which equipment needs maintenance?",
        "What is the safety status?",
    ]

    for question in questions:
        result = process_question(question, use_llm=False)
        assert result["errors"] == [], question
        assert result["answer"]["summary"]


# 3. Missing dictionary keys.
def test_missing_dictionary_keys_are_tolerated():
    assert find_highest_energy_consumer(
        [{"energy_consumption_kwh": 5.0}]
    ) == {
        "facility_id": None,
        "facility_name": None,
        "energy_consumption_kwh": 5.0,
        "reading_ts": None,
    }
    assert find_highest_water_consumer(
        [{"water_consumption_liters": 5.0}]
    )["facility_name"] is None
    assert find_highest_waste_producer(
        [{"waste_quantity_kg": 5.0}]
    )["waste_type"] is None


# 4. Numeric fields containing None.
def test_numeric_none_values_do_not_crash(monkeypatch):
    _install(
        monkeypatch,
        get_alerts=[_record(alert_type="ENERGY", severity="HIGH", message=None)],
        get_latest_energy_data=[_record(energy_consumption_kwh=900.0)],
        get_m3_energy_intelligence=[
            _record(
                timestamp=str(TS),
                actual_value=900.0,
                expected_value=500.0,
                deviation_pct=None,
                severity=None,
                anomaly=True,
            )
        ],
    )

    for question in (
        "Which facilities currently have energy anomalies?",
        "Which facility has the highest energy consumption?",
        "What are today's biggest problems?",
    ):
        result = process_question(question, use_llm=False)
        assert result["errors"] == [], question


def test_risk_score_and_impact_estimator_handle_none():
    assert calculate_risk({"deviation_pct": None}) == "LOW"
    assert calculate_excess({"message": None}) is None
    assert calculate_excess_quantity({"message": None}) is None


def test_energy_anomaly_response_handles_none_deviation():
    answer = create_energy_anomaly_response(
        [
            {
                "facility_name": "Facility A",
                "actual_value": 900.0,
                "expected_value": 500.0,
                "deviation_pct": None,
                "severity": None,
            }
        ],
        [],
    )

    assert answer["summary"]
    assert "deviation unavailable" in answer["evidence"][0]


# 5. Numeric fields containing pandas null values.
def test_pandas_null_numeric_values_are_treated_as_missing():
    records = [
        {"facility_id": 1, "facility_name": "A", "energy_consumption_kwh": float("nan")},
        {"facility_id": 2, "facility_name": "B", "energy_consumption_kwh": pd.NA},
        {"facility_id": 3, "facility_name": "C", "energy_consumption_kwh": 5.0},
    ]

    assert find_highest_energy_consumer(records)["facility_name"] == "C"
    assert find_highest_energy_consumer(records[:2]) is None


def test_pandas_null_energy_in_assistant(monkeypatch):
    _install(
        monkeypatch,
        get_latest_energy_data=[
            _record(energy_consumption_kwh=float("nan")),
            _record(facility_id=2, facility_name="Facility B", energy_consumption_kwh=pd.NA),
        ],
    )

    result = process_question("Which facility has the highest energy consumption?", use_llm=False)

    assert result["errors"] == []
    assert result["answer"]["summary"] == "No current energy data is available."


# 6. Missing optional columns.
def test_missing_optional_columns_do_not_crash(monkeypatch):
    _install(
        monkeypatch,
        get_latest_waste_data=[
            {"facility_id": 1, "facility_name": "Facility A", "waste_quantity_kg": 5.0, "reading_ts": TS}
        ],
    )

    result = process_question("What is the waste status?", use_llm=False)

    assert result["errors"] == []
    assert "highest latest recorded waste" in result["answer"]["summary"]


# 7. No recent sensor readings.
def test_no_recent_sensor_readings(monkeypatch):
    _install(monkeypatch)

    current = process_question("What are today's biggest problems?", use_llm=False)
    energy = process_question("Which facility has the highest energy consumption?", use_llm=False)

    assert current["errors"] == []
    assert "0 operational problems" in current["answer"]["summary"]
    assert energy["errors"] == []
    assert energy["answer"]["summary"] == "No current energy data is available."


# 8. Partial data from one or more domains.
def test_partial_domain_data_is_handled(monkeypatch):
    _install(
        monkeypatch,
        get_latest_energy_data=[_record(energy_consumption_kwh=500.0)],
        get_latest_air_quality_data=[_record(aqi=120, pm25=2.0, pm10=3.0, aqi_category="Unhealthy")],
    )

    result = process_question("What are today's biggest problems?", use_llm=False)

    assert result["errors"] == []
    assert result["answer"]["summary"]


# 9. Valid data produces a normal response.
def test_valid_data_produces_normal_answer(monkeypatch):
    _healthy(monkeypatch)

    result = process_question("Which facility has the highest energy consumption?", use_llm=False)

    assert result["errors"] == []
    assert result["route"] == "energy"
    assert "Facility A" in result["answer"]["summary"]
    assert "500.0 kWh" in result["answer"]["summary"]


# 10. Internal exceptions reported safely.
def test_internal_exception_is_reported_without_leaking_details(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("connection failed for postgres://user:secret-password@host/db")

    _install(monkeypatch)
    monkeypatch.setattr(data_retriever, "get_latest_energy_data", boom)

    result = process_question("Which facility has the highest energy consumption?", use_llm=False)

    assert result["errors"], "the failure must still be reported"
    assert result["errors"][0]["type"] == "RuntimeError"

    serialized = json.dumps(result, default=str)
    assert "secret-password" not in serialized
    assert "Traceback" not in serialized
    assert "postgres://" not in serialized
