-- Incremental migration for waste-bin telemetry.
-- Safe to run against the existing database; it preserves existing rows.
ALTER TABLE public.waste_readings
    ADD COLUMN IF NOT EXISTS fill_level_percent NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS fill_rate_percent_per_hour NUMERIC(8,3);

ALTER TABLE raw.raw_sensor_data
    ADD COLUMN IF NOT EXISTS fill_level_percent NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS fill_rate_percent_per_hour NUMERIC(8,3);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_waste_fill_level'
          AND conrelid = 'public.waste_readings'::regclass
    ) THEN
        ALTER TABLE public.waste_readings
            ADD CONSTRAINT ck_waste_fill_level
            CHECK (
                fill_level_percent IS NULL
                OR (fill_level_percent >= 0 AND fill_level_percent <= 100)
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_waste_fill_rate'
          AND conrelid = 'public.waste_readings'::regclass
    ) THEN
        ALTER TABLE public.waste_readings
            ADD CONSTRAINT ck_waste_fill_rate
            CHECK (
                fill_rate_percent_per_hour IS NULL
                OR fill_rate_percent_per_hour >= 0
            );
    END IF;
END $$;

-- Existing historical rows remain intact. The simulator supplies telemetry for
-- new readings. Do not invent historical measurements unless explicitly labelled
-- as estimated in a separate backfill process.
