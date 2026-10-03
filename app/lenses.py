"""Contextual secondary evidence; these are not separate primary destinations."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import data
from app.components import ACCENT, SILVER, caption, chart, line, metrics, table
from pulse.analytics.core import contributions
from pulse.analytics.health import health
from pulse.analytics.impact import stockout_opportunity
from pulse.metrics.registry import REGISTRY
from pulse.runtime import query, read_sql


def availability(ctx, fingerprint, key="stock_substitution"):
    substitution = (
        st.slider("Assumed substitution when a SKU is unavailable %", 0, 100, 50, key=key) / 100
    )
    start = str((pd.Timestamp(ctx["end"]) - pd.Timedelta(days=55)).date())
    frame = stockout_opportunity(start, ctx["end"], ctx["location"], fingerprint[0], substitution)
    if frame.empty:
        st.info("No supported store/SKU reference cells for this window.")
    else:
        table(frame)
    caption(
        f"Estimated stockout opportunity · {start} to {ctx['end']} · selected location scope · ≥3 available reference days per store/SKU/weekday · {substitution:.0%} substitution. Not observed lost sales; do not add to warning exposure."
    )


def campaigns(ctx, fingerprint):
    table(
        query(
            read_sql("promotion_analysis.sql"),
            {"start": ctx["start"], "end": ctx["end"]},
            fingerprint[0],
        )
    )
    caption(
        "Company campaign economics for the selected period. Whole store-day contribution versus prior 56-day same-store/weekday reference (≥3 days); subtract campaign spend once. Selection and seasonality confound this observational ROI."
    )


def customers(ctx, fingerprint):
    current = data.measured(ctx["start"], ctx["end"], ctx["location"], fingerprint)
    metrics(current, keys=["customer_count", "repeat_rate", "satisfaction"])
    table(
        contributions(ctx["start"], ctx["end"], "Customer segment", ctx["location"], fingerprint[0])
    )
    retention = query("SELECT * FROM mart_retention", path=fingerprint[0])
    chart(
        line(retention, "month", "retention", "Next-month retention"),
        "Are identified customers returning?",
        "Company/month transitions, irrespective of selected location. Latest month right-censored; absence next month is not permanent churn.",
    )
    with st.expander("Inspect customer cohorts and retention evidence"):
        table(retention)
        table(query("SELECT * FROM mart_cohorts", path=fingerprint[0]))
        caption(
            "First observed purchase, not necessarily acquisition; left-censored at dataset start. Guest identities excluded."
        )


def operations(ctx, fingerprint):
    inv = data.investigation(ctx["start"], ctx["end"], ctx["location"], fingerprint)
    metrics(
        inv["after"],
        inv["before"],
        ["labour_cost", "labour_pct", "sales_per_labour_hour", "stockout_rate"],
    )
    history = data.history(ctx["location"], fingerprint)
    history = history[history.date_id <= ctx["end"]].tail(56)
    chart(
        line(history, "date_id", "labour_pct", "Observed payroll share"),
        "Is payroll pressure rising?",
        "Daily loaded payroll / net revenue. A lower sales denominator can increase this ratio without more hours.",
    )
    availability(ctx, fingerprint, key="operations_substitution")
    campaigns(ctx, fingerprint)


def forecasts(ctx, fingerprint):
    output = data.outlook(ctx["location"], fingerprint)
    metric = st.selectbox(
        "Forecast KPI",
        ["revenue", "transactions", "gross_profit", "labour_hours"],
        format_func=lambda k: REGISTRY[k].name if k in REGISTRY else "Paid labour hours",
        key="forecast_metric",
    )
    selected = output["future"].query("metric==@metric")
    history = data.history(ctx["location"], fingerprint).tail(56)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=history.date_id, y=history[metric], name="Observed", line=dict(color=SILVER))
    )
    fig.add_trace(
        go.Scatter(
            x=selected.date_id,
            y=selected.upper,
            name="Approx. upper",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected.date_id,
            y=selected.lower,
            name="Approx. lower",
            fill="tonexty",
            fillcolor="rgba(0,161,156,.12)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected.date_id,
            y=selected.forecast,
            name="Forecast",
            line=dict(color=ACCENT, dash="dash"),
        )
    )
    chart(
        fig,
        "What might happen after the dataset ends?",
        f"FORECAST · location scope retained · origin {history.date_id.iloc[-1]} irrespective of selected observed period. Fictional continuation, not a current business forecast.",
    )
    stats = output["metrics"].query("metric==@metric").iloc[0]
    if stats.holdout_coverage < 0.8:
        st.warning(
            f"Held-out band coverage {stats.holdout_coverage:.0%}, below nominal 90%. These approximate bands are unsuitable as operational safety bounds."
        )
    table(output["metrics"])
    caption(
        "Last-week seasonal naive versus eight-week weekday average; three pre-holdout validation origins select the model. Final 28 days are untouched holdout. Three-origin empirical bands have limited calibration. Paid hours are historical payroll, not an optimal roster."
    )
    with st.expander("Inspect forecast backtests"):
        table(output["backtests"])
    st.download_button(
        "Export forecast evidence",
        output["future"].to_csv(index=False),
        "pulse_forecast.csv",
        "text/csv",
    )


def system(ctx, fingerprint, quality):
    st.subheader("System & analytical trust")
    passed = int((quality.status == "PASS").sum())
    caption(
        f"{passed}/{len(quality)} source rules passed · pipeline-time validation, not live infrastructure monitoring"
    )
    area = st.radio(
        "System area",
        ["Data quality", "Metric registry", "Health assumptions"],
        horizontal=True,
        key="system_area",
    )
    if area == "Data quality":
        table(quality)
        table(query("SELECT * FROM metadata", path=fingerprint[0]))
        caption(
            "Failed publication retains the previous analytical snapshot. No live POS/payroll connection or production authentication."
        )
    elif area == "Metric registry":
        from dataclasses import asdict

        table(pd.DataFrame([{"Key": key, **asdict(value)} for key, value in REGISTRY.items()]))
        caption(
            "Definitions, grains, owners and limitations come from the authoritative KPI registry."
        )
    else:
        weights = {}
        defaults = {"Financial": 40, "Customer": 20, "Operations": 25, "Inventory": 15}
        for column, (name, default) in zip(st.columns(2) * 2, defaults.items()):
            weights[name] = column.number_input(
                name + " weight", 0, 100, default, key="health_" + name
            )
        try:
            output = health(
                data.measured(ctx["start"], ctx["end"], ctx["location"], fingerprint), weights
            )
            st.json(output)
            caption(
                "Exploratory weighting only; does not alter the governed Home index. Fictional targets, not a predictive risk model."
            )
        except ValueError as error:
            st.error(str(error))
            st.button("Restore health weights", on_click=restore_health_weights)


def restore_health_weights():
    for name, value in {"Financial": 40, "Customer": 20, "Operations": 25, "Inventory": 15}.items():
        st.session_state["health_" + name] = value
