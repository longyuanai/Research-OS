# FD-0005 — Implement the First-RC Prerequisite Repair

**ID:** FD-0005-implement-first-rc-prerequisite-repair
**Title:** Implement the approved first-RC prerequisite repair
**Status:** Ratified
**Version:** 0.1.0-draft
**Date:** 2026-08-04
**Owner:** Architect
**Approver:** Human Architect — role-based approval recorded from the current continuation instruction; no personal identity or handwritten signature stored
**Related Constitution Version:** v0.1.0-draft (Ratified by FD-0001)
**Related RFC:** FRFC-0002-reconcile-first-rc-prerequisites (Approved with Notes, 2026-08-04)
**Supersedes:** none
**Superseded By:** none
**Dependencies:** FD-0001 (Ratified); FD-0002 (Ratified); FD-0003 (Ratified); FRFC-0002 (Approved with Notes); Validation Cycle 03 (Approved with Notes); `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/03-Standards/release-specification.md`.
**Decision Scope:** Amendment
**Last Transition:** `Pending Ratification` → `Ratified`, 2026-08-04 (Human Architect continuation instruction).

---

> **Ratification boundary.** This FD was explicitly Ratified by the Human Architect
> through the current continuation instruction. Ratification authorizes the later
> controlled patch described herein; it does not claim that the patch has been
> applied and does not release the Foundation Invariant, authorize Stage B, or
> advance the Foundation version.

## §1. Context

Validation Cycle 03 confirmed a `NORMATIVE BASELINE CONTRADICTION` between Ratified
FD-0003 and Release Specification `0.1.0-draft` §9.2 conditions 1 and 2. The
validated repair route requires:

1. Validation evidence;
2. an approved Foundation RFC;
3. a separately Ratified implementing FD;
4. an exact controlled patch;
5. repair Audit, Report, and Review;
6. RC-package reconciliation and Human Architect re-review.

Steps 1 and 2 are complete. `FRFC-0002-reconcile-first-rc-prerequisites.md` was
Approved with Notes on 2026-08-04. This FD is the Step-4 implementing decision
package. It does not itself perform Step 5.

### §1.1 Approval Notes carried from FRFC-0002

This FD implements all three binding approval Notes:

1. preserve separation between RFC approval, Foundation patch authorization, RC
   authorization, application, and publication;
2. prove that the aggregated-approval route in proposed condition 2 is not
   contested by an active FD or other normative artifact after the explicit
   supersession performed by this Decision;
3. pin the exact replacement text, source version, target version, affected file,
   and rollback boundary.

## §2. Decision

If and only if this FD is explicitly Ratified by a Human Architect, the Architect
authorizes one controlled Foundation patch with the following exact scope.

### §2.1 Source and target

| Field | Authorized value |
|---|---|
| Source artifact | `FOUNDATION/03-Standards/release-specification.md` |
| Source Standard version | `0.1.0-draft` |
| Target Standard version | `0.2.0-draft` |
| Document status after patch | `Draft / In Review` |
| Clauses replaced | §9.2 conditions 1 and 2 only |
| Clause preserved verbatim | §9.2 condition 3 |
| Other permitted edit | Header `Version:` and the Standard Change Log entry required to record the transition |
| Foundation platform version | Unchanged at `0.1.0-dev` |

No other Standard clause, governance artifact, FD, Release artifact, or version
surface is authorized for modification.

### §2.2 Exact resulting §9.2 text

The controlled patch must make §9.2 read exactly as follows:

> ### §9.2 Prohibition on `rc` and `ga` Release Types
>
> During the Foundation phase:
>
> - A Release of type `rc` is **forbidden** (per Constitution §15.3 Hard Prohibitions).
> - A Release of type `ga` is **forbidden**.
> - A Release of type `dev` is the **only** Release type permitted during the Foundation phase.
>
> The first `rc` Release may be declared **only** when:
>
> 1. The Constitution has reached a Human-Architect-ratified state explicitly
>    authorizing first-RC declaration, as recorded by a separate Authorizing FD
>    that names the Constitution ratification state and the scope of first-RC
>    authorization.
> 2. Every Foundation Standard has been either (a) ratified via an Authorizing FD,
>    or (b) bound to an exact version by an aggregated-approval FD whose binding
>    scope has been ratified by a Human Architect and has not been contested by
>    any active FD or normative artifact.
> 3. The Foundation Invariant is **explicitly released** by an Authorizing FD.
>
> Until those three conditions are met, no Release may declare `rc` or `ga`.

Condition 3 is reproduced verbatim from `0.1.0-draft`. The prohibitions before and
after the three conditions are also preserved verbatim.

### §2.3 Authority test for condition 2

The required authority test is satisfied for the controlled patch:

| Authority | State | Effect on aggregated approval |
|---|---|---|
| Constitution v0.1.0-draft | Ratified by FD-0001 | Declares Task 12 the only Foundation RC gate; does not require one FD per Standard |
| FD-0001 | Ratified | No contest |
| FD-0002 | Ratified | Requires the RFC → FD → patch route used here; no contest |
| FD-0003 | Ratified | Explicitly binds the exact versions of all 15 baseline components through one aggregated approval |
| FRFC-0002 | Approved with Notes | Approves replacement semantics that recognize aggregated approval |
| Release Specification `0.1.0-draft` §9.2 condition 2 | Binding baseline clause and patch target | Explicitly superseded only within condition 2 by this FD after ratification and controlled application |
| FD-0004 | Pending | Non-binding; cannot contest or implement this repair |

No active FD contests FD-0003's aggregated-approval scope. The only normative
conflict is the exact source clause being explicitly replaced through this
Ratified-FD route. This is explicit supersession, not a silent waiver.

### §2.4 Binding and application rule

Ratification authorizes the patch but does not claim that the patch has already
been applied. The transition becomes operational only when all of the following
occur:

1. this FD is Ratified;
2. the exact patch in §2.1–§2.2 is applied to the single allowed Standard;
3. the repair Audit verifies exact-text and version integrity;
4. the repair Review receives Human Architect disposition `Approved` or
   `Approved with Notes`.

Until then, Release Specification `0.1.0-draft` remains the on-disk source and the
RC package remains blocked.

### §2.5 Separation of authorization boundaries

This FD is a Foundation repair authorization only. It does not:

- Ratify FD-0004;
- release the Foundation Invariant;
- authorize or perform Stage B;
- declare a Release;
- advance the Release Manifest;
- modify `FOUNDATION/VERSION`;
- create a git tag or external publication.

Those actions remain separate governance events after repair Review and RC-package
reconciliation.

## §3. Consequences

### §3.1 Positive

- Resolves the two validated prerequisite contradictions through an explicit,
  auditable authority chain.
- Preserves FD-0003's aggregated baseline approval.
- Preserves Constitution supremacy and §9.2 condition 3.
- Keeps RC authorization, application, and publication separate.

### §3.2 Negative

- Requires a Standard minor-version transition before RC-package reconciliation.
- Adds a repair Audit and Human Review before Stage B can be reconsidered.
- Leaves the RC package blocked until all application conditions in §2.4 pass.

### §3.3 Neutral

- The Foundation platform remains `0.1.0-dev`.
- The Release Specification retains document status `Draft / In Review`.
- FD-0004 and the Release Manifest retain their current pending/draft states.
- APES remains paused and Frozen.

## §4. Affected Artifacts

### §4.1 Authorized patch target

1. `FOUNDATION/03-Standards/release-specification.md` — only the exact changes
   enumerated in §2.1–§2.2 after ratification.

### §4.2 Required process records

1. `FOUNDATION/04-Audits/AUDIT-FD-0005-implement-first-rc-prerequisite-repair.md`.
2. `FOUNDATION/06-Reports/REPORT-FD-0005-implement-first-rc-prerequisite-repair.md`.
3. `FOUNDATION/07-Reviews/REVIEW-FD-0005-implement-first-rc-prerequisite-repair.md`.
4. `CHANGELOG.md` — decision-package entry now; repair-application entry only in
   the later patch cycle.

### §4.3 Explicitly unaffected

- `FOUNDATION/01-Constitution/constitution.md`;
- FD-0001 through FD-0004;
- all other Foundation Standards and Governance artifacts;
- `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`;
- `FOUNDATION/VERSION`;
- every Pack, Workspace, Project, Runtime, Engine, SDK, and Plugin artifact.

## §5. Migration Plan

1. Human Architect reviews this FD decision package.
2. If accepted, the Human Architect explicitly Ratifies FD-0005.
3. A new, separately scoped patch cycle edits only
   `release-specification.md` as authorized by §2.
4. The patch cycle verifies:
   - source version `0.1.0-draft`;
   - target version `0.2.0-draft`;
   - exact §9.2 resulting text;
   - condition 3 unchanged;
   - all other clauses unchanged.
5. Patch Audit, Report, and Review are produced.
6. Human Architect reviews the applied repair.
7. Only after repair approval is the RC package reconciled.

No step may be skipped or combined with Stage B.

### §5.1 Rollback

- Before patch application: leave `release-specification.md` unchanged; FD-0005
  may be Rejected or Withdrawn.
- After patch application but before repair Review approval: restore the exact
  `0.1.0-draft` header and §9.2 source text, record the failed attempt, and keep
  the RC package blocked.
- After an approved repair has become binding: rollback requires a superseding FD
  under `change-control-policy.md` §13; the Ratified FD is not edited in place.

## §6. References

- `FOUNDATION/01-Constitution/constitution.md`.
- `FOUNDATION/02-Governance/change-control-policy.md` §§8, 12, 13.
- `FOUNDATION/03-Standards/release-specification.md` §9.2.
- `FOUNDATION/08-RFCs/FRFC-0002-reconcile-first-rc-prerequisites.md`.
- `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md`.
- `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md`.
- `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md`.
- `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md`.
- `VALIDATION/04-Validation-Report/REPORT-VALIDATION-03.md`.
- `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-03.md`.
- `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-03.md`.
- `FOUNDATION/04-Audits/AUDIT-FD-0005-implement-first-rc-prerequisite-repair.md`.
- `FOUNDATION/06-Reports/REPORT-FD-0005-implement-first-rc-prerequisite-repair.md`.
- `FOUNDATION/07-Reviews/REVIEW-FD-0005-implement-first-rc-prerequisite-repair.md`.

## §7. Approver

**Current status:** Ratified.

**Approver:** Human Architect (role-based).

**Signature:** Human Architect role-based approval recorded from the current
continuation instruction on 2026-08-04. No personal name, handwritten signature,
email address, or other identity data is fabricated.

**Ratification effect:** FD-0005 is binding authorization for the later controlled
patch cycle within §2 and §5 only.

## §8. Change Log

| Version | Date | Actor | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-08-04 | Research-OS Foundation Builder (Builder role) | Initial implementing-FD decision package. Status `Pending Ratification`; exact patch, target version, authority test, migration, rollback, and hard boundaries recorded. No patch applied. |
| 0.1.0-draft (ratification) | 2026-08-04 | Human Architect (role-based) | FD transitioned from `Pending Ratification` to `Ratified` through the current continuation instruction. Exact authorization accepted with Review disposition `Approved with Notes`. No patch, RC, Stage B, version advancement, git action, or publication occurred. |

---

*End of FD-0005 — Implement the First-RC Prerequisite Repair — Ratified, 2026-08-04.*
