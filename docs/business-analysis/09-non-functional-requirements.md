> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Non-functional requirements

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
