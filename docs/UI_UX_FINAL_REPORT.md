# PULSE UX transformation — final report

Developer review: 3 October 2026, Australia/Sydney. All business data, roles and proposed decisions are synthetic. This report records executed local checks; it does not claim real stakeholder acceptance, achieved benefits or production deployment.

## What changed

PULSE now guides a decision rather than asking a user to assemble one from disconnected dashboard pages. Home identifies business health, commercial reference exposure and the next signal. A selected warning carries its exact store, KPI and complete-week dates through evidence, comparisons, conditional simulation, questions and executive communication.

The former four-file UI was reorganised into a six-destination shell, shared state transitions, cached adapters, central components/design tokens, contextual analytical lenses, a curated brief adapter and a nine-stage guided case. Existing analytical engines were reused. Obsolete primary navigation and old dashboard screenshots were removed.

| Before | After |
|---|---|
| Eleven sidebar pages organised by analytical capability | Home · Signals · Investigate · Scenario Lab · Ask PULSE · Briefs |
| Headline metrics, trends and dataframe warnings | A morning narrative, governed health, non-overlapping exposure and actionable Pulse markers |
| Page-specific scope controls and disconnected workflows | Visible shared context; functional company/state drill-down; deliberate resets |
| Many unrelated investigation charts | Nine-stage story with baseline, contributors and comparison disclosures |
| Questions and reports largely company-wide | Context-aware deterministic questions and selected, ordered briefing evidence |
| Simulator as a separate page | Live base/scenario/delta with retained inputs, saved cases and service trade-offs |
| Customer/operations/forecast/system as separate destinations | Contextual lenses and secondary source/metric/health panel |

## Design and interaction philosophy

The central [design system](../app/design.css) uses obsidian `#090A0B`, carbon `#111315`, graphite `#1A1D1F`, elevated graphite `#222629`, silver `#C7CDD1`, off-white `#F4F7F8` and restrained turquoise `#00A19C`/`#00D2BE`. Critical/watch status is additionally expressed in words. There are no automotive logos, team graphics, race cars or affiliation claims.

Small system labels lead to business statements, clean tabular financial values, evidence and one principal action. Open composition and section rules replace pervasive bordered KPI cards. Native input labels and keyboard behaviour are retained. Plotly uses transparent surfaces, restrained grids, explicit reference lines, concise hover and no decorative toolbar. Motion is limited to state/focus/selection and respects reduced-motion preferences.

The Pulse combines actual twelve-week health with three priority latest-window markers. A marker or the equivalent labelled selector chooses a real warning; the primary action opens that exact investigation. Older health weeks are observed history, not backfilled anomaly detections.

## Verified journeys

1. **Warning → evidence:** select Norwood operating profit for 22–28 December 2025; review the prior-eight-week reference and the distinct previous-week accounting bridge; choose company, state, previous-period or historical comparison.
2. **Evidence → scenario:** retain location/period/base ledger; test independently supported assumptions. A −3% hours change with other assumptions unchanged gives approximately **+A$85** modelled operating profit. It remains a conditional scenario, not a forecast or achieved saving.
3. **Evidence → question → follow-up:** deterministic questions expose actual rows, method, scope and limitations. Explicit “last month” changes the answer window; follow-up uses the effective result period rather than silently restoring the old week. Cross-store questions in an active store context ask the user to change scope explicitly.
4. **Evidence → brief:** add frozen findings once; order/remove them; include considered cases and unapproved proposals; export authentic HTML/JSON. Company exposure and selected finding exposure are separate to prevent overlapping estimates being added.
5. **Guided case:** nine Next/Back/Exit stages use actual Norwood results, a −3% hours/−1% demand sensitivity, a saved considered case and a fictional unapproved proposal with service/demand guardrails. Browser execution verified the exact context through the case and preserved records after exit.

The full demo's current Home values are **57/100 health**, **17 warnings** across **10 represented stores**, and **A$1,890 estimated weekly operating-profit reference exposure**. Norwood's selected profit-reference gap is approximately **A$774**. These figures come from the engine, not the illustrative values in the design request.

## State and integrity

[Shared state](../app/state.py) owns navigation, validated context, selected signal, session status, frozen findings/cases/proposals, comparisons and demo progress. Stable signal IDs use location, KPI and timestamp. Context changes clear incompatible question/scenario derivatives while preserving previously saved evidence. Reset context deliberately returns to the latest company week and exits the tour; reset assumptions reproduces the observed ledger exactly without replacing baseline rates with rounded controls.

Control callbacks update an authoritative permanent input record before rerender; returning restores it even when a dormant widget default remains. Permanent shadow values protect scenario inputs, filters and question text from Streamlit's cleanup of widgets when changing destinations. Tests exercise return navigation and saved evidence boundaries. Brief exports escape user-authored text, retain numerical precision and distinguish full-company versus selected exposure.

No analytical defect required changing the backend. SHA-256 tests verify **every recorded file under `pulse/`, SQL and analytical settings remains byte-identical** to [the pre-edit manifest](../reports/ui_backend_baseline.json). Original analytical tests remain unchanged. Presentation-only AUD formatting was corrected in the UI without altering answer calculations.

## Accessibility and responsive work

Native controls provide labels and keyboard operations. Visible focus outlines were added; navigation inputs remain in the accessibility tree. Browser Right-arrow navigation and scenario slider arrows were exercised. Important charts have supporting text and a keyboard selection alternative. Status and estimates are expressed in words; essential decisions do not rely on colour or hover alone. Reduced-motion styles are provided.

All six destinations were checked at requested large desktop **1920×1080**, laptop **1366×900** and narrow **600×900** settings. Actual embedded-browser CSS dimensions are recorded in the [browser audit](../reports/ui_browser_audit.json), since browser scaling reports slightly different sizes. No document-level horizontal overflow was measured. Narrow columns stack, header navigation takes a separate row, and controls remain reachable. Native data grids may scroll inside their own region. The native grid client-side CSV action did not download in the embedded browser and was removed; explicit server-backed evidence exports are used. Table column visibility, search/result navigation and fullscreen controls were exercised in the browser.

These are developer accessibility checks. No external WCAG audit, screen-reader study or real manager usability session is claimed.

## Performance and execution results

Cached adapters key results by resolved database path, file size and modification time, then scope/period. Snapshot changes invalidate cached data. Customer/operations/forecast lenses compute when requested rather than on every primary destination. Scenario arithmetic recomputes live from a cached observed ledger. Home limits expensive explanatory investigations to its priority locations.

The final [full-data verification](../reports/full_verification.json) processed **1,060,291 orders**, reconciled **37 scopes** and **10 dimensions**, and rendered all six destinations in **3.952 seconds** locally. Warning detection took **0.060 seconds**. AppTest render measurements were Home **0.621s**, Signals **0.024s**, Investigate **0.078s**, Scenario Lab **0.034s**, Ask PULSE **0.013s**, Briefs **0.317s**. These are local Python/render measurements with shared caches, not browser latency, cold-start guarantees or an SLA.

| Check | Executed result |
|---|---|
| Before-edit regression baseline | 38 passed |
| Final analytical, state and application suite | **74 passed**, zero failures, 13.84s |
| Source totals / profit bridges / zero-change identity | PASS at company and all 36 stores |
| Ten-dimensional contribution reconciliation | PASS |
| Raw generated-source hashes | PASS |
| Analytical source preservation | PASS, recorded hashes unchanged |
| Ruff lint and formatting | PASS |
| Repository Markdown links and fences | PASS; [check artifact](../reports/documentation_checks.json) |
| Local Streamlit startup and all primary journeys | PASS |
| Browser console errors at final review | None captured |
| HTML and JSON brief downloads | Downloaded, parsed, selected evidence inspected |
| All primary destinations at three requested widths | No document horizontal overflow |

The [control-by-control audit](UI_UX_INTERACTION_AUDIT.md) distinguishes automated assertions, native browser execution and library controls. Failures found during development were fixed: duplicate chart IDs, nested disclosures, widget cleanup, effective question-period transfer, guided selector mismatch, keyboard radio styling, header wrapping, number formatting, duplicate content and premature screenshot captures.

## Five-perspective review and fixes

| Perspective | Weakness found | Implemented fix |
|---|---|---|
| Recruiter | Feature list concealed the business journey; action sat below the first screen | Six destinations, real Home priority, action beside selector, nine-stage optional guided case |
| BA hiring manager | Recommendations could be mistaken for approved decisions | Explicit contribution/reference methods, owner/action/guardrail form, fictional Proposed status, evidence retained in brief |
| Data/BI hiring manager | Median warning baseline and previous-week bridge could be confused; month answers lost scope | Distinct labels and disclosures, all registry definitions, actual effective-period follow-up, source-hash regression guard |
| Executive | Repeated signal and overlapping exposure made priorities harder to read | Selected focus is excluded from other attention items; profit exposure counted once per location; selected brief total separated from company total |
| Product designer | Default chart title, scattered surfaces, dead one-option controls and narrow header weakened coherence | Central design tokens, transparent charts, open metrics, radio focus fix, removed redundant selectors, responsive navigation row and settled screenshot recapture |

RESTOPS was inspected read-only and preserved. [Differentiation evidence](RESTOPS_DIFFERENTIATION.md) explains PULSE's top navigation, silver/turquoise identity, signal-led story, contextual questions, live simulator and curated brief versus RESTOPS's restaurant/month/action-tracker interface.

## Limits and future production work

Streamlit reruns are native and bounded, rather than a client-only SPA. The header is consistent across destinations, but is not a sticky overlay while scrolling. Ask uses a focused native panel; there is no advertised command shortcut or fragile modal. Snapshot failures expose a recovery action and technical detail separately. Session records require export to survive closing the browser; no durable case database, approvals, RBAC or real integration was introduced.

Latest-warning time is fixed to the current engine window. Campaign and retention evidence use their declared company-wide grain. Forecasts use the dataset's final origin; weak observed band coverage remains visible. Health targets are assumed, contributions are associations, stockout exposure is conditional, and scenarios do not model service elasticity or staffing feasibility. HTML is supported; a dedicated PDF export is deferred.

Production improvements would require actual role-based discovery/UAT, durable versioned case storage, authenticated permissions, real source contracts, refresh locking/audit logs, prospective warning evaluation and better calibrated forecast intervals. The local synthetic application and public source are the deliverables; a hosted production application is not claimed.

[Transformation plan](UI_UX_TRANSFORMATION_PLAN.md) · [Interaction audit](UI_UX_INTERACTION_AUDIT.md) · [README and screenshots](../README.md) · [Full audit](FINAL_AUDIT.md)
