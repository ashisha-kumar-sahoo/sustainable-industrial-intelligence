"""
Data Cleaner for sensor readings.
Handles missing values, normalizes data, and prepares for database loading.
"""
from typing import Dict, Any, List
import datetime

class DataCleaner:
    """Cleans and normalizes sensor data."""

    def clean_energy_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean energy reading."""
        cleaned = reading.copy()
        # Fill defaults
        if cleaned.get('power_factor') is None:
            cleaned['power_factor'] = 0.85
        if cleaned.get('peak_demand_kw') is None and cleaned.get('energy_consumption_kwh'):
            cleaned['peak_demand_kw'] = cleaned['energy_consumption_kwh'] * 1.2
        if cleaned.get('voltage') is None:
            cleaned['voltage'] = 415.0
        if cleaned.get('current') is None:
            cleaned['current'] = 0.0
        return cleaned

    def clean_water_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean water reading."""
        cleaned = reading.copy()
        if cleaned.get('water_pressure') is None:
            cleaned['water_pressure'] = 4.0
        if cleaned.get('water_temperature') is None:
            cleaned['water_temperature'] = 25.0
        if cleaned.get('flow_rate') is None:
            cleaned['flow_rate'] = cleaned.get('water_consumption_liters', 0) / 3600.0
        return cleaned

    def clean_waste_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean waste reading."""
        cleaned = reading.copy()
        if cleaned.get('recyclable_quantity_kg') is None:
            cleaned['recyclable_quantity_kg'] = 0.0
        if cleaned.get('hazardous_quantity_kg') is None:
            cleaned['hazardous_quantity_kg'] = 0.0
        if cleaned.get('waste_type') is None:
            cleaned['waste_type'] = 'General'
        return cleaned

    def clean_environment_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean environment reading."""
        cleaned = reading.copy()
        if cleaned.get('humidity_percent') is None:
            cleaned['humidity_percent'] = 60.0
        if cleaned.get('rainfall_mm') is None:
            cleaned['rainfall_mm'] = 0.0
        if cleaned.get('wind_speed_kmph') is None:
            cleaned['wind_speed_kmph'] = 0.0
        return cleaned

    def clean_traffic_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean traffic reading."""
        cleaned = reading.copy()
        if cleaned.get('heavy_vehicle_count') is None:
            cleaned['heavy_vehicle_count'] = 0
        if cleaned.get('average_speed_kmph') is None:
            cleaned['average_speed_kmph'] = 40.0
        if cleaned.get('congestion_level') is None:
            cleaned['congestion_level'] = 'MEDIUM'
        if cleaned.get('lane_occupancy_percent') is None:
            cleaned['lane_occupancy_percent'] = 50.0
        return cleaned

    def clean_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Clean reading based on sensor type."""
        cleaned = reading.copy()
        sensor_type = str(cleaned.get('sensor_type', '')).upper()

        # Normalize timestamp
        if cleaned.get('reading_ts'):
            try:
                if isinstance(cleaned['reading_ts'], str):
                    # Ensure proper format
                    dt = datetime.datetime.fromisoformat(cleaned['reading_ts'].replace(' ', 'T'))
                    cleaned['reading_ts'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass

        # Type conversion
        numeric_fields = ['sensor_id', 'facility_id', 'vehicle_count', 'heavy_vehicle_count']
        for field in numeric_fields:
            if field in cleaned and cleaned[field] is not None:
                try:
                    if field in ['vehicle_count', 'heavy_vehicle_count', 'sensor_id', 'facility_id']:
                        cleaned[field] = int(float(cleaned[field]))
                    else:
                        cleaned[field] = float(cleaned[field])
                except Exception:
                    pass

        # Apply type-specific cleaning
        if sensor_type == 'ENERGY':
            cleaned = self.clean_energy_reading(cleaned)
        elif sensor_type == 'WATER':
            cleaned = self.clean_water_reading(cleaned)
        elif sensor_type == 'WASTE':
            cleaned = self.clean_waste_reading(cleaned)
        elif sensor_type in ('ENVIRONMENT', 'TEMPERATURE', 'HUMIDITY', 'AQI'):
            cleaned = self.clean_environment_reading(cleaned)
        elif sensor_type == 'TRAFFIC':
            cleaned = self.clean_traffic_reading(cleaned)

        return cleaned

    def clean_batch(self, readings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean batch of readings."""
        return [self.clean_reading(r) for r in readings]