# AI Assistant — KeyError Repair Change Log

Date: 2026-10-09
Audit dir: `diagnostics/assistant_keyerror_20261009_120926`

Reported symptom:
`⚠️ AI Assistant is temporarily unavailable (KeyError). The rest of the dashboard can continue.`

## Root cause
`dashboard/services/ai_service.py:ask()` catches any HTTP failure from the
Member 6 service and falls back to local `alerts()`. The fallback assumed the
synthetic/demo `alerts()` schema (`source`, `evidence_actual`,
`evidence_expected`). In PostgreSQL mode `alerts()` produces a different schema,
so the fallback raised `KeyError: 'source'` (and would next raise
`KeyError: 'evidence_actual'`). The `KeyError` propagated to `utils.safe()`,
which replaced the real detail with the friendly warning above.

## Files changed
### 1. `dashboard/services/ai_service.py`
- Backup: `backups/dashboard/services/ai_service.py`
- Diff: `diffs/ai_service.py.diff`
- Changes:
  - Added `_present`/`_text` helpers (None/NaN-safe).
  - Added `_terms(row)`: matches the question against the facility name plus
    only the columns actually present (`source`, `alert_type`).
  - Added `_evidence(row)`: uses real available fields in priority order
    (`evidence_actual`/`evidence_expected`, else `value`/`threshold`, else
    `deviation_pct`); returns `""` when none exist. No fabricated values.
  - `ask()` no longer indexes columns directly; uses `.get()` only for
    genuinely optional/non-contract fields and preserves the response shape
    (`answer`, `evidence`, `sample`, `connected`).
- Why: removes the contract mismatch between the fallback and the
  PostgreSQL-mode `alerts()` schema.

### 2. `dashboard/utils.py`
- Backup: `backups/dashboard/utils.py`
- Diff: `diffs/utils.py.diff`
- Changes:
  - Added `_diagnostic_log_path()` and `record_operation_failure()`.
  - `safe()` now records the full traceback (type, missing `KeyError` key,
    stage/function name) to a local log before showing the unchanged friendly
    warning.
  - Log location: `diagnostics/assistant_errors.log`, overridable with the
    `ASSISTANT_ERROR_LOG` environment variable.
  - Nothing is shown to dashboard users; the existing `st.warning` text is
    byte-for-byte unchanged.
- Why: satisfies the requirement to capture the exact traceback locally while
  preserving the friendly UI message.

### 3. `tests/dashboard/test_ai_service_fallback.py` (new)
- 9 offline regression tests (see test_results.txt). Executed in a subprocess
  with the same isolated import layout Streamlit uses (`dashboard` before the
  project root), because the project root also contains a `config/` namespace
  package that shadows `dashboard/config.py` in the shared pytest process.

## Not changed
- PostgreSQL data/schema, `.env`/secrets, dependencies, model files, GitHub
  state, working dashboard charts, and unrelated modules.

## Diagnostic evidence
- `assistant_errors.log` contains the real `KeyError: 'source'` traceback
  captured from the pre-fix backup file, at
  `backups/dashboard/services/ai_service.py:23`.
