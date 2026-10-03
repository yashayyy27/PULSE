"""PULSE's central presentation vocabulary and accessible native controls."""

from dataclasses import asdict
from html import escape
import math
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from pulse.metrics.registry import REGISTRY

ACCENT = "#00D2BE"
SILVER = "#C7CDD1"
WARNING = "#EBC17A"
CRITICAL = "#F29595"


def money(value):
    return (
        f"{'−' if value < 0 else ''}A${abs(value):,.0f}" if math.isfinite(value) else "Unavailable"
    )


def display(key, value):
    if not math.isfinite(value):
        return "Unavailable"
    unit = REGISTRY[key].unit if key in REGISTRY else "count"
    return (
        money(value)
        if unit == "AUD"
        else f"{value:.1%}"
        if unit == "ratio"
        else f"{value:,.1f}"
        if unit == "score"
        else f"{value:,.0f}"
    )


def delta(key, value):
    if not math.isfinite(value):
        return "Unavailable"
    if REGISTRY[key].unit == "ratio" and round(value * 100, 1) == 0:
        return "0.0 pp"
    return (
        f"{value * 100:+.1f} pp"
        if REGISTRY[key].unit == "ratio"
        else ("+" if value > 0 else "") + display(key, value)
    )


def caption(text):
    st.caption(str(text).replace("$", "\\$"))


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def label(text):
    html(f'<div class="eyebrow">{escape(text)}</div>')


def header(title, description, eyebrow="DECISION INTELLIGENCE"):
    label(eyebrow)
    st.title(title)
    st.markdown(description.replace("$", "\\$"))


def section(number, title, description=None):
    html(
        f'<div class="section-title"><span>{escape(str(number))}</span><h2>{escape(title)}</h2></div>'
    )
    if description:
        caption(description)


def status(text):
    kind = "critical" if text == "CRITICAL" else "warning" if text == "WARNING" else "neutral"
    return f'<span class="status {kind}">{escape(text)}</span>'


def metric(key, value, subtext="", large=False):
    html(
        f'<div class="metric-display {"large" if large else ""}"><div class="eyebrow">{escape(REGISTRY[key].name)}</div><div class="figure">{escape(display(key, value))}</div><div class="support">{escape(subtext)}</div></div>'
    )


def metrics(current, before=None, keys=None):
    keys = keys or ["revenue", "operating_profit", "operating_margin", "transactions"]
    for column, key in zip(st.columns(len(keys)), keys):
        with column:
            metric(
                key,
                current[key],
                delta(key, current[key] - before[key]) + " vs previous period"
                if before
                else "Observed · synthetic",
            )


def narrative(statement, supporting="", tag="OBSERVED"):
    statement = statement.replace("A$-", "−A$")
    html(
        f'<div class="narrative"><div class="eyebrow">{escape(tag)}</div><p>{escape(statement)}</p><div class="support">{escape(supporting)}</div></div>'
    )


def signal_summary(row, index=None, selected=False, compact=False):
    prefix = f'<span class="signal-number">{index:02d}</span>' if index is not None else ""
    exposure = (
        money(row["estimated_profit_exposure"])
        if row["estimated_profit_exposure"] > 0
        else "No monetary estimate"
    )
    statement = (
        ""
        if compact
        else f"<h3>{escape(REGISTRY[row['kpi']].name)} moved outside its recent reference range.</h3>"
    )
    html(
        f"""<div class="signal-summary {"selected" if selected else ""}">{prefix}<div class="signal-body"><div class="eyebrow">{escape(row["entity"])} · {escape(REGISTRY[row["kpi"]].name)} {status(row["severity"])}</div>{statement}<div class="signal-values"><span><small>ACTUAL</small>{escape(display(row["kpi"], row["actual"]))}</span><span><small>8-WEEK MEDIAN</small>{escape(display(row["kpi"], row["baseline"]))}</span><span><small>ESTIMATED EXPOSURE</small>{escape(exposure)}</span></div><div class="support">Week ending {escape(row["timestamp"])} · {escape(delta(row["kpi"], row["variance"]))} from median · reference gap, not achieved savings</div></div></div>"""
    )


def evidence(text, tag="OBSERVED"):
    narrative(text, tag=tag)


def comparison_row(key, actual, reference, label_text):
    html(
        f'<div class="comparison-row"><span>{escape(REGISTRY[key].name)}</span><strong>{escape(display(key, actual))}</strong><span>{escape(display(key, reference))}<small>{escape(label_text)}</small></span><strong class="accent">{escape(delta(key, actual - reference))}</strong></div>'
    )


def empty(title, detail):
    narrative(title, detail, "NO MATCHING EVIDENCE")


def error_state(title, detail):
    st.error(title)
    caption(detail)


def explain_metric(default="operating_profit", key="metric_explanation"):
    with st.popover("Explain metric", use_container_width=True):
        name = st.selectbox(
            "Metric definition",
            list(REGISTRY),
            index=list(REGISTRY).index(default),
            format_func=lambda k: REGISTRY[k].name,
            key=key,
        )
        definition = asdict(REGISTRY[name])
        st.subheader(definition["name"])
        for field, title in [
            ("interpretation", "Business definition"),
            ("formula", "Formula"),
            ("source", "Source"),
            ("grain", "Grain"),
            ("owner", "Business owner"),
            ("technical_owner", "Technical owner"),
            ("refresh", "Refresh"),
            ("limitation", "Limitations"),
        ]:
            st.markdown(f"**{title}**")
            st.text(definition[field])


def plot_style(figure, title=None, height=330):
    figure.update_layout(
        template="plotly_dark",
        title={"text": title or ""},
        height=height,
        margin=dict(l=12, r=18, t=42 if title else 16, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, ui-sans-serif, system-ui, sans-serif", color=SILVER, size=13),
        colorway=[ACCENT, SILVER, "#8C969D", WARNING],
        hoverlabel=dict(bgcolor="#222629", font_color="#F4F7F8"),
        legend=dict(orientation="h", y=-0.18),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="#222629", zerolinecolor="#465057"),
    )
    return figure


def chart(figure, title, explanation, key=None):
    st.plotly_chart(
        plot_style(figure, title),
        use_container_width=True,
        config={"displayModeBar": False},
        theme=None,
        key=key,
    )
    caption(explanation)


def line(frame, x, y, text):
    return go.Figure(
        go.Scatter(
            x=frame[x], y=frame[y], mode="lines", name=text, line=dict(width=2.5, color=ACCENT)
        )
    )


def table(frame):
    numeric = frame.select_dtypes(include="number").columns
    config = {
        key: st.column_config.NumberColumn(
            key.replace("_", " ").title(),
            format="%.2f" if frame[key].dtype.kind == "f" else "%d",
        )
        for key in numeric
    }
    st.dataframe(frame, use_container_width=True, hide_index=True, column_config=config)


def style():
    html("<style>" + Path(__file__).with_name("design.css").read_text() + "</style>")
