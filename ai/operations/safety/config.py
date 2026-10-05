"""Configuration for Safety Operations AI."""

TIMESTAMP_COLUMN = "reading_ts"
FACILITY_COLUMN = "facility_id"
SENSOR_COLUMN = "sensor_id"

INCIDENT_COUNT_COLUMN = "incident_count"
RESPONSE_TIME_COLUMN = "response_time_minutes"
SEVERITY_COLUMN = "severity"

HIGH_INCIDENT_COUNT_THRESHOLD = 3
HIGH_RESPONSE_TIME_THRESHOLD = 10

HIGH_RISK_SCORE_THRESHOLD = 2