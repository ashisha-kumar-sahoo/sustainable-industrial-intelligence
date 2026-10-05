"""Configuration for Traffic Operations AI."""

TIMESTAMP_COLUMN = "reading_ts"
FACILITY_COLUMN = "facility_id"
SENSOR_COLUMN = "sensor_id"

VEHICLE_COUNT_COLUMN = "vehicle_count"
HEAVY_VEHICLE_COUNT_COLUMN = "heavy_vehicle_count"
SPEED_COLUMN = "average_speed_kmph"
CONGESTION_COLUMN = "congestion_level"
OCCUPANCY_COLUMN = "lane_occupancy_percent"

HIGH_VEHICLE_COUNT_THRESHOLD = 200
LOW_SPEED_THRESHOLD = 20
HIGH_OCCUPANCY_THRESHOLD = 80

HOTSPOT_SCORE_THRESHOLD = 2