"""Restrained presentation components and honest number formats."""

import math

import plotly.graph_objects as go
import streamlit as st

from pulse.metrics.registry import REGISTRY

PAGES = [
    "Executive Overview",
    "Investigate",
    "Alerts",
    "Forecast",
    "Scenario Lab",
    "Customers",
    "Operations",
    "Ask PULSE",
    "Executive Brief",
    "Data Quality",
    "Methodology",
]


def money(value):
    return (
        f"{'-' if value < 0 else ''}A${abs(value):,.0f}" if math.isfinite(value) else "Unavailable"
    )


def display(key, value):
    unit = REGISTRY[key].unit if key in REGISTRY else "count"
    if not math.isfinite(value):
        return "Unavailable"
    return (
        money(value)
        if unit == "AUD"
        else (
            f"{value:.1%}"
            if unit == "ratio"
            else f"{value:,.1f}"
            if unit == "score"
            else f"{value:,.0f}"
        )
    )


def caption(text):
    st.caption(text.replace("$", "\\$"))


def header(title, description):
    caption("WATTLE & RYE  /  SYNTHETIC BUSINESS  /  DECISION INTELLIGENCE")
    st.title(title)
    st.markdown(description)


def metrics(current, before=None, keys=None):
    keys = keys or ["revenue", "operating_profit", "operating_margin", "transactions"]
    for column, key in zip(st.columns(len(keys)), keys):
        delta = None
        if before is not None:
            difference = current[key] - before[key]
            delta = (
                f"{difference * 100:+.1f} pp"
                if REGISTRY[key].unit == "ratio"
                else display(key, difference)
            )
        column.metric(
            REGISTRY[key].name,
            display(key, current[key]),
            delta,
            delta_color="inverse"
            if key in ["labour_pct", "refund_rate", "stockout_rate"]
            else "normal",
        )


def chart(figure, title, explanation):
    figure.update_layout(
        title=title,
        height=350,
        margin=dict(l=10, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#172B3D"),
        colorway=["#007C83", "#9B4A37", "#486A92"],
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(figure, use_container_width=True)
    caption(explanation)


def line(frame, x, y, label):
    return go.Figure(
        go.Scatter(x=frame[x], y=frame[y], mode="lines", name=label, line=dict(width=2.5))
    )


def table(frame):
    st.dataframe(frame, use_container_width=True, hide_index=True)


def style():
    st.markdown(
        """<style>
    .block-container {padding-top:3.8rem;max-width:1320px}
    h1 {font-weight:700;letter-spacing:-1.1px;font-size:2.5rem}
    h2 {font-size:1.45rem;letter-spacing:-.4px}
    h3 {font-size:1.15rem}
    [data-testid='stMetric'] {background:#fff;border:1px solid #d7e1e8;border-top:3px solid #007C83;border-radius:10px;padding:18px 16px;margin:8px 0 20px}
    [data-testid='stMetricValue'] {font-size:1.8rem}
    [data-testid='stSidebar'] {border-right:1px solid #d7e1e8}
    [data-testid='stCaptionContainer'] {color:#435B6C}
    </style>""",
        unsafe_allow_html=True,
    )
