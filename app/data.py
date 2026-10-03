"""Snapshot-aware cached adapters around PULSE's unchanged analytical engines."""

import pandas as pd
import streamlit as st

from pulse.alerts.engine import detect
from pulse.analytics.core import ADDITIVE, daily, investigate, ledger
from pulse.analytics.health import health
from pulse.forecasting.engine import forecast
from pulse.metrics.registry import calculate
from pulse.reports.brief import make_brief
from pulse.runtime import database_path, query


def snapshot():
    path = database_path().resolve()
    stat = path.stat()
    return str(path), stat.st_mtime_ns, stat.st_size


@st.cache_data(show_spinner=False)
def locations(fingerprint):
    return query("SELECT * FROM dim_location ORDER BY name", path=fingerprint[0])


@st.cache_data(show_spinner=False)
def signals(fingerprint):
    return detect(fingerprint[0])


@st.cache_data(show_spinner=False)
def investigation(start, end, location, fingerprint):
    return investigate(start, end, location, fingerprint[0])


@st.cache_data(show_spinner=False)
def measured(start, end, location, fingerprint):
    return ledger(start, end, location, fingerprint[0])


@st.cache_data(show_spinner=False)
def history(location, fingerprint):
    return daily(fingerprint[0], location)


@st.cache_data(show_spinner=False)
def pulse_timeline(location, end, fingerprint):
    frame = history(location, fingerprint)
    frame = frame[frame.date_id <= end].copy()
    frame["week"] = (
        pd.to_datetime(frame.date_id).dt.to_period("W-SUN").dt.end_time.dt.strftime("%Y-%m-%d")
    )
    rows = []
    for week, group in frame.groupby("week", sort=True):
        if len(group) == 7:
            metrics = calculate(group[ADDITIVE].sum().to_dict())
            rows.append(
                {
                    "week": week,
                    "health": health(metrics)["overall"],
                    "profit": metrics["operating_profit"],
                    "revenue": metrics["revenue"],
                }
            )
    return pd.DataFrame(rows).tail(12)


@st.cache_data(show_spinner=False)
def outlook(location, fingerprint):
    return forecast(history(location, fingerprint))


@st.cache_data(show_spinner=False)
def company_brief(fingerprint):
    return make_brief(fingerprint[0])
