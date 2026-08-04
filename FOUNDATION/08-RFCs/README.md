# 08-RFCs

This directory holds **Foundation RFCs (FRFCs)** and **Release RFCs (RRFCs)** of Research-OS Foundation. PRFCs (Project RFCs) are stored within their respective Project directories — see `rfc-policy.md` §9.

## Status

- The RFC mechanism is established by `rfc-policy.md`.
- **One FRFC exists.** `FRFC-0001-foundation-change-principle.md` was authored on 2026-08-03 per Architect Authorization (Part B). Its status is `Approved` per `rfc-policy.md` §5 Status Lifecycle enum (transitioned from `Draft` per Architect Decision, 2026-08-03, Part A; corrected from `Proposed` in Revision Cycle 01).
- **Two Approved FRFCs.** `FRFC-0002-reconcile-first-rc-prerequisites.md` was approved with Notes on 2026-08-04 under the current Human Architect execution instruction. It proposes exact replacement semantics for Release Specification §9.2 conditions 1 and 2 only; preserves FD-0003 binding baseline, Constitution supremacy, §9.2 condition 3 verbatim, and separation of baseline approval / Release Gate approval / RC decision / application / publication. Grounded in Step-1 Validation evidence: `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md`, `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md`, `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md` (Approved with Notes, 2026-08-04). No patch applied; FD-0005 not created; Stage B not authorized; FD-0004 remains Pending; RC not declared; Foundation Invariant preserved. Companion records: `FOUNDATION/04-Audits/AUDIT-FRFC-0002-reconcile-first-rc-prerequisites.md` (Verdict: PASS with Notes; Open Finding-Count: 3 Observations, 0 High); `FOUNDATION/06-Reports/REPORT-FRFC-0002-reconcile-first-rc-prerequisites.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0002-reconcile-first-rc-prerequisites.md` (Status: Approved with Notes).
- **Revision history (2026-08-03, Architect Revision Cycle 01).** The original version of FRFC-0001 recorded initial status as `Proposed`. Architect Review disposition `Revision Required` (2026-08-03) corrected the status to `Draft`. The correction is recorded as Audit finding F-1 (Resolved). Per the Architect's instruction: "Architect authorization permits authorship of an RFC but does not silently amend the RFC Policy. Changing `Proposed` to `Draft` is compliance repair, not an RFC Policy amendment." The `rfc-policy.md` §5 enum is **unchanged** by FRFC-0001.
- **Approval (2026-08-03, Architect Decision, Part A).** The RFC was transitioned from `Draft` to `Approved` per Architect Decision, Part A. Disposition: **Approved with Notes** with three non-blocking Notes (N-1 status-consistency wording reconciliation — "All five files consistently identify the FRFC-0001 lifecycle status as Approved. Each companion artifact retains its own applicable document or review status."; N-2 Constitution version-sequence discrepancy remains out of scope; N-3 Foundation Patch Cycle 01 authorized separately per Architect Decision, Part B). RFC Policy §5 enum is unchanged.
- **Patch implementation (2026-08-03, Architect Decision, Part B).** The Foundation Patch Cycle 01 was separately authorized to implement the approved Foundation Change Principle via existing governance artifacts only (no new Standard/Policy; no Constitution amendment; no FD-0003 or later). Implementation records: `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` (status Ratified); `FOUNDATION/04-Audits/AUDIT-FRFC-0001-implementation.md`; `FOUNDATION/06-Reports/REPORT-FRFC-0001-implementation.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0001-implementation.md` (Disposition: Approved with Notes). Foundation returned to Freeze State after Patch Review approval.
- Task 02 does not create RFCs unless a blocking conflict requires one. No such conflict was discovered.

## Contents

| File | Status | Description |
|---|---|---|
| `README.md` | (this file) | Index for the RFC directory |
| `rfc-policy.md` | Draft / In Review | Operational RFC policy |
| `FRFC-0001-foundation-change-principle.md` | `Approved` (transitioned from `Draft` per Architect Decision, 2026-08-03, Part A; corrected from `Proposed` per Architect Revision Cycle 01, 2026-08-03) | Establishes a normative Foundation Change Principle that constrains how new Foundation artifacts may be introduced. Carries 21 substantive sections per Architect specification, including the triggered Validation Cycle definition (RFC §5.3.1), emergency handling clarification (RFC §10.9), and artifact exclusions (RFC §9.1). Disposition: **Approved with Notes** per Architect Decision, 2026-08-03, Part A (three non-blocking Notes: N-1 wording; N-2 version-sequence out of scope; N-3 patch cycle separate). Implementing FD: **FD-0002 (Ratified, 2026-08-03)** per Architect Decision, Part B. Companion records: `FOUNDATION/04-Audits/AUDIT-FRFC-0001-foundation-change-principle.md` (Verdict: PASS; Open Finding-Count: 0; Resolved Finding-Count: 1 — F-1: initial status corrected); `FOUNDATION/06-Reports/REPORT-FRFC-0001-foundation-change-principle.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0001-foundation-change-principle.md` (Disposition: Approved with Notes). Patch-implementation records: `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` (Ratified); `FOUNDATION/04-Audits/AUDIT-FRFC-0001-implementation.md`; `FOUNDATION/06-Reports/REPORT-FRFC-0001-implementation.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0001-implementation.md` (Disposition: Approved with Notes, 2026-08-03). |
| `FRFC-0002-reconcile-first-rc-prerequisites.md` | `Approved` (Disposition: Approved with Notes, 2026-08-04) | Proposes exact replacement semantics for Release Specification §9.2 conditions 1 and 2 to resolve the validated `NORMATIVE BASELINE CONTRADICTION` between Ratified FD-0003 and §9.2. Condition 1 decoupled from a hardcoded Constitution version and bound to a separate Authorizing FD naming the Constitution ratification state. Condition 2 accepts exact-version aggregated Standard authority (per FD-0003 §3 #2 / §7) while retaining per-Standard FD option. Condition 3 preserved verbatim. Exact-version pin to `v0.1.0-draft` preserved pending the controlled patch. Five alternatives evaluated; A5 approved with three Notes. Migration Plan enumerates the controlled patch sequence (RFC → FD → patch → repair Audit/Report/Review → RC reconcile → re-review). No patch, FD-0005, Stage B, FD-0004 Ratification, RC declaration, Invariant release, Pack/Workspace/Project/APES, git/publication, or identity fabrication occurred. Companion records: `FOUNDATION/04-Audits/AUDIT-FRFC-0002-reconcile-first-rc-prerequisites.md` (Verdict: PASS with Notes; Open Finding-Count: 3 Observations, 0 High); `FOUNDATION/06-Reports/REPORT-FRFC-0002-reconcile-first-rc-prerequisites.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0002-reconcile-first-rc-prerequisites.md` (Status: Approved with Notes). Step-1 evidence: `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md`, `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md`, `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md` (Approved with Notes, 2026-08-04). |

## Future Work

- `FRFC-0001-...`, `RRFC-0001-...`, and beyond, as Foundation Tasks 03–12 require normative changes.
- A ratification cycle for the RFC policy itself (anticipated as a follow-on after Task 02 review).

## RFC Classes (Summary)

| Class | Scope | Stored In | Decision Record |
|---|---|---|---|
| FRFC | Foundation-level normative change | `FOUNDATION/08-RFCs/` | FD |
| PRFC | Project-local normative proposal | `PROJECTS/<project>/08-RFCs/` | PD |
| RRFC | Release planning, scope, exceptions, governance | `FOUNDATION/08-RFCs/` | FD |

## Naming

All RFCs follow `<CLASS>-NNNN-short-title.md`. See `rfc-policy.md` §3.

## Out of Scope

- Foundation Decisions (FDs) — stored in `FOUNDATION/09-Decisions/`.
- Architecture Decision Records (ADRs) — stored in `FOUNDATION/10-ADRs/`.
- Project Decisions (PDs) — stored within the Project's directory.

## Dependencies

- Constitution v0.1.0-draft (Provisional) §6 — defines RFC format and authority.
- Task 02 Governance artifacts — operationalize the FRFC mechanism.
- Foundation FD mechanism — required for FRFC ratification.
