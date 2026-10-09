"""Validate sensor readings before cleaning and database insertion."""

from __future__ import annotations

import datetime
import math
from typing import Any


class ValidationError(Exception):
    """Raised when a sensor reading violates its data contract."""


class DataValidator:
    """Validate required fields, numeric ranges, timestamps, and domain rules."""

    ENERGY_RANGES = {
        "energy_consumption_kwh": (0, 10_000),
        "voltage": (0, 1_000),
        "current": (0, 2_000),
        "power_factor": (0, 1),
        "peak_demand_kw": (0, 10_000),
    }
    WATER_RANGES = {
        "water_consumption_liters": (0, 100_000),
        "water_pressure": (0, 20),
        "water_temperature": (-10, 120),
        "flow_rate": (0, 5_000),
    }
    WASTE_RANGES = {
        "waste_quantity_kg": (0, 50_000),
        "recyclable_quantity_kg": (0, 50_000),
        "hazardous_quantity_kg": (0, 50_000),
        "fill_level_percent": (0, 100),
        "fill_rate_percent_per_hour": (0, 100),
    }
    AQI_RANGES = {
        "aqi": (0, 500),
        "pm25": (0, 2_000),
        "pm10": (0, 3_000),
        "co": (0, 100),
        "co2": (0, 10_000),
        "no2": (0, 1_000),
        "so2": (0, 1_000),
    }
    ENVIRONMENT_RANGES = {
        "temperature_c": (-50, 65),
        "humidity_percent": (0, 100),
        "rainfall_mm": (0, 1_000),
        "wind_speed_kmph": (0, 300),
    }
    TRAFFIC_RANGES = {
        "vehicle_count": (0, 10_000),
        "heavy_vehicle_count": (0, 10_000),
        "average_speed_kmph": (0, 200),
        "lane_occupancy_percent": (0, 100),
    }
    EQUIPMENT_RANGES = {
        "vibration_mms": (0, 100),
        "temperature_c": (-50, 200),
        "operating_hours": (0, 1_000_000),
        "utilization_percent": (0, 100),
    }
    SAFETY_RANGES = {
        "gas_leak_ppm": (0, 1_000_000),
        "safety_temperature_c": (-50, 200),
        "people_affected": (0, 1_000_000),
        "response_time": (0, 1_000_000),
    }

    @staticmethod
    def validate_required_fields(
        reading: dict[str, Any],
        required_fields: list[str],
    ) -> None:
        """Reject readings with a missing or ``None`` required field."""
        for field in required_fields:
            if field not in reading or reading[field] is None:
                raise ValidationError(f"Missing required field: {field}")

    @staticmethod
    def validate_numeric_range(
        reading: dict[str, Any],
        allowed_ranges: dict[str, tuple[float, float]],
    ) -> None:
        """Validate the range of every optional numeric field that is present."""
        for field, (minimum, maximum) in allowed_ranges.items():
            value = reading.get(field)
            if value is None:
                continue

            try:
                numeric_value = float(value)
            except (ValueError, TypeError) as exc:
                raise ValidationError(
                    f"Invalid numeric value for {field}: {value}"
                ) from exc

            if not math.isfinite(numeric_value):
                raise ValidationError(f"{field} must be a finite number, received {value}")
            if not minimum <= numeric_value <= maximum:
                raise ValidationError(
                    f"{field}={numeric_value} out of range [{minimum}, {maximum}]"
                )

    @staticmethod
    def validate_timestamp(reading: dict[str, Any]) -> None:
        """Reject timestamps that cannot be parsed as ISO-8601 values."""
        timestamp = reading.get("reading_ts")
        if not timestamp:
            return

        if isinstance(timestamp, datetime.datetime):
            return
        if not isinstance(timestamp, str):
            raise ValidationError(f"Invalid timestamp: {timestamp}")

        try:
            datetime.datetime.fromisoformat(timestamp.replace(" ", "T"))
        except ValueError as exc:
            raise ValidationError(f"Invalid timestamp: {timestamp}") from exc

    def validate_energy_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate the required fields and ranges for an energy reading."""
        return self._validate_domain(
            reading,
            required_fields=[
                "sensor_id",
                "facility_id",
                "reading_ts",
                "energy_consumption_kwh",
            ],
            allowed_ranges=self.ENERGY_RANGES,
        )

    def validate_water_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate the required fields and ranges for a water reading."""
        return self._validate_domain(
            reading,
            required_fields=[
                "sensor_id",
                "facility_id",
                "reading_ts",
                "water_consumption_liters",
            ],
            allowed_ranges=self.WATER_RANGES,
        )

    def validate_waste_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate waste quantities and any optional fill telemetry."""
        return self._validate_domain(
            reading,
            required_fields=[
                "sensor_id",
                "facility_id",
                "reading_ts",
                "waste_quantity_kg",
            ],
            allowed_ranges=self.WASTE_RANGES,
        )

    def validate_aqi_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Require a real AQI measurement instead of inventing one in the loader."""
        return self._validate_domain(
            reading,
            required_fields=["sensor_id", "facility_id", "reading_ts", "aqi"],
            allowed_ranges=self.AQI_RANGES,
        )

    def validate_environment_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate environmental readings, allowing optional measurements."""
        return self._validate_domain(
            reading,
            required_fields=["sensor_id", "facility_id", "reading_ts"],
            allowed_ranges=self.ENVIRONMENT_RANGES,
        )

    def validate_traffic_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate traffic readings, including heavy-vehicle count consistency."""
        valid, errors = self._validate_domain(
            reading,
            required_fields=[
                "sensor_id",
                "facility_id",
                "reading_ts",
                "vehicle_count",
            ],
            allowed_ranges=self.TRAFFIC_RANGES,
        )
        if not valid:
            return valid, errors

        heavy_vehicle_count = reading.get("heavy_vehicle_count")
        vehicle_count = reading.get("vehicle_count")
        if heavy_vehicle_count is not None and vehicle_count is not None:
            if float(heavy_vehicle_count) > float(vehicle_count):
                return False, [
                    "heavy_vehicle_count cannot exceed vehicle_count"
                ]

        return True, []

    def validate_equipment_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate the telemetry required by equipment monitoring models."""
        return self._validate_domain(
            reading,
            required_fields=[
                "sensor_id", "facility_id", "reading_ts", "equipment_id",
                "vibration_mms", "temperature_c", "operating_hours",
                "utilization_percent",
            ],
            allowed_ranges=self.EQUIPMENT_RANGES,
        )

    def validate_safety_reading(
        self,
        reading: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate safety telemetry and any supplied synthetic incident context."""
        return self._validate_domain(
            reading,
            required_fields=["sensor_id", "facility_id", "reading_ts", "gas_leak_ppm"],
            allowed_ranges=self.SAFETY_RANGES,
        )

    def _validate_domain(
        self,
        reading: dict[str, Any],
        required_fields: list[str],
        allowed_ranges: dict[str, tuple[float, float]],
    ) -> tuple[bool, list[str]]:
        """Run the shared validation steps for a domain-specific contract."""
        try:
            self.validate_required_fields(reading, required_fields)
            self.validate_numeric_range(reading, allowed_ranges)
            self.validate_timestamp(reading)
        except ValidationError as error:
            return False, [str(error)]
        return True, []

    def validate(self, reading: dict[str, Any]) -> tuple[bool, list[str]]:
        """Select a domain validator from the reading's sensor type."""
        sensor_type = str(reading.get("sensor_type", "")).upper()
        validators = {
            "ENERGY": self.validate_energy_reading,
            "WATER": self.validate_water_reading,
            "WASTE": self.validate_waste_reading,
            "AQI": self.validate_aqi_reading,
            "ENVIRONMENT": self.validate_environment_reading,
            "TEMPERATURE": self.validate_environment_reading,
            "HUMIDITY": self.validate_environment_reading,
            "TRAFFIC": self.validate_traffic_reading,
            "EQUIPMENT": self.validate_equipment_reading,
            "SAFETY": self.validate_safety_reading,
        }

        validator = validators.get(sensor_type)
        if validator:
            return validator(reading)

        # Unknown sensor types are retained in raw storage only when their
        # identity and timestamp metadata are valid.
        try:
            self.validate_required_fields(
                reading,
                ["sensor_id", "facility_id", "reading_ts"],
            )
            self.validate_timestamp(reading)
        except ValidationError as error:
            return False, [str(error)]
        return True, []

    def filter_valid_readings(
        self,
        readings: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Split a batch into valid records and records with attached errors."""
        valid_readings = []
        rejected_readings = []

        for reading in readings:
            is_valid, errors = self.validate(reading)
            if is_valid:
                valid_readings.append(reading)
            else:
                rejected_readings.append({**reading, "errors": errors})

        return valid_readings, rejected_readings
