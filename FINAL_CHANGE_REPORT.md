# Final Change Report — Sustainable Industrial Intelligence

## Baseline and handling

Re-audited `sustainable-industrial-intelligence-audited-v3.zip` in an isolated working copy. The archive contents were preserved and additional fixes were applied to the working copy. GitHub, the live local PostgreSQL database, and the user's existing repository were not modified.

## Database and ingestion

- Added `database/migrations/002_add_equipment_safety_telemetry.sql` for equipment/safety telemetry storage.
- Added `public.equipment_readings` and `public.safety_readings`, unique sensor/timestamp keys, foreign keys, range checks, and facility/time indexes.
- Extended `public.sensors.sensor_type` validation to support `EQUIPMENT` and `SAFETY`.
- Added typed equipment/safety columns and `raw_payload` JSONB to `raw.raw_sensor_data`; newly ingested records retain the complete original payload.
- Existing raw history is preserved. Historical rows get the empty-object default for `raw_payload` because the previous schema did not store their original JSON payloads.
- Added missing synthetic sensor registrations per facility without replacing existing sensor IDs.
- Updated the loader to insert all eight sensor-style domains into their raw and public tables, using idempotent `(sensor_id, reading_ts)` keys.
- Added equipment/safety validation and simulator contracts. Equipment identifiers are stable per sensor; synthetic safety context is marked explicitly.
- Added tests for SQL parameter counts and full raw-payload preservation.

## Dashboard and assistant integration

- Added equipment and safety ML adapters and connected them to the dashboard's operational pages.
- Updated dashboard PostgreSQL queries to use the new telemetry tables and expose model input fields.
- Updated assistant retrieval and response logic to use equipment/safety telemetry instead of claiming those tables do not exist.
- Added clear disclosure that simulator-generated incident labels and response times are synthetic.
- Kept existing resource, environment, traffic, and waste functionality in place.

## Model folder decision

- Compared `ai/operations/{environment,equipment,safety,traffic}` with `ml/{environment,equipment,safety,traffic}`.
- They overlap but are not byte-for-byte duplicates; their data contracts and unique functions differ.
- `ml/` is canonical for dashboard runtime. `ai/operations/` is retained as a separate research/legacy implementation because it has distinct analysis functions and regression tests.
- Documented the comparison and ownership in `docs/AI_MODEL_FOLDER_AUDIT.md` rather than deleting code without reconciling its behavior.

## Backend decision

The empty `backend/` directory remains a placeholder. A separate backend service is not required for this prototype's current architecture: Streamlit serves the dashboard, and `ai.assistant.web_app` serves the local assistant endpoint. No extra service was invented without a demonstrated need.

## Latest validation

- `python -m compileall -q .` — PASS.
- `python -m pytest -q` — **59 passed, 8 skipped**.
- Non-dashboard import smoke test — **127 imported, 0 failures**.
- Dashboard import smoke test with lightweight Streamlit/PyDeck stubs — **36 imported, 0 failures**; not a live browser test.
- Loader/schema contract check — all **9 INSERT targets** reference schema/migration columns.
- The PostgreSQL migration has **not** been executed in this isolated environment. Apply it locally only after a verified database backup, then run PostgreSQL integration tests and the live assistant/dashboard workflow.
