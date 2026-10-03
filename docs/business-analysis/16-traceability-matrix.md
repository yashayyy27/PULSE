# Requirements traceability matrix

> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.


Problem: late detection, inconsistent metrics and weak decision follow-through. Every major feature below supports a proposed outcome, not an achieved benefit.

| Problem / need | BR | FR | Story | Feature | Automated test | UAT | Proposed outcome |
|---|---|---|---|---|---|---|---|
| Present headline performance | BR-001 | FR-001 | US-001 | Home | `test_every_page[Home]` | UAT-001 | Review priorities |
| Known values produce profit 290 | BR-002 | FR-002 | US-002 | KPI ledger | `test_governed_ledger` | UAT-002 | Shared financial truth |
| Adverse 70 versus 100 warns | BR-003 | FR-003 | US-003 | Signals | `test_anomaly_edges` | UAT-003 | Earlier issue review |
| Profit and ten dimensional movements reconcile | BR-004 | FR-004 | US-004 | Investigate | `test_bridge_and_dimensions` | UAT-004 | Defensible investigation |
| 100% substitution gives zero estimated lost sales | BR-006 | FR-005 | US-005 | Stockout estimates | `test_health_and_opportunity` | UAT-005 | Bounded availability pilot |
| Holdout changes cannot alter selection/calibration | BR-009 | FR-006 | US-006 | Investigate / Forecast lens | `test_forecast_chronology` | UAT-006 | Honest planning uncertainty |
| Zero changes reproduce ledger | BR-005 | FR-007 | US-007 | Scenario Lab | `test_scenarios_identity_and_sensitivity` | UAT-007 | Compare conditional decisions |
| Unsupported/SQL input rejected | BR-010 | FR-008 | US-008 | Ask PULSE | `test_unknown_and_sql_injection` | UAT-008 | Evidence access |
| Latest retention is censored; campaign economics executes | BR-006 | FR-009 | US-009 | Customers and campaigns | `test_cohorts_retention_and_promotions` | UAT-009 | Avoid inference mistakes |
| Brief values reconcile with period ledger | BR-007 | FR-010 | US-010 | Briefs | `test_brief_reconciles` | UAT-010 | Consistent communication |
| Invalid source cannot replace prior DB | BR-008 | FR-011 | US-002 | Validation/publish | `test_failed_publish_retains_database` | UAT-011 | Reliable reporting |
| Proposal remains unapproved | BR-007 | FR-012 | US-011 | Decision proposal | `test_navigation_and_decision` | UAT-012 | Accountable next step |
| Valid normalised weights; zero weights rejected | BR-001 | FR-013 | US-001 | Health index | `test_health_and_opportunity` | UAT-013 | Inspectable priorities |
| Home signal opens investigation | BR-003 | FR-014 | US-003 | Navigation/scope | `test_navigation_and_decision` | UAT-014 | Practical workflow |

Tests: [engines](../../tests/test_engines.py) and [interface](../../tests/test_app.py). [Criteria](11-acceptance-criteria.md) define numerical acceptance; [actual results](20-uat-results.md) are generated from JUnit. Stakeholder acceptance remains Not Run.

Example discovery chain: CFO statement → BR-002 (one financial truth) → FR-002/FR-011 → US-002 → AC-001/AC-002/AC-010 → ledger and publication gate → executable fixture/reconciliation/failure tests → proposed consistency benefit.