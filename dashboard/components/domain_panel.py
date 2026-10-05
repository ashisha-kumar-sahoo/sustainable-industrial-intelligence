"""Standard per-dataset panel (KPI card, trend + forecast, last-24h comparison, anomalies, waste bins, supporting metrics).
Moved from pages.domain(); shared by the Resources, Environment and Operations (traffic/equipment/safety) pages.
Calculations live in services.resource_service, drawing in components.charts/tables."""
import streamlit as st
import config
from components.charts import compare, supporting_chart, trend
from components.filters import FORECAST, RAW, RES
from components.kpi_cards import kpis_data, render_kpis
from components.tables import anomalies_table, bin_fill_table
from services import resource_service as R


def domain(ds, dark):
    lab, unit, how = config.KP[ds]; r = RES(ds)
    if r.empty: st.info("No data for the selected filters."); return
    fc = FORECAST(ds, label=f"{ds} forecast"); fcs = R.forecast_series(fc, how)
    k = kpis_data()[ds]; render_kpis([k[:4]]); st.plotly_chart(trend(R.series(r, how), fcs, dark, f"{lab} — actual vs baseline, anomalies & 24h forecast ({unit})"), use_container_width=True, theme=None)
    by = R.group_column(ds); g = R.latest_by_group(r, how, by); a, b = st.columns(2); a.plotly_chart(compare(g, dark, "Last 24h by " + ("zone (hotspots)" if by == "zone_id" else "facility")), use_container_width=True, theme=None)
    an = R.latest_anomalies(r)
    with b: anomalies_table(an)
    if ds == "waste": bin_fill_table(R.bin_fill_status(r, fc))
    if ds in config.EXTRA:
        x = RAW(ds); cols = [c for c in config.EXTRA[ds] if c in x]
        if len(x) and cols: st.plotly_chart(supporting_chart(R.supporting_metrics(x, cols), cols, dark), use_container_width=True, theme=None)
