"""Streamlit entry point for Sustainable Industrial Intelligence.

Run this module from the dashboard directory with:
    streamlit run app.py

Page rendering is delegated to the page modules. Data access and business
logic live in the service modules so they can be tested independently.
"""

from __future__ import annotations

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

# Put the dashboard first so ``import config`` resolves to dashboard/config.py.
# Keep the project root available for shared packages such as ai and ml.
for project_path in (ROOT_DIR, DASHBOARD_DIR):
    if project_path not in sys.path:
        sys.path.insert(0, project_path)

import streamlit as st

import config
from components.header import render_login
from components.sidebar import render_sidebar
from pages.ai_insights import assistant, recs
from pages.alerts import alerts_page
from pages.environment import environment
from pages.operations import operations
from pages.overview import overview
from pages.raw_data import rawdata
from pages.resources import resources
from pages.simulation import simulation
from styles import apply_styles


PAGES = {
    "Overview": overview,
    "Resources": resources,
    "Environment": environment,
    "Operations": operations,
    "Alerts": alerts_page,
    "AI Assistant": assistant,
    "Recommendations": recs,
    "Scenario Simulation": simulation,
    "Raw Data Explorer": rawdata,
}


st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
)

# ``light_mode`` is False by default, so the dashboard starts in dark mode.
dark_mode = not st.session_state.get("light_mode", False)
apply_styles(dark_mode)

if not st.session_state.get("user"):
    render_login(dark_mode)
    st.stop()

st.session_state.setdefault("page", "Overview")
render_sidebar(list(PAGES), dark_mode)

selected_page = st.session_state.get("page", "Overview")
page_renderer = PAGES.get(selected_page, overview)

try:
    page_renderer(dark_mode)
except Exception as exc:
    # Keep a single page failure from crashing the rest of the dashboard.
    st.error(
        "This page could not be displayed "
        f"({type(exc).__name__}: {exc}). Other pages may still work."
    )
