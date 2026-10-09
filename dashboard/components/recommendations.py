"""Recommendation and decision-insight panels."""

import streamlit as st

from components.status_badges import EMO
from utils import ask_ai, drill, fname


def recommendation_cards(alert_data) -> None:
    """Render alert recommendations with shortcuts to evidence and the AI helper."""
    if alert_data is None or alert_data.empty:
        st.info("No recommendations are pending.")
        return

    for _, alert in alert_data.iterrows():
        severity = str(alert.get("severity", "UNKNOWN")).upper()
        facility_id = alert.get("facility_id")
        dataset = alert.get("source", "unknown")

        with st.container(border=True):
            st.markdown(
                f"**{EMO.get(severity, EMO['UNKNOWN'])} {severity}** — "
                f"{alert.get('title', 'Operational alert')}"
            )
            st.write(f"**Recommended action:** {alert.get('recommendation', 'Review the evidence.')}")
            st.caption(f"Reason: {alert.get('insight_text', 'No explanation was provided.')}")

            raw_column, assistant_column, _spacer = st.columns([1, 1, 3])
            raw_column.button(
                "🔎 View raw data",
                key=f"recommendation_raw_{alert.get('alert_id', facility_id)}",
                on_click=drill,
                args=(dataset, facility_id),
            )
            assistant_column.button(
                "🤖 Ask AI",
                key=f"recommendation_ai_{alert.get('alert_id', facility_id)}",
                on_click=ask_ai,
                args=(f"Why is {fname(facility_id)} {dataset} high?",),
            )


def insights_panel(alert_data) -> None:
    """Display up to three plain-language insights."""
    st.markdown("**AI insights** (from the decision layer)")
    if alert_data is None or alert_data.empty:
        st.info("No current insights are available.")
        return

    for insight in alert_data["insight_text"].head(3):
        st.info(insight)


def recommendations_panel(alert_data) -> None:
    """Display up to three prioritized recommended actions."""
    st.markdown("**Recommendations**")
    if alert_data is None or alert_data.empty:
        st.info("No recommendations are available.")
        return

    for _, alert in alert_data.head(3).iterrows():
        severity = str(alert.get("severity", "UNKNOWN")).upper()
        icon = EMO.get(severity, EMO["UNKNOWN"])
        st.success(
            f"{icon} {alert.get('recommendation', 'Review the evidence.')} "
            f"· _{alert.get('title', 'Operational alert')}_"
        )
