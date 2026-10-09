"""Shared domain panel for charts, KPIs, anomaly tables, and supporting data."""

import streamlit as st

import config
from components.charts import compare, supporting_chart, trend
from components.filters import FORECAST, RAW, RES
from components.header import page_header
from components.kpi_cards import kpis_data, render_kpis
from components.tables import (
    anomalies_table,
    bin_fill_table,
    waste_overflow_table,
)
from services import resource_service as resource
from services.operations_ml_service import (
    predict_environment,
    predict_traffic,
    predict_equipment,
    predict_safety,
)
from services.waste_service import predict_overflow


def domain(dataset: str, dark: bool) -> None:
    """Render the main analytics panel for one configured dataset."""
    label, unit, aggregation = config.KP[dataset]
    results = RES(dataset)

    if results.empty:
        st.info("No data is available for the selected filters.")
        return

    forecasts = FORECAST(dataset)
    forecast_series = resource.forecast_series(forecasts, aggregation)
    kpi = kpis_data()[dataset]
    render_kpis([kpi[:4]])

    st.plotly_chart(
        trend(
            resource.series(results, aggregation),
            forecast_series,
            dark,
            f"{label} — actual vs baseline, anomalies & 24h forecast ({unit})",
        ),
        use_container_width=True,
        theme=None,
    )

    group_by = resource.group_column(dataset)
    comparison_data = resource.latest_by_group(results, aggregation, group_by)
    comparison_column, anomaly_column = st.columns(2)
    comparison_column.plotly_chart(
        compare(
            comparison_data,
            dark,
            "Last 24h by "
            + ("zone (hotspots)" if group_by == "zone_id" else "facility"),
        ),
        use_container_width=True,
        theme=None,
    )

    with anomaly_column:
        anomalies_table(resource.latest_anomalies(results))

    raw_data = RAW(dataset) if dataset in config.EXTRA or dataset == "waste" else None

    if dataset == "waste":
        bin_fill_table(resource.bin_fill_status(results, forecasts))
        overflow_predictions, prediction_note = predict_overflow(raw_data)
        if prediction_note:
            st.info(prediction_note)
        waste_overflow_table(overflow_predictions)

    if dataset == "environment":
        st.markdown("**Environment ML checks**")
        predictions, prediction_note = predict_environment(raw_data)
        if prediction_note:
            st.info(prediction_note)
        else:
            latest_by_location = (
                predictions.sort_values("timestamp")
                .groupby("location", dropna=False)
                .tail(1)
                .sort_values("timestamp", ascending=False)
            )
            st.dataframe(
                latest_by_location[
                    [
                        column
                        for column in (
                            "timestamp",
                            "location",
                            "aqi",
                            "anomaly_status",
                            "environment_risk",
                        )
                        if column in latest_by_location.columns
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

    if dataset == "traffic":
        st.markdown("**Traffic ML checks**")
        predictions, hotspot_summary, prediction_note = predict_traffic(raw_data)
        if prediction_note:
            st.info(prediction_note)
        else:
            latest_by_location = (
                predictions.sort_values("timestamp")
                .groupby("location", dropna=False)
                .tail(1)
                .sort_values("timestamp", ascending=False)
            )
            st.dataframe(
                latest_by_location[
                    [
                        column
                        for column in (
                            "timestamp",
                            "location",
                            "vehicle_count",
                            "average_speed",
                            "occupancy",
                            "congestion_status",
                        )
                        if column in latest_by_location.columns
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )
            if hotspot_summary is not None and not hotspot_summary.empty:
                st.markdown("**Traffic hotspot summary**")
                st.dataframe(
                    hotspot_summary,
                    hide_index=True,
                    use_container_width=True,
                )

    if dataset == "equipment":
        st.markdown("**Predictive maintenance model checks**")
        predictions, prediction_note = predict_equipment(raw_data)
        if prediction_note:
            st.info(prediction_note)
        else:
            display_columns = [
                column for column in (
                    "timestamp", "location", "equipment_id", "temperature",
                    "vibration", "operating_hours", "utilization",
                    "anomaly_status", "inspection_priority",
                ) if column in predictions.columns
            ]
            st.dataframe(
                predictions[display_columns].tail(100),
                hide_index=True,
                use_container_width=True,
            )

    if dataset == "safety":
        st.markdown("**Safety risk and hotspot checks**")
        if raw_data is not None and not raw_data.empty and "synthetic_context" in raw_data.columns:
            if raw_data["synthetic_context"].fillna(False).any():
                st.caption(
                    "Synthetic incident labels/response times are illustrative, "
                    "not real incident records."
                )
        predictions, hotspot_summary, prediction_note = predict_safety(raw_data)
        if prediction_note:
            st.info(prediction_note)
        else:
            display_columns = [
                column for column in (
                    "timestamp", "location", "incident_type", "severity",
                    "people_affected", "response_time", "safety_risk",
                    "inspection_priority",
                ) if column in predictions.columns
            ]
            st.dataframe(
                predictions[display_columns].tail(100),
                hide_index=True,
                use_container_width=True,
            )
            if hotspot_summary is not None and not hotspot_summary.empty:
                st.markdown("**Potential safety hotspots**")
                st.dataframe(hotspot_summary, hide_index=True, use_container_width=True)

    if dataset in config.EXTRA:
        available_columns = [
            column for column in config.EXTRA[dataset] if column in raw_data.columns
        ]
        if not raw_data.empty and available_columns:
            st.plotly_chart(
                supporting_chart(
                    resource.supporting_metrics(raw_data, available_columns),
                    available_columns,
                    dark,
                ),
                use_container_width=True,
                theme=None,
            )
