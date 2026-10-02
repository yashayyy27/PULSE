> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Data flow and lineage

```mermaid
flowchart TD
    G[Deterministic synthetic generator] --> R[Compressed raw CSV and hash manifest]
    R --> V[Null key range grain and coverage validation]
    V --> S[Constrained SQLite star schema]
    S --> M[SQL daily mart and monthly customer views]
    M --> K[Governed KPI registry]
    K --> A[Warnings and profit investigation]
    K --> F[Chronological forecasts]
    K --> C[Conditional scenarios]
    A --> U[Streamlit management review]
    F --> U
    C --> U
    U --> B[HTML brief and session evidence exports]
```

Sales lineages: source order → fact_sales → location/day aggregation → revenue and product cost → profit ledger. Payroll: employee/day → fact_labour → separate location/day aggregate → profit ledger. Stock: store/SKU/day → unavailable check count → stockout rate; opportunity uses same-SKU available-day observations. Feedback: response → order FK → location/day rating sums and counts → weighted mean. Retention bypasses additive mart customer counts and uses distinct customer/month activity.

[Data dictionary](13-data-dictionary.md) specifies grain and keys. A failed validation never replaces the previous DB. Forecast model selection excludes final holdout. User questions never become arbitrary SQL. Registry definition changes require Finance/Operations review under [governance](27-data-governance.md).
