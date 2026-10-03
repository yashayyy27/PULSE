"""Real product journeys; analytical regression tests remain unchanged."""

import pytest
from streamlit.testing.v1 import AppTest

from app.state import PAGES, signal_id
from pulse.runtime import ROOT


def boot(demo, monkeypatch, page="Home"):
    monkeypatch.setenv("PULSE_DB", str(demo))
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=45)
    app.session_state["nav"] = page
    return app.run()


def clean(app):
    assert not app.exception, [e.message for e in app.exception]
    assert not app.error, [e.value for e in app.error]


@pytest.mark.parametrize("page", PAGES)
def test_every_page(demo, monkeypatch, page):
    app = boot(demo, monkeypatch, page)
    clean(app)
    assert app.title and app.radio(key="nav").value == page
    assert not app.sidebar.radio


def test_navigation_and_decision(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    clean(app)
    selected = app.session_state["selected_signal"]
    ctx = app.session_state["context"].copy()
    assert ctx["location"] == selected["location_id"]
    assert (ctx["start"], ctx["end"], ctx["kpi"]) == (
        selected["period_start"],
        selected["timestamp"],
        selected["kpi"],
    )
    next(b for b in app.button if b.label == "Record proposal").click().run()
    record = app.session_state["decisions"][0]
    assert record["status"] == "Proposed; unapproved" and record["context"] == ctx
    app.button(key="investigation_brief").click().run()
    assert app.session_state["brief_items"][0]["id"] == signal_id(selected)
    app.button(key="investigation_scenario").click().run()
    assert app.session_state["context"] == ctx
    clean(app)


def test_scenario_compare_and_ask(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    ctx = app.session_state["context"].copy()
    app.button(key="investigation_scenario").click().run()
    base = app.session_state["scenario_current"]["base"]["operating_profit"]
    app.slider(key="scenario_hours_change").set_value(-10).run()
    assert app.session_state["scenario_current"]["result"]["operating_profit"] > base
    app.button(key="scenario_save").click().run()
    assert app.session_state["scenarios"][0]["assumptions"]["hours_change"] == -0.1
    assert app.session_state["scenarios"][0]["context"] == ctx
    app.button(key="scenario_reset").click().run()
    assert app.session_state["scenario_current"]["result"]["operating_profit"] == pytest.approx(
        base
    )
    app.radio(key="nav").set_value("Ask PULSE").run()
    app.button(key="ask_suggestion_1").click().run()
    result = app.session_state["ask_result"]
    assert result["supported"] and result["scope"] == ctx["entity"]
    assert result["period"] == f"{ctx['start']} to {ctx['end']}"
    clean(app)


@pytest.mark.parametrize(
    "key,value",
    [
        ("scenario_price_change", 2),
        ("scenario_transaction_change", -3),
        ("scenario_basket_change", 2),
        ("scenario_hours_change", -3),
        ("scenario_wage_change", 2),
        ("scenario_retention_change", 5),
        ("scenario_promotion_uptake_change", 5),
    ],
)
def test_independent_scenario_controls(demo, monkeypatch, key, value):
    app = boot(demo, monkeypatch, "Scenario Lab")
    initial = app.session_state["scenario_current"].copy()
    app.slider(key=key).set_value(value).run()
    changed = app.session_state["scenario_current"]
    assert changed["assumptions"][key.removeprefix("scenario_")] == value / 100
    assert changed["result"] != initial["result"]
    clean(app)


def test_rate_overrides_reset_exactly(demo, monkeypatch):
    app = boot(demo, monkeypatch, "Scenario Lab")
    initial = app.session_state["scenario_current"]["base"]
    for switch, slider, value in [
        ("scenario_replace_discount", "scenario_discount_rate", 20.0),
        ("scenario_replace_margin", "scenario_product_margin", 70.0),
    ]:
        app.checkbox(key=switch).check().run()
        app.slider(key=slider).set_value(value).run()
        clean(app)
    app.button(key="scenario_reset").click().run()
    result = app.session_state["scenario_current"]
    assert (
        result["assumptions"]["discount_rate"] is None
        and result["assumptions"]["product_margin"] is None
    )
    for key in initial:
        assert result["result"][key] == pytest.approx(initial[key])
    clean(app)


def test_widget_values_survive_navigation(demo, monkeypatch):
    app = boot(demo, monkeypatch, "Scenario Lab")
    app.slider(key="scenario_hours_change").set_value(-7).run()
    assert app.session_state["scenario_inputs"]["hours_change"] == -7
    app.radio(key="nav").set_value("Ask PULSE").run()
    app.text_input(key="ask_question").set_value("Why did profit change?").run()
    app.radio(key="nav").set_value("Briefs").run()
    app.radio(key="nav").set_value("Home").run()
    # Native sessions may retain a dormant default widget key after cleanup.
    app.session_state["scenario_hours_change"] = 0
    app.radio(key="nav").set_value("Scenario Lab").run()
    assert app.slider(key="scenario_hours_change").value == -7
    app.radio(key="nav").set_value("Ask PULSE").run()
    assert app.text_input(key="ask_question").value == "Why did profit change?"
    app.radio(key="nav").set_value("Signals").run()
    app.selectbox(key="filter_severity").set_value("WARNING").run()
    app.radio(key="nav").set_value("Home").run()
    app.radio(key="nav").set_value("Signals").run()
    assert app.selectbox(key="filter_severity").value == "WARNING"
    clean(app)


def test_signal_feed_filters_actions_and_empty_recovery(demo, monkeypatch):
    app = boot(demo, monkeypatch, "Signals")
    open_key = next(b.key for b in app.button if b.key and b.key.startswith("ack_"))
    sid = open_key.removeprefix("ack_")
    app.button(key=open_key).click().run()
    assert app.session_state["signal_status"][sid] == "Acknowledged"
    app.button(key="add_" + sid).click().run()
    assert app.session_state["brief_items"][0]["id"] == sid
    app.selectbox(key="filter_kpi").set_value("retention").run()
    assert any("No signals match these filters" in m.value for m in app.markdown)
    app.button(key="empty_reset").click().run()
    assert app.selectbox(key="filter_kpi").value == "All"
    app.button(key="compare_" + sid).click().run()
    assert app.radio(key="nav").value == "Investigate"
    assert app.session_state["comparison"] == "8-week baseline"
    clean(app)


@pytest.mark.parametrize("mode", ["Previous period", "Company", "State", "8-week baseline"])
def test_comparison_modes(demo, monkeypatch, mode):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    ctx = app.session_state["context"].copy()
    app.radio(key="comparison").set_value(mode).run()
    assert app.session_state["context"] == ctx
    clean(app)


@pytest.mark.parametrize(
    "path",
    [
        "Review labour hours",
        "Investigate discounting",
        "Compare product mix",
        "Review stock availability",
    ],
)
def test_investigation_paths(demo, monkeypatch, path):
    app = boot(demo, monkeypatch, "Investigate")
    app.radio(key="decision_path").set_value(path).run()
    app.checkbox(key="secondary_evidence").check().run()
    app.radio(key="evidence_lens").set_value("Operations").run()
    clean(app)  # Includes availability twice, with independent widget keys.


@pytest.mark.parametrize("lens", ["Customer", "Operations", "Forecast"])
def test_secondary_evidence_lenses(demo, monkeypatch, lens):
    app = boot(demo, monkeypatch, "Investigate")
    app.checkbox(key="secondary_evidence").check().run()
    app.radio(key="evidence_lens").set_value(lens).run()
    clean(app)
    assert app.dataframe
    if lens == "Forecast":
        for metric in ["revenue", "transactions", "gross_profit", "labour_hours"]:
            app.selectbox(key="forecast_metric").set_value(metric).run()
            clean(app)
            assert app.get("plotly_chart")


def test_scope_period_breadcrumb_and_reset(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    app.selectbox(key="investigation_period").set_value("Latest full month").run()
    assert app.session_state["context"]["start"].endswith("-01")
    assert app.session_state["selected_signal"] is None
    app.selectbox(key="investigation_location").set_value("Company").run()
    assert app.session_state["context"]["location"] is None
    app.button(key="breadcrumb_company").click().run()
    assert app.session_state["context"]["start"] == "2025-12-22"
    clean(app)


def test_brief_order_remove_exports(demo, monkeypatch):
    app = boot(demo, monkeypatch, "Briefs")
    app.button(key="brief_priorities").click().run()
    items = app.session_state["brief_items"]
    assert len(items) >= 2
    sid = items[1]["id"]
    app.button(key="brief_up_" + sid).click().run()
    assert app.session_state["brief_items"][0]["id"] == sid
    app.button(key="brief_down_" + sid).click().run()
    assert app.session_state["brief_items"][1]["id"] == sid
    app.button(key="brief_remove_" + sid).click().run()
    assert all(item["id"] != sid for item in app.session_state["brief_items"])
    assert len(app.get("download_button")) == 2
    clean(app)


def test_ask_suggestions_followup_invalid_and_context(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    ctx = app.session_state["context"].copy()
    app.button(key="investigation_ask").click().run()
    for index in range(4):
        app.button(key=f"ask_suggestion_{index}").click().run()
        assert app.session_state["ask_result"]["supported"]
        clean(app)
    app.button(key="ask_followup").click().run()
    assert app.session_state["ask_result"]["intent"] == "dimensional_movement"
    app.text_input(key="ask_question").set_value("DROP TABLE fact_sales").run()
    app.button(key="ask_analyse").click().run()
    assert not app.session_state["ask_result"]["supported"]
    assert app.session_state["context"] == ctx
    app.button(key="reset_context").click().run()
    assert app.session_state["context"]["location"] is None
    assert "ask_result" not in app.session_state
    clean(app)


def test_demo_next_back_exit_and_exports(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="start_demo").click().run()
    assert app.session_state["demo_step"] == 0
    original = app.session_state["context"].copy()
    for step in range(1, 9):
        app.button(key="demo_next").click().run()
        assert app.session_state["demo_step"] == step
        assert app.session_state["context"] == original
        clean(app)
    assert app.session_state["brief_items"] and app.session_state["scenarios"]
    assert app.session_state["decisions"][0]["status"] == "Proposed; unapproved"
    app.button(key="demo_back").click().run()
    assert app.session_state["demo_step"] == 7
    app.button(key="demo_exit").click().run()
    assert app.session_state["demo_step"] is None
    assert app.session_state["context"] == original
    app.radio(key="nav").set_value("Scenario Lab").run()
    assert app.slider(key="scenario_hours_change").value == -3
    assert app.slider(key="scenario_transaction_change").value == -1
    clean(app)


def test_form_validation_and_saved_case_removal(demo, monkeypatch):
    app = boot(demo, monkeypatch, "Investigate")
    next(t for t in app.text_input if t.label == "Proposed owner / role").set_value("").run()
    next(b for b in app.button if b.label == "Record proposal").click().run()
    assert not app.session_state["decisions"] and app.error
    app.radio(key="nav").set_value("Scenario Lab").run()
    app.text_input(key="scenario_name").set_value("").run()
    app.button(key="scenario_save").click().run()
    assert not app.session_state["scenarios"]
    app.text_input(key="scenario_name").set_value("Test case").run()
    app.button(key="scenario_save").click().run()
    next(b for b in app.button if b.label == "Remove saved scenario").click().run()
    assert not app.session_state["scenarios"]
    clean(app)


def test_source_missing_recovery(tmp_path, monkeypatch):
    monkeypatch.setenv("PULSE_DB", str(tmp_path / "missing.sqlite"))
    app = AppTest.from_file(str(ROOT / "app/main.py")).run()
    assert not app.exception
    assert any("No analytical snapshot" in e.value for e in app.error)
    assert any(b.label == "Retry snapshot" for b in app.button)


def test_system_health_invalid_and_recovery(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.radio(key="system_area").set_value("Health assumptions").run()
    for name in ["Financial", "Customer", "Operations", "Inventory"]:
        app.number_input(key="health_" + name).set_value(0).run()
    assert app.error
    next(b for b in app.button if b.label == "Restore health weights").click().run()
    clean(app)
    app.radio(key="system_area").set_value("Metric registry").run()
    clean(app)


def test_ask_followup_carries_effective_month_scope(demo, monkeypatch):
    app = boot(demo, monkeypatch)
    app.button(key="overview_investigate").click().run()
    entity = app.session_state["context"]["entity"]
    app.button(key="investigation_ask").click().run()
    app.text_input(key="ask_question").set_value("Why did profit change last month?").run()
    app.button(key="ask_analyse").click().run()
    result = app.session_state["ask_result"]
    next(b for b in app.button if b.label == "Review investigation evidence").click().run()
    assert app.session_state["context"]["entity"] == entity
    assert app.session_state["context"]["start"] == result["period"].split(" to ")[0]
    assert app.session_state["selected_signal"] is None
    clean(app)


def test_all_metric_explanations_are_registry_backed(demo, monkeypatch):
    from pulse.metrics.registry import REGISTRY

    app = boot(demo, monkeypatch)
    for key, metric in REGISTRY.items():
        app.selectbox(key="home_metric").set_value(key).run()
        assert metric.formula in [item.value for item in app.text]
        assert metric.source in [item.value for item in app.text]
        assert metric.limitation in [item.value for item in app.text]
        clean(app)


def test_source_validation_failure_and_recovery(demo, tmp_path, monkeypatch):
    import shutil
    import sqlite3

    broken = tmp_path / "failed.sqlite"
    shutil.copyfile(demo, broken)
    with sqlite3.connect(broken) as con:
        con.execute("UPDATE quality_checks SET failures=1,status='FAIL' WHERE rowid=1")
    app = boot(broken, monkeypatch)
    assert app.error and not app.radio
    with sqlite3.connect(broken) as con:
        con.execute("UPDATE quality_checks SET failures=0,status='PASS' WHERE rowid=1")
    next(b for b in app.button if b.label == "Recheck source validation").click().run()
    clean(app)
    assert app.radio(key="nav").value == "Home"


def test_empty_signal_home_and_demo_do_not_fabricate_warnings(demo, monkeypatch):
    from app import data
    from pulse.alerts.engine import detect

    monkeypatch.setattr(data, "signals", lambda fingerprint: detect(demo).iloc[:0])
    app = boot(demo, monkeypatch)
    clean(app)
    assert any("No current weekly signals" in m.value for m in app.markdown)
    app.button(key="start_demo").click().run()
    assert app.session_state["demo_step"] is None
    assert app.radio(key="nav").value == "Investigate"
    clean(app)
