# Dashboard design

## Purpose
A Streamlit control-centre for an industrial estate: live KPIs, anomaly/forecast charts, a 3D facility map, alerts, AI recommendations,
an AI assistant, scenario simulation and a raw-data explorer. The dashboard is a **presentation layer** — models and decision logic belong to other teams;
without a database it uses a labelled synthetic provider.

## Run-time flow (`dashboard/app.py`)
1. `st.set_page_config` (values from `config.py`).
2. `dark = not session_state.get("light_mode", False)` → `styles.apply_styles(dark)` (one CSS injection per run, same for login and dashboard).
3. No `session_state["user"]` → `components.header.render_login(dark)` and `st.stop()` (Admin Login / Create Admin Account → `services.auth_service`).
4. `PAGES` maps the 9 navigation labels to page functions; `session_state["page"]` selects one (default *Overview*).
5. `components.sidebar.render_sidebar` draws brand, theme switch, navigation buttons, global filters, data-mode caption, user name, logout.
6. The selected page function is called as `page(dark)`; any exception is caught and shown as an error without breaking the other pages.

## Layers
| Layer | Folder | Rule |
|---|---|---|
| Entry / routing | `app.py` | init + routing only |
| Config & helpers | `config.py`, `db.py`, `utils.py`, `styles.py` | constants/env, DB access, tiny helpers, CSS |
| Services | `services/` | data access and calculations; no widgets (`database_service`/`auth_service`/`alert_service`/`ai_service`/`simulation_service` may use `st.cache_data`) |
| Components | `components/` | reusable widgets; may read global filter state |
| Pages | `pages/` | compose components for one screen |

Imports only point downwards (`pages → components → services → db/config`), so there are no circular imports.

## Pages
| Navigation label | Module / function | Contents |
|---|---|---|
| 📊 Overview | `pages/overview.py::overview` | KPI grid (7 domains + alerts, pending recommendations, draft sustainability score), 3D map with domain layer selector, energy trend + forecast, top-3 alerts, AI insights, recommendations, scorecard, methodology |
| ⚡ Resources | `pages/resources.py::resources` | tabs Energy / Water / Waste → `domain_panel.domain` |
| 🌿 Environment | `pages/environment.py::environment` | AQI panel with zone hotspots + supporting metrics (pm25, pm10, co2, no2) |
| 🏭 Operations | `pages/operations.py::operations` | tabs Traffic / Equipment / Safety → `pages/traffic.py`, `equipment.py`, `safety.py` |
| 🚨 Alerts | `pages/alerts.py::alerts_page` | severity radio + alert cards with "View raw data" / "Ask AI" |
| 💬 AI Assistant | `pages/ai_insights.py::assistant` | question box, history, evidence and sample-answer notice |
| ✅ Recommendations | `pages/ai_insights.py::recs` | recommendation cards |
| 📝 Scenario Simulation | `pages/simulation.py::simulation` | domain, scenario, reduction slider, simulated result metrics |
| 📁 Raw Data Explorer | `pages/raw_data.py::rawdata` | dataset picker, search, column picker, sort, paging, CSV download |

`pages/operations.py`, `components/domain_panel.py` and `services/auth_service.py` are the only modules beyond the originally requested layout:
the nav needs the Operations tab wrapper, the seven dataset panels share one renderer, and login/register needs a home.

## Components
`sidebar` (whole sidebar) · `header` (`page_header`, `theme_switch`, `render_login`) · `kpi_cards` (`kpi_html`, `render_kpis`, `kpis_data`) ·
`charts` (Plotly `trend`, `compare`, `supporting_chart`, `apply_layout`) · `maps` (pydeck `estate_map`, `render_estate_map`) · `tables` ·
`alerts` (`alert_cards`) · `recommendations` · `filters` (sidebar widgets + `filt`, `RES`, `RAW`, `ALERTS`, `FORECAST`) ·
`status_badges` (`EMO`, severity classes) · `domain_panel` (`domain`).

## Theme and styling
`styles.py` holds all CSS: `css(dark)` base theme, `neon_css(dark)` animated form border, `NAV` login feature tiles,
`ui_css(dark)` sidebar/nav/theme-switch layer, `LOGIN_CSS` login positioning. Dark is the default; 🌙 / ☀️ call `header.set_mode`, which sets `session_state["light_mode"]`.
The same switch component is used on the login page and in the sidebar, so both stay in sync.

## Session-state keys
`user` (dict after login) · `page` · `light_mode` · `g_fac`, `g_zone`, `g_dates` (global filters) · `map_layer` · `rx_ds` (raw explorer dataset) · `aq`, `hist` (assistant) · `registered`.
