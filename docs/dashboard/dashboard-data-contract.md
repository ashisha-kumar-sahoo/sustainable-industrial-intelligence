# Dashboard data contract

All timestamps are hourly. `facility_id` ∈ `F001…F005`, `zone_id` ∈ `Z01…Z10` (see `config.FAC`). Severity values: `HIGH`, `MEDIUM`, `NORMAL`.
Mode is chosen by `DATABASE_URL`: set → PostgreSQL tables below; unset → synthetic sample provider (168 h, seed 7, 5 facilities × 2 zones, fixed anomaly injections in `config.INJ`).

## 1. Raw tables (`services.database_service.raw`)
Common columns: `timestamp, facility_id, zone_id`. Dataset-specific:

| Table | Main metric | Extra columns |
|---|---|---|
| energy | `kwh` | – |
| water | `kl` | – |
| waste | `fill_pct` | `bin_id` |
| environment | `aqi` | `pm25, pm10, co2, no2` |
| equipment | `temp_c` | `machine_id, vibration_mm_s, runtime_h, utilization_pct` |
| traffic | `vehicles` | `trucks, avg_speed_kmh, parking_occupancy_pct` |
| safety | `incidents` | `severity_level` |

`raw(ds, fac=None, zone=None, start=None, end=None, limit=5000) → DataFrame` (newest first; `end` is inclusive of the whole day). Used by: Raw Data Explorer, supporting-metrics chart.

## 2. AI results (`ai_results`, `database_service.results(ds)`)
Columns (`config.CONTRACT`): `source, facility_id, zone_id, timestamp, actual_value, expected_value, deviation_pct, severity, is_anomaly`.
Synthetic mode: expected = hour-of-day median; severity HIGH ≥ +30 %, MEDIUM ≥ +15 %. Used by: every KPI, trend, comparison, anomaly table, map layer.

## 3. Forecasts (`forecasts`, `database_service.forecast(ds)`)
Columns: `source, facility_id, zone_id, timestamp, forecast_value` (next 24 h). Used by: trend charts, waste "predicted_%".

## 4. Alerts (`alerts`, `alert_service.alerts()`)
Columns: `alert_id, severity, source, facility_id, zone_id, timestamp, title, evidence_actual, evidence_expected, deviation_pct, recommendation, insight_text, status`.
Used by: Overview (alerts, insights, recommendations, score cards), Alerts page, Recommendations page, assistant fallback.

## 5. Assistant (`ai_service.ask(q)`)
`ASSISTANT_URL` set → POST `{"question": q}` → `{"answer": str, "evidence": str}`. Otherwise returns `{answer, evidence, sample: True}` built from the first matching alert (facility name or dataset keyword in the question).

## 6. Simulation (`simulation_service.simulate(ds, action, pct)`)
`SIMULATION_URL` set → POST `{"dataset", "action", "reduction_pct"}` → `{"current", "simulated", "change_pct"}`. Otherwise `{current: last-24h actual sum, simulated: current × (1 − pct/100), change_pct: −pct, sample: True}`.
Scenarios per domain: `config.ACT`; reduction slider 0–40 % (default 15).

## 7. Shaping functions (pure, no Streamlit)
| Function | Input → output | Used by |
|---|---|---|
| `resource_service.kpi_for(ds, r)` | filtered results → `(label, value, delta text, severity, deviation %)` | KPI cards, scorecard |
| `series(r, how)` | results → `timestamp, actual, expected, anom` | trend chart |
| `forecast_series(fc, how)` | forecast → `timestamp, forecast` or `None` | trend chart |
| `latest_by_group(r, how, by)` | results → last-24 h `actual, expected, label` per facility/zone | comparison chart |
| `latest_anomalies(r)` | results → 10 newest anomalies | anomalies table |
| `bin_fill_status(r, fc)` | results, forecast → `current_%`, `predicted_%` | waste table |
| `supporting_metrics(x, cols)` | raw → hourly mean of `cols` | supporting chart |
| `sustainability_score(K)`, `domain_scorecard(K)` | KPI dict → score / table (domain = 100 − 2·min(50, dev %)) | Overview |
| `operations_service.facility_severity_rows(layer, get_results)` | → `name, lat, lon, severity, height, tip` per facility | 3D map |

## 8. Auth store (`auth_service`)
`dashboard/users.json`: list of `{full_name, admin_id, email, org, phone, salt, hash}` (PBKDF2-SHA256, 120 000 rounds).
`register(form) → error text | None`, `login(id_or_email, password) → {full_name, admin_id, email, org} | None`.

## 9. Global filters (session state)
`g_fac` (name or "All"), `g_zone` ("All" or zone id; reset when facility changes), `g_dates` (start, end). Applied by `components.filters.filt` to results/raw (dates) and alerts/forecast (facility, zone only).


## Team ownership / integration boundary

| Owner | Dashboard contract |
|---|---|
| Member 2 | Raw PostgreSQL tables listed above |
| Member 3 | `ai_results` / `forecasts` rows for energy, water and waste |
| Member 4 | `ai_results` / `forecasts` rows for environment, traffic, equipment and safety |
| Member 6 | `alerts`, `ASSISTANT_URL`, and `SIMULATION_URL` decision-layer outputs |
| Member 5 | Streamlit presentation, filtering, charts, maps, KPIs and raw-data exploration |

The dashboard does not assume that Member 5 owns the anomaly detection, forecasting, hotspot detection or recommendation algorithms. In PostgreSQL mode those results are consumed from the agreed tables.
