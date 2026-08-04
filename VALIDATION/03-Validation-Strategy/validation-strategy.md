# Research-OS — Validation Cycle 01 — Validation Strategy

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev (FROZEN)
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `VALIDATION/03-Validation-Strategy/validation-strategy.md`
**Validation Cycle:** 01
**Validator:** Research-OS Validation Builder
**Related:** `VALIDATION/01-Validation-Plan/validation-plan.md`; `VALIDATION/02-Validation-Checklist/validation-checklist.md`; `VALIDATION/04-Validation-Report/REPORT-VALIDATION-01.md`; `quality-gate-standard.md` §5 (analogous Gate Evaluation Model); Foundation Freeze State (per Architect Authorization, 2026-08-03)

---

## §1. Purpose

This Validation Strategy declares the approach, success thresholds, evidence sources, and risk scoring rubric the Validation Builder applies during the trace-through reading and cross-reference graph verification.

The Strategy is the **rubric**; the Plan is the **scope**; the Checklist is the **questions**; the Report is the **answers**.

---

## §2. Validation Approach

The Validation Cycle uses **four read-only methods** applied in this order:

### §2.1 Method 1 — Trace-Through Reading

**Approach:** The Validator reads each Foundation artifact end-to-end and records observations per the eight categories (per `validation-plan.md` §3). The reading is annotated with structural markers (section presence, section completeness, declaration vs. normative clauses, deferred-ratification clauses).

**Time budget:** The Validator allocates proportional time per artifact based on artifact size and category count. Larger artifacts (Constitution, Runtime Specification, Release Specification) receive more time; smaller artifacts (Policies) receive less.

**Output:** Per-artifact structured observations recorded in `REPORT-VALIDATION-01.md` §3 (Per-Artifact Matrix).

### §2.2 Method 2 — Cross-Reference Graph Verification

**Approach:** The Validator builds a cross-reference graph in-memory (Constitution ↔ Standards ↔ Policies ↔ artifacts) and verifies that every cross-reference resolves. Unresolved references are recorded as **Open Issues** in the Report.

**Time budget:** The Validator allocates proportional time per artifact based on the artifact's cross-reference count. Higher cross-reference counts (Release Specification with 33 references) receive more time.

**Output:** Cross-reference resolution table recorded in `REPORT-VALIDATION-01.md` §5 (Cross-Cutting Observations).

### §2.3 Method 3 — Objective Coverage Check

**Approach:** For each of the seven objectives (per `validation-plan.md` §2), the Validator identifies the Foundation artifacts that govern the objective and verifies that the objective is traceably coverable by the Foundation's normative clauses. The trace is recorded in the Report.

**Time budget:** The Validator allocates equal time per objective (5 sub-checks per objective × 7 objectives = 35 sub-checks).

**Output:** Per-objective trace recorded in `REPORT-VALIDATION-01.md` §4 (Per-Objective Matrix).

### §2.4 Method 4 — Risk and Simplification Pass

**Approach:** For each artifact, the Validator identifies (a) over-engineering risks and (b) simplification opportunities. The pass is non-binding — no simplification is enacted; recommendations are recorded for the Architect.

**Time budget:** The Validator allocates proportional time per artifact based on the artifact's perceived complexity.

**Output:** Risk register and Simplification register recorded in `REPORT-VALIDATION-01.md` §6 (Risk Register) and §7 (Simplification Register).

---

## §3. Success Thresholds

The Validation Cycle is **Successful** if:

| Criterion | Threshold |
|---|---|
| Coverage | All 168 checks answered (128 per-artifact + 35 per-objective + 5 cross-cutting) |
| Traceability | Every objective evaluation cites ≥ 1 Foundation artifact |
| Risk register completeness | All over-engineering risks recorded with severity |
| Simplification register completeness | All simplification opportunities recorded with priority |
| Foundation Readiness Score | A single integer (0–100) computed |
| Remaining Risks | A list of residual risks recorded |
| Recommended Next Phase | A recommendation recorded |

The Validation Cycle is **Blocked** if any of:

- The Foundation tree cannot be read (permission denied, file missing).
- The Cross-Reference Graph has unresolved references that prevent traceability.
- The Architect revokes the Validation Builder's read-only authority.

---

## §4. Evidence Sources

The Validation Cycle draws evidence from Foundation artifacts only (per `validation-plan.md` §5). No evidence is drawn from external sources. No live API calls. No network endpoints. No web search.

The Validator does NOT:

- Read files outside the Foundation tree (with the exception of `VALIDATION/` for prior validation documents).
- Invoke external tools beyond Read / Grep / Glob (no Bash execution).
- Generate new files in the Foundation tree.
- Generate new files in the `VALIDATION/` tree beyond the 6 declared deliverables.

---

## §5. Risk Scoring Rubric

Over-engineering risks are scored on a 4-point severity scale:

| Severity | Definition |
|---|---|
| **Critical** | The artifact has structural over-engineering that prevents downstream execution; Foundation amendment is required to remediate. |
| **High** | The artifact has significant over-engineering that imposes unreasonable burden on downstream consumers; a future Simplification Cycle is recommended. |
| **Medium** | The artifact has moderate over-engineering that is addressable via clarification or reduced scope; addressable in a future Maintenance Cycle. |
| **Low** | The artifact has minor over-engineering that is cosmetic or stylistic; addressable in a future Polish Cycle. |

The Risk Register in `REPORT-VALIDATION-01.md` §6 records every risk with its severity, artifact, and rationale.

---

## §6. Simplification Scoring Rubric

Simplification opportunities are scored on a 4-point priority scale:

| Priority | Definition |
|---|---|
| **High** | The simplification is materially valuable and should be enacted in the next Foundation cycle. |
| **Medium** | The simplification is valuable and should be considered in a future Maintenance Cycle. |
| **Low** | The simplification is cosmetic or stylistic; addressable in a future Polish Cycle. |
| **None** | The artifact is at the right level of detail; no simplification needed. |

The Simplification Register in `REPORT-VALIDATION-01.md` §7 records every opportunity with its priority, artifact, and rationale.

---

## §7. Foundation Readiness Score

The Foundation Readiness Score is computed as follows:

1. For each artifact, compute the **artifact score** as the mean of the eight category scores (per `validation-plan.md` §3), where each category score is on the 4-point scale (0–4).
2. The Foundation overall score is the mean of all artifact scores (16 artifacts).
3. The Foundation Readiness Score is the Foundation overall score × 25 (to yield a 0–100 scale).

**Score interpretation:**

| Range | Interpretation |
|---|---|
| 90–100 | **Excellent** — Foundation is ready for the next phase; minor observations only. |
| 75–89 | **Good** — Foundation is ready for the next phase; some observations to address. |
| 60–74 | **Sufficient** — Foundation is ready for the next phase with caveats; observations must be addressed. |
| 40–59 | **Marginal** — Foundation is not ready for the next phase; significant amendment required. |
| 0–39 | **Insufficient** — Foundation is not ready; structural amendment required. |

The Foundation Readiness Score is recorded in `REPORT-VALIDATION-01.md` §8.

---

## §8. Remaining Risks Register

The Remaining Risks Register records risks that are NOT fully resolved by the Foundation as drafted. Each risk is scored on:

- **Likelihood** — Low / Medium / High.
- **Impact** — Low / Medium / High / Critical.
- **Risk score** — Likelihood × Impact (Low=1, Medium=2, High=3, Critical=4).
- **Owner** — the role responsible for addressing the risk.
- **Mitigation** — a brief description of how the risk could be addressed.

The Remaining Risks Register is recorded in `REPORT-VALIDATION-01.md` §9.

---

## §9. Recommended Next Phase

The Validator records a single recommendation for the next phase, drawn from the following options:

| Recommendation | When Selected |
|---|---|
| **Ratification Cycle** | Foundation Readiness Score ≥ 75 AND no Critical Remaining Risks. |
| **Maintenance Cycle** | Foundation Readiness Score 60–74 AND no Critical Remaining Risks. |
| **Simplification Cycle** | Foundation Readiness Score ≥ 60 AND ≥ 3 High-priority Simplification Opportunities. |
| **Foundation Amendment Required** | Foundation Readiness Score < 60 OR ≥ 1 Critical Remaining Risk. |
| **Deferred** | Foundation Readiness Score ≥ 75 but Architect chooses to defer. |

The Recommended Next Phase is recorded in `REPORT-VALIDATION-01.md` §10.

---

## §10. Validation Cycle Constraints (Honor)

| Constraint | Honored |
|---|---|
| Read-only | YES — no Foundation file is modified |
| No new Standards | YES — only Validation documents |
| No RFC / FD / ADR | YES — none created |
| No Packs / Workspaces / Runtimes / SDKs / Plugins | YES — none created |
| No Project / Migration / Sprint | YES — none executed |
| No Implementation / Git / GitHub Release | YES — none performed |
| No Foundation Version advancement | YES — `FOUNDATION/VERSION` is `0.1.0-dev` and remains so |
| No Constitution amendment | YES — Constitution remains `v0.1.0-draft` Provisional |

---

## §11. Sign-Off

```
Validator:         Research-OS Validation Builder
Validation Cycle:  01
Strategy Date:     2026-08-03
Foundation Status: FROZEN
Companion Docs:    validation-plan.md; validation-checklist.md; REPORT-VALIDATION-01.md;
                   AUDIT-VALIDATION-01.md; REVIEW-VALIDATION-01.md.
Next action:       Validation Builder authors Report, Audit, Review, then delivers
                   seven-section completion report and STOPS.
```

> **Note.** This Validation Strategy is **Draft / In Review**. The Architect's Review disposition is the binding Validation Cycle outcome. The Foundation remains FROZEN. The Validator awaits Architect Review.

---

*End of validation-strategy.md v0.1.0-draft (Draft / In Review).*