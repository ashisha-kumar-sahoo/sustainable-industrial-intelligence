"""
Data Validator for sensor readings.
Validates incoming readings for required fields, data types, ranges, and constraints.
"""
from typing import Dict, Any, List, Tuple
import datetime

class ValidationError(Exception):
    pass

class DataValidator:
    """Validates sensor data before processing."""

    # Valid ranges and constraints
    ENERGY_RANGES = {
        'energy_consumption_kwh': (0, 10000),
        'voltage': (0, 1000),
        'current': (0, 2000),
        'power_factor': (0, 1),
        'peak_demand_kw': (0, 10000)
    }

    WATER_RANGES = {
        'water_consumption_liters': (0, 100000),
        'water_pressure': (0, 20),
        'water_temperature': (-10, 120),
        'flow_rate': (0, 5000)
    }

    WASTE_RANGES = {
        'waste_quantity_kg': (0, 50000),
        'recyclable_quantity_kg': (0, 50000),
        'hazardous_quantity_kg': (0, 50000)
    }

    ENV_RANGES = {
        'temperature_c': (-50, 65),
        'humidity_percent': (0, 100),
        'rainfall_mm': (0, 1000),
        'wind_speed_kmph': (0, 300)
    }

    TRAFFIC_RANGES = {
        'vehicle_count': (0, 10000),
        'heavy_vehicle_count': (0, 10000),
        'average_speed_kmph': (0, 200),
        'lane_occupancy_percent': (0, 100)
    }

    def validate_required_fields(self, reading: Dict[str, Any], required: List[str]) -> None:
        """Check all required fields are present and not None."""
        for field in required:
            if field not in reading or reading[field] is None:
                raise ValidationError(f"Missing required field: {field}")

    def validate_numeric_range(self, reading: Dict[str, Any], ranges: Dict[str, Tuple]) -> None:
        """Validate numeric fields are within specified ranges."""
        for field, (min_val, max_val) in ranges.items():
            if field in reading and reading[field] is not None:
                val = reading[field]
                try:
                    num_val = float(val)
                    if num_val < min_val or num_val > max_val:
                        raise ValidationError(f"{field}={num_val} out of range [{min_val}, {max_val}]")
                except (ValueError, TypeError):
                    raise ValidationError(f"Invalid numeric value for {field}: {val}")

    def validate_timestamp(self, reading: Dict[str, Any]) -> None:
        """Validate timestamp format."""
        if 'reading_ts' in reading and reading['reading_ts']:
            try:
                if isinstance(reading['reading_ts'], str):
                    # Try to parse
                    datetime.datetime.fromisoformat(reading['reading_ts'].replace(' ', 'T'))
            except Exception:
                raise ValidationError(f"Invalid timestamp: {reading['reading_ts']}")

    def validate_energy_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate energy reading."""
        errors = []
        try:
            required = ['sensor_id', 'facility_id', 'reading_ts', 'energy_consumption_kwh']
            self.validate_required_fields(reading, required)
            self.validate_numeric_range(reading, self.ENERGY_RANGES)
            self.validate_timestamp(reading)
            return True, []
        except ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate_water_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate water reading."""
        errors = []
        try:
            required = ['sensor_id', 'facility_id', 'reading_ts', 'water_consumption_liters']
            self.validate_required_fields(reading, required)
            self.validate_numeric_range(reading, self.WATER_RANGES)
            self.validate_timestamp(reading)
            return True, []
        except ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate_waste_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        try:
            required = ['sensor_id', 'facility_id', 'reading_ts', 'waste_quantity_kg']
            self.validate_required_fields(reading, required)
            self.validate_numeric_range(reading, self.WASTE_RANGES)
            self.validate_timestamp(reading)
            return True, []
        except ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate_environment_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        try:
            required = ['sensor_id', 'facility_id', 'reading_ts']
            self.validate_required_fields(reading, required)
            self.validate_numeric_range(reading, self.ENV_RANGES)
            self.validate_timestamp(reading)
            return True, []
        except ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate_traffic_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        try:
            required = ['sensor_id', 'facility_id', 'reading_ts', 'vehicle_count']
            self.validate_required_fields(reading, required)
            self.validate_numeric_range(reading, self.TRAFFIC_RANGES)
            self.validate_timestamp(reading)
            # Business rule: heavy <= vehicle
            if reading.get('heavy_vehicle_count') and reading.get('vehicle_count'):
                if float(reading['heavy_vehicle_count']) > float(reading['vehicle_count']):
                    raise ValidationError('heavy_vehicle_count cannot exceed vehicle_count')
            return True, []
        except ValidationError as e:
            errors.append(str(e))
            return False, errors

    def validate(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate reading based on sensor type."""
        sensor_type = reading.get('sensor_type', '').upper()
        if sensor_type == 'ENERGY':
            return self.validate_energy_reading(reading)
        elif sensor_type == 'WATER':
            return self.validate_water_reading(reading)
        elif sensor_type == 'WASTE':
            return self.validate_waste_reading(reading)
        elif sensor_type in ('ENVIRONMENT', 'TEMPERATURE', 'HUMIDITY', 'AQI'):
            return self.validate_environment_reading(reading)
        elif sensor_type == 'TRAFFIC':
            return self.validate_traffic_reading(reading)
        else:
            # Generic validation
            try:
                required = ['sensor_id', 'facility_id', 'reading_ts']
                self.validate_required_fields(reading, required)
                self.validate_timestamp(reading)
                return True, []
            except ValidationError as e:
                return False, [str(e)]

    def filter_valid_readings(self, readings: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split readings into valid and invalid."""
        valid = []
        invalid = []
        for r in readings:
            ok, errs = self.validate(r)
            if ok:
                valid.append(r)
            else:
                invalid.append({**r, 'errors': errs})
        return valid, invalid