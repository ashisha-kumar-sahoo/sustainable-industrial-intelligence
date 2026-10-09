"""Scenario simulation page."""

import streamlit as st

import config
from components.header import page_header
from services.simulation_service import simulate
from utils import safe


def simulation(dark: bool) -> None:
    del dark  # The shared page header handles the dashboard theme.
    page_header("🧪 Scenario Simulation")

    available_domains = [
        dataset
        for dataset in config.ACT
        if dataset in config.active_domains()
    ]
    if not available_domains:
        st.info("No simulation domains are enabled for this facility profile.")
        return

    dataset = st.selectbox("Domain", available_domains)
    action = st.selectbox("Scenario", config.ACT[dataset])
    reduction_pct = st.slider("Reduction (%)", min_value=0, max_value=40, value=15)

    if not st.button("RUN SIMULATION", type="primary"):
        return

    result = safe(
        simulate,
        dataset,
        action,
        reduction_pct,
        default=None,
        label="Simulation",
    )
    if not result:
        return

    st.warning("SIMULATED / ESTIMATED — not a measured future value.")
    current_value = result.get("current", 0.0)
    simulated_value = result.get("simulated", 0.0)
    change_pct = result.get("change_pct", 0.0)

    current_column, simulated_column, change_column = st.columns(3)
    current_column.metric("Current (24h)", f"{current_value:,.0f}")
    simulated_column.metric(
        "Simulated",
        f"{simulated_value:,.0f}",
        f"{change_pct:.1f}%",
    )
    change_column.metric("Estimated change", f"{change_pct:.1f}%")

    if result.get("sample"):
        st.caption("Sample estimate: external simulation service is not connected.")
    elif result.get("mode") == "local_estimate":
        st.caption(
            "Local deterministic estimate from the selected data; "
            "this is not an ML forecast."
        )
    if result.get("message"):
        st.caption(result["message"])
