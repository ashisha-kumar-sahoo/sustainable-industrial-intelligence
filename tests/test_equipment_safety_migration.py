"""Static contract checks for the additive equipment/safety migration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_migration_is_additive_and_has_complete_raw_payload_storage():
    migration = (ROOT / "database/migrations/002_add_equipment_safety_telemetry.sql").read_text()

    assert "BEGIN;" in migration
    assert "COMMIT;" in migration
    assert "DROP TABLE" not in migration.upper()
    assert "DROP DATABASE" not in migration.upper()
    assert "ADD COLUMN IF NOT EXISTS raw_payload jsonb" in migration
    assert "public.equipment_readings" in migration
    assert "public.safety_readings" in migration
    assert "ON DELETE CASCADE" in migration
    assert "INSERT INTO public.sensors" in migration


def test_schema_and_loader_include_the_new_domain_fields():
    schema = (ROOT / "database/schema.sql").read_text()
    loader = (ROOT / "ingestion/load_to_postgres.py").read_text()
    dashboard = (ROOT / "dashboard/services/database_service.py").read_text()

    for table in ("public.equipment_readings", "public.safety_readings"):
        assert table in schema
        assert table in loader
        assert table in dashboard

    for field in (
        "vibration_mms", "operating_hours", "utilization_percent",
        "gas_leak_ppm", "smoke_detected", "fire_alarm", "raw_payload",
        "synthetic_context",
    ):
        assert field in schema
        assert field in loader
