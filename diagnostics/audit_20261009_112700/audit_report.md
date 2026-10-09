# Audit Report — Sustainable Industrial Intelligence

Date: 2026-10-09
Audit directory: `diagnostics/audit_20261009_112700`
Project root: `C:\Users\sahoo\OneDrive\Desktop\sustainable-industrial-intelligence-final-v4`

## 1. Scope and safety boundaries

- No PostgreSQL database was altered. No SQL was executed against the live database.
- No `.env`, credential, key, or secret file was read or modified.
- Not a Git repository (`git status` → "not a git repository"); no Git operations were performed.
- No dependency was installed, upgraded, downgraded, or removed.
- No model artifact was retrained or replaced.
- Only application source code was edited, after creating backups of every edited file.
- All tests are offline: no database, network, or Streamlit runtime is required.

## 2. Environment baseline

| Item | Value |
|---|---|
| Python | 3.14.4 (win32) |
| pandas | 3.0.6 |
| numpy | 2.4.1 |
| plotly | 7.1.0 |
| scikit-learn | 1.9.0 |
| streamlit | 1.65.0 |
| SQLAlchemy | 2.0.52 |
| psycopg2 | 2.9.13 |
| Dashboard DB mode | `PostgreSQL — source of truth` (DATABASE_URL configured; value not read/printed) |
| Test baseline (pre-fix) | **67 passed** |
| Test result (post-fix) | **78 passed** (67 baseline + 11 new regression tests) |

Entry point: `dashboard/app.py` (run from the `dashboard/` directory with `streamlit run app.py`).

## 3. Confirmed bugs and root causes

### Bug 1 — Dashboard Equipment/Safety/Environment/Traffic supporting charts crash (`charts.py` regression)

- **Severity:** High (all `config.EXTRA` domains fail to render the supporting metrics chart).
- **File:** `dashboard/components/charts.py`.
- **Reproduced:** `NameError: name 'pd' is not defined`.
- **Root cause:** The earlier audit patch modified `supporting_chart()` to call
  `pd.to_numeric(...)`, but the module only imported `plotly.express` and
  `plotly.graph_objects`. `pandas` was never imported. Any tab whose dataset is in
  `config.EXTRA` (equipment, safety, environment, traffic) and that has an available
  supporting column reaches this function and raises `NameError`.
- **Secondary (original) symptom:** In the pre-patch code, `supporting_chart()` passed
  a raw wide-form frame to `px.line(..., y=columns)`. When the plotted columns had
  differing dtypes (numeric + categorical), Plotly raised
  `ValueError: Plotly Express cannot process wide-form data with columns of different type.`
  This was reproduced directly with a mixed-dtype frame.
- **Fix:** Import `pandas as pd`. The existing guarded numeric normalization (added by
  the earlier patch) is retained and now executes correctly: only columns that convert
  to usable numeric values are plotted; non-numeric/categorical columns are skipped
  rather than crashing the page.
- **Confidence:** High (directly reproduced before and after fix).

### Bug 2 — AI assistant `float(None)` on nullable numeric columns

- **Severity:** High (whole assistant context build fails → "no numerical result is available").
- **File:** `ai/assistant/data_retriever.py`.
- **Reproduced:** Feeding a `None` numeric column through
  `get_latest_energy_data`, `get_latest_water_data`, `get_latest_waste_data`, and
  `get_latest_traffic_data` raised
  `TypeError: float() argument must be a string or a real number, not 'NoneType'`.
- **Root cause:** Several columns were converted with an unconditional `float(row[n])`
  while sibling columns in the same functions already guarded with
  `float(row[n]) if row[n] is not None else None`. A SQL `NULL` in one of the
  unguarded columns aborts retrieval, which aborts the decision context and produces
  the reported error.
- **Fix:** Guard each conversion to return `None` when the column is `NULL`, matching
  the existing pattern in the file (lines for energy `energy_consumption_kwh` /
  `peak_demand_kw`, water `water_consumption_liters` / `flow_rate`, waste
  `waste_quantity_kg` / `recyclable_quantity_kg` / `hazardous_quantity_kg`, and traffic
  `lane_occupancy_percent`).
- **Confidence:** High (directly reproduced before and after fix).

### Bug 3 — AI assistant `KeyError` from unguarded dictionary access in the recommendation layer

- **Severity:** Medium/High (assistant degrades to "unavailable"; intermittent depending on data).
- **Files:** `ai/recommendations/rule_engine.py`, `ai/recommendations/decision_summary.py`.
- **Reproduced:** With records missing optional keys (for example a water/waste reading
  without `anomaly_flag`/`anomaly_reason`/`waste_type`, or an alert/air-quality record
  without `priority`/`aqi_category`), `process_question` captured errors such as
  `KeyError: 'anomaly_flag'`, `KeyError: 'waste_type'`, and
  `KeyError: 'aqi_category'`.
- **Root cause:** Rule functions used direct subscription (`item["key"]`) for optional
  fields, assuming a fixed schema. Any schema drift, optional field, or partial record
  raises `KeyError` and aborts the decision.
- **Fix:** Use `item.get(...)` for optional fields in the anomaly/issue finders and in
  the decision summary. Anomaly flags default to falsy, so a missing flag never
  produces a false alert. Ranking functions now also skip records whose measurement is
  missing/non-numeric instead of comparing `None` to a float (`TypeError`).
- **Confidence:** High (directly reproduced before and after fix).

### Latent issue resolved alongside Bug 3 — `TypeError` when a NULL measurement is ranked

Once retrieval correctly returns `None`, `find_highest_*` originally compared `None`
with floats using `max(...)` and raised
`TypeError: '>' not supported between instances of 'float' and 'NoneType'` when more
than one record existed. The ranking helpers now filter to records with a usable
numeric value. If no record has a usable measurement, the function returns `None`,
which the assistant reports as "No current ... data is available" rather than inventing
a value.

## 4. Unconfirmed / not reproducibly failing

- No live PostgreSQL query was executed, so NULL prevalence in the user's actual tables
  was not measured. The `float(None)` and `KeyError` fixes were validated with
  representative synthetic records, not against the live database.
- The "intermittent KeyError" observed historically is consistent with Bug 3 and is
  addressed, but because the live data was not inspected, other schema-specific
  variants cannot be fully excluded.
- `dashboard/services/model_metrics.py` uses broad `except Exception: continue` in its
  metrics collector. This is pre-existing, intentional (keeps the dashboard usable when
  the DB is unavailable), and was left unchanged.

## 5. Files changed

| File | Reason |
|---|---|
| `dashboard/components/charts.py` | Added missing `import pandas as pd` so `supporting_chart()` works; retained guarded numeric normalization. |
| `ai/assistant/data_retriever.py` | Guarded nullable numeric conversions to prevent `float(None)`. |
| `ai/recommendations/rule_engine.py` | None-safe ranking; KeyError-safe optional field access. |
| `ai/recommendations/decision_summary.py` | KeyError-safe optional field access. |
| `tests/test_audit_regressions.py` | New regression tests (11). |

## 6. Commands executed (summary)

- `python --version`
- `python -m pytest -q -p no:cacheprovider` (baseline → 67 passed; post-fix → 78 passed)
- `python -m pytest tests/test_audit_regressions.py -v -p no:cacheprovider` (11 passed)
- Direct reproduction scripts (read-only) for the NameError, wide-form ValueError,
  `float(None)`, `KeyError`, and ranking `TypeError`.
- Dashboard import smoke test: 36/36 modules imported (Streamlit emitted non-fatal
  "No runtime found" warnings outside a live session).

## 7. Remaining risks / limitations

- A live Streamlit browser session and a live PostgreSQL/Ollama workflow were **not**
  executed. Passing unit and import tests do not prove end-to-end UI rendering.
- The database was deliberately not queried; NULL handling is validated structurally,
  not against production data.
- The UTF-8 BOM present in `dashboard/components/charts.py` was preserved (pre-existing;
  Python's importer accepts it). `ast.parse` on the raw text flags the BOM, but the
  module imports and runs normally.
