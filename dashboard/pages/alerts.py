"""Alert Center with a severity filter."""

import streamlit as st

from components.alerts import alert_cards
from components.filters import ALERTS
from components.header import page_header


def alerts_page(dark: bool) -> None:
    """Render active alerts, optionally filtered to one severity."""
    del dark
    page_header("🚨 Alert Center")
    alert_data = ALERTS()
    severity_filter = st.radio(
        "Severity", ["All", "HIGH", "MEDIUM"], horizontal=True
    )

    if severity_filter != "All" and not alert_data.empty:
        alert_data = alert_data.loc[
            alert_data["severity"] == severity_filter
        ]

    alert_cards(alert_data, "alert_center")
