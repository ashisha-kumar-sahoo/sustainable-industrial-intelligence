"""Scenario Simulation page. Moved from pages.simulation."""
import streamlit as st
import config
from components.header import page_header
from services.simulation_service import simulate
from utils import safe


def simulation(dark):
    page_header("🧪 Scenario Simulation"); ds = st.selectbox("Domain", list(config.ACT)); act = st.selectbox("Scenario", config.ACT[ds]); pct = st.slider("Reduction (%)", 0, 40, 15)
    if st.button("RUN SIMULATION", type="primary"):
        r = safe(simulate, ds, act, pct, default=None, label="Simulation")
        if r: st.warning("SIMULATED / ESTIMATED — not a measured value"); a, b, c = st.columns(3); a.metric("Current (24h)", f"{r['current']:,.0f}"); b.metric("Simulated", f"{r['simulated']:,.0f}", f"{r['change_pct']:.1f}%"); c.metric("Estimated change", f"{r['change_pct']:.1f}%"); r.get("sample") and st.caption("Sample estimate: Member 6 simulation service not connected.")
