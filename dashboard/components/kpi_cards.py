"""KPI cards. kpi_html moved unchanged from pages.py; kpis_data is the loop of pages.kpis_data (per-dataset maths now in services.resource_service.kpi_for)."""
import streamlit as st
from config import KP
from components.filters import RES
from components.status_badges import SEVERITY_CLASS, badge
from services.resource_service import kpi_for


def kpis_data():
    return {ds: kpi_for(ds, RES(ds)) for ds in KP}


def kpi_html(cards): return '<div class="kg">' + "".join(f'<div class="kpi s-{SEVERITY_CLASS[sv]}"><small>{l}</small><b>{v}</b><i>{d} · {badge(sv)}</i></div>' for l, v, d, sv in cards) + "</div>"


def render_kpis(cards): st.markdown(kpi_html(cards), unsafe_allow_html=True)
