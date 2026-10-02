"""Forecasts, conditional scenarios, evidence routing and governance."""

from dataclasses import asdict
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components import caption, chart, display, header, metrics, table
from pulse.analytics.core import daily, ledger
from pulse.analytics.health import health
from pulse.forecasting.engine import forecast
from pulse.metrics.registry import REGISTRY
from pulse.query.ask import EXAMPLES, answer
from pulse.reports.brief import brief_html, make_brief
from pulse.runtime import database_path
from pulse.scenarios.engine import ASSUMPTION_TEXT, Assumptions, simulate


@st.cache_data(show_spinner=False)
def forecast_cached(location, fingerprint):
    return forecast(daily(location=location))


@st.cache_data(show_spinner=False)
def brief_cached(fingerprint):
    return make_brief()


def forecasts(start, end, location):
    header(
        "Forecast watch",
        "Transparent 28-day outlook. Compare models, review held-out errors and challenge the uncertainty.",
    )
    output = forecast_cached(location, database_path().stat().st_mtime_ns)
    metric = st.selectbox(
        "Forecast KPI", ["revenue", "transactions", "gross_profit", "labour_hours"]
    )
    selected = output["future"].query("metric==@metric")
    history = daily(location=location).tail(56)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history.date_id, y=history[metric], name="Observed", line=dict(color="#486A92")
        )
    )
    fig.add_trace(
        go.Scatter(x=selected.date_id, y=selected.upper, name="Approx. upper", line=dict(width=0))
    )
    fig.add_trace(
        go.Scatter(
            x=selected.date_id,
            y=selected.lower,
            name="Approx. lower",
            fill="tonexty",
            fillcolor="rgba(0,124,131,.15)",
            line=dict(width=0),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected.date_id,
            y=selected.forecast,
            name="Forecast",
            line=dict(color="#007C83", dash="dash"),
        )
    )
    chart(
        fig,
        f"What might happen next? · {metric.replace('_', ' ').title()}",
        "Forecast origin is the final dataset date, independently of sidebar period. Revenue/GP are AUD; transactions are orders; labour demand is hours.",
    )
    table(output["metrics"])
    selected_stats = output["metrics"].query("metric==@metric").iloc[0]
    if selected_stats.holdout_coverage < 0.8:
        st.warning(
            f"Held-out interval coverage is {selected_stats.holdout_coverage:.0%}, below the nominal 90%. "
            "Treat these bands as illustrative uncertainty; they are unsuitable as operational safety bounds. "
            "Structural change and the small calibration sample require review before planning."
        )
    caption(
        "Choose between last-week seasonal naive and 8-week weekday average using three prior 28-day validation origins. Evaluate selected model on untouched final 28 days. Refit on all history for future. Bands use horizon-specific 90th percentiles of three pre-holdout absolute errors; very small calibration sample, approximate coverage only. Staffing demand forecasts historical paid hours, not an optimised roster."
    )
    with st.expander("Inspect backtests"):
        table(output["backtests"])
    st.download_button(
        "Export forecast", output["future"].to_csv(index=False), "pulse_forecast.csv", "text/csv"
    )


def scenarios(start, end, location):
    header(
        "Scenario Lab",
        "Test a conditional decision against the observed cost ledger. Compare the base case, scenario and difference.",
    )
    base = ledger(start, end, location)
    caption(
        f"Base case: {start} to {end}. Controls are percentage changes unless labelled as a replacement rate."
    )
    left, right = st.columns(2)
    with left:
        price = st.slider("Price change %", -30, 30, 0)
        demand = st.slider("Transactions change %", -30, 30, 0)
        basket = st.slider("Basket quantity / AOV change %", -30, 30, 0)
        hours = st.slider("Labour hours change %", -30, 30, 0)
        wage = st.slider("Loaded hourly wage change %", -20, 20, 0)
    with right:
        retention = st.slider("Retention response change %", -30, 30, 0)
        uptake = st.slider("Additional promotion uptake (pp)", 0, 30, 0)
        replace_discount = st.checkbox("Replace discount rate")
        discount = st.slider(
            "Replacement discount rate %",
            0,
            50,
            int(round(base["discounts"] / base["list_sales"] * 100)),
            disabled=not replace_discount,
        )
        replace_margin = st.checkbox("Replace product margin on list sales")
        margin = st.slider(
            "Replacement product margin %",
            0,
            90,
            int(round((1 - base["cogs"] / base["list_sales"]) * 100)),
            disabled=not replace_margin,
        )
    assumptions = Assumptions(
        price / 100,
        demand / 100,
        basket / 100,
        hours / 100,
        wage / 100,
        retention / 100,
        uptake / 100,
        discount / 100 if replace_discount else None,
        margin / 100 if replace_margin else None,
    )
    result = simulate(base, assumptions)
    keys = [
        "revenue",
        "gross_profit",
        "operating_profit",
        "gross_margin",
        "operating_margin",
        "labour_pct",
    ]
    table(
        pd.DataFrame(
            [
                {
                    "Metric": REGISTRY[k].name,
                    "Base case": display(k, base[k]),
                    "Scenario": display(k, result[k]),
                    "Difference": display(k, result[k] - base[k]),
                }
                for k in keys
            ]
        )
    )
    caption(ASSUMPTION_TEXT)
    name = st.text_input("Comparison label", value="Proposed operating case")
    if st.button("Save scenario to comparison"):
        if name.strip():
            st.session_state.setdefault("scenarios", []).append(
                {
                    "name": name,
                    "scope": location,
                    "start": start,
                    "end": end,
                    "assumptions": asdict(assumptions),
                    **{key: result[key] for key in keys},
                }
            )
    saved = st.session_state.get("scenarios", [])
    if saved:
        st.subheader("Saved scenarios · session only")
        table(pd.DataFrame(saved).drop(columns="assumptions"))
        st.download_button(
            "Export scenario comparison",
            json.dumps(saved, indent=2),
            "pulse_scenarios.json",
            "application/json",
        )


def ask(start, end, location):
    header(
        "Ask PULSE",
        "Evidence-backed business questions, powered by deterministic analytical intents.",
    )
    caption(
        "Questions use company scope unless a store name is included. 'Last month' selects the latest full month; otherwise the latest complete week. Sidebar filters do not silently alter the question."
    )
    example = st.selectbox("Example question", EXAMPLES)
    question = st.text_input("Your business question", value=example, key="ask_question")
    # Example selection remains useful even if text was already edited.
    if st.button("Use selected example"):
        st.session_state.ask_question_pending = example
        st.rerun()
    if st.button("Analyse question"):
        st.session_state.ask_result = answer(question)
    result = st.session_state.get("ask_result")
    if result:
        st.write(result["answer"].replace("$", "\\$"))
        if result["supported"]:
            caption(
                f"Observed / estimated as labelled · {result['period']} · scope {result['scope']}"
            )
            table(result["evidence"])
            caption(result["method"])
            st.info(result["limitations"])


def brief(start, end, location):
    header(
        "Monday morning brief",
        "A company-wide management pack generated from current analytical results.",
    )
    output = brief_cached(database_path().stat().st_mtime_ns)
    caption(
        f"Company scope · Week ending {output['week_ending']}. Sidebar scope and period do not change the brief."
    )
    metrics(output["business_health"])
    for issue in output["top_issues"]:
        st.subheader(issue["entity"] + " · " + issue["issue"])
        st.write(issue["investigation"])
        table(pd.DataFrame(issue["evidence"]))
        caption(issue["risk"] + " " + issue["success_measure"])
    st.subheader("Top opportunity · estimated")
    table(pd.DataFrame(output["top_opportunity"]))
    caption(output["opportunity_assumptions"])
    st.subheader("Decisions required")
    for decision in output["decisions_required"]:
        st.write("• " + decision)
    st.download_button(
        "Export HTML executive brief", brief_html(output), "pulse_monday_brief.html", "text/html"
    )
    st.download_button(
        "Export evidence JSON",
        json.dumps(output, indent=2, allow_nan=False),
        "pulse_brief.json",
        "application/json",
    )
    caption(output["limitations"])


def methodology(start, end, location):
    header(
        "Methodology & governance",
        "Inspect definitions, assumptions and the limits of a portfolio prototype.",
    )
    table(pd.DataFrame([{"Key": key, **asdict(value)} for key, value in REGISTRY.items()]))
    st.subheader("Health index weighting")
    weights = {}
    defaults = {"Financial": 40, "Customer": 20, "Operations": 25, "Inventory": 15}
    for column, (name, default) in zip(st.columns(4), defaults.items()):
        weights[name] = column.number_input(
            name + " weight", min_value=0, max_value=100, value=default
        )
    try:
        output = health(ledger(start, end, location), weights)
        st.json(output)
    except ValueError as error:
        st.error(str(error))
    st.write(
        "Synthetic source → validation → constrained star schema → grain-safe SQL daily mart → governed KPI calculations → weekly warnings / investigation / forecasts / scenarios → management review. No causal or real-company impact claim."
    )
    st.info(
        "Observed = measured synthetic records. Estimated = an assumption-based reference gap. Forecast = modelled future. Scenario = conditional management assumptions. These labels are not interchangeable."
    )
    caption(
        "Local analytics connections are read-only and parameters are bound. No production authentication, row-level permissions or live integrations. No actual PII. Decisions/scenarios are session-only exports. Paid-hour forecasts and wage inputs are not compliance advice."
    )
