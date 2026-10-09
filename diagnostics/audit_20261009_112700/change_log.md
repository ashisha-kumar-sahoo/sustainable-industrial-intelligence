# Change Log — Sustainable Industrial Intelligence

Date: 2026-10-09
Audit directory: `diagnostics/audit_20261009_112700`

All edits were made only after backing up the original file into
`diagnostics/audit_20261009_112700/backups/<original path>`. Unified diffs are in
`diagnostics/audit_20261009_112700/diffs/`.

No database, `.env`, secret, dependency, model artifact, or Git operation was changed.

---

## 1. `dashboard/components/charts.py`

- **Backup:** `backups/dashboard/components/charts.py`
- **Diff:** `diffs/charts.py.diff`
- **Change:** Added `import pandas as pd` at the top of the module.
- **Why:** `supporting_chart()` calls `pd.to_numeric(...)` but the module never imported
  pandas, producing `NameError: name 'pd' is not defined` for every Equipment/Safety/
  Environment/Traffic section that renders supporting metrics.
- **Effect:** The existing guarded numeric normalization now executes. Mixed-dtype
  wide-form frames no longer reach `px.line` with incompatible column types; only
  numeric columns are plotted, and the categorical column is skipped.
- **Risk:** Low. Import-only addition; no behavior change beyond enabling the already
  intended code path.

## 2. `ai/assistant/data_retriever.py`

- **Backup:** `backups/ai/assistant/data_retriever.py`
- **Diff:** `diffs/data_retriever.py.diff`
- **Change:** Guarded nullable numeric conversions in
  `get_latest_energy_data`, `get_latest_water_data`, `get_latest_waste_data`, and
  `get_latest_traffic_data` so a SQL `NULL` becomes Python `None` instead of
  `float(None)`.
- **Why:** `float(row[n])` on a NULL column raised
  `TypeError: float() argument must be a string or a real number, not 'NoneType'`,
  aborting the assistant's context build.
- **Effect:** NULL measurements flow through the pipeline as `None` and are handled
  downstream by the recommendation layer.
- **Risk:** Low. Behavior is consistent with the already-guarded sibling columns in the
  same functions.

## 3. `ai/recommendations/rule_engine.py`

- **Backup:** `backups/ai/recommendations/rule_engine.py`
- **Diff:** `diffs/rule_engine.py.diff`
- **Changes:**
  - Added `import math` and `import numbers` and two helpers:
    `_numeric_value(record, key)` and `_ranked_by_metric(records, key)`.
  - `find_highest_energy_consumer`, `find_highest_water_consumer`,
    `find_highest_waste_producer`: rank only records with a usable numeric
    measurement; return `None` when none qualify.
  - `find_water_anomalies`, `find_waste_anomalies`, `find_air_quality_issues`,
    `find_traffic_issues`, `find_high_priority_alerts`: read optional fields with
    `.get(...)` instead of `item[...]`.
- **Why:** Direct indexing raised `KeyError` on records missing optional keys
  (`anomaly_flag`, `waste_type`, etc.), and `max()` over `None` raised
  `TypeError: '>' not supported between instances of 'float' and 'NoneType'`.
- **Effect:** Missing optional keys no longer crash the decision layer; missing
  measurements are excluded from rankings instead of causing false comparisons.
- **Risk:** Low/medium. Ranking semantics are unchanged for complete data; records
  without a usable measurement are now simply not ranked (verified by tests).

## 4. `ai/recommendations/decision_summary.py`

- **Backup:** `backups/ai/recommendations/decision_summary.py`
- **Diff:** `diffs/decision_summary.py.diff`
- **Change:** Replaced direct subscription on optional alert/issue fields with
  `.get(...)` (for example `issue.get("priority", 0)`).
- **Why:** `issue["aqi_category"]` and similar raised `KeyError` on partial records,
  which `process_question` captured into `result["errors"]`.
- **Effect:** `build_decision_summary` tolerates missing optional keys.
- **Risk:** Low.

## 5. `tests/test_audit_regressions.py` (new)

- **Change:** Added 11 offline regression tests:
  - 3 for `dashboard.components.charts.supporting_chart` (numeric wide-form, mixed
    dtypes, empty/missing-column frames).
  - 3 for `data_retriever` nullable columns (energy, water+waste, traffic) via a
    monkeypatched fake connection.
  - 4 for `rule_engine` ranking/anomaly behavior (missing measurements, missing
    optional keys, complete records still reported).
  - 1 for `decision_summary.build_decision_summary` with partial records.
  - 1 end-to-end `process_question(use_llm=False)` test asserting `errors == []` with
    NULL/partial data.
- **Why:** No existing tests referenced these modules; the regressions were uncovered
  only by direct reproduction.
- **Risk:** None (test-only).

---

## Files intentionally NOT changed

- `dashboard/components/charts.py` BOM: pre-existing, harmless, left in place.
- `dashboard/services/model_metrics.py` broad `except Exception: continue`: pre-existing
  and intentional resilience; left unchanged (flagged as an observation).
- Database, `.env`, secrets, dependencies, model artifacts, and Git state: untouched.

## Verification

- Baseline (pre-fix): `python -m pytest -q -p no:cacheprovider` → **67 passed**.
- Post-fix: same command → **78 passed** (see `test_results.txt`).
- New tests: `python -m pytest tests/test_audit_regressions.py -v -p no:cacheprovider`
  → **11 passed**.
- Dashboard import smoke test: **36/36** modules imported.
