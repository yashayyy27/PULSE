import pytest
from streamlit.testing.v1 import AppTest
from app.components import PAGES
from pulse.runtime import ROOT


@pytest.mark.parametrize("page", PAGES)
def test_every_page(demo, monkeypatch, page):
    monkeypatch.setenv("PULSE_DB", str(demo))
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=45)
    app.session_state["nav"] = page
    app.run()
    assert not app.exception, [error.message for error in app.exception]
    assert len(app.title) > 0
    assert app.radio[0].value == page


def test_navigation_and_decision(demo, monkeypatch):
    monkeypatch.setenv("PULSE_DB", str(demo))
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=45).run()
    app.button(key="overview_investigate").click().run()
    assert not app.exception and app.radio[0].value == "Investigate"
    next(b for b in app.button if b.label == "Record proposal").click().run()
    assert app.session_state["decisions"][0]["status"] == "Proposed; unapproved"
    assert not app.exception


def test_scenario_compare_and_ask(demo, monkeypatch):
    monkeypatch.setenv("PULSE_DB", str(demo))
    app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=45)
    app.session_state["nav"] = "Scenario Lab"
    app.run()
    app.slider[3].set_value(-10).run()
    app.button[0].click().run()
    assert app.session_state["scenarios"][0]["assumptions"]["hours_change"] == -0.1
    app.radio[0].set_value("Ask PULSE").run()
    app.button[1].click().run()
    assert app.session_state["ask_result"]["supported"]
    assert not app.exception
