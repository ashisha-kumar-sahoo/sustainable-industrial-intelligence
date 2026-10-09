# AI Operations vs. ML Model Folder Audit

## Conclusion

`ai/operations/` and `ml/` are **not byte-for-byte duplicates**, but they do contain overlapping implementations for environment, traffic, equipment, and safety analytics. They use different data contracts and expose different outputs, so deleting one tree by folder name alone would be unsafe.

## How the implementations differ

| Area | `ai/operations/` | `ml/` |
|---|---|---|
| Primary contract | Database-shaped records using `reading_ts`, `facility_id`, and `sensor_id` | Reusable Pandas pipelines using `timestamp`/`location`, or `equipment_id` for equipment data |
| Structure | Domain config, data preparation, feature creation, anomaly/risk/hotspot logic, and analysis builders | Reusable preprocessing and individual algorithms orchestrated by each domain's `predict.py` |
| Domains | Environment, traffic, equipment, safety | Energy, water, waste, environment, traffic, equipment, safety |
| Automated tests | `tests/operations/` tests the schema-oriented functions | `tests/test_ml_operation_pipelines.py` now smoke-tests the four reusable operations pipelines |

The two trees therefore overlap in purpose but are not interchangeable without a deliberate data-contract and output migration.

## Runtime wiring found in this audit

- The dashboard's common analytics path is `dashboard/services/database_service.py`. It computes a recent hourly baseline and IQR-style anomaly flags; it does not call the four `ai/operations` pipelines.
- The assistant calls the M3 energy intelligence path and the waste overflow estimator. The four reusable `ml/{environment,traffic,equipment,safety}` pipelines are tested but are not yet wired to the live dashboard/assistant paths.
- `ai/operations/` has no production call sites in the current codebase; its imports are within that tree and its tests.
- Dashboard equipment status currently comes from `public.sensors` status/calibration fields. Safety currently comes from safety-tagged `public.alerts` records.

## Recommended long-term boundary

1. Keep `ml/` as the reusable model/prediction layer.
2. Use one explicit adapter layer to translate PostgreSQL names into the model contracts.
3. Keep only one active implementation of each algorithm after output contracts and tests are migrated.
4. Do not remove `ai/operations/` until its unique functionality and existing tests have been migrated or explicitly retired.

This archive documents the overlap rather than silently deleting teammate code. A full consolidation requires choosing and testing the canonical outputs for all four domains.

## Data and backend limitations

- The supplied schema has waste fill-level and fill-rate telemetry, which supports the six-hour waste estimator.
- The supplied schema does not have a dedicated equipment-health telemetry table containing the full temperature/vibration/utilization series expected by the reusable equipment model.
- The supplied schema does not have a dedicated safety-incident table with people affected and response time, so the safety model cannot be evaluated against live incident records without an approved schema/data change.
- `backend/` is currently a reserved/empty directory. A separate backend service is not required for this local prototype: the Streamlit dashboard uses `dashboard/services/` for data access and `ai/assistant/web_app.py` exposes the local assistant HTTP API. No extra backend service or database table was added during this audit.

These limitations are explicit; they should not be presented in the demo as fully integrated live predictive models.
