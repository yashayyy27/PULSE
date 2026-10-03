# PULSE experience transformation plan

Recorded before UI implementation, 3 October 2026. Baseline: **38 tests passed in 5.04 seconds**, Python 3.12, existing dependency lock. No analytical failure found.

## Existing architecture and problems

`pulse/data` generates, validates and atomically publishes the synthetic SQLite snapshot; `sql` provides the grain-safe star schema, marts, dimensional contributions and campaign economics. `pulse/metrics/registry.py` owns 19 definitions and derived calculations. `analytics` owns scoped ledgers, exact profit bridges, health and estimated impact. `alerts` owns complete-week median/MAD warnings; `forecasting` owns chronological baseline selection and held-out evaluation. `scenarios` owns the conditional ledger. `query/ask.py` owns bounded deterministic intents. `reports/brief.py` owns calculated company reports and HTML exports. These modules remain authoritative.

The four UI files currently expose eleven sidebar pages. Page-specific selectors and pending navigation keys lose signal/KPI context. Home is a dashboard of metrics, a trend and a queue rather than a next-action experience. Warnings are a dataframe; investigation exposes many results at once. Ask and briefs ignore sidebar context deliberately but that creates an awkward workflow. Scenario comparisons and decision records are session-only. Existing tests include backend reconciliation, source contracts, forecasts, reports and Streamlit AppTest page/interaction checks. UI assertions will be adapted to the new navigation without weakening analytical tests.

## Proposed architecture

Six primary destinations: **Home · Signals · Investigate · Scenario Lab · Ask PULSE · Briefs**. A top product bar replaces the sidebar. Contextual investigation lenses expose customer, operations and forecast capabilities. A secondary System panel exposes source checks, metric definitions and health assumptions. One signal carries its stable ID, store, KPI and exact complete-week dates through investigation, simulation, questions and selected briefing evidence.

Home presents business health, non-overlapping warning exposure, a real twelve-week health timeline, a selected warning and an executive narrative. Signals becomes an actionable feed. Investigation progresses through signal, context, baseline, accounting contributors, exposure, comparison, options, scenario and decision. Disclosure is intentional; evidence is accessible without hover. Scenario inputs operate on the inherited ledger and update live. Ask offers supported contextual questions and explicit scope/method/limits. Briefs allows ordering/removing selected evidence, considered scenarios and proposed decisions, with real HTML/JSON downloads. A guided case uses actual results and reversible Next/Back/Exit navigation.

## Design system

Central CSS tokens and presentation components: obsidian `#090A0B`, carbon `#111315`, graphite `#1A1D1F`, elevated `#222629`, silver `#C7CDD1`, muted silver `#8C969D`, off-white `#F4F7F8`, turquoise `#00A19C` / interactive `#00D2BE`. Restrained critical/warning statuses also have text labels. Tabular figures, compact uppercase system labels, clear sentence headings, editorial spacing, small radii and minimal borders. No team branding or racing graphics. Charts use dark surfaces, silver history and turquoise focus, restrained grids and explicit units/reference lines. Reusable headers, metrics, signal summaries, badges, breadcrumbs, narratives, evidence, comparisons, explainability, action groups and recovery states.

## State and interactions

A pure state module manages context construction, selection, navigation, signal acknowledgment, brief membership/order, scenarios and resets. Native Streamlit callbacks and keyed widgets handle state changes; no injected parent-window scripts or simulated links. Cached adapters are keyed by resolved database path, modification time and size, plus analytical scope. Selection IDs prevent stale chart events from repeatedly overriding context. Resets clear contextual widget assumptions/results but preserve intentionally saved briefing evidence and proposals. Brief items retain their original period and scope. Empty filters and unsupported questions have explicit recovery. Scenario reset restores the exact baseline, not rounded rate replacements.

Ask passes explicit context to a presentation adapter that uses the existing ledger/contribution/warning/campaign engines; the public analytical intent engine remains unchanged. Contextual questions use only supported intents. Methodology states when campaign or retention results have company scope. No fake natural-language scenario answering, keyboard shortcuts or exports.

## Responsive and accessible approach

Desktop/laptop is primary. Native controls retain labels, keyboard focus and semantics. The top navigation wraps; columns collapse on narrow screens; cards do not have fixed widths; charts resize. CSS has visible focus, readable text, sufficient contrast and reduced-motion handling. Status includes words; timeline selection also has a labelled native selector. No mandatory hover-only evidence. The product header persists across reruns; a sticky header will be used only if it remains reliable in native Streamlit layout. Avoid unsupported DOM mutation.

## Sequence and regression controls

1. Record baseline and source hashes; inspect RESTOPS without edits.
2. Build state, cached analytical adapters and design components.
3. Replace shell/navigation; implement Home/Pulse and Signals.
4. Implement progressive investigation/comparison/explainability and context transfer.
5. Implement simulator, contextual Ask, briefing workspace and guided case.
6. Adapt/add meaningful state and AppTest journey tests; retain all analytical tests.
7. Run browser interaction/visual checks at desktop, laptop and narrow widths; fix failures and capture five current screenshots.
8. Update README/demos/architecture and differentiation; document full interaction and five-perspective audits.
9. Run tests, Ruff, local links, full-source/engine verification and startup; publish reviewed changes to the existing GitHub repository.

Risks: widget state mutations after instantiation, stale cached snapshots, chart event replay, expensive company customer scans, historical baselines mistaken for forecasts, overlapping exposure sums, briefing context leakage, narrow navigation, and unsupported shortcuts. Tests target these boundaries. Preserve an original-source hash manifest for all `pulse`, SQL and settings files, so accidental analytical changes are visible. Adapt the final verification script to the six destinations and secondary evidence areas.

## Verification strategy

Keep the analytical suite unchanged. Add pure state/filter/brief/context tests plus AppTest journeys for exact signal-to-investigation-to-scenario-to-question-to-brief propagation, nine assumptions, comparison lenses, proposals, reset, empty filters, validation and tour navigation. Use browser checks for Plotly click/hover, keyboard focus, real downloads, disclosure and responsive composition, which AppTest cannot fully validate. Audit every rendered control by family and record expected/result/state/context/pass. A passing startup is only the first check. Record limitations honestly in the final report, including session persistence, snapshot scope and Streamlit-native constraints.
