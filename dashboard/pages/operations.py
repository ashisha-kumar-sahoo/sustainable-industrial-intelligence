"""Operations page: tabs Traffic / Equipment / Safety. Moved from pages.operations; each tab body lives in its own page module."""
import streamlit as st
from components.header import page_header
from pages.equipment import equipment
from pages.safety import safety
from pages.traffic import traffic


def operations(dark):
    page_header("🏭 Operations"); t = st.tabs(["🚚 Traffic", "⚙️ Equipment", "🛡 Safety"])
    for tab, fn in zip(t, [traffic, equipment, safety]):
        with tab: fn(dark)
