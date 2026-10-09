"""Offline contract tests for the synthetic ingestion pipeline."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ingestion.data_cleaner import DataCleaner
from ingestion.data_validator import DataValidator
from ingestion.sensor_simulator import SensorSimulator


REGISTRY = {
    "ENERGY": [(1, 1), (2, 2)],
    "WATER": [(3, 1), (4, 2)],
    "WASTE": [(5, 1), (6, 2)],
    "AQI": [(7, 1), (8, 2)],
    "TEMPERATURE": [(9, 1), (10, 2)],
    "HUMIDITY": [(11, 1), (12, 2)],
    "TRAFFIC": [(13, 1), (14, 2)],
    "EQUIPMENT": [(15, 1), (16, 2)],
    "SAFETY": [(17, 1), (18, 2)],
}


def test_simulator_defaults_to_recent_window():
    simulator = SensorSimulator(sensor_registry=REGISTRY)
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    assert simulator.end_date <= now
    assert simulator.end_date >= now - timedelta(hours=1, minutes=1)
    assert simulator.start_date >= simulator.end_date - timedelta(days=7, minutes=1)


def test_all_simulated_domains_generate_valid_readings():
    simulator = SensorSimulator(sensor_registry=REGISTRY)
    batches = simulator.generate_all_domains(size=3)
    assert set(batches) == {
        "energy", "water", "waste", "air_quality", "environment",
        "traffic", "equipment", "safety",
    }
    validator = DataValidator()
    all_readings = [row for rows in batches.values() for row in rows]
    assert len(all_readings) == 24
    assert all(validator.validate(row)[0] for row in all_readings)
    assert all(row["reading_ts"].endswith("+0530") for row in all_readings)


def test_domain_sensor_facility_pairs_match_registry():
    simulator = SensorSimulator(sensor_registry=REGISTRY)
    batches = simulator.generate_all_domains(size=10)
    lookup = {sensor_id: facility_id for rows in REGISTRY.values() for sensor_id, facility_id in rows}
    for domain in (
        "energy", "water", "waste", "air_quality", "environment",
        "traffic", "equipment", "safety",
    ):
        assert all(lookup[row["sensor_id"]] == row["facility_id"] for row in batches[domain])


def test_waste_telemetry_respects_schema_ranges():
    simulator = SensorSimulator(sensor_registry=REGISTRY)
    for row in simulator.generate_all_domains(size=20)["waste"]:
        assert 0 <= row["fill_level_percent"] <= 100
        assert row["fill_rate_percent_per_hour"] >= 0
        assert row["recyclable_quantity_kg"] + row["hazardous_quantity_kg"] <= row["waste_quantity_kg"]


def test_cleaner_preserves_timestamp_timezone():
    reading = {
        "sensor_type": "ENERGY",
        "sensor_id": 1,
        "facility_id": 1,
        "reading_ts": "2026-10-08 12:30:00+0530",
        "energy_consumption_kwh": 10.0,
    }
    cleaned = DataCleaner().clean_reading(reading)
    assert cleaned["reading_ts"].endswith("+05:30")


def test_equipment_and_safety_contracts_validate_model_fields():
    simulator = SensorSimulator(sensor_registry=REGISTRY)
    validator = DataValidator()

    equipment = simulator.generate_equipment_reading()
    safety = simulator.generate_safety_reading()

    assert validator.validate(equipment)[0]
    assert validator.validate(safety)[0]
    assert 0 <= equipment["utilization_percent"] <= 100
    assert safety["synthetic_incident_context"] is True
    assert safety["severity"] in {"Low", "Medium", "High", "Critical"}


def test_equipment_and_safety_registry_identity_is_domain_specific():
    simulator = SensorSimulator(sensor_registry=REGISTRY)

    equipment = simulator.generate_equipment_reading()
    safety = simulator.generate_safety_reading()
    equipment_ids = {sensor_id for sensor_id, _ in REGISTRY["EQUIPMENT"]}
    safety_ids = {sensor_id for sensor_id, _ in REGISTRY["SAFETY"]}

    assert equipment["sensor_id"] in equipment_ids
    assert safety["sensor_id"] in safety_ids
