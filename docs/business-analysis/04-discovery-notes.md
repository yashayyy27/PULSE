> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Simulated discovery notes

| Raw stakeholder statement | BA question | Need uncovered | Derived requirement |
|---|---|---|---|
| COO: “I have five minutes before the weekly meeting.” | Which decision should those minutes produce? | Prioritised investigations, not every KPI | BR-001 / FR-001 |
| CFO: “Finance and Operations must use the same profit.” | Which costs and tax treatment belong in it? | AUD excl. GST; payroll, fees, overhead and campaigns once | BR-002 / FR-002 |
| Regional Manager: “Tell me which store to call.” | What evidence makes a warning credible? | Baseline, period, materiality and ledger drivers | BR-003 / FR-003 |
| Finance Analyst: “I need to trace every number.” | What grain and reconciliation do you trust? | Separate fact aggregation and inspectable SQL | BR-002 / FR-004 |
| Marketing: “Discounts grow sales, but is that value?” | Can available data prove incremental demand? | Observational contribution comparison with explicit confounding | BR-006 / FR-009 |
| Store Manager: “A red number without context feels unfair.” | What context and guardrails matter? | Service, payroll and period evidence; propose before approval | BR-007 / FR-012 |
| Technology: “Who owns a changed metric?” | What review and refresh contract is needed? | Registry, validation gate and definition change control | BR-008 / FR-011 |

Assumptions exposed: payroll is loaded hourly cost; the prototype lacks outage duration; guest customers cannot be retained; promotions are not randomised; calendars are synthetic and exclude actual holiday effects. Open questions for a real pilot: treatment of returned inventory, central overhead allocation, minimum response count and store manager alert tolerance.

Conflicts: CFO wants detail, COO wants brevity; resolve with executive summary plus evidence drill-down. Marketing wants causal ROI, Technology cannot supply a control group; deliver labelled observational economics and propose a controlled pilot. Operations wants savings from fewer hours, Store Managers want service protection; scenarios are conditional and decisions are proposals. See [decision log](29-decision-log.md).
