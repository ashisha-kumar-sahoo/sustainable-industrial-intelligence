"""Sidebar: brand, theme switch, navigation buttons, global filters, data-mode caption, user name and logout.
Moved from app.py (the `with st.sidebar:` block). `go` was a duplicate of utils.nav and is replaced by it."""
import html
import streamlit as st
import config
from utils import nav
from components.filters import render_sidebar_filters
from components.header import theme_switch


def render_sidebar(page_names, dark):
    with st.sidebar:
        st.markdown('<div class="sb-brand"><div class="sb-logo">🏭</div><div class="sb-title">Sustainable Industrial<br>Intelligence</div></div>', unsafe_allow_html=True);
        st.markdown('<div class="sb-sep"></div><div class="sb-sec"></div>', unsafe_allow_html=True)
        with st.container(key="nav"):
            for i, p in enumerate(page_names): st.button(config.NAV_ICONS[p] + "  " + p, key=f"nav_{i}", type="primary" if st.session_state.page == p else "secondary", use_container_width=True, on_click=nav, args=(p,))
        st.markdown('<div class="sb-sep"></div><div class="sb-sec"></div>', unsafe_allow_html=True)
        render_sidebar_filters()
        st.caption(f"Data mode: {config.MODE}")
        st.markdown('<div class="sb-user">👤 ' + html.escape(st.session_state.user["full_name"]) + '</div>', unsafe_allow_html=True)
        st.markdown("""
                <style>
                div[data-testid="stButton"]:has(button[kind="secondary"]){margin-top: 0px !importnt;}
                </style>""", unsafe_allow_html=True)
        if st.button("↪ Logout", key="sidebar_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown('<div class="sb-sep"></div>', unsafe_allow_html=True)
        theme_switch("side", dark)
