"""Overview page with KPIs, estate map, alerts, and validation evidence."""

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
from services.resource_service import (
    domain_scorecard,
    forecast_series,
    series,
    sustainability_score,
)


def overview(dark: bool) -> None:
    """Render the estate-wide summary and explain how its scores are derived."""
    page_header("📊 Overview — current state of the estate")
    st.info(
        f"**Data mode:** {config.MODE}. Values are prototype decision-support "
        "data, not official measurements."
    )

    kpis = kpis_data()
    alert_data = ALERTS()
    alert_count = len(alert_data)
    high_priority_count = (
        int((alert_data["severity"] == "HIGH").sum()) if alert_count else 0
    )
    score = sustainability_score(kpis)

    summary_cards = [values[:4] for values in kpis.values()]
    summary_cards.extend(
        [
            (
                "Active alerts",
                str(alert_count),
                f"{high_priority_count} high priority",
                "HIGH" if high_priority_count else "NORMAL",
            ),
            (
                "Recommendations pending",
                str(alert_count),
                "from decision layer",
                "MEDIUM" if alert_count else "NORMAL",
            ),
            (
                "Sustainability score (draft)",
                f"{score:.0f}/100",
                "see methodology below",
                "NORMAL" if score >= 75 else "MEDIUM",
            ),
        ]
    )
    render_kpis(summary_cards)

    map_domains = [
        dataset for dataset in config.KP if dataset in config.active_domains()
    ]
    if map_domains:
        selected_layer = st.selectbox(
            "Map layer (severity by domain)", map_domains, key="map_layer"
        )
        render_estate_map(facility_severity_rows(selected_layer, RES), dark)

    left_column, right_column = st.columns(2)
    energy_results = RES("energy")
    energy_forecasts = FORECAST("energy")
    if not energy_results.empty:
        left_column.plotly_chart(
            trend(
                series(energy_results, "sum"),
                forecast_series(energy_forecasts, "sum"),
                dark,
                "Energy trend & forecast (kWh)",
            ),
            use_container_width=True,
            theme=None,
        )

    with right_column:
        st.markdown("**Priority alerts**")
        alert_cards(alert_data.head(3), "overview")

    insights_column, recommendations_column = st.columns(2)
    with insights_column:
        insights_panel(alert_data)
    with recommendations_column:
        recommendations_panel(alert_data)

    st.subheader("Sustainability scorecard (draft)")
    scorecard_table(domain_scorecard(kpis))
    with st.expander("Scoring methodology"):
        st.write(
            "Domain score = 100 − 2 × the positive 24-hour deviation above "
            "baseline, capped at 50%. The overall score is the average of "
            "enabled domains. This is a prototype decision-support score, "
            "not an official regulatory index."
        )

    with st.expander("AI/ML validation evidence"):
        from services.model_metrics import collect_metrics

        metrics = collect_metrics()
        st.markdown(
            "**Forecast backtest** — one-step persistence baseline on current data."
        )
        if metrics["forecast"]:
            st.dataframe(
                metrics["forecast"], use_container_width=True, hide_index=True
            )
        else:
            st.info("Not enough connected data for a backtest yet.")

        st.markdown("**Anomaly monitoring**")
        if metrics["anomaly"]:
            st.dataframe(
                metrics["anomaly"], use_container_width=True, hide_index=True
            )
        st.caption(metrics["anomaly_note"])
