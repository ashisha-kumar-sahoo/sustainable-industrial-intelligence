# Sustainable Industrial Intelligence — Dashboard

AI-powered monitoring and decision-support dashboard for an industrial estate (Streamlit / Python).
It **presents** results (energy, water, waste, environment, traffic, equipment, safety, alerts, recommendations, AI answers, simulations);
it trains no models. Without a database it runs on a clearly-labelled synthetic sample provider, so it works out of the box.

## Folder structure

```
sustainable-industrial-intelligence/
├── dashboard/
│   ├── app.py              entry point: page config, theme/styles, login gate, sidebar, routing
│   ├── config.py           constants + env-driven settings (facilities, datasets, KPI specs, nav icons, users file path)
│   ├── db.py               PostgreSQL engine/query helpers (used only when DATABASE_URL is set)
│   ├── utils.py            small shared helpers (fid/fname lookups, safe(), nav/drill/ask_ai callbacks, post_json)
│   ├── styles.py           all global CSS (theme, neon forms, sidebar nav buttons, login layout) + apply_styles(dark)
│   ├── pages/              one module per dashboard page (plain modules routed by app.py, NOT Streamlit multipage scripts)
│   │   ├── overview.py  resources.py  environment.py  alerts.py  ai_insights.py (AI Assistant + Recommendations)
│   │   ├── operations.py (tab wrapper) → traffic.py  equipment.py  safety.py
│   │   └── simulation.py  raw_data.py
│   ├── components/         reusable UI: sidebar, header (theme switch, login screen), kpi_cards, charts, tables, maps,
│   │                       alerts, recommendations, filters (+ filtered data accessors), status_badges, domain_panel
│   ├── services/           data/business logic: database_service, resource_service, operations_service,
│   │                       alert_service, ai_service, simulation_service, auth_service
│   ├── assets/             logo.png, icons/
│   ├── .streamlit/config.toml
│   └── requirements.txt
├── outputs/dashboard/      generated outputs (kept with .gitkeep)
└── docs/dashboard/         dashboard-design.md, dashboard-data-contract.md
```

Dependency direction (no cycles): `config → db → services → components → pages → app`; `utils` depends only on `config`; `styles` on nothing project-specific.

## Installation

```bash
cd dashboard
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Dependencies: `streamlit>=1.40`, `pandas`, `numpy`, `plotly`, `pydeck`, and (PostgreSQL mode only) `sqlalchemy`, `psycopg2-binary`.
Streamlit 1.40+ is required because the styling uses `st.container(key=...)`.

## Run

```bash
cd dashboard
streamlit run app.py          # http://localhost:8501
```
(Running `streamlit run dashboard/app.py` from the repository root also works; a copy of `.streamlit/config.toml` sits at the root for that case.)

Create an admin account on the **Create Admin Account** tab, then log in. Accounts are stored (PBKDF2-hashed) in `dashboard/users.json`
— a prototype store; replace with PostgreSQL + secure sessions for production. If you had a `sii/users.json` before the refactor, copy it to `dashboard/users.json`.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/db`. Enables Member 2 PostgreSQL data mode. | unset → synthetic sample data |
| `ESTATE_LAT`, `ESTATE_LON` | Map centre | `20.29`, `85.84` |
| `ASSISTANT_URL` | AI assistant service: POST `{question}` → `{answer, evidence}` | unset → labelled sample answer |
| `SIMULATION_URL` | Simulation service: POST `{dataset, action, reduction_pct}` → `{current, simulated, change_pct}` | unset → labelled estimate |

No secrets are stored in the source code. Copy `dashboard/.env.example` to your local environment configuration; do not commit real credentials.

## Database setup (PostgreSQL mode)

Tables expected (see `docs/dashboard/dashboard-data-contract.md` for every column):
raw `energy, water, waste, environment, equipment, traffic, safety`; AI output `ai_results`, `forecasts`; decision layer `alerts`.
All raw/AI tables need `timestamp, facility_id, zone_id`. Facility ids/zones come from `config.FAC` (`F001`–`F005`, `Z01`–`Z10`) — edit it to match your estate.

## Development notes

- **New page:** add `pages/<name>.py` with `def <name>(dark): ...`, add an icon to `config.NAV_ICONS`, register it in `PAGES` in `app.py`.
- **New dataset/domain:** add it to `config.DS`, `config.KP` (label, unit, aggregation), `config.RECO`; the shared panel in `components/domain_panel.py` renders it.
- Keep calculations in `services/` (no Streamlit calls in `resource_service` / `operations_service`), widgets in `components/`, and page composition in `pages/`.
- Theme: `st.session_state["light_mode"]` (False = dark, default). The 🌙/☀️ switch in `components/header.py` sets it; `app.py` derives `dark` once per run and passes it down.
- `pages/` is a normal Python package folder here. `.streamlit/config.toml` sets `client.showSidebarNavigation = false` so Streamlit does not list those files as multipage scripts.


## Member 5 integration workflow

This dashboard is the presentation/integration layer. Member 5 does not retrain or recreate the ML models owned by Members 3 and 4.

- **Member 2:** supplies PostgreSQL raw tables for energy, water, waste, environment/AQI, equipment, traffic and safety.
- **Members 3/4:** supply the standardized `ai_results` and `forecasts` outputs described in `docs/dashboard/dashboard-data-contract.md`.
- **Member 6:** supplies `ASSISTANT_URL` and `SIMULATION_URL` when those services are ready.
- **Member 5:** consumes these outputs and renders KPIs, charts, maps, alerts, recommendations and raw data.

When `DATABASE_URL` is set, the dashboard reads PostgreSQL instead of the synthetic provider. Optional `*_TABLE` environment variables allow the team to keep different PostgreSQL table names without changing dashboard code.

Before integration, agree on the column names in `docs/dashboard/dashboard-data-contract.md`. The dashboard cannot safely infer a different schema without an explicit mapping.
