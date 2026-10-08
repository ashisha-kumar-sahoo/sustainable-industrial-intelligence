--
-- PostgreSQL database dump
--

\restrict wdwhN170bODBQNB9KOsRZnm4T4bt2ECYP0OVQYgnU4dV7eim41OthBmFwLc2mmj

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: etl; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA etl;


ALTER SCHEMA etl OWNER TO postgres;

--
-- Name: SCHEMA etl; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA etl IS 'ETL audit trail: rejected rows and data quality ledger.';


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'Clean application-facing data, views and summaries read by the dashboard.';


--
-- Name: raw; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA raw;


ALTER SCHEMA raw OWNER TO postgres;

--
-- Name: SCHEMA raw; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA raw IS 'Uncleaned sensor payloads exactly as received. Landing zone only.';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cleaned_sensor_data; Type: TABLE; Schema: etl; Owner: postgres
--

CREATE TABLE etl.cleaned_sensor_data (
    cleaned_id bigint NOT NULL,
    raw_id bigint NOT NULL,
    sensor_id integer,
    facility_id integer,
    sensor_type character varying(20),
    reading_ts timestamp with time zone NOT NULL,
    data_quality_status character varying(12) NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    energy_consumption_kwh numeric(12,3),
    voltage numeric(8,2),
    current numeric(10,3),
    power_factor numeric(4,3),
    peak_demand_kw numeric(12,3),
    water_consumption_liters numeric(12,2),
    water_pressure numeric(8,2),
    water_temperature numeric(6,2),
    flow_rate numeric(10,3),
    waste_type character varying(20),
    waste_quantity_kg numeric(12,2),
    recyclable_quantity_kg numeric(12,2),
    hazardous_quantity_kg numeric(12,2),
    aqi integer,
    pm25 numeric(8,2),
    pm10 numeric(8,2),
    co numeric(8,3),
    co2 numeric(10,2),
    no2 numeric(8,3),
    so2 numeric(8,3),
    temperature numeric(6,2),
    humidity numeric(6,2),
    vehicle_count integer,
    heavy_vehicle_count integer,
    average_speed_kmph numeric(6,2),
    congestion_level character varying(10),
    temperature_c numeric(6,2),
    humidity_percent numeric(6,2),
    rainfall_mm numeric(8,2),
    wind_speed_kmph numeric(6,2),
    processed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE etl.cleaned_sensor_data OWNER TO postgres;

--
-- Name: TABLE cleaned_sensor_data; Type: COMMENT; Schema: etl; Owner: postgres
--

COMMENT ON TABLE etl.cleaned_sensor_data IS 'Staging table: every raw row that passed validation, classified and repaired.';


--
-- Name: cleaned_sensor_data_cleaned_id_seq; Type: SEQUENCE; Schema: etl; Owner: postgres
--

ALTER TABLE etl.cleaned_sensor_data ALTER COLUMN cleaned_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME etl.cleaned_sensor_data_cleaned_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: data_quality_log; Type: TABLE; Schema: etl; Owner: postgres
--

CREATE TABLE etl.data_quality_log (
    log_id bigint NOT NULL,
    run_id character varying(40) DEFAULT 'etl-run-1'::character varying NOT NULL,
    sensor_type character varying(20),
    rule_name character varying(60) NOT NULL,
    severity character varying(10) NOT NULL,
    rows_affected integer DEFAULT 0 NOT NULL,
    action_taken character varying(80) NOT NULL,
    logged_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE etl.data_quality_log OWNER TO postgres;

--
-- Name: TABLE data_quality_log; Type: COMMENT; Schema: etl; Owner: postgres
--

COMMENT ON TABLE etl.data_quality_log IS 'One line per validation rule, with how many rows it caught on this run.';


--
-- Name: data_quality_log_log_id_seq; Type: SEQUENCE; Schema: etl; Owner: postgres
--

ALTER TABLE etl.data_quality_log ALTER COLUMN log_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME etl.data_quality_log_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rejected_readings; Type: TABLE; Schema: etl; Owner: postgres
--

CREATE TABLE etl.rejected_readings (
    rejected_id bigint NOT NULL,
    raw_id bigint NOT NULL,
    sensor_id integer,
    facility_id integer,
    sensor_type character varying(20),
    reading_ts timestamp with time zone,
    rejection_reason character varying(30) NOT NULL,
    detail text,
    original_row jsonb,
    rejected_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_rejection_reason CHECK (((rejection_reason)::text = ANY ((ARRAY['MISSING_TIMESTAMP'::character varying, 'DUPLICATE_RECORD'::character varying, 'NULL_CORE_MEASUREMENT'::character varying, 'IMPOSSIBLE_VALUE'::character varying, 'UNKNOWN_SENSOR'::character varying])::text[])))
);


ALTER TABLE etl.rejected_readings OWNER TO postgres;

--
-- Name: TABLE rejected_readings; Type: COMMENT; Schema: etl; Owner: postgres
--

COMMENT ON TABLE etl.rejected_readings IS 'Quarantine. Rows so broken they must not reach the clean tables. Original payload kept as JSONB.';


--
-- Name: rejected_readings_rejected_id_seq; Type: SEQUENCE; Schema: etl; Owner: postgres
--

ALTER TABLE etl.rejected_readings ALTER COLUMN rejected_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME etl.rejected_readings_rejected_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: air_quality_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.air_quality_readings (
    reading_id bigint NOT NULL,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    aqi integer,
    pm25 numeric(8,2),
    pm10 numeric(8,2),
    co numeric(8,3),
    co2 numeric(10,2),
    no2 numeric(8,3),
    so2 numeric(8,3),
    temperature numeric(6,2),
    humidity numeric(6,2),
    aqi_category character varying(30) GENERATED ALWAYS AS (
CASE
    WHEN (aqi IS NULL) THEN NULL::text
    WHEN (aqi <= 50) THEN 'Good'::text
    WHEN (aqi <= 100) THEN 'Moderate'::text
    WHEN (aqi <= 150) THEN 'Unhealthy for Sensitive Groups'::text
    WHEN (aqi <= 200) THEN 'Unhealthy'::text
    WHEN (aqi <= 300) THEN 'Very Unhealthy'::text
    ELSE 'Hazardous'::text
END) STORED,
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_aqi_humidity_range CHECK (((humidity IS NULL) OR ((humidity >= (0)::numeric) AND (humidity <= (100)::numeric)))),
    CONSTRAINT ck_aqi_pm_ordering CHECK (((pm25 IS NULL) OR (pm10 IS NULL) OR (pm10 >= pm25))),
    CONSTRAINT ck_aqi_pollutants_not_negative CHECK (((COALESCE(pm25, (0)::numeric) >= (0)::numeric) AND (COALESCE(pm10, (0)::numeric) >= (0)::numeric) AND (COALESCE(co, (0)::numeric) >= (0)::numeric) AND (COALESCE(co2, (0)::numeric) >= (0)::numeric) AND (COALESCE(no2, (0)::numeric) >= (0)::numeric) AND (COALESCE(so2, (0)::numeric) >= (0)::numeric))),
    CONSTRAINT ck_aqi_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_aqi_range CHECK (((aqi IS NULL) OR ((aqi >= 0) AND (aqi <= 500)))),
    CONSTRAINT ck_aqi_temp_range CHECK (((temperature IS NULL) OR ((temperature >= ('-50'::integer)::numeric) AND (temperature <= (60)::numeric))))
);


ALTER TABLE public.air_quality_readings OWNER TO postgres;

--
-- Name: TABLE air_quality_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.air_quality_readings IS 'Hourly air quality pollutant concentrations per sensor.';


--
-- Name: COLUMN air_quality_readings.aqi_category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.air_quality_readings.aqi_category IS 'Auto-generated EPA label derived from aqi. Never edit by hand.';


--
-- Name: air_quality_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.air_quality_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.air_quality_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alerts (
    alert_id bigint NOT NULL,
    facility_id integer NOT NULL,
    sensor_id integer,
    alert_type character varying(20) NOT NULL,
    severity character varying(10) NOT NULL,
    message text NOT NULL,
    value numeric(14,3),
    threshold numeric(14,3),
    reading_ts timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    status character varying(15) DEFAULT 'ACTIVE'::character varying NOT NULL,
    acknowledged_by character varying(100),
    acknowledged_at timestamp with time zone,
    resolved_at timestamp with time zone,
    CONSTRAINT ck_alerts_severity CHECK (((severity)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[]))),
    CONSTRAINT ck_alerts_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ACKNOWLEDGED'::character varying, 'RESOLVED'::character varying])::text[]))),
    CONSTRAINT ck_alerts_type CHECK (((alert_type)::text = ANY ((ARRAY['HIGH_ENERGY'::character varying, 'HIGH_WATER'::character varying, 'HIGH_AQI'::character varying, 'HIGH_WASTE'::character varying, 'HIGH_TRAFFIC'::character varying, 'SENSOR_FAILURE'::character varying, 'ANOMALY'::character varying])::text[])))
);


ALTER TABLE public.alerts OWNER TO postgres;

--
-- Name: TABLE alerts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.alerts IS 'Threshold and anomaly alerts raised for the estate. Populated by 13_generate_alerts.sql.';


--
-- Name: alerts_alert_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.alerts ALTER COLUMN alert_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.alerts_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: daily_facility_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_facility_summary (
    summary_id bigint NOT NULL,
    facility_id integer NOT NULL,
    summary_date date NOT NULL,
    total_energy_kwh numeric(14,2) DEFAULT 0 NOT NULL,
    total_water_liters numeric(14,2) DEFAULT 0 NOT NULL,
    total_waste_kg numeric(14,2) DEFAULT 0 NOT NULL,
    total_recyclable_kg numeric(14,2) DEFAULT 0 NOT NULL,
    total_hazardous_kg numeric(14,2) DEFAULT 0 NOT NULL,
    average_aqi numeric(8,2),
    max_aqi integer,
    total_vehicle_count bigint DEFAULT 0 NOT NULL,
    total_heavy_vehicle_count bigint DEFAULT 0 NOT NULL,
    average_temperature numeric(8,2),
    average_humidity numeric(8,2),
    total_rainfall_mm numeric(10,2) DEFAULT 0 NOT NULL,
    energy_cost_estimate numeric(12,2) DEFAULT 0 NOT NULL,
    alert_count integer DEFAULT 0 NOT NULL,
    readings_flagged integer DEFAULT 0 NOT NULL,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_daily_counts CHECK (((alert_count >= 0) AND (readings_flagged >= 0)))
);


ALTER TABLE public.daily_facility_summary OWNER TO postgres;

--
-- Name: TABLE daily_facility_summary; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.daily_facility_summary IS 'One row per facility per day, rolled up from the hourly reading tables.';


--
-- Name: daily_facility_summary_summary_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.daily_facility_summary ALTER COLUMN summary_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.daily_facility_summary_summary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: energy_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.energy_readings (
    reading_id bigint NOT NULL,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    energy_consumption_kwh numeric(12,3) NOT NULL,
    voltage numeric(8,2),
    current numeric(10,3),
    power_factor numeric(4,3),
    peak_demand_kw numeric(12,3),
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_energy_not_negative CHECK (((energy_consumption_kwh >= (0)::numeric) AND (peak_demand_kw >= (0)::numeric) AND (current >= (0)::numeric))),
    CONSTRAINT ck_energy_power_factor CHECK (((power_factor IS NULL) OR ((power_factor >= (0)::numeric) AND (power_factor <= (1)::numeric)))),
    CONSTRAINT ck_energy_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_energy_voltage_range CHECK (((voltage IS NULL) OR ((voltage >= (0)::numeric) AND (voltage <= (1000)::numeric))))
);


ALTER TABLE public.energy_readings OWNER TO postgres;

--
-- Name: TABLE energy_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.energy_readings IS 'Hourly electricity consumption per sensor.';


--
-- Name: energy_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.energy_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.energy_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: environmental_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.environmental_readings (
    reading_id bigint NOT NULL,
    facility_id integer NOT NULL,
    sensor_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    temperature_c numeric(6,2),
    humidity_percent numeric(6,2),
    rainfall_mm numeric(8,2) DEFAULT 0 NOT NULL,
    wind_speed_kmph numeric(6,2),
    wind_direction character varying(3),
    air_pressure_hpa numeric(7,2),
    solar_irradiance_wm2 numeric(8,2),
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_env_humidity_range CHECK (((humidity_percent IS NULL) OR ((humidity_percent >= (0)::numeric) AND (humidity_percent <= (100)::numeric)))),
    CONSTRAINT ck_env_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_env_rainfall_not_negative CHECK ((rainfall_mm >= (0)::numeric)),
    CONSTRAINT ck_env_temp_range CHECK (((temperature_c IS NULL) OR ((temperature_c >= ('-50'::integer)::numeric) AND (temperature_c <= (65)::numeric)))),
    CONSTRAINT ck_env_wind_range CHECK (((wind_speed_kmph IS NULL) OR ((wind_speed_kmph >= (0)::numeric) AND (wind_speed_kmph <= (300)::numeric))))
);


ALTER TABLE public.environmental_readings OWNER TO postgres;

--
-- Name: TABLE environmental_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.environmental_readings IS 'Hourly ambient weather: temperature, humidity, rainfall and wind.';


--
-- Name: environmental_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.environmental_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.environmental_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: facilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.facilities (
    facility_id integer NOT NULL,
    facility_code character varying(20) NOT NULL,
    facility_name character varying(120) NOT NULL,
    facility_type character varying(50) NOT NULL,
    company_name character varying(120) NOT NULL,
    location character varying(120) NOT NULL,
    area_sqft integer NOT NULL,
    contact_person character varying(100),
    contact_email character varying(120),
    contact_phone character varying(20),
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    energy_threshold_kwh numeric(12,2) DEFAULT 500 NOT NULL,
    water_threshold_liters numeric(12,2) DEFAULT 800 NOT NULL,
    waste_threshold_kg numeric(12,2) DEFAULT 200 NOT NULL,
    aqi_threshold integer DEFAULT 150 NOT NULL,
    traffic_threshold_count integer DEFAULT 120 NOT NULL,
    sustainability_rating character varying(5) DEFAULT 'B'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_facilities_area CHECK ((area_sqft > 0)),
    CONSTRAINT ck_facilities_email CHECK (((contact_email IS NULL) OR ((contact_email)::text ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'::text))),
    CONSTRAINT ck_facilities_rating CHECK (((sustainability_rating)::text = ANY ((ARRAY['A'::character varying, 'B'::character varying, 'C'::character varying, 'D'::character varying])::text[]))),
    CONSTRAINT ck_facilities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'UNDER_RENOVATION'::character varying, 'INACTIVE'::character varying])::text[]))),
    CONSTRAINT ck_facilities_thresholds CHECK (((energy_threshold_kwh > (0)::numeric) AND (water_threshold_liters > (0)::numeric) AND (waste_threshold_kg > (0)::numeric) AND ((aqi_threshold >= 0) AND (aqi_threshold <= 500)) AND (traffic_threshold_count > 0))),
    CONSTRAINT ck_facilities_type CHECK (((facility_type)::text = ANY ((ARRAY['Manufacturing'::character varying, 'Warehouse'::character varying, 'Chemical Plant'::character varying, 'Food Processing'::character varying, 'Textile'::character varying, 'Automobile'::character varying, 'Electronics'::character varying, 'Packaging'::character varying])::text[]))),
    CONSTRAINT fk_facilities_thresholds_present CHECK (((energy_threshold_kwh > (0)::numeric) AND (water_threshold_liters > (0)::numeric)))
);


ALTER TABLE public.facilities OWNER TO postgres;

--
-- Name: TABLE facilities; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.facilities IS 'Master list of the industrial estate buildings/plants.';


--
-- Name: COLUMN facilities.facility_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.facilities.facility_id IS 'Surrogate key. Joins to every other table.';


--
-- Name: COLUMN facilities.facility_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.facilities.facility_code IS 'Short human-friendly code such as FAC-01.';


--
-- Name: COLUMN facilities.energy_threshold_kwh; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.facilities.energy_threshold_kwh IS 'Daily energy target used to raise HIGH_ENERGY alerts.';


--
-- Name: facilities_facility_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.facilities ALTER COLUMN facility_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.facilities_facility_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: monthly_facility_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monthly_facility_summary (
    summary_id bigint NOT NULL,
    facility_id integer NOT NULL,
    summary_month date NOT NULL,
    total_energy_kwh numeric(16,2) DEFAULT 0 NOT NULL,
    total_water_liters numeric(16,2) DEFAULT 0 NOT NULL,
    total_waste_kg numeric(16,2) DEFAULT 0 NOT NULL,
    total_recyclable_kg numeric(16,2) DEFAULT 0 NOT NULL,
    total_hazardous_kg numeric(16,2) DEFAULT 0 NOT NULL,
    average_aqi numeric(8,2),
    max_aqi integer,
    total_vehicle_count bigint DEFAULT 0 NOT NULL,
    average_temperature numeric(8,2),
    average_humidity numeric(8,2),
    energy_cost_estimate numeric(14,2) DEFAULT 0 NOT NULL,
    alert_count integer DEFAULT 0 NOT NULL,
    days_with_data integer DEFAULT 0 NOT NULL,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_monthly_counts CHECK (((alert_count >= 0) AND (days_with_data >= 0)))
);


ALTER TABLE public.monthly_facility_summary OWNER TO postgres;

--
-- Name: TABLE monthly_facility_summary; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.monthly_facility_summary IS 'One row per facility per calendar month. summary_month is stored as YYYY-MM-01.';


--
-- Name: monthly_facility_summary_summary_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.monthly_facility_summary ALTER COLUMN summary_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.monthly_facility_summary_summary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sensors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensors (
    sensor_id integer NOT NULL,
    sensor_code character varying(30) NOT NULL,
    facility_id integer NOT NULL,
    sensor_type character varying(20) NOT NULL,
    sensor_name character varying(120) NOT NULL,
    unit character varying(20),
    manufacturer character varying(60),
    model character varying(40),
    installation_date date NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    calibration_due_date date,
    last_reading_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_sensors_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying, 'FAULTY'::character varying, 'MAINTENANCE'::character varying, 'DECOMMISSIONED'::character varying])::text[]))),
    CONSTRAINT ck_sensors_type CHECK (((sensor_type)::text = ANY ((ARRAY['ENERGY'::character varying, 'WATER'::character varying, 'WASTE'::character varying, 'AQI'::character varying, 'TEMPERATURE'::character varying, 'HUMIDITY'::character varying, 'TRAFFIC'::character varying])::text[])))
);


ALTER TABLE public.sensors OWNER TO postgres;

--
-- Name: TABLE sensors; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sensors IS 'Every IoT sensor installed in the estate, one row per physical device.';


--
-- Name: sensors_sensor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sensors ALTER COLUMN sensor_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sensors_sensor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: traffic_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.traffic_readings (
    reading_id bigint NOT NULL,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    vehicle_count integer NOT NULL,
    heavy_vehicle_count integer DEFAULT 0 NOT NULL,
    average_speed_kmph numeric(6,2),
    congestion_level character varying(10) NOT NULL,
    lane_occupancy_percent numeric(5,2),
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_traffic_congestion CHECK (((congestion_level)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'SEVERE'::character varying])::text[]))),
    CONSTRAINT ck_traffic_heavy_subset CHECK ((heavy_vehicle_count <= vehicle_count)),
    CONSTRAINT ck_traffic_lane_occupancy CHECK (((lane_occupancy_percent IS NULL) OR ((lane_occupancy_percent >= (0)::numeric) AND (lane_occupancy_percent <= (100)::numeric)))),
    CONSTRAINT ck_traffic_not_negative CHECK (((vehicle_count >= 0) AND (heavy_vehicle_count >= 0))),
    CONSTRAINT ck_traffic_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_traffic_speed_range CHECK (((average_speed_kmph IS NULL) OR ((average_speed_kmph >= (0)::numeric) AND (average_speed_kmph <= (200)::numeric))))
);


ALTER TABLE public.traffic_readings OWNER TO postgres;

--
-- Name: TABLE traffic_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.traffic_readings IS 'Hourly vehicle counts, heavy vehicle counts, speed and congestion at estate gates.';


--
-- Name: traffic_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.traffic_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.traffic_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vw_alerts; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_alerts AS
 SELECT a.alert_id,
    a.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    a.sensor_id,
    s.sensor_code,
    s.sensor_type,
    a.alert_type,
    a.severity,
    a.status,
    a.message,
    a.value,
    a.threshold,
    round((((100)::numeric * a.value) / NULLIF(a.threshold, (0)::numeric)), 1) AS pct_of_threshold,
    a.reading_ts,
    a.created_at,
    a.acknowledged_by,
    a.acknowledged_at,
    a.resolved_at
   FROM ((public.alerts a
     JOIN public.facilities f ON ((f.facility_id = a.facility_id)))
     LEFT JOIN public.sensors s ON ((s.sensor_id = a.sensor_id)));


ALTER VIEW public.vw_alerts OWNER TO postgres;

--
-- Name: VIEW vw_alerts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_alerts IS 'Alerts with facility and sensor names, percent-of-threshold and full lifecycle timestamps.';


--
-- Name: vw_active_alerts; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_active_alerts AS
 SELECT alert_id,
    facility_id,
    facility_code,
    facility_name,
    facility_type,
    sensor_id,
    sensor_code,
    sensor_type,
    alert_type,
    severity,
    status,
    message,
    value,
    threshold,
    pct_of_threshold,
    reading_ts,
    created_at,
    acknowledged_by,
    acknowledged_at,
    resolved_at
   FROM public.vw_alerts
  WHERE ((status)::text = 'ACTIVE'::text);


ALTER VIEW public.vw_active_alerts OWNER TO postgres;

--
-- Name: VIEW vw_active_alerts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_active_alerts IS 'Unresolved alerts, most severe first.';


--
-- Name: vw_air_quality_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_air_quality_readings AS
 SELECT a.sensor_id,
    a.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    s.sensor_code,
    s.unit,
    a.reading_ts AS "timestamp",
    a.aqi,
    a.aqi_category,
    a.pm25,
    a.pm10,
    a.co,
    a.co2,
    a.no2,
    a.so2,
    a.temperature,
    a.humidity,
    f.aqi_threshold,
    (a.aqi > f.aqi_threshold) AS exceeds_site_limit,
    a.data_quality_status,
    a.anomaly_flag,
    a.anomaly_reason,
    a.ingested_at
   FROM ((public.air_quality_readings a
     JOIN public.facilities f ON ((f.facility_id = a.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = a.sensor_id)));


ALTER VIEW public.vw_air_quality_readings OWNER TO postgres;

--
-- Name: VIEW vw_air_quality_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_air_quality_readings IS 'Air quality readings with AQI category, site limit and an over-limit boolean.';


--
-- Name: waste_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waste_readings (
    reading_id bigint NOT NULL,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    waste_type character varying(20) NOT NULL,
    waste_quantity_kg numeric(12,2) NOT NULL,
    recyclable_quantity_kg numeric(12,2) DEFAULT 0 NOT NULL,
    hazardous_quantity_kg numeric(12,2) DEFAULT 0 NOT NULL,
    fill_level_percent numeric(5,2),
    fill_rate_percent_per_hour numeric(8,3),
    disposal_method character varying(30) DEFAULT 'LANDFILL'::character varying NOT NULL,
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_waste_disposal CHECK (((disposal_method)::text = ANY ((ARRAY['LANDFILL'::character varying, 'RECYCLING'::character varying, 'INCINERATION'::character varying, 'COMPOSTING'::character varying, 'HAZARDOUS_COLLECTION'::character varying])::text[]))),
    CONSTRAINT ck_waste_not_negative CHECK (((waste_quantity_kg >= (0)::numeric) AND (recyclable_quantity_kg >= (0)::numeric) AND (hazardous_quantity_kg >= (0)::numeric))),
    CONSTRAINT ck_waste_parts_within_total CHECK (((hazardous_quantity_kg <= waste_quantity_kg) AND (recyclable_quantity_kg <= waste_quantity_kg))),
    CONSTRAINT ck_waste_fill_level CHECK ((fill_level_percent IS NULL OR ((fill_level_percent >= (0)::numeric) AND (fill_level_percent <= (100)::numeric)))),
    CONSTRAINT ck_waste_fill_rate CHECK ((fill_rate_percent_per_hour IS NULL OR (fill_rate_percent_per_hour >= (0)::numeric))),
    CONSTRAINT ck_waste_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_waste_type CHECK (((waste_type)::text = ANY ((ARRAY['Plastic'::character varying, 'Metal'::character varying, 'Organic'::character varying, 'Chemical'::character varying, 'Paper'::character varying, 'General'::character varying])::text[])))
);


ALTER TABLE public.waste_readings OWNER TO postgres;

--
-- Name: TABLE waste_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.waste_readings IS 'Hourly solid waste generation, split into recyclable / hazardous portions.';


--
-- Name: water_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.water_readings (
    reading_id bigint NOT NULL,
    sensor_id integer NOT NULL,
    facility_id integer NOT NULL,
    reading_ts timestamp with time zone NOT NULL,
    water_consumption_liters numeric(12,2) NOT NULL,
    water_pressure numeric(8,2),
    water_temperature numeric(6,2),
    flow_rate numeric(10,3),
    data_quality_status character varying(12) DEFAULT 'OK'::character varying NOT NULL,
    anomaly_flag boolean DEFAULT false NOT NULL,
    anomaly_reason text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_water_not_negative CHECK (((water_consumption_liters >= (0)::numeric) AND (flow_rate >= (0)::numeric))),
    CONSTRAINT ck_water_pressure_range CHECK (((water_pressure IS NULL) OR ((water_pressure >= (0)::numeric) AND (water_pressure <= (20)::numeric)))),
    CONSTRAINT ck_water_quality CHECK (((data_quality_status)::text = ANY ((ARRAY['OK'::character varying, 'FLAGGED'::character varying, 'ESTIMATED'::character varying])::text[]))),
    CONSTRAINT ck_water_temp_range CHECK (((water_temperature IS NULL) OR ((water_temperature >= ('-10'::integer)::numeric) AND (water_temperature <= (120)::numeric))))
);


ALTER TABLE public.water_readings OWNER TO postgres;

--
-- Name: TABLE water_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.water_readings IS 'Hourly water consumption, pressure and flow per sensor.';


--
-- Name: vw_daily_facility_consumption; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_daily_facility_consumption AS
 WITH bounds AS (
         SELECT min(u.d) AS first_day,
            max(u.d) AS last_day
           FROM ( SELECT (energy_readings.reading_ts)::date AS d
                   FROM public.energy_readings
                UNION ALL
                 SELECT (water_readings.reading_ts)::date AS reading_ts
                   FROM public.water_readings
                UNION ALL
                 SELECT (waste_readings.reading_ts)::date AS reading_ts
                   FROM public.waste_readings
                UNION ALL
                 SELECT (air_quality_readings.reading_ts)::date AS reading_ts
                   FROM public.air_quality_readings
                UNION ALL
                 SELECT (traffic_readings.reading_ts)::date AS reading_ts
                   FROM public.traffic_readings) u
        ), days AS (
         SELECT f_1.facility_id,
            (g.g)::date AS summary_date
           FROM ((public.facilities f_1
             CROSS JOIN bounds b)
             CROSS JOIN LATERAL generate_series((b.first_day)::timestamp with time zone, (b.last_day)::timestamp with time zone, '1 day'::interval) g(g))
        ), en AS (
         SELECT energy_readings.facility_id,
            (energy_readings.reading_ts)::date AS d,
            round(sum(energy_readings.energy_consumption_kwh), 2) AS total_energy_kwh,
            round(max(energy_readings.peak_demand_kw), 2) AS peak_demand_kw,
            count(*) AS energy_readings
           FROM public.energy_readings
          GROUP BY energy_readings.facility_id, ((energy_readings.reading_ts)::date)
        ), wa AS (
         SELECT water_readings.facility_id,
            (water_readings.reading_ts)::date AS d,
            round(sum(water_readings.water_consumption_liters), 2) AS total_water_liters,
            round(avg(water_readings.water_pressure), 2) AS avg_water_pressure,
            count(*) AS water_readings
           FROM public.water_readings
          GROUP BY water_readings.facility_id, ((water_readings.reading_ts)::date)
        ), ws AS (
         SELECT waste_readings.facility_id,
            (waste_readings.reading_ts)::date AS d,
            round(sum(waste_readings.waste_quantity_kg), 2) AS total_waste_kg,
            round(sum(waste_readings.recyclable_quantity_kg), 2) AS total_recyclable_kg,
            round(sum(waste_readings.hazardous_quantity_kg), 2) AS total_hazardous_kg,
            count(*) AS waste_readings
           FROM public.waste_readings
          GROUP BY waste_readings.facility_id, ((waste_readings.reading_ts)::date)
        ), aq AS (
         SELECT air_quality_readings.facility_id,
            (air_quality_readings.reading_ts)::date AS d,
            round(avg(air_quality_readings.aqi), 1) AS avg_aqi,
            max(air_quality_readings.aqi) AS max_aqi,
            count(*) FILTER (WHERE (air_quality_readings.aqi > 150)) AS hours_unhealthy,
            count(*) AS aqi_readings
           FROM public.air_quality_readings
          GROUP BY air_quality_readings.facility_id, ((air_quality_readings.reading_ts)::date)
        ), tr AS (
         SELECT traffic_readings.facility_id,
            (traffic_readings.reading_ts)::date AS d,
            sum(traffic_readings.vehicle_count) AS total_vehicles,
            sum(traffic_readings.heavy_vehicle_count) AS total_heavy_vehicles,
            round(avg(traffic_readings.average_speed_kmph), 1) AS avg_speed_kmph,
            count(*) FILTER (WHERE ((traffic_readings.congestion_level)::text = ANY ((ARRAY['HIGH'::character varying, 'SEVERE'::character varying])::text[]))) AS congested_hours
           FROM public.traffic_readings
          GROUP BY traffic_readings.facility_id, ((traffic_readings.reading_ts)::date)
        )
 SELECT f.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    f.sustainability_rating,
    days.summary_date,
    days.summary_date AS summary_date_only,
    en.total_energy_kwh,
    en.peak_demand_kw,
    en.energy_readings,
    wa.total_water_liters,
    wa.avg_water_pressure,
    wa.water_readings,
    ws.total_waste_kg,
    ws.total_recyclable_kg,
    ws.total_hazardous_kg,
    ws.waste_readings,
    aq.avg_aqi,
    aq.max_aqi,
    aq.hours_unhealthy,
    aq.aqi_readings,
    tr.total_vehicles,
    tr.total_heavy_vehicles,
    tr.avg_speed_kmph,
    tr.congested_hours,
    round((((100)::numeric * en.total_energy_kwh) / NULLIF(f.energy_threshold_kwh, (0)::numeric)), 1) AS energy_pct_of_budget,
    round((((100)::numeric * wa.total_water_liters) / NULLIF(f.water_threshold_liters, (0)::numeric)), 1) AS water_pct_of_budget,
    round((((100)::numeric * ws.total_waste_kg) / NULLIF(f.waste_threshold_kg, (0)::numeric)), 1) AS waste_pct_of_budget,
    round((((100)::numeric * ws.total_recyclable_kg) / NULLIF(ws.total_waste_kg, (0)::numeric)), 1) AS recycling_rate_pct,
    GREATEST(COALESCE(round((((100)::numeric * en.total_energy_kwh) / NULLIF(f.energy_threshold_kwh, (0)::numeric)), 1), (0)::numeric), COALESCE(round((((100)::numeric * wa.total_water_liters) / NULLIF(f.water_threshold_liters, (0)::numeric)), 1), (0)::numeric), COALESCE(round((((100)::numeric * ws.total_waste_kg) / NULLIF(f.waste_threshold_kg, (0)::numeric)), 1), (0)::numeric)) AS worst_budget_pct,
    (((COALESCE(en.energy_readings, (0)::bigint) + COALESCE(wa.water_readings, (0)::bigint)) + COALESCE(ws.waste_readings, (0)::bigint)) + COALESCE(aq.aqi_readings, (0)::bigint)) AS total_readings
   FROM ((((((days
     JOIN public.facilities f ON ((f.facility_id = days.facility_id)))
     LEFT JOIN en ON (((en.facility_id = days.facility_id) AND (en.d = days.summary_date))))
     LEFT JOIN wa ON (((wa.facility_id = days.facility_id) AND (wa.d = days.summary_date))))
     LEFT JOIN ws ON (((ws.facility_id = days.facility_id) AND (ws.d = days.summary_date))))
     LEFT JOIN aq ON (((aq.facility_id = days.facility_id) AND (aq.d = days.summary_date))))
     LEFT JOIN tr ON (((tr.facility_id = days.facility_id) AND (tr.d = days.summary_date))));


ALTER VIEW public.vw_daily_facility_consumption OWNER TO postgres;

--
-- Name: VIEW vw_daily_facility_consumption; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_daily_facility_consumption IS 'One row per facility per day: totals for every metric plus budget usage. Facilities with a missing sensor still appear.';


--
-- Name: vw_energy_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_energy_readings AS
 SELECT e.sensor_id,
    e.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    s.sensor_code,
    s.unit,
    e.reading_ts AS "timestamp",
    e.energy_consumption_kwh,
    e.voltage,
    e.current,
    e.power_factor,
    e.peak_demand_kw,
    f.energy_threshold_kwh,
    round((((100)::numeric * e.energy_consumption_kwh) / NULLIF(f.energy_threshold_kwh, (0)::numeric)), 1) AS pct_of_daily_budget,
    e.data_quality_status,
    e.anomaly_flag,
    e.anomaly_reason,
    e.ingested_at
   FROM ((public.energy_readings e
     JOIN public.facilities f ON ((f.facility_id = e.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = e.sensor_id)));


ALTER VIEW public.vw_energy_readings OWNER TO postgres;

--
-- Name: VIEW vw_energy_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_energy_readings IS 'Energy readings with facility context and percentage of the daily kWh budget.';


--
-- Name: vw_environment_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_environment_readings AS
 SELECT e.sensor_id,
    e.facility_id,
    f.facility_code,
    f.facility_name,
    s.sensor_code,
    s.sensor_type,
    s.unit,
    e.reading_ts AS "timestamp",
    e.temperature_c,
    e.humidity_percent,
    e.rainfall_mm,
    e.wind_speed_kmph,
    round((((e.temperature_c * (9)::numeric) / (5)::numeric) + (32)::numeric), 1) AS temperature_f,
    (e.temperature_c < (5)::numeric) AS is_freezing,
    (e.rainfall_mm > (0)::numeric) AS is_raining,
    e.data_quality_status,
    e.anomaly_flag,
    e.anomaly_reason,
    e.ingested_at
   FROM ((public.environmental_readings e
     JOIN public.facilities f ON ((f.facility_id = e.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = e.sensor_id)));


ALTER VIEW public.vw_environment_readings OWNER TO postgres;

--
-- Name: VIEW vw_environment_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_environment_readings IS 'Weather readings with Fahrenheit conversion and simple boolean conditions.';


--
-- Name: vw_facilities; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_facilities AS
SELECT
    NULL::integer AS facility_id,
    NULL::character varying(20) AS facility_code,
    NULL::character varying(120) AS facility_name,
    NULL::character varying(50) AS facility_type,
    NULL::character varying(120) AS company_name,
    NULL::character varying(120) AS location,
    NULL::integer AS area_sqft,
    NULL::character varying(20) AS status,
    NULL::character varying(5) AS sustainability_rating,
    NULL::numeric(12,2) AS energy_threshold_kwh,
    NULL::numeric(12,2) AS water_threshold_liters,
    NULL::numeric(12,2) AS waste_threshold_kg,
    NULL::integer AS aqi_threshold,
    NULL::integer AS traffic_threshold_count,
    NULL::character varying(100) AS contact_person,
    NULL::character varying(120) AS contact_email,
    NULL::character varying(20) AS contact_phone,
    NULL::timestamp with time zone AS created_at,
    NULL::bigint AS sensor_count,
    NULL::bigint AS active_sensor_count,
    NULL::bigint AS unhealthy_sensor_count,
    NULL::bigint AS active_alert_count,
    NULL::bigint AS critical_alert_count,
    NULL::timestamp with time zone AS latest_reading_at;


ALTER VIEW public.vw_facilities OWNER TO postgres;

--
-- Name: VIEW vw_facilities; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_facilities IS 'Facilities with sensor counts, active alert counts and latest reading time.';


--
-- Name: vw_latest_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_latest_readings AS
 WITH all_readings AS (
         SELECT energy_readings.sensor_id,
            energy_readings.reading_ts AS "timestamp",
            'ENERGY'::character varying AS sensor_type,
            jsonb_build_object('energy_kwh', energy_readings.energy_consumption_kwh, 'voltage', energy_readings.voltage, 'current', energy_readings.current, 'power_factor', energy_readings.power_factor, 'peak_demand_kw', energy_readings.peak_demand_kw) AS reading,
            energy_readings.energy_consumption_kwh AS energy_value,
            NULL::numeric AS water_value,
            NULL::numeric AS waste_value,
            NULL::integer AS aqi_value,
            NULL::integer AS traffic_value,
            NULL::numeric AS environmental_value,
            energy_readings.data_quality_status,
            energy_readings.anomaly_flag
           FROM public.energy_readings
        UNION ALL
         SELECT water_readings.sensor_id,
            water_readings.reading_ts,
            'WATER'::character varying,
            jsonb_build_object('water_liters', water_readings.water_consumption_liters, 'pressure_bar', water_readings.water_pressure, 'temperature_c', water_readings.water_temperature, 'flow_rate_lph', water_readings.flow_rate) AS jsonb_build_object,
            NULL::numeric AS "numeric",
            water_readings.water_consumption_liters,
            NULL::numeric AS "numeric",
            NULL::integer AS int4,
            NULL::integer AS int4,
            NULL::numeric AS "numeric",
            water_readings.data_quality_status,
            water_readings.anomaly_flag
           FROM public.water_readings
        UNION ALL
         SELECT waste_readings.sensor_id,
            waste_readings.reading_ts,
            'WASTE'::character varying,
            jsonb_build_object('waste_type', waste_readings.waste_type, 'waste_kg', waste_readings.waste_quantity_kg, 'recyclable_kg', waste_readings.recyclable_quantity_kg, 'hazardous_kg', waste_readings.hazardous_quantity_kg) AS jsonb_build_object,
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            waste_readings.waste_quantity_kg,
            NULL::integer AS int4,
            NULL::integer AS int4,
            NULL::numeric AS "numeric",
            waste_readings.data_quality_status,
            waste_readings.anomaly_flag
           FROM public.waste_readings
        UNION ALL
         SELECT air_quality_readings.sensor_id,
            air_quality_readings.reading_ts,
            'AQI'::character varying,
            jsonb_build_object('aqi', air_quality_readings.aqi, 'category', air_quality_readings.aqi_category, 'pm25_ugm3', air_quality_readings.pm25, 'pm10_ugm3', air_quality_readings.pm10, 'co_ppm', air_quality_readings.co, 'co2_ppm', air_quality_readings.co2, 'no2_ppb', air_quality_readings.no2, 'so2_ppb', air_quality_readings.so2, 'temp_c', air_quality_readings.temperature, 'humidity_pct', air_quality_readings.humidity) AS jsonb_build_object,
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            air_quality_readings.aqi,
            NULL::integer AS int4,
            NULL::numeric AS "numeric",
            air_quality_readings.data_quality_status,
            air_quality_readings.anomaly_flag
           FROM public.air_quality_readings
        UNION ALL
         SELECT traffic_readings.sensor_id,
            traffic_readings.reading_ts,
            'TRAFFIC'::character varying,
            jsonb_build_object('vehicle_count', traffic_readings.vehicle_count, 'heavy_vehicle_count', traffic_readings.heavy_vehicle_count, 'avg_speed_kmph', traffic_readings.average_speed_kmph, 'congestion', traffic_readings.congestion_level) AS jsonb_build_object,
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            NULL::integer AS int4,
            traffic_readings.vehicle_count,
            NULL::numeric AS "numeric",
            traffic_readings.data_quality_status,
            traffic_readings.anomaly_flag
           FROM public.traffic_readings
        UNION ALL
         SELECT e.sensor_id,
            e.reading_ts,
                CASE s_1.sensor_type
                    WHEN 'HUMIDITY'::text THEN 'HUMIDITY'::text
                    ELSE 'TEMPERATURE'::text
                END AS "case",
            jsonb_build_object('temperature_c', e.temperature_c, 'humidity_pct', e.humidity_percent, 'rainfall_mm', e.rainfall_mm, 'wind_kmph', e.wind_speed_kmph) AS jsonb_build_object,
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            NULL::numeric AS "numeric",
            NULL::integer AS int4,
            NULL::integer AS int4,
            e.temperature_c,
            e.data_quality_status,
            e.anomaly_flag
           FROM (public.environmental_readings e
             JOIN public.sensors s_1 ON ((s_1.sensor_id = e.sensor_id)))
        ), ranked AS (
         SELECT DISTINCT ON (a.sensor_id) a.sensor_id,
            a."timestamp",
            a.sensor_type,
            a.reading,
            a.energy_value,
            a.water_value,
            a.waste_value,
            a.aqi_value,
            a.traffic_value,
            a.environmental_value,
            a.data_quality_status,
            a.anomaly_flag
           FROM all_readings a
          ORDER BY a.sensor_id, a."timestamp" DESC
        )
 SELECT s.sensor_id,
    s.sensor_code,
    s.sensor_type,
    s.unit,
    s.status AS sensor_status,
    s.facility_id,
    f.facility_code,
    f.facility_name,
    r."timestamp",
    r.reading,
    r.energy_value AS energy_consumption_kwh,
    r.water_value AS water_consumption_liters,
    r.waste_value AS waste_quantity_kg,
    r.aqi_value AS aqi,
    r.traffic_value AS vehicle_count,
    r.environmental_value AS temperature_c,
    r.data_quality_status,
    r.anomaly_flag
   FROM ((public.sensors s
     JOIN public.facilities f ON ((f.facility_id = s.facility_id)))
     LEFT JOIN ranked r ON ((r.sensor_id = s.sensor_id)));


ALTER VIEW public.vw_latest_readings OWNER TO postgres;

--
-- Name: VIEW vw_latest_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_latest_readings IS 'One row per sensor: its most recent reading, with the measurement as JSONB and also as typed columns. Sensors that have never reported appear with NULLs.';


--
-- Name: vw_sensor_health; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sensor_health AS
 SELECT s.sensor_id,
    s.sensor_code,
    s.sensor_type,
    s.sensor_name,
    s.status,
    s.facility_id,
    f.facility_code,
    f.facility_name,
    s.last_reading_at,
    s.installation_date,
    s.calibration_due_date,
    ((s.calibration_due_date IS NOT NULL) AND (s.calibration_due_date < CURRENT_DATE)) AS calibration_overdue,
    ( SELECT count(*) AS count
           FROM public.alerts a
          WHERE ((a.sensor_id = s.sensor_id) AND ((a.alert_type)::text = 'SENSOR_FAILURE'::text) AND ((a.status)::text = 'ACTIVE'::text))) AS active_sensor_fault_alerts
   FROM (public.sensors s
     JOIN public.facilities f ON ((f.facility_id = s.facility_id)));


ALTER VIEW public.vw_sensor_health OWNER TO postgres;

--
-- Name: VIEW vw_sensor_health; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_sensor_health IS 'Sensor registry with overdue calibration and open hardware fault alerts.';


--
-- Name: vw_sensors; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sensors AS
 SELECT s.sensor_id,
    s.sensor_code,
    s.sensor_type,
    s.sensor_name,
    s.unit,
    s.manufacturer,
    s.model,
    s.status,
    s.installation_date,
    s.calibration_due_date,
    s.last_reading_at,
    s.created_at,
    s.facility_id,
    f.facility_code,
    f.facility_name,
    ((s.calibration_due_date IS NOT NULL) AND (s.calibration_due_date < CURRENT_DATE)) AS calibration_overdue,
        CASE
            WHEN ((s.status)::text <> 'ACTIVE'::text) THEN true
            WHEN (s.last_reading_at IS NULL) THEN true
            ELSE false
        END AS needs_attention
   FROM (public.sensors s
     JOIN public.facilities f ON ((f.facility_id = s.facility_id)));


ALTER VIEW public.vw_sensors OWNER TO postgres;

--
-- Name: VIEW vw_sensors; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_sensors IS 'Sensor registry joined to its facility, with overdue-calculation and attention flags.';


--
-- Name: vw_traffic_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_traffic_readings AS
 SELECT t.sensor_id,
    t.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    s.sensor_code,
    s.unit,
    t.reading_ts AS "timestamp",
    t.vehicle_count,
    t.heavy_vehicle_count,
    t.average_speed_kmph,
    t.congestion_level,
    round((((100 * t.heavy_vehicle_count) / NULLIF(t.vehicle_count, 0)))::numeric, 1) AS heavy_vehicle_pct,
    f.traffic_threshold_count,
    (t.vehicle_count > f.traffic_threshold_count) AS exceeds_site_limit,
    t.data_quality_status,
    t.anomaly_flag,
    t.anomaly_reason,
    t.ingested_at
   FROM ((public.traffic_readings t
     JOIN public.facilities f ON ((f.facility_id = t.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = t.sensor_id)));


ALTER VIEW public.vw_traffic_readings OWNER TO postgres;

--
-- Name: VIEW vw_traffic_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_traffic_readings IS 'Traffic readings with heavy-vehicle share and an over-limit boolean.';


--
-- Name: vw_waste_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_waste_readings AS
 SELECT x.sensor_id,
    x.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    s.sensor_code,
    s.unit,
    x.reading_ts AS "timestamp",
    x.waste_type,
    x.waste_quantity_kg,
    x.recyclable_quantity_kg,
    x.hazardous_quantity_kg,
    round((((100)::numeric * x.recyclable_quantity_kg) / NULLIF(x.waste_quantity_kg, (0)::numeric)), 1) AS recycling_rate_pct,
    f.waste_threshold_kg,
    round((((100)::numeric * x.waste_quantity_kg) / NULLIF(f.waste_threshold_kg, (0)::numeric)), 1) AS pct_of_daily_budget,
    x.data_quality_status,
    x.anomaly_flag,
    x.anomaly_reason,
    x.ingested_at
   FROM ((public.waste_readings x
     JOIN public.facilities f ON ((f.facility_id = x.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = x.sensor_id)));


ALTER VIEW public.vw_waste_readings OWNER TO postgres;

--
-- Name: VIEW vw_waste_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_waste_readings IS 'Waste readings with facility context, recycling rate and percentage of the daily kg limit.';


--
-- Name: vw_water_readings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_water_readings AS
 SELECT w.sensor_id,
    w.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    s.sensor_code,
    s.unit,
    w.reading_ts AS "timestamp",
    w.water_consumption_liters,
    w.water_pressure,
    w.water_temperature,
    w.flow_rate,
    f.water_threshold_liters,
    round((((100)::numeric * w.water_consumption_liters) / NULLIF(f.water_threshold_liters, (0)::numeric)), 1) AS pct_of_daily_budget,
    w.data_quality_status,
    w.anomaly_flag,
    w.anomaly_reason,
    w.ingested_at
   FROM ((public.water_readings w
     JOIN public.facilities f ON ((f.facility_id = w.facility_id)))
     JOIN public.sensors s ON ((s.sensor_id = w.sensor_id)));


ALTER VIEW public.vw_water_readings OWNER TO postgres;

--
-- Name: VIEW vw_water_readings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_water_readings IS 'Water readings with facility context and percentage of the daily litres budget.';


--
-- Name: waste_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.waste_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.waste_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: water_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.water_readings ALTER COLUMN reading_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.water_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: raw_sensor_data; Type: TABLE; Schema: raw; Owner: postgres
--

CREATE TABLE raw.raw_sensor_data (
    raw_id bigint NOT NULL,
    sensor_id integer,
    facility_id integer,
    sensor_type character varying(20),
    received_at timestamp with time zone DEFAULT now() NOT NULL,
    reading_ts timestamp with time zone,
    energy_consumption_kwh numeric(16,3),
    voltage numeric(12,2),
    current numeric(14,3),
    power_factor numeric(8,3),
    peak_demand_kw numeric(16,3),
    water_consumption_liters numeric(16,2),
    water_pressure numeric(10,2),
    water_temperature numeric(8,2),
    flow_rate numeric(14,3),
    waste_type character varying(30),
    waste_quantity_kg numeric(16,2),
    recyclable_quantity_kg numeric(16,2),
    hazardous_quantity_kg numeric(16,2),
    fill_level_percent numeric(5,2),
    fill_rate_percent_per_hour numeric(8,3),
    aqi integer,
    pm25 numeric(12,2),
    pm10 numeric(12,2),
    co numeric(10,3),
    co2 numeric(12,2),
    no2 numeric(10,3),
    so2 numeric(10,3),
    temperature numeric(8,2),
    humidity numeric(8,2),
    vehicle_count integer,
    heavy_vehicle_count integer,
    average_speed_kmph numeric(8,2),
    congestion_level character varying(20),
    temperature_c numeric(8,2),
    humidity_percent numeric(8,2),
    rainfall_mm numeric(10,2),
    wind_speed_kmph numeric(8,2)
);


ALTER TABLE raw.raw_sensor_data OWNER TO postgres;

--
-- Name: TABLE raw_sensor_data; Type: COMMENT; Schema: raw; Owner: postgres
--

COMMENT ON TABLE raw.raw_sensor_data IS 'UNTRUSTED landing zone. Sensor payloads exactly as received, with no validation at all.';


--
-- Name: raw_sensor_data_raw_id_seq; Type: SEQUENCE; Schema: raw; Owner: postgres
--

ALTER TABLE raw.raw_sensor_data ALTER COLUMN raw_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME raw.raw_sensor_data_raw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: cleaned_sensor_data cleaned_sensor_data_pkey; Type: CONSTRAINT; Schema: etl; Owner: postgres
--

ALTER TABLE ONLY etl.cleaned_sensor_data
    ADD CONSTRAINT cleaned_sensor_data_pkey PRIMARY KEY (cleaned_id);


--
-- Name: data_quality_log data_quality_log_pkey; Type: CONSTRAINT; Schema: etl; Owner: postgres
--

ALTER TABLE ONLY etl.data_quality_log
    ADD CONSTRAINT data_quality_log_pkey PRIMARY KEY (log_id);


--
-- Name: rejected_readings rejected_readings_pkey; Type: CONSTRAINT; Schema: etl; Owner: postgres
--

ALTER TABLE ONLY etl.rejected_readings
    ADD CONSTRAINT rejected_readings_pkey PRIMARY KEY (rejected_id);


--
-- Name: air_quality_readings air_quality_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.air_quality_readings
    ADD CONSTRAINT air_quality_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (alert_id);


--
-- Name: daily_facility_summary daily_facility_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_facility_summary
    ADD CONSTRAINT daily_facility_summary_pkey PRIMARY KEY (summary_id);


--
-- Name: energy_readings energy_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_readings
    ADD CONSTRAINT energy_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: environmental_readings environmental_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environmental_readings
    ADD CONSTRAINT environmental_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: facilities facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (facility_id);


--
-- Name: monthly_facility_summary monthly_facility_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_facility_summary
    ADD CONSTRAINT monthly_facility_summary_pkey PRIMARY KEY (summary_id);


--
-- Name: sensors sensors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_pkey PRIMARY KEY (sensor_id);


--
-- Name: traffic_readings traffic_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traffic_readings
    ADD CONSTRAINT traffic_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: alerts uq_alerts_dedupe; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT uq_alerts_dedupe UNIQUE NULLS NOT DISTINCT (facility_id, sensor_id, alert_type, reading_ts);


--
-- Name: air_quality_readings uq_aqi_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.air_quality_readings
    ADD CONSTRAINT uq_aqi_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: daily_facility_summary uq_daily_facility_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_facility_summary
    ADD CONSTRAINT uq_daily_facility_date UNIQUE (facility_id, summary_date);


--
-- Name: energy_readings uq_energy_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_readings
    ADD CONSTRAINT uq_energy_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: environmental_readings uq_env_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environmental_readings
    ADD CONSTRAINT uq_env_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: monthly_facility_summary uq_monthly_facility_month; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_facility_summary
    ADD CONSTRAINT uq_monthly_facility_month UNIQUE (facility_id, summary_month);


--
-- Name: traffic_readings uq_traffic_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traffic_readings
    ADD CONSTRAINT uq_traffic_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: waste_readings uq_waste_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_readings
    ADD CONSTRAINT uq_waste_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: water_readings uq_water_sensor_ts; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT uq_water_sensor_ts UNIQUE (sensor_id, reading_ts);


--
-- Name: waste_readings waste_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_readings
    ADD CONSTRAINT waste_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: water_readings water_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT water_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: raw_sensor_data raw_sensor_data_pkey; Type: CONSTRAINT; Schema: raw; Owner: postgres
--

ALTER TABLE ONLY raw.raw_sensor_data
    ADD CONSTRAINT raw_sensor_data_pkey PRIMARY KEY (raw_id);


--
-- Name: idx_alerts_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerts_active ON public.alerts USING btree (facility_id, created_at DESC) WHERE ((status)::text = 'ACTIVE'::text);


--
-- Name: idx_alerts_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerts_created_at ON public.alerts USING btree (created_at DESC);


--
-- Name: idx_alerts_facility; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerts_facility ON public.alerts USING btree (facility_id);


--
-- Name: idx_alerts_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerts_status ON public.alerts USING btree (status);


--
-- Name: idx_alerts_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alerts_type ON public.alerts USING btree (alert_type);


--
-- Name: idx_aqi_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aqi_facility_ts ON public.air_quality_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_aqi_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aqi_ts ON public.air_quality_readings USING btree (reading_ts);


--
-- Name: idx_aqi_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aqi_ts_desc ON public.air_quality_readings USING btree (reading_ts DESC);


--
-- Name: idx_aqi_value; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aqi_value ON public.air_quality_readings USING btree (aqi DESC);


--
-- Name: idx_daily_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_date ON public.daily_facility_summary USING btree (summary_date DESC);


--
-- Name: idx_daily_date_facility; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_date_facility ON public.daily_facility_summary USING btree (summary_date DESC, facility_id);


--
-- Name: idx_daily_facility; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_facility ON public.daily_facility_summary USING btree (facility_id, summary_date DESC);


--
-- Name: idx_energy_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_energy_facility_ts ON public.energy_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_energy_quality; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_energy_quality ON public.energy_readings USING btree (data_quality_status) WHERE ((data_quality_status)::text <> 'OK'::text);


--
-- Name: idx_energy_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_energy_ts ON public.energy_readings USING btree (reading_ts);


--
-- Name: idx_energy_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_energy_ts_desc ON public.energy_readings USING btree (reading_ts DESC);


--
-- Name: idx_env_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_env_facility_ts ON public.environmental_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_env_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_env_ts ON public.environmental_readings USING btree (reading_ts);


--
-- Name: idx_env_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_env_ts_desc ON public.environmental_readings USING btree (reading_ts DESC);


--
-- Name: idx_facilities_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_facilities_status ON public.facilities USING btree (status);


--
-- Name: idx_facilities_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_facilities_type ON public.facilities USING btree (facility_type);


--
-- Name: idx_monthly_fac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_monthly_fac ON public.monthly_facility_summary USING btree (facility_id, summary_month DESC);


--
-- Name: idx_monthly_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_monthly_month ON public.monthly_facility_summary USING btree (summary_month DESC);


--
-- Name: idx_monthly_month_facility; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_monthly_month_facility ON public.monthly_facility_summary USING btree (summary_month DESC, facility_id);


--
-- Name: idx_sensors_facility; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sensors_facility ON public.sensors USING btree (facility_id);


--
-- Name: idx_sensors_facility_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sensors_facility_type ON public.sensors USING btree (facility_id, sensor_type);


--
-- Name: idx_sensors_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sensors_status ON public.sensors USING btree (status);


--
-- Name: idx_sensors_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sensors_type ON public.sensors USING btree (sensor_type);


--
-- Name: idx_traffic_congestion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_traffic_congestion ON public.traffic_readings USING btree (congestion_level);


--
-- Name: idx_traffic_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_traffic_facility_ts ON public.traffic_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_traffic_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_traffic_ts ON public.traffic_readings USING btree (reading_ts);


--
-- Name: idx_traffic_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_traffic_ts_desc ON public.traffic_readings USING btree (reading_ts DESC);


--
-- Name: idx_waste_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waste_facility_ts ON public.waste_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_waste_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waste_ts ON public.waste_readings USING btree (reading_ts);


--
-- Name: idx_waste_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waste_ts_desc ON public.waste_readings USING btree (reading_ts DESC);


--
-- Name: idx_waste_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waste_type ON public.waste_readings USING btree (waste_type);


--
-- Name: idx_water_facility_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_water_facility_ts ON public.water_readings USING btree (facility_id, reading_ts);


--
-- Name: idx_water_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_water_ts ON public.water_readings USING btree (reading_ts);


--
-- Name: idx_water_ts_desc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_water_ts_desc ON public.water_readings USING btree (reading_ts DESC);


--
-- Name: vw_facilities _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.vw_facilities AS
 SELECT f.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    f.company_name,
    f.location,
    f.area_sqft,
    f.status,
    f.sustainability_rating,
    f.energy_threshold_kwh,
    f.water_threshold_liters,
    f.waste_threshold_kg,
    f.aqi_threshold,
    f.traffic_threshold_count,
    f.contact_person,
    f.contact_email,
    f.contact_phone,
    f.created_at,
    count(DISTINCT s.sensor_id) AS sensor_count,
    count(DISTINCT s.sensor_id) FILTER (WHERE ((s.status)::text = 'ACTIVE'::text)) AS active_sensor_count,
    count(DISTINCT s.sensor_id) FILTER (WHERE ((s.status)::text <> 'ACTIVE'::text)) AS unhealthy_sensor_count,
    count(DISTINCT a.alert_id) FILTER (WHERE ((a.status)::text = 'ACTIVE'::text)) AS active_alert_count,
    count(DISTINCT a.alert_id) FILTER (WHERE (((a.status)::text = 'ACTIVE'::text) AND ((a.severity)::text = 'CRITICAL'::text))) AS critical_alert_count,
    max(s.last_reading_at) AS latest_reading_at
   FROM ((public.facilities f
     LEFT JOIN public.sensors s ON ((s.facility_id = f.facility_id)))
     LEFT JOIN public.alerts a ON ((a.facility_id = f.facility_id)))
  GROUP BY f.facility_id;


--
-- Name: alerts fk_alerts_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT fk_alerts_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: alerts fk_alerts_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT fk_alerts_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE SET NULL;


--
-- Name: air_quality_readings fk_aqi_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.air_quality_readings
    ADD CONSTRAINT fk_aqi_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: air_quality_readings fk_aqi_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.air_quality_readings
    ADD CONSTRAINT fk_aqi_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: daily_facility_summary fk_daily_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_facility_summary
    ADD CONSTRAINT fk_daily_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: energy_readings fk_energy_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_readings
    ADD CONSTRAINT fk_energy_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: energy_readings fk_energy_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.energy_readings
    ADD CONSTRAINT fk_energy_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: environmental_readings fk_env_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environmental_readings
    ADD CONSTRAINT fk_env_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: environmental_readings fk_env_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environmental_readings
    ADD CONSTRAINT fk_env_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: monthly_facility_summary fk_monthly_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_facility_summary
    ADD CONSTRAINT fk_monthly_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: sensors fk_sensors_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT fk_sensors_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: traffic_readings fk_traffic_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traffic_readings
    ADD CONSTRAINT fk_traffic_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: traffic_readings fk_traffic_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traffic_readings
    ADD CONSTRAINT fk_traffic_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: waste_readings fk_waste_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_readings
    ADD CONSTRAINT fk_waste_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: waste_readings fk_waste_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_readings
    ADD CONSTRAINT fk_waste_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: water_readings fk_water_facility; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT fk_water_facility FOREIGN KEY (facility_id) REFERENCES public.facilities(facility_id) ON DELETE CASCADE;


--
-- Name: water_readings fk_water_sensor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.water_readings
    ADD CONSTRAINT fk_water_sensor FOREIGN KEY (sensor_id) REFERENCES public.sensors(sensor_id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO smart_estate_app;


--
-- Name: TABLE air_quality_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.air_quality_readings TO smart_estate_app;


--
-- Name: SEQUENCE air_quality_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.air_quality_readings_reading_id_seq TO smart_estate_app;


--
-- Name: TABLE alerts; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.alerts TO smart_estate_app;


--
-- Name: COLUMN alerts.status; Type: ACL; Schema: public; Owner: postgres
--

GRANT UPDATE(status) ON TABLE public.alerts TO smart_estate_app;


--
-- Name: COLUMN alerts.acknowledged_by; Type: ACL; Schema: public; Owner: postgres
--

GRANT UPDATE(acknowledged_by) ON TABLE public.alerts TO smart_estate_app;


--
-- Name: COLUMN alerts.acknowledged_at; Type: ACL; Schema: public; Owner: postgres
--

GRANT UPDATE(acknowledged_at) ON TABLE public.alerts TO smart_estate_app;


--
-- Name: COLUMN alerts.resolved_at; Type: ACL; Schema: public; Owner: postgres
--

GRANT UPDATE(resolved_at) ON TABLE public.alerts TO smart_estate_app;


--
-- Name: SEQUENCE alerts_alert_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.alerts_alert_id_seq TO smart_estate_app;


--
-- Name: TABLE daily_facility_summary; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.daily_facility_summary TO smart_estate_app;


--
-- Name: SEQUENCE daily_facility_summary_summary_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.daily_facility_summary_summary_id_seq TO smart_estate_app;


--
-- Name: TABLE energy_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.energy_readings TO smart_estate_app;


--
-- Name: SEQUENCE energy_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.energy_readings_reading_id_seq TO smart_estate_app;


--
-- Name: TABLE environmental_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.environmental_readings TO smart_estate_app;


--
-- Name: SEQUENCE environmental_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.environmental_readings_reading_id_seq TO smart_estate_app;


--
-- Name: TABLE facilities; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.facilities TO smart_estate_app;


--
-- Name: SEQUENCE facilities_facility_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.facilities_facility_id_seq TO smart_estate_app;


--
-- Name: TABLE monthly_facility_summary; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.monthly_facility_summary TO smart_estate_app;


--
-- Name: SEQUENCE monthly_facility_summary_summary_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.monthly_facility_summary_summary_id_seq TO smart_estate_app;


--
-- Name: TABLE sensors; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.sensors TO smart_estate_app;


--
-- Name: SEQUENCE sensors_sensor_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.sensors_sensor_id_seq TO smart_estate_app;


--
-- Name: TABLE traffic_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.traffic_readings TO smart_estate_app;


--
-- Name: SEQUENCE traffic_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.traffic_readings_reading_id_seq TO smart_estate_app;


--
-- Name: TABLE vw_alerts; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_alerts TO smart_estate_app;


--
-- Name: TABLE vw_active_alerts; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_active_alerts TO smart_estate_app;


--
-- Name: TABLE vw_air_quality_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_air_quality_readings TO smart_estate_app;


--
-- Name: TABLE waste_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.waste_readings TO smart_estate_app;


--
-- Name: TABLE water_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.water_readings TO smart_estate_app;


--
-- Name: TABLE vw_daily_facility_consumption; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_daily_facility_consumption TO smart_estate_app;


--
-- Name: TABLE vw_energy_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_energy_readings TO smart_estate_app;


--
-- Name: TABLE vw_environment_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_environment_readings TO smart_estate_app;


--
-- Name: TABLE vw_facilities; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_facilities TO smart_estate_app;


--
-- Name: TABLE vw_latest_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_latest_readings TO smart_estate_app;


--
-- Name: TABLE vw_sensor_health; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_sensor_health TO smart_estate_app;


--
-- Name: TABLE vw_sensors; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_sensors TO smart_estate_app;


--
-- Name: TABLE vw_traffic_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_traffic_readings TO smart_estate_app;


--
-- Name: TABLE vw_waste_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_waste_readings TO smart_estate_app;


--
-- Name: TABLE vw_water_readings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.vw_water_readings TO smart_estate_app;


--
-- Name: SEQUENCE waste_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.waste_readings_reading_id_seq TO smart_estate_app;


--
-- Name: SEQUENCE water_readings_reading_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.water_readings_reading_id_seq TO smart_estate_app;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO smart_estate_app;


--
-- PostgreSQL database dump complete
--

\unrestrict wdwhN170bODBQNB9KOsRZnm4T4bt2ECYP0OVQYgnU4dV7eim41OthBmFwLc2mmj

