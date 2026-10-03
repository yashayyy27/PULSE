"""Curated presentation over the existing calculated executive reporting engine."""

from copy import deepcopy
from html import escape
import json

from app import data
from app.components import display, money
from pulse.alerts.engine import exposure_summary
from pulse.metrics.registry import REGISTRY
from pulse.reports.brief import brief_html
import pandas as pd


def build_brief(fingerprint, items, scenarios, decisions):
    output = deepcopy(data.company_brief(fingerprint))
    selected = []
    for item in items:
        row = item["signal"]
        inv = data.investigation(
            row["period_start"], row["timestamp"], int(row["location_id"]), fingerprint
        )
        selected.append(
            {
                "entity": row["entity"],
                "issue": row["kpi"],
                "actual": row["actual"],
                "baseline": row["baseline"],
                "estimated_profit_exposure": row["estimated_profit_exposure"],
                "evidence": inv["bridge"].sort_values("impact").head(3).to_dict("records"),
                "investigation": row["investigation"],
                "risk": "Accounting association, not causality. Service/demand responses require validation.",
                "success_measure": "Review margin, satisfaction and signal recurrence over four complete weeks.",
                "period_start": row["period_start"],
                "period_end": row["timestamp"],
                "severity": row["severity"],
            }
        )
    output["top_issues"] = selected
    output["selected_signals"] = [item["signal"] for item in items]
    output["scenarios_considered"] = deepcopy(scenarios)
    output["session_proposals"] = deepcopy(decisions)
    output["selected_profit_exposure"] = (
        exposure_summary(pd.DataFrame(output["selected_signals"])) if items else 0
    )
    output["decisions_required"] = [item["action"] for item in decisions] or [
        "Assign a fictional investigation owner and agree service/demand guardrails before a bounded pilot."
    ]
    return output


def export_html(output):
    company = deepcopy(output)
    company["top_issues"] = []
    document = brief_html(company)
    esc = escape
    priority = "".join(
        f"<section><h3>{esc(item['entity'])} · {esc(REGISTRY[item['issue']].name)}</h3><p>{esc(item['period_start'])} to {esc(item['period_end'])} · {esc(item['severity'])}. Actual {esc(display(item['issue'], item['actual']))}; 8-week median {esc(display(item['issue'], item['baseline']))}.</p></section>"
        for item in output["top_issues"]
    )
    evidence = "".join(
        f"<section><h3>{esc(item['entity'])} · associated ledger evidence</h3><p>{esc(item['period_start'])} to {esc(item['period_end'])}, compared with the previous equal-length period. Contributors: {esc('; '.join(r['contributor'] + ' ' + money(r['impact']) for r in item['evidence']))}</p><p>Next investigation: {esc(item['investigation'])}</p></section>"
        for item in output["top_issues"]
    )
    scenarios = "".join(
        f"<section><h3>{esc(s['name'])} · {esc(s['context']['entity'])}</h3><p>{esc(s['context']['start'])} to {esc(s['context']['end'])} · CONDITIONAL SCENARIO</p><p>Base profit {esc(money(s['base']['operating_profit']))}; modelled {esc(money(s['result']['operating_profit']))}; change {esc(money(s['result']['operating_profit'] - s['base']['operating_profit']))}.</p><p>Assumptions: {esc(json.dumps(s['assumptions']))}</p><p>Demand, feasibility and service response are untested. Not a forecast or achieved saving.</p></section>"
        for s in output["scenarios_considered"]
    )
    proposals = "".join(
        f"<section><h3>{esc(d['owner'])} · {esc(d['status'])}</h3><p>{esc(d['context']['entity'])}, {esc(d['context']['start'])} to {esc(d['context']['end'])}</p><p>{esc(d['action'])}</p><p>Guardrails: {esc(d['guardrails'])}</p></section>"
        for d in output["session_proposals"]
    )
    additional = f"<h2>Selected evidence</h2>{evidence or '<p>No findings selected. Company health remains the reporting baseline.</p>'}<h2>Selected estimated exposure</h2><p>{esc(money(output['selected_profit_exposure']))} from selected operating-profit signals only, once per location. Company exposure above includes all current operating-profit warnings. Neither is achieved savings.</p><h2>Scenario considered</h2>{scenarios or '<p>No scenario saved for consideration.</p>'}<h2>Decision required / proposed record</h2>{proposals or '<p>No approved decision. Assign an owner and define guardrails.</p>'}<h2>Next investigation</h2><p>Validate payroll, product/channel mix and availability with the location manager; evaluate demand and service sensitivities before a bounded intervention.</p><h2>Risks / limitations</h2><p>{esc(output['limitations'])} Warnings use heuristic references; accounting contributions do not establish causes. Session selections are retained only through export.</p>"
    theme = "<style>body{background:#090A0B;color:#F4F7F8;font:16px system-ui;max-width:1050px}h1{font-size:32px;letter-spacing:-1px}h2{font-size:22px;border-top:1px solid #343B40;padding-top:24px}h3{font-size:18px}.card,section{background:#111315;border:1px solid #343B40;border-radius:5px}span{color:#C7CDD1}strong{font-variant-numeric:tabular-nums;color:#00D2BE}p{line-height:1.65}@media print{body{background:white;color:#111315}.card,section{background:white;color:#111315}strong,span{color:#111315}}</style>"
    return (
        document.replace("</html>", theme + additional + "</html>")
        .replace(
            "<h2>Top issues</h2><p>No warning meets configured thresholds.</p>",
            "<h2>Priority signals</h2>"
            + (
                priority
                or "<p>No findings selected; this does not imply there are no company warnings.</p>"
            ),
        )
        .replace("<div class='grid'>", "<h2>Business health</h2><div class='grid'>")
    )
