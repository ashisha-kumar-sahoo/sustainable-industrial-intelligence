-- Additive migration: equipment and safety telemetry support.
-- Run against the existing smart_industrial_estate database after migration 001.
-- Existing rows/tables are preserved; only new columns, tables, constraints,
-- and missing synthetic sensor registrations are added.

BEGIN;

-- Preserve the complete incoming payload in addition to typed columns. This
-- keeps new sensor fields from being lost when the raw schema evolves.
ALTER TABLE raw.raw_sensor_data
    ADD COLUMN IF NOT EXISTS raw_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS equipment_id varchar(40),
    ADD COLUMN IF NOT EXISTS vibration_mms numeric(8,3),
    ADD COLUMN IF NOT EXISTS operating_hours numeric(10,2),
    ADD COLUMN IF NOT EXISTS utilization_percent numeric(5,2),
    ADD COLUMN IF NOT EXISTS equipment_status varchar(20),
    ADD COLUMN IF NOT EXISTS gas_leak_ppm numeric(10,3),
    ADD COLUMN IF NOT EXISTS smoke_detected boolean,
    ADD COLUMN IF NOT EXISTS fire_alarm boolean,
    ADD COLUMN IF NOT EXISTS emergency_button boolean,
    ADD COLUMN IF NOT EXISTS safety_temperature_c numeric(6,2),
    ADD COLUMN IF NOT EXISTS incident_type varchar(40),
    ADD COLUMN IF NOT EXISTS severity varchar(20),
    ADD COLUMN IF NOT EXISTS people_affected integer,
    ADD COLUMN IF NOT EXISTS response_time numeric(8,2);

-- Expand the sensor registry to include the two new operational streams.
ALTER TABLE public.sensors DROP CONSTRAINT IF EXISTS ck_sensors_type;
ALTER TABLE public.sensors
    ADD CONSTRAINT ck_sensors_type
    CHECK (sensor_type IN (
        'ENERGY', 'WATER', 'WASTE', 'AQI', 'TEMPERATURE', 'HUMIDITY',
        'TRAFFIC', 'EQUIPMENT', 'SAFETY'
    ));

CREATE TABLE IF NOT EXISTS public.equipment_readings (
    reading_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamptz NOT NULL,
    equipment_id varchar(40) NOT NULL,
    vibration_mms numeric(8,3),
    temperature_c numeric(6,2),
    operating_hours numeric(10,2),
    utilization_percent numeric(5,2),
    equipment_status varchar(20) NOT NULL DEFAULT 'NORMAL',
    data_quality_status varchar(12) NOT NULL DEFAULT 'OK',
    anomaly_flag boolean NOT NULL DEFAULT false,
    anomaly_reason text,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_equipment_sensor_ts UNIQUE (sensor_id, reading_ts),
    CONSTRAINT fk_equipment_facility FOREIGN KEY (facility_id)
        REFERENCES public.facilities(facility_id) ON DELETE CASCADE,
    CONSTRAINT fk_equipment_sensor FOREIGN KEY (sensor_id)
        REFERENCES public.sensors(sensor_id) ON DELETE CASCADE,
    CONSTRAINT ck_equipment_vibration_nonnegative
        CHECK (vibration_mms IS NULL OR vibration_mms >= 0),
    CONSTRAINT ck_equipment_temperature_range
        CHECK (temperature_c IS NULL OR temperature_c BETWEEN -50 AND 200),
    CONSTRAINT ck_equipment_operating_hours_nonnegative
        CHECK (operating_hours IS NULL OR operating_hours >= 0),
    CONSTRAINT ck_equipment_utilization_range
        CHECK (utilization_percent IS NULL OR utilization_percent BETWEEN 0 AND 100),
    CONSTRAINT ck_equipment_status
        CHECK (equipment_status IN ('NORMAL', 'WARNING', 'CRITICAL', 'OFFLINE')),
    CONSTRAINT ck_equipment_quality
        CHECK (data_quality_status IN ('OK', 'FLAGGED', 'ESTIMATED'))
);

CREATE TABLE IF NOT EXISTS public.safety_readings (
    reading_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamptz NOT NULL,
    gas_leak_ppm numeric(10,3),
    smoke_detected boolean NOT NULL DEFAULT false,
    fire_alarm boolean NOT NULL DEFAULT false,
    emergency_button boolean NOT NULL DEFAULT false,
    temperature_c numeric(6,2),
    incident_type varchar(40),
    severity varchar(20),
    people_affected integer,
    response_time numeric(8,2),
    synthetic_context boolean NOT NULL DEFAULT false,
    data_quality_status varchar(12) NOT NULL DEFAULT 'OK',
    anomaly_flag boolean NOT NULL DEFAULT false,
    anomaly_reason text,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_safety_sensor_ts UNIQUE (sensor_id, reading_ts),
    CONSTRAINT fk_safety_facility FOREIGN KEY (facility_id)
        REFERENCES public.facilities(facility_id) ON DELETE CASCADE,
    CONSTRAINT fk_safety_sensor FOREIGN KEY (sensor_id)
        REFERENCES public.sensors(sensor_id) ON DELETE CASCADE,
    CONSTRAINT ck_safety_gas_nonnegative
        CHECK (gas_leak_ppm IS NULL OR gas_leak_ppm >= 0),
    CONSTRAINT ck_safety_people_nonnegative
        CHECK (people_affected IS NULL OR people_affected >= 0),
    CONSTRAINT ck_safety_response_nonnegative
        CHECK (response_time IS NULL OR response_time >= 0),
    CONSTRAINT ck_safety_severity
        CHECK (severity IS NULL OR severity IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT ck_safety_quality
        CHECK (data_quality_status IN ('OK', 'FLAGGED', 'ESTIMATED'))
);

COMMENT ON TABLE public.equipment_readings IS
    'Equipment telemetry for condition monitoring and predictive-maintenance analysis.';
ALTER TABLE public.safety_readings
    ADD COLUMN IF NOT EXISTS synthetic_context boolean NOT NULL DEFAULT false;

COMMENT ON TABLE public.safety_readings IS
    'Safety sensor telemetry and optional incident context; generated incident labels must be treated as synthetic.';
COMMENT ON COLUMN public.safety_readings.response_time IS
    'Response time in minutes; NULL means no measured response time is available.';

CREATE INDEX IF NOT EXISTS ix_equipment_facility_time
    ON public.equipment_readings (facility_id, reading_ts DESC);
CREATE INDEX IF NOT EXISTS ix_safety_facility_time
    ON public.safety_readings (facility_id, reading_ts DESC);
COMMENT ON COLUMN raw.raw_sensor_data.raw_payload IS
    'Complete incoming JSON payload for newly ingested readings. Existing historical rows default to an empty object because their original payloads were not retained.';

-- Grant read access when the optional dashboard application role exists.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'smart_estate_app') THEN
        EXECUTE 'GRANT SELECT ON public.equipment_readings, public.safety_readings TO smart_estate_app';
    END IF;
END $$;

-- Register one synthetic sensor per facility/domain only where none exists.
-- This makes simulator IDs valid without changing existing sensor identities.
INSERT INTO public.sensors (
    sensor_code, facility_id, sensor_type, sensor_name, unit,
    manufacturer, model, installation_date, status
)
SELECT
    'EQ-SYN-' || lpad(f.facility_id::text, 4, '0'),
    f.facility_id,
    'EQUIPMENT',
    'Synthetic equipment monitor - ' || f.facility_name,
    'mixed',
    'Synthetic',
    'SII-EQ-1',
    CURRENT_DATE,
    'ACTIVE'
FROM public.facilities AS f
WHERE NOT EXISTS (
    SELECT 1 FROM public.sensors AS s
    WHERE s.facility_id = f.facility_id AND s.sensor_type = 'EQUIPMENT'
);

INSERT INTO public.sensors (
    sensor_code, facility_id, sensor_type, sensor_name, unit,
    manufacturer, model, installation_date, status
)
SELECT
    'SF-SYN-' || lpad(f.facility_id::text, 4, '0'),
    f.facility_id,
    'SAFETY',
    'Synthetic safety monitor - ' || f.facility_name,
    'mixed',
    'Synthetic',
    'SII-SF-1',
    CURRENT_DATE,
    'ACTIVE'
FROM public.facilities AS f
WHERE NOT EXISTS (
    SELECT 1 FROM public.sensors AS s
    WHERE s.facility_id = f.facility_id AND s.sensor_type = 'SAFETY'
);

COMMIT;
