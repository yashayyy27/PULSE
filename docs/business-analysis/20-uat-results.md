# Simulated UAT results

> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.


These are executed developer tests, not stakeholder sign-off. Generated from the final local JUnit result file; no manual Pass overrides.

| UAT | Requirement | Scenario / expected result | Actual result | Status |
|---|---|---|---|---|
| UAT-001 | FR-001 | Home: Present headline performance | 1 executed check; assertions passed | PASS (developer) |
| UAT-002 | FR-002 | KPI ledger: Known values produce profit 290 | 1 executed check; assertions passed | PASS (developer) |
| UAT-003 | FR-003 | Signals: Adverse 70 versus 100 warns | 1 executed check; assertions passed | PASS (developer) |
| UAT-004 | FR-004 | Investigate: Profit and ten dimensional movements reconcile | 1 executed check; assertions passed | PASS (developer) |
| UAT-005 | FR-005 | Stockout estimates: 100% substitution gives zero estimated lost sales | 1 executed check; assertions passed | PASS (developer) |
| UAT-006 | FR-006 | Investigate / Forecast lens: Holdout changes cannot alter selection/calibration | 1 executed check; assertions passed | PASS (developer) |
| UAT-007 | FR-007 | Scenario Lab: Zero changes reproduce ledger | 1 executed check; assertions passed | PASS (developer) |
| UAT-008 | FR-008 | Ask PULSE: Unsupported/SQL input rejected | 1 executed check; assertions passed | PASS (developer) |
| UAT-009 | FR-009 | Customers and campaigns: Latest retention is censored; campaign economics executes | 1 executed check; assertions passed | PASS (developer) |
| UAT-010 | FR-010 | Briefs: Brief values reconcile with period ledger | 1 executed check; assertions passed | PASS (developer) |
| UAT-011 | FR-011 | Validation/publish: Invalid source cannot replace prior DB | 1 executed check; assertions passed | PASS (developer) |
| UAT-012 | FR-012 | Decision proposal: Proposal remains unapproved | 1 executed check; assertions passed | PASS (developer) |
| UAT-013 | FR-013 | Health index: Valid normalised weights; zero weights rejected | 1 executed check; assertions passed | PASS (developer) |
| UAT-014 | FR-014 | Navigation/scope: Home signal opens investigation | 1 executed check; assertions passed | PASS (developer) |

Final JUnit file contains 74 test cases. Page parametrisation covers the six primary destinations and contextual evidence lenses. Additional source, identity, scope, corruption and financial checks are included in the suite.

| Real stakeholder acceptance | Status | Reason |
|---|---|---|
| CFO metric approval | NOT RUN | No real organisation/approver |
| Store-manager task usability | NOT RUN | Developer review only |
| COO rollout sign-off | NOT RUN | Portfolio prototype, not production release |
| Production accessibility/security UAT | NOT RUN | Requires real deployment and users |