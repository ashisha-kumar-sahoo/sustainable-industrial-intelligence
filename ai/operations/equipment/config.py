"""Configuration for Equipment Operations AI."""

TIMESTAMP_COLUMN = "reading_ts"
FACILITY_COLUMN = "facility_id"
SENSOR_COLUMN = "sensor_id"

TEMPERATURE_COLUMN = "temperature_c"
VIBRATION_COLUMN = "vibration"
ENERGY_COLUMN = "energy_consumption_kwh"

HIGH_TEMPERATURE_THRESHOLD = 80
HIGH_VIBRATION_THRESHOLD = 4
HIGH_ENERGY_THRESHOLD = 60

ANOMALY_CONTAMINATION = 0.10