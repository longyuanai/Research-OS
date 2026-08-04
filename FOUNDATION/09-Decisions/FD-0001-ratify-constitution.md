# FD-0001 — Ratify the Research-OS Constitution (v0.1.0-draft)

**ID:** FD-0001
**Title:** Ratify the Research-OS Constitution (v0.1.0-draft)
**Status:** Ratified
**Version:** 0.1.0-draft
**Date:** 2026-08-03
**Owner:** Architect
**Approver:** Human Architect — Role-based approval (no personal name, signature, or identity data; per Architect Decision, 2026-08-03)
**Related Constitution Version:** 0.1.0-draft (Ratified)
**Supersedes:** none
**Superseded By:** none
**Dependencies:** Foundation Task 01 (Constitution); Foundation Task 02 (Governance); `FOUNDATION/09-Decisions/foundation-decision-policy.md`.
**Decision Scope:** Ratification
**ratifies-constitution:** 0.1.0-draft
**Last Transition:** Builder (Task 02) → `Pending Ratification`, 2026-08-03; Human Architect → `Ratified`, 2026-08-03.

---

## 1. Context

Research-OS Foundation Task 01 produced the Constitution at version `0.1.0-draft` with status `Provisional`. Per the Constitution's own §17.3 (Ratification Sequence), the Provisional Constitution can govern Foundation work on a best-effort basis but cannot be formally binding until:

1. Task 02 establishes the FD mechanism.
2. An Architect-issued `FD-0001` ratifies the Constitution with explicit `ratifies-constitution: 0.1.0-draft` flag.

This FD fulfills step (2). Task 02 establishes step (1) via the FD Policy and the other governance artifacts.

## 2. Decision

**The Architect ratifies the Research-OS Constitution at version `0.1.0-draft`, located at `FOUNDATION/01-Constitution/constitution.md`, as the binding governance document of the Research-OS Foundation, effective upon the Architect's signature on this FD.**

Upon ratification:

- The Constitution's header `Status:` line updates from `Provisional` to `Ratified`.
- Prior versions (`v0.1`, `v0.2`) enter the **Archived** state (Constitution §17.1).
- `CHANGELOG.md` records the ratification with date and FD reference.

## 3. Effect on the Constitution

This FD does **not** modify the Constitution's content. The Constitution, as written in `FOUNDATION/01-Constitution/constitution.md` at version `0.1.0-draft`, becomes the ratified governance document.

Any subsequent change to the Constitution requires a new FD that:

- Declares `amends-constitution: true` (Constitution §17.2).
- Includes a Migration Plan.
- Carries a MAJOR version bump.
- Is approved by the Architect through the constitutional amendment workflow.

## 4. Ratification Does Not Promote the Foundation to RC

**This FD does not declare the Foundation v1.0.0-rc.1.** The Foundation platform remains at version `0.1.0-dev`. The Foundation RC gate is **Task 12 (Foundation Release Candidate)**; Task 12 is the **only** path by which Foundation `v1.0.0-rc.1` may be declared (Constitution §14.1, §17.3 step 5).

Constitution ratification makes the governance document binding. It does not declare the platform ready for release. Project work, Foundation Standards, Engines, SDKs, Plugins, and Workspaces remain under development and require their own Tasks (Tasks 03–11) and review.

## 5. Foundation Version Remains `0.1.0-dev`

`FOUNDATION/VERSION` remains `0.1.0-dev` until Task 12 passes review. No version bump is applied by this FD.

## 6. Task 12 Is the Only Foundation RC Gate

The Foundation `v1.0.0-rc.1` tag is reserved and may not be applied to any artifact before Task 12 passes review. The Hard Prohibitions (Constitution §15.3) explicitly forbid claiming `1.0.0-rc.1` or `1.0.0` status before then.

## 7. Required Approver

This FD requires the **human Architect** as approver. The Architect's signature, name, and date must be supplied via explicit human instruction.

**No AI agent, including the Foundation Builder, may:**

- Sign this FD on behalf of a human.
- Fabricate a signature, name, or approval timestamp.
- Transition this FD out of `Pending Ratification` to `Ratified` without explicit human approval.

## 8. Current Status

This FD is **Ratified** as of 2026-08-03. The Architect's disposition was issued as part of the Architect Decision "Approve Validation Cycle 01 and Ratify FD-0001" on 2026-08-03, with explicit directive to:

- Transition this FD from `Pending Ratification` to `Ratified`.
- Record `ratifies-constitution: 0.1.0-draft`.
- Update the Constitution's status from `Provisional` to `Ratified`.
- Retain the Constitution version `0.1.0-draft` (per the explicit instruction: "Do not change its version unless the existing governance policy explicitly requires removal of the `-draft` suffix after ratification. If version semantics are ambiguous, retain `0.1.0-draft`, mark it Ratified, and record the ambiguity for the maintenance RFC rather than inventing a rule.").
- Not create FD-0002 automatically, nor FD-0003 through FD-0012 (Standards ratification is deferred and conditional; a later Foundation baseline decision may ratify the reviewed Standard set collectively).
- Not declare Foundation `v1.0.0-rc.1`; not advance `FOUNDATION/VERSION` from `0.1.0-dev`.

### Effect on the Constitution

The Constitution's header `Status:` line is updated from `Provisional` to `Ratified`. The Constitution's `Version:` line remains `0.1.0-draft`. The version semantics ambiguity (whether ratification removes the `-draft` suffix) is recorded for resolution in a subsequent Maintenance RFC; this FD does not invent a rule.

### Effect on the Foundation

- `FOUNDATION/VERSION` remains `0.1.0-dev`.
- Foundation RC (`1.0.0-rc.1`) is **not** declared by this FD. Task 12 remains the only Foundation RC gate.
- Standards remain Draft / In Review. The Foundation baseline decision on Standards is deferred.
- No Pack, no Workspace, no Project, no Engine, no SDK, no Plugin, no Runtime is created by this FD.
- APES remains Frozen.
- The Foundation's governance scope is unchanged by this FD.

### Non-Normative Note (Validation Cycle 01 Observation)

Validation Cycle 01 identified a potential governance gap concerning evidence-driven Foundation expansion. Resolution is deferred to a separately proposed and approved Foundation RFC. No governance principle is adopted, ratified, or rendered binding by this FD.

### Validation Cycle 01 Disposition

Validation Cycle 01 was reviewed and disposed as **Approved with Notes** in the same Architect Decision that ratified this FD. The disposition is recorded in `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-01.md` §4. The disposition text is reproduced verbatim in that Review record; this FD does not adopt, endorse, or ratify any disposition language beyond recording that the cycle was disposed.

### Scope of this FD

This FD is limited to ratifying `FOUNDATION/01-Constitution/constitution.md` at version `0.1.0-draft`. No other Foundation governance decision is made, modified, or implied by this FD.

## 9. References

- `FOUNDATION/01-Constitution/constitution.md` (Constitution v0.1.0-draft, Provisional)
- `FOUNDATION/09-Decisions/foundation-decision-policy.md`
- `FOUNDATION/02-Governance/governance-model.md`
- `FOUNDATION/02-Governance/approval-workflow.md`
- `FOUNDATION/02-Governance/roles-and-authority.md`
- Constitution §17.3 (Ratification Sequence)

## 10. Approver Signature

| Field | Value |
|---|---|
| Approver Name | *(not recorded — per Architect Decision: no personal name fabricated)* |
| Approval Date | 2026-08-03 |
| Signature | *(not recorded — per Architect Decision: no signature image or identity data fabricated)* |
| Authority | Human Architect — Role-based approval, per Architect Decision "Approve Validation Cycle 01 and Ratify FD-0001" issued 2026-08-03. Authority is established by the Architect Decision text itself; no personal name, signature, email, or identity data is fabricated. |

Authority for the ratification is established by:

1. The explicit `ratifies-constitution: 0.1.0-draft` flag in this FD's header.
2. The Architect Decision of 2026-08-03 explicitly directing this transition.
3. The date 2026-08-03 in this Approver Signature block.
4. The corresponding Validation Review disposition recorded in `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-01.md` §4.

Per the Constitution §7.4 ("An FD becomes `active` upon the Architect's signature recorded in its header. No FD is binding until active."), this FD is **active** upon the recorded Authority and Date; the FD Policy's signature requirement is satisfied by the recorded Authority field without fabrication of personal identity data.

---

*End of FD-0001 v0.1.0-draft (Ratified).*
