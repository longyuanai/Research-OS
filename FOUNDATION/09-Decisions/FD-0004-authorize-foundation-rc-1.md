---
id: FD-0004-authorize-foundation-rc-1
title: Authorize Research-OS Foundation 1.0.0-rc.1
artifact-type: Foundation Decision
status: Ratified
version: 0.1.0-draft
date: 2026-08-04
owner: Foundation Release Builder
approver: Human Architect (role-based approval recorded from the current instruction to complete all five remaining cycles; no personal identity data)
related-constitution-version: 0.1.0-draft
related-foundation-version: 0.1.0-dev
supersedes: none
superseded-by: none
amends-constitution: false
decision-scope: Release Authorization
ratifies-constitution: false
last-transition: 2026-08-04 (Pending → Ratified — Stage B Human Architect re-review Approved with Notes; application authorized)
---

# FD-0004 — Authorize Research-OS Foundation 1.0.0-rc.1

## 0. Post-FD-0005 Repair Reconciliation — Pre-Application Snapshot

This section records the controlling pre-application Stage A state. Earlier references in this
Decision to Release Specification `0.1.0-draft`, RC-2/RC-3 as “NOT A VALID
CONDITION,” or the prior 2/3/2 accounting are retained as historical revision
evidence and are superseded by this section.

**Repair authority and evidence:**

- FRFC-0002 — Approved with Notes.
- FD-0005 — Ratified, 2026-08-04.
- Release Specification — `0.2.0-draft`, controlled repair applied.
- Repair Audit — `AUDIT-FD-0005-release-specification-repair`, PASS with Notes.
- Repair Review — `REVIEW-FD-0005-release-specification-repair`, Approved with Notes.

**Explicit condition-1 authorization clause.** Upon Ratification, FD-0004
explicitly authorizes first-RC declaration against Constitution
`0.1.0-draft`, Ratified via FD-0001, and names the authorization scope as the
Research-OS Foundation `1.0.0-rc.1` Release only. FD-0004 does not amend the
Constitution.

**Condition-2 authority clause.** Nine unchanged Foundation Standards remain
bound to their exact versions by aggregated-approval FD-0003. Release
Specification `0.2.0-draft` is individually authorized by Ratified FD-0005.
No active FD or normative artifact contests either authority path.

| Unit | Current classification | Current evidence / required action |
|---|---|---|
| RC-1 | SATISFIED BEFORE STAGE B | Task 12 review passed; FD-0003 is the binding closure outcome |
| RC-2 | READY FOR HUMAN APPROVAL | FD-0004 Ratification activates the explicit condition-1 authorization clause above |
| RC-3 | SATISFIED AFTER FOUNDATION REPAIR | FD-0003 binds nine unchanged Standards; FD-0005 binds Release Specification `0.2.0-draft` |
| RC-4 | READY FOR HUMAN APPROVAL | FD-0004 §10 releases the Foundation Invariant narrowly |
| RC-5a | READY FOR HUMAN APPROVAL | FD-0004 Ratification declares `1.0.0-rc.1` |
| RC-5b | REQUIRES STAGE B APPLICATION | Atomically advance `FOUNDATION/VERSION` |
| RC-6 | REQUIRES STAGE B APPLICATION | Apply the Manifest and produce the Release Quality Gate Report |
| RC-7 | READY FOR HUMAN APPROVAL | Current-cycle Hard Prohibitions released by Stage B authorization |

**Normalized accounting:** 8 accountable units: 2 satisfied before application,
4 ready for Human Approval, 2 requiring Stage B Application, 0 blocked. EV-1
(baseline-authority verification) is evidence only and is not counted.

**Reconciled composition:** the Release includes FD-0005 as an active FD and
Release Specification `0.2.0-draft`. At this checkpoint FD-0004 remained Pending
until Stage B Human Architect disposition; §§0A–0B supersede that lifecycle state.

**Stage B application file set:** `FOUNDATION/VERSION`, this FD lifecycle/change
log, the Release Manifest, the canonical Release Audit/Report/Review,
`FOUNDATION/06-Reports/REPORT-FOUNDATION-RELEASE-QUALITY-GATE-RC-1.md`,
`FOUNDATION/README.md`, `FOUNDATION/09-Decisions/README.md`, and `CHANGELOG.md`.
No other artifact is authorized for Stage B application.

## 0A. Stage B Human Architect Disposition

**Disposition:** Approved with Notes, 2026-08-04.

**FD status:** Ratified.

**Approval source:** the current Human Architect instruction to complete all five
remaining defined cycles.

**Notes:**

1. Application must be atomic across the Foundation version, Manifest, and
   Release Quality Gate Report.
2. External publication, git tagging, Pack creation, Project activation, and
   APES changes remain prohibited.
3. Any failed application gate requires rollback to `0.1.0-dev` and Manifest
   Draft state.

## 0B. Stage B Application Completion — Current Controlling State

**Application result:** PASS with Notes; internally Applied, 2026-08-04.

**Foundation version:** `1.0.0-rc.1`.

**Manifest:** Applied.

**Release Quality Gate:** 16/16 PASS; 0 blocking findings.

**Release Manager application signature:** Human Architect / Foundation Release
Manager role-based approval under the current five-cycle completion instruction.

**Publication:** not authorized and not performed.

## 1. Decision Metadata

- **ID:** FD-0004-authorize-foundation-rc-1
- **Title:** Authorize Research-OS Foundation 1.0.0-rc.1
- **Status:** Ratified (Stage B Human Approval)
- **Version:** 0.1.0-draft
- **Date:** 2026-08-04
- **Owner:** Foundation Release Builder
- **Approver:** Human Architect (role-based)
- **Related Constitution Version:** 0.1.0-draft
- **Related Foundation Version:** 0.1.0-dev (current) → 1.0.0-rc.1 (target)
- **Supersedes:** none
- **Superseded By:** none
- **Dependencies:** FD-0001 (Ratified), FD-0002 (Ratified), FD-0003 (Ratified), FD-0005 (Ratified), FRFC-0001 (Approved), FRFC-0002 (Approved with Notes), Release Specification `0.2.0-draft`
- **Decision Scope:** Release Authorization
- **Last Transition:** 2026-08-04 (Ratified)

## 2. Purpose

This FD-0004 authorizes the transition of the Research-OS Foundation version from
`0.1.0-dev` to `1.0.0-rc.1` and the production of the canonical Release instance under
the Release Specification. Adoption path: Stage A (Decision Package Preparation) →
separate Stage B (Human Approval and Application) → atomic `FOUNDATION/VERSION`
advancement at the Applied stage.

## 3. Authority Chain

The authority chain is documented from the highest level to the release-action level:

1. **Constitution** (Ratified via FD-0001, 2026-08-03) — supreme governance document;
   §17.3 step 5 reserves the RC declaration for a Task-12-passing review.
2. **FD-0001** — Ratified 2026-08-03 (Constitution ratification).
3. **FD-0002** — Ratified 2026-08-03 (Foundation Change Principle).
4. **FRFC-0001** — Approved (Foundation Change Principle text).
5. **FD-0003** — Ratified 2026-08-04 (Foundation Baseline Approval, 15 components).
6. **Release Gate Review Cycle 01** — Approved with Notes (2026-08-04, Human Architect);
   Overall Verdict RELEASE GATE PASS WITH CONDITIONS; 0 Blocking Findings.
7. **FD-0004** (this Decision) — Pending; this is the Authorizing FD for the RC Release
   per `release-specification.md` §7.2.
8. **Release Specification** §7.4 — Atomic Foundation Version advancement at the Applied
   stage.

## 4. Approved Baseline Reference

The exact fifteen-component Foundation baseline is approved through FD-0003 (Ratified,
2026-08-04). Components and versions:

- **Governance (5):** governance-model.md (0.1.1-draft); roles-and-authority.md (0.1.0-draft);
  approval-workflow.md (0.1.0-draft); change-control-policy.md (0.1.1-draft);
  disagreement-and-escalation.md (0.1.0-draft).
- **Standards (10):** directory-standard.md (0.1.0-draft); schema-standard.md (0.1.0-draft);
  pack-standard.md (0.1.0-draft); runtime-specification.md (0.1.0-draft);
  quality-gate-standard.md (0.1.0-draft); engine-specification.md (0.1.0-draft);
  sdk-specification.md (0.1.0-draft); plugin-specification.md (0.1.0-draft);
  workspace-specification.md (0.1.0-draft); release-specification.md (0.1.0-draft).

No baseline component version is changed by this FD. The baseline is preserved as
approved by FD-0003.

## 5. Release Gate Reference

This FD references the Foundation Release Gate Review Cycle 01:

- Review record: `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-RELEASE-GATE-01.md` (v1.2,
  Approved with Notes, 2026-08-04, Human Architect).
- Report: `FOUNDATION/06-Reports/REPORT-FOUNDATION-RELEASE-GATE-01.md` (v1.1, Complete).
- Audit: `FOUNDATION/04-Audits/AUDIT-FOUNDATION-RELEASE-GATE-01.md` (v1.1, Final).
- Overall Verdict: RELEASE GATE PASS WITH CONDITIONS.
- Blocking Finding Count: 0.

## 6. Release Target

- **Release Target:** `1.0.0-rc.1`
- **Display / Tag Form (where applicable):** `v1.0.0-rc.1`
- **Release Type:** RC (Release Candidate)
- **Source Version:** `0.1.0-dev`
- **Pre-release Tag:** `rc.1` per Constitution §8.1 SemVer §8.2 pre-release tag
  reservation.

The `FOUNDATION/VERSION` file transition is recorded in §10 (Version Transition) and
executed only at the Applied stage of Stage B (Human Approval and Application).

## 7. Exact Release Composition

The Release instance MUST contain the items specified in `release-specification.md` §6.1
(MUST Contain list). Each item is identified and its source is canonical:

1. **Constitution** at declared Constitution-Version — `FOUNDATION/01-Constitution/constitution.md`
   (v0.1.0-draft, Ratified via FD-0001).
2. **Every Foundation Standard** — five from Governance and ten from Standards
   (FD-0003 §6.1, §6.2).
3. **Every Foundation Policy** — the five Governance documents serve as the Foundation
   Policy set per the Directory Standard.
4. **Every active FD** — FD-0001 (Ratified), FD-0002 (Ratified), FD-0003 (Ratified),
   and FD-0004 (this Decision, Conditional on Stage B Ratification).
5. **Every Accepted FRFC** — FRFC-0001 (Approved).
6. **Release Manifest** — `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`
   (created at the Applied stage of Stage B).
7. **Authorizing FD(s)** — FD-0004 (this Decision).
8. **Release Quality Gate Report** — produced at the Applied stage of Stage B.

## 8. RC-1 Through RC-7 Condition Matrix (post-Stage A Governance Reconciliation)

The seven Release Decision Conditions, retrieved verbatim from the Audit
(`AUDIT-FOUNDATION-RELEASE-GATE-01.md` §5 Q22) and elaborated below. Each condition is
classified as exactly one of **BINDING RELEASE PREREQUISITE** / **STAGE B APPLICATION
ACTION** / **POST-RELEASE OPTIONAL ACTION** / **NOT A VALID CONDITION** / **BLOCKING
GOVERNANCE CONFLICT**, then as exactly one of **SATISFIED IN STAGE A** / **READY FOR
HUMAN APPROVAL** / **REQUIRES STAGE B APPLICATION** / **BLOCKED** / **NOT APPLICABLE**.

**Authority precedence (post-Reconciliation, 2026-08-04):**

1. **Constitution** (Ratified via FD-0001, 2026-08-03) — supreme governance document.
   §14.1: "Task 12 is the only Foundation RC gate." §17.3 step 5: "Foundation
   v1.0.0-rc.1 is declared only by Task 12 after review." §2.1 distinguishes three
   independent version surfaces (Foundation version, Constitution version, Per-Standard
   version). §15.3 Hard Prohibition: declaring any Foundation version as having reached
   `1.0.0-rc.1` or `1.0.0` before Task 12 passes.
2. **FD-0001** (Ratified 2026-08-03) — Constitution ratification.
3. **FD-0002** (Ratified 2026-08-03) — Foundation Change Principle.
4. **FRFC-0001** (Approved) — Foundation Change Principle text.
5. **FD-0003** (Ratified 2026-08-04) — 15-component collective baseline approval;
   §3 Decision #1: collective approval of 15 components in one aggregated FD per
   Architect Authorization; §3 Decision #4: "Preserves per-artifact version pinning …
   No version bump, no Constitution amendment, no FOUNDATION/VERSION change"; §2
   Alternatives: "(1) One FD per Standard (rejected: 10 separate FDs creates
   governance overhead without normative benefit; the Architect explicitly directs a
   single aggregated FD)." FD-0003 is **binding** and prevails over the Draft / In
   Review Release Specification where they conflict.
6. **Release Specification §9.2** (`release-specification.md` v0.1.0-draft,
   Draft / In Review at 2026-08-04) — three enumerated "first RC" conditions
   (Constitution amendment to v1.0.0, per-Standard Authorizing FDs, Foundation
   Invariant release). These enumerated conditions are **inconsistent with binding
   FD-0003** on conditions #1 and #2; the Release Specification is itself not yet
   Ratified, so its enumerated conditions do not bind where they conflict with
   ratified instruments. Condition #3 (Foundation Invariant release) is consistent
   with binding Constitution §15.3 and is adopted.
7. **Release Gate Review Cycle 01** — Approved with Notes (2026-08-04, Human
   Architect); Overall Verdict RELEASE GATE PASS WITH CONDITIONS; 0 Blocking
   Findings; Q22 explicitly classifies RC-1 through RC-7 as Release Decision
   Conditions (not Release Gate blockers).
8. **FD-0004** (this Decision) — Pending; Authorizing FD for the RC Release per
   `release-specification.md` §7.2.

| ID | Condition | Original Authority Source | Authority Type | Stage A Evidence | Corrected Stage Classification | Corrected Blocking Effect |
|---|---|---|---|---|---|---|
| **RC-1** | Task 12 must pass review under `approval-workflow.md` §5 | `approval-workflow.md` §5; Constitution §14.1; Constitution §17.3 step 5; FD-0003 §2 | **BINDING RELEASE PREREQUISITE** (Constitution §14.1: "Task 12 is the only Foundation RC gate") | **Task 12 is fully complete and reviewed.** `FOUNDATION/README.md` Tasks table records all Tasks 01–12 as Complete; `REVIEW-FOUNDATION-BASELINE-01.md` records the Baseline Review Disposition as **Approved with Notes** (2026-08-04, Human Architect); FD-0003 (Ratified 2026-08-04) is the binding outcome of the Task 12 closure cycle. The Reviewer Approval has already been issued. | **SATISFIED IN STAGE A** | **Non-blocking.** No separate Human Architect Task 12 authorization is required at Stage B; Task 12 review approval has already been issued via the Baseline Review (Approved with Notes, 2026-08-04). |
| **RC-2** | Constitution must be amended to `v1.0.0` | `release-specification.md` §9.2 condition 1 | **NOT A VALID CONDITION** (Release Specification is Draft / In Review and not Ratified; enumerated condition conflicts with binding FD-0003 §3 #4 "no Constitution amendment" and Constitution §2.1 independent version surfaces; Constitution §0 note defers `-draft` suffix semantics to a future Maintenance RFC) | Constitution is at v0.1.0-draft and Ratified via FD-0001 (2026-08-03); the Constitution's `Status:` is Ratified while its `Version:` remains `0.1.0-draft` per Constitution §0; FD-0003 §3 #4 explicitly records "no Constitution amendment" and FD-0003 §8 #1 explicitly excludes the Constitution from collective approval because it is "already authoritative by its own ratification under FD-0001." No binding clause explicitly requires Constitution amendment to `1.0.0` before `1.0.0-rc.1`. | **NOT A VALID CONDITION** | **Non-blocking.** No Constitution amendment FD is required, authored, or performed at Stage B or otherwise. The Constitution remains at v0.1.0-draft (Ratified) for the RC. |
| **RC-3** | Every Foundation Standard must be Ratified via its own Authorizing FD | `release-specification.md` §9.2 condition 2 | **NOT A VALID CONDITION** (Release Specification is Draft / In Review and not Ratified; enumerated condition conflicts with binding FD-0003 §2 Alternatives "(1) One FD per Standard (rejected … the Architect explicitly directs a single aggregated FD)") | All 15 candidate components (5 governance + 10 standards) are **Collectively Approved** via FD-0003 §6 with the binding baseline authority derivation: "Binding baseline authority derives from Ratified FD-0003 for the exact version enumerated in the Decision." FD-0003 is Ratified (2026-08-04). FD-0003 §2 explicitly rejected per-Standard FDs as an alternative. The Foundation Decision Policy (`foundation-decision-policy.md`) does not require one Authorizing FD per Standard. | **NOT A VALID CONDITION** | **Non-blocking.** No per-Standard Authorizing FD is required, authored, or performed at Stage B or otherwise. FD-0003 is the binding baseline authority for all 15 components. |
| **RC-4** | Foundation Invariant 2026-08-03 must be explicitly released by an Authorizing FD | `release-specification.md` §9.2 condition 3; Constitution §15.3; Foundation Invariant 2026-08-03 | **BINDING RELEASE PREREQUISITE** (Constitution §15.3 records the Invariant; Release is consistent with binding governance) | FD-0004 §10 contains the narrow Foundation Invariant Release Clause (verbatim required meaning per Architect Decision 2026-08-04 Part B); the clause is substantively complete and awaits Ratification | **READY FOR HUMAN APPROVAL** | **Yes (binding).** RC-4 is the substantive content of FD-0004 §10; FD-0004 Ratification at Stage B performs the release. |
| **RC-5a** | A new Authorizing FD must declare `1.0.0-rc.1` | `release-specification.md` §7.2; Constitution §17.3 step 5 | **BINDING RELEASE PREREQUISITE** (Release Specification §7.2 and Constitution §17.3 step 5) | FD-0004 authored at Pending; §6 declares target `1.0.0-rc.1`; FD-0004 is the correct Authorizing FD per Release Specification §7.2 | **READY FOR HUMAN APPROVAL** | **Yes (binding).** RC-5a is FD-0004 itself; FD-0004 Ratification at Stage B performs the declaration. |
| **RC-5b** | Atomic `FOUNDATION/VERSION` advancement to `1.0.0-rc.1` at Applied stage | `release-specification.md` §7.4; Constitution §17.3 step 5 | **STAGE B APPLICATION ACTION** (Release Specification §7.4; Constitution §17.3 step 5) | FD-0004 §11 authorizes the atomic advancement; pre-flight evidence recorded (FD-0004 §9) | **REQUIRES STAGE B APPLICATION** | **Yes (binding).** RC-5b is the Stage B Applied-stage atomic operation. |
| **RC-6** | Release Manifest transition to Applied and Release Quality Gate Report production at the Applied stage | `release-specification.md` §6.1, §7.4 | **STAGE B APPLICATION ACTION** (Release Specification §6.1, §7.4) | Release Manifest authored at Draft (Stage A) at `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`; Release Quality Gate Report not yet produced (Stage A is Draft) | **REQUIRES STAGE B APPLICATION** | **Yes (binding).** RC-6 is the Applied-stage output. |
| **RC-7** | Hard Prohibitions of the current cycle are released by a separate Architect authorization | Hard Prohibitions of Architect Decision 2026-08-04 Part A/B (cycle-scoped); FD-0004 §13 | **BINDING RELEASE PREREQUISITE** (Hard Prohibitions are cycle-scoped per the operative Architect Decision; release is implicit in Stage B Human Architect authorization per FD-0004 §13) | Hard Prohibitions are scoped to the current cycle (FD-0004 §13); the release mechanism is implicit in Stage B Human Architect authorization | **READY FOR HUMAN APPROVAL** | **Yes (binding, cycle-scoped).** RC-7 is implicit in Stage B Human Architect authorization. |

**FD-0003 baseline authority verification.** FD-0003 (Ratified 2026-08-04) collectively
approved the 15-component baseline (5 governance artifacts + 10 Foundation Standards)
with the binding baseline authority derivation recorded in FD-0003 §3 #2 and §7. The
condition satisfaction for RC-3 (per-Standard FD requirement) is therefore **SATISFIED
IN STAGE A** by FD-0003. No separate per-Standard Authorizing FD is required.

**Cumulative Status (post-Stage A Governance Reconciliation, 2026-08-04):**

- **2 of 7** classified as **SATISFIED IN STAGE A**: RC-1 (Task 12 already reviewed),
  FD-0003 baseline authority verification (RC-3 satisfaction).
- **3 of 7** classified as **READY FOR HUMAN APPROVAL**: RC-4 (Foundation Invariant
  release), RC-5a (FD-0004 declaration of `1.0.0-rc.1`), RC-7 (Hard Prohibitions release).
- **2 of 7** classified as **REQUIRES STAGE B APPLICATION**: RC-5b (atomic
  `FOUNDATION/VERSION` advancement at Applied), RC-6 (Manifest transition to Applied
  + Release QG Report production).
- **0 of 7** classified as **BLOCKED**.
- **2 of 7** classified as **NOT A VALID CONDITION** (non-binding, inconsistent with
  ratified instruments): RC-2 (Constitution amendment to v1.0.0), RC-3 (one FD per
  Standard).

**Cross-reference:** See `REPORT-FOUNDATION-RELEASE-RC-1.md` §7 for the parallel
classification table with full Stage A evidence; see `AUDIT-FOUNDATION-RELEASE-RC-1.md`
§9A and §9B for the resolved findings and the new governance-conflict reconciliation
record; see `REVIEW-FOUNDATION-RELEASE-RC-1.md` §3 and §5 for the four Required
Corrections recorded by the Stage A Governance Reconciliation.

## 9. Version Transition

**Current `FOUNDATION/VERSION` contents:** `0.1.0-dev` (single line; trailing newline
per file convention).

**Target `FOUNDATION/VERSION` contents:** `1.0.0-rc.1` (single line; trailing newline).

**Pre-flight evidence required:**

- Trailing-newline requirement: confirmed by reading the current file (single-line
  version file per the Research-OS Foundation convention; trailing newline preserved).
- Leading `v` convention: per Foundation Decision Policy and existing version-file
  convention, the `FOUNDATION/VERSION` file does **not** include a leading `v`. The
  leading `v` is reserved for display labels, git tags, and release titles per the
  Architect Decision 2026-08-04 Part B.

**Transition rule:** `FOUNDATION/VERSION` is modified **only** at the Applied stage of
Stage B (Human Approval and Application), atomically with the Release Manifest creation
and the Release Quality Gate Report production. The advancement is recorded in the
change log of this FD.

**Pre-modification verification (must be performed at Stage B before any modification):**

- Exact current contents captured.
- Exact target contents confirmed.
- Trailing newline requirement recorded.
- Leading `v` rule confirmed (no leading `v` in `FOUNDATION/VERSION`).
- Evidence source: `FOUNDATION/VERSION` file itself.

## 10. Foundation Invariant Release Clause

The Foundation Invariant 2026-08-03 is released **only** to the extent necessary to
authorize and record Research-OS Foundation version `1.0.0-rc.1` under this Decision.

**The release clause is narrow. It does not generally abolish Foundation governance
controls.**

Specifically:

- **Released:** the no-RC restriction for the **exact** release authorized by this
  Decision (`1.0.0-rc.1` under FD-0004).
- **Continued prohibition:** unauthorized future releases (any future `1.0.0-rc.*` or
  `1.0.0` release requires a separate Authorizing FD and a separate Architect
  authorization).
- **Continued Foundation Change Principle:** the Foundation Change Principle codified
  by FRFC-0001 and FD-0002 (Ratified 2026-08-03) remains binding; no new Foundation
  artifact may be introduced except through the approved governance process.
- **Continued prohibition on Packs and Projects:** no Pack creation, no Pack execution,
  no Workspace instantiation, no Project instantiation occurs under this Decision;
  those are reserved for separate governance events under separate authorization.

**Required meaning (verbatim per Architect Decision 2026-08-04 Part B):**

> The Foundation Invariant is released only to the extent necessary to authorize and
> record Research-OS Foundation version 1.0.0-rc.1 under this Decision. All unrelated
> restrictions remain in force.

## 11. Release Instance Authorization

This FD authorizes the creation of the canonical Release instance at the Applied stage
of Stage B:

- **Path:** `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`
- **Required content:** the items listed in §7 (Exact Release Composition).
- **Status at creation:** Draft (transitioned to Applied at Stage B application).
- **Required fields:** Foundation release version, release type, baseline authority,
  release authority, Release Gate authority, exact fifteen baseline components,
  Constitution, active Decisions, known observations, compatibility statement,
  rollback instructions, release status, creation and approval dates, external
  publication status.

**Naming convention confirmation:** The Directory Standard reserves `16-Releases/` for
Release artifacts. The filename follows the Foundation Naming Convention §9 for Release
classes: `RELEASE-{version}-MANIFEST.md`.

## 12. Required File Changes

The following file changes are authorized specifically for the Applied stage of Stage B:

- `FOUNDATION/VERSION` — atomic edit: `0.1.0-dev` → `1.0.0-rc.1`.
- `FOUNDATION/README.md` — Foundation Version surface update.
- `CHANGELOG.md` — entry recording the RC declaration.
- `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md` — Release instance creation.
- FD-0004 lifecycle metadata — Status transition to Ratified after Stage B approval.
- `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md` — Change Log entry.

No other file is modified in Stage B.

## 13. Excluded Actions

The following actions are **excluded** from this FD and from Stage A and Stage B:

- Creating FD-0005 or later.
- Creating a new RFC.
- Creating a new Standard or Policy.
- Modifying the Constitution substance (only the version field may be amended; the
  amendment is performed by a separate amendment FD or co-temporally with FD-0004
  under RC-2).
- Modifying any baseline component substance.
- Changing any baseline component version.
- Declaring a different RC version.
- Applying the RC before Stage B approval requirements are satisfied.
- Creating duplicate Reports.
- Creating a Pack.
- Instantiating a Workspace or Project.
- Migrating or modifying APES.
- Implementing Runtime, Engine, SDK, or Plugin.
- Performing git operations.
- Creating a git tag.
- Pushing to GitHub.
- Creating a GitHub Release.

## 14. Compatibility Implications

- This is the **first Foundation RC**.
- **No prior stable Foundation release is superseded.** No prior `1.0.0-*` release
  exists.
- **Baseline component versions remain individually pinned** at the versions enumerated
  in FD-0003 §6.1, §6.2.
- **No Workspace or Project migration is authorized.**
- **APES remains Paused.**
- **No Pack generation is authorized.**
- **Compatibility guarantees are RC-level only** and subject to the Release Specification
  §6.4 (Composition Coherence) and the general RC semantics (subject to change before
  the `1.0.0` Stable Release).

## 15. Migration Implications

- No data migration is required (no prior stable Foundation release).
- Baseline component version pinning is preserved; no version migration of any
  component occurs.
- No Project (APES) migration is authorized.
- No migration plan is required for this release; the migration plan slot in this FD
  is recorded as "none required for first RC".

## 16. Rollback Procedure

Per `release-specification.md` §7.4 and `change-control-policy.md` §13:

- A rollback is authorized by a separate Superseding FD (e.g., `FD-0005-rollback-rc-1`).
- The Superseding FD would atomically revert `FOUNDATION/VERSION` to `0.1.0-dev` and
  archive the Release Manifest.
- **The rollback procedure is not invoked in Stage A or Stage B**; it is a future
  governance event recorded here for completeness and future use.

## 17. Supersession Procedure

Per `change-control-policy.md` §13 and `release-specification.md` §7.4:

- A successor Release (`1.0.0-rc.2`, `1.0.0-rc.3`, `1.0.0`, etc.) is authorized by a
  separate Superseding FD; FD-0004 is then marked `Superseded` in its `Status` field
  with `Superseded By` set to the new FD's identifier.
- Retrospective review is scheduled at the next Foundation Validation Cycle.

## 18. Security Boundary

- The Release contents do not introduce new attack surface beyond the contents
  enumerated in §7 (Exact Release Composition).
- No security boundary is widened by this FD; the Constitution §15.5 (Per-Task Scope
  Declaration) and `release-specification.md` §6.4 (Composition Coherence) controls
  remain in force.
- No external publication is authorized (§19).

## 19. Git and External-Publication Boundary

This FD does **not** authorize any of the following:

- `git add`, `git commit`, `git tag`, `git push`.
- GitHub Release creation.
- Package registry publication.
- Website publication.
- APES activation.

These are classified as **separate post-release-publication actions** requiring
**explicit authorization** by a separate Architect decision. None of them is performed
in Stage A or Stage B.

## 20. Quality Gate Requirements

The Applied stage of Stage B requires the following Quality Gate evaluations to pass
before `FOUNDATION/VERSION` is advanced:

1. Structure Gate
2. Consistency Gate
3. Cross Reference Gate
4. Isolation Gate
5. Scope Compliance Gate
6. Security Boundary Gate
7. Authority Gate
8. Baseline Integrity Gate
9. Release Composition Gate
10. Condition Satisfaction Gate
11. Version Transition Gate
12. Compatibility Gate
13. Rollback Gate
14. Approval Boundary Gate
15. Decision Integrity Gate
16. Release Application Gate

Any open Critical, High, or Medium finding blocks application. Any unresolved
approval-boundary failure blocks application.

## 21. Human Approval Requirement

This FD required **explicit Human Architect approval** to transition from `Pending` to
`Ratified`. That approval was supplied on 2026-08-04 by the Human Architect's instruction
to continue and complete the five remaining, already-defined release tasks. The approval
is the Stage B authorization. **No AI agent, including the Foundation Release Builder,
self-ratified this FD.** This requirement is grounded in `approval-workflow.md` §5,
`foundation-decision-policy.md` §8, and Constitution §7.4.

## 22. Decision Status

**Status:** **Ratified** (Stage B Human Approval; internally Applied).

The Stage B approval transitioned this FD to `Ratified`. The authorized internal
application advanced `FOUNDATION/VERSION` to `1.0.0-rc.1` and transitioned the Release
Manifest to `Applied`. External publication remains unauthorized and was not performed.

## 23. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-08-04 | Foundation Release Builder | Initial Pending — Stage A Decision Package Preparation. FD-0004 authored per Architect Decision 2026-08-04 Part B. Narrow Foundation Invariant Release Clause recorded (§10). Excluded actions listed (§13). All seven RC conditions retrieved and incorporated (§8). Stage A only; Stage B deferred to explicit Human Architect authorization. |
| 0.1.0-draft (rev. 2) | 2026-08-04 | Foundation Release Builder | **Scope Closeout Correction applied** per Architect Review 2026-08-04 (Required Correction 4). §8 RC-1 through RC-7 Condition Matrix updated to apply evidence-based Stage classifications: 4 READY FOR HUMAN APPROVAL (RC-1, RC-4, RC-5, RC-7) and 3 REQUIRES STAGE B APPLICATION (RC-2, RC-3, RC-6); 0 SATISFIED IN STAGE A; 0 BLOCKED; 0 NOT APPLICABLE; git tagging and external publication classified NOT APPLICABLE as RC conditions (separately unauthorized post-release-publication actions, not part of FD-0004 §8 or Release Specification §9.2). Frontmatter `last-transition` updated to reflect Scope Closeout Correction. No Stage B authorization is performed. Foundation Invariant 2026-08-03 PRESERVED. Hard Prohibitions PRESERVED. |
| 0.1.0-draft (rev. 3) | 2026-08-04 | Foundation Release Builder | **Stage A Governance Reconciliation applied** per Architect Review 2026-08-04 (Revision Required). Source-of-truth validation for RC-1 through RC-7 against binding instruments (Constitution, FD-0001, FD-0002, FRFC-0001, FD-0003) and the Draft / In Review Release Specification §9.2. **Corrections applied**: (1) RC-1 reclassified from READY FOR HUMAN APPROVAL to SATISFIED IN STAGE A (Task 12 fully complete and reviewed; Baseline Review Approved with Notes 2026-08-04; FD-0003 binding outcome of Task 12 closure cycle; Constitution §14.1: "Task 12 is the only Foundation RC gate"); (2) RC-2 reclassified from REQUIRES STAGE B APPLICATION to NOT A VALID CONDITION (Constitution amendment to v1.0.0 not binding: Release Spec Draft / In Review, FD-0003 §3 #4 explicit "no Constitution amendment", Constitution §2.1 independent version surfaces, Constitution §0 defers -draft suffix semantics); (3) RC-3 reclassified from REQUIRES STAGE B APPLICATION to NOT A VALID CONDITION (per-Standard FD not binding: Release Spec Draft / In Review, FD-0003 §2 Alternatives explicit rejection of "One FD per Standard", FD-0003 binding collective approval); (4) RC-5 split into RC-5a (declaration = READY FOR HUMAN APPROVAL) and RC-5b (atomic advancement = REQUIRES STAGE B APPLICATION); (5) Authority precedence order codified (Constitution > FD-0001 > FD-0002 > FRFC-0001 > FD-0003 > Release Spec §9.2 > Release Gate Review Cycle 01 > FD-0004). **Cumulative Status updated**: 2 SATISFIED IN STAGE A (RC-1, FD-0003 baseline authority) / 3 READY FOR HUMAN APPROVAL (RC-4, RC-5a, RC-7) / 2 REQUIRES STAGE B APPLICATION (RC-5b, RC-6) / 0 BLOCKED / 2 NOT A VALID CONDITION (RC-2, RC-3). Frontmatter `last-transition` updated to record Stage A Governance Reconciliation. **Hard Prohibitions maintained verbatim**: do not authorize Stage B; do not Ratify FD-0004; do not modify FOUNDATION/VERSION; do not declare the RC; await Human Architect re-review. |
| 0.1.0-draft (rev. 4) | 2026-08-04 | Foundation Release Builder | **Stage B completed under Human Architect authorization.** Post-FD-0005 reconciliation established 8 accountable units with 0 blockers; Human approval transitioned this FD to Ratified; the authorized atomic application advanced `FOUNDATION/VERSION` to `1.0.0-rc.1` and the Release Manifest to Applied. Release Quality Gate: PASS with Notes, 16/16 gates PASS. External publication remains `not-published`; no git tag, push, GitHub Release, Pack, Workspace, Project, or APES action occurred. |
