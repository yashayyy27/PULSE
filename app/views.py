"""Executive, investigation, warnings and operational decision surfaces."""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components import caption, chart, display, header, line, metrics, money, table
from pulse.alerts.engine import detect, exposure_summary
from pulse.analytics.core import DIMENSIONS, contributions, daily, investigate
from pulse.analytics.health import health
from pulse.analytics.impact import annualise, stockout_opportunity
from pulse.metrics.registry import REGISTRY
from pulse.runtime import query, read_sql


def overview(start, end, location):
    header(
        "See the change. Decide where to act.",
        "A weekly view of performance, financial pressure and the investigations that deserve management attention.",
    )
    inv = investigate(start, end, location)
    a, b = inv["after"], inv["before"]
    caption(
        f"Observed · {start} — {end} · compared with {inv['prior_start']} — {inv['prior_end']} · AUD excluding GST"
    )
    metrics(a, b)
    alerts = detect()
    if location is not None:
        alerts = alerts[alerts.location_id == location]
    left, right = st.columns([1.65, 1])
    with left:
        trend = daily(location=location).tail(84)
        trend["7-day revenue"] = trend.revenue.rolling(7).sum()
        chart(
            line(trend, "date_id", "7-day revenue", "Observed 7-day revenue"),
            "Is net demand strengthening?",
            "Trailing seven-day revenue; the first six displayed observations lack a full window.",
        )
    with right:
        st.subheader("Attention queue")
        st.metric("Estimated weekly profit exposure", money(exposure_summary(alerts)))
        caption(
            "Operating-profit warning gaps only, once per store. Overlapping KPI estimates are excluded."
        )
        if alerts.empty:
            st.info("No weekly warning exceeds the configured thresholds.")
        for row in alerts.drop_duplicates("location_id").head(3).itertuples():
            st.markdown(f"**{row.severity} · {row.entity}**")
            caption(
                f"{REGISTRY[row.kpi].name} · actual {display(row.kpi, row.actual)} · baseline {display(row.kpi, row.baseline)}"
            )
        if st.button("Open investigation", key="overview_investigate"):
            st.session_state.nav_pending = "Investigate"
            st.rerun()
    h = health(a)
    st.subheader("Business health · a transparent management index")
    table(
        pd.DataFrame(
            [
                {
                    "Dimension": key,
                    "Score / 100": round(value, 1),
                    "Weight": h["normalised_weights"][key],
                }
                for key, value in h["scores"].items()
            ]
        )
    )
    caption(
        f"Overall {h['overall']:.0f}/100. {h['method']} Targets and weights are inspectable in Methodology."
    )


def investigation(start, end, location):
    header(
        "Investigate the movement",
        "Follow the accounting evidence from business movement to a store and its associated drivers.",
    )
    state = st.selectbox(
        "Drill into state / district",
        ["All"] + query("SELECT DISTINCT state FROM dim_location ORDER BY state").state.tolist(),
    )
    stores = query(
        "SELECT location_id,name FROM dim_location WHERE (?='All' OR state=?) ORDER BY name",
        (state, state),
    )
    options = {"Use sidebar scope": location, **dict(zip(stores.name, stores.location_id))}
    chosen = st.selectbox("Then choose a location", list(options))
    selected = options[chosen]
    inv = investigate(start, end, selected)
    a, b = inv["after"], inv["before"]
    metrics(a, b)
    bridge = inv["bridge"]
    fig = go.Figure(
        go.Waterfall(
            x=bridge.contributor,
            y=bridge.impact,
            measure=["relative"] * len(bridge),
            increasing=dict(marker_color="#007C83"),
            decreasing=dict(marker_color="#9B4A37"),
        )
    )
    chart(
        fig,
        "Which ledger movements explain the profit difference?",
        f"Observed profit change {money(a['operating_profit'] - b['operating_profit'])}; bridge reconciles exactly. Volume uses previous list AOV; basket includes price, quantity and mix.",
    )
    table(bridge)
    dim = st.selectbox("Explore associated revenue contributors", list(DIMENSIONS))
    frame = contributions(start, end, dim, selected)
    chart(
        go.Figure(go.Bar(x=frame.head(12).entity.astype(str), y=frame.head(12).contribution)),
        f"Where did revenue change? · {dim}",
        "Equal-length prior-period comparison. All rows reconcile; chart displays the 12 largest adverse contributors.",
    )
    table(frame)
    st.info(
        "Evidence suggests where to investigate. Accounting contribution does not identify a causal effect."
    )
    with st.form("decision_record"):
        st.subheader("Record an investigation decision")
        owner = st.text_input("Fictional owner / role", value="Regional Operations Manager")
        action = st.text_area(
            "Proposed investigation",
            value="Reconcile roster and product/channel mix with store manager; agree service guardrails.",
        )
        submitted = st.form_submit_button("Record proposal")
    if submitted:
        if not owner.strip() or not action.strip():
            st.error("An owner and investigation are required.")
        else:
            st.session_state.setdefault("decisions", []).append(
                {
                    "status": "Proposed; unapproved",
                    "owner": owner,
                    "action": action,
                    "location_id": selected,
                    "period_end": end,
                    "observed_profit": a["operating_profit"],
                    "guardrails": "Satisfaction and service must be reviewed",
                }
            )
            st.success("Proposal recorded in this session. Export it to retain the decision.")
    records = st.session_state.get("decisions", [])
    if records:
        table(pd.DataFrame(records))
        st.download_button(
            "Export decision log",
            json.dumps(records, indent=2),
            "pulse_decisions.json",
            "application/json",
        )


def alerts_page(start, end, location):
    header(
        "Early warnings",
        "Explainable deviations against eight prior complete weeks. Review evidence before taking action.",
    )
    frame = detect()
    if location is not None:
        frame = frame[frame.location_id == location]
    caption(
        "Alerts use the latest complete Monday–Sunday week, independently of the sidebar period."
    )
    table(frame)
    st.metric("Estimated weekly operating-profit exposure", money(exposure_summary(frame)))
    with st.expander("Financial assumptions and annualised sensitivity"):
        st.json(annualise(exposure_summary(frame)))
        st.write(
            "Revenue warnings use historical gross margin; labour warnings use excess share times current revenue. Ratio-only warnings have no monetary estimate. These estimates overlap and are not summed."
        )
    caption(
        "Baseline median; MAD ×1.4826 with 3% scale floor; adverse deviation ≥8%, robust z ≥2.5. Monetary warnings require ≥A$150; critical ≥A$750. Expected range is a heuristic reference, not a calibrated prediction interval."
    )
    if not frame.empty:
        label = st.selectbox("Review warning", frame.entity + " / " + frame.kpi)
        row = frame.loc[(frame.entity + " / " + frame.kpi) == label].iloc[0]
        st.write(row.investigation)
        if st.button("Investigate this store"):
            names = query(
                "SELECT name FROM dim_location WHERE location_id=?", (int(row.location_id),)
            )
            st.session_state.scope_pending = names.iloc[0, 0]
            st.session_state.nav_pending = "Investigate"
            st.rerun()


def customers(start, end, location):
    header(
        "Customer signals", "Separate repeat activity, segment movement and next-month retention."
    )
    a = investigate(start, end, location)["after"]
    metrics(a, keys=["customer_count", "repeat_rate", "satisfaction"])
    segments = contributions(start, end, "Customer segment", location)
    chart(
        go.Figure(go.Bar(x=segments.entity, y=segments.contribution)),
        "Which customer segment is weakening?",
        "Revenue movement for selected scope and equal-length previous period; guest sales are shown separately.",
    )
    table(segments)
    st.subheader("Company retention · completed monthly transitions")
    retention = query("SELECT * FROM mart_retention")
    retention["churn"] = 1 - retention.retention
    chart(
        line(retention, "month", "retention", "Next-month retention"),
        "Are identified customers returning?",
        "Company scope, irrespective of store filter. Final month is right-censored and intentionally blank; churn is absence next month, not permanent loss.",
    )
    table(retention)
    with st.expander("First-observed-month cohorts"):
        table(query("SELECT * FROM mart_cohorts"))
        caption(
            "Cohort membership is left-censored at dataset start; this is first observed purchase, not necessarily acquisition."
        )


def operations(start, end, location):
    header(
        "Operational pressure",
        "Connect staffing, inventory availability and campaign economics to a practical investigation.",
    )
    inv = investigate(start, end, location)
    metrics(
        inv["after"],
        inv["before"],
        ["labour_cost", "labour_pct", "sales_per_labour_hour", "stockout_rate"],
    )
    history = daily(location=location).tail(84)
    chart(
        line(history, "date_id", "labour_pct", "Observed labour share"),
        "Is payroll pressure rising?",
        "Daily loaded payroll / net revenue; higher share can reflect lower sales rather than more hours.",
    )
    substitution = st.slider("Assumed substitution when a SKU is unavailable", 0, 100, 50) / 100
    st.subheader("Estimated stockout opportunity")
    opportunity_start = (pd.Timestamp(end) - pd.Timedelta(days=55)).strftime("%Y-%m-%d")
    table(stockout_opportunity(opportunity_start, end, location, substitution=substitution))
    caption(
        f"Estimated, not observed lost sales. Last 56 days; same store/SKU/weekday reference with ≥3 available days; {substitution:.0%} substitution. Do not add this to alert exposure."
    )
    st.subheader("Company campaign economics · observational")
    table(query(read_sql("promotion_analysis.sql"), {"start": start, "end": end}))
    caption(
        "Company scope. Full store-day contribution compares campaign days against non-campaign same-store/weekday averages from the prior 56 days (at least 3 reference days); subtract campaign spend once. Includes cannibalisation across products; seasonality and selection remain confounded. Not causal ROI."
    )


def quality(start, end, location):
    header(
        "Trust starts with the source",
        "Data contract checks run before the database is published. Failed validation retains the previous analytical database.",
    )
    frame = query("SELECT * FROM quality_checks")
    st.metric("Passed source rules", f"{(frame.status == 'PASS').sum()} / {len(frame)}")
    st.metric("Failures", int(frame.failures.sum()))
    table(frame)
    caption(
        "These are pipeline-time checks. Local files are treated as immutable after publication; this is not continuous production monitoring."
    )
    table(query("SELECT * FROM metadata"))
