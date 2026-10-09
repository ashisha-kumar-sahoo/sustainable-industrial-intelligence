# AI Assistant End-to-End Diagnostic Report

## A. Root cause
Two independent causes, both confirmed with evidence:

1. The Member 6 backend was simply **not running**. Nothing was listening on
   `127.0.0.1:8000`, so `dashboard/services/ai_service.py:ask` raised a
   connection error and `utils.safe` rendered the "service is unavailable"
   fallback.
2. **Timeout mismatch (application bug).** `ask` called `post_json` with its
   default `timeout=15`, but a real answer via local Ollama `qwen3:8b` takes
   ~20-60s. Live reproduction: the same request timed out at 15s and succeeded
   (HTTP 200) at 20.7s with a longer timeout. So even a healthy service would
   be reported as unavailable.

The backend itself was healthy: `process_question(..., use_llm=False)` returned
route `current_status` with 18 real problems and no errors.

## B. Environment configuration
- `.env` is loaded by `python-dotenv` (`config/database.py`, `dashboard/config.py`).
- `DATABASE_URL` is empty. The backend's `config.database.get_connection()`
  builds the connection from the individual `DB_*` variables, so **DB_*
  fallback is supported and works** (verified by a real connection + reads).
- No `.env` change was made. No secrets were printed.

## C. PostgreSQL status
- Connectivity: port 5432 listening.
- Authentication + query: **verified** through the app's own helper
  (`ai.db.get_connection`). Read-only counts: facilities=20, alerts=374,
  energy_readings=12970, water_readings=12970, waste_readings=13690.
- No writes, DDL, or migrations were performed.

## D. Ollama status
- API: `http://127.0.0.1:11434` reachable; `/api/tags` OK.
- Model: `qwen3:8b` installed (also llama3.2:3b / llama3.2:latest).
- Real generation: **succeeded**. The real assistant prompt produced a valid,
  grounded explanation in ~24s and passed the numeric-fidelity guardrail.
  A cold model load can exceed `OLLAMA_TIMEOUT=60`, in which case the backend
  correctly keeps the deterministic answer.

## E. Backend status
- Entry point: `ai/assistant/web_app.py` (Python stdlib `ThreadingHTTPServer`,
  not FastAPI/Flask).
- Startup command (from project root): `python -m ai.assistant.web_app`.
- Listening address: `127.0.0.1:8000` (default `AI_ASSISTANT_PORT=8000`).
- Route: `POST /api/ask`; JSON `{"question": "..."}`.
- Response schema: `route`, `answer` (dict), `natural_language_response`
  (string or null), `errors` (list). Matches the dashboard's expectations.
- Response test: `HTTP 200` in 20.7s with a real `natural_language_response`.

## F. Files changed
- `dashboard/services/ai_service.py` — explicit, configurable assistant request
  timeout (`ASSISTANT_TIMEOUT`, else `OLLAMA_TIMEOUT + 30`).
  Backup: `backups/dashboard/services/ai_service.py`; diff: `diffs/ai_service.py.diff`.
- `tests/dashboard/test_ai_service_fallback.py` — 2 new regression tests plus a
  stub fix.
No `.env`, database, dependency, model, or unrelated module changes.

## G. Tests
- `python -m pytest tests/dashboard/test_ai_service_fallback.py -q` -> 11 passed.
- `python -m pytest -q` (full suite) -> 102 passed.
- See `test_results.txt`.

## H. End-to-end result
With the service running and the timeout fix in place, the dashboard's exact UI
path `utils.safe(ai.ask, "What are today's biggest problems?", label="AI Assistant")`:

- elapsed 25.6s
- warnings shown: 0
- `sample` flag: None (no fallback)
- route: `current_status`
- errors: `[]`
- displayed answer: real Ollama-generated natural-language explanation grounded
  in real PostgreSQL data.

## I. Remaining blockers / manual steps
The only remaining requirement is that the assistant service is (and stays)
running while Streamlit is used, and that Ollama is running. The service was
started for this audit (PID 30992) but background processes may stop when the
terminal/session closes. To run it persistently, use a dedicated terminal:

```powershell
# Terminal 1 (Ollama, if not already running as a service)
ollama serve

# Terminal 2 (from the project root)
python -m ai.assistant.web_app

# Terminal 3 (dashboard)
cd dashboard
streamlit run app.py
```

Optional tuning (no `.env` edit required): set `ASSISTANT_TIMEOUT` to override
the dashboard's assistant request deadline.

## J. Safety confirmation
- PostgreSQL data/schema: unchanged (read-only `SELECT`s only).
- `.env`/credentials: unchanged; no secrets printed.
- Dependencies/model files: unchanged; no downloads or installs.
- GitHub state: unchanged; no commits, pushes, or remotes.
- Files edited: backed up first; all prior backups preserved.
