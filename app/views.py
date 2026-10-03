"""Signal-first journeys, with progressively disclosed analytical evidence."""

from html import escape
import json
import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from app import data
from app.components import (
    ACCENT,
    SILVER,
    WARNING,
    caption,
    chart,
    comparison_row,
    delta,
    display,
    empty,
    explain_metric,
    header,
    html,
    label,
    metrics,
    money,
    narrative,
    plot_style,
    section,
    signal_summary,
    table,
)
from app.state import (
    DOMAINS,
    acknowledge,
    add_to_brief,
    filter_signals,
    navigate,
    reset_context,
    reset_filters,
    select_signal,
    set_context,
    signal_id,
)
from pulse.alerts.engine import exposure_summary
from pulse.analytics.core import ADDITIVE, DIMENSIONS, contributions
from pulse.analytics.health import health
from pulse.metrics.registry import REGISTRY, calculate
from pulse.query.ask import month_window
from pulse.analytics.core import latest_week
from pulse.runtime import query
from pulse.scenarios.engine import Assumptions, simulate


def open_signal(row, page="Investigate", comparison=None, question=None):
    select_signal(st.session_state, row, data.locations(data.snapshot()))
    if comparison:
        st.session_state.comparison = comparison
        st.session_state.comparison_mode = comparison
    if question:
        st.session_state.ask_question = question
    navigate(st.session_state, page)


def add_finding(row):
    add_to_brief(st.session_state, row)


def pulse_figure(timeline, rows, selected_id):
    figure = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.04
    )
    figure.add_trace(
        go.Scatter(
            x=timeline.week,
            y=timeline.health,
            mode="lines",
            line=dict(color=ACCENT, width=3),
            fill="tozeroy",
            fillcolor="rgba(0,161,156,.045)",
            customdata=timeline[["profit", "revenue"]],
            hovertemplate="Week ending %{x}<br>Health %{y:.0f}/100<br>Profit A$%{customdata[0]:,.0f}<br>Revenue A$%{customdata[1]:,.0f}<extra></extra>",
            name="Observed business health",
        ),
        row=1,
        col=1,
    )
    events = rows.drop_duplicates("location_id").head(3).to_dict("records")
    for index, row in enumerate(events):
        selected = signal_id(row) == selected_id
        figure.add_trace(
            go.Scatter(
                x=[row["timestamp"]],
                y=[len(events) - index],
                mode="markers+text",
                text=[row["entity"]],
                textposition="middle left",
                textfont=dict(size=13, color=SILVER),
                marker=dict(
                    size=14 if selected else 10,
                    color=ACCENT if selected else WARNING,
                    line=dict(color="#090A0B", width=2),
                ),
                customdata=[
                    [
                        signal_id(row),
                        row["entity"],
                        REGISTRY[row["kpi"]].name,
                        row["severity"],
                        display(row["kpi"], row["variance"]),
                        money(row["estimated_profit_exposure"]),
                    ]
                ],
                hovertemplate="%{customdata[1]} · %{customdata[2]}<br>%{customdata[3]} · week ending %{x}<br>Deviation %{customdata[4]}<br>Estimated exposure %{customdata[5]}<extra></extra>",
                name=row["entity"],
                showlegend=False,
            ),
            row=2,
            col=1,
        )
    plot_style(figure, height=250)
    figure.update_layout(
        showlegend=False,
        clickmode="event+select",
        dragmode=False,
        margin=dict(l=0, r=90, t=10, b=10),
    )
    figure.update_yaxes(range=[0, 105], title_text="Health / 100", row=1, col=1)
    figure.update_yaxes(visible=False, range=[0, 4], row=2, col=1)
    figure.update_xaxes(
        showgrid=False,
        zeroline=False,
        range=[
            pd.Timestamp(timeline.week.iloc[0]) - pd.Timedelta(days=3),
            pd.Timestamp(timeline.week.iloc[-1]) + pd.Timedelta(days=8),
        ],
    )
    return figure


def pulse_select():
    points = st.session_state.get("business_pulse", {}).get("selection", {}).get("points", [])
    for point in points:
        values = point.get("customdata", [])
        if values and isinstance(values[0], str) and ":" in values[0]:
            frame = data.signals(data.snapshot())
            rows = [row for row in frame.to_dict("records") if signal_id(row) == values[0]]
            if rows:
                select_signal(st.session_state, rows[0], data.locations(data.snapshot()))
                st.session_state.pulse_selector = values[0]
                st.session_state.feedback = (
                    f"Selected {rows[0]['entity']} signal. Open its investigation below."
                )
            break


def selector_change():
    rows = data.signals(data.snapshot()).to_dict("records")
    row = next((r for r in rows if signal_id(r) == st.session_state.pulse_selector), None)
    if row:
        select_signal(st.session_state, row, data.locations(data.snapshot()))


def home(ctx, fingerprint):
    start, end = latest_week(fingerprint[0])
    observed = data.investigation(start, end, None, fingerprint)
    current, before = observed["after"], observed["before"]
    warnings = data.signals(fingerprint)
    h = health(current)
    header(
        "Your business, in focus.",
        "Spot the change. Follow the evidence. Decide what deserves a closer look.",
        "THE MORNING VIEW / WATTLE & RYE",
    )
    left, right = st.columns([1, 2.6], gap="large")
    with left:
        label("BUSINESS PULSE")
        html(
            f'<div class="hero-score">{h["overall"]:.0f}<small> / 100</small></div><div class="hero-state">{"REVIEW SIGNALS" if len(warnings) else "NO CURRENT WARNINGS"}</div>'
        )
        caption("A transparent management index, not a predictive risk score.")
        count = len(data.locations(fingerprint))
        html(
            f'<p class="hero-summary">{count} locations monitored<br>{len(REGISTRY)} governed KPIs<br><strong>{len(warnings)} signals</strong> to review</p>'
        )
        label("ESTIMATED WEEKLY PROFIT EXPOSURE")
        html(
            f'<div class="metric-display large"><div class="figure">{escape(money(exposure_summary(warnings)))}</div></div>'
        )
        caption("Operating-profit median gaps, once per store. Overlapping KPI estimates excluded.")
    with right:
        label("THE PULSE / 12 COMPLETE WEEKS")
        selected = st.session_state.get("selected_signal")
        timeline = data.pulse_timeline(None, end, fingerprint)
        if not timeline.empty:
            st.plotly_chart(
                pulse_figure(timeline, warnings, signal_id(selected) if selected else None),
                key="business_pulse",
                on_select=pulse_select,
                selection_mode="points",
                use_container_width=True,
                config={"displayModeBar": False},
                theme=None,
            )
        caption(
            "Observed weekly health. Markers: three priority locations in the latest warning window. Click or choose a signal below."
        )
        rows = warnings.to_dict("records")
        if rows:
            choices = {signal_id(row): row for row in rows}
            if st.session_state.get("pulse_selector") not in choices:
                selected_id = signal_id(selected) if selected else None
                st.session_state.pulse_selector = (
                    selected_id if selected_id in choices else next(iter(choices))
                )
            selector, action = st.columns([3, 1])
            with selector:
                choice = st.selectbox(
                    "Select a business signal",
                    list(choices),
                    format_func=lambda k: f"{choices[k]['entity']} · {REGISTRY[choices[k]['kpi']].name} · {choices[k]['severity']}",
                    key="pulse_selector",
                    on_change=selector_change,
                )
            row = choices[choice]
            with action:
                label("NEXT ACTION")
                st.button(
                    "Investigate signal →",
                    key="overview_investigate",
                    type="primary",
                    on_click=open_signal,
                    args=(row,),
                )
            signal_summary(row, selected=True, compact=True)
        else:
            empty(
                "No current weekly signals.", "Explore the observed company ledger in Investigate."
            )
            st.button(
                "Explore company evidence",
                on_click=navigate,
                args=(st.session_state, "Investigate"),
            )
    section("01", "This week in 30 seconds")
    narrative(
        f"Operating profit was {money(current['operating_profit'])}, {delta('operating_profit', current['operating_profit'] - before['operating_profit'])} versus the previous week, on {money(current['revenue'])} revenue.",
        f"Observed · {start} to {end} · operating margin {current['operating_margin']:.1%}. {len(warnings)} latest-week signals; {warnings.location_id.nunique()} locations represented. Synthetic records, AUD excluding GST.",
    )
    metrics(current, before)
    with st.expander("Understand the health index"):
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
        caption(h["method"])
        st.json(h["targets"])
    explain_metric(key="home_metric")
    section(
        "02",
        "Needs your attention",
        "Prioritised by the warning engine. Reference gaps indicate investigations, not guaranteed benefits.",
    )
    attention = warnings.drop_duplicates("location_id")
    if rows:
        attention = attention[attention.location_id != choices[choice]["location_id"]]
    for index, row in enumerate(attention.head(2).to_dict("records"), 1):
        signal_summary(row, index)
        inv = data.investigation(
            row["period_start"], row["timestamp"], int(row["location_id"]), fingerprint
        )
        adverse = inv["bridge"].sort_values("impact").head(2)
        caption(
            "Associated previous-week ledger movements: "
            + " · ".join(f"{r.contributor} {money(r.impact)}" for r in adverse.itertuples())
            + ". Different comparison from warning median; no causal claim."
        )
        st.button(
            f"Investigate {row['entity']}",
            key=f"home_open_{signal_id(row)}",
            on_click=open_signal,
            args=(row,),
        )


def signals(ctx, fingerprint):
    frame = data.signals(fingerprint)
    header(
        "Find the signal worth following.",
        "Each warning is a starting point for an investigation. Review the baseline before acting.",
        "SIGNALS / LATEST COMPLETE WEEK",
    )
    start, end = latest_week(fingerprint[0])
    caption(
        f"{start} to {end} · status is session-only · acknowledge does not resolve or remove analytical evidence"
    )
    with st.popover("Filter signals", use_container_width=False):
        filters = {}
        choices = {
            "severity": ["All", "CRITICAL", "WARNING"],
            "domain": ["All", *sorted(set(DOMAINS.values()))],
            "entity": ["All", *sorted(frame.entity.unique())],
            "kpi": ["All", *REGISTRY],
            "status": ["All", "Open", "Acknowledged"],
        }
        labels = {
            "severity": "Severity",
            "domain": "Business domain",
            "entity": "Location",
            "kpi": "KPI",
            "status": "Session status",
        }
        for key, options in choices.items():
            st.session_state.setdefault(
                "filter_" + key, st.session_state.get("signal_filters", {}).get(key, "All")
            )
            filters[key] = st.selectbox(
                labels[key],
                options,
                key="filter_" + key,
                format_func=(lambda k: REGISTRY[k].name if k in REGISTRY else k)
                if key == "kpi"
                else str,
            )
        st.button(
            "Reset filters", key="signal_reset", on_click=reset_filters, args=(st.session_state,)
        )
    st.session_state.signal_filters = filters.copy()
    filtered = filter_signals(frame, st.session_state.signal_status, **filters)
    caption(
        f"{len(filtered)} matching signals · {len(frame)} total · non-overlapping company profit exposure {money(exposure_summary(frame))}"
    )
    if filtered.empty:
        empty(
            "No signals match these filters.",
            "Reset the filters to return to the current weekly feed.",
        )
        st.button(
            "Reset filters",
            key="empty_reset",
            on_click=reset_filters,
            args=(st.session_state,),
            type="primary",
        )
        return
    pages = max(1, math.ceil(len(filtered) / 5))
    if st.session_state.get("signal_feed_page", 1) > pages:
        st.session_state.signal_feed_page = 1
    page = st.number_input("Feed page", 1, pages, key="signal_feed_page") if pages > 1 else 1
    for index, row in enumerate(
        filtered.iloc[(page - 1) * 5 : page * 5].to_dict("records"), (page - 1) * 5 + 1
    ):
        sid = signal_id(row)
        signal_summary(
            row,
            index,
            selected=bool(
                st.session_state.selected_signal
                and signal_id(st.session_state.selected_signal) == sid
            ),
        )
        caption(f"{row['domain']} · Status: {row['status']} · {row['evidence']}")
        primary, other = st.columns([1, 3])
        primary.button(
            "Investigate signal",
            key="open_" + sid,
            type="primary",
            on_click=open_signal,
            args=(row,),
        )
        with other.popover("Signal actions"):
            st.button(
                "Acknowledge signal",
                key="ack_" + sid,
                disabled=row["status"] == "Acknowledged",
                on_click=acknowledge,
                args=(st.session_state, row),
            )
            included = any(item["id"] == sid for item in st.session_state.brief_items)
            st.button(
                "Add to brief",
                key="add_" + sid,
                disabled=included,
                on_click=add_finding,
                args=(row,),
            )
            st.button(
                "Compare with baseline",
                key="compare_" + sid,
                on_click=open_signal,
                args=(row, "Investigate", "8-week baseline"),
            )
            st.button(
                "Ask PULSE about this signal",
                key="ask_" + sid,
                on_click=open_signal,
                args=(row, "Ask PULSE", None, "Why is this signal here?"),
            )
        with st.expander("Why was this triggered?"):
            caption(row["method"])
            st.write(
                f"Robust z: {row['robust_z']:+.2f} · adverse threshold: 2.5 · deviation threshold: 8%"
            )
            caption(
                f"Heuristic reference range {display(row['kpi'], row['expected_low'])} to {display(row['kpi'], row['expected_high'])}. Not a calibrated prediction interval. No holiday adjustment; small-rate baselines can amplify warnings."
            )


def choose_scope():
    ctx = st.session_state.context.copy()
    info = data.locations(data.snapshot())
    name = st.session_state.investigation_location
    if name == "Company":
        ctx.update(location=None, entity="Company", state="All")
    else:
        row = info.loc[info.name == name].iloc[0]
        ctx.update(location=int(row.location_id), entity=row["name"], state=row.state)
    set_context(st.session_state, ctx)


def choose_period():
    ctx = st.session_state.context.copy()
    ctx["start"], ctx["end"] = (
        month_window()
        if st.session_state.investigation_period == "Latest full month"
        else latest_week()
    )
    set_context(st.session_state, ctx)


def compare_state():
    st.session_state.comparison = "State"
    st.session_state.comparison_mode = "State"


def baseline_evidence(row, fingerprint, chart_key="signal_baseline"):
    if not row:
        empty(
            "No warning is attached to this context.",
            "Choose a current signal to inspect its median/MAD reference. Previous-period evidence is available below.",
        )
        return
    caption(row["evidence"] + ". " + row["method"])
    frame = data.history(int(row["location_id"]), fingerprint).copy()
    frame["week"] = (
        pd.to_datetime(frame.date_id).dt.to_period("W-SUN").dt.end_time.dt.strftime("%Y-%m-%d")
    )
    values = []
    for week, group in frame[frame.date_id <= row["timestamp"]].groupby("week"):
        if len(group) == 7:
            measured = calculate(group[ADDITIVE].sum().to_dict())
            values.append({"week": week, "value": measured[row["kpi"]]})
    frame = pd.DataFrame(values).tail(9)
    fig = go.Figure(
        go.Scatter(
            x=frame.week,
            y=frame.value,
            mode="lines+markers",
            line=dict(color=SILVER),
            name="Observed weekly KPI",
        )
    )
    fig.add_hline(
        y=row["baseline"], line_color=ACCENT, line_dash="dash", annotation_text="8-week median"
    )
    fig.add_hrect(
        y0=row["expected_low"],
        y1=row["expected_high"],
        fillcolor="rgba(0,161,156,.08)",
        line_width=0,
    )
    fig.update_yaxes(
        title_text="Ratio" if REGISTRY[row["kpi"]].unit == "ratio" else REGISTRY[row["kpi"]].unit
    )
    chart(
        fig,
        "How unusual is the latest complete week?",
        "Previous eight complete weeks plus selected week. Shaded range is a heuristic MAD reference, not a forecast confidence band.",
        key=chart_key,
    )
    comparison_row(row["kpi"], row["actual"], row["baseline"], "8-week median")
    caption(
        f"Robust z {row['robust_z']:+.2f}; denominator uses max(|median|, scale). Percentage deviations can be extreme near zero; the monetary/percentage-point differences remain visible."
    )


def comparison(ctx, inv, fingerprint):
    modes = ["Previous period", "Company", "State", "8-week baseline"]
    mode = st.radio("Compare against", modes, key="comparison", horizontal=True)
    st.session_state.comparison_mode = mode
    current = inv["after"]
    if mode == "8-week baseline":
        baseline_evidence(st.session_state.selected_signal, fingerprint, "comparison_baseline")
        return
    if mode == "Previous period":
        reference = inv["before"]
        reference_name = f"{inv['prior_start']} to {inv['prior_end']}"
        caption(
            "Equal-length previous-period comparison; the full profit bridge reconciles to this comparison."
        )
    elif mode == "Company":
        reference = data.measured(ctx["start"], ctx["end"], None, fingerprint)
        reference_name = "Company aggregate"
        caption(
            "Company totals are larger in scale. Compare margin, payroll share, satisfaction and availability rather than interpreting a total-sales gap as underperformance."
        )
    else:
        if ctx["location"] is None:
            empty(
                "Choose a location to compare with its state.",
                "Use the scope controls above. No state benchmark is inferred for company scope.",
            )
            return
        sums = ",".join(f"SUM({k}) {k}" for k in ADDITIVE)
        raw = (
            query(
                f"SELECT {sums} FROM mart_daily WHERE state=? AND date_id BETWEEN ? AND ?",
                (ctx["state"], ctx["start"], ctx["end"]),
                fingerprint[0],
            )
            .iloc[0]
            .to_dict()
        )
        reference = calculate(raw)
        reference_name = f"{ctx['state']} aggregate"
        caption(
            "State benchmark includes the selected location. Ratios come from aggregate sums, not averages of store ratios."
        )
    keys = (
        ["revenue", "gross_profit", "operating_profit", "operating_margin", "labour_pct"]
        if mode == "Previous period"
        else [
            "operating_margin",
            "gross_margin",
            "labour_pct",
            "satisfaction",
            "inventory_availability",
        ]
    )
    for key in keys:
        comparison_row(key, current[key], reference[key], reference_name)


def decision_path(path):
    st.session_state.decision_path = path


def preset_scenario(hours):
    from app.state import update_scenario_inputs

    update_scenario_inputs(st.session_state, hours_change=hours)
    navigate(st.session_state, "Scenario Lab")


def investigation(ctx, fingerprint):
    header(
        "Follow the evidence.",
        "From a signal to a defensible next investigation, with every comparison and assumption visible.",
        "INVESTIGATE / ANALYTICAL STORY",
    )
    controls = st.columns([1, 1.3, 1.5])
    controls[0].button(
        "PULSE / Company",
        key="breadcrumb_company",
        on_click=reset_context,
        args=(st.session_state, *latest_week(fingerprint[0])),
    )
    controls[1].button(
        f"{ctx['state']} / State comparison" if ctx["location"] else "State comparison",
        disabled=ctx["location"] is None,
        on_click=compare_state,
    )
    with controls[2]:
        explain_metric(ctx["kpi"], "investigation_metric")
    with st.expander("Change investigation scope"):
        names = data.locations(fingerprint)
        region = st.selectbox(
            "Filter locations by state", ["All", *sorted(names.state.unique())], key="scope_state"
        )
        options = [
            "Company",
            *names.loc[(names.state == region) | (region == "All"), "name"].tolist(),
        ]
        if ctx["entity"] not in options:
            options.append(ctx["entity"])
        st.session_state.investigation_location = ctx["entity"]
        st.selectbox(
            "Investigation location", options, key="investigation_location", on_change=choose_scope
        )
        st.session_state.investigation_period = (
            "Latest full month"
            if ctx["start"] == month_window(fingerprint[0])[0]
            and ctx["end"] == month_window(fingerprint[0])[1]
            else "Latest complete week"
        )
        st.selectbox(
            "Observed period",
            ["Latest complete week", "Latest full month"],
            key="investigation_period",
            on_change=choose_period,
        )
    inv = data.investigation(ctx["start"], ctx["end"], ctx["location"], fingerprint)
    current, before = inv["after"], inv["before"]
    selected = st.session_state.selected_signal
    section("01", "Signal detected" if selected else "Observed movement")
    if selected:
        signal_summary(selected, selected=True)
    else:
        narrative(
            f"{ctx['entity']} operating profit changed by {delta('operating_profit', current['operating_profit'] - before['operating_profit'])}.",
            "No anomaly is implied by this previous-period comparison.",
        )
    section("02", "Put the change in context")
    caption(
        f"PULSE / {ctx['state']} / {ctx['entity']} / {REGISTRY[ctx['kpi']].name} · {ctx['start']} to {ctx['end']} · synthetic · AUD excluding GST"
    )
    metrics(current, before, ["operating_profit", "revenue", "labour_pct", "satisfaction"])
    section("03", "Challenge the baseline")
    with st.expander(
        "Why is this signal here?",
        expanded=st.session_state.comparison == "8-week baseline"
        or st.session_state.get("demo_step") == 2,
    ):
        baseline_evidence(selected, fingerprint)
    section("04", "Reveal the contributors")
    with st.expander("Show contributors", expanded=st.session_state.get("demo_step") == 3):
        bridge = inv["bridge"]
        fig = go.Figure(
            go.Waterfall(
                x=bridge.contributor,
                y=bridge.impact,
                measure=["relative"] * len(bridge),
                increasing=dict(marker_color=ACCENT),
                decreasing=dict(marker_color="#8C969D"),
                connector=dict(line_color="#465057"),
            )
        )
        fig.update_yaxes(title_text="Operating-profit contribution / AUD")
        chart(
            fig,
            "Which ledger movements reconcile the profit change?",
            f"Observed change {money(current['operating_profit'] - before['operating_profit'])}. Equal-length prior period {inv['prior_start']} to {inv['prior_end']}; different from the warning median. No causal inference.",
        )
        table(bridge)
        dim = st.selectbox("Business driver", list(DIMENSIONS), key="contribution_dimension")
        frame = contributions(ctx["start"], ctx["end"], dim, ctx["location"], fingerprint[0])
        chart(
            go.Figure(
                go.Bar(
                    x=frame.head(10).entity.astype(str),
                    y=frame.head(10).contribution,
                    marker_color=SILVER,
                )
            ),
            f"Where did revenue move? · {dim}",
            "Ten largest adverse contributors shown; all rows reconcile to observed net-sales movement. Basket combines price, quantity and mix.",
        )
        table(frame)
    section("05", "Understand estimated exposure")
    if selected and selected["estimated_profit_exposure"] > 0:
        narrative(
            f"{money(selected['estimated_profit_exposure'])} estimated weekly reference gap.",
            "This warning estimate is not achieved savings. Related revenue, profit and payroll gaps overlap; do not add them.",
            "ESTIMATED",
        )
    else:
        caption(
            "This context has no monetary warning estimate. Observed profit movement is available above; it is a different quantity from warning exposure."
        )
    section("06", "Choose a meaningful comparison")
    with st.expander(
        "Compare locations, periods or baseline",
        expanded=st.session_state.get("comparison") != "Previous period",
    ):
        comparison(ctx, inv, fingerprint)
    section("07", "What would you investigate next?")
    path = st.radio(
        "Investigation path",
        [
            "Review labour hours",
            "Investigate discounting",
            "Compare product mix",
            "Review stock availability",
        ],
        key="decision_path",
        horizontal=True,
    )
    if path == "Review labour hours":
        model = simulate(current, Assumptions(hours_change=-0.05))
        narrative(
            f"A 5% hours reduction changes modelled operating profit by {money(model['operating_profit'] - current['operating_profit'])}.",
            f"Observed satisfaction {current['satisfaction']:.2f}/5 versus {before['satisfaction']:.2f} previously. Service response is not modelled; agree guardrails and a demand sensitivity before a pilot.",
            "SCENARIO / SERVICE TRADE-OFF",
        )
        st.button(
            "Model this scenario",
            key="path_model",
            type="primary",
            on_click=preset_scenario,
            args=(-5,),
        )
    elif path == "Investigate discounting":
        narrative(
            f"Discount cost changed by {money(current['discounts'] - before['discounts'])}.",
            "Review campaign economics and customer response. Association is not incremental causal ROI.",
        )
        from app.lenses import campaigns

        campaigns(ctx, fingerprint)
    elif path == "Compare product mix":
        frame = contributions(ctx["start"], ctx["end"], "Product", ctx["location"], fingerprint[0])
        table(frame.head(8))
        caption(
            "Product-level revenue contribution. Price, unit quantity and mix effects are combined in the profit bridge."
        )
    else:
        from app.lenses import availability

        availability(ctx, fingerprint)
    if st.checkbox("Review customer, operations or forecast evidence", key="secondary_evidence"):
        lens = st.radio(
            "Evidence lens",
            ["Customer", "Operations", "Forecast"],
            horizontal=True,
            key="evidence_lens",
        )
        from app.lenses import customers, operations, forecasts

        {"Customer": customers, "Operations": operations, "Forecast": forecasts}[lens](
            ctx, fingerprint
        )
    section("08", "Test the decision assumptions")
    primary, secondary, brief_action = st.columns(3)
    primary.button(
        "Open Scenario Lab",
        key="investigation_scenario",
        on_click=navigate,
        args=(st.session_state, "Scenario Lab"),
        type="primary",
    )
    secondary.button(
        "Ask PULSE with this context",
        key="investigation_ask",
        on_click=navigate,
        args=(st.session_state, "Ask PULSE"),
    )
    if selected:
        brief_action.button(
            "Add evidence to brief",
            key="investigation_brief",
            on_click=add_finding,
            args=(selected,),
            disabled=any(
                item["id"] == signal_id(selected) for item in st.session_state.brief_items
            ),
        )
    else:
        brief_action.button(
            "Review company brief", on_click=navigate, args=(st.session_state, "Briefs")
        )
    section("09", "Document the next decision")
    with st.form("decision_record"):
        owner = st.text_input("Proposed owner / role", value="Regional Operations Manager")
        action = st.text_area(
            "Next investigation or bounded pilot",
            value="Reconcile roster and product/channel mix with the location manager; agree service guardrails before any staffing change.",
        )
        guardrails = st.text_input(
            "Guardrails and review",
            value="Review satisfaction, demand and margin for the next four complete weeks.",
        )
        submitted = st.form_submit_button("Record proposal")
    if submitted:
        if not owner.strip() or not action.strip() or not guardrails.strip():
            st.error("An owner, investigation and review guardrails are required.")
        else:
            st.session_state.decisions.append(
                dict(
                    status="Proposed; unapproved",
                    owner=owner.strip(),
                    action=action.strip(),
                    guardrails=guardrails.strip(),
                    context=ctx.copy(),
                    observed_profit=current["operating_profit"],
                )
            )
            st.success(
                "Proposal recorded for this session and available in Briefs. Export to retain it."
            )
    if st.session_state.decisions:
        caption(
            f"{len(st.session_state.decisions)} session proposals · no real approval or achieved benefits"
        )
        st.download_button(
            "Export decision log",
            json.dumps(st.session_state.decisions, indent=2),
            "pulse_decisions.json",
            "application/json",
        )
