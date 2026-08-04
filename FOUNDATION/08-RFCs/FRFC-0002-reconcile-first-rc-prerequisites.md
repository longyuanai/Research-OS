# Research-OS — Foundation RFC 0002 — Reconcile First-RC Prerequisites with the Approved Foundation Baseline

**ID:** FRFC-0002
**Title:** Reconcile First-RC Prerequisites with the Approved Foundation Baseline
**Status:** Approved
**Version:** 0.1.0-draft
**Date:** 2026-08-04
**Author:** Research-OS Foundation Builder (Builder role)
**Related Constitution Version:** v0.1.0-draft (Ratified via FD-0001, 2026-08-03)
**Supersedes:** none
**Superseded By:** not required
**Decision Scope:** Foundation
**Affected Artifacts:**

- `FOUNDATION/03-Standards/release-specification.md` — §9.2 conditions 1 and 2 (proposed replacement; not applied in this cycle)
- `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md` — binding baseline authority; unchanged
- `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md` — pending Foundation repair
- `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md` — Pending; not the repair mechanism
- `FOUNDATION/01-Constitution/constitution.md` — supremacy preserved; not amended
- `FOUNDATION/02-Governance/change-control-policy.md` — workflow preserved

**Migration Plan:** required (proposes normative replacement of Release Specification §9.2 clauses 1 and 2; exact-version pin to `v0.1.0-draft` preserved pending the controlled patch)
**Last Transition:** In Review → Approved, 2026-08-04 (Human Architect execution instruction; disposition: Approved with Notes)
**Trigger:** Architect Decision "Approve Triggered Validation Cycle 03 — Authorize FRFC-0002 Proposal Cycle" (2026-08-04)
**Related:** `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md`; `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md`; `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md` (Approved with Notes, 2026-08-04); `FOUNDATION/04-Audits/AUDIT-FRFC-0002-reconcile-first-rc-prerequisites.md`; `FOUNDATION/06-Reports/REPORT-FRFC-0002-reconcile-first-rc-prerequisites.md`; `FOUNDATION/07-Reviews/REVIEW-FRFC-0002-reconcile-first-rc-prerequisites.md`

---

## 1. Summary

Validation Cycle 03 (2026-08-04) classified the conflict between Ratified FD-0003 and
Release Specification §9.2 conditions 1 and 2 as a `NORMATIVE BASELINE CONTRADICTION`.
The Foundation Change Principle (binding through Ratified FD-0002) requires a separate
Foundation RFC, a separate implementing FD, a controlled patch, and a repair
audit/review before the RC package can be reconciled. This RFC proposes exact
replacement semantics for §9.2 conditions 1 and 2 only; it does not apply them. The
proposed replacement decouples conditions 1 and 2 from a hardcoded Constitution
version and from a per-Standard-FD enumeration, while preserving FD-0003's binding
baseline authority, the Constitution supremacy principle, §9.2 condition 3 verbatim,
and the separation between baseline approval, Release Gate approval, RC decision,
application, and publication.

## 2. Motivation

The Foundation is Frozen at platform version `0.1.0-dev`. The first `rc` Release is
forbidden until §9.2 conditions 1, 2, and 3 are satisfied. Validation Cycle 03
established:

- §9.2 is part of the exact Release Specification version (`v0.1.0-draft`) bound by
  Ratified FD-0003.
- FD-0003 §3 #2 supplies binding baseline authority to the exact version despite its
  Draft / In Review header.
- FD-0003 §3 #4 (preservation of artifact versions) and FD-0003 §7 (aggregated Category
  C approval) conflict operationally with §9.2 conditions 1 and 2.
- No FD-0003 clause expressly overrides, waives, supersedes, or modifies §9.2.
- §9.2 condition 3 remains compatible with FD-0003.

Eight-unit RC condition accounting normalizes the package:

| Unit | Classification |
|---|---|
| RC-1 | SATISFIED IN STAGE A |
| RC-2 | NOT A VALID CONDITION (authoritative dispute remains) |
| RC-3 | NOT A VALID CONDITION (authoritative dispute remains) |
| RC-4 | READY FOR HUMAN APPROVAL |
| RC-5a | READY FOR HUMAN APPROVAL |
| RC-5b | REQUIRES STAGE B APPLICATION |
| RC-6 | REQUIRES STAGE B APPLICATION |
| RC-7 | READY FOR HUMAN APPROVAL |
| EV-1 | Evidence only (FD-0003 baseline authority verification); excluded from denominator |

Correct denominator: 8 accountable units. EV-1 excluded. RC-3 is not double-counted.
RC-5a and RC-5b are distinct.

RC-2 and RC-3 are the two conditions tied to §9.2 conditions 1 and 2. They remain
disputed pending this Foundation repair.

## 3. Validation Evidence

This RFC is grounded in Step-1 Validation evidence per `change-control-policy.md §8`:

- `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md` — Draft / In Review; the
  sixteen primary questions, exact §9.2 quotation, eleven-row Authority Matrix,
  eight-unit condition accounting, EV-1 separation, ten Quality Gates, and findings
  F-1 through F-6.
- `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md` — Draft / In Review;
  independent evidence verification, explicit-override test, classification audit,
  and accounting audit.
- `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md` — Approved with Notes,
  2026-08-04; substantive finding `NORMATIVE BASELINE CONTRADICTION` accepted;
  required action `FOUNDATION RFC AND CONTROLLED PATCH REQUIRED`.

The Builder may not self-approve this RFC; final disposition is reserved for the
Human Architect.

## 4. Scope

**In scope.** Release Specification §9.2 conditions 1 and 2 only.

**Out of scope.** §9.2 condition 3; Constitution amendment; modification of FD-0003
or FD-0004; Ratification of FD-0004; Stage B authorization; RC declaration;
Foundation Invariant release; any Pack, Workspace, Project, or APES action; any
git or publication action; any change to the Release Manifest; any change to
`FOUNDATION/VERSION`.

## 5. Detailed Proposal

The proposed replacement text for §9.2 conditions 1 and 2 is presented below. The
current text is quoted exactly from `FOUNDATION/03-Standards/release-specification.md`
v0.1.0-draft. The proposed text is RFC proposal only; it is **not** applied in this
cycle. Application requires a separate implementing FD and a controlled patch after
this RFC is approved.

### 5.1 Current §9.2 text (binding via FD-0003)

> During the Foundation phase:
>
> - A Release of type `rc` is **forbidden**.
> - A Release of type `ga` is **forbidden**.
> - A Release of type `dev` is the **only** Release type permitted.
>
> The first `rc` Release may be declared **only** when:
>
> 1. The Constitution has been amended to `v1.0.0` or an equivalent ratified state.
> 2. Every Foundation Standard has been ratified via an Authorizing FD.
> 3. The Foundation Invariant is explicitly released by an Authorizing FD.
>
> Until those three conditions are met, no Release may declare `rc` or `ga`.

### 5.2 Proposed replacement for condition 1

> 1. The Constitution has reached a Human-Architect-ratified state explicitly
>    authorizing first-RC declaration, as recorded by a separate Authorizing FD that
>    names the Constitution ratification state and the scope of first-RC authorization.

**Rationale.** Decouples the condition from a hardcoded version string while
preserving a meaningful ratified-Constitution requirement. The Constitution
supremacy principle is preserved; the binding version remains v0.1.0-draft (Ratified
via FD-0001) until a separate Authorizing FD advances it. The replacement still
requires a Human Architect signature on the authorizing ratification.

### 5.3 Proposed replacement for condition 2

> 2. Every Foundation Standard has been either (a) ratified via an Authorizing FD, or
>    (b) bound to an exact version by an aggregated-approval FD whose binding scope
>    has been ratified by a Human Architect and has not been contested by any active
>    FD or normative artifact.

**Rationale.** Accepts exact-version aggregated Standard authority where valid
(pursuant to FD-0003 §3 #2 and §7). Preserves the existing aggregated-approval
pathway that produced Ratified FD-0003. Retains the per-Standard FD option for any
Standard whose binding scope is contested or whose ratification cannot be
aggregated. Eliminates the implicit all-or-nothing enumeration that conflicts
operationally with FD-0003.

### 5.4 Condition 3 — preserved verbatim

> 3. The Foundation Invariant is explicitly released by an Authorizing FD.

**Rationale.** Condition 3 is compatible with FD-0003. It is preserved exactly. The
Foundation Invariant 2026-08-03 remains preserved until an Authorizing FD
explicitly releases it.

### 5.5 Preservation of exact-version pin

The binding exact-version pin to Release Specification `v0.1.0-draft` is preserved.
A separate implementing FD, if and when this RFC is approved, must apply the
controlled patch as a new version of the Release Specification with an explicit
transition narrative (e.g., `v0.2.0-draft` or `v1.0.0`), preserving the binding
authority of FD-0003 over the prior version and binding the new version by the same
process.

## 6. Affected Artifacts

| Artifact | Current State | Required Change Scope |
|---|---|---|
| `FOUNDATION/03-Standards/release-specification.md` | Ratified baseline binding via FD-0003; §9.2 conditions 1 and 2 conflict with FD-0003 | Controlled patch after implementing FD; this RFC only proposes |
| `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md` | Ratified | Unchanged |
| `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md` | Pending | Unchanged; remains a Release Authorization decision |
| `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md` | Draft / Stage 1 | Reconciled only after Foundation repair; not in this cycle |
| `FOUNDATION/01-Constitution/constitution.md` | v0.1.0-draft Ratified via FD-0001 | Unchanged |
| `FOUNDATION/02-Governance/change-control-policy.md` | Binding | Unchanged |
| `FOUNDATION/02-Governance/governance-model.md` | Binding | Unchanged |
| `FOUNDATION/03-Standards/schema-standard.md` | Binding | Unchanged |
| `FOUNDATION/03-Standards/directory-standard.md` | Binding | Unchanged |

## 7. Migration Plan

A controlled patch sequence applies only after this RFC is `Approved` and a separate
implementing FD is `Ratified`:

1. RFC `Approved` by Human Architect disposition.
2. Implementing FD drafted, audited, reported, reviewed, and Ratified by Human
   Architect.
3. The implementing FD authorizes the exact patch scope (clauses 1 and 2 of §9.2;
   new Release Specification version; preservation of binding baseline).
4. The controlled patch is applied by editing `release-specification.md` only.
5. Foundation repair Audit, Report, and Review are produced and reviewed.
6. The RC package is reconciled against the patched Standard.
7. The RC package returns to Human Architect for Stage B re-review.
8. `CHANGELOG.md` records the Foundation repair event.

No automatic patch is permitted at any step. No step may be skipped.

## 8. Compatibility

**Backward compatibility.** No existing Foundation artifact currently consumes the
patched semantics. The RC package is blocked; no Release consumes §9.2. The patched
semantics are activated only after the implementing FD, patch, repair audit/review,
and RC re-review complete.

**Forward compatibility.** Next-RC semantics are explicitly preserved: condition 3
remains binding; FD-0003's baseline authority over the prior version is preserved;
the new Release Specification version is bound by the same aggregated-approval
process that produced FD-0003.

**Quality Gate effects.** Constitution §11 Quality Gate criteria are unchanged. The
Foundation Change Principle and Patch Cycle precedence are unchanged. Cross-Reference
integrity is preserved by citing RFC, Audit, Report, Review, and Validation Cycle 03
records as concrete paths.

**Policy effects.** `change-control-policy.md §8` and `rfc-policy.md §10` are
followed exactly. RFC approval alone does not bind; the implementing FD is
separately required.

## 9. Security / Isolation

No Project-specific rule, lifecycle, schema, or implementation rule is introduced.
Foundation ↔ Project isolation is preserved per `governance-model.md §1` and
`approval-workflow.md §6`. No Pack, Workspace, Project, or APES action is
authorized. No git or publication action is authorized. The Audit and Report
explicitly confirm isolation.

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Replacement text weakens unrelated controls | Low | High | Migration Plan binds a narrow patch scope; repair audit/review required; condition 3 preserved verbatim |
| Aggregated-authority phrasing is later contested | Medium | Medium | Replacement retains the per-Standard FD option for contested Standards |
| Implementing FD silently broadens scope | Medium | High | Implementing FD must be a separate, audited, reviewed decision; controlled patch authorized by it |
| Foundation repair conflated with Release authorization | Medium | High | FD-0004 explicitly prohibited as the repair mechanism; separation preserved |
| RC package reconciled before repair completes | Low | High | RC package remains blocked; re-review required after repair |

## 11. Acceptance Criteria

This RFC is `Approved → Ratified` only when:

1. The Human Architect disposition sets `Status: Approved` on this RFC.
2. A separate implementing FD is `Ratified` by the Human Architect, scoped to
   clauses 1 and 2 of §9.2 only, preserving condition 3 and FD-0003's baseline.
3. The controlled patch is applied exactly as authorized.
4. Foundation repair Audit verdict is `PASS` or `PASS with Notes`.
5. Foundation repair Review disposition is `Approved` or `Approved with Notes`.
6. The RC package is reconciled against the patched Standard.
7. The RC package returns to Human Architect for Stage B re-review.

## 12. Rollback

If the implementing FD fails, the patch fails verification, or the repair audit
or review records a blocking finding:

1. The Release Specification reverts to `v0.1.0-draft` §9.2 (current state).
2. FD-0003 remains Ratified and binding over `v0.1.0-draft`.
3. The Foundation Invariant 2026-08-03 remains preserved.
4. The RC package remains blocked.
5. `CHANGELOG.md` records the failed attempt, the rollback, and the rationale.
6. A new FRFC may be opened to propose a different replacement; this RFC's status
   transitions to `Withdrawn` or `Superseded` per RFC Policy.

## 13. Drawbacks

- The decoupled condition 1 phrasing requires a separate Authorizing FD to name the
  Constitution ratification state, adding one explicit artifact to the route.
- The decoupled condition 2 phrasing retains aggregated authority, which may be
  recontested if a future Standard's binding scope is unclear.
- The route lengthens the path to first-RC by one explicit implementing FD and one
  repair audit/review cycle, which is correct per the binding change principle but
  increases coordination cost.

## 14. Alternatives Considered

Five alternatives were evaluated:

- **A1: Status quo (no change).** Rejected. The RC package would remain blocked
  indefinitely; conditions 1 and 2 remain unmet in literal reading; the
  contradiction is unresolved.
- **A2: Ratify FD-0004 as the Foundation repair.** Rejected. FD-0004 is a Release
  Authorization decision, not a Foundation repair mechanism; it cannot silently
  reinterpret a Standard; using it would bypass the binding change principle.
- **A3: Amend the Constitution to v1.0.0.** Rejected as primary route. Bypasses the
  binding change principle; weakens a ratified Constitution requirement; conflates
  the Foundation repair with a Constitution amendment.
- **A4: Treat §9.2 self-declaration (§12) as non-normative.** Rejected. FD-0003 §3
  #2 supplies binding baseline authority to the exact version regardless of header
  status; the self-declaration cannot negate the binding derivation.
- **A5 (recommended): Decouple conditions 1 and 2 from a hardcoded version and from
  a per-Standard-FD enumeration via this RFC, preserving binding baseline, a
  meaningful Constitution requirement, and condition 3 verbatim.** Accepts
  exact-version aggregated authority where valid; requires a separate implementing
  FD; requires a controlled patch and repair audit/review before RC reconciliation.

## 15. Review Questions

- Is the decoupled condition 1 phrasing consistent with Constitution supremacy and
  the binding change principle?
- Is the decoupled condition 2 phrasing sufficient to accept FD-0003's aggregated
  authority while preserving per-Standard FD option?
- Are condition 3 and the exact-version pin correctly preserved?
- Is the Migration Plan complete, controlled, and free of implicit shortcuts?
- Are the Acceptance Criteria measurable and sufficient?
- Are the Hard Prohibitions complete and consistent with the binding change
  principle and the Foundation Invariant?

## 16. Open Questions

None at draft time.

## 17. References

- `FOUNDATION/01-Constitution/constitution.md` — v0.1.0-draft, Ratified via FD-0001.
- `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md` — Ratified.
- `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` — Ratified.
- `FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md` — Approved.
- `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md` — Ratified.
- `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md` — Pending.
- `FOUNDATION/03-Standards/release-specification.md` — v0.1.0-draft (binding via FD-0003).
- `FOUNDATION/02-Governance/governance-model.md`.
- `FOUNDATION/02-Governance/change-control-policy.md` (§8 RFC → FD → patch route).
- `FOUNDATION/02-Governance/approval-workflow.md`.
- `FOUNDATION/02-Governance/roles-and-authority.md`.
- `FOUNDATION/02-Governance/disagreement-and-escalation.md`.
- `FOUNDATION/09-Decisions/foundation-decision-policy.md`.
- `FOUNDATION/03-Standards/schema-standard.md`.
- `FOUNDATION/03-Standards/directory-standard.md`.
- `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md`.
- `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md`.
- `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md` — Approved with Notes.

## 18. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-08-04 | Research-OS Foundation Builder (Builder role) | Initial Draft. Twenty-one sections per RFC Policy §6 and FRFC-0001 precedent. Five alternatives evaluated; A5 recommended. No patch applied. No personal identity or signature fabricated. |
| 0.1.0-draft (approval disposition) | 2026-08-04 | Human Architect (role-based) | RFC transitioned through review to Approved with Notes under the current execution instruction. Notes require the implementing FD to preserve the separate authorization boundaries, prove the condition-2 authority test against active normative artifacts, and pin the exact replacement text and target version. No implementing FD or patch is created in this cycle. |

## 19. Hard Prohibitions

This RFC is Approved as a proposal only. The following remain prohibited in this
approval-disposition cycle:

- Do not patch Release Specification §9.2 or any other Standard.
- Do not modify FD-0003, FD-0004, the Release Manifest, Release Audit, Release
  Report, or Release Review.
- Do not amend the Constitution.
- Do not create FD-0005 or any other implementing FD in this cycle.
- Do not authorize Stage B.
- Do not Ratify FD-0004.
- Do not modify `FOUNDATION/VERSION`.
- Do not declare the RC.
- Do not advance the Release Manifest.
- Do not release the Foundation Invariant.
- Do not create a Pack, Workspace, or Project.
- Do not modify or migrate APES.
- Do not perform git or publication actions.
- Do not fabricate approval, identity, or signature information.

## 20. Decision Status

**Status:** Approved.
**Disposition:** Approved with Notes, 2026-08-04.
**Approval evidence:** Current Human Architect execution instruction (role-based;
no personal identity or handwritten signature stored).
**Next governance task:** Draft the separate implementing FD only after this cycle
stops and a new, explicitly scoped Foundation Task begins.

## 21. Cross-References

- Validation Cycle 03 Report, Audit, Review.
- RFC Policy (`FOUNDATION/08-RFCs/rfc-policy.md`).
- Schema Standard (`FOUNDATION/03-Standards/schema-standard.md`).
- Directory Standard (`FOUNDATION/03-Standards/directory-standard.md`).
- Change-Control Policy (`FOUNDATION/02-Governance/change-control-policy.md`).
- Governance Model (`FOUNDATION/02-Governance/governance-model.md`).
- FRFC-0001 (`FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md`) —
  precedent for header fields, body sections, evidence basis, and companion
  records.

---

*End of FRFC-0002 — Reconcile First-RC Prerequisites with the Approved Foundation Baseline — Approved, 2026-08-04.*
