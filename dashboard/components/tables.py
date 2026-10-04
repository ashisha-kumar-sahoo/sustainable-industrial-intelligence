"""Table renderers. Moved from pages.py: the anomalies / waste-bin / scorecard / raw-data tables (arguments and options unchanged)."""
import streamlit as st

ANOMALY_COLS = ["timestamp", "facility_id", "zone_id", "actual_value", "expected_value", "deviation_pct", "severity"]


def anomalies_table(an):
    st.markdown("**Latest anomalies**"); st.dataframe(an[ANOMALY_COLS], hide_index=True, use_container_width=True) if len(an) else st.success("No anomalies in range.")


def bin_fill_table(cur):
    st.markdown("**Bin fill: current vs predicted**"); st.dataframe(cur.round(0), hide_index=True, use_container_width=True)


def scorecard_table(df): st.dataframe(df, hide_index=True, use_container_width=True)


def raw_data_table(d, cols, p, size, ds):
    st.dataframe(d[cols].iloc[(p - 1) * size:p * size], hide_index=True, use_container_width=True); st.download_button("⬇ Download CSV", d[cols].to_csv(index=False), f"{ds}.csv", "text/csv")
