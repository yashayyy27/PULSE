# Two-minute decision walkthrough

All data, stakeholders and decisions are synthetic. Build the full demo for the following case; the six-store CI sample has different findings.

1. Executive Overview: read observed revenue/profit/margin/orders and the complete-week dates. Note the estimated exposure excludes overlapping KPI warnings.
2. Alerts: choose Norwood / operating_profit, inspect actual, median reference, expected range and severity; use “Investigate this store”.
3. Investigate: inspect the reconciled bridge. Switch dimension from State through Location/Category/Product; use state/district and store selectors to inspect regional context. Associated contributions are not causes.
4. Scenario Lab: retain Norwood scope, change labour hours by -5%, leave demand/price fixed. Compare base/scenario/difference. This sensitivity assumes service is unaffected and must not be called a realised saving. Save a second case with -3% transactions to challenge that assumption.
5. Return to Investigate and record an unapproved proposal with a fictional owner, then export the session log. Explain service guardrails and why approval is outside the app.
6. Executive Brief: export company-wide HTML. Forecast covers the 28 days after dataset end; its origin differs from the complete-week report cutoff. Ask PULSE can answer “Why did profit decline last month?” using actual numbers, even when the question's premise is false.

For a longer interview, inspect KPI and data dictionaries, SQL fact aggregation, forecast validation/holdout separation, deliberately corrupted-data tests and requirements traceability. [Case study](PORTFOLIO_CASE_STUDY.md).
