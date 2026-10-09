# Final Setup

## 1. Configure the environment

From the project root, copy `.env.example` to `.env` and set `DB_PASSWORD` to the password for your existing PostgreSQL user. The dashboard will build its connection URL from `DB_*` if `DATABASE_URL` is blank. If you use `DATABASE_URL` explicitly, ensure its password is URL-encoded.

Do not commit `.env`. The final ZIP intentionally does not include it.

## 2. Install Python dependencies

From the project root:

```powershell
pip install -r requirements.txt
```

## 3. Keep the existing database

Use your existing `smart_industrial_estate` database. Do not drop or recreate it. This package does not require re-running `schema.sql` or `seed.sql` against the existing database.

## 4. Apply the additive equipment/safety migration

Back up your existing database before applying a schema change. From PowerShell, run:

```powershell
pg_dump -U postgres -h localhost -p 5432 -d smart_industrial_estate -F c -f "$HOME\smart_industrial_estate_backup.dump"
```

After confirming the backup exists, apply only the new migration from the project root:

```powershell
psql -U postgres -h localhost -p 5432 -d smart_industrial_estate -v ON_ERROR_STOP=1 -f ".\database\migrations\002_add_equipment_safety_telemetry.sql"
```

This migration is additive: it preserves existing rows, adds typed raw fields plus a complete JSONB payload, creates `public.equipment_readings` and `public.safety_readings`, extends the sensor type constraint, and registers missing synthetic equipment/safety sensors per facility. It does not create, drop, or replace the database. Do not apply it until the backup is verified. If `psql` or `pg_dump` is not on PATH, run them from your PostgreSQL `bin` directory.

Verify that both tables exist before proceeding:

```powershell
psql -U postgres -h localhost -p 5432 -d smart_industrial_estate -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('equipment_readings', 'safety_readings') ORDER BY table_name;"
psql -U postgres -h localhost -p 5432 -d smart_industrial_estate -c "SELECT sensor_type, COUNT(*) FROM public.sensors WHERE sensor_type IN ('EQUIPMENT', 'SAFETY') GROUP BY sensor_type ORDER BY sensor_type;"
```

The first query should list both new tables. The second should show the equipment and safety sensor registrations created for facilities that did not already have those sensor types.

## 5. Generate fresh sensor-style data (optional demo step)

With PostgreSQL running, the migration applied, and `.env` configured, run from the project root:

```powershell
python -m ingestion.sensor_simulator
python -m ingestion.load_to_postgres
```

The simulator creates a recent seven-day batch across eight sensor-style domains. The loader preserves the original JSON payload in `raw.raw_sensor_data`, validates and cleans readings, and inserts idempotently into the eight public domain tables, including the new equipment and safety tables. Safety incident context produced by the simulator is synthetic and must not be described as real incident/response data.

## 6. Start the local AI assistant

Ensure Ollama is running and Qwen is installed. In one terminal:

```powershell
ollama run qwen3:8b
```

In another terminal, from the project root:

```powershell
python -m ai.assistant.web_app
```

The assistant endpoint is `http://127.0.0.1:8000/api/ask`. The deterministic PostgreSQL/rule-based answer is retained if Ollama is unavailable.

## 7. Start the dashboard

In another terminal, from the project root:

```powershell
cd dashboard
streamlit run app.py
```

Register a local account on first launch. The first account becomes the initial administrator; later public registrations can choose Operations or Sustainability but cannot grant themselves administrator access. Account records are stored outside the source tree at `~/.sustainable-industrial-intelligence/users.json` by default (override with `USERS_FILE`) so local account details are not accidentally committed. If an older project-local `dashboard/users.json` contains accounts, the first load migrates them to the local account store.

## 8. Facility profile

Use the sidebar's **Facility profile** selector. The Hospital profile hides traffic-oriented views while reusing the same dashboard architecture. The included seeded dataset is still industrial-estate data and must not be presented as actual hospital measurements.

## 9. Tests

From the project root:

```powershell
python -m pytest -q
```

Database integration tests require valid environment credentials and a running PostgreSQL database. Live assistant testing requires Ollama and the local assistant service to be running.
