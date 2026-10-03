"""A reversible guided analytical case built from actual warning output."""

import streamlit as st

from app import data
from app.state import add_to_brief, navigate, select_signal

STEPS = [
    (
        "Home",
        "A business signal, not a wall of charts.",
        "Select the highest-exposure operating-profit warning. The index, gap and timeline use actual synthetic outputs.",
    ),
    (
        "Investigate",
        "Open the exact signal.",
        "The store, KPI and complete-week period follow you. Observed values are separate from reference estimates.",
    ),
    (
        "Investigate",
        "Challenge why it triggered.",
        "Inspect the prior eight weeks, median/MAD reference and thresholds in the expanded baseline section.",
    ),
    (
        "Investigate",
        "Reveal the accounting evidence.",
        "The expanded bridge reconciles to the previous-week profit difference. Contributors are associations, not proven causes.",
    ),
    (
        "Investigate",
        "Understand the commercial reference gap.",
        "Exposure uses a different comparison from the profit bridge. Related KPI gaps overlap and cannot be added.",
    ),
    (
        "Investigate",
        "Choose an investigation path.",
        "Review labour, discounting, product mix or availability. The labour preview makes a service trade-off explicit.",
    ),
    (
        "Scenario Lab",
        "Test a bounded intervention.",
        "Begin with −3% hours and −1% demand. Change either control and inspect the conditional profit difference; service response is untested.",
    ),
    (
        "Briefs",
        "Bring the evidence into a brief.",
        "The selected signal and considered scenario retain their scope and assumptions. Order or remove findings before exporting.",
    ),
    (
        "Briefs",
        "Document a proposed decision.",
        "An explicitly fictional, unapproved pilot proposal includes service/demand guardrails. Export the real HTML brief to retain this session.",
    ),
]


def start_demo():
    fingerprint = data.snapshot()
    frame = data.signals(fingerprint)
    profit = frame[frame.kpi == "operating_profit"]
    source = profit if not profit.empty else frame
    if source.empty:
        st.session_state.feedback = "No computed weekly warning is available for a signal-led demo. Explore the observed company investigation instead."
        navigate(st.session_state, "Investigate")
        return
    row = source.iloc[0].to_dict()
    st.session_state.demo_signal = row
    select_signal(st.session_state, row, data.locations(fingerprint))
    st.session_state.demo_step = 0
    navigate(st.session_state, STEPS[0][0])


def demo_move(offset):
    previous = st.session_state.demo_step
    target = max(0, min(len(STEPS) - 1, previous + offset))
    if previous == 6 and offset > 0:
        current = st.session_state.get("scenario_current")
        if current and current["context"] == st.session_state.context:
            record = {"name": "Guided case: considered operating assumptions", **current}
            if record not in st.session_state.scenarios:
                st.session_state.scenarios.append(record)
    st.session_state.demo_step = target
    if target == 6 and previous != 7:
        from app.state import update_scenario_inputs

        update_scenario_inputs(st.session_state, hours_change=-3, transaction_change=-1)
    if target >= 7:
        add_to_brief(st.session_state, st.session_state.demo_signal)
    if target == 8:
        proposal = dict(
            status="Proposed; unapproved",
            owner="Fictional Regional Operations Manager",
            action="Validate roster and demand assumptions, then consider a bounded staffing pilot; no approval or achieved benefit claimed.",
            guardrails="Compare margin, demand and satisfaction over four complete weeks; stop and review if service deteriorates.",
            context=st.session_state.context.copy(),
        )
        if proposal not in st.session_state.decisions:
            st.session_state.decisions.append(proposal)
    navigate(st.session_state, STEPS[target][0])


def exit_demo():
    st.session_state.demo_step = None
    st.session_state.feedback = (
        "Guided demo closed. Your selected context and saved evidence remain available."
    )


def render_demo():
    step = st.session_state.get("demo_step")
    if step is None:
        return
    with st.container(key="demo_banner"):
        title = STEPS[step][1]
        st.caption(f"90-SECOND GUIDED CASE · {step + 1} / {len(STEPS)} · ACTUAL SYNTHETIC EVIDENCE")
        st.subheader(title)
        st.write(STEPS[step][2])
        st.progress((step + 1) / len(STEPS))
        back, forward, exit_action = st.columns(3)
        back.button("Back", key="demo_back", disabled=step == 0, on_click=demo_move, args=(-1,))
        forward.button(
            "Next" if step < len(STEPS) - 1 else "Case complete",
            key="demo_next",
            disabled=step == len(STEPS) - 1,
            on_click=demo_move,
            args=(1,),
            type="primary",
        )
        exit_action.button("Exit demo", key="demo_exit", on_click=exit_demo)
