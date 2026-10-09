"""Operations page containing traffic, equipment, and safety tabs."""

import streamlit as st

import config
from components.header import page_header
from pages.equipment import equipment
from pages.safety import safety
from pages.traffic import traffic


ALL_OPERATION_TABS = [
    ("🚚 Traffic", "traffic", traffic),
    ("⚙️ Equipment", "equipment", equipment),
    ("🛡 Safety", "safety", safety),
]


def operations(dark: bool) -> None:
    page_header("🏭 Operations")

    available_tabs = [
        (label, renderer)
        for label, dataset, renderer in ALL_OPERATION_TABS
        if dataset in config.active_domains()
    ]

    if not available_tabs:
        st.info("No operational domains are enabled for this facility profile.")
        return

    tabs = st.tabs([label for label, _renderer in available_tabs])
    for tab, (_label, renderer) in zip(tabs, available_tabs):
        with tab:
            renderer(dark)
