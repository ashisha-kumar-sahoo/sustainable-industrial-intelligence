"""Overview page: KPI grid, 3D estate map, energy trend, priority alerts, AI insights, recommendations, sustainability scorecard.
Moved from pages.overview; calculations now come from services.resource_service / operations_service, widgets from components."""
import streamlit as st
import config
from components.alerts import alert_cards
from components.charts import trend
from components.filters import ALERTS, FORECAST, RES
from components.header import page_header
from components.kpi_cards import kpis_data, render_kpis
from components.maps import render_estate_map
from components.recommendations import insights_panel, recommendations_panel
from components.tables import scorecard_table
from services.operations_service import facility_severity_rows
from services.resource_service import domain_scorecard, forecast_series, series, sustainability_score


def overview(dark):
    page_header("📊 Overview — current state of the estate"); st.info(f"**Data mode:** {config.MODE}. Values are prototype decision-support data, not official measurements.")
    K = kpis_data(); al = ALERTS(); n = len(al); hi = int((al["severity"] == "HIGH").sum()) if n else 0
    score = sustainability_score(K)
    render_kpis([v[:4] for v in K.values()] + [("Active alerts", str(n), f"{hi} high priority", "HIGH" if hi else "NORMAL"), ("Recommendations pending", str(n), "from decision layer", "MEDIUM" if n else "NORMAL"), ("Sustainability score (draft)", f"{score:.0f}/100", "see methodology below", "NORMAL" if score >= 75 else "MEDIUM")])
    layer = st.selectbox("Map layer (severity by domain)", list(config.KP), key="map_layer")
    render_estate_map(facility_severity_rows(layer, RES), dark)
    a, b = st.columns(2); e = RES("energy"); fc = FORECAST("energy")
    if len(e): a.plotly_chart(trend(series(e, "sum"), forecast_series(fc, "sum"), dark, "Energy trend & forecast (kWh)"), use_container_width=True, theme=None)
    with b: st.markdown("**Priority alerts**"); alert_cards(al.head(3), "ov")
    c, d = st.columns(2)
    with c: insights_panel(al)
    with d: recommendations_panel(al)
    st.subheader("Sustainability scorecard (draft)"); scorecard_table(domain_scorecard(K))
    with st.expander("Scoring methodology"):
        st.write("Domain score = 100 − 2 × (24h deviation above baseline, capped at 50%). Overall = average of domains. This is a prototype decision-support score, not an official regulatory index.")
    with st.expander("AI/ML validation evidence"):
        from services.model_metrics import collect_metrics
        metrics = collect_metrics()
        st.markdown("**Forecast backtest** — one-step persistence baseline on the current data.")
        if metrics["forecast"]:
            st.dataframe(metrics["forecast"], use_container_width=True, hide_index=True)
        else:
            st.info("Not enough connected data for a backtest yet.")
        st.markdown("**Anomaly monitoring**")
        if metrics["anomaly"]:
            st.dataframe(metrics["anomaly"], use_container_width=True, hide_index=True)
        st.caption(metrics["anomaly_note"])
