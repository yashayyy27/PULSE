> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Risk register

| Risk | Likelihood / impact | Owner | Mitigation / trigger |
|---|---|---|---|
| R-01 Synthetic mechanics mistaken for real-company evidence | High / high | BA | Label every surface; no achieved benefits; interview discussion explicit |
| R-02 Fanout inflates payroll and profit errors | Medium / high | Analytics | Pre-aggregate facts; independent ledger tests |
| R-03 Slow drift normalises into rolling baseline | High / medium | Operations | Inspect trends and period movement; production add seasonal/control baselines |
| R-04 Campaign confounding creates false causal claims | High / high | Marketing | Label observational ROI; pilot with controls before budget shift |
| R-05 Holiday and event seasonality creates false alerts | High / medium | Operations | Complete weeks reduce weekday bias; production calendar/event controls |
| R-06 Low forecast interval coverage | Medium / high | Planner | Show holdout coverage and small calibration sample; reject guaranteed forecasts |
| R-07 Users confuse cohort retention with repeat rate | Medium / medium | Marketing | Governed definitions, distinct customer counts, final-month censoring |
| R-08 Staff cuts harm service | Medium / high | Store Manager | Conditional scenario only; pre-agreed satisfaction/service guardrails |
| R-09 Snapshot corruption / incomplete refresh | Medium / high | Technology | Constraints, coverage checks, atomic publish, fail-closed app |
| R-10 Low adoption due to unclear ownership | Medium / high | COO | Pilot role ownership, task training and proposed investigation SLA |
| R-11 Local app exposed with no authentication | Low local / high production | Technology | Bind loopback; production access/security design before exposure |

Residual risk is stated, not hidden by passing tests. [Assumptions](18-assumptions-constraints.md) and [rollout gates](23-implementation-plan.md) identify where better source data or real stakeholder feedback is necessary.
