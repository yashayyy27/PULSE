"""Weekly management brief generated from measured outputs, not seed labels."""

import html
import json
from pathlib import Path

import pandas as pd

from pulse.alerts.engine import detect, exposure_summary
from pulse.analytics.core import daily, investigate, latest_week
from pulse.analytics.health import health
from pulse.analytics.impact import stockout_opportunity
from pulse.forecasting.engine import forecast
from pulse.runtime import ROOT


def make_brief(path=None):
    start, end = latest_week(path)
    inv = investigate(start, end, path=path)
    metrics = inv["after"]
    alerts = detect(path)
    issues = []
    for row in alerts.drop_duplicates("location_id").head(3).itertuples():
        details = investigate(start, end, row.location_id, path)
        associated = details["bridge"].sort_values("impact").head(2)
        issues.append(
            {
                "entity": row.entity,
                "issue": row.kpi,
                "actual": row.actual,
                "baseline": row.baseline,
                "estimated_profit_exposure": row.estimated_profit_exposure,
                "evidence": associated.to_dict("records"),
                "investigation": "Reconcile roster, discount and channel records with store manager before changing hours or offers.",
                "risk": "Demand and service trade-offs; period comparison does not establish causality.",
                "success_measure": "Review next 4 complete weeks of margin, satisfaction and warning recurrence; no achieved benefit claimed.",
            }
        )
    outlook = forecast(daily(path))
    future = outlook["future"].query("metric=='revenue'")
    opportunity_start = (pd.Timestamp(end) - pd.Timedelta(days=55)).strftime("%Y-%m-%d")
    opportunities = stockout_opportunity(opportunity_start, end, path=path)
    opportunity = (
        opportunities.sort_values("estimated_gross_profit_opportunity", ascending=False)
        .head(1)
        .to_dict("records")
    )
    return {
        "title": "PULSE — MONDAY MORNING BRIEF",
        "synthetic": True,
        "week_ending": end,
        "business_health": {
            k: metrics[k]
            for k in ["revenue", "operating_profit", "operating_margin", "transactions"]
        },
        "health_index": health(metrics),
        "top_issues": issues,
        "warning_count": len(alerts),
        "estimated_weekly_profit_exposure": exposure_summary(alerts),
        "exposure_method": "Operating-profit warnings only, once per location; median-baseline gaps. No overlapping KPI sums.",
        "top_opportunity": opportunity,
        "opportunity_assumptions": "Last 56 days; >=3 available days per store/SKU/weekday; 50% substitution. Estimated gross profit, not recovered sales.",
        "forecast_watch": {
            "next_28_days_revenue": float(future.forecast.sum()),
            "model_metrics": outlook["metrics"].to_dict("records"),
            "limitation": "Future forecast begins after dataset end; report week can precede end by six days. Daily empirical bands are approximate, not an aggregate guarantee.",
        },
        "decisions_required": [
            "Assign owners to top store investigations within two business days.",
            "Approve a bounded availability or labour pilot after service and financial guardrails are agreed.",
        ],
        "limitations": "All synthetic. No real interviews, approvals or achieved benefits. Estimates, forecasts and scenarios require assumptions.",
    }


def brief_html(brief):
    esc = html.escape
    k = brief["business_health"]
    cards = "".join(
        f"<div class='card'><span>{esc(label)}</span><strong>{value}</strong></div>"
        for label, value in [
            ("Observed revenue", f"A${k['revenue']:,.0f}"),
            ("Observed profit", f"A${k['operating_profit']:,.0f}"),
            ("Operating margin", f"{k['operating_margin']:.1%}"),
            ("Transactions", f"{k['transactions']:,.0f}"),
        ]
    )
    issues = "".join(
        f"<section><h3>{esc(i['entity'])} · {esc(i['issue'])}</h3><p>Actual {i['actual']:,.2f}; reference {i['baseline']:,.2f}. Estimated weekly profit exposure A${i['estimated_profit_exposure']:,.0f}.</p><p>Associated contributors: {esc(str(i['evidence']))}</p><p>{esc(i['investigation'])}</p><p>Risk: {esc(i['risk'])}</p><p>Measure: {esc(i['success_measure'])}</p></section>"
        for i in brief["top_issues"]
    )
    decisions = "".join(f"<li>{esc(item)}</li>" for item in brief["decisions_required"])
    return f"""<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>PULSE executive brief</title><style>body{{font:16px system-ui;background:#f3f5f7;color:#142434;margin:48px auto;max-width:1000px;padding:24px}}h1{{font-size:34px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.card,section{{background:white;border:1px solid #dce3ea;padding:20px;margin:16px 0;border-radius:12px}}span{{display:block;color:#42596c}}strong{{display:block;font-size:26px}}p{{line-height:1.6}}@media(max-width:650px){{.grid{{grid-template-columns:1fr 1fr}}}}@media print{{body{{margin:0;background:white}}}}</style>
    <p>SYNTHETIC DECISION INTELLIGENCE · WATTLE &amp; RYE</p><h1>{esc(brief["title"])}</h1>
    <p>Week ending {esc(brief["week_ending"])} · Health index {brief["health_index"]["overall"]:.0f}/100</p>
    <div class='grid'>{cards}</div><h2>Top issues</h2>{issues or "<p>No warning meets configured thresholds.</p>"}
    <p>Estimated weekly operating-profit exposure A${brief["estimated_weekly_profit_exposure"]:,.0f}. {esc(brief["exposure_method"])}</p>
    <h2>Top opportunity</h2><p>{esc(str(brief["top_opportunity"]))}</p><p>{esc(brief["opportunity_assumptions"])}</p>
    <h2>Forecast watch</h2><p>Next 28 days revenue: A${brief["forecast_watch"]["next_28_days_revenue"]:,.0f} (forecast).</p>
    <p>{esc(brief["forecast_watch"]["limitation"])}</p><h2>Decisions required</h2><ul>{decisions}</ul><p>{esc(brief["limitations"])}</p></html>"""


def export_reports(path=None, target=None):
    target = Path(target or ROOT / "reports")
    target.mkdir(parents=True, exist_ok=True)
    brief = make_brief(path)
    (target / "monday_brief.json").write_text(json.dumps(brief, indent=2, allow_nan=False))
    (target / "monday_brief.html").write_text(brief_html(brief))
    detect(path).to_csv(target / "alerts.csv", index=False)
    for name, frame in forecast(daily(path)).items():
        frame.to_csv(target / f"forecast_{name}.csv", index=False)
    start, end = latest_week(path)
    investigate(start, end, path=path)["bridge"].to_csv(target / "profit_bridge.csv", index=False)
    return brief
