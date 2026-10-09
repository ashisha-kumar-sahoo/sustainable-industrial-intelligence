"""Regression tests for AQI validation and ingestion data fidelity."""

from ingestion.data_validator import DataValidator


def aqi_reading(**overrides):
    reading = {
        "sensor_id": 12,
        "facility_id": 4,
        "sensor_type": "AQI",
        "reading_ts": "2026-10-09 10:00:00+05:30",
        "aqi": 90,
        "pm25": 25,
        "pm10": 50,
        "co": 0.5,
        "co2": 420,
        "no2": 10,
        "so2": 5,
    }
    reading.update(overrides)
    return reading


def test_aqi_requires_a_real_measurement():
    valid, errors = DataValidator().validate(aqi_reading())
    assert valid is True
    assert errors == []

    valid, errors = DataValidator().validate(aqi_reading(aqi=None))
    assert valid is False
    assert any("aqi" in error.lower() for error in errors)


def test_aqi_rejects_out_of_range_measurements():
    valid, errors = DataValidator().validate(aqi_reading(aqi=700))

    assert valid is False
    assert any("out of range" in error.lower() for error in errors)


def test_zero_temperature_is_not_treated_as_missing_by_loader_mapping():
    from ingestion.load_to_postgres import DataLoader

    class FakeCursor:
        rowcount = 1

        def execute(self, query, parameters):
            self.parameters = parameters

    loader = DataLoader.__new__(DataLoader)
    loader.cur = FakeCursor()
    loader._insert_environment(
        {
            "sensor_id": 1,
            "facility_id": 1,
            "reading_ts": "2026-10-09 10:00:00+05:30",
            "temperature_c": 0,
            "temperature": 22,
            "humidity_percent": 0,
            "humidity": 60,
        }
    )

    assert loader.cur.parameters[3] == 0
    assert loader.cur.parameters[4] == 0


def test_validator_rejects_nan_measurements():
    valid, errors = DataValidator().validate(aqi_reading(aqi=float("nan")))

    assert valid is False
    assert any("finite number" in error.lower() for error in errors)


def test_raw_loader_parameter_contract_preserves_full_json_payload():
    import json

    from ingestion.load_to_postgres import DataLoader

    class FakeCursor:
        rowcount = 1

        def __init__(self):
            self.calls = []

        def execute(self, query, parameters=None):
            self.calls.append((query, parameters))

        def close(self):
            pass

    class FakeConnection:
        def __init__(self):
            self.committed = False

        def commit(self):
            self.committed = True

        def close(self):
            pass

    cursor = FakeCursor()
    connection = FakeConnection()
    loader = DataLoader.__new__(DataLoader)
    loader.cur = cursor
    loader.conn = connection

    reading = {
        "sensor_id": 17,
        "facility_id": 3,
        "sensor_type": "EQUIPMENT",
        "reading_ts": "2026-10-09 10:00:00+05:30",
        "equipment_id": "EQ-SENSOR-0017",
        "vibration_mms": 2.1,
        "temperature_c": 70.0,
        "operating_hours": 12.0,
        "utilization_percent": 82.0,
        "custom_sensor_field": "preserve-me",
    }

    inserted = loader.load_to_raw([reading])
    insert_query, insert_parameters = next(
        (query, parameters)
        for query, parameters in cursor.calls
        if "INSERT INTO raw.raw_sensor_data" in query
    )

    assert inserted == 1
    assert connection.committed is True
    assert insert_query.count("%s") == len(insert_parameters)
    assert json.loads(insert_parameters[-1])["custom_sensor_field"] == "preserve-me"


def test_new_public_domain_insert_methods_match_parameter_counts():
    from ingestion.load_to_postgres import DataLoader

    class FakeCursor:
        rowcount = 1

        def execute(self, query, parameters):
            self.query = query
            self.parameters = parameters

    loader = DataLoader.__new__(DataLoader)
    loader.cur = FakeCursor()

    equipment_reading = {
        "sensor_id": 17,
        "facility_id": 3,
        "reading_ts": "2026-10-09 10:00:00+05:30",
        "equipment_id": "EQ-SENSOR-0017",
        "vibration_mms": 2.1,
        "temperature_c": 70.0,
        "operating_hours": 12.0,
        "utilization_percent": 82.0,
        "equipment_status": "WARNING",
    }
    assert loader._insert_equipment(equipment_reading) is True
    assert loader.cur.query.count("%s") == len(loader.cur.parameters)

    safety_reading = {
        "sensor_id": 18,
        "facility_id": 3,
        "reading_ts": "2026-10-09 10:00:00+05:30",
        "gas_leak_ppm": 2.0,
        "smoke_detected": False,
        "fire_alarm": False,
        "emergency_button": False,
        "safety_temperature_c": 32.0,
        "incident_type": "ROUTINE_MONITORING",
        "severity": "Low",
        "people_affected": 0,
        "response_time": 0.0,
        "synthetic_incident_context": True,
    }
    assert loader._insert_safety(safety_reading) is True
    assert loader.cur.query.count("%s") == len(loader.cur.parameters)
    assert loader.cur.parameters[-1] is True
