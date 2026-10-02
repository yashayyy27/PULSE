> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Current and future process maps

```mermaid
flowchart LR
    A[Source extracts] --> B[Weekly manual reports]
    B --> C[Manager inspects totals]
    C --> D[Issue noticed late]
    D --> E[Analyst reconciles definitions]
    E --> F[Management meeting]
    F --> G[Action with limited outcome tracking]
```

```mermaid
flowchart LR
    A[Synthetic refresh] --> B{Data contract passes}
    B -->|No| C[Retain previous database and repair]
    B -->|Yes| D[Publish governed marts]
    D --> E[Complete-week monitoring]
    E --> F[Warning and financial reference gap]
    F --> G[Manager reviews ledger evidence]
    G --> H[Conditional scenario]
    H --> I[Unapproved decision proposal and export]
    I --> J[Future organisational pilot and benefit review]
```

Technology owns the refresh gate; Finance owns metric approval; Operations owns investigations. The final pilot box is a proposed organisational process, not an automated application action. [RACI](28-raci-matrix.md) assigns accountability; [implementation plan](23-implementation-plan.md) defines readiness gates.
