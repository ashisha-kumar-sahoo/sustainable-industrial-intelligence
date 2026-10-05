"""Plotly figure builders. Moved unchanged from charts.py (_lay -> apply_layout, trend, compare);
supporting_chart is the figure part of the 'Supporting metrics' block from pages.domain()."""
import plotly.graph_objects as go, plotly.express as px


def apply_layout(f, dark, title, h=340):
    t = "#e2e8f0" if dark else "#0f172a"; f.update_layout(title=dict(text=title, x=0, xanchor="left", y=.96, font=dict(size=16)), height=h + 60, margin=dict(l=10, r=10, t=60, b=70), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=t), legend=dict(orientation="h", yanchor="top", y=-.2, xanchor="left", x=0))
    f.update_xaxes(gridcolor="rgba(148,163,184,.2)"); f.update_yaxes(gridcolor="rgba(148,163,184,.2)"); return f
def trend(s, fc, dark, title):
    f = go.Figure(); f.add_scatter(x=s["timestamp"], y=s["actual"], name="Actual", line=dict(color="#00e5ff", width=2))
    f.add_scatter(x=s["timestamp"], y=s["expected"], name="Baseline", line=dict(color="#94a3b8", dash="dash"))
    a = s[s["anom"]]; f.add_scatter(x=a["timestamp"], y=a["actual"], name="Anomaly", mode="markers", marker=dict(color="#ff2d55", size=10, line=dict(color="white", width=1)))
    if fc is not None and len(fc): f.add_scatter(x=fc["timestamp"], y=fc["forecast"], name="Forecast", line=dict(color="#a3ff12", dash="dot", width=2))
    return apply_layout(f, dark, title)
def compare(d, dark, title):
    f = go.Figure([go.Bar(x=d["label"], y=d["actual"], name="Actual", marker_color="#00e5ff"), go.Bar(x=d["label"], y=d["expected"], name="Baseline", marker_color="#94a3b8")]); f.update_layout(barmode="group"); return apply_layout(f, dark, title)


def supporting_chart(df, cols, dark):
    return apply_layout(px.line(df, x="timestamp", y=cols), dark, "Supporting metrics (mean)")
