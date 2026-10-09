"""Normalize sensor readings before public-table insertion."""

from __future__ import annotations

import datetime
from typing import Any


class DataCleaner:
    """Clean timestamps, convert common types, and fill safe domain defaults."""

    def clean_energy_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Fill optional energy fields without overwriting valid zero values."""
        cleaned = reading.copy()
        if cleaned.get("power_factor") is None:
            cleaned["power_factor"] = 0.85
        if (
            cleaned.get("peak_demand_kw") is None
            and cleaned.get("energy_consumption_kwh")
        ):
            cleaned["peak_demand_kw"] = cleaned["energy_consumption_kwh"] * 1.2
        if cleaned.get("voltage") is None:
            cleaned["voltage"] = 415.0
        if cleaned.get("current") is None:
            cleaned["current"] = 0.0
        return cleaned

    def clean_water_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Fill optional water pressure, temperature, and flow-rate fields."""
        cleaned = reading.copy()
        if cleaned.get("water_pressure") is None:
            cleaned["water_pressure"] = 4.0
        if cleaned.get("water_temperature") is None:
            cleaned["water_temperature"] = 25.0
        if cleaned.get("flow_rate") is None:
            consumption = cleaned.get("water_consumption_liters") or 0
            cleaned["flow_rate"] = consumption / 3600.0
        return cleaned

    def clean_waste_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Fill optional waste classification and quantity fields."""
        cleaned = reading.copy()
        if cleaned.get("recyclable_quantity_kg") is None:
            cleaned["recyclable_quantity_kg"] = 0.0
        if cleaned.get("hazardous_quantity_kg") is None:
            cleaned["hazardous_quantity_kg"] = 0.0
        if cleaned.get("waste_type") is None:
            cleaned["waste_type"] = "General"
        return cleaned

    def clean_environment_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Fill optional weather/environment fields with explicit defaults."""
        cleaned = reading.copy()
        if cleaned.get("humidity_percent") is None:
            cleaned["humidity_percent"] = 60.0
        if cleaned.get("rainfall_mm") is None:
            cleaned["rainfall_mm"] = 0.0
        if cleaned.get("wind_speed_kmph") is None:
            cleaned["wind_speed_kmph"] = 0.0
        return cleaned

    def clean_traffic_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Fill optional traffic indicators when the source omits them."""
        cleaned = reading.copy()
        if cleaned.get("heavy_vehicle_count") is None:
            cleaned["heavy_vehicle_count"] = 0
        if cleaned.get("average_speed_kmph") is None:
            cleaned["average_speed_kmph"] = 40.0
        if cleaned.get("congestion_level") is None:
            cleaned["congestion_level"] = "MEDIUM"
        if cleaned.get("lane_occupancy_percent") is None:
            cleaned["lane_occupancy_percent"] = 50.0
        return cleaned

    @staticmethod
    def _normalize_timestamp(reading: dict[str, Any]) -> None:
        """Normalize parseable timestamp strings while preserving timezone data."""
        timestamp = reading.get("reading_ts")
        if not isinstance(timestamp, str) or not timestamp:
            return

        try:
            parsed_timestamp = datetime.datetime.fromisoformat(
                timestamp.replace(" ", "T")
            )
        except ValueError:
            # Validation reports invalid timestamps; cleaning must not disguise them.
            return

        reading["reading_ts"] = parsed_timestamp.isoformat(sep=" ")

    @staticmethod
    def _convert_common_types(reading: dict[str, Any]) -> None:
        """Convert identity/count fields to integers where conversion is safe."""
        integer_fields = {
            "sensor_id",
            "facility_id",
            "vehicle_count",
            "heavy_vehicle_count",
        }
        for field in integer_fields:
            value = reading.get(field)
            if value is None:
                continue

            try:
                reading[field] = int(float(value))
            except (TypeError, ValueError, OverflowError):
                # Preserve the original value so validation can reject it clearly.
                continue

    def clean_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Normalize one record and apply the defaults for its sensor type."""
        cleaned = reading.copy()
        sensor_type = str(cleaned.get("sensor_type", "")).upper()

        self._normalize_timestamp(cleaned)
        self._convert_common_types(cleaned)

        cleaners = {
            "ENERGY": self.clean_energy_reading,
            "WATER": self.clean_water_reading,
            "WASTE": self.clean_waste_reading,
            "ENVIRONMENT": self.clean_environment_reading,
            "TEMPERATURE": self.clean_environment_reading,
            "HUMIDITY": self.clean_environment_reading,
            "AQI": self.clean_environment_reading,
            "TRAFFIC": self.clean_traffic_reading,
        }
        cleaner = cleaners.get(sensor_type)
        return cleaner(cleaned) if cleaner else cleaned

    def clean_batch(self, readings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Clean every reading in a batch."""
        return [self.clean_reading(reading) for reading in readings]
