"""AI Assistant and recommendation dashboard pages."""
import streamlit as st
from components.filters import ALERTS
from components.header import page_header
from components.recommendations import recommendation_cards
from services.ai_service import ask
from utils import safe


def assistant(dark):
    page_header("💬 Facility AI Assistant")
    st.caption("Answers come from Member 6's decision service. The dashboard only displays them.")
    q = st.text_input(
        "Ask a question",
        key="aq",
        placeholder="Why is Factory B's energy high?",
    )
    history = st.session_state.setdefault("hist", [])
    if st.button("ASK AI", type="primary") and q:
        with st.spinner("Asking…"):
            result = safe(ask, q, default=None, label="AI Assistant")
        if result:
            history.insert(0, (q, result))

    for question, result in history:
        with st.container(border=True):
            st.markdown(f"**Admin:** {question}")
            answer = result.get("natural_language_response") or result.get("answer", "")
            if isinstance(answer, dict):
                answer = answer.get("text") or answer.get("summary") or str(answer)
            st.markdown(f"**AI:** {answer}")
            evidence = result.get("evidence")
            if evidence:
                st.caption("Evidence: " + str(evidence))
            errors = result.get("errors") or []
            if errors:
                st.caption("Service note: " + str(errors[-1].get("message", errors[-1])))
            if result.get("sample"):
                st.caption("⚠️ Fallback answer: Member 6 assistant service is not connected.")


def recs(dark):
    page_header("✅ Recommendations")
    recommendation_cards(ALERTS())
