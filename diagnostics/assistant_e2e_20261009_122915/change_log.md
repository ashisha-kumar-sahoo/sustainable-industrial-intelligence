# AI Assistant End-to-End Repair — Change Log

Date: 2026-10-09
Audit dir: `diagnostics/assistant_e2e_20261009_122915`

## Confirmed issues
1. Operational: the Member 6 HTTP service was not running on `127.0.0.1:8000`
   (nothing listening), so the dashboard's `post_json` failed and the UI showed
   the fallback.
2. Application-code mismatch (confirmed by live measurement): the dashboard
   assistant request used `post_json`'s default 15-second timeout, but a real
   assistant answer takes ~20-60s (local Ollama `qwen3:8b`). Even with the
   service running, the dashboard aborted at 15s and showed the fallback.

## Files changed
### `dashboard/services/ai_service.py`
- Backup: `backups/dashboard/services/ai_service.py`
- Diff: `diffs/ai_service.py.diff`
- Changes:
  - Added `_request_timeout()`:
    - uses `ASSISTANT_TIMEOUT` when set,
    - else `OLLAMA_TIMEOUT + 30` (default 60 + 30 = 90s),
    - safe numeric fallback 150s.
  - `ask()` now calls `post_json(..., timeout=_request_timeout())`.
- Why: align the dashboard HTTP client deadline with the assistant's real,
  LLM-backed latency so a healthy service can return a genuine answer instead
  of the 15s fallback. `post_json`'s shared default is left untouched, so
  unrelated callers (e.g. simulation) are unaffected.

### `tests/dashboard/test_ai_service_fallback.py`
- Added 2 regression tests: `ask()` passes a timeout >= 60s, and the timeout is
  configurable via `ASSISTANT_TIMEOUT`. Updated one existing stub to accept the
  new keyword argument.

## Not changed
- `.env`, PostgreSQL data/schema, dependencies, model files, GitHub state,
  other dashboard modules, and the previous fallback fix + logging.

## Evidence
- DB (read-only): `facilities=20`, `alerts=374`, `energy_readings=12970`.
- Live HTTP: `POST /api/ask` -> `HTTP 200` in 20.7s with a real
  `natural_language_response`.
- Dashboard UI path: `utils.safe(ai.ask, ...)` -> 25.6s, 0 warnings,
  `sample=None`, real answer.
