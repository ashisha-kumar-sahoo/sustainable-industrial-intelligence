# AI Assistant KeyError — Diagnostic Report

## 1. Exact missing dictionary key
`'source'` (a second latent key was also confirmed: `'evidence_actual'`).

## 2. Exact failing location
- File: `dashboard/services/ai_service.py`
- Function: `ask` -> inner `lambda`
- Line: `23` (original): `for w in (fname(r["facility_id"]).lower(), str(r["source"]).lower())`
- Exception chain started at `ai_service.py:17` (`post_json(...)` failed because
  the Member 6 service at `http://127.0.0.1:8000/api/ask` was not running), then
  the `except` fallback raised `KeyError: 'source'`.

## 3. Why the key was missing
`services/alert_service.alerts()` returns two different schemas:
- Synthetic/demo mode: includes `source`, `evidence_actual`, `evidence_expected`.
- PostgreSQL mode: includes `facility_id`, `alert_type`, `message`, `value`,
  `threshold`, ... and **no** `source` or `evidence_*`.

The `ask` fallback was written against the demo schema only. Whenever the HTTP
service was unavailable (the normal condition here), the fallback ran and
crashed. The crash propagated to `utils.safe()`, producing the reported UI text.

## 4. Fix and modified files
- `dashboard/services/ai_service.py`: schema-aware fallback that matches on
  facility name plus only-present columns and builds evidence from available
  real fields.
- `dashboard/utils.py`: diagnostic traceback logging in `safe()` (local log,
  UI message unchanged).
- `tests/dashboard/test_ai_service_fallback.py`: 9 regression tests.
- Backups: `backups/`; unified diffs: `diffs/`; real traceback:
  `assistant_errors.log`.

No PostgreSQL data/schema, `.env`, dependencies, model files, GitHub state,
charts, or unrelated modules were touched.

## 5. Verification
- Reproduced the original failure exactly (traceback in `assistant_errors.log`).
- Original reproduction now returns a clean fallback dict (no exception).
- UI boundary check (`utils.safe(ai.ask, ...)` with the real down endpoint):
  `WARNINGS_SHOWN: 0`, result is the labelled fallback dict.
- New tests: 9 passed. Full suite: 100 passed.

## 6. Live retest status
The reported defect (fallback `KeyError` replacing the real answer with the
warning) is fixed and verified at the UI boundary while the service is down.
A full live round-trip through the running Member 6 HTTP server could not be
completed in this environment because `process_question` blocks on the
unconfigured PostgreSQL connection (`DATABASE_URL` unset) / Ollama, so the
server did not return within the timeout. Start the assistant with a reachable
database (and optionally Ollama) and ask the original question to confirm the
live branch.

## 7. How to capture the traceback if it recurs
Reproduce and read `diagnostics/assistant_errors.log` (set
`ASSISTANT_ERROR_LOG` to relocate it). Each entry lists the stage, exception
type, missing key, and the full chained traceback.
