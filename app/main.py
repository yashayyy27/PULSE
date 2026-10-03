"""PULSE product shell. Run: streamlit run app/main.py."""

import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st

from app import advanced, data, views
from app.components import caption, error_state, html, style
from app.demo import render_demo, start_demo
from app.lenses import system
from app.state import PAGES, initialise, reset_context
from pulse.analytics.core import latest_week
from pulse.runtime import database_path, query

st.set_page_config(
    page_title="PULSE | Decision Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)
style()
if not database_path().exists():
    st.title("PULSE")
    error_state(
        "No analytical snapshot is available.",
        "Run python scripts/setup_demo.py from the repository root, then retry. PULSE regenerates its synthetic data; no credentials are needed.",
    )
    st.button("Retry snapshot", on_click=st.rerun)
    st.stop()
try:
    fingerprint = data.snapshot()
    quality = query("SELECT * FROM quality_checks", path=fingerprint[0])
    if quality.failures.sum():
        st.title("PULSE / source validation")
        error_state(
            "Analytics are paused because source validation failed.",
            "Repair the source and rerun the setup script. The app will not display unverified calculations.",
        )
        st.dataframe(quality[quality.failures > 0], hide_index=True)
        st.button("Recheck source validation", on_click=st.rerun)
        st.stop()
    start, end = latest_week(fingerprint[0])
except Exception as error:
    st.title("PULSE / snapshot unavailable")
    error_state(
        "PULSE could not open the analytical snapshot.",
        "Check the configured database path or rebuild the synthetic demo, then retry.",
    )
    with st.expander("Technical details"):
        st.text(str(error))
    st.button("Retry snapshot", on_click=st.rerun)
    st.stop()
initialise(st.session_state, start, end)
ctx = st.session_state.context
with st.container(key="product_header"):
    brand, nav, trust = st.columns([1.15, 5.4, 1.8], gap="small")
    with brand:
        html(
            '<div class="brand"><i></i>PULSE</div><div class="brand-sub">DECISION INTELLIGENCE</div>'
        )
    with nav:
        page = st.radio(
            "Product navigation", PAGES, horizontal=True, key="nav", label_visibility="collapsed"
        )
    with trust:
        with st.popover(
            f"✓ {int((quality.status == 'PASS').sum())} source checks", use_container_width=True
        ):
            system(ctx, fingerprint, quality)
with st.container(key="utility_bar"):
    scope, reset, demo = st.columns([4, 1.4, 1.7])
    with scope:
        html(
            f'<div class="context-strip"><strong>WATTLE & RYE</strong> / SYNTHETIC · <strong>{escape(ctx["entity"].upper())}</strong> · {escape(ctx["start"])} → {escape(ctx["end"])}<br>AUD EXCL. GST · LOCAL SNAPSHOT · SESSION WORKSPACE</div>'
        )
    reset.button(
        "Reset context",
        key="reset_context",
        on_click=reset_context,
        args=(st.session_state, start, end),
    )
    demo.button(
        "90-second guided demo",
        key="start_demo",
        on_click=start_demo,
        disabled=st.session_state.demo_step is not None,
    )
if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))
render_demo()
handlers = {
    "Home": views.home,
    "Signals": views.signals,
    "Investigate": views.investigation,
    "Scenario Lab": advanced.scenarios,
    "Ask PULSE": advanced.ask,
    "Briefs": advanced.brief,
}
try:
    handlers[page](ctx, fingerprint)
except Exception as error:
    error_state(
        "PULSE could not complete this analysis.",
        "The selected context is retained. Reset context or retry the view to recover safely.",
    )
    with st.expander("Technical details"):
        st.text(str(error))
    st.button("Retry analysis", on_click=st.rerun)
caption(
    "PULSE · Entirely synthetic · Observed ≠ estimated ≠ forecast ≠ scenario · No real approvals or achieved benefits. AI-assisted portfolio prototype."
)
