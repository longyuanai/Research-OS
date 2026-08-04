# Disagreement and Escalation

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/02-Governance/disagreement-and-escalation.md`
**Related:** `governance-model.md`; `approval-workflow.md`; Constitution v0.1.0-draft §1, §3.

---

## 1. Purpose

This document defines the workflows by which **disagreements** about Foundation artifacts are recorded, escalated, and resolved. Its goal is to ensure that:

- No decision is made by silence.
- Minority views are preserved.
- Escalation paths are explicit.
- Resolution outcomes are auditable.
- A resolved decision may later be revisited if new evidence emerges.

## 2. Recording a Disagreement

A disagreement is recorded as a **Disagreement Record** (`DIS-<scope>-<NN>-<slug>.md`) in `FOUNDATION/09-Decisions/` (or the Project equivalent). The record contains:

1. **ID** — `DIS-NNNN-<slug>`.
2. **Title** — short imperative phrase.
3. **Date raised** — ISO-8601.
4. **Author(s)** — the individual(s) raising the disagreement.
5. **Subject artifact** — the artifact under dispute (with version).
6. **Position(s)** — each author's position, with rationale and citations.
7. **Conflict-of-interest declarations** — per `roles-and-authority.md` §2.
8. **Outcome** — `Recorded`, `Resolved via <mechanism>`, or `Withdrawn`.
9. **References** — Constitution sections, FDs, ADRs cited.

A disagreement may be raised by **any role**, including a Contributor. The Builder role may raise disagreements about its own work (e.g., when a Reviewer's rejection seems to misapply a Quality Gate criterion).

## 3. When a Disagreement Becomes an RFC

A disagreement becomes a **Foundation RFC** (FRFC) when:

- The disagreement concerns a normative Foundation artifact (Constitution, FD, Standard, Engine, SDK, Plugin, Workspace).
- At least one party proposes a change to the artifact.
- The disagreement cannot be resolved through informal clarification within the Review cycle.

A disagreement may also be raised as a **Release RFC** (RRFC) when the disagreement concerns release planning, release scope, release exceptions, or release governance. RRFCs follow the same routing rules as FRFCs but are bound to release-related artifacts.

The transition from `DIS-` to `FRFC-` (or `RRFC-`) requires:

- A new FRFC (or RRFC) drafted by the proposing party.
- Cross-reference from the RFC header back to the `DIS-` record.
- Cross-reference from the `DIS-` record forward to the RFC.

### 3.1  When a Disagreement Becomes a PRFC

A disagreement becomes a **Project RFC** (PRFC) when:

- The disagreement is bounded within a single Project.
- At least one party proposes a Project-local normative change.
- The disagreement cannot be resolved through informal clarification within the Project's Review cycle.

The transition from `DIS-` to `PRFC-` follows the same cross-reference pattern as FRFCs.

## 4. When a Disagreement Becomes an FD

A disagreement becomes a **Foundation Decision** (FD) when:

- The FRFC is approved and requires an architectural decision to implement.
- The Architect issues an FD that ratifies, modifies, or rejects the FRFC.
- A disagreement requires immediate disposition (e.g., emergency change).

The FD's `References:` section must include the originating `DIS-` record and the `FRFC-` (if any).

## 5. When a Disagreement Becomes an ADR

A disagreement becomes an **ADR** when:

- The disagreement concerns a specific implementation choice, not a normative rule.
- The disagreement can be resolved by documenting the chosen approach and its rationale.
- No normative change to a Foundation artifact is required.

ADRs are lighter-weight than FDs and FRCs; they are appropriate when the disagreement is "which approach is best" rather than "what rule should govern."

## 6. Who Resolves Unresolved Conflicts

When a disagreement is not resolved at the FRFC, RRFC, PRFC, FD, or ADR level, escalation proceeds in this order:

1. **Architect review.** The Architect reviews the disagreement and any related FRFCs/ADRs. The Architect may issue an FD that resolves the conflict.
2. **Constitutional review.** If the conflict concerns a Constitution section, the Architect initiates a constitutional amendment per Constitution §17.2.
3. **Founding-principle review.** As a last resort, the conflict is resolved by reference to the Constitution's Design Principles (§3) and Execution Principles (§16). The principle that better preserves Foundation integrity prevails.
4. **Human override.** The Founding-principle review may be overridden by explicit human instruction, recorded as a Constitution amendment.

The Architect's resolution is recorded as an FD that explicitly references the originating `DIS-` record and explains the reasoning.

## 7. How Minority Views Are Preserved

When a disagreement is resolved, the **minority view** is preserved in the resolution record:

- The `DIS-` record retains all positions, including those that did not prevail.
- The resolving FD includes a `Minority Views:` section that summarizes the minority position and explains why it did not prevail.
- The `CHANGELOG.md` entry for the resolution references the `DIS-` record.

This ensures that future revisitations (see §10) can recover the full reasoning chain.

## 8. How Blocked Work Is Represented

When work is blocked by an unresolved disagreement:

- The Builder's Task Report includes a `Blocked By:` section listing the `DIS-` ID(s).
- The Builder does not proceed past the blocked step.
- The Reviewer is notified that the artifact is blocked.

A blocked artifact remains in `In Review` (or `Submitted`, depending on the workflow stage) until the disagreement is resolved.

## 9. Revisiting a Decision

A `Ratified` or `Approved` decision may be revisited when:

- New evidence emerges that was not available at decision time.
- The original decision is shown to have been based on incorrect assumptions.
- The Foundation context has materially changed.

The revisitation proceeds as:

1. A new `DIS-` record is opened, referencing the original decision.
2. The disagreement is processed through the normal FRFC / FD / ADR flow.
3. A new FD supersedes the original if the revisitation succeeds.

The original decision remains in `Ratified` (or `Approved`) until the superseding FD's transition; it then enters `Superseded` (Constitution §12). This preserves history.

## 10. Audit Trail

Every disagreement, FRFC, FD, and ADR leaves an audit trail:

- `Status:` line in each artifact.
- Cross-references between `DIS-`, `FRFC-`, `FD-`, and `ADR-` records.
- `CHANGELOG.md` entries for each transition.

The Audit Report for any Foundation Task verifies that the audit trail is complete and that no decision was made by silence.

---

*End of Disagreement and Escalation v0.1.0-draft.*
