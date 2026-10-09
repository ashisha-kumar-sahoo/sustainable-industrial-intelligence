"""
Sensor Simulator for Sustainable Industrial Intelligence.

Generates realistic synthetic sensor readings across all domains:
- Energy
- Water
- Waste
- Environment
- Traffic
- Equipment
- Safety
"""
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from zoneinfo import ZoneInfo

from . import config

class SensorSimulator:
    """Simulates IoT sensor data for all industrial domains."""

    def __init__(
        self,
        start_date: str = None,
        end_date: str = None,
        num_sensors: int = None,
        sensor_registry=None,
    ):
        settings = config.SIMULATOR_CONFIG
        self.sensor_registry = {
            str(kind).upper(): list(rows)
            for kind, rows in (sensor_registry or {}).items()
        }
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz).replace(minute=0, second=0, microsecond=0)
        configured_end = end_date or settings.get("end_date")
        configured_start = start_date or settings.get("start_date")
        self.end_date = self._parse_datetime(configured_end, now) if configured_end else now
        default_start = self.end_date - timedelta(days=int(settings.get("window_days", 7)))
        self.start_date = (
            self._parse_datetime(configured_start, default_start)
            if configured_start
            else default_start
        )
        if self.end_date <= self.start_date:
            raise ValueError("Simulation end_date must be after start_date.")
        self.num_sensors = num_sensors or int(settings.get("num_sensors", 50))
        self.facilities = list(range(1, 21))

    @staticmethod
    def _parse_datetime(value: str, fallback: datetime) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=fallback.tzinfo)
        return parsed

    def _identity(self, sensor_type: str, sensor_id=None, facility_id=None):
        """Choose a sensor/facility pair from PostgreSQL metadata when available."""
        if sensor_id is not None and facility_id is not None:
            return sensor_id, facility_id

        kind = str(sensor_type).upper()
        compatible = [kind]
        if kind == "ENVIRONMENT":
            compatible = ["TEMPERATURE", "HUMIDITY"]
        elif kind in {"EQUIPMENT", "SAFETY"}:
            # These domains have dedicated sensor types after migration 002.
            compatible = [kind]

        candidates = [row for name in compatible for row in self.sensor_registry.get(name, [])]
        if facility_id is not None:
            candidates = [row for row in candidates if int(row[1]) == int(facility_id)]
        if sensor_id is not None:
            candidates = [row for row in candidates if int(row[0]) == int(sensor_id)]
        if candidates:
            selected = random.choice(candidates)
            return int(selected[0]), int(selected[1])

        # Offline-only fallback; the main demo path loads the registry from PostgreSQL.
        return sensor_id or random.randint(1, 140), facility_id or random.choice(self.facilities)

    def generate_timestamp(self) -> str:
        """Generate realistic timestamp within range."""
        delta = self.end_date - self.start_date
        random_seconds = random.randint(0, int(delta.total_seconds()))
        ts = self.start_date + timedelta(seconds=random_seconds)
        return ts.strftime('%Y-%m-%d %H:%M:%S%z')

    def generate_energy_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate energy sensor reading."""
        selected_sensor, selected_facility = self._identity('ENERGY', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'ENERGY',
            'reading_ts': self.generate_timestamp(),
            'energy_consumption_kwh': round(random.uniform(5.0, 200.0), 3),
            'voltage': round(random.uniform(380.0, 440.0), 2),
            'current': round(random.uniform(10.0, 300.0), 3),
            'power_factor': round(random.uniform(0.7, 0.95), 3),
            'peak_demand_kw': round(random.uniform(10.0, 250.0), 3)
        }

    def generate_water_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate water sensor reading."""
        selected_sensor, selected_facility = self._identity('WATER', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'WATER',
            'reading_ts': self.generate_timestamp(),
            'water_consumption_liters': round(random.uniform(100.0, 10000.0), 2),
            'water_pressure': round(random.uniform(2.0, 8.0), 2),
            'water_temperature': round(random.uniform(15.0, 40.0), 2),
            'flow_rate': round(random.uniform(50.0, 2000.0), 3)
        }

    def generate_waste_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate waste sensor reading."""
        waste_types = ['Plastic', 'Metal', 'Organic', 'Chemical', 'Paper', 'General']
        total = round(random.uniform(10.0, 1000.0), 2)
        selected_sensor, selected_facility = self._identity('WASTE', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'WASTE',
            'reading_ts': self.generate_timestamp(),
            'waste_type': random.choice(waste_types),
            'waste_quantity_kg': total,
            'recyclable_quantity_kg': round(total * random.uniform(0.1, 0.8), 2),
            'hazardous_quantity_kg': round(total * random.uniform(0.0, 0.1), 2),
            'fill_level_percent': round(random.uniform(10.0, 95.0), 2),
            'fill_rate_percent_per_hour': round(random.uniform(0.0, 8.0), 3)
        }

    def generate_air_quality_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate an air-quality reading for the AQI stream."""
        pm25 = round(random.uniform(8.0, 120.0), 2)
        pm10 = round(max(pm25, random.uniform(15.0, 220.0)), 2)
        selected_sensor, selected_facility = self._identity('AQI', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'AQI',
            'reading_ts': self.generate_timestamp(),
            'aqi': random.randint(25, 180),
            'pm25': pm25,
            'pm10': pm10,
            'co': round(random.uniform(0.1, 5.0), 3),
            'co2': round(random.uniform(350.0, 900.0), 2),
            'no2': round(random.uniform(5.0, 100.0), 2),
            'so2': round(random.uniform(2.0, 80.0), 2),
            'temperature': round(random.uniform(20.0, 45.0), 2),
            'humidity': round(random.uniform(30.0, 90.0), 2),
        }

    def generate_environment_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate environmental sensor reading."""
        selected_sensor, selected_facility = self._identity('ENVIRONMENT', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'ENVIRONMENT',
            'reading_ts': self.generate_timestamp(),
            'temperature_c': round(random.uniform(20.0, 45.0), 2),
            'humidity_percent': round(random.uniform(30.0, 90.0), 2),
            'rainfall_mm': round(random.uniform(0.0, 50.0), 2),
            'wind_speed_kmph': round(random.uniform(0.0, 25.0), 2)
        }

    def generate_traffic_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate traffic sensor reading."""
        congestion_levels = ['LOW', 'MEDIUM', 'HIGH', 'SEVERE']
        vehicles = random.randint(0, 500)
        selected_sensor, selected_facility = self._identity('TRAFFIC', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'TRAFFIC',
            'reading_ts': self.generate_timestamp(),
            'vehicle_count': vehicles,
            'heavy_vehicle_count': random.randint(0, min(vehicles, 100)),
            'average_speed_kmph': round(random.uniform(10.0, 60.0), 2),
            'congestion_level': random.choice(congestion_levels)
        }

    def generate_equipment_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate equipment sensor reading."""
        selected_sensor, selected_facility = self._identity('EQUIPMENT', sensor_id, facility_id)
        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'EQUIPMENT',
            'reading_ts': self.generate_timestamp(),
            'equipment_id': f"EQ-SENSOR-{selected_sensor:04d}",
            'vibration_mms': round(random.uniform(0.1, 5.0), 3),
            'temperature_c': round(random.uniform(30.0, 90.0), 2),
            'operating_hours': round(random.uniform(1.0, 24.0), 2),
            'utilization_percent': round(random.uniform(10.0, 100.0), 2),
            'equipment_status': random.choice(['NORMAL', 'WARNING', 'CRITICAL'])
        }

    def generate_safety_reading(
        self,
        sensor_id: int = None,
        facility_id: int = None,
    ) -> Dict[str, Any]:
        """Generate safety sensor reading."""
        selected_sensor, selected_facility = self._identity('SAFETY', sensor_id, facility_id)
        gas_level = round(random.uniform(0.0, 10.0), 3)
        smoke_detected = random.random() < 0.04
        fire_alarm = smoke_detected and random.random() < 0.25
        emergency_button = random.random() < 0.01

        # These are explicitly synthetic incident-context labels, not real
        # incident records or measured emergency response times.
        if fire_alarm or emergency_button:
            incident_type = 'FIRE_OR_EMERGENCY'
            severity = 'Critical'
        elif smoke_detected or gas_level >= 7.5:
            incident_type = 'SMOKE_OR_GAS_ALERT'
            severity = 'High'
        elif gas_level >= 4.0:
            incident_type = 'ELEVATED_GAS_READING'
            severity = 'Medium'
        else:
            incident_type = 'ROUTINE_MONITORING'
            severity = 'Low'

        people_affected = random.randint(1, 5) if severity in {'High', 'Critical'} else 0
        response_time = (
            round(random.uniform(2.0, 25.0), 2)
            if severity in {"High", "Critical"}
            else 0.0
        )

        return {
            'sensor_id': selected_sensor,
            'facility_id': selected_facility,
            'sensor_type': 'SAFETY',
            'reading_ts': self.generate_timestamp(),
            'gas_leak_ppm': gas_level,
            'smoke_detected': smoke_detected,
            'fire_alarm': fire_alarm,
            'emergency_button': emergency_button,
            'safety_temperature_c': round(random.uniform(20.0, 60.0), 2),
            'incident_type': incident_type,
            'severity': severity,
            'people_affected': people_affected,
            'response_time': response_time,
            'synthetic_incident_context': True,
        }

    def generate_batch(self, size: int = 10) -> List[Dict[str, Any]]:
        """Generate a batch of mixed sensor readings."""
        generators = [
            self.generate_energy_reading,
            self.generate_water_reading,
            self.generate_waste_reading,
            self.generate_air_quality_reading,
            self.generate_environment_reading,
            self.generate_traffic_reading,
            self.generate_equipment_reading,
            self.generate_safety_reading
        ]
        readings = []
        for _ in range(size):
            gen = random.choice(generators)
            readings.append(gen())
        return readings

    def generate_all_domains(self, size: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Generate readings organized by domain."""
        return {
            'energy': [self.generate_energy_reading() for _ in range(size)],
            'water': [self.generate_water_reading() for _ in range(size)],
            'waste': [self.generate_waste_reading() for _ in range(size)],
            'air_quality': [self.generate_air_quality_reading() for _ in range(size)],
            'environment': [self.generate_environment_reading() for _ in range(size)],
            'traffic': [self.generate_traffic_reading() for _ in range(size)],
            'equipment': [self.generate_equipment_reading() for _ in range(size)],
            'safety': [self.generate_safety_reading() for _ in range(size)]
        }

    def save_to_file(self, readings: List[Dict[str, Any]], filename: str) -> str:
        """Save readings to JSON file in raw data directory."""
        filepath = os.path.join(config.RAW_DIR, filename)
        with open(filepath, 'w') as f:
            json.dump(readings, f, indent=2)
        return filepath

def _load_sensor_registry():
    """Read the current sensor/facility mapping from PostgreSQL."""
    try:
        from .db_connection import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT sensor_id, facility_id, sensor_type
                    FROM public.sensors
                    WHERE status = 'ACTIVE'
                    ORDER BY sensor_type, sensor_id
                """)
                registry = {}
                for sensor_id, facility_id, sensor_type in cursor.fetchall():
                    registry.setdefault(str(sensor_type).upper(), []).append(
                        (int(sensor_id), int(facility_id))
                    )
                return registry
        finally:
            conn.close()
    except Exception as exc:
        print(
            "Warning: could not load the PostgreSQL sensor registry "
            f"({type(exc).__name__}); using offline fallback identities."
        )
        return {}


def main():
    simulator = SensorSimulator(sensor_registry=_load_sensor_registry())
    per_domain = max(1, int(config.SIMULATOR_CONFIG.get('batch_size', 10)))
    domain_batches = simulator.generate_all_domains(size=per_domain)
    batch = [reading for readings in domain_batches.values() for reading in readings]
    filepath = simulator.save_to_file(batch, 'synthetic_readings.json')
    counts = {domain: len(readings) for domain, readings in domain_batches.items()}
    print(f"Generated {len(batch)} readings across domains: {counts}")
    print(f"Saved readings to {filepath}")

if __name__ == '__main__':
    main()