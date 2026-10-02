"""Generate dictionaries, traceability, evidence-backed recommendations and UAT results."""

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pulse.runtime import ROOT, query
from pulse.metrics.registry import REGISTRY
from scripts.build_docs import INTRO

BA = ROOT / "docs/business-analysis"
GRAINS = {
    "dim_date": "one calendar day",
    "dim_location": "one fictional store",
    "dim_product": "one SKU",
    "dim_customer": "one anonymous synthetic customer; 0 means guest",
    "dim_channel": "one channel",
    "dim_promotion": "one offer; 0 means none",
    "dim_employee": "one fictional employee",
    "fact_sales": "one order with one featured SKU and 1–3 units",
    "fact_labour": "one paid employee/day",
    "fact_inventory": "one store/SKU/day snapshot",
    "fact_operating_costs": "one store/day overhead",
    "fact_promotions": "one store/day campaign assignment/spend, including none",
    "fact_feedback": "one voluntary order response; at most one per order",
}
DEFS = {
    "date_id": "ISO business date; FK to calendar in dated facts",
    "month": "YYYY-MM reporting period",
    "weekday": "Monday 0 through Sunday 6",
    "week_start": "ISO Monday of week",
    "name": "fictional entity display name",
    "state": "NSW, VIC, QLD, WA, SA or ACT",
    "region": "fictional state district",
    "category": "Kitchen, Drinks or Pantry",
    "list_price": "AUD unit price excluding GST",
    "unit_cost": "AUD reference unit product cost",
    "segment": "Regular, Convenience, Occasional or Guest",
    "fee_rate": "channel fee fraction of net sales",
    "discount_rate": "offer fraction of list sales",
    "role": "fictional employee role",
    "daypart": "Morning, Lunch or Evening",
    "quantity": "units in the single-SKU order",
    "list_sales": "AUD gross list amount",
    "discount": "AUD discount amount",
    "refund": "AUD revenue reversed; does not reverse COGS",
    "cogs": "AUD sale-captured product cost",
    "channel_fee": "AUD fee on net revenue",
    "hours": "loaded paid hours per employee/day",
    "labour_cost": "AUD loaded payroll",
    "available": "daily SKU check: 0 unavailable, 1 available",
    "closing_units": "synthetic units remaining",
    "overhead": "AUD store/day fixed operating overhead",
    "campaign_spend": "AUD store/day campaign spend",
    "rating": "voluntary satisfaction response from 1 to 5",
}
TRACE = [
    (
        "BR-001",
        "FR-001",
        "US-001",
        "Executive Overview",
        "test_every_page[Executive Overview]",
        "Present headline performance",
        "Review priorities",
    ),
    (
        "BR-002",
        "FR-002",
        "US-002",
        "KPI ledger",
        "test_governed_ledger",
        "Known values produce profit 290",
        "Shared financial truth",
    ),
    (
        "BR-003",
        "FR-003",
        "US-003",
        "Alerts",
        "test_anomaly_edges",
        "Adverse 70 versus 100 warns",
        "Earlier issue review",
    ),
    (
        "BR-004",
        "FR-004",
        "US-004",
        "Investigate",
        "test_bridge_and_dimensions",
        "Profit and ten dimensional movements reconcile",
        "Defensible investigation",
    ),
    (
        "BR-006",
        "FR-005",
        "US-005",
        "Stockout estimates",
        "test_health_and_opportunity",
        "100% substitution gives zero estimated lost sales",
        "Bounded availability pilot",
    ),
    (
        "BR-009",
        "FR-006",
        "US-006",
        "Forecast",
        "test_forecast_chronology",
        "Holdout changes cannot alter selection/calibration",
        "Honest planning uncertainty",
    ),
    (
        "BR-005",
        "FR-007",
        "US-007",
        "Scenario Lab",
        "test_scenarios_identity_and_sensitivity",
        "Zero changes reproduce ledger",
        "Compare conditional decisions",
    ),
    (
        "BR-010",
        "FR-008",
        "US-008",
        "Ask PULSE",
        "test_unknown_and_sql_injection",
        "Unsupported/SQL input rejected",
        "Evidence access",
    ),
    (
        "BR-006",
        "FR-009",
        "US-009",
        "Customers and campaigns",
        "test_cohorts_retention_and_promotions",
        "Latest retention is censored; campaign economics executes",
        "Avoid inference mistakes",
    ),
    (
        "BR-007",
        "FR-010",
        "US-010",
        "Executive Brief",
        "test_brief_reconciles",
        "Brief values reconcile with period ledger",
        "Consistent communication",
    ),
    (
        "BR-008",
        "FR-011",
        "US-002",
        "Validation/publish",
        "test_failed_publish_retains_database",
        "Invalid source cannot replace prior DB",
        "Reliable reporting",
    ),
    (
        "BR-007",
        "FR-012",
        "US-011",
        "Decision proposal",
        "test_navigation_and_decision",
        "Proposal remains unapproved",
        "Accountable next step",
    ),
    (
        "BR-001",
        "FR-013",
        "US-001",
        "Health index",
        "test_health_and_opportunity",
        "Valid normalised weights; zero weights rejected",
        "Inspectable priorities",
    ),
    (
        "BR-003",
        "FR-014",
        "US-003",
        "Navigation/scope",
        "test_navigation_and_decision",
        "Overview button opens investigation",
        "Practical workflow",
    ),
]


def main():
    doc = [
        "# Data dictionary and source contracts",
        "",
        INTRO,
        "AUD excluding GST; all keys synthetic. Source PK/FK/check definitions are authoritative in [schema](../../sql/schema.sql). Sale cost is captured at transaction time. No genuine PII.",
        "",
    ]
    for name, grain in GRAINS.items():
        columns = query(f"PRAGMA table_info({name})")
        doc += [
            f"## {name}",
            f"Grain: **{grain}**.",
            "",
            "| Column | SQLite type | Key / required | Business meaning |",
            "|---|---|---|---|",
        ]
        for row in columns.itertuples():
            meaning = DEFS.get(
                row.name,
                "Synthetic " + row.name.replace("_id", "").replace("_", " ") + " identifier",
            )
            doc.append(
                f"| {row.name} | {row.type} | {'PK' if row.pk else 'required' if row.notnull else 'see DDL'} | {meaning} |"
            )
        doc.append("")
    doc += [
        "`mart_daily`: store/day additive ledger; source facts aggregate independently. `mart_monthly`: store/month plus LAG, ranking and trailing three-month average (first months have shorter windows). `mart_customer_month`: identified customer/month activity. `mart_retention`: company monthly transition; final month NULL. `mart_cohorts`: first-observed cohort/month activity.",
        "",
        "[Lineage](15-data-flow.md) · [ERD and architecture](../ARCHITECTURE.md) · [KPI definitions](12-kpi-dictionary.md)",
    ]
    (BA / "13-data-dictionary.md").write_text("\n".join(doc))
    trace = [
        "# Requirements traceability matrix",
        "",
        INTRO,
        "Problem: late detection, inconsistent metrics and weak decision follow-through. Every major feature below supports a proposed outcome, not an achieved benefit.",
        "",
        "| Problem / need | BR | FR | Story | Feature | Automated test | UAT | Proposed outcome |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, (br, fr, us, feature, test, expected, outcome) in enumerate(TRACE, 1):
        trace.append(
            f"| {expected} | {br} | {fr} | {us} | {feature} | `{test}` | UAT-{i:03} | {outcome} |"
        )
    trace += [
        "",
        "Tests: [engines](../../tests/test_engines.py) and [interface](../../tests/test_app.py). [Criteria](11-acceptance-criteria.md) define numerical acceptance; [actual results](20-uat-results.md) are generated from JUnit. Stakeholder acceptance remains Not Run.",
        "",
        "Example discovery chain: CFO statement → BR-002 (one financial truth) → FR-002/FR-011 → US-002 → AC-001/AC-002/AC-010 → ledger and publication gate → executable fixture/reconciliation/failure tests → proposed consistency benefit.",
    ]
    (BA / "16-traceability-matrix.md").write_text("\n".join(trace))
    root = ET.parse(ROOT / "reports/test-results.xml").getroot()
    cases = root.findall(".//testcase")
    result = [
        "# Simulated UAT results",
        "",
        INTRO,
        "These are executed developer tests, not stakeholder sign-off. Generated from the final local JUnit result file; no manual Pass overrides.",
        "",
        "| UAT | Requirement | Scenario / expected result | Actual result | Status |",
        "|---|---|---|---|---|",
    ]
    for i, (_, fr, _, feature, test, expected, _) in enumerate(TRACE, 1):
        matching = [c for c in cases if c.attrib["name"] == test]
        if not matching:
            status = "NOT RUN"
            actual = "No matching executed test"
        elif any(c.find("failure") is not None or c.find("error") is not None for c in matching):
            status = "FAIL"
            actual = "Failure in executed JUnit result"
        elif any(c.find("skipped") is not None for c in matching):
            status = "SKIPPED"
            actual = "Not executed"
        else:
            status = "PASS (developer)"
            actual = f"{len(matching)} executed check; assertions passed"
        result.append(f"| UAT-{i:03} | {fr} | {feature}: {expected} | {actual} | {status} |")
    result += [
        "",
        f"Final JUnit file contains {len(cases)} test cases. Page parametrisation covers all eleven views. Additional source, identity, scope, corruption and financial checks are included in the suite.",
        "",
        "| Real stakeholder acceptance | Status | Reason |",
        "|---|---|---|",
        "| CFO metric approval | NOT RUN | No real organisation/approver |",
        "| Store-manager task usability | NOT RUN | Developer review only |",
        "| COO rollout sign-off | NOT RUN | Portfolio prototype, not production release |",
        "| Production accessibility/security UAT | NOT RUN | Requires real deployment and users |",
    ]
    (BA / "20-uat-results.md").write_text("\n".join(result))
    brief = json.loads((ROOT / "reports/monday_brief.json").read_text())
    recommendation = [
        "# Executive recommendations — generated evidence",
        "",
        INTRO,
        f"Observed week ending **{brief['week_ending']}**. All financial gaps below are reference estimates. No achieved benefit or causal attribution is claimed.",
        "",
    ]
    lookup = {
        "Labour cost": "Reconcile paid hours, loaded wages and roster requirements; check service before a staffing pilot.",
        "Order volume": "Review demand, availability and channel context with the store manager; compare local events and promotions.",
        "Basket / price / product mix": "Inspect quantity, category/product and channel mix before changing prices or offers.",
        "Refunds": "Reconcile refund reasons and returned-product treatment; audit policy before alleging misconduct.",
        "Discounting": "Inspect offer uptake and contribution economics; a control group is needed for incremental-value claims.",
    }
    for issue in brief["top_issues"]:
        k = REGISTRY[issue["issue"]]

        def fmt(value):
            return (
                f"A${value:,.2f}"
                if k.unit == "AUD"
                else f"{value:.2%}"
                if k.unit == "ratio"
                else f"{value:,.2f}"
            )

        action = (
            lookup.get(issue["evidence"][0]["contributor"], issue["investigation"])
            if issue["evidence"]
            else issue["investigation"]
        )
        recommendation += [
            f"## {issue['entity']}",
            f"**Observation:** {k.name} {fmt(issue['actual'])}, versus eight-week reference {fmt(issue['baseline'])}.",
            f"**Evidence:** equal-length previous-week associated ledger contributors: {issue['evidence']}. The ledger comparison and warning baseline differ.",
            f"**Business impact:** estimated weekly profit reference gap A${issue['estimated_profit_exposure']:,.2f}; ratio-only alerts may carry zero monetary estimate.",
            f"**Recommended investigation:** {action}",
            "**Expected benefit:** better-informed pilot scope; any financial recovery is conditional and unmeasured.",
            f"**Risk:** {issue['risk']}",
            f"**Measure success:** {issue['success_measure']}",
            "",
        ]
    recommendation += [
        "## Availability opportunity",
        "**Observation/evidence:** " + str(brief["top_opportunity"]),
        "**Estimated impact and assumptions:** " + brief["opportunity_assumptions"],
        "**Proposed action:** validate stock counts, replenishment and substitution with Supply chain; pilot high-margin availability at selected stores.",
        "**Expected benefit:** possible gross-profit opportunity conditional on recoverable demand; not an achieved saving.",
        "**Risk / measure:** waste and substitution could offset value. Track available SKU checks, category contribution and waste/service in a comparable pilot. Do not add this estimate to warning exposure.",
        "",
        "[Generated brief](../../reports/monday_brief.json) · [Impact methodology](../ARCHITECTURE.md) · [Benefits plan](25-benefits-realisation.md)",
    ]
    (BA / "21-executive-recommendations.md").write_text("\n\n".join(recommendation))
    print(
        f"Generated dictionary, {len(TRACE)} traceability/UAT scenarios and measured recommendations"
    )


if __name__ == "__main__":
    main()
