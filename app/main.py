"""PULSE command centre. Run: streamlit run app/main.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st

from app import advanced, views
from app.components import PAGES, style
from pulse.analytics.core import latest_week
from pulse.query.ask import month_window
from pulse.runtime import database_path, query

st.set_page_config(page_title="PULSE | Decision Intelligence", page_icon="◉", layout="wide")
style()
if not database_path().exists():
    st.title("PULSE")
    st.info("Generate the synthetic demo first: python scripts/setup_demo.py")
    st.stop()
quality = query("SELECT SUM(failures) failures FROM quality_checks").iloc[0, 0]
if quality:
    st.error(
        "Source validation failed. Analytics suppressed; rebuild the demo after repairing source data."
    )
    st.stop()
if "ask_question_pending" in st.session_state:
    st.session_state.ask_question = st.session_state.pop("ask_question_pending")
for pending, target in [("nav_pending", "nav"), ("scope_pending", "scope")]:
    if pending in st.session_state:
        st.session_state[target] = st.session_state.pop(pending)
with st.sidebar:
    st.title("◉ PULSE")
    st.caption("BUSINESS EARLY-WARNING")
    page = st.radio("Command centre", PAGES, key="nav")
    st.divider()
    names = query("SELECT location_id,name FROM dim_location ORDER BY name")
    selected = st.selectbox("Scope", ["Company"] + names.name.tolist(), key="scope")
    period = st.selectbox("Reporting period", ["Latest complete week", "Latest full month"])
    st.caption("100% synthetic · AUD excl. GST\n\nLocal portfolio prototype")
location = (
    None if selected == "Company" else int(names.loc[names.name == selected, "location_id"].iloc[0])
)
start, end = latest_week() if period == "Latest complete week" else month_window()
st.caption(f"SCOPE: {selected.upper()}  ·  OBSERVED PERIOD: {start} TO {end}")
handlers = dict(
    zip(
        PAGES,
        [
            views.overview,
            views.investigation,
            views.alerts_page,
            advanced.forecasts,
            advanced.scenarios,
            views.customers,
            views.operations,
            advanced.ask,
            advanced.brief,
            views.quality,
            advanced.methodology,
        ],
    )
)
handlers[page](start, end, location)
