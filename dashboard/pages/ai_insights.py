"""AI Assistant and Recommendations pages (the two AI-decision-layer views). Moved from pages.assistant and pages.recs."""
import streamlit as st
from components.filters import ALERTS
from components.header import page_header
from components.recommendations import recommendation_cards
from services.ai_service import ask
from utils import safe


def assistant(dark):
    page_header("💬 Facility AI Assistant"); st.caption("Answers come from Member 6's decision service (ASSISTANT_URL). The dashboard only displays them.")
    q = st.text_input("Ask a question", key="aq", placeholder="Why is Factory B's energy high?"); h = st.session_state.setdefault("hist", [])
    if st.button("ASK AI", type="primary") and q:
        with st.spinner("Asking…"): r = safe(ask, q, default=None, label="AI Assistant")
        if r: h.insert(0, (q, r))
    for q_, r in h:
        with st.container(border=True): st.markdown(f"**Admin:** {q_}"); st.markdown(f"**AI:** {r.get('answer', '')}"); r.get("evidence") and st.caption("Evidence: " + str(r["evidence"])); r.get("sample") and st.caption("⚠️ Sample answer: Member 6 assistant service not connected.")


def recs(dark):
    page_header("✅ Recommendations"); recommendation_cards(ALERTS())
