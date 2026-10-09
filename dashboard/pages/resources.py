"""Resource monitoring page with Energy, Water, and Waste tabs."""

import streamlit as st

from components.domain_panel import domain
from components.header import page_header


RESOURCE_DOMAINS = ["energy", "water", "waste"]
RESOURCE_TAB_LABELS = ["⚡ Energy", "💧 Water", "🗑 Waste"]


def resources(dark: bool) -> None:
    page_header("💧 Resources")
    tabs = st.tabs(RESOURCE_TAB_LABELS)

    for tab, dataset in zip(tabs, RESOURCE_DOMAINS):
        with tab:
            domain(dataset, dark)
