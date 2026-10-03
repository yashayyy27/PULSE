"""Generate BA artefacts from curated case material and governed source definitions."""

from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pulse.metrics.registry import REGISTRY
from pulse.runtime import ROOT

BA = ROOT / "docs/business-analysis"
INTRO = "> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.\n\n"
DOCS = {
    "01-business-problem.md": """# Business problem

The fictional COO sees consolidated weekly totals while store-level profit pressure accumulates unnoticed. Finance spends the review meeting reconciling competing definitions; Operations asks for specific investigation priorities; Marketing treats campaign revenue as evidence of success. The ambiguous request “give us a better dashboard” hides three different decisions: recognise material deterioration, allocate investigation effort, and assess an intervention before approval.

PULSE addresses **late detection and inconsistent decision evidence**. It does not automate management judgement. The weekly decision unit is a store investigation with an accountable role, a financial reference gap, an evidence trail and service guardrails. The solution presents observed synthetic records separately from estimated exposures, forecasts and conditional scenarios.

Scope: 36 stores, six Australian jurisdictions, 24 months. Outcomes such as faster detection and less reporting preparation are hypotheses to measure in a real pilot, not results from this prototype. The [charter](02-project-charter.md) bounds delivery; [benefits plan](25-benefits-realisation.md) defines proposed success measures.
""",
    "02-project-charter.md": """# Project charter

**Sponsor (fictional):** COO. **Financial authority:** CFO. **Delivery lead:** Business Analyst / Analytics Engineer. **Purpose:** convert performance reporting into a governed investigation-and-decision workflow.

Deliverables: constrained synthetic star schema; SQL analytical marts; KPI registry; executive overview; weekly warnings; profit bridge and dimensional investigation; estimates with assumptions; four KPI forecasts; Scenario Lab; deterministic Ask PULSE; HTML brief; quality evidence; BA and adoption pack.

In scope: a local portfolio prototype, synthetic discovery and developer verification. Out of scope: live POS/payroll integration, customer targeting, autonomous recommendations, production access controls, real stakeholder approval and legal roster validation. A prototype cannot establish organisational benefit.

Exit gates: full source generation and reconciliation; functioning six primary destinations and contextual evidence lenses; analytics and navigation tests; no fabricated UAT pass; accessible textual chart evidence; reproducible setup and documented trade-offs. [Traceability](16-traceability-matrix.md) connects each deliverable to a need. [Implementation plan](23-implementation-plan.md) distinguishes this release from a potential organisational rollout.
""",
    "03-stakeholder-map.md": """# Stakeholder map

| Role | Goal / pain | Influence and engagement | Decision responsibility |
|---|---|---|---|
| COO | Act before deterioration becomes entrenched; limited review time | High; weekly exception review | Investigation priority and rollout sponsor |
| CFO | One profit definition; reconcile costs without join inflation | High; definition approval workshop | Financial KPI definitions and exposure assumptions |
| Regional Operations Manager | Find store pressure without reading 36 reports | High; prototype walkthrough | Assign store investigations and service guardrails |
| Finance Analyst | Inspect underlying calculations and export evidence | Medium; SQL reconciliation session | Steward ledger and variance evidence |
| Marketing Manager | Distinguish campaign sales from incremental contribution | Medium; observational comparison review | Campaign pilot hypotheses |
| Store Manager | Short morning queue, fair context and feasible actions | Medium; task-based usability trial | Validate operational context; no unilateral staffing change |
| Data / Technology Team | Maintainable pipeline and owned metrics | High; technical design review | Source contracts, refresh, support and access design |

A power/interest strategy puts COO/CFO/Technology in definition and release decisions, store managers in usability and guardrail review, and analysts in reconciliation. Role labels in the application are fictional proposals, not authenticated assignments. See [discovery](04-discovery-notes.md) and [RACI](28-raci-matrix.md).
""",
    "04-discovery-notes.md": """# Simulated discovery notes

| Raw stakeholder statement | BA question | Need uncovered | Derived requirement |
|---|---|---|---|
| COO: “I have five minutes before the weekly meeting.” | Which decision should those minutes produce? | Prioritised investigations, not every KPI | BR-001 / FR-001 |
| CFO: “Finance and Operations must use the same profit.” | Which costs and tax treatment belong in it? | AUD excl. GST; payroll, fees, overhead and campaigns once | BR-002 / FR-002 |
| Regional Manager: “Tell me which store to call.” | What evidence makes a warning credible? | Baseline, period, materiality and ledger drivers | BR-003 / FR-003 |
| Finance Analyst: “I need to trace every number.” | What grain and reconciliation do you trust? | Separate fact aggregation and inspectable SQL | BR-002 / FR-004 |
| Marketing: “Discounts grow sales, but is that value?” | Can available data prove incremental demand? | Observational contribution comparison with explicit confounding | BR-006 / FR-009 |
| Store Manager: “A red number without context feels unfair.” | What context and guardrails matter? | Service, payroll and period evidence; propose before approval | BR-007 / FR-012 |
| Technology: “Who owns a changed metric?” | What review and refresh contract is needed? | Registry, validation gate and definition change control | BR-008 / FR-011 |

Assumptions exposed: payroll is loaded hourly cost; the prototype lacks outage duration; guest customers cannot be retained; promotions are not randomised; calendars are synthetic and exclude actual holiday effects. Open questions for a real pilot: treatment of returned inventory, central overhead allocation, minimum response count and store manager alert tolerance.

Conflicts: CFO wants detail, COO wants brevity; resolve with executive summary plus evidence drill-down. Marketing wants causal ROI, Technology cannot supply a control group; deliver labelled observational economics and propose a controlled pilot. Operations wants savings from fewer hours, Store Managers want service protection; scenarios are conditional and decisions are proposals. See [decision log](29-decision-log.md).
""",
    "05-current-state.md": """# Current-state assessment

Fictional process: weekly reports are assembled → managers inspect totals manually → someone notices deterioration → an analyst reconciles definitions → a meeting chooses an action → outcomes are rarely compared with a frozen baseline.

Handoffs: source owners supply extracts; Finance calculates profit; Operations reviews stores; Marketing reports campaign sales. Failure modes include different discount treatment, payroll multiplied by transaction joins, incomplete-period comparisons and unclear investigation ownership. No measured cycle-time baseline exists; discovery must measure it before a real rollout.

Controls proposed for transition: agree cost grain, define net sales, expose period completeness, distinguish estimates and record a proposed decision. The [process map](14-process-map.md) shows handoffs; [change assessment](22-change-impact-assessment.md) addresses adoption risks rather than assuming a dashboard creates action.
""",
    "06-future-state.md": """# Future-state design

A synthetic source refresh is validated and only then published. The weekly engine compares complete Monday–Sunday periods. Management sees observed business performance, material reference gaps and an attention queue; an analyst drills into a reconciled profit bridge and dimensional revenue contributors; a manager tests conditional assumptions and records an unapproved investigation proposal.

The executable local loop ends with session export. It does not implement durable organisational approval, case ownership, alerts by email or benefits measurement. A real rollout would add case workflow, role permissions, integration contracts and service guardrails before any operational change.

Decisions supported: allocate review effort, challenge campaign economics, assess product availability hypotheses, discuss staffing feasibility and decide whether to commission a pilot. Every output has a period, scope and epistemic label (observed, estimated, forecast or scenario). [Functional requirements](08-functional-requirements.md) define the current release; [implementation plan](23-implementation-plan.md) defines the future organisational steps.
""",
    "07-business-requirements.md": """# Business requirements and prioritisation

| ID | Why / business need | MoSCoW | Value / effort (1–5) | Rationale and trade-off |
|---|---|---|---|---|
| BR-001 | Allocate scarce executive attention to material store issues | Must | 5 / 2 | COO urgency; summary reuses governed marts |
| BR-002 | Trust reconciled and consistent financial evidence | Must | 5 / 4 | Financial errors invalidate decisions; costs kept at their own grain |
| BR-003 | Detect deterioration before manual report inspection | Must | 5 / 3 | Operational urgency; explainable methods reduce support risk |
| BR-004 | Investigate associated contributors without causal overclaim | Must | 5 / 3 | Required to defend warnings and focus store discussion |
| BR-005 | Evaluate conditional commercial interventions | Must | 4 / 3 | Cost ledger available; behavioural response remains an assumption |
| BR-006 | Review customer, availability and campaign economics | Should | 4 / 4 | Useful diagnosis; missing controls limit campaign inference |
| BR-007 | Communicate evidence and propose an accountable investigation | Should | 4 / 2 | HTML export and session log; durable approvals deferred |
| BR-008 | Maintain owned, reliable and reproducible definitions | Must | 5 / 3 | No source credentials; data contract and registry necessary |
| BR-009 | Understand future demand with honest uncertainty | Should | 3 / 3 | History available; transparent baselines fit prototype risk |
| BR-010 | Make evidence accessible through supported business questions | Could | 3 / 2 | Templates economical; unrestricted conversation not justified |

Value vs effort matrix: high value / low effort = executive summary and brief; high value / higher effort = ledger, warnings and investigation; moderate value / low effort = deterministic Ask PULSE; moderate value / higher effort = production integrations and access design. Scores are simulated stakeholder judgements, not measured ROI. “Should/Could” items shipped only after Must checks passed; priority is delivery order, not a claim they remain absent.

**Won’t have this release:** paid LLM, causal campaign lift, automated roster changes, live integrations, durable approvals and PDF library export. These have higher risk, missing data or little incremental decision value. HTML can be printed by the browser. [Traceability](16-traceability-matrix.md) explains the implementation links.
""",
    "08-functional-requirements.md": """# Functional requirements

| ID | What PULSE must do | Implemented feature |
|---|---|---|
| FR-001 | Show revenue/profit/margin/orders with equal-length period comparison | Home |
| FR-002 | Calculate governed ratios from additive sums and distinct period customers | KPI registry and ledger |
| FR-003 | Flag adverse complete-week deviations with baseline, severity and exposure | Signals |
| FR-004 | Reconcile profit movement and rank ten dimensions of revenue movement | Investigate |
| FR-005 | Quantify conditional stockout opportunity and prevent overlapping exposure totals | Operations / alert exposure summary |
| FR-006 | Forecast revenue, orders, GP and paid hours with chronological evaluation | Investigate / Forecast lens |
| FR-007 | Preserve base case at zero changes and compare saved conditional scenarios | Scenario Lab |
| FR-008 | Route supported analytical questions to bounded evidence; reject SQL/unknown intent | Ask PULSE |
| FR-009 | Show repeat/retention/cohorts and observational promotion economics | Customers / Operations |
| FR-010 | Export a company-wide brief from computed results | Briefs |
| FR-011 | Validate raw contracts and publish only a reconciled constrained model | Pipeline / Data Quality |
| FR-012 | Record an unapproved proposed investigation and export session evidence | Investigate decision form |
| FR-013 | Explain targets and configure health dimension weights | Methodology |
| FR-014 | Offer store/period scope and working warning-to-store navigation | Shared context / Signals |

Metric semantics and scope exceptions are visible: retention, campaigns and brief are company-wide; forecasts end at the dataset origin; weekly alerts always use the latest complete week. See [acceptance criteria](11-acceptance-criteria.md) for testable outcomes and [dictionary](12-kpi-dictionary.md) for limits.
""",
    "09-non-functional-requirements.md": """# Non-functional requirements

| ID | Quality constraint and verification | Current boundary |
|---|---|---|
| NFR-001 Usability | All six destinations render; Home presents health, exposure and actionable signal evidence | Developer walkthrough, not manager usability study |
| NFR-002 Maintainability | Modular engines; central registry; Ruff and pytest in CI | No microservices or unnecessary adapter layers |
| NFR-003 Performance | Full 0.5–1.5m order target works locally; small CI fixture; query latency recorded in audit | Measured host-specific timings, no production SLA |
| NFR-004 Reliability | Validation/FK/reconciliation fail before atomic database replacement | Prototype crash recovery preserves prior DB |
| NFR-005 Reproducibility | Same seed gives identical source frames and gzip byte hashes; setup regenerates without credentials | Dependencies pinned; generated DB binary layout need not match |
| NFR-006 Security | Analytics opens SQLite read-only; values parameterised; dimensions allow-listed; user SQL rejected | No authentication or user roles implemented |
| NFR-007 Accessibility | Text tables accompany key plots; warning severity labels; readable contrast; no colour-only decision | No claimed WCAG certification; manual review required |
| NFR-008 Analytical integrity | Every estimate exposes assumptions; no achieved-benefit or causal claims; final retention censored | Synthetic data validates mechanics, not external validity |

Acceptance: automated tests and document checks in [UAT evidence](20-uat-results.md); manual browser screenshot inspection in [final audit](../FINAL_AUDIT.md). Production accessibility and concurrent-user testing remain pre-rollout requirements, not implemented guarantees.
""",
    "10-user-stories.md": """# User stories

| Story | As a… / I want… / so that… | Requirements |
|---|---|---|
| US-001 | COO: see a concise weekly business view so I can prioritise store discussion | FR-001, FR-013 |
| US-002 | CFO: reconcile cost and profit definitions so departments use the same evidence | FR-002, FR-011 |
| US-003 | Regional Manager: see material complete-week warnings so I know which manager to call | FR-003, FR-014 |
| US-004 | Finance Analyst: inspect a profit bridge and dimension contributors so I can explain movement | FR-004 |
| US-005 | Supply lead: see assumption-based stockout opportunity so I can assess a pilot | FR-005 |
| US-006 | Operations planner: compare forecast baselines and errors so staffing discussion acknowledges uncertainty | FR-006 |
| US-007 | COO: compare conditional cases so I can challenge demand, pricing and staffing assumptions | FR-007 |
| US-008 | Store Manager: ask a supported question and see evidence so analysis is explainable | FR-008 |
| US-009 | Marketing Manager: distinguish repeat/retention and observational ROI so I do not confuse sales with causal value | FR-009 |
| US-010 | COO: export an executive brief so a meeting has consistent evidence | FR-010 |
| US-011 | Regional Manager: record a proposed owner/action so investigation has a reviewable next step | FR-012 |

Each story is demonstrated in the local app. [Acceptance criteria](11-acceptance-criteria.md) and [traceability](16-traceability-matrix.md) prevent features without a decision purpose.
""",
    "11-acceptance-criteria.md": """# Testable acceptance criteria

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
""",
    "14-process-map.md": """# Current and future process maps

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
""",
    "15-data-flow.md": """# Data flow and lineage

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
""",
    "17-risk-register.md": """# Risk register

| Risk | Likelihood / impact | Owner | Mitigation / trigger |
|---|---|---|---|
| R-01 Synthetic mechanics mistaken for real-company evidence | High / high | BA | Label every surface; no achieved benefits; interview discussion explicit |
| R-02 Fanout inflates payroll and profit errors | Medium / high | Analytics | Pre-aggregate facts; independent ledger tests |
| R-03 Slow drift normalises into rolling baseline | High / medium | Investigate / Operations lens | Inspect trends and period movement; production add seasonal/control baselines |
| R-04 Campaign confounding creates false causal claims | High / high | Marketing | Label observational ROI; pilot with controls before budget shift |
| R-05 Holiday and event seasonality creates false alerts | High / medium | Investigate / Operations lens | Complete weeks reduce weekday bias; production calendar/event controls |
| R-06 Low forecast interval coverage | Medium / high | Planner | Show holdout coverage and small calibration sample; reject guaranteed forecasts |
| R-07 Users confuse cohort retention with repeat rate | Medium / medium | Marketing | Governed definitions, distinct customer counts, final-month censoring |
| R-08 Staff cuts harm service | Medium / high | Store Manager | Conditional scenario only; pre-agreed satisfaction/service guardrails |
| R-09 Snapshot corruption / incomplete refresh | Medium / high | Technology | Constraints, coverage checks, atomic publish, fail-closed app |
| R-10 Low adoption due to unclear ownership | Medium / high | COO | Pilot role ownership, task training and proposed investigation SLA |
| R-11 Local app exposed with no authentication | Low local / high production | Technology | Bind loopback; production access/security design before exposure |

Residual risk is stated, not hidden by passing tests. [Assumptions](18-assumptions-constraints.md) and [rollout gates](23-implementation-plan.md) identify where better source data or real stakeholder feedback is necessary.
""",
    "18-assumptions-constraints.md": """# Assumptions and constraints

AUD excluding GST; synthetic orders feature one SKU with multiple units. Returns reverse revenue but do not reverse recorded product cost. Loaded hourly payroll includes on-costs in fictional rates. Overhead excludes depreciation, tax, financing and central office allocations. Inventory is a daily availability snapshot, not units lost or outage duration. Feedback is voluntary and biased. Customer ID 0 is a guest, never one persistent customer.

Two years permit weekly and monthly comparisons, but do not validate business seasonality in the real world. The generator uses annual seasonality rather than an authoritative holiday calendar. Forecast intervals have only three calibration origins; show actual held-out coverage. Promotion references are observational same-store/weekdays. First-observed cohorts are left-censored; latest-month next-month retention is right-censored.

Financial alert gaps are references, not recovered profit. Stockout opportunities assume substitution and minimum matched sample size; do not sum with warning exposures. Scenarios hold specified cost/mix factors fixed and require explicit demand response; retention uses repeat-customer share as a disclosed proxy.

Local SQLite, no credentials and session-only decision/scenario exports constrain this release. No production SLA, access control or native approval workflow is claimed. Dependencies and full generation commands appear in [README](../../README.md); [decision log](29-decision-log.md) explains choices.
""",
    "19-uat-plan.md": """# UAT plan

Scope: six destinations, contextual analytical lenses and the complete decision workflow, using synthetic data. Developer automation supplies executable evidence; this is **simulated UAT**, not acceptance by real COO/CFO/store managers.

Entry: validated DB, reconciled ledgers and test fixtures; each acceptance criterion has a named test. Execution: pytest exercises known ledger inputs, deliberate corruption, forecasting split changes, all views, drill-down/navigation, scenario save, question analysis and decision proposal. Record IDs, expected/actual outcomes and test case results from JUnit rather than manually marking Pass.

Real pilot roles: CFO checks ledger definitions, Regional Manager judges alert usefulness, store manager completes an investigation task, Marketing reviews inference wording and Technology reviews refresh/access design. Collect task completion, time, confusion and unhandled issues. Exit for real acceptance: all Must requirements accepted, severe defects repaired and sponsor sign-off recorded. Those real acceptance gates are not yet met by a portfolio demo.

The generated [results](20-uat-results.md) distinguish automated Pass from stakeholder Not Run. [Acceptance criteria](11-acceptance-criteria.md) and [traceability](16-traceability-matrix.md) tie this plan to delivered features.
""",
    "22-change-impact-assessment.md": """# Change impact assessment

| Stakeholder | Current → future behaviour | Training / communication | Adoption risk and mitigation |
|---|---|---|---|
| COO | Review all totals → review prioritised exceptions and proposed owners | Five-minute Monday walkthrough; explain non-overlapping exposure | Treat estimates as savings; label reference gap and require pilot |
| CFO / Finance | Reconcile department spreadsheets → approve central ledger and inspect bridge | Worked accounting example; metric change procedure | Lost control of definitions; Finance retains business ownership |
| Regional Manager | Call stores based on anecdotes → inspect warnings and assign investigation | Complete-week and baseline exercise | Alert fatigue; review usefulness and threshold changes in pilot |
| Store Manager | Defend a red metric → validate context and propose service-safe action | Ten-minute task practice using fictional store | Perceived surveillance; no ranking as performance verdict |
| Marketing | Celebrate campaign revenue → discuss contribution and confounding | Same-weekday comparison and causal limitations | Disputed ROI; controlled pilot before reallocating budget |
| Technology | Ad hoc extracts → source contracts, validation and controlled publication | Runbook and failure recovery | Support load; clear steward and refresh expectations |

Changes affect decision habits and responsibility, not only interface skills. Establish an investigation meeting cadence and escalation route before rollout. Track rejected warnings, unfinished proposals and definition disputes alongside usage. No adoption rate is claimed; [benefits measures](25-benefits-realisation.md) define evidence to collect.
""",
    "23-implementation-plan.md": """# Implementation plan

**Delivered portfolio release:** local synthetic pipeline, six primary destinations and contextual evidence lenses, SQL/analytics tests, simulated UAT and evidence exports. This demonstrates mechanics; it is not an installed organisational system.

**Potential organisational rollout:**
1. Pilot three stores and one regional manager; obtain real source contracts, metric approvals, least-privilege access and privacy review.
2. Collect feedback for four weekly cycles; record false warnings, missing context, task completion and preparation time.
3. Execute role-based UAT; resolve critical ledger, access and usability defects; require CFO/COO sign-off.
4. Train managers with cost-ledger and scenario exercises; publish support contacts and escalation.
5. Limited rollout to one region; monitor pipeline timeliness, investigation queue age and service guardrails.
6. Gate wider rollout on accepted metrics, stable refresh, usable warnings and support ownership.
7. Review proposed benefits at 30/60/90 days; compare measured baselines and investigate confounders.

Dependencies: source availability, agreed tax/returns treatment, promotion controls, workforce data policy and authentication. Rollback: retain previous validated snapshot, suspend warnings and revert to approved manual reporting; communicate stale-data timestamp. Release accountability appears in [RACI](28-raci-matrix.md). No implementation dates or approvals are fabricated.
""",
    "24-training-support-plan.md": """# Training and support plan

Role-based exercises: executives identify one weekly priority in five minutes; Finance recomputes A$290 profit from the acceptance fixture; regional managers explain a warning baseline and propose an owner; store managers compare a staffing scenario with satisfaction guardrails; Marketing explains why observational ROI is not incremental lift; Technology reproduces setup and a validation failure.

Learning check: participants must correctly label observed/estimated/forecast/scenario, distinguish repeat rate from retention, and identify overlapping exposure estimates. Use task-based observation rather than attendance as competence evidence. Accessibility feedback should include labels, keyboard navigation, contrast and table comprehension.

Local support runbook: activate environment → run setup → inspect reports/data_quality.csv and pipeline.json → launch app. If generation fails, keep last DB and repair source; do not override checks. If a KPI is disputed, log the definition request with the business owner before altering SQL/registry. If a forecast seems implausible, inspect holdout errors and structural changes rather than presenting a confident number.

Proposed production support: Technology first response for refresh failures; Finance steward for metric reconciliation; Operations for investigation workflow. Escalate unresolved material errors to CFO/COO and suspend affected outputs. No support SLA or training completion is claimed.
""",
    "25-benefits-realisation.md": """# Proposed benefits realisation

No achieved benefits are claimed. All baselines below are **to be measured before a real pilot**; targets are proposed for sponsor validation.

| Benefit / measure | Baseline | Proposed target | Measurement method | Owner / review |
|---|---|---|---|---|
| Reporting preparation time | Unmeasured | 30% reduction | Timed comparable weekly preparation, 4-week baseline and pilot | Finance / monthly |
| Issue detection lead time | Unmeasured | Review material adverse change within 2 business days of validated refresh | Event-to-warning and manager review timestamps | Operations / weekly |
| KPI consistency | Unmeasured | 100% of approved headline KPIs reconcile | Independent Finance recomputation and definition audit | CFO / monthly |
| Active adoption | Unmeasured | 80% of pilot managers complete weekly investigation task | Authenticated production task completion, not page views alone | COO / monthly |
| Alerts investigated | Unmeasured | 90% of material alerts assigned within 2 days | Workflow audit with false-positive disposition | Regional Manager / weekly |
| Forecast accuracy | Baseline model evaluated in synthetic reports only | Beat seasonal naive MAE without worsening business-relevant bias | Prospective rolling holdout, no test-set tuning | Analytics / monthly |
| Data-quality pass rate | Synthetic pipeline report only | 100% critical rules pass before publication | Contract check log; rejected refreshes counted separately | Technology / daily |
| Anomaly-to-investigation time | Unmeasured | Median <=2 business days | Validated warning and recorded investigation timestamps | Operations / weekly |

Do not infer profit uplift from a scenario. A pilot should measure service/customer guardrails and use comparison stores where feasible. Benefit attribution requires accounting for seasonality, concurrent promotions and demand changes. Stop or revise a pilot if service deteriorates or evidence quality fails.
""",
    "26-discovery-workshop.md": """# Simulated discovery workshop design and outcome

**Participants:** COO, CFO, Regional Operations Manager, Finance Analyst, Marketing Manager, Store Manager and Technology lead. **Duration:** proposed 90 minutes. This workshop did not occur with real people; its output is a coherent requirements simulation.

Agenda: 0–15 min establish business decisions and reporting pain; 15–30 map current handoffs; 30–45 reconcile net sales/profit definitions; 45–60 walk a store deterioration case; 60–75 value/effort prioritisation; 75–90 agree scope, assumptions and unresolved questions.

Prompts: “What action follows a warning?”, “Which costs can we confidently attribute?”, “How could this recommendation harm service?”, “What would make you distrust a number?”, “Which users approve a definition change?”

Simulated outcomes: one governed ledger rather than departmental variants; weekly complete-period warnings rather than noisy daily rankings; summary plus drill-down for conflicting brevity/detail needs; observational campaign economics rather than causal lift; session proposals rather than false production approvals. These decisions directly explain FR-001–FR-014.

Illustrative chain: Store Manager statement “A red number without context feels unfair” → need for defensible operational context (BR-004/BR-007) → reconciled bridge and unapproved proposal (FR-004/FR-012) → US-004/US-011 → AC-004/AC-012 → Investigate page and decision form → tests bridge reconciliation and actual proposal status. See [traceability](16-traceability-matrix.md).
""",
    "27-data-governance.md": """# Data governance and production considerations

Source of truth: fact_sales net-sales ledger; fact_labour loaded payroll; fact_inventory daily SKU checks; fact_operating_costs overhead; fact_promotions campaign spend; fact_feedback responses. Analytical truth: grain-safe mart_daily plus the [KPI registry](12-kpi-dictionary.md). Distinct customers, cohorts and retention use fact_sales rather than summing daily distinct counts.

Owners: Finance owns ledger/profit/refunds; Operations owns labour/service; Marketing owns identified customer and campaign definitions; Supply chain owns availability; Technology owns source contracts and refresh. Analytics stewards model lineage and tests. Each metric's owner, formula, grain, source, interpretation and limitation are generated from code in the KPI dictionary.

Change control: request with decision purpose → business-owner approval → impact and traceability review → versioned SQL/registry edit → reconciliation and UAT → release notes and training. For example, adding central overhead changes operating profit and every scenario/brief using it; Finance approval and regression tests precede release. One central implementation prevents silent spreadsheet variants.

Local release: synthetic IDs only, read-only analytics, parameterised values, no secrets. Session exports may contain user-entered text; avoid real PII. Production requirements: authenticated role access and least privilege; minimised/tokenised customer IDs; source consent/privacy review; managed secrets; audit logs without customer payloads; refresh/staleness alerting; secure backups and deletion policy. Retention periods must be set with the organisation's legal/security teams; no statutory claim is made here. None of those production controls is falsely presented as fully implemented.
""",
    "28-raci-matrix.md": """# RACI matrix

R = Responsible; A = Accountable; C = Consulted; I = Informed. One accountable role per activity. All roles are fictional.

| Activity | COO | CFO | Regional Ops | Finance Analyst | Marketing | Store Manager | Technology / Analytics |
|---|---|---|---|---|---|---|---|
| Requirements | A | C | R | C | C | C | R |
| Financial KPI approval | I | A | C | R | C | I | R |
| Data ownership / contracts | I | C | C | R | C | C | A |
| Data quality | I | C | C | R | I | I | A/R |
| Development | I | C | C | C | C | C | A/R |
| UAT coordination | I | C | A | R | C | R | R |
| Release | A | C | R | I | I | I | R |
| Training | I | C | A | R | C | R | R |
| Dashboard ownership | I | C | A/R | C | C | C | R |
| Financial metric changes | I | A | C | R | C | I | R |
| Ongoing technical support | I | I | C | C | I | I | A/R |

Accountability for source ownership differs by domain in [governance](27-data-governance.md); the consolidated contract activity here is accountable to Technology. Sponsor approval and manager acceptance are proposed real-organisation gates, not actual portfolio sign-offs.
""",
    "29-decision-log.md": """# Architectural and product decision log

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
""",
}


def main():
    BA.mkdir(parents=True, exist_ok=True)
    for name, body in DOCS.items():
        (BA / name).write_text(INTRO + body)
    rows = [
        "# Governed KPI dictionary",
        "",
        INTRO,
        "Definitions are generated from `pulse/metrics/registry.py`; update code and regenerate rather than maintaining parallel formulas.",
        "",
        "| Key / name | Formula | Source / grain | Business / technical owner | Refresh | Interpretation / limitation |",
        "|---|---|---|---|---|---|",
    ]
    for key, kpi in REGISTRY.items():
        k = asdict(kpi)
        rows.append(
            f"| {key}: {k['name']} | `{k['formula']}` | {k['source']}; {k['grain']} | {k['owner']} / {k['technical_owner']} | {k['refresh']} | {k['interpretation']}. {k['limitation']} |"
        )
    rows += [
        "",
        "Ratios use sums at scope, not averages of store ratios. Zero denominators produce missing values. Daily `customers` is informational only: period customer counts are recomputed distinctly. Retention/churn and campaign ROI have their declared company/month or campaign scope.",
        "",
        "[Governance](27-data-governance.md) · [Data model](13-data-dictionary.md)",
    ]
    (BA / "12-kpi-dictionary.md").write_text("\n".join(rows))


if __name__ == "__main__":
    main()
