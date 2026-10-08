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
import uuid

from . import config

class SensorSimulator:
    """Simulates IoT sensor data for all industrial domains."""

    def __init__(self, start_date: str = None, end_date: str = None, num_sensors: int = 50):
        self.start_date = datetime.fromisoformat(start_date or config.SIMULATOR_CONFIG['start_date'])
        self.end_date = datetime.fromisoformat(end_date or config.SIMULATOR_CONFIG['end_date'])
        self.num_sensors = num_sensors
        self.facilities = list(range(1, 21))  # 20 facilities as per schema

    def generate_timestamp(self) -> str:
        """Generate realistic timestamp within range."""
        delta = self.end_date - self.start_date
        random_seconds = random.randint(0, int(delta.total_seconds()))
        ts = self.start_date + timedelta(seconds=random_seconds)
        return ts.strftime('%Y-%m-%d %H:%M:%S')

    def generate_energy_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate energy sensor reading."""
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'ENERGY',
            'reading_ts': self.generate_timestamp(),
            'energy_consumption_kwh': round(random.uniform(5.0, 200.0), 3),
            'voltage': round(random.uniform(380.0, 440.0), 2),
            'current': round(random.uniform(10.0, 300.0), 3),
            'power_factor': round(random.uniform(0.7, 0.95), 3),
            'peak_demand_kw': round(random.uniform(10.0, 250.0), 3)
        }

    def generate_water_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate water sensor reading."""
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'WATER',
            'reading_ts': self.generate_timestamp(),
            'water_consumption_liters': round(random.uniform(100.0, 10000.0), 2),
            'water_pressure': round(random.uniform(2.0, 8.0), 2),
            'water_temperature': round(random.uniform(15.0, 40.0), 2),
            'flow_rate': round(random.uniform(50.0, 2000.0), 3)
        }

    def generate_waste_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate waste sensor reading."""
        waste_types = ['Plastic', 'Metal', 'Organic', 'Chemical', 'Paper', 'General']
        total = round(random.uniform(10.0, 1000.0), 2)
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'WASTE',
            'reading_ts': self.generate_timestamp(),
            'waste_type': random.choice(waste_types),
            'waste_quantity_kg': total,
            'recyclable_quantity_kg': round(total * random.uniform(0.1, 0.8), 2),
            'hazardous_quantity_kg': round(total * random.uniform(0.0, 0.1), 2),
            'fill_level_percent': round(random.uniform(10.0, 95.0), 2),
            'fill_rate_percent_per_hour': round(random.uniform(0.0, 8.0), 3)
        }

    def generate_environment_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate environmental sensor reading."""
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'ENVIRONMENT',
            'reading_ts': self.generate_timestamp(),
            'temperature_c': round(random.uniform(20.0, 45.0), 2),
            'humidity_percent': round(random.uniform(30.0, 90.0), 2),
            'rainfall_mm': round(random.uniform(0.0, 50.0), 2),
            'wind_speed_kmph': round(random.uniform(0.0, 25.0), 2)
        }

    def generate_traffic_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate traffic sensor reading."""
        congestion_levels = ['LOW', 'MEDIUM', 'HIGH', 'SEVERE']
        vehicles = random.randint(0, 500)
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'TRAFFIC',
            'reading_ts': self.generate_timestamp(),
            'vehicle_count': vehicles,
            'heavy_vehicle_count': random.randint(0, min(vehicles, 100)),
            'average_speed_kmph': round(random.uniform(10.0, 60.0), 2),
            'congestion_level': random.choice(congestion_levels)
        }

    def generate_equipment_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate equipment sensor reading."""
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'EQUIPMENT',
            'reading_ts': self.generate_timestamp(),
            'equipment_id': f"EQ-{random.randint(1, 100):03d}",
            'vibration_mms': round(random.uniform(0.1, 5.0), 3),
            'temperature_c': round(random.uniform(30.0, 90.0), 2),
            'operating_hours': round(random.uniform(1.0, 24.0), 2),
            'status': random.choice(['NORMAL', 'WARNING', 'CRITICAL'])
        }

    def generate_safety_reading(self, sensor_id: int = None, facility_id: int = None) -> Dict[str, Any]:
        """Generate safety sensor reading."""
        return {
            'sensor_id': sensor_id or random.randint(1, 140),
            'facility_id': facility_id or random.choice(self.facilities),
            'sensor_type': 'SAFETY',
            'reading_ts': self.generate_timestamp(),
            'gas_leak_ppm': round(random.uniform(0.0, 10.0), 3),
            'smoke_detected': random.choice([0, 1]),
            'fire_alarm': random.choice([0, 1]),
            'emergency_button': random.choice([0, 1]),
            'temperature_c': round(random.uniform(20.0, 60.0), 2)
        }

    def generate_batch(self, size: int = 10) -> List[Dict[str, Any]]:
        """Generate a batch of mixed sensor readings."""
        generators = [
            self.generate_energy_reading,
            self.generate_water_reading,
            self.generate_waste_reading,
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

def main():
    simulator = SensorSimulator()
    batch = simulator.generate_batch(size=20)
    filepath = simulator.save_to_file(batch, 'synthetic_readings.json')
    print(f"Generated {len(batch)} readings to {filepath}")

if __name__ == '__main__':
    main()