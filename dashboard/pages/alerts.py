"""Alert Center page. Moved from pages.alerts_page."""
import streamlit as st
from components.alerts import alert_cards
from components.filters import ALERTS
from components.header import page_header


def alerts_page(dark):
    page_header("🚨 Alert Center"); a = ALERTS(); f = st.radio("Severity", ["All", "HIGH", "MEDIUM"], horizontal=True); alert_cards(a if f == "All" or a.empty else a[a["severity"] == f], "al")
