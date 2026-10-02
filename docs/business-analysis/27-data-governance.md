> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Data governance and production considerations

Source of truth: fact_sales net-sales ledger; fact_labour loaded payroll; fact_inventory daily SKU checks; fact_operating_costs overhead; fact_promotions campaign spend; fact_feedback responses. Analytical truth: grain-safe mart_daily plus the [KPI registry](12-kpi-dictionary.md). Distinct customers, cohorts and retention use fact_sales rather than summing daily distinct counts.

Owners: Finance owns ledger/profit/refunds; Operations owns labour/service; Marketing owns identified customer and campaign definitions; Supply chain owns availability; Technology owns source contracts and refresh. Analytics stewards model lineage and tests. Each metric's owner, formula, grain, source, interpretation and limitation are generated from code in the KPI dictionary.

Change control: request with decision purpose → business-owner approval → impact and traceability review → versioned SQL/registry edit → reconciliation and UAT → release notes and training. For example, adding central overhead changes operating profit and every scenario/brief using it; Finance approval and regression tests precede release. One central implementation prevents silent spreadsheet variants.

Local release: synthetic IDs only, read-only analytics, parameterised values, no secrets. Session exports may contain user-entered text; avoid real PII. Production requirements: authenticated role access and least privilege; minimised/tokenised customer IDs; source consent/privacy review; managed secrets; audit logs without customer payloads; refresh/staleness alerting; secure backups and deletion policy. Retention periods must be set with the organisation's legal/security teams; no statutory claim is made here. None of those production controls is falsely presented as fully implemented.
