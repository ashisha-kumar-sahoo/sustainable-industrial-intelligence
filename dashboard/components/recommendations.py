"""Recommendation / insight panels. Moved from pages.py: the loop of recs() and the 'AI insights' / 'Recommendations' panels of overview()."""
import streamlit as st
from utils import ask_ai, drill, fname
from components.status_badges import EMO


def recommendation_cards(a):
    for _, x in a.iterrows() if len(a) else []:
        with st.container(border=True): st.markdown(f"**{EMO[x['severity']]} {x['severity']}** — {x['title']}"); st.write(f"**Recommended action:** {x['recommendation']}"); st.caption(f"Reason: {x['insight_text']}"); c1, c2, _ = st.columns([1, 1, 3]); c1.button("🔎 View raw data", key=f"rr{x['alert_id']}", on_click=drill, args=(x["source"], x["facility_id"])); c2.button("🤖 Ask AI", key=f"ra{x['alert_id']}", on_click=ask_ai, args=(f"Why is {fname(x['facility_id'])} {x['source']} high?",))
    if a.empty: st.info("No recommendations pending.")


def insights_panel(al):
    st.markdown("**AI insights** (from decision layer)"); [st.info(t) for t in (al["insight_text"].head(3) if len(al) else [])]


def recommendations_panel(al):
    st.markdown("**Recommendations**"); [st.success(f"{EMO[x['severity']]} {x['recommendation']}  ·  _{x['title']}_") for _, x in al.head(3).iterrows()]
