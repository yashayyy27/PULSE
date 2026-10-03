"""Context-aware simulation, deterministic questions and an executive workspace."""

from dataclasses import asdict
from html import escape
import json

import pandas as pd
import streamlit as st

from app import data
from app.briefing import build_brief, export_html
from app.components import (
    caption,
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
    section,
    table,
)
from app.state import (
    add_to_brief,
    context_question,
    move_brief,
    navigate,
    remove_brief,
    reset_assumptions,
    update_scenario_inputs,
    SCENARIO_DEFAULTS,
    context,
    set_context,
)
from pulse.metrics.registry import REGISTRY
from pulse.query.ask import answer
from pulse.scenarios.engine import ASSUMPTION_TEXT, Assumptions, simulate

SCENARIO_KEYS = [
    "revenue",
    "gross_profit",
    "operating_profit",
    "gross_margin",
    "operating_margin",
    "labour_pct",
]


def save_scenario(name, ctx, assumptions, base, result):
    if not name.strip():
        st.session_state.feedback = "Give the scenario a comparison label before saving."
        return
    record = dict(
        name=name.strip(),
        context=ctx.copy(),
        assumptions=asdict(assumptions),
        base={k: base[k] for k in SCENARIO_KEYS},
        result={k: result[k] for k in SCENARIO_KEYS},
    )
    if record not in st.session_state.scenarios:
        st.session_state.scenarios.append(record)
    st.session_state.feedback = "Scenario saved for comparison and the executive brief. No approval or achieved benefit is implied."


def remove_scenario(index):
    if 0 <= index < len(st.session_state.scenarios):
        st.session_state.scenarios.pop(index)
    st.session_state.pop("saved_scenario_selection", None)


def remember_scenario():
    fields = [*SCENARIO_DEFAULTS, "discount_rate", "product_margin"]
    saved = st.session_state.setdefault("scenario_inputs", {})
    saved.update(
        {
            field: st.session_state["scenario_" + field]
            for field in fields
            if "scenario_" + field in st.session_state
        }
    )


def scenarios(ctx, fingerprint):
    header(
        "Test the decision before the decision.",
        "Adjust the operating assumptions. See the commercial difference. Keep the trade-offs visible.",
        "SCENARIO LAB / CONDITIONAL SIMULATOR",
    )
    base = data.measured(ctx["start"], ctx["end"], ctx["location"], fingerprint)
    for field, value in st.session_state.get("scenario_inputs", {}).items():
        st.session_state["scenario_" + field] = value
    caption(
        f"Inherited baseline: {ctx['entity']} · {ctx['start']} to {ctx['end']} · {REGISTRY[ctx['kpi']].name} context · AUD excluding GST"
    )
    st.button(
        "Reset assumptions",
        key="scenario_reset",
        on_click=reset_assumptions,
        args=(st.session_state,),
    )
    results, controls = st.columns([1.45, 1], gap="large")
    with controls:
        label("CHANGE THE ASSUMPTIONS")
        values = {}
        for field, title, lower, upper in [
            ("price_change", "Average price change %", -30, 30),
            ("transaction_change", "Transactions / demand change %", -30, 30),
            ("basket_change", "Basket quantity / AOV change %", -30, 30),
            ("hours_change", "Labour hours change %", -30, 30),
            ("wage_change", "Loaded hourly labour cost change %", -20, 20),
        ]:
            values[field] = (
                st.slider(
                    title, lower, upper, 0, key="scenario_" + field, on_change=remember_scenario
                )
                / 100
            )
        with st.expander("Retention, promotion and product economics"):
            values["retention_change"] = (
                st.slider(
                    "Retention response change %",
                    -30,
                    30,
                    0,
                    key="scenario_retention_change",
                    on_change=remember_scenario,
                )
                / 100
            )
            values["promotion_uptake_change"] = (
                st.slider(
                    "Additional promotion uptake (percentage points)",
                    0,
                    30,
                    0,
                    key="scenario_promotion_uptake_change",
                    on_change=remember_scenario,
                )
                / 100
            )
            discount_on = st.checkbox(
                "Replace discount rate",
                key="scenario_replace_discount",
                on_change=remember_scenario,
            )
            discount = st.slider(
                "Replacement discount rate %",
                0.0,
                50.0,
                min(50.0, base["discounts"] / base["list_sales"] * 100),
                step=0.1,
                disabled=not discount_on,
                key="scenario_discount_rate",
                on_change=remember_scenario,
            )
            margin_on = st.checkbox(
                "Replace product margin on list sales",
                key="scenario_replace_margin",
                on_change=remember_scenario,
            )
            margin = st.slider(
                "Replacement product margin %",
                0.0,
                95.0,
                min(95.0, max(0.0, (1 - base["cogs"] / base["list_sales"]) * 100)),
                step=0.1,
                disabled=not margin_on,
                key="scenario_product_margin",
                on_change=remember_scenario,
            )
            values["discount_rate"] = discount / 100 if discount_on else None
            values["product_margin"] = margin / 100 if margin_on else None
    assumptions = Assumptions(**values)
    st.session_state.scenario_inputs = {
        key.removeprefix("scenario_"): st.session_state[key]
        for key in [
            "scenario_price_change",
            "scenario_transaction_change",
            "scenario_basket_change",
            "scenario_hours_change",
            "scenario_wage_change",
            "scenario_retention_change",
            "scenario_promotion_uptake_change",
            "scenario_replace_discount",
            "scenario_replace_margin",
            "scenario_discount_rate",
            "scenario_product_margin",
        ]
    }
    try:
        result = simulate(base, assumptions)
    except ValueError as error:
        st.error(f"PULSE could not run these assumptions: {error}")
        caption("Reset assumptions to restore the observed ledger.")
        return
    st.session_state.scenario_current = dict(
        context=ctx.copy(),
        assumptions=asdict(assumptions),
        base={k: base[k] for k in SCENARIO_KEYS},
        result={k: result[k] for k in SCENARIO_KEYS},
    )
    with results:
        with st.container(key="scenario_result"):
            label("OPERATING PROFIT / LIVE SCENARIO")
            change = result["operating_profit"] - base["operating_profit"]
            html(
                f'<div class="hero-score accent scenario-delta">{escape(delta("operating_profit", change))}</div>'
            )
            caption(
                "Conditional change from the observed base case. Results recalculate when a control changes."
            )
            html(
                '<div class="comparison-row"><span>METRIC</span><span>BASE CASE</span><span>SCENARIO</span><span>DELTA</span></div>'
            )
            for key in SCENARIO_KEYS:
                html(
                    f'<div class="comparison-row"><span>{escape(REGISTRY[key].name)}</span><strong>{escape(display(key, base[key]))}</strong><strong>{escape(display(key, result[key]))}</strong><strong class="accent">{escape(delta(key, result[key] - base[key]))}</strong></div>'
                )
        section("01", "Assumptions changed")
        changed = []
        for field, value in asdict(assumptions).items():
            if value is not None and value != 0:
                changed.append(
                    {
                        "Assumption": field.replace("_", " ").title(),
                        "Value": f"{value:+.1%}"
                        if field not in ["discount_rate", "product_margin"]
                        else f"{value:.1%} replacement",
                    }
                )
        if changed:
            table(pd.DataFrame(changed))
        else:
            caption("No assumptions changed. The scenario equals the observed base case exactly.")
        narrative(
            "This is a conditional scenario, not a forecast or guaranteed outcome.",
            f"Observed satisfaction {base['satisfaction']:.2f}/5. No automatic price elasticity, staffing feasibility or service-response effect is modelled.",
            "SCENARIO / LIMITS",
        )
        with st.expander("Inspect model assumptions"):
            st.write(ASSUMPTION_TEXT)
        explain_metric(ctx["kpi"], "scenario_metric")
        name = st.text_input(
            "Scenario comparison label", value="Proposed operating case", key="scenario_name"
        )
        st.button(
            "Save scenario to brief & comparison",
            key="scenario_save",
            type="primary",
            on_click=save_scenario,
            args=(name, ctx, assumptions, base, result),
        )
    section(
        "02",
        "Considered scenarios",
        "Saved cases retain their original scope, period and inputs. Session-only until exported.",
    )
    saved = st.session_state.scenarios
    if not saved:
        caption("Save a case above to include its assumptions and result in the executive brief.")
    else:
        table(
            pd.DataFrame(
                [
                    {
                        "Scenario": s["name"],
                        "Scope": s["context"]["entity"],
                        "Period": s["context"]["end"],
                        "Base profit": money(s["base"]["operating_profit"]),
                        "Scenario profit": money(s["result"]["operating_profit"]),
                        "Delta": money(
                            s["result"]["operating_profit"] - s["base"]["operating_profit"]
                        ),
                    }
                    for s in saved
                ]
            )
        )
        selected = (
            st.selectbox(
                "Saved scenario",
                list(range(len(saved))),
                format_func=lambda i: f"{i + 1}. {saved[i]['name']} / {saved[i]['context']['entity']}",
                key="saved_scenario_selection",
            )
            if len(saved) > 1
            else 0
        )
        st.button("Remove saved scenario", on_click=remove_scenario, args=(selected,))
        st.download_button(
            "Export scenario comparison",
            json.dumps(saved, indent=2),
            "pulse_scenarios.json",
            "application/json",
        )
    st.button("Continue to executive brief →", on_click=navigate, args=(st.session_state, "Briefs"))


def contextual_answer(question, ctx, fingerprint, selected):
    if question.strip().lower() in ["why is this signal here?", "how unusual is this result?"]:
        if not selected:
            return {
                "supported": False,
                "answer": "Choose a current signal to inspect its warning reference. Try a profit or labour question for the current scope.",
                "evidence": None,
            }
        return dict(
            supported=True,
            intent="warning_reference",
            answer=f"{selected['entity']} {REGISTRY[selected['kpi']].name.lower()} is {display(selected['kpi'], selected['actual'])} against the prior-eight-week median {display(selected['kpi'], selected['baseline'])}. Robust z {selected['robust_z']:+.2f} crosses the configured threshold.",
            evidence=pd.DataFrame(
                [
                    {
                        k: selected[k]
                        for k in [
                            "actual",
                            "baseline",
                            "expected_low",
                            "expected_high",
                            "variance",
                            "robust_z",
                            "estimated_profit_exposure",
                        ]
                    }
                ]
            ),
            scope=selected["entity"],
            period=f"{selected['period_start']} to {selected['timestamp']}",
            method=selected["method"],
            limitations="Heuristic reference, not calibrated probability. No holiday adjustment; accounting evidence does not establish cause.",
        )
    locations = data.locations(fingerprint)
    named = [row for row in locations.to_dict("records") if row["name"].lower() in question.lower()]
    if ctx["location"] is not None and any(row["location_id"] != ctx["location"] for row in named):
        return {
            "supported": False,
            "answer": "This question names another location. Change or reset context first so the analytical scope stays explicit.",
            "evidence": None,
        }
    result = answer(context_question(question, ctx), fingerprint[0])
    if result["supported"]:
        if result["scope"] != "Company":
            row = locations.loc[locations.location_id == int(result["scope"])]
            result["scope"] = row.iloc[0]["name"]
        result["effective_question"] = context_question(question, ctx)
    return result


def analyse_question(question):
    st.session_state.ask_question = question
    st.session_state.ask_text = question
    with st.spinner("Reading the governed evidence…"):
        st.session_state.ask_result = contextual_answer(
            question, st.session_state.context, data.snapshot(), st.session_state.selected_signal
        )


def edit_question():
    st.session_state.ask_text = st.session_state.ask_question
    st.session_state.pop("ask_result", None)


def ask(ctx, fingerprint):
    header(
        "Ask your business a better question.",
        "A focused evidence workspace. Bounded analytical intents, visible numbers and honest limits.",
        "ASK PULSE / DETERMINISTIC ANALYTICAL ENGINE",
    )
    st.session_state.setdefault("ask_question", st.session_state.get("ask_text", ""))
    result = st.session_state.get("ask_result")
    with st.container(key="ask_workspace"):
        label(f"CURRENT CONTEXT / {ctx['entity']} / {ctx['start']} → {ctx['end']}")
        caption(
            "Profit, margin, labour and dimensional questions retain the current location. Promotions are company-wide; attention always uses the latest complete week. Explicit “last month” changes the answer window and is shown with the result."
        )
        question_area, suggestions_area = st.columns([1.2, 1], gap="large")
        with question_area:
            question = st.text_input(
                "Ask your business a question…",
                placeholder="What contributed to the profit movement?",
                key="ask_question",
                on_change=edit_question,
            )
            st.session_state.ask_text = question
            st.button(
                "Analyse question",
                key="ask_analyse",
                type="primary",
                on_click=analyse_question,
                args=(question,),
            )
            if result:
                narrative(result["answer"], tag="ANALYTICAL ANSWER")
            else:
                caption("Choose a supported question. No external model or generated SQL.")
        with suggestions_area:
            label("QUESTIONS WORTH ASKING")
            suggestions = (
                [
                    "Why is this signal here?",
                    "What contributed to profit movement?",
                    "Where is labour percentage increasing?",
                    "Which product contributed to revenue movement?",
                ]
                if st.session_state.selected_signal
                else [
                    "Why did operating profit change this week?",
                    "Which locations need attention?",
                    "Where is labour percentage increasing?",
                    "Which promotion performed poorly?",
                ]
            )
            for index, suggestion in enumerate(suggestions):
                st.button(
                    suggestion,
                    key="ask_suggestion_" + str(index),
                    on_click=analyse_question,
                    args=(suggestion,),
                )
    result = st.session_state.get("ask_result")
    if not result:
        caption(
            "Choose a suggested question or enter a supported business question. No external model, generated SQL or fabricated evidence."
        )
        return
    section("01", "What the evidence says")
    if result["supported"]:
        caption(
            f"Scope: {result['scope']} · period: {result['period']} · observed / estimated as labelled"
        )
        frame = result["evidence"]
        if frame.empty:
            empty(
                "No supported evidence rows for this question.",
                "The analytical scope and method remain shown. Choose a different supported question.",
            )
        else:
            table(frame)
        with st.expander("Explain the method and limits"):
            st.write(result["method"])
            st.info(result["limitations"])
        st.download_button(
            "Export answer evidence",
            frame.to_csv(index=False),
            "pulse_answer_evidence.csv",
            "text/csv",
        )
        section("02", "Follow the evidence")
        left, right = st.columns(2)
        left.button(
            "Review investigation evidence",
            on_click=investigate_answer,
            args=(result,),
        )
        right.button("Model a labour-hour sensitivity", on_click=route_labour, args=(result,))
        st.button(
            "What contributed to product movement?",
            key="ask_followup",
            on_click=analyse_question,
            args=("Which product contributed to revenue movement?",),
        )
    else:
        st.info(
            "Supported paths: profit/margin, warning reference, attention, labour, promotion and product/channel/customer-segment movement."
        )


def apply_answer_context(result):
    start, end = result["period"].split(" to ")
    location, entity, state = None, "Company", "All"
    if result["scope"] != "Company":
        row = (
            data.locations(data.snapshot()).loc[lambda frame: frame.name == result["scope"]].iloc[0]
        )
        location, entity, state = int(row.location_id), row["name"], row.state
    new_context = context(start, end, location, entity, state)
    selected = st.session_state.selected_signal
    if selected and (
        selected["period_start"],
        selected["timestamp"],
        int(selected["location_id"]),
    ) == (start, end, location):
        new_context["kpi"] = selected["kpi"]
    else:
        selected = None
    set_context(st.session_state, new_context, selected)


def investigate_answer(result):
    apply_answer_context(result)
    navigate(st.session_state, "Investigate")


def route_labour(result):
    apply_answer_context(result)
    update_scenario_inputs(st.session_state, hours_change=-3)
    navigate(st.session_state, "Scenario Lab")


def include_priorities(fingerprint):
    for row in data.signals(fingerprint).drop_duplicates("location_id").head(3).to_dict("records"):
        add_to_brief(st.session_state, row)


def brief(ctx, fingerprint):
    header(
        "Turn evidence into an executive decision.",
        "Build a concise management brief from selected findings, considered scenarios and proposed next steps.",
        "BRIEFS / EXECUTIVE WORKSPACE",
    )
    caption(
        "Company health is the latest complete week. Each selected finding, scenario and proposal retains its own labelled location and period. Nothing is sent or approved."
    )
    workspace, preview = st.columns([1, 1.65], gap="large")
    with workspace:
        label("SELECTED FINDINGS")
        if not st.session_state.brief_items:
            empty(
                "Your brief has no selected findings.",
                "Add evidence from Signals or Investigate, or include the three current priority locations.",
            )
        st.button(
            "Include current priority findings",
            key="brief_priorities",
            on_click=include_priorities,
            args=(fingerprint,),
            type="primary",
        )
        for index, item in enumerate(st.session_state.brief_items):
            row = item["signal"]
            st.markdown(f"**{index + 1:02d} · {row['entity']} / {REGISTRY[row['kpi']].name}**")
            caption(f"{row['period_start']} to {row['timestamp']} · {row['severity']}")
            up, down, remove = st.columns(3)
            up.button(
                "Move up",
                key="brief_up_" + item["id"],
                disabled=index == 0,
                on_click=move_brief,
                args=(st.session_state, item["id"], -1),
            )
            down.button(
                "Move down",
                key="brief_down_" + item["id"],
                disabled=index == len(st.session_state.brief_items) - 1,
                on_click=move_brief,
                args=(st.session_state, item["id"], 1),
            )
            remove.button(
                "Remove",
                key="brief_remove_" + item["id"],
                on_click=remove_brief,
                args=(st.session_state, item["id"]),
            )
        section("01", "Scenario & decision records")
        caption(
            f"{len(st.session_state.scenarios)} considered scenarios · {len(st.session_state.decisions)} unapproved proposals"
        )
        st.button(
            "Consider a scenario",
            key="brief_scenario",
            on_click=navigate,
            args=(st.session_state, "Scenario Lab"),
        )
        st.button(
            "Document next investigation",
            key="brief_decision",
            on_click=navigate,
            args=(st.session_state, "Investigate"),
        )
        caption("Session workspace. Export before closing the browser to retain your evidence.")
    output = build_brief(
        fingerprint,
        st.session_state.brief_items,
        st.session_state.scenarios,
        st.session_state.decisions,
    )
    with preview:
        with st.container(key="brief_preview"):
            label(f"PULSE / MANAGEMENT BRIEF / WEEK ENDING {output['week_ending']}")
            st.subheader("Business health")
            metrics(output["business_health"], keys=["revenue", "operating_profit"])
            caption(
                f"Health index {output['health_index']['overall']:.0f}/100 · {output['warning_count']} latest-week warnings · full-company profit exposure {money(output['estimated_weekly_profit_exposure'])}"
            )
            st.subheader("Priority signals & evidence")
            for item in output["top_issues"]:
                narrative(
                    f"{item['entity']} / {REGISTRY[item['issue']].name}: {display(item['issue'], item['actual'])} against {display(item['issue'], item['baseline'])} median.",
                    f"{item['period_start']} to {item['period_end']} · {item['severity']}",
                )
                caption(
                    "Associated ledger contributors: "
                    + "; ".join(
                        f"{r['contributor']} {money(r['impact'])}" for r in item["evidence"]
                    )
                )
            if not output["top_issues"]:
                caption("Select evidence to build this section.")
            st.subheader("Estimated exposure")
            narrative(
                f"{money(output['selected_profit_exposure'])} across selected operating-profit signals.",
                "Counted once per location; other KPI gaps overlap. Reference exposure, not recovered profit.",
                "ESTIMATED",
            )
            st.subheader("Scenario considered")
            for s in output["scenarios_considered"]:
                caption(
                    f"{s['name']} · {s['context']['entity']} · {s['context']['start']} to {s['context']['end']}"
                )
                narrative(
                    f"Modelled operating-profit difference {money(s['result']['operating_profit'] - s['base']['operating_profit'])}.",
                    "Conditional assumptions; no forecast or achieved benefit.",
                    "SCENARIO",
                )
            if not output["scenarios_considered"]:
                caption("No saved scenario. Open Scenario Lab to consider an intervention.")
            st.subheader("Decision required")
            for action in output["decisions_required"]:
                st.write(action)
            for decision in output["session_proposals"]:
                caption(
                    f"{decision['owner']} · {decision['status']} · {decision['context']['entity']} · {decision['guardrails']}"
                )
            st.subheader("Next investigation")
            st.write(
                "Reconcile roster, discounting and product/channel mix with the location manager. Agree service and demand guardrails before a bounded pilot."
            )
            st.subheader("Risks & limitations")
            caption(
                output["limitations"]
                + " Contributions are associations. Warning references and forecast bands are heuristic. No real stakeholder validation."
            )
        left, right = st.columns(2)
        left.download_button(
            "Export HTML executive brief",
            export_html(output),
            "pulse_executive_brief.html",
            "text/html",
            type="primary",
        )
        right.download_button(
            "Export briefing evidence JSON",
            json.dumps(output, indent=2, allow_nan=False),
            "pulse_brief.json",
            "application/json",
        )
