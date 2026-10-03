"""Assemble the final audit from executed local verification artifacts."""

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pulse.runtime import ROOT


def main():
    reports = ROOT / "reports"
    full = json.loads((reports / "full_verification.json").read_text())
    pipeline = json.loads((reports / "pipeline.json").read_text())
    reproduction = json.loads((reports / "reproduction.json").read_text())
    diagrams = json.loads((reports / "mermaid.json").read_text())
    tests = ET.parse(reports / "test-results.xml").getroot().findall(".//testcase")
    failed = [
        case for case in tests if case.find("failure") is not None or case.find("error") is not None
    ]
    assert not failed
    timings = "\n".join(
        f"| {row['page']} | {row['status']} | {row['seconds']:.3f} | {row['charts']} | {row['tables']} |"
        for row in full["pages"]
    )
    forecasts = "\n".join(
        f"| {row['metric']} | {row['selected_model']} | {row['MAE']:.2f} | {row['RMSE']:.2f} | {row['MAPE']:.2%} | {row['holdout_coverage']:.1%} |"
        for row in full["forecast_holdout"]
    )
    text = f"""# Final audit — PULSE

Local audit date: **3 October 2026 (Australia/Sydney)**. All business records, stakeholders and proposals are synthetic. Forecast origins are fictional 2025 history; no current real-world business signal is claimed.

## Implemented and verified

The repository implements deterministic generation, constrained SQLite star schema, SQL daily/monthly/customer marts, 19 governed KPIs, source quality reporting, Home, weekly warnings, exact profit investigation, ten-dimensional revenue contribution analysis, explicit financial reference/stockout estimates, four forecasts, nine scenario levers, deterministic Ask PULSE, generated HTML executive brief, configurable health weights and session decision/scenario exports. Six primary destinations are present; no empty feature page or placeholder button is used.

The full run produced **{pipeline["orders"]} orders**, **{pipeline["locations"]} stores** and **{pipeline["start"]} to {pipeline["end"]}** history. Source contracts passed **{pipeline["validation_rules"]} checks** with **{pipeline["validation_failures"]} failures**. All foreign keys and source-to-mart revenue/COGS/payroll/profit reconcile. Full verification covers **{len(full["scopes"])} scopes** (company plus every store), **{full["dimensions"]} dimensions** and all views. Profit bridges and zero-change scenarios reconcile at every scope.

## Architecture

Seeded source → compressed raw and SHA-256 manifest → fail-closed validation → constrained star schema → separate fact aggregation and indexed customer summaries → central KPI registry → explainable engines → modular Streamlit views → HTML/JSON/CSV evidence. Publication atomically replaces the validated DB. SQLite was selected for standard-library availability and constraints. PostgreSQL would require connection/date/DDL/bulk-load adaptation; no drop-in or production-scale claim.

Existing `opspulse` / RESTOPS and parent coursework were preserved. PULSE is its own local Git repository. Core implementation, subsequent performance/integrity fixes and completed evidence are committed locally. This audit records pre-publication local verification; the source is now published at [yashayyy27/PULSE](https://github.com/yashayyy27/PULSE). GitHub Actions provides subsequent remote verification. A hosted application has not been deployed.

## Execution evidence

- Pinned dependencies installed in a clean Python 3.12 virtual environment.
- Full setup executed without credentials; actual build/export time recorded as **{reproduction["setup_seconds"]:.3f} seconds** on this Mac. This is a local measurement, not an SLA.
- Source reproducibility independently checked over all **{reproduction["source_tables"]}** compressed table files: **{reproduction["identical_raw_hashes"]}** for repeated deterministic raw hashes.
- `python -m pytest -q --junitxml=reports/test-results.xml`: **{len(tests)} passed, zero failures** in the final clean environment.
- Ruff check and format check pass. Local Markdown link/fence checks pass; results are saved in `reports/documentation_checks.json`.
- **{diagrams["passed"]}/{diagrams["diagrams"]} Mermaid diagrams** parse with Mermaid 11.12.0, including ERD, processes, pipeline, investigation, alert lifecycle and requirements lifecycle.
- Full verification: **{full["total_seconds"]:.3f} seconds**, database **{full["db_bytes"] / 1024 / 1024:.1f} MiB**; weekly warning engine **{full["alert_seconds"]:.3f} seconds**. Timing excludes browser asset/network loading and varies by host/cache.
- Native local server launched on loopback; actual screenshots of Home, investigation, Scenario Lab, Ask PULSE and Briefs are in `docs/screenshots`. Automated view checks also validate chart construction and navigation/proposal/scenario/question workflows. Developer inspection is not stakeholder UAT or WCAG certification.

| View | Result | AppTest seconds | Charts | Tables |
|---|---|---:|---:|---:|
{timings}

Ask PULSE initially has no table until a question is submitted; supported-intent and interaction tests exercise the returned numerical evidence. Hidden expanders are computed and tested, not empty content. Customer and campaign/brief scopes are explicitly labelled company-wide where applicable.

## Forecast evidence and limitations

Validation chooses between seasonal naive and weekday mean across three prior 28-day origins. The final 28 days are excluded from model selection and band calibration. Daily bands use horizon-specific pre-holdout absolute errors and are approximate.

| KPI | Selected model | MAE | RMSE | MAPE | Actual band coverage |
|---|---|---:|---:|---:|---:|
{forecasts}

Nominal bands are 90%, but observed coverage is materially lower, especially paid hours after staffing changes. The app explicitly warns against treating these as operational safety bounds. No tuning against the holdout was used to conceal this result. A production planner needs more calibration history, structural/event controls and prospective evaluation. Paid hours predict the historic staffing process rather than optimise a roster.

## BA evidence

All 29 requested artefacts exist in `docs/business-analysis`. Discovery identifies seven fictional roles, BA questions, assumptions, conflicts and decisions. Requirements distinguish business purpose, functional behaviour and quality constraints; MoSCoW and value/effort record trade-offs. Fourteen traceability rows connect requirements, stories, features, executed tests, simulated UAT scenarios and proposed outcomes. Process maps, ownership, RACI, metric change control, pilot rollout, training and proposed benefits correspond to the local prototype and potential organisational implementation.

Simulated UAT results are generated from JUnit; real CFO approval, store-manager usability, sponsor sign-off and production accessibility/security acceptance are **Not Run**. No achieved savings, adoption, reporting-time reduction or company impact is claimed. Executive recommendations are generated from measured warning/bridge/opportunity results.

## Five-perspective review and fixes

| Perspective | Weakness identified | Fix made and evidence |
|---|---|---|
| Recruiter | Large feature list could conceal the business decision | README opens with purpose, actual preview and one computed store case; recruiter guide supplies timed paths |
| BA hiring manager | Artefact volume can hide weak feature justification | Requirement/story/criterion/test/UAT/outcome matrix; workshop statement-to-feature chain; actual developer results distinguished from acceptance |
| Data analyst | Grain inflation, identity counting and campaign comparison ambiguity | Independent SQL fact aggregation; period distinct customers; censoring; source ledgers reconciled; campaigns use prior 56-day same-weekday reference with minimum sample |
| Engineer | Customer views repeated million-order scans | Materialised/indexed customer activity, retention and cohorts; contextual lenses compute only when requested; current six-destination timings are recorded above |
| Executive | Overlapping exposure and scenario savings could be read as guaranteed benefit | Profit warnings counted once per store; estimate/forecast/scenario labels; assumptions shown; unapproved proposal status; forecast under-coverage warning |

Additional fixes: realistic staffing/overhead calibration in generator; negative currency placed before the AUD prefix so Streamlit shows adverse profit deltas correctly; Markdown dollar signs escaped to avoid accidental mathematical rendering; navigation test targets actual proposal control after rerun; campaign assignment consistency validated against order discounts.

## Known trade-offs and production readiness

One-SKU orders simplify a POS basket; costs are recorded at sale and refunds do not reverse COGS. Inventory checks do not measure outage duration or lost demand. Stockout opportunity assumes substitution and comparable available days; campaign ROI remains observational and confounded. Feedback is voluntary; synthetic identities use a simplified national pool without geographic home-store anchoring; guest identity is unavailable; cohort acquisition is left-censored. Rolling warnings can absorb gradual drift and do not control for holidays/multiple testing. Health targets/weights are simulated stakeholder choices, not empirical risk probabilities.

The app is a local synthetic prototype: no production authentication, RBAC, live integration, case persistence, approvals or automated email/scheduling. Read-only analytics and bounded query routing are implemented; enterprise permissions, audit logging, secrets, privacy/retention policy, refresh locks and versioned snapshots remain rollout requirements. Session decisions/scenarios need export to persist. HTML works; a PDF-specific export engine is deferred. CI is configured, with no claim of a completed remote run. Main dependencies are pinned; the clean-environment lock also captures transitives for CI.

## Ten questions an interviewer may ask

1. **What business problem did you solve?** Late discovery and inconsistent decision evidence. PULSE prioritises investigations, reconciles contributors and exposes conditional decisions; a real pilot must measure whether it improves response time.
2. **How did discovery affect the design?** Fictional CFO/COO detail-versus-brevity needs led to summary plus evidence. Marketing's causal-lift wish became labelled observational economics because no control group exists. Store service concerns made proposals unapproved and scenarios conditional.
3. **Why SQLite?** It is bundled with Python, supports constraints and analytical windows, and runs without credentials. Indexed marts are adequate for this measured local dataset; PostgreSQL migration needs explicit SQL/load changes.
4. **How do you avoid inflated payroll?** Aggregate sales, payroll, inventory and feedback separately to store/day, then join at that grain. Independent source totals and known-value tests protect the ledger.
5. **Does a contributor prove a cause?** No. The volume/basket/cost bridge is an accounting identity and dimensional revenue changes are associations. Pricing, mix and quantity share a residual; operational context or controlled interventions are needed for causality.
6. **Why this warning method?** Complete weeks reduce weekday imbalance; median/MAD is transparent and robust to isolated extremes. Materiality and a scale floor reduce noise, but drift, holidays and low-rate baselines remain limitations.
7. **What does estimated financial exposure mean?** A gap against a historical reference, not a recoverable or achieved saving. Company totals count operating-profit warnings once per store; stockout/revenue/labour opportunities overlap and are not added.
8. **How did you avoid forecast leakage?** Select the baseline on three validation windows before an untouched final holdout; calibrate bands from pre-holdout errors only. A test changes final actuals and confirms selection and band widths stay fixed. Coverage failures are visible.
9. **What makes a scenario defensible?** Zero changes reproduce the observed ledger. Price, quantity, demand and payroll are separate assumptions; no implicit elasticity. Retention uses a disclosed repeat-share proxy and campaign uptake changes discount share. Feasibility/service are untested.
10. **What would you do before a real rollout?** Conduct actual discovery and metric/source approvals, add authenticated access and durable case management, run role-based UAT and prospective forecast/alert evaluation, then pilot with service guardrails and measured benefit baselines. The prototype does not claim those results.

[UX transformation report](UI_UX_FINAL_REPORT.md) · [Interaction audit](UI_UX_INTERACTION_AUDIT.md) · [Recruiter guide](RECRUITER_GUIDE.md) · [Case study](PORTFOLIO_CASE_STUDY.md) · [Architecture](ARCHITECTURE.md) · [UAT results](business-analysis/20-uat-results.md) · [Raw verification](../reports/full_verification.json)
"""
    (ROOT / "docs/FINAL_AUDIT.md").write_text(text)
    print("Final audit generated from executed local evidence")


if __name__ == "__main__":
    main()
