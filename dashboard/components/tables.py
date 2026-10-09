"""Tables for anomaly details, waste-bin status, and domain scorecards."""

import streamlit as st


def anomalies_table(data) -> None:
    """Show the most recent anomaly rows, or a friendly empty-state message."""
    st.markdown("**Recent anomalies**")
    if data is None or data.empty:
        st.info("No anomalies in the selected period.")
        return

    columns = [
        column
        for column in (
            "timestamp",
            "facility_id",
            "actual_value",
            "expected_value",
            "deviation_pct",
            "severity",
        )
        if column in data.columns
    ]
    st.dataframe(data[columns], hide_index=True, use_container_width=True)


def bin_fill_table(data) -> None:
    """Show current and predicted fill level for waste bins."""
    st.markdown("**Waste-bin fill status**")
    if data is None or data.empty:
        st.info("No waste-bin fill readings are available.")
        return

    st.dataframe(data, hide_index=True, use_container_width=True)


def scorecard_table(data) -> None:
    """Display a domain scorecard without an index column."""
    st.dataframe(data, hide_index=True, use_container_width=True)


def raw_data_table(data, columns, page_number, page_size, dataset) -> None:
    """Display one page of raw rows and offer a CSV download of all filtered rows."""
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    st.dataframe(
        data[columns].iloc[start_index:end_index],
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "⬇ Download CSV",
        data[columns].to_csv(index=False),
        file_name=f"{dataset}.csv",
        mime="text/csv",
    )


def waste_overflow_table(predictions) -> None:
    """Display the latest six-hour bin overflow estimates."""
    st.markdown("**AI waste-bin overflow estimate (next 6 hours)**")
    if predictions is None or predictions.empty:
        st.info("No usable waste telemetry is available for overflow estimation.")
        return

    visible_columns = [
        column
        for column in (
            "facility_id",
            "sensor_id",
            "reading_ts",
            "fill_level_percent",
            "fill_rate_percent_per_hour",
            "predicted_fill_level_percent",
            "overflow_risk",
            "overflow_probability",
            "prediction_method",
        )
        if column in predictions.columns
    ]
    st.dataframe(
        predictions[visible_columns],
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "The normalized overflow score is not a calibrated probability. "
        "The Random Forest is used only when enough per-bin future observations "
        "are available; otherwise the model uses a transparent fill-rate projection."
    )
