"""Small reusable helpers shared by components, pages and services (no business logic).
Moved from: data_service.py (fid, fname, _post), pages.py (safe, drill, ask_ai, nav)."""
import json, urllib.request
import streamlit as st
from config import FAC


def fid(n): return FAC.loc[FAC["name"] == n, "facility_id"].iloc[0]       # facility name -> id
def fname(i): return FAC.loc[FAC["facility_id"] == i, "name"].iloc[0]     # facility id -> name


def post_json(url, body):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"}); return json.load(urllib.request.urlopen(req, timeout=15))


def safe(fn, *a, default=None, label=""):
    try: return fn(*a)
    except Exception as e: st.warning(f"⚠️ {label or fn.__name__} is temporarily unavailable ({type(e).__name__}). The rest of the dashboard still works."); return default


def drill(ds, fid):
    s = st.session_state; s.page, s.rx_ds, s.g_fac, s.g_zone = "Raw Data Explorer", ds, fname(fid), "All"
def ask_ai(q): st.session_state.page, st.session_state.aq = "AI Assistant", q
def nav(p): st.session_state.page = p
