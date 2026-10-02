# PULSE portfolio case study

**Context.** Wattle & Rye is a fictional Australian food/pantry retailer with 36 stores, three channels and two years of synthetic source records. This is an AI-assisted coding and documentation project. The repository demonstrates implemented analytical mechanics and simulated BA delivery; the candidate should reproduce, inspect and explain them before claiming personal proficiency.

**Business problem.** “Build a better dashboard” concealed late issue detection, incompatible metrics and weak follow-through. I framed the management decision as allocating investigation effort, interpreting financial movement and evaluating a bounded pilot.

**Discovery and stakeholders.** Simulated COO/CFO/Operations/Marketing/Store/Technology statements exposed conflicting brevity, detail, causal inference and service needs. I separated executive attention from analyst evidence, defined one operating ledger, and declined to present observational campaigns as causal lift. The workshop and notes are explicitly fictional.

**Requirements and prioritisation.** Musts protect credibility: reconciliation, owned definitions, material warnings and exact investigation. Forecasting, customer/campaign diagnostics and executive communications are Shoulds; deterministic questions are Could. Production integrations and paid LLMs are outside this release because data availability and risk do not justify them. Traceability ties statements to requirements, stories, criteria, tests and proposed outcomes.

**Analysis.** I chose independent fact grains, SQL aggregation before joins and a central KPI registry. The profit bridge reconciles volume, basket/price/mix and costs. Dimensional SQL ranks associated revenue changes without claiming causal attribution. Weekly median/MAD provides explainable warnings; stockout and campaign estimates expose their comparison assumptions.

**Solution.** Eleven Streamlit views lead from executive performance through warning evidence, store drill-down, conditional scenarios and a proposed decision export. Ask PULSE returns bounded numerical evidence using templates. The Monday brief is generated from current analytical outputs. The full demo has over one million synthetic orders; scale is measured locally, not presented as production capacity.

**Testing.** Known-value fixtures protect financial arithmetic; source corruption checks contract rules and atomic publication; forecasts are tested against holdout leakage; every page renders under AppTest. Executable evidence appears in the final audit. Developer checks do not substitute for real-user acceptance or accessibility certification.

**Insights and recommendations.** Read the generated executive recommendations rather than memorising an invented narrative. Norwood's full-demo warning is a median-reference gap; period bridge contributors can differ because the comparison periods differ. Managers should reconcile roster, demand, basket and campaign context before an intervention. A stockout hypothesis merits a pilot only after checking availability records and substitution assumptions.

**Change considerations and benefits.** Roles move from reporting totals to reviewing exceptions and owning investigations. Training must address definitions, inference and service guardrails. Reporting time, alert assignment, forecast accuracy and adoption are proposed success measures; no achieved savings or adoption is claimed.

**Limitations.** One-SKU synthetic baskets; voluntary feedback; partial identity coverage; simple seasonal models; three-origin interval calibration; rolling baseline drift; no production authentication, integrations, approval workflow or concurrent refresh guarantee.

**Next steps.** Conduct real discovery, source-contract/privacy review and manager UAT; add seasonal/event controls, better forecast calibration, case persistence and authenticated access; test interventions prospectively. In an interview, distinguish what the code demonstrates from what only a real pilot could establish. [Ten model answers](FINAL_AUDIT.md).
