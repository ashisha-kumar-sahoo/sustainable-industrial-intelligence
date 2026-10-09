# AI/ML Model Folder Audit

## Executive finding

`ai/operations/` and `ml/` are **overlapping parallel implementations, not exact duplicate copies**. They cover the same four operational domains—environment, equipment, safety, and traffic—but use different data contracts, feature engineering, and analysis functions.

## Runtime ownership

- `ml/` is the **canonical runtime pipeline** for the dashboard. `dashboard/services/operations_ml_service.py` imports predictors from `ml.environment`, `ml.traffic`, `ml.equipment`, and `ml.safety`.
- `ai/operations/` is a separate domain-analysis implementation currently imported by `tests/operations/`, but not imported by the dashboard or assistant runtime.
- The `ai/operations/` version includes functions not identically represented in `ml/`, such as its AQI forecast and some domain-specific feature/risk summaries. Conversely, `ml/` includes the predictor orchestration and evaluation/hotspot modules used by the dashboard.

## Domain-by-domain comparison

| Domain | `ai/operations/` focus | `ml/` focus | Conclusion |
|---|---|---|---|
| Environment | Validation, pollution features, anomaly/risk scoring, AQI forecasting, structured results | Predictor orchestration, anomaly/risk pipeline, evaluation and hotspot support | Overlap plus distinct forecasting/analysis functionality |
| Equipment | Temperature/vibration/energy features and equipment risk summaries | Isolation Forest anomaly detection, utilization features, inspection priority and evaluation | Overlap; `ml/` is the dashboard runtime implementation |
| Safety | Incident-count/response-time features and domain risk summary | Incident risk scoring, inspection priority, hotspot analysis and evaluation | Overlap but different input contract and feature definitions |
| Traffic | Traffic feature engineering, risk and hotspot summaries | Congestion predictor, parking/hotspot analysis and evaluation | Overlap; `ml/` is the dashboard runtime implementation |

## Decision taken in this audit

1. Do **not** delete either tree based on folder names alone.
2. Keep `ml/` as the single runtime source used by the dashboard and its adapters.
3. Keep `ai/operations/` as a separate legacy/research pipeline for now because it has distinct functions and its own tests. Do not import it into production routes without an explicit adapter and contract tests.
4. Keep the distinction documented so future team members do not assume the two trees are synchronized.
5. New equipment/safety database integration uses `ml/` through the dashboard adapters; the old `ai/operations/` tests remain regression coverage for that alternate pipeline.

## Remaining maintainability risk

There is still overlapping business logic across the two trees, so thresholds and results can diverge. Full code consolidation would require porting and reconciling the unique features, forecasting behavior, output schemas, and tests—not a safe bulk deletion. This audit documents the split and establishes `ml/` as runtime canonical without silently discarding M4 work.
