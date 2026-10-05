"""Sustainable Industrial Intelligence - dashboard entry point.  Run:  cd dashboard && streamlit run app.py
Responsibilities: page config, theme + styles, login gate, sidebar, routing to the page modules. Everything else lives in
config.py / styles.py / utils.py, components/, pages/ and services/ (see README.md)."""
import streamlit as st
import config
from styles import apply_styles
from components.header import render_login
from components.sidebar import render_sidebar
from pages.overview import overview
from pages.resources import resources
from pages.environment import environment
from pages.operations import operations
from pages.alerts import alerts_page
from pages.ai_insights import assistant, recs
from pages.simulation import simulation
from pages.raw_data import rawdata

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout=config.APP_LAYOUT)
dark = not st.session_state.get("light_mode", False)   # theme: light_mode False = dark (default), True = light
apply_styles(dark)
if not st.session_state.get("user"): render_login(dark); st.stop()
PAGES = {"Overview": overview, "Resources": resources, "Environment": environment, "Operations": operations, "Alerts": alerts_page, "AI Assistant": assistant, "Recommendations": recs, "Scenario Simulation": simulation, "Raw Data Explorer": rawdata}
st.session_state.setdefault("page", "Overview")
render_sidebar(list(PAGES), dark)
try: PAGES[st.session_state.page](dark)
except Exception as e: st.error(f"This page could not be displayed ({type(e).__name__}: {e}). Other pages still work.")
