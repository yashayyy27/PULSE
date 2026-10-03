> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Functional requirements

| ID | What PULSE must do | Implemented feature |
|---|---|---|
| FR-001 | Show revenue/profit/margin/orders with equal-length period comparison | Home |
| FR-002 | Calculate governed ratios from additive sums and distinct period customers | KPI registry and ledger |
| FR-003 | Flag adverse complete-week deviations with baseline, severity and exposure | Signals |
| FR-004 | Reconcile profit movement and rank ten dimensions of revenue movement | Investigate |
| FR-005 | Quantify conditional stockout opportunity and prevent overlapping exposure totals | Operations / alert exposure summary |
| FR-006 | Forecast revenue, orders, GP and paid hours with chronological evaluation | Investigate / Forecast lens |
| FR-007 | Preserve base case at zero changes and compare saved conditional scenarios | Scenario Lab |
| FR-008 | Route supported analytical questions to bounded evidence; reject SQL/unknown intent | Ask PULSE |
| FR-009 | Show repeat/retention/cohorts and observational promotion economics | Customers / Operations |
| FR-010 | Export a company-wide brief from computed results | Briefs |
| FR-011 | Validate raw contracts and publish only a reconciled constrained model | Pipeline / Data Quality |
| FR-012 | Record an unapproved proposed investigation and export session evidence | Investigate decision form |
| FR-013 | Explain targets and configure health dimension weights | Methodology |
| FR-014 | Offer store/period scope and working warning-to-store navigation | Shared context / Signals |

Metric semantics and scope exceptions are visible: retention, campaigns and brief are company-wide; forecasts end at the dataset origin; weekly alerts always use the latest complete week. See [acceptance criteria](11-acceptance-criteria.md) for testable outcomes and [dictionary](12-kpi-dictionary.md) for limits.
