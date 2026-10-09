"""Alert cards with shortcuts to supporting raw data and the AI assistant."""

import html

import streamlit as st

from components.status_badges import EMO, alert_class
from utils import ask_ai, drill, fname


def alert_cards(alert_data, key_prefix: str) -> None:
    """Render alert cards and their evidence/action controls."""
    if alert_data is None or alert_data.empty:
        st.info("No active alerts for the selected filters.")
        return

    for _, alert in alert_data.iterrows():
        severity = str(alert.get("severity", "UNKNOWN")).upper()
        icon = EMO.get(severity, EMO["UNKNOWN"])
        title = html.escape(str(alert.get("title", "Operational alert")))
        source = html.escape(str(alert.get("source", "unknown")))
        status = html.escape(str(alert.get("status", "Open")))
        insight = html.escape(str(alert.get("insight_text", "No explanation provided.")))
        actual = html.escape(str(alert.get("evidence_actual", "unavailable")))
        expected = html.escape(str(alert.get("evidence_expected", "unavailable")))
        recommendation = html.escape(
            str(alert.get("recommendation", "Review the evidence."))
        )

        card_html = (
            f'<div class="alert {alert_class(severity)}">'
            f"<b>{icon} {severity} — {title}</b>"
            f"<br><small>{source} · {status}</small>"
            f"<p>{insight}</p>"
            f"<i>Evidence: actual {actual} vs expected {expected} · "
            f"Action: {recommendation}</i></div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)

        facility_id = alert.get("facility_id")
        alert_id = alert.get("alert_id", facility_id)
        raw_column, assistant_column, _spacer = st.columns([1, 1, 3])
        raw_column.button(
            "🔎 View raw data",
            key=f"{key_prefix}_raw_{alert_id}",
            on_click=drill,
            args=(alert.get("source", "unknown"), facility_id),
        )
        assistant_column.button(
            "🤖 Ask AI",
            key=f"{key_prefix}_ai_{alert_id}",
            on_click=ask_ai,
            args=(f"Why is {fname(facility_id)} {source} high?",),
        )
