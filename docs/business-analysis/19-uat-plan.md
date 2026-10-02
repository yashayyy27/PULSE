> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# UAT plan

Scope: eleven views and the complete decision workflow, using synthetic data. Developer automation supplies executable evidence; this is **simulated UAT**, not acceptance by real COO/CFO/store managers.

Entry: validated DB, reconciled ledgers and test fixtures; each acceptance criterion has a named test. Execution: pytest exercises known ledger inputs, deliberate corruption, forecasting split changes, all views, drill-down/navigation, scenario save, question analysis and decision proposal. Record IDs, expected/actual outcomes and test case results from JUnit rather than manually marking Pass.

Real pilot roles: CFO checks ledger definitions, Regional Manager judges alert usefulness, store manager completes an investigation task, Marketing reviews inference wording and Technology reviews refresh/access design. Collect task completion, time, confusion and unhandled issues. Exit for real acceptance: all Must requirements accepted, severe defects repaired and sponsor sign-off recorded. Those real acceptance gates are not yet met by a portfolio demo.

The generated [results](20-uat-results.md) distinguish automated Pass from stakeholder Not Run. [Acceptance criteria](11-acceptance-criteria.md) and [traceability](16-traceability-matrix.md) tie this plan to delivered features.
