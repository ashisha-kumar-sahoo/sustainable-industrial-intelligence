"""Resources page (Energy / Water / Waste tabs). Moved from pages.resources."""
import streamlit as st
from components.domain_panel import domain
from components.header import page_header


def resources(dark):
    page_header("💧 Resources"); t = st.tabs(["⚡ Energy", "💧 Water", "🗑 Waste"])
    for tab, ds in zip(t, ["energy", "water", "waste"]):
        with tab: domain(ds, dark)
