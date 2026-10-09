"""Plotly figure builders used throughout the dashboard."""

import plotly.express as px
import plotly.graph_objects as go


GRID_COLOR = "rgba(148, 163, 184, 0.2)"


def apply_layout(figure, dark: bool, title: str, height: int = 340):
    """Apply the shared transparent background, typography, and grid styling."""
    text_color = "#e2e8f0" if dark else "#0f172a"
    figure.update_layout(
        title={
            "text": title,
            "x": 0,
            "xanchor": "left",
            "y": 0.96,
            "font": {"size": 16},
        },
        height=height + 60,
        margin={"l": 10, "r": 10, "t": 60, "b": 70},
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font={"color": text_color},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "left",
            "x": 0,
        },
    )
    figure.update_xaxes(gridcolor=GRID_COLOR)
    figure.update_yaxes(gridcolor=GRID_COLOR)
    return figure


def trend(series, forecast, dark: bool, title: str):
    """Plot actual values, the baseline, detected anomalies, and forecasts."""
    figure = go.Figure()
    figure.add_scatter(
        x=series["timestamp"],
        y=series["actual"],
        name="Actual",
        line={"color": "#00e5ff", "width": 2},
    )
    figure.add_scatter(
        x=series["timestamp"],
        y=series["expected"],
        name="Baseline",
        line={"color": "#94a3b8", "dash": "dash"},
    )

    anomalies = series.loc[series["anom"]]
    figure.add_scatter(
        x=anomalies["timestamp"],
        y=anomalies["actual"],
        name="Anomaly",
        mode="markers",
        marker={
            "color": "#ff2d55",
            "size": 10,
            "line": {"color": "white", "width": 1},
        },
    )

    if forecast is not None and not forecast.empty:
        figure.add_scatter(
            x=forecast["timestamp"],
            y=forecast["forecast"],
            name="Forecast",
            line={"color": "#a3ff12", "dash": "dot", "width": 2},
        )

    return apply_layout(figure, dark, title)


def compare(data, dark: bool, title: str):
    """Compare actual and baseline values across facilities or zones."""
    figure = go.Figure(
        data=[
            go.Bar(
                x=data["label"],
                y=data["actual"],
                name="Actual",
                marker_color="#00e5ff",
            ),
            go.Bar(
                x=data["label"],
                y=data["expected"],
                name="Baseline",
                marker_color="#94a3b8",
            ),
        ]
    )
    figure.update_layout(barmode="group")
    return apply_layout(figure, dark, title)


def supporting_chart(data, columns: list[str], dark: bool):
    """Plot optional supporting metrics such as AQI components or speed."""
    figure = px.line(data, x="timestamp", y=columns)
    return apply_layout(figure, dark, "Supporting metrics (mean)")
