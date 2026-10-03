# PULSE interaction audit

Executed 3 October 2026, Australia/Sydney. This is developer verification of a synthetic local prototype, not stakeholder acceptance or accessibility certification.

## Evidence and coverage

- Baseline before implementation: **38 tests passed**. Final suite: **74 passed in 13.84 seconds**. Original analytical tests remain unchanged.
- [App journeys](../tests/test_app.py) exercise all six destinations, every supported scenario lever, all comparisons, all decision paths, three contextual lenses, all 19 metric explanations, session records, guided steps and recovery states. [State tests](../tests/test_ui_state.py) cover boundaries, frozen evidence, resets and exports.
- Native browser checks exercised Pulse marker selection, signal filtering/acknowledgement/brief selection, baseline and contribution disclosures, keyboard navigation and sliders, contextual questions, the entire guided case with Back/Exit, and actual HTML/JSON downloads. Downloaded files were parsed and their selected Norwood evidence inspected.
- [Browser evidence](../reports/ui_browser_audit.json) records measured viewport dimensions and the guided case context. [Screenshots](../README.md#actual-product-screens) show the running app, not design mockups.
- Automated assertions validate state and analytical results; browser checks validate representative rendered controls. Repeated instances share the same tested handlers. A PASS does not imply every row was manually clicked in every possible dataset.

## Global controls and Home

| Control | Expected behaviour | Actual behaviour / evidence | State change | Context preservation | Result |
|---|---|---|---|---|---|
| Home, Signals, Investigate, Scenario Lab, Ask PULSE, Briefs | Open named destination and indicate selection | Six AppTest cases and browser navigation render actual destinations | `nav` | Retained on ordinary navigation | PASS |
| Source checks popover | Open secondary system evidence | Quality, registry and health areas render through the system panel | Disclosure / `system_area` | Retained | PASS |
| Reset context | Return to company/latest complete week; exit tour | Boundary and UI assertions check scope, cleared assumptions and retained saved records | `context`, selected signal, demo, derived inputs | Explicit reset; saved evidence retains original scope | PASS |
| 90-second guided demo | Select computed warning and start real case | Norwood operating-profit warning selected; nine real stages completed | `demo_signal`, `demo_step`, `nav`, context | Exact store/KPI/week throughout | PASS |
| Pulse latest-warning markers | Select exact warning and highlight it | Browser Newcastle marker selected Newcastle/gross profit and transferred into investigation | selected signal, selector, context | Exact ID, period and KPI | PASS |
| Pulse hover | Explain health or warning point | Actual health/profit/revenue and warning scope/deviation/exposure supplied in hover data | Transient hover | No scope mutation | PASS |
| Select a business signal | Keyboard alternative to marker selection | Real warnings populate selector; callback resolves stable signal ID | selector / selected signal | Exact chosen warning | PASS |
| Investigate signal →; Investigate named location | Open chosen warning | Navigation assertions verify selected row, location, dates and KPI | `nav`, context | Exact chosen warning | PASS |
| Explore company evidence (no warnings) | Offer useful empty-state route | Empty-warning test renders truthful message and opens company evidence | `nav` | Company scope; no fabricated signal | PASS |
| Understand health index | Reveal scores, weights and targets | Governed health output rendered with limitations | Disclosure | Retained | PASS |
| Explain metric / Metric definition | Reveal registry definition, formula, source, grain, owners, refresh and limits | All 19 registry entries checked against displayed authoritative fields | metric selector / disclosure | Retained; no analytical mutation | PASS |

## Signal feed

| Control | Expected behaviour | Actual behaviour / evidence | State change | Context preservation | Result |
|---|---|---|---|---|---|
| Filter signals | Reveal compact controls | Native popover opens labelled selectors | Disclosure | Retained | PASS |
| Severity, Business domain, Location, KPI, Session status | Filter actual rows conjunctively | Pure state tests plus UI empty/acknowledged filter tests; browser Critical filter yields Norwood | `signal_filters` and widget keys | Does not overwrite investigation context | PASS |
| Reset filters; empty-state Reset filters | Restore all rows | UI test changes retention filter to empty and recovers | All filter fields → All; page → 1 | Retained | PASS |
| Feed page | Page bounded five-item feed | Rendered only for multiple pages; bounded integer controls actual slice | `signal_feed_page` | Retained | PASS |
| Investigate signal | Open row's investigation | Shared selected-row handler exercised | `nav`, context | Exact row | PASS |
| Signal actions | Reveal secondary actions | Browser popover exposes real operations | Disclosure | Retained | PASS |
| Acknowledge | Mark current-session status; retain evidence | Browser feedback and Acknowledged label verified; repeat action disabled | `signal_status[id]` | Row unchanged | PASS |
| Add to brief | Save exact frozen warning once | Browser and state tests verify record and duplicate prevention | `brief_items` | Original store/KPI/week frozen | PASS |
| Compare with baseline | Open exact signal and comparison | UI assertion checks `8-week baseline` | context, comparison, nav | Exact row | PASS |
| Ask about this signal | Open contextual question | Shared route resolves warning context and actual evidence | context, question, nav | Exact row | PASS |
| Why was this triggered? | Reveal rule/reference evidence | Median/MAD, thresholds and sample explanation shown | Disclosure | Retained | PASS |

Time is visibly fixed to the engine's **latest complete warning week**. A redundant one-option time filter was removed. Historic health points do not masquerade as retrospectively recomputed warnings.

## Investigation and secondary evidence

| Control | Expected behaviour | Actual behaviour / evidence | State change | Context preservation | Result |
|---|---|---|---|---|---|
| PULSE / Company breadcrumb | Return to company observed ledger | Scope test checks company context | context / selected signal cleared | Deliberate scope change | PASS |
| State comparison breadcrumb | Open current-state benchmark | Comparison changes to State | comparison / disclosure | Selected store retained | PASS |
| Change investigation scope | Reveal scope controls | Native expander exposes state/location/period | Disclosure | Retained until chosen | PASS |
| Filter locations by state | Narrow offered stores | Options derive from actual location dimension; current selection stays available | `scope_state` | Filter alone retains active scope | PASS |
| Investigation location | Recompute selected scope | Company/location UI test and source-scoped adapters | context / derived inputs | Explicit location change; frozen records retained | PASS |
| Observed period | Select latest week or latest full month | Scope and Ask follow-up tests check exact effective dates | context / derived inputs | Explicit period change | PASS |
| Why is this signal here? | Reveal actual vs eight-week reference | Browser and tour display actual chart/evidence | Disclosure | Retained | PASS |
| Show contributors | Reveal reconciled bridge and dimensional evidence | Browser, tour and all ten-dimensional reconciliation checks | Disclosure | Retained | PASS |
| Business driver | Change dimensional revenue evidence | All ten dimensions reconcile; real grouped rows shown | `contribution_dimension` | Retained | PASS |
| Compare locations, periods or baseline | Reveal focused comparison | Native disclosure and comparison test family | Disclosure | Retained | PASS |
| Compare against: Previous period, Company, State, 8-week baseline | Select meaningful benchmark | All four modes render without errors and preserve context | `comparison`, shadow mode | Retained; aggregate references labelled | PASS |
| Investigation path: labour, discounting, product mix, availability | Evaluate chosen analytical path | All four choices tested; service caveat, campaign evidence, dimensional or stockout evidence shown | `decision_path` | Retained | PASS |
| Model this scenario | Carry hours sensitivity into simulator | Conditional hours assumption and existing scenario engine used | scenario inputs / nav | Retained | PASS |
| Stock substitution assumption | Recompute conditional availability estimate | Independent widget keys for path and Operations lens; zero-opportunity boundary test | Substitution input | Retained | PASS |
| Review customer, operations or forecast evidence | Reveal optional lenses | All three lens cases tested, lazy evaluation avoids unrelated work | `secondary_evidence`, `evidence_lens` | Labels disclose company-wide metrics | PASS |
| Customer cohort/retention disclosure | Reveal supporting customer history | Existing cohort and retention outputs rendered | Disclosure | Declared company scope | PASS |
| Forecast metric: Revenue, Transactions, Gross Profit, Labour Hours | Recompute supported forecast | Existing four-metric validation/holdout evidence verified | metric selector | Location retained; final-data origin disclosed | PASS |
| Inspect forecast backtests / forecast CSV | Reveal/export actual forecast rows | Nonempty existing engine outputs and real download payload | Disclosure / download | Labelled origin and scope | PASS |
| Open Scenario Lab | Open current-ledger simulator | End-to-end context assertion | nav | Retained | PASS |
| Ask PULSE with this context | Open contextual deterministic questions | Supported evidence and effective-period tests | nav / question | Retained unless explicit effective period differs | PASS |
| Add evidence to brief; Open brief workspace | Save warning or open curated workspace | Idempotent selected evidence and functional continuation | brief / nav | Frozen evidence retained | PASS |
| Proposed owner, next investigation, guardrails; Record proposal | Validate and retain unapproved proposal | Empty fields rejected; valid form stores explicit Proposed status | `decisions` | Full context frozen | PASS |
| Export decision log | Download actual session proposals | JSON download contains saved proposal data | Download only | Frozen scope retained | PASS |

## Scenario Lab, questions and briefs

| Control | Expected behaviour | Actual behaviour / evidence | State change | Context preservation | Result |
|---|---|---|---|---|---|
| Average price, Transactions/demand, Basket quantity/AOV, Labour hours, Loaded hourly labour cost sliders | Independently recompute conditional ledger | Parameterised tests check each; browser keyboard −3% hours gives Norwood approximately **+A$85** profit | Widget values + permanent `scenario_inputs` | Same scope and observed base | PASS |
| Retention response; Additional promotion uptake | Recompute supported assumptions | Each parameter independently tested | scenario inputs | Same scope; proxy/discount method disclosed | PASS |
| Retention, promotion and product economics disclosure | Reveal further legitimate controls | Native expander, tested rendered controls | Disclosure | Retained | PASS |
| Replace discount rate + replacement rate; Replace product margin + replacement margin | Enable deliberate overrides | Both overrides tested; inactive sliders disabled | enable flag / rate | Same scope | PASS |
| Reset assumptions | Reproduce base case exactly | Independent rate reset and identity tests prevent rounded baseline replacement | All assumptions reset; derived result cleared | Scope retained | PASS |
| Inspect model assumptions | Reveal method and limitations | Existing model assumption statement displayed | Disclosure | Retained | PASS |
| Scenario comparison label; Save scenario to brief & comparison | Validate label and freeze considered case | Empty label rejected; full base/result/assumptions/context stored | `scenarios` | Frozen exact scope | PASS |
| Saved case selector (multiple cases only) | Choose comparison/removal target | Functional selected-index comparison; single-case decorative selector removed | selection | Frozen scopes labelled | PASS |
| Remove saved scenario; Export scenario comparison | Remove chosen case / export actual saved records | Removal test and JSON payload checks | scenarios / download | Remaining records unchanged | PASS |
| Continue to executive brief → | Open retained workspace | Native navigation callback | nav | Retained | PASS |
| Ask question field; Analyse question | Run supported deterministic intent | Real Norwood bridge, scope, period and limits shown; unsupported SQL rejected | question / result | Store-bound; explicit last-month period visible | PASS |
| All contextual suggestion buttons and product follow-up | Run displayed analytical question | Suggestion and follow-up tests verify numerical evidence; browser profit suggestion used | question / result | Same declared scope; company intents labelled | PASS |
| Explain the method and limits; Export answer evidence | Reveal method / export evidence rows | Existing method/limits and real CSV payload | Disclosure / download | Answer scope retained | PASS |
| Review investigation evidence; Model a labour-hour sensitivity | Carry actual answer scope into next workflow | Effective-month follow-up test checks dates, store and cleared stale warning | context / nav / assumptions | Effective result scope, not old week | PASS |
| Include current priority findings | Populate curated brief from actual priorities | Idempotent frozen priority rows added | brief items | Each row retains scope | PASS |
| Move up; Move down | Reorder findings | Boundary tests; end buttons disabled; reordering changes exported order | brief list order | Records unchanged | PASS |
| Remove finding | Remove selected record | UI and pure-state checks | brief list | Remaining records unchanged | PASS |
| Consider a scenario; Document next investigation | Open corresponding current-context workflow | Native routes use shared state | nav | Current context retained; saved records frozen | PASS |
| Export HTML executive brief; Export briefing evidence JSON | Download authentic curated evidence | Both actual browser downloads parsed; selected Norwood, scenario, proposal and limits present | Download only | Original scopes and precision retained | PASS |

## Guided controls, recovery and accessibility

| Control | Expected behaviour | Actual behaviour / evidence | State change | Context preservation | Result |
|---|---|---|---|---|---|
| Demo Next | Advance through actual analytical case | All nine stages exercised in AppTest and native browser | step, nav; selected evidence/scenario/proposal added at appropriate stages | Norwood / operating profit / 22–28 Dec 2025 | PASS |
| Demo Back | Revisit previous stage | Browser returned final decision to brief stage; automated boundary test | step / nav | Retained | PASS |
| Demo Exit | Exit from any stage; keep useful records | Browser final-stage exit; AppTest checks demo state cleared | demo step → None | Scope and saved records retained | PASS |
| Retry snapshot; Recheck source validation | Recover after missing or failed source is repaired | Missing DB and injected failed-check/repaired-check tests | rerun / fresh fingerprint | Safe initialisation | PASS |
| Retry analysis; Technical details | Recover from failed calculation; separate diagnostics | Safe catch retains scope and offers rerun; corrupt/missing snapshot coverage | rerun / disclosure | Existing context retained | PASS (code/recovery coverage) |
| System area / data-quality and registry tables | Choose evidence area | All real source checks/metadata and definitions displayed | `system_area` | Retained | PASS |
| Financial, Customer, Operations, Inventory weight inputs | Explore health weighting transparently | Positive weights normalise; all-zero input shows validation error | Weight inputs only | Home governed index unchanged | PASS |
| Restore health weights | Recover invalid weighting | Zero-weight UI test recovers defaults | Weights reset | Retained | PASS |
| Native radio keyboard navigation and slider arrows | Operate without pointer | Native Right arrow opens Signals; −3 slider steps update scenario | nav / input | Retained | PASS |
| Native expanders, popovers and labelled inputs | Keyboard focus and disclosure | Native controls retained; CSS focus outlines; radio inputs kept accessible with opacity rather than display:none | Focus/disclosure | Retained | PASS (developer check) |
| Chart markers versus keyboard selector | Avoid hover-only essential workflow | Equivalent labelled selector and primary action available | selected signal | Exact row | PASS |
| Table sort, column visibility, search/Next/Previous/Close, Fullscreen/Close | Change evidence presentation | Browser checked sorting, hide/restore Impact, five search matches and result navigation, fullscreen and close | Grid presentation | No analytical context mutation | PASS |
| Dedicated evidence exports | Download actual analytical rows | Answer CSV downloaded and parsed; forecast/scenario/proposal/brief use explicit exports. Native client-side grid CSV did not download reliably in the embedded browser and was removed | Download | Scope retained | PASS (replacement verified) |
| Heading anchor links / README links | Navigate actual anchors/files | Native anchors and repository Markdown checks | Navigation only | No state mutation | PASS |

No shortcut is advertised: a reliable native Ask destination was implemented instead of an unsupported command-key overlay. No placeholder, fake export or externally generated AI response is present.

## Visual, responsive and regression fixes

All six destinations were checked at requested **1920×1080, 1366×900 and 600×900**. The embedded browser reported approximately **1959×1102, 1394×918 and 612×918 CSS pixels**, respectively. Document width did not exceed viewport width. Narrow layouts stack meaningful columns, keep all six navigation choices, and keep reset/demo actions accessible. Wide analytical tables scroll internally; the page does not overflow horizontally. This is a desktop/laptop product with narrow-browser recovery, not a mobile-first certification.

Fixed during verification: duplicate baseline chart IDs; unsupported nested disclosures; disappearing scenario/filter/question inputs after Streamlit widget cleanup; stale effective-month Ask follow-up; guided signal/selector mismatch; default Plotly undefined title; hidden radio keyboard failure; narrow header wrapping; raw numeric decimals; duplicate Home signal; negative AUD placement; false empty-brief text; redundant one-page/time/saved-case controls; unreliable embedded-browser grid CSV (replaced by explicit evidence exports); and screenshot capture before Streamlit rerender settled. Final screenshots were recaptured from settled pages.

See [final report](UI_UX_FINAL_REPORT.md) for five-perspective review, limitations and performance measurements. Engine source/SQL/config hashes match [the recorded baseline](../reports/ui_backend_baseline.json).
