"""Global filters (Facility / Zone / Date range) and the filtered data accessors that apply them.
Moved from app.py (the three sidebar widgets) and pages.py (filt, RES, RAW, ALERTS). Filter state lives in
st.session_state keys g_fac, g_zone, g_dates, exactly as before."""
import datetime
import pandas as pd
import streamlit as st
import config
from utils import fid, safe
from services.database_service import forecast, raw, results
from services.alert_service import alerts


def render_sidebar_filters():
    fac = st.selectbox("Facility", ["All"] + config.FAC["name"].tolist(), key="g_fac"); zs = config.ZONES if fac == "All" else config.FAC.loc[config.FAC["name"] == fac, "zones"].iloc[0]
    if st.session_state.get("g_zone", "All") not in ["All"] + zs: st.session_state.g_zone = "All"
    st.selectbox("Zone", ["All"] + zs, key="g_zone"); today = datetime.date.today(); st.date_input("Date range", (today - datetime.timedelta(days=6), today), key="g_dates")


def filt(df, dates=True):
    s = st.session_state; f, z, d = s.get("g_fac", "All"), s.get("g_zone", "All"), s.get("g_dates")
    if df is None or df.empty: return pd.DataFrame()
    if f != "All": df = df[df["facility_id"] == fid(f)]
    if z != "All": df = df[df["zone_id"] == z]
    if dates and d and len(d) == 2: df = df[(df["timestamp"].dt.date >= d[0]) & (df["timestamp"].dt.date <= d[1])]
    return df


def RES(ds): return filt(safe(results, ds, default=pd.DataFrame(), label=f"{ds} AI results"))
def RAW(ds, limit=5000):
    s = st.session_state; d = s.get("g_dates") or (None, None); f, z = s.get("g_fac", "All"), s.get("g_zone", "All")
    return safe(raw, ds, fid(f) if f != "All" else None, z if z != "All" else None, d[0] if len(d) > 0 else None, d[1] if len(d) > 1 else None, limit, default=pd.DataFrame(), label=f"{ds} raw data")
def ALERTS(): return filt(safe(alerts, default=pd.DataFrame(), label="Alerts"), dates=False)
def FORECAST(ds, label=None):
    """Filtered forecast frame (date filter not applied), as pages used: filt(safe(S.forecast, ...), dates=False)."""
    return filt(safe(forecast, ds, default=pd.DataFrame(), **({"label": label} if label else {})), dates=False)
