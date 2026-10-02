> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Architectural and product decision log

| ADR | Context / decision | Alternatives | Trade-offs |
|---|---|---|---|
| ADR-001 | No credentials and available Python runtime: SQLite star schema and analytical views | DuckDB, PostgreSQL | Standard library and FK constraints; slower large queries and no concurrent production warehouse. Isolate runtime connection for future PostgreSQL |
| ADR-002 | Ask PULSE needs evidence without paid services: deterministic intents and bound SQL templates | LLM text-to-SQL, unrestricted search | Auditable bounded vocabulary; unsupported questions rejected |
| ADR-003 | Public portfolio cannot use employer/customer data: seeded synthetic company | Anonymised employer data, public retail sample | Reproducible multi-domain problems; validates mechanics not external business effectiveness |
| ADR-004 | Managers need to challenge warnings: complete-week median/MAD and materiality | Isolation forest, deep anomaly model | Explainable and inexpensive; holiday effects and gradual drift remain risks |
| ADR-005 | Two-year fictional history and transparent interview discussion: seasonal naive / weekday mean | ARIMA, boosted features | Chronological comparison easy to audit; three-origin empirical bands have uncertain coverage |
| ADR-006 | SQL matters and fact grains differ: aggregate facts independently then join | Single transaction-enriched table | Prevents payroll fanout; separate customer/cohort path needed |
| ADR-007 | Scenario levers can double count AOV/price: treat basket quantity, price and volume independently | One unconstrained AOV multiplier | Requires explicit assumptions; no automatic elasticity |
| ADR-008 | Decisions need ownership but production auth absent: session-only unapproved proposals and export | Persistent approvals, fake approval button | Honest local workflow; data lost unless exported |
| ADR-009 | Executive exposure should not sum related KPI gaps: sum operating-profit warnings once per store | Sum every warning or max each KPI | Conservative narrow exposure can be zero despite other warnings; display nonmonetary attention separately |
| ADR-010 | Portable reporting matters more than another dependency: HTML brief with print stylesheet | PDF engine and scheduling service | Working export; user browser can print; no automated scheduler or built-in PDF claimed |

Architecture choices resolve the [discovery conflicts](04-discovery-notes.md). Future changes must preserve definition ownership and test evidence under [governance](27-data-governance.md).
