# AI Assistant Repair — Change Log

Date: 2026-10-09
Audit dir: `diagnostics/assistant_fix_20261009_114723`

Backups (pre-edit) are in `backups/<original path>`; unified diffs in `diffs/`.
No existing backup was overwritten.

## 1. `ai/recommendations/rule_engine.py`
- Backup: `backups/ai/recommendations/rule_engine.py`
- Diff: `diffs/rule_engine.py.diff`
- Change: `find_highest_energy_consumer`, `find_highest_water_consumer`,
  `find_highest_waste_producer` now build their result dicts with `.get(...)`
  instead of direct subscription.
- Why: `highest["waste_type"]` (and `facility_name`/`reading_ts`) raised
  `KeyError` when an optional column/key was absent, failing the waste route.
- Risk: low; values are unchanged when present.

## 2. `ai/recommendations/risk_score.py`
- Backup: `backups/ai/recommendations/risk_score.py`
- Diff: `diffs/risk_score.py.diff`
- Change: added `_deviation_magnitude(value)` (treats `None`, `bool`, non-Real,
  and NaN as `0.0`) and used it in `calculate_risk`.
- Why: `abs(anomaly.get("deviation_pct", 0))` raised
  `TypeError: bad operand type for abs(): 'NoneType'` when the key existed with
  value `None`, failing energy/anomaly routes.
- Risk: low; absent deviation already mapped to LOW previously.

## 3. `ai/recommendations/impact_estimator.py`
- Backup: `backups/ai/recommendations/impact_estimator.py`
- Diff: `diffs/impact_estimator.py.diff`
- Change: `calculate_excess` / `calculate_excess_quantity` return `None` when
  `problem["message"]` is not a string (e.g. SQL NULL).
- Why: an alert with a NULL message raised `TypeError` in string membership /
  regex, failing the current-status question.
- Risk: low; only affects unparseable messages.

## 4. `ai/assistant/response_generator.py`
- Backup: `backups/ai/assistant/response_generator.py` (reconstructed verbatim
  from the pre-edit content because the edit preceded the copy)
- Diff: `diffs/response_generator.py.diff`
- Change: added `_deviation_magnitude`; the anomaly evidence sort key is
  NaN/None-safe, and evidence prints "deviation unavailable" /
  "severity unclassified" instead of "None".
- Why: `abs(x.get("deviation_pct", 0))` raised `TypeError` on the
  energy-anomaly route when deviation was `None`.
- Risk: low; display-only change.

## 5. `ai/assistant/service.py`
- Backup: `backups/ai/assistant/service.py`
- Diff: `diffs/service.py.diff`
- Changes:
  - `_scenario`: for the all-facilities case, sum only non-`None` readings and
    return "No current energy/water data is available for this simulation."
    when none exist. For a matched facility, require a non-`None` baseline
    before simulating.
  - `process_question`: the `data_or_decision` error entry keeps the exception
    `type` but uses a fixed safe message instead of `str(exc)`.
- Why: `float(None)` in the simulation path; and raw exception text (possible
  connection strings/paths) was surfaced to the UI.
- Risk: low; behavior for valid data is unchanged.

## 6. `ai/simulation/impact_calculator.py`
- Backup: `backups/ai/simulation/impact_calculator.py`
- Diff: `diffs/impact_calculator.py.diff`
- Change: `calculate_energy_reduction` validates the baseline (`float(...)` in
  try/except + `math.isfinite`) and raises a clear `ValueError` for
  non-numeric/non-finite input.
- Why: the reported source line `float(baseline_value)` raised a cryptic
  `TypeError` for `None`.
- Risk: low; valid numeric baselines behave exactly as before.

## 7. `tests/test_assistant_repair.py` (new)
- 13 offline regression tests covering: the biggest-problems question, empty
  results, missing keys, `None` numerics, pandas NaN/`pd.NA`, missing optional
  columns, no recent readings, partial-domain data, a normal valid response,
  and safe reporting of internal exceptions.

## Not changed
- PostgreSQL schema/records, `.env`, secrets, dependencies, model artifacts,
  Git state, dashboard tabs, and chart code.
