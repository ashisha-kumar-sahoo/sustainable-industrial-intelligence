"""Alert cards UI. alert_cards moved from pages.py (markup unchanged); drill/ask_ai callbacks now come from utils."""
import streamlit as st
from utils import ask_ai, drill, fname
from components.status_badges import EMO, alert_class


def alert_cards(a, key):
    if a is None or a.empty: st.info("No active alerts for the selected filters."); return
    for _, x in a.iterrows():
        st.markdown(f'<div class="alert {alert_class(x["severity"])}"><b>{EMO[x["severity"]]} {x["severity"]} — {x["title"]}</b><br><small>{x["source"]} · {x["status"]}</small><p>{x["insight_text"]}</p><i>Evidence: actual {x["evidence_actual"]} vs expected {x["evidence_expected"]} · Action: {x["recommendation"]}</i></div>', unsafe_allow_html=True)
        c1, c2, _ = st.columns([1, 1, 3]); c1.button("🔎 View raw data", key=f"{key}r{x['alert_id']}", on_click=drill, args=(x["source"], x["facility_id"])); c2.button("🤖 Ask AI", key=f"{key}a{x['alert_id']}", on_click=ask_ai, args=(f"Why is {fname(x['facility_id'])} {x['source']} high?",))
