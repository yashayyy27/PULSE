"""Boundary tests for scope preservation, reset semantics and curated evidence."""

import hashlib
import json

import pandas as pd
import pytest

from app.advanced import contextual_answer
from app.briefing import build_brief, export_html
from app.data import pulse_timeline
from app.state import (
    PAGES,
    acknowledge,
    add_to_brief,
    context,
    context_question,
    filter_signals,
    initialise,
    move_brief,
    navigate,
    remove_brief,
    reset_assumptions,
    reset_context,
    select_signal,
    signal_id,
)
from pulse.alerts.engine import detect, exposure_summary
from pulse.analytics.core import ledger, latest_week
from pulse.analytics.health import health
from pulse.runtime import ROOT, query


def seeded(demo):
    state = {}
    initialise(state, *latest_week(demo))
    row = detect(demo).iloc[0].to_dict()
    select_signal(state, row, query("SELECT * FROM dim_location", path=demo))
    return state, row


def test_context_and_navigation_boundaries(demo):
    state, row = seeded(demo)
    original = state["context"].copy()
    for page in PAGES:
        navigate(state, page)
        assert state["context"] == original
    with pytest.raises(ValueError):
        navigate(state, "Unknown")
    with pytest.raises(ValueError):
        context("2025-12-28", "2025-12-22")
    assert row["location_id"] == original["location"]


def test_reset_retains_frozen_evidence_and_removes_derived_state(demo):
    state, row = seeded(demo)
    add_to_brief(state, row)
    state["ask_result"] = {"stale": True}
    state["scenario_hours_change"] = -5
    state["demo_step"] = 4
    reset_context(state, *latest_week(demo))
    assert state["context"]["location"] is None and state["demo_step"] is None
    assert state["brief_items"][0]["signal"] == row
    assert "ask_result" not in state and state["scenario_hours_change"] == 0


def test_acknowledgment_filters_and_brief_idempotence(demo):
    state, row = seeded(demo)
    acknowledge(state, row)
    frame = detect(demo)
    out = filter_signals(frame, state["signal_status"], entity=row["entity"], status="Acknowledged")
    assert signal_id(out.iloc[0]) == signal_id(row)
    assert filter_signals(frame, {}, kpi="retention").empty
    add_to_brief(state, row)
    add_to_brief(state, row)
    assert len(state["brief_items"]) == 1
    # A saved finding is immutable even after changing the selected row.
    row["actual"] = 999
    assert state["brief_items"][0]["signal"]["actual"] != 999


def test_brief_order_boundaries_and_removal(demo):
    state, _ = seeded(demo)
    rows = detect(demo).head(3).to_dict("records")
    for row in rows:
        add_to_brief(state, row)
    original = [item["id"] for item in state["brief_items"]]
    move_brief(state, original[0], -1)
    assert [i["id"] for i in state["brief_items"]] == original
    move_brief(state, original[1], -1)
    assert state["brief_items"][0]["id"] == original[1]
    move_brief(state, "missing", 1)
    remove_brief(state, original[1])
    assert len(state["brief_items"]) == len(original) - 1


def test_assumption_reset_does_not_replace_baseline_rates():
    state = {
        "scenario_replace_discount": True,
        "scenario_discount_rate": 30,
        "scenario_product_margin": 65,
        "scenario_current": {},
        "scenarios": [{"saved": True}],
    }
    reset_assumptions(state)
    assert not state["scenario_replace_discount"]
    assert "scenario_discount_rate" not in state and "scenario_current" not in state
    assert state["scenarios"] == [{"saved": True}]


def test_ask_scope_period_invalid_and_cross_store(demo):
    state, row = seeded(demo)
    fingerprint = (str(demo), demo.stat().st_mtime_ns, demo.stat().st_size)
    ctx = state["context"]
    result = contextual_answer("What contributed to profit movement?", ctx, fingerprint, row)
    assert result["scope"] == ctx["entity"]
    assert result["period"] == f"{ctx['start']} to {ctx['end']}"
    baseline = contextual_answer("Why is this signal here?", ctx, fingerprint, row)
    assert baseline["evidence"].actual.iloc[0] == row["actual"]
    another = query(
        "SELECT name FROM dim_location WHERE location_id<>? LIMIT 1", (ctx["location"],), demo
    ).iloc[0, 0]
    assert not contextual_answer(f"profit in {another}", ctx, fingerprint, row)["supported"]
    assert not contextual_answer("DROP TABLE", ctx, fingerprint, row)["supported"]
    assert context_question("profit", {**ctx, "start": "2025-12-01", "end": "2025-12-31"}).endswith(
        "last month"
    )


def test_pulse_latest_point_matches_governed_ledger(demo):
    fingerprint = (str(demo), demo.stat().st_mtime_ns, demo.stat().st_size)
    frame = pulse_timeline(None, latest_week(demo)[1], fingerprint)
    assert len(frame) == 12
    expected = health(ledger(*latest_week(demo), path=demo))["overall"]
    assert frame.health.iloc[-1] == pytest.approx(expected)
    assert frame.week.iloc[-1] == latest_week(demo)[1]


def test_curated_brief_exposure_and_escaped_real_html(demo):
    state, row = seeded(demo)
    for row in detect(demo).head(5).to_dict("records"):
        add_to_brief(state, row)
    fingerprint = (str(demo), demo.stat().st_mtime_ns, demo.stat().st_size)
    proposal = dict(
        owner="<script>bad</script>",
        status="Proposed; unapproved",
        action="Review hours",
        guardrails="Service review",
        context=state["context"],
    )
    brief = build_brief(fingerprint, state["brief_items"], [], [proposal])
    assert brief["selected_profit_exposure"] == exposure_summary(
        pd.DataFrame(brief["selected_signals"])
    )
    assert len(brief["top_issues"]) == len(state["brief_items"])
    output = export_html(brief)
    assert "<script>bad</script>" not in output and "&lt;script&gt;" in output
    for title in [
        "Business health",
        "Priority signals",
        "Selected evidence",
        "Selected estimated exposure",
        "Scenario considered",
        "Decision required",
        "Next investigation",
        "Risks / limitations",
    ]:
        assert title in output
    json.dumps(brief, allow_nan=False)


def test_no_analytical_source_changes():
    manifest = json.loads((ROOT / "reports/ui_backend_baseline.json").read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
