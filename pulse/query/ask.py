"""Deterministic intent routing; no generated SQL, credentials or LLM dependency."""

import re

import pandas as pd

from pulse.alerts.engine import detect
from pulse.analytics.core import contributions, investigate, latest_week, previous_period
from pulse.runtime import query, read_sql

EXAMPLES = [
    "Why did profit decline last month?",
    "Which locations need attention?",
    "What contributed to margin deterioration?",
    "Which promotion performed poorly?",
    "Where is labour percentage increasing?",
    "Which customer segment is declining?",
]


def month_window(path=None):
    end = pd.Timestamp(query("SELECT MAX(date_id) d FROM dim_date", path=path).iloc[0, 0])
    if end.day != end.days_in_month:
        end = end.replace(day=1) - pd.Timedelta(days=1)
    return str(end.replace(day=1).date()), str(end.date())


def answer(question, path=None):
    text = question.lower().strip()
    if (
        not text
        or len(text) > 500
        or re.search(r"\b(drop|delete|insert|update|select|pragma)\b", text)
    ):
        return {
            "supported": False,
            "answer": "Use a supported business question. Ask PULSE never accepts SQL.",
            "evidence": None,
        }
    start, end = month_window(path) if "month" in text else latest_week(path)
    scope = None
    for row in query("SELECT location_id,name FROM dim_location", path=path).itertuples():
        if row.name.lower() in text:
            scope = row.location_id
            break
    dimension = next(
        (
            name
            for token, name in [
                ("channel", "Channel"),
                ("product", "Product"),
                ("category", "Category"),
                ("segment", "Customer segment"),
                ("state", "State"),
                ("region", "Region"),
            ]
            if token in text
        ),
        "Location",
    )
    caveat = "Synthetic observations; contributors are associations, not proven causes. Comparisons may reflect seasonality."
    if "promotion" in text:
        scope = None  # Campaign economics have explicitly company-wide scope.
        frame = query(
            read_sql("promotion_analysis.sql"), {"start": start, "end": end}, path
        ).sort_values("promotion_roi")
        narrative = "Campaigns ranked by estimated observational ROI against prior 56-day same-store/weekdays (>=3 reference days); compare economics before proposing a controlled pilot."
        intent = "promotion_economics"
    elif "labour" in text or "labor" in text:
        inv = investigate(start, end, scope, path)
        a, b = inv["after"], inv["before"]
        narrative = f"Labour share changed by {(a['labour_pct'] - b['labour_pct']) * 100:+.2f} percentage points to {a['labour_pct'] * 100:.2f}%. Lower revenue can increase this ratio."
        prior_start, prior_end = previous_period(start, end)
        frame = query(
            """WITH windows AS (
            SELECT name,location_id,
            SUM(CASE WHEN date_id BETWEEN :start AND :end THEN labour_cost ELSE 0 END) current_labour,
            SUM(CASE WHEN date_id BETWEEN :start AND :end THEN revenue ELSE 0 END) current_revenue,
            SUM(CASE WHEN date_id BETWEEN :prior_start AND :prior_end THEN labour_cost ELSE 0 END) prior_labour,
            SUM(CASE WHEN date_id BETWEEN :prior_start AND :prior_end THEN revenue ELSE 0 END) prior_revenue
            FROM mart_daily WHERE date_id BETWEEN :prior_start AND :end
            AND (:location IS NULL OR location_id=:location) GROUP BY location_id,name
        ) SELECT *,current_labour/NULLIF(current_revenue,0) current_share,
            prior_labour/NULLIF(prior_revenue,0) prior_share,
            100*(current_labour/NULLIF(current_revenue,0)-prior_labour/NULLIF(prior_revenue,0)) change_pp
            FROM windows ORDER BY change_pp DESC""",
            {
                "start": start,
                "end": end,
                "prior_start": prior_start,
                "prior_end": prior_end,
                "location": scope,
            },
            path,
        )
        intent = "labour_pressure"
    elif "attention" in text or "alert" in text:
        frame = detect(path)
        if scope is not None:
            frame = frame[frame.location_id == scope]
        narrative = f"{len(frame)} current weekly warnings. Prioritise operating-profit exposure and inspect the supporting ledger."
        start, end = latest_week(path)
        intent = "attention"
    elif any(
        word in text for word in ["segment", "channel", "product", "category", "state", "region"]
    ):
        frame = contributions(start, end, dimension, scope, path)
        narrative = (
            f"Revenue movement ranked by {dimension.lower()}; rows reconcile to net sales movement."
        )
        intent = "dimensional_movement"
    elif "profit" in text or "margin" in text:
        inv = investigate(start, end, scope, path)
        a, b = inv["after"], inv["before"]
        narrative = (
            f"Observed operating profit changed by A${a['operating_profit'] - b['operating_profit']:+,.0f} "
            f"to A${a['operating_profit']:,.0f}. Operating margin moved from {b['operating_margin']:.1%} to {a['operating_margin']:.1%}."
        )
        frame = inv["bridge"].sort_values("impact")
        intent = "profit_bridge"
    else:
        return {
            "supported": False,
            "answer": "Outside supported intents. Try profit/margin, attention, promotions, labour or dimension/segment movement.",
            "evidence": None,
        }
    return {
        "supported": True,
        "intent": intent,
        "answer": narrative,
        "evidence": frame,
        "period": f"{start} to {end}",
        "scope": "Company" if scope is None else str(scope),
        "method": "Governed ledger + equal-length previous period; SQL contribution/weekday reference or weekly median/MAD warnings.",
        "limitations": caveat,
    }
