"""Raw Data Explorer page. Moved from pages.rawdata (final table + CSV download now in components.tables.raw_data_table)."""
import streamlit as st
import config
from components.filters import RAW
from components.header import page_header
from components.tables import raw_data_table


def rawdata(dark):
    page_header("📁 Raw Data Explorer"); st.caption("Evidence behind dashboard/AI results. Use the global filters in the sidebar (facility, zone, dates).")
    a, b, c = st.columns(3); ds = a.selectbox("Dataset", list(config.DS), key="rx_ds"); q = b.text_input("Search"); size = c.selectbox("Rows per page", [25, 50, 100], index=1); d = RAW(ds)
    if q and len(d): d = d[d.astype(str).apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
    if d.empty: st.info("No records for the selected filters."); return
    cols = st.multiselect("Columns", list(d.columns), default=list(d.columns)); s1, s2 = st.columns(2); sk = s1.selectbox("Sort by", cols or list(d.columns)); asc = s2.toggle("Ascending"); d = d.sort_values(sk, ascending=asc)
    pages = max(1, -(-len(d) // size)); p = st.number_input(f"Page (1–{pages})", 1, pages, 1); st.caption(f"{len(d):,} records · showing {size} per page")
    raw_data_table(d, cols, p, size, ds)
