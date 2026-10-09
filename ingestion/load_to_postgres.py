"""
Load validated and cleaned readings into PostgreSQL database.

Follows the existing schema:
- raw.raw_sensor_data is the append-only landing zone.
- public domain tables are the analytical/source-of-truth tables.
- Public tables use (sensor_id, reading_ts) for idempotent ingestion.
"""

import json
import os
from typing import Dict, Any, List

from . import db_connection
from . import config
from .data_validator import DataValidator
from .data_cleaner import DataCleaner


class DataLoader:
    """Loads sensor data into PostgreSQL database."""

    def __init__(self):
        self.conn = db_connection.get_connection()
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    @staticmethod
    def _optional_boolean(value):
        """Convert common sensor boolean encodings without treating "0" as true."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0

        normalized_value = str(value).strip().casefold()
        if normalized_value in {"1", "true", "yes", "on"}:
            return True
        if normalized_value in {"0", "false", "no", "off", ""}:
            return False
        raise ValueError(f"Cannot interpret {value!r} as a boolean sensor value.")

    def load_to_raw(self, readings: List[Dict[str, Any]]) -> int:
        """
        Load readings into raw.raw_sensor_data.

        The raw layer is intentionally append-only. Duplicate ingestion
        attempts are preserved as ingestion history.
        """

        if not readings:
            return 0

        query = """
            INSERT INTO raw.raw_sensor_data (
                sensor_id,
                facility_id,
                sensor_type,
                reading_ts,

                energy_consumption_kwh,
                voltage,
                current,
                power_factor,
                peak_demand_kw,

                water_consumption_liters,
                water_pressure,
                water_temperature,
                flow_rate,

                waste_type,
                waste_quantity_kg,
                recyclable_quantity_kg,
                hazardous_quantity_kg,
                fill_level_percent,
                fill_rate_percent_per_hour,

                aqi,
                pm25,
                pm10,
                co,
                co2,
                no2,
                so2,
                temperature,
                humidity,

                vehicle_count,
                heavy_vehicle_count,
                average_speed_kmph,
                congestion_level,

                temperature_c,
                humidity_percent,
                rainfall_mm,
                wind_speed_kmph,
                equipment_id,
                vibration_mms,
                operating_hours,
                utilization_percent,
                equipment_status,
                gas_leak_ppm,
                smoke_detected,
                fire_alarm,
                emergency_button,
                safety_temperature_c,
                incident_type,
                severity,
                people_affected,
                response_time,
                raw_payload
            )
            VALUES (
                %s, %s, %s, %s,

                %s, %s, %s, %s, %s,

                %s, %s, %s, %s,

                %s, %s, %s, %s, %s, %s,

                %s, %s, %s, %s, %s, %s, %s, %s, %s,

                %s, %s, %s, %s,

                %s, %s, %s, %s,

                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s::jsonb
            )
        """

        inserted = 0

        for index, r in enumerate(readings):
            savepoint = f"raw_reading_{index}"
            try:
                self.cur.execute(f"SAVEPOINT {savepoint}")
                self.cur.execute(
                    query,
                    (
                        r.get("sensor_id"),
                        r.get("facility_id"),
                        r.get("sensor_type"),
                        r.get("reading_ts"),

                        r.get("energy_consumption_kwh"),
                        r.get("voltage"),
                        r.get("current"),
                        r.get("power_factor"),
                        r.get("peak_demand_kw"),

                        r.get("water_consumption_liters"),
                        r.get("water_pressure"),
                        r.get("water_temperature"),
                        r.get("flow_rate"),

                        r.get("waste_type"),
                        r.get("waste_quantity_kg"),
                        r.get("recyclable_quantity_kg"),
                        r.get("hazardous_quantity_kg"),
                        r.get("fill_level_percent"),
                        r.get("fill_rate_percent_per_hour"),

                        r.get("aqi"),
                        r.get("pm25"),
                        r.get("pm10"),
                        r.get("co"),
                        r.get("co2"),
                        r.get("no2"),
                        r.get("so2"),
                        r.get("temperature"),
                        r.get("humidity"),

                        r.get("vehicle_count"),
                        r.get("heavy_vehicle_count"),
                        r.get("average_speed_kmph"),
                        r.get("congestion_level"),

                        r.get("temperature_c")
                        if r.get("temperature_c") is not None
                        else r.get("temperature"),
                        r.get("humidity_percent")
                        if r.get("humidity_percent") is not None
                        else r.get("humidity"),
                        r.get("rainfall_mm"),
                        r.get("wind_speed_kmph"),

                        r.get("equipment_id"),
                        r.get("vibration_mms"),
                        r.get("operating_hours"),
                        r.get("utilization_percent"),
                        r.get("equipment_status", r.get("status")),
                        r.get("gas_leak_ppm"),
                        self._optional_boolean(r.get("smoke_detected")),
                        self._optional_boolean(r.get("fire_alarm")),
                        self._optional_boolean(r.get("emergency_button")),
                        r.get("safety_temperature_c"),
                        r.get("incident_type"),
                        r.get("severity"),
                        r.get("people_affected"),
                        r.get("response_time"),
                        json.dumps(r, default=str),
                    ),
                )

                inserted += 1
                self.cur.execute(f"RELEASE SAVEPOINT {savepoint}")

            except Exception as e:
                self.cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self.cur.execute(f"RELEASE SAVEPOINT {savepoint}")
                print(f"Error inserting raw reading: {e}")

        self.conn.commit()
        return inserted

    def load_to_public_domain(
        self,
        readings: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Load clean readings into the appropriate public domain tables.

        Public tables are idempotent using the existing
        UNIQUE(sensor_id, reading_ts) constraints.
        """

        counts = {}

        for index, r in enumerate(readings):
            sensor_type = str(r.get("sensor_type", "")).upper()
            savepoint = f"public_reading_{index}"

            try:
                self.cur.execute(f"SAVEPOINT {savepoint}")
                if sensor_type == "ENERGY":
                    if self._insert_energy(r):
                        counts["energy"] = counts.get("energy", 0) + 1

                elif sensor_type == "WATER":
                    if self._insert_water(r):
                        counts["water"] = counts.get("water", 0) + 1

                elif sensor_type == "WASTE":
                    if self._insert_waste(r):
                        counts["waste"] = counts.get("waste", 0) + 1

                elif sensor_type == "AQI":
                    if self._insert_aqi(r):
                        counts["aqi"] = counts.get("aqi", 0) + 1

                elif sensor_type in (
                    "ENVIRONMENT",
                    "TEMPERATURE",
                    "HUMIDITY",
                ):
                    if self._insert_environment(r):
                        counts["environment"] = counts.get(
                            "environment", 0
                        ) + 1

                elif sensor_type == "TRAFFIC":
                    if self._insert_traffic(r):
                        counts["traffic"] = counts.get("traffic", 0) + 1

                elif sensor_type == "EQUIPMENT":
                    if self._insert_equipment(r):
                        counts["equipment"] = counts.get("equipment", 0) + 1

                elif sensor_type == "SAFETY":
                    if self._insert_safety(r):
                        counts["safety"] = counts.get("safety", 0) + 1

                self.cur.execute(f"RELEASE SAVEPOINT {savepoint}")

            except Exception as e:
                self.cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self.cur.execute(f"RELEASE SAVEPOINT {savepoint}")
                print(
                    f"Error loading {sensor_type} reading: {e}"
                )

        self.conn.commit()
        return counts

    def _insert_equipment(self, reading: Dict[str, Any]) -> bool:
        """Insert one equipment telemetry record idempotently."""
        query = """
            INSERT INTO public.equipment_readings (
                sensor_id, facility_id, reading_ts, equipment_id,
                vibration_mms, temperature_c, operating_hours,
                utilization_percent, equipment_status,
                data_quality_status, anomaly_flag, anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """
        equipment_status = str(
            reading.get("equipment_status", reading.get("status", "NORMAL"))
        ).upper()
        if equipment_status not in {"NORMAL", "WARNING", "CRITICAL", "OFFLINE"}:
            equipment_status = "NORMAL"

        self.cur.execute(
            query,
            (
                reading.get("sensor_id"),
                reading.get("facility_id"),
                reading.get("reading_ts"),
                reading.get("equipment_id", "UNKNOWN"),
                reading.get("vibration_mms"),
                reading.get("temperature_c"),
                reading.get("operating_hours"),
                reading.get("utilization_percent"),
                equipment_status,
            ),
        )
        return self.cur.rowcount == 1

    def _insert_safety(self, reading: Dict[str, Any]) -> bool:
        """Insert one safety sensor record and optional synthetic incident context."""
        query = """
            INSERT INTO public.safety_readings (
                sensor_id, facility_id, reading_ts, gas_leak_ppm,
                smoke_detected, fire_alarm, emergency_button, temperature_c,
                incident_type, severity, people_affected, response_time,
                synthetic_context, data_quality_status, anomaly_flag, anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """
        severity = reading.get("severity")
        if severity is not None:
            normalized_severity = str(severity).strip().title()
            severity = normalized_severity if normalized_severity in {
                "Low", "Medium", "High", "Critical"
            } else None

        self.cur.execute(
            query,
            (
                reading.get("sensor_id"),
                reading.get("facility_id"),
                reading.get("reading_ts"),
                reading.get("gas_leak_ppm"),
                reading.get("smoke_detected", False),
                reading.get("fire_alarm", False),
                reading.get("emergency_button", False),
                reading.get("safety_temperature_c", reading.get("temperature_c")),
                reading.get("incident_type"),
                severity,
                reading.get("people_affected"),
                reading.get("response_time"),
                self._optional_boolean(
                    reading.get("synthetic_incident_context", False)
                ) or False,
            ),
        )
        return self.cur.rowcount == 1

    def _insert_energy(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.energy_readings (
                sensor_id,
                facility_id,
                reading_ts,
                energy_consumption_kwh,
                voltage,
                current,
                power_factor,
                peak_demand_kw,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("energy_consumption_kwh"),
                r.get("voltage"),
                r.get("current"),
                r.get("power_factor"),
                r.get("peak_demand_kw"),
            ),
        )

        return self.cur.rowcount == 1

    def _insert_water(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.water_readings (
                sensor_id,
                facility_id,
                reading_ts,
                water_consumption_liters,
                water_pressure,
                water_temperature,
                flow_rate,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("water_consumption_liters"),
                r.get("water_pressure"),
                r.get("water_temperature"),
                r.get("flow_rate"),
            ),
        )

        return self.cur.rowcount == 1

    def _insert_waste(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.waste_readings (
                sensor_id,
                facility_id,
                reading_ts,
                waste_type,
                waste_quantity_kg,
                recyclable_quantity_kg,
                hazardous_quantity_kg,
                fill_level_percent,
                fill_rate_percent_per_hour,
                disposal_method,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                'LANDFILL',
                'OK',
                false,
                NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("waste_type"),
                r.get("waste_quantity_kg"),
                r.get("recyclable_quantity_kg"),
                r.get("hazardous_quantity_kg"),
                r.get("fill_level_percent"),
                r.get("fill_rate_percent_per_hour"),
            ),
        )

        return self.cur.rowcount == 1

    def _insert_aqi(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.air_quality_readings (
                sensor_id,
                facility_id,
                reading_ts,
                aqi,
                pm25,
                pm10,
                co,
                co2,
                no2,
                so2,
                temperature,
                humidity,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("aqi"),
                r.get("pm25") if r.get("pm25") is not None else 0,
                r.get("pm10") if r.get("pm10") is not None else 0,
                r.get("co") if r.get("co") is not None else 0,
                r.get("co2") if r.get("co2") is not None else 400,
                r.get("no2") if r.get("no2") is not None else 0,
                r.get("so2") if r.get("so2") is not None else 0,
                r.get("temperature")
                if r.get("temperature") is not None
                else r.get("temperature_c"),
                r.get("humidity")
                if r.get("humidity") is not None
                else r.get("humidity_percent"),
            ),
        )

        return self.cur.rowcount == 1

    def _insert_environment(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.environmental_readings (
                sensor_id,
                facility_id,
                reading_ts,
                temperature_c,
                humidity_percent,
                rainfall_mm,
                wind_speed_kmph,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("temperature_c")
                if r.get("temperature_c") is not None
                else r.get("temperature"),
                r.get("humidity_percent")
                if r.get("humidity_percent") is not None
                else r.get("humidity"),
                r.get("rainfall_mm"),
                r.get("wind_speed_kmph"),
            ),
        )

        return self.cur.rowcount == 1

    def _insert_traffic(self, r: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO public.traffic_readings (
                sensor_id,
                facility_id,
                reading_ts,
                vehicle_count,
                heavy_vehicle_count,
                average_speed_kmph,
                congestion_level,
                data_quality_status,
                anomaly_flag,
                anomaly_reason
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                'OK', false, NULL
            )
            ON CONFLICT (sensor_id, reading_ts) DO NOTHING
        """

        self.cur.execute(
            query,
            (
                r.get("sensor_id"),
                r.get("facility_id"),
                r.get("reading_ts"),
                r.get("vehicle_count"),
                r.get("heavy_vehicle_count"),
                r.get("average_speed_kmph"),
                r.get("congestion_level"),
            ),
        )

        return self.cur.rowcount == 1


def load_from_json(filepath: str):
    """Load readings from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_readings(
    readings: List[Dict[str, Any]],
    load_raw: bool = True,
    load_public: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function for loading readings.

    Returns:
        Dictionary containing raw insertion count and public counts.
    """

    result = {
        "raw_inserted": 0,
        "valid_readings": 0,
        "rejected_readings": 0,
        "public_inserted": {},
    }

    # Preserve original payloads in raw before validation/normalization.
    if load_raw:
        with DataLoader() as raw_loader:
            result["raw_inserted"] = raw_loader.load_to_raw(readings)

    if load_public:
        validator = DataValidator()
        valid, invalid = validator.filter_valid_readings(readings)
        cleaned = DataCleaner().clean_batch(valid)
        result["valid_readings"] = len(cleaned)
        result["rejected_readings"] = len(invalid)
        with DataLoader() as public_loader:
            result["public_inserted"] = public_loader.load_to_public_domain(cleaned)

    return result


def main():
    """
    Optional command-line entry point.

    Reads synthetic_readings.json from the configured raw directory
    and loads it into PostgreSQL.
    """

    filepath = os.path.join(
        config.RAW_DIR,
        "synthetic_readings.json",
    )

    if not os.path.exists(filepath):
        print(f"Input file not found: {filepath}")
        return

    readings = load_from_json(filepath)

    result = load_readings(readings)

    print(
        f"Raw rows inserted: {result['raw_inserted']}"
    )
    print(f"Valid readings: {result['valid_readings']}")
    print(f"Rejected readings: {result['rejected_readings']}")
    print(f"Public rows inserted: {result['public_inserted']}")


if __name__ == "__main__":
    main()