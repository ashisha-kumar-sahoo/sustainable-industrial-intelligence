"""Sidebar branding, role-filtered navigation, filters, and account controls."""

import html

import streamlit as st

import config
from components.filters import render_sidebar_filters
from components.header import theme_switch
from utils import nav


ROLE_PAGES = {
    "OPERATIONS": [
        "Overview",
        "Resources",
        "Environment",
        "Operations",
        "Alerts",
        "AI Assistant",
        "Scenario Simulation",
        "Raw Data Explorer",
    ],
    "SUSTAINABILITY": [
        "Overview",
        "Resources",
        "Environment",
        "Alerts",
        "AI Assistant",
        "Recommendations",
        "Scenario Simulation",
        "Raw Data Explorer",
    ],
}


def render_sidebar(page_names: list[str], dark: bool) -> None:
    """Render navigation and filters for the logged-in user."""
    with st.sidebar:
        st.markdown(
            '<div class="sb-brand"><div class="sb-logo">🏭</div>'
            '<div class="sb-title">Sustainable Industrial<br>Intelligence</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sb-sep"></div><div class="sb-sec"></div>',
            unsafe_allow_html=True,
        )

        user = st.session_state.user
        role = str(user.get("role", "OPERATIONS")).upper()
        allowed_pages = ROLE_PAGES.get(role, page_names) if role != "ADMIN" else page_names
        allowed_pages = [page for page in allowed_pages if page in page_names]

        if not allowed_pages:
            allowed_pages = ["Overview"] if "Overview" in page_names else page_names
        if st.session_state.get("page") not in allowed_pages:
            st.session_state.page = allowed_pages[0]

        with st.container(key="nav"):
            for index, page_name in enumerate(allowed_pages):
                st.button(
                    f"{config.NAV_ICONS.get(page_name, '•')}  {page_name}",
                    key=f"nav_{index}",
                    type=(
                        "primary"
                        if st.session_state.page == page_name
                        else "secondary"
                    ),
                    use_container_width=True,
                    on_click=nav,
                    args=(page_name,),
                )

        st.markdown(
            '<div class="sb-sep"></div><div class="sb-sec"></div>',
            unsafe_allow_html=True,
        )
        render_sidebar_filters()

        profile_names = list(config.FACILITY_PROFILES)
        current_profile = config.current_profile()
        profile_index = (
            profile_names.index(current_profile)
            if current_profile in profile_names
            else 0
        )
        selected_profile = st.selectbox(
            "Facility profile",
            profile_names,
            index=profile_index,
            key="facility_profile",
            help=(
                "The same dashboard architecture can be configured for an "
                "industrial estate or a hospital."
            ),
        )

        previous_profile = st.session_state.get("_last_facility_profile")
        if previous_profile != selected_profile:
            st.cache_data.clear()
            st.session_state["_last_facility_profile"] = selected_profile

        profile = config.FACILITY_PROFILES[selected_profile]
        st.caption(f"{profile['icon']} {profile['description']}")
        st.caption(f"Data mode: {config.MODE}")
        st.caption(f"Role: {role.title()}")
        st.markdown(
            '<div class="sb-user">👤 '
            + html.escape(str(user.get("full_name", "User")))
            + "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
            div[data-testid="stButton"]:has(button[kind="secondary"]) {
                margin-top: 0px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if st.button("↪ Logout", key="sidebar_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown('<div class="sb-sep"></div>', unsafe_allow_html=True)
        theme_switch("side", dark)
