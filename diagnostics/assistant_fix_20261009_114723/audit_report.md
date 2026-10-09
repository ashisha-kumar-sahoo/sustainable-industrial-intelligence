# AI Assistant Repair — Audit Report

Date: 2026-10-09
Audit dir: `diagnostics/assistant_fix_20261009_114723`
Project root: `C:\Users\sahoo\OneDrive\Desktop\sustainable-industrial-intelligence-final-v4`

## Scope

Repair only the AI Assistant. No database schema/records, `.env`, secrets,
dependencies, model artifacts, Git state, or working dashboard/chart code were
changed. No SQL was executed and no LLM/network call was made during tests.

## Execution path traced

Streamlit `dashboard/pages/ai_insights.py` -> `dashboard/services/ai_service.py`
(HTTP) OR the local `ai/assistant/web_app.py` (`/api/ask`) ->
`ai/assistant/service.py:process_question` -> `query_router.route_question` ->
`context_builder.build_context` -> `data_retriever` (PostgreSQL) +
`ml.energy.predict` (M3) -> `_build_decision` ->
`ai/recommendations/*` (rule_engine, decision_summary, recommendation_engine,
risk_score, impact_estimator, explanation) + `ai/simulation/*` for scenarios ->
`response_generator` -> optional `_ollama_explain`.

## Confirmed root causes (reproduced before fixing)

### 1. Missing-key `KeyError` in the ranking helpers
- Files/lines: `ai/recommendations/rule_engine.py` — `find_highest_energy_consumer`
  return block (old lines 41-44), `find_highest_water_consumer` (old 92-95),
  `find_highest_waste_producer` (old 138-142).
- Traceback line: `"waste_type": highest["waste_type"]` (old line 141) for a
  record without the optional `waste_type` column; analogous for
  `facility_name`/`reading_ts`.
- Effect: `process_question("What is the waste status?")` returned
  `errors=[{stage: data_or_decision, type: KeyError, message: "'waste_type'"}]`
  and the answer "Database or intelligence processing failed". This is the
  reported intermittent KeyError (schema/partial-record dependent).
- Fix: read returned fields with `.get(...)` so absent optional columns/keys
  yield `None` instead of raising.

### 2. `abs(None)` `TypeError` in the risk score
- File/line: `ai/recommendations/risk_score.py:3-5`
  `abs(anomaly.get("deviation_pct", 0))`.
- Cause: the default `0` only applies when the key is *absent*. When it is
  present with value `None` (an M3 anomaly without deviation, or a problem dict
  built with `deviation_pct=None`), `abs(None)` raises
  `TypeError: bad operand type for abs(): 'NoneType'`.
- Effect: energy / energy-anomaly routes returned "processing failed".
- Fix: coerce non-numeric/`None`/NaN deviations to `0.0` before `abs`.

### 3. `None` message `TypeError` in the impact estimator
- File/lines: `ai/recommendations/impact_estimator.py:10-12` and `:34-36`
  (`message = problem.get("message", "")`).
- Cause: an alert whose SQL `message` is `NULL` yields `None` here, then
  `"over)" not in None` and `re.search(pattern, None)` raise `TypeError`.
- Effect: `process_question("What are today's biggest problems?")` failed with
  an alert that has a NULL message.
- Fix: treat a non-string message as "no parseable impact" and return `None`.

### 4. `float(None)` in the scenario simulation
- Source line: `ai/simulation/impact_calculator.py:10`
  `baseline_value = float(baseline_value)`.
- Trigger: `ai/assistant/service.py:_scenario` passed
  `baseline["energy_consumption_kwh"]` (SQL `NULL`) into the simulation.
- Effect: `process_question("What if Facility A reduces energy by 20%?")`
  returned `TypeError: float() argument must be a string or a real number, not
  'NoneType'` — the exact reported `float(None)` error.
- Fix: `_scenario` detects a missing baseline and returns
  "No current energy data is available for this simulation." instead of
  simulating. `impact_calculator.calculate_energy_reduction` now raises a clear
  `ValueError` for a non-numeric/non-finite baseline instead of a cryptic
  `TypeError`.

### 5. `abs(None)` `TypeError` in the energy-anomaly response
- File/line: `ai/assistant/response_generator.py` — sort key
  `abs(x.get("deviation_pct", 0))` (old line 61).
- Same root cause as (2); reached on the energy-anomaly route.
- Fix: shared deviation-magnitude helper; evidence renders
  "deviation unavailable" and "severity unclassified" instead of "None".
- Note: this file was edited before its backup was placed; the exact pre-edit
  content was reconstructed verbatim into `backups/` for a valid diff.
- Fix #5 was applied after re-running the harness showed the energy-anomaly
  route still failing.

## Data semantics preserved

- Missing measurements are **not** converted to zero for simulation; a NULL
  energy/water baseline produces an explicit "no current data" message.
- `None`/NaN/`pd.NA` measurements are excluded from rankings rather than
  treated as real values.
- Zero remains distinguishable from unavailable (a genuine `0.0` is still
  returned as `0.0`; only `None`/NaN are treated as missing).
- No sensor reading, prediction, incident, or recommendation is invented.

## Error reporting / security

- `process_question` no longer stores raw `str(exc)` in `result["errors"]`.
  Tests and the UI previously could surface connection strings or paths. The
  failure `type` is retained; the message is a fixed safe string. The
  `/api/ask` handler already returns only the exception class name on 500.

## Files changed

| File | Change |
|---|---|
| `ai/recommendations/rule_engine.py` | `.get(...)` in the three `find_highest_*` returns |
| `ai/recommendations/risk_score.py` | None/NaN-safe deviation via `_deviation_magnitude` |
| `ai/recommendations/impact_estimator.py` | non-string `None` message handled |
| `ai/assistant/response_generator.py` | None/NaN-safe sort key + evidence text |
| `ai/assistant/service.py` | `_scenario` missing-baseline guard; sanitized error text |
| `ai/simulation/impact_calculator.py` | clear `ValueError` for invalid baseline |
| `tests/test_assistant_repair.py` | 13 new offline regression tests |

## Verification

- New tests: 13 passed.
- Full suite: 91 passed (78 prior + 13 new).
- Level: unit/integration of `process_question` and its collaborators with mocked
  retrievers. Not verified end-to-end against live PostgreSQL, Streamlit, or Ollama.

## Remaining risks

- Live NULL prevalence and exact schema were not queried (DB deliberately not
  touched); fixes are validated against representative mocked rows.
- Ollama explanation generation is independent of the fixed data path and was
  not exercised (no local LLM call made).
