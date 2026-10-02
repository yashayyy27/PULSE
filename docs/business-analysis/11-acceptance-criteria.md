> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Testable acceptance criteria

| AC | Given / when / then | Evidence |
|---|---|---|
| AC-001 | Given list sales 1,000, discount 100, refund 20, COGS 300, payroll 200, fees 30, overhead 50, campaign 10; calculate; revenue 880, GP 580 and operating profit 290 | test_governed_ledger |
| AC-002 | Given source and mart; aggregate; revenue, COGS and payroll reconcile without fanout | test_sql_reconciliation |
| AC-003 | Given baseline 100 for 8 weeks and actual 70; detect; adverse warning has baseline 100; actual 130 does not warn | test_anomaly_edges |
| AC-004 | Given adjacent periods; investigate; all bridge impacts sum to observed profit delta and dimension rows sum to revenue delta | test_bridge_and_dimensions |
| AC-005 | Given overlapping warnings for one store; summarise; count only one operating-profit exposure | test_alert_and_exposure |
| AC-006 | Given no scenario changes; simulate; reproduce ledger; 10% hours cut changes profit by 10% payroll cost | test_scenarios_identity_and_sensitivity |
| AC-007 | Given altered final forecast holdout; rerun; selected models/calibration widths do not change | test_forecast_chronology |
| AC-008 | Given supported question; answer; return numerical evidence, method, scope and limits; unknown/SQL input is bounded | test_ask_evidence / test_unknown_and_sql_injection |
| AC-009 | Given latest month; calculate retention; return missing because next month has not been observed | test_cohorts_retention_and_promotions |
| AC-010 | Given corrupt IDs/values/grains; validate; fail named rules and retain previously published DB | test_validation_detects_corruption / test_failed_publish_retains_database |
| AC-011 | Given each navigation target; render; no exception and correct page title | test_every_page |
| AC-012 | Given valid proposed owner/action; record; status remains unapproved and downloadable | test_navigation_and_decision |
| AC-013 | Given invalid/all-zero health weights; calculate; reject; valid weights sum to 1 | test_health_and_opportunity |
| AC-014 | Given full pipeline; export brief; values match current ledger and output HTML contains limitations | test_brief_reconciles |

Tests are developer verification. Stakeholder acceptance and benefit validation require a real pilot; see [UAT plan](19-uat-plan.md).
