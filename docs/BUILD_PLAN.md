# PULSE build plan

Status: completed locally; actual verification is in [FINAL_AUDIT.md](FINAL_AUDIT.md). All business, stakeholder and data examples are synthetic.

## Inspection and preservation

The parent workspace has unrelated coursework and an independent, committed RESTOPS repository (`opspulse/`). Preserve both. PULSE is a separate project in `PULSE/`; do not alter or stage parent files. Existing RESTOPS financial-ledger and temporal-validation principles inform the design, but PULSE has its own company, data and implementation.

## Business model and decisions

Fictional **Wattle & Rye**, an Australian neighbourhood food and pantry retailer, operates 36 stores across NSW, VIC, QLD, WA, SA and ACT. Two years (2024–2025) of synthetic orders, products, customer segments, labour, promotions, stock availability, feedback and expenses support a weekly management decision: which store needs investigation, how much profit movement is associated with it, and which conditional intervention deserves a pilot?

## Architecture and structure

`pulse/data` deterministic generation and validation → compressed CSV raw layer → constrained SQLite star schema → SQL daily/monthly marts → governed metrics → modular alerts, investigation, financial exposure, forecasting, scenarios, queries and reports → Streamlit application.

Directories: `pulse/{data,metrics,analytics,alerts,forecasting,scenarios,query,reports}`, `sql/`, `scripts/`, `app/`, `tests/`, `config/`, `docs/business-analysis/`, `data/raw/`, `reports/`. Generated raw data/database are ignored. Commit small evidence reports and a real application screenshot. SQLite is bundled with Python; isolate connection/query functions so a future PostgreSQL migration has a clear boundary.

## Data model

Dimensions: date (day), location (store), product (SKU), customer (anonymous synthetic ID), channel, promotion, employee. Facts: sales (one order with one featured product; quantity may exceed one), labour (employee/day), inventory (store/product/day), operating costs (store/day), feedback (response) and promotions (store/campaign/day spend). Explicit primary/foreign keys. Taxes excluded; amounts in AUD; product cost captured at sale. Grain-safe aggregation precedes joins. No claim of multi-line POS fidelity.

## Methods and risks

- SQL ledger: revenue = list sales − discounts − refunds; gross profit = revenue − COGS; operating profit subtracts labour, channel fees, overhead and campaign spend once.
- Weekly warnings compare the latest complete Monday–Sunday week with eight prior weeks. Median/MAD plus materiality threshold, denominator floors and financial exposure estimates; no seed labels in analytics.
- Exact operating-profit bridge and dimensional revenue contributors. These are accounting associations, not causes. Stockout opportunity uses comparable available days and explicit substitution assumptions; never add overlapping opportunity estimates.
- Four KPI forecasts: last-week seasonal naive versus trailing weekday averages; expanding-window model selection, untouched final holdout, horizon-specific empirical bands. Small samples and structural breaks limit reliability.
- Scenarios preserve observed ledger at zero changes and expose price, demand, basket, hours, wages, discounts, margin, promotion uptake and retention assumptions without double counting.
- Ask PULSE routes supported intents to read-only SQL/analysis; unsupported questions return a bounded explanation. No paid service.
- Configurable health weights are stakeholder assumptions, not empirical predictions. Suppress analytical output if validation fails.
- Risks: synthetic patterns are not business evidence; seasonality may trigger alerts; respondent/customer selection biases; local performance; no production authentication or live integration.

## Milestones and implementation sequence

1. Architecture, company and deterministic generator (full target 500k–1.5m orders; small CI mode).
2. Constrained database, SQL joins/CTEs/windows, profitability, cohorts and retention.
3. Data quality and central KPI registry.
4. Executive overview.
5–7. Alerts, investigation and financial impact.
8–11. Forecasts, Scenario Lab, Ask PULSE and generated HTML Monday brief.
12–13. Discovery, prioritisation, traceability, governance, adoption and proposed benefits.
14–15. Pytest, simulated developer UAT and GitHub Actions.
16–17. README/recruiter walkthrough, full demo, every application view, SQL/documentation/Mermaid checks and final audit.

Dependencies: Python 3.11–3.12, NumPy, Pandas, Plotly, Streamlit; pytest and Ruff for development. SQLite is standard-library. No proprietary credentials. HTML export is the portable reporting format; PDF is a deferred convenience.

## Verification and phase gates

At each major phase run relevant tests and inspect actual output; preserve previous behaviour. Validate raw nulls, duplicates, IDs, dates, categories, values, coverage, reconciliations and foreign keys before publication. Use tiny hand-calculated fixtures for metrics/bridges/scenarios and chronological fixtures for forecasts. Execute a full two-year dataset and application page tests. Check local links and render Mermaid using an available parser. Record actual commands/results in `FINAL_AUDIT.md`; distinguish automated developer verification from real stakeholder UAT. Commit coherent phases in the isolated repository when filesystem permissions allow.
