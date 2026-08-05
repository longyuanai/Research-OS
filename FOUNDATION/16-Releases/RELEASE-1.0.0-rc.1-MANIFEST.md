---
id: RELEASE-1.0.0-rc.1
title: Research-OS Foundation 1.0.0-rc.1 (Applied; GitHub Pre-release Published)
artifact-type: Release
status: Applied
version: 1.0.0-rc.1
foundation-version: 0.1.0-dev
foundation-version-new: 1.0.0-rc.1
constitution-version: 0.1.0-draft
path: FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md
supersedes: none
superseded-by: none
release-type: rc
release-version: 1.0.0-rc.1
release-vendor: Research-OS Foundation
release-name: Research-OS Foundation 1.0.0-rc.1
release-description: First Foundation Release Candidate for Research-OS. Internally applied the Foundation version transition from 0.1.0-dev to 1.0.0-rc.1 on 2026-08-04, then externally published as a docs-first GitHub Pre-release under a separate Human Architect instruction on 2026-08-05. FD-0004 itself does not authorize external publication.
authorizing-fd: FD-0004-authorize-foundation-rc-1
manifest: MANIFEST-FOUNDATION-1.0.0-rc.1
release-manager: Foundation Release Manager (role-based; per roles-and-authority.md)
release-date: 2026-08-04
related-foundation-version: 0.1.0-dev
related-constitution-version: 0.1.0-draft
dependencies:
  - FD-0001-ratify-constitution
  - FD-0002-adopt-foundation-change-principle
  - FD-0003-approve-foundation-baseline
  - FD-0005-implement-first-rc-prerequisite-repair
  - FRFC-0001-foundation-change-principle
  - FRFC-0002-reconcile-first-rc-prerequisites
  - REVIEW-FOUNDATION-RELEASE-GATE-01
release-gate-authority: REVIEW-FOUNDATION-RELEASE-GATE-01 (Approved with Notes, 2026-08-04, Human Architect)
external-publication-status: github-pre-release-published
supersession: none
lifecycle-stage: Applied
last-transition: 2026-08-05 (separate external GitHub Pre-release publication; Foundation lifecycle remains Applied)
---

# Release — Research-OS Foundation 1.0.0-rc.1 (Applied; GitHub Pre-release Published)

## 0. Post-FD-0005 Repair Reconciliation — Pre-Application Snapshot

This section supersedes earlier current-state references in this Draft Manifest
to Release Specification `0.1.0-draft`, RC-2/RC-3 as invalid, and the former
2/3/2 accounting. Those earlier passages remain historical revision evidence.

- **Release Specification:** `0.2.0-draft`, repaired under Ratified FD-0005.
- **Active repair FD:** FD-0005 (Ratified) is included in the Release composition.
- **Repair evidence:** Audit PASS with Notes; Review Approved with Notes.
- **Condition state:** RC-1 and RC-3 satisfied; RC-2, RC-4, RC-5a, and RC-7
  ready for Human Approval; RC-5b and RC-6 require Stage B Application.
- **Accounting:** 8 accountable units = 2 satisfied + 4 ready + 2 application;
  0 blocked. EV-1 is evidence only.
- **Lifecycle at reconciliation:** Draft. No Foundation version advancement had occurred.

At this pre-application checkpoint, the Manifest was reconciled and ready for
Stage B Human Architect re-review. This snapshot is superseded by §0A.

## 0A. Stage B Application Record — Current Controlling State

**Human Architect disposition:** Approved with Notes, 2026-08-04.

**Authorizing FD:** FD-0004, Ratified.

**Application:** Applied internally on 2026-08-04.

**Atomic transition:**

- `FOUNDATION/VERSION`: `0.1.0-dev` → `1.0.0-rc.1`;
- Manifest lifecycle: Draft → Approved → Applied;
- Release Quality Gate Report:
  `FOUNDATION/06-Reports/REPORT-FOUNDATION-RELEASE-QUALITY-GATE-RC-1.md`;
- Release Manager application signature: role-based record under the current
  Human Architect authorization.

**Quality Gate:** PASS with Notes; 16/16 gates PASS; 0 blocking findings.

**External publication at the Stage B application checkpoint:** `not-published`.
No git tag, push, GitHub Release, registry publication, Pack, Workspace, Project,
APES, or implementation action had occurred at that checkpoint.

This section supersedes all earlier Draft/current-state notices for the internal
application lifecycle. Its publication-status sentence is later superseded by §0B
on `main`; the tagged copy intentionally preserves this pre-publication snapshot.

## 0B. Separate External Publication Record — Current Publication State on `main`

The Human Architect separately authorized external RC publication on 2026-08-05.
This authorization is independent of FD-0004 and does not change the internally
Applied Foundation composition or its 25-entry Manifest.

- **Repository:** `https://github.com/longyuanai/Research-OS` (Public).
- **Release:** `https://github.com/longyuanai/Research-OS/releases/tag/v1.0.0-rc.1`.
- **Release state:** non-draft GitHub Pre-release; published
  `2026-08-05T06:05:21Z`.
- **Annotated tag object:** `0a61aa1fc9b187618d16e8f4b901ce8fc7e98490`.
- **Tag target:** `139d455dc0f71525b88e010a566cf99b05740c6e`.
- **Tag contents:** sanitized Foundation baseline plus root Apache-2.0 `LICENSE`
  and `.gitattributes` publication metadata.
- **Publication boundary:** docs-first/no-runtime; no registry, Stable Release,
  Pack, Runtime, Workspace, Project, APES, or private data was published.

This §0B supersedes only current external-publication status. All Stage A and Stage B
passages remain timestamped historical evidence. Because this addendum was written
after publication, it exists on `main` and does not retroactively alter the immutable
tagged snapshot.

> **Historical Stage A status notice (superseded by §0A).** This Release instance was
> authored in **Draft** status at the Stage A Decision Package Preparation stage per
> `release-specification.md` §4.2. At that checkpoint it had not yet advanced, the
> Foundation Version remained `0.1.0-dev`, and Stage B was deferred to explicit Human
> Architect authorization. No git, tag, or external publication action was performed.

## 1. Purpose

This Release instance declares the **Research-OS Foundation 1.0.0-rc.1** Release
Candidate. Per `release-specification.md` §6.1 (MUST Contain) and §4.2 (Draft stage), it
records the Release's intended Contents, Manifest, Authorizing FD, target Foundation
Version, Release Manager, and pre-flight verification, and it serves as the canonical
Release instance to be advanced through the Release Lifecycle at Stage B.

This Release is the **first Foundation RC**. It is the first artifact that may advance
`FOUNDATION/VERSION` to a non-`dev` value, and it is the first Release of type `rc`
authorized under `release-specification.md` §5.4 (Foundation Phase binding). The Release
traverses the seven-stage Lifecycle in this order only: **Draft → Submitted → Under
Review → Approved → Applied → Superseded → Withdrawn** (§4).

## 2. Eligibility (Pre-conditions)

This Release's eligibility for transition to Submitted, Under Review, Approved, and
Applied is determined by the seven Release Decision Conditions (RC-1 through RC-7). Each
condition is mandatory; all seven must be satisfied before `FOUNDATION/VERSION` is
advanced. The conditions are enumerated and assessed in `FD-0004-authorize-foundation-rc-1.md`
§8 (RC-1 Through RC-7 Condition Matrix).

**Pre-flight eligibility checks completed at Stage A:**

- The Constitution is Ratified via FD-0001 (2026-08-03).
- The Foundation Change Principle is binding via FRFC-0001 and FD-0002 (2026-08-03).
- The Foundation baseline of 15 components is Collectively Approved via FD-0003
  (2026-08-04).
- The Foundation Release Gate Review Cycle 01 has been Dispositioned: **Approved with
  Notes** by Human Architect on 2026-08-04; Overall Verdict **RELEASE GATE PASS WITH
  CONDITIONS**; Blocking Finding Count: 0.

**Pre-flight eligibility checks (post-Stage A Governance Reconciliation, 2026-08-04):**

The seven Release Decision Conditions (RC-1 through RC-7) have been reclassified by the
Stage A Governance Reconciliation. The corrected classification is:

- **SATISFIED IN STAGE A** (2): RC-1 (Task 12 review approval — already issued via
  Baseline Review Approved with Notes, 2026-08-04); FD-0003 baseline authority
  verification (RC-3 satisfaction — collective approval binding).
- **READY FOR HUMAN APPROVAL** (3): RC-4 (Foundation Invariant release via FD-0004
  §10); RC-5a (FD-0004 declaration of `1.0.0-rc.1`); RC-7 (Hard Prohibitions release
  implicit in Stage B Human Architect authorization).
- **REQUIRES STAGE B APPLICATION** (2): RC-5b (atomic `FOUNDATION/VERSION` advancement
  at Applied stage); RC-6 (Manifest transition to Applied + Release Quality Gate Report
  production).
- **NOT A VALID CONDITION** (2): RC-2 (Constitution amendment to v1.0.0 — Release
  Specification §9.2 condition 1 is non-binding because the Release Specification is
  Draft / In Review, FD-0003 §3 #4 records "no Constitution amendment", Constitution
  §2.1 distinguishes three independent version surfaces, and Constitution §0 defers
  `-draft` suffix semantics); RC-3 (one Authorizing FD per Standard — Release
  Specification §9.2 condition 2 is non-binding because the Release Specification is
  Draft / In Review and FD-0003 §2 Alternatives explicitly rejected "One FD per
  Standard" as an alternative).
- **BLOCKED**: 0.

**Conditions satisfied at Stage A (post-Reconciliation):**

- The Constitution is Ratified via FD-0001 (2026-08-03); Constitution amendment is
  NOT required (RC-2 = NOT A VALID CONDITION).
- The Foundation Change Principle is binding via FRFC-0001 and FD-0002 (2026-08-03).
- The Foundation baseline of 15 components is Collectively Approved via FD-0003
  (Ratified 2026-08-04); per-Standard Authorizing FDs are NOT required (RC-3 = NOT A
  VALID CONDITION).
- Task 12 review approval has been issued via `REVIEW-FOUNDATION-BASELINE-01.md`
  (Approved with Notes, 2026-08-04, Human Architect); RC-1 is SATISFIED IN STAGE A.
- The Foundation Release Gate Review Cycle 01 has been Dispositioned: **Approved with
  Notes** by Human Architect on 2026-08-04; Overall Verdict **RELEASE GATE PASS WITH
  CONDITIONS**; Blocking Finding Count: 0.

**Conditions pending Stage B (Human Approval and Application):**

- RC-4. Explicit release of the Foundation Invariant 2026-08-03 by FD-0004 ratification
  (this Release's Authorizing FD per §7 below).
- RC-5a. Ratification of FD-0004 (this Release's Authorizing FD; declares
  `1.0.0-rc.1`).
- RC-5b. Atomic `FOUNDATION/VERSION` advancement at the Applied stage.
- RC-6. Production of this Release Manifest at the Applied stage and the Release Quality
  Gate Report.
- RC-7. Implicit release of the Hard Prohibitions of the current cycle by Stage B Human
  Architect authorization.

The seven Release Decision Conditions are **Release Decision Conditions**, not Release
Gate blockers. Two are SATISFIED IN STAGE A (RC-1, FD-0003 baseline authority); three
await Human Approval (RC-4, RC-5a, RC-7); two require Stage B Application (RC-5b,
RC-6). Two are NOT A VALID CONDITION (RC-2, RC-3). None is BLOCKED.

## 3. Version Impact

| Field | Value | Notes |
|---|---|---|
| `Foundation-Version` (before) | `0.1.0-dev` | current `FOUNDATION/VERSION` |
| `Foundation-Version-New` (after) | `1.0.0-rc.1` | target `FOUNDATION/VERSION` at Applied stage |
| `Constitution-Version` | `0.1.0-draft` (current and at Applied) | Constitution at Submission time is `0.1.0-draft`; amendment to `v1.0.0` is NOT a binding precondition for this RC (RC-2 = NOT A VALID CONDITION per Stage A Governance Reconciliation) |
| `Release-Type` | `rc` | per Constitution §8, `release-specification.md` §5.4 |
| `Release-Version` | `1.0.0-rc.1` | declared by this Release |
| Display / Tag Form (where applicable) | `v1.0.0-rc.1` | leading `v` reserved for display, git tags, release titles |

**Pre-flight evidence (recorded at Stage A):**

- Current `FOUNDATION/VERSION` contents captured: `0.1.0-dev` (single line; trailing
  newline preserved per file convention).
- Target `FOUNDATION/VERSION` contents confirmed: `1.0.0-rc.1` (single line; trailing
  newline; **no leading `v`** per Foundation Decision Policy and existing version-file
  convention).
- Trailing-newline requirement: confirmed.
- Leading `v` rule: confirmed (no leading `v` in `FOUNDATION/VERSION`; leading `v`
  reserved for display labels, git tags, release titles per the Architect Decision
  2026-08-04 Part B).

**Transition rule.** `FOUNDATION/VERSION` is modified **only** at the Applied stage of
Stage B (Human Approval and Application), atomically with the Release Manifest's
transition to `Applied` status and the Release Quality Gate Report production. The
advancement is atomic per `release-specification.md` §7.4. A partial advancement is a
**Boundary Violation** per §3.2.

## 4. Compatibility

### 4.1 Backward Compatibility

- This is the **first Foundation RC**. No prior stable Foundation release exists.
- No prior `1.0.0-*` release is superseded.
- Baseline component versions remain individually pinned at the versions enumerated in
  `FD-0003-authorize-foundation-baseline.md` §6.1, §6.2.
- No Workspace or Project migration is authorized.
- APES remains Paused.
- No Pack generation is authorized.

### 4.2 Forward Compatibility

Forward compatibility is not guaranteed. A consumer written against this Release may not
operate on later RCs or Stable Releases without checking the Release Notes and
Compatibility Profile of the later Release.

### 4.3 Migration Compatibility

No data migration is required (no prior stable Foundation release). Baseline component
version pinning is preserved; no version migration of any component occurs. No Project
(APES) migration is authorized.

### 4.4 Compatibility Statement (per Schema Standard §12.2)

**Compatibility Statement:** This Release is **technology-neutral and
project-independent** during the Foundation phase. The Release aggregates Foundation
Standards, Policies, Decisions, and Accepted RFCs; it does not instantiate any Pack,
Runtime, Engine, SDK, Plugin, Workspace, or Project. RC-level compatibility guarantees
apply; the Release is subject to change before the `1.0.0` Stable Release per
`release-specification.md` §6.4 (Composition Coherence) and the general RC semantics.

### 4.5 Compatibility Profile (per Release Specification §5.5)

- **Foundation versions:** compatible with `>= 1.0.0-rc.1` and `< next-Foundation-Major`.
- **Constitution versions:** SHALL NOT invoke clauses past `Constitution-Version` at
  Submission time (`0.1.0-draft`).
- **Plugin-SDK versions:** not applicable at Foundation phase.
- **Host platform versions:** technology-neutral; the Release declares the range of
  host platform versions it supports (technology-neutral per Schema Standard §1).
- **Downstream consumer versions:** the Release declares the range of downstream
  consumer versions that may consume this Release (post-Foundation; out of scope for
  Stage A).

## 5. Manifest (Release Composition per Release Specification §6.1 MUST Contain)

The Release instance MUST contain the items specified in `release-specification.md` §6.1
(MUST Contain list). Each item is identified and its source is canonical:

### 5.1 Constitution

- **Constitution** at declared Constitution-Version —
  `FOUNDATION/01-Constitution/constitution.md` (v0.1.0-draft, Ratified via FD-0001).

### 5.2 Every Foundation Standard (10)

Per `FD-0003-authorize-foundation-baseline.md` §6.2 and the Directory Standard §3.2:

| # | Path | Version |
|---|---|---|
| 1 | `FOUNDATION/03-Standards/directory-standard.md` | 0.1.0-draft |
| 2 | `FOUNDATION/03-Standards/schema-standard.md` | 0.1.0-draft |
| 3 | `FOUNDATION/03-Standards/pack-standard.md` | 0.1.0-draft |
| 4 | `FOUNDATION/03-Standards/runtime-specification.md` | 0.1.0-draft |
| 5 | `FOUNDATION/03-Standards/quality-gate-standard.md` | 0.1.0-draft |
| 6 | `FOUNDATION/03-Standards/engine-specification.md` | 0.1.0-draft |
| 7 | `FOUNDATION/03-Standards/sdk-specification.md` | 0.1.0-draft |
| 8 | `FOUNDATION/03-Standards/plugin-specification.md` | 0.1.0-draft |
| 9 | `FOUNDATION/03-Standards/workspace-specification.md` | 0.1.0-draft |
| 10 | `FOUNDATION/03-Standards/release-specification.md` | 0.2.0-draft |

### 5.3 Every Foundation Policy (5)

The five Governance documents serve as the Foundation Policy set per the Directory
Standard §3.2:

| # | Path | Version |
|---|---|---|
| 1 | `FOUNDATION/02-Governance/governance-model.md` | 0.1.1-draft |
| 2 | `FOUNDATION/02-Governance/roles-and-authority.md` | 0.1.0-draft |
| 3 | `FOUNDATION/02-Governance/approval-workflow.md` | 0.1.0-draft |
| 4 | `FOUNDATION/02-Governance/change-control-policy.md` | 0.1.1-draft |
| 5 | `FOUNDATION/02-Governance/disagreement-and-escalation.md` | 0.1.0-draft |

### 5.4 Every Active Foundation Decision (FD)

| # | ID | Status | Title |
|---|---|---|---|
| 1 | FD-0001 | Ratified (2026-08-03) | Ratify Constitution |
| 2 | FD-0002 | Ratified (2026-08-03) | Adopt Foundation Change Principle |
| 3 | FD-0003 | Ratified (2026-08-04) | Approve Foundation Baseline |
| 4 | FD-0004 | Ratified (2026-08-04) | Authorize Research-OS Foundation 1.0.0-rc.1 |
| 5 | FD-0005 | Ratified (2026-08-04) | Implement First-RC Prerequisite Repair |

### 5.5 Every Accepted Foundation RFC (FRFC)

| # | ID | Status | Title |
|---|---|---|---|
| 1 | FRFC-0001 | Approved | Foundation Change Principle |
| 2 | FRFC-0002 | Approved with Notes | Reconcile First-RC Prerequisites |

### 5.6 Every Accepted Release RFC (RRFC)

None at Stage A. RRFC records may be added in a future cycle per
`release-specification.md` §6.1 item 6.

### 5.7 Manifest of the Release

- **Manifest-ID:** MANIFEST-FOUNDATION-1.0.0-rc.1
- **Storage:** `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md` (this file).
- **Generated-At:** 2026-08-04 (Draft creation timestamp).
- **Entry-Count:** see §5.8 below.

### 5.8 Manifest Entries (per Schema Standard §8.4 Entry Sub-Structure)

| # | Path | Class | ID | Status | Version |
|---|---|---|---|---|---|
| 1 | `FOUNDATION/01-Constitution/constitution.md` | Standard | constitution | Ratified | 0.1.0-draft |
| 2 | `FOUNDATION/03-Standards/directory-standard.md` | Standard | STD-directory | In Review | 0.1.0-draft |
| 3 | `FOUNDATION/03-Standards/schema-standard.md` | Standard | STD-schema | In Review | 0.1.0-draft |
| 4 | `FOUNDATION/03-Standards/pack-standard.md` | Standard | STD-pack | In Review | 0.1.0-draft |
| 5 | `FOUNDATION/03-Standards/runtime-specification.md` | Standard | STD-runtime | In Review | 0.1.0-draft |
| 6 | `FOUNDATION/03-Standards/quality-gate-standard.md` | Standard | STD-quality-gate | In Review | 0.1.0-draft |
| 7 | `FOUNDATION/03-Standards/engine-specification.md` | Standard | STD-engine | In Review | 0.1.0-draft |
| 8 | `FOUNDATION/03-Standards/sdk-specification.md` | Standard | STD-sdk | In Review | 0.1.0-draft |
| 9 | `FOUNDATION/03-Standards/plugin-specification.md` | Standard | STD-plugin | In Review | 0.1.0-draft |
| 10 | `FOUNDATION/03-Standards/workspace-specification.md` | Standard | STD-workspace | In Review | 0.1.0-draft |
| 11 | `FOUNDATION/03-Standards/release-specification.md` | Standard | STD-release | In Review | 0.2.0-draft |
| 12 | `FOUNDATION/02-Governance/governance-model.md` | Standard | GOV-governance | In Review | 0.1.1-draft |
| 13 | `FOUNDATION/02-Governance/roles-and-authority.md` | Standard | GOV-roles | In Review | 0.1.0-draft |
| 14 | `FOUNDATION/02-Governance/approval-workflow.md` | Standard | GOV-approval | In Review | 0.1.0-draft |
| 15 | `FOUNDATION/02-Governance/change-control-policy.md` | Standard | GOV-change | In Review | 0.1.1-draft |
| 16 | `FOUNDATION/02-Governance/disagreement-and-escalation.md` | Standard | GOV-disagreement | In Review | 0.1.0-draft |
| 17 | `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md` | FD | FD-0001 | Ratified | (Ratified 2026-08-03) |
| 18 | `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` | FD | FD-0002 | Ratified | (Ratified 2026-08-03) |
| 19 | `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md` | FD | FD-0003 | Ratified | (Ratified 2026-08-04) |
| 20 | `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md` | FD | FD-0004 | Ratified | 0.1.0-draft |
| 21 | `FOUNDATION/09-Decisions/FD-0005-implement-first-rc-prerequisite-repair.md` | FD | FD-0005 | Ratified | 0.1.0-draft |
| 22 | `FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md` | FRFC | FRFC-0001 | Approved | (Approved 2026-08-03) |
| 23 | `FOUNDATION/08-RFCs/FRFC-0002-reconcile-first-rc-prerequisites.md` | FRFC | FRFC-0002 | Approved | (Approved 2026-08-04) |
| 24 | `FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md` | Release | RELEASE-1.0.0-rc.1 | Applied | 1.0.0-rc.1 |
| 25 | `FOUNDATION/06-Reports/REPORT-FOUNDATION-RELEASE-QUALITY-GATE-RC-1.md` | Report | REPORT-FOUNDATION-RELEASE-QUALITY-GATE-RC-1 | Approved | 1.0 |

**Entry-Count:** 25.

### 5.9 Release Manifest's Manifest (Schema Standard §8)

Per `schema-standard.md` §8 (Manifest Schema), this Release instance also serves as a
Manifest of itself (Recursive enumeration). The Manifest's required sections are
populated:

- §1 Purpose (this section).
- §2 Entries (entries table in §5.8).
- §3 Integrity (integrity section below).
- §4 References (references section below).

### 5.10 Integrity

- **Manifest-Digest:** not computed at Stage A Draft (computed at the Submitted stage
  per `release-specification.md` §5.2).
- **Hash strategy:** SHA-256 over the canonical text of §5.8 Entries table (technology-neutral
  binding; to be computed at the Submitted stage per Schema Standard §11.5 and Release
  Specification §5.2).
- **Signing notes:** no signature required at Stage A Draft; the Authorizing FD (FD-0004)
  carries the binding authority at Stage B.
- **Atomic-advancement clause:** the `FOUNDATION/VERSION` edit (Draft → Applied
  transition) is atomic with the Release Manifest's transition to `Applied` per
  `release-specification.md` §7.4.

### 5.11 Known Observations

- **O-RC-1.** All ten Standards and five Governance documents carry `Draft / In Review`
  header posture. Binding baseline authority derives from FD-0003 (Ratified 2026-08-04)
  §3 #2 for the exact versions enumerated in FD-0003 §6. Per-Standard Authorizing FDs
  are NOT required (RC-3 = NOT A VALID CONDITION per Stage A Governance
  Reconciliation: Release Specification §9.2 condition 2 is non-binding; FD-0003 §2
  Alternatives explicitly rejected "One FD per Standard").
- **O-RC-2.** Constitution amendment to `v1.0.0` is NOT a binding precondition
  (RC-2 = NOT A VALID CONDITION per Stage A Governance Reconciliation: Release
  Specification §9.2 condition 1 is non-binding; FD-0003 §3 #4 records "no
  Constitution amendment"; Constitution §2.1 distinguishes three independent version
  surfaces; Constitution §0 defers `-draft` suffix semantics to a future Maintenance
  RFC). The Constitution remains at v0.1.0-draft (Ratified via FD-0001) for the RC.
- **O-RC-3.** The first `rc` Release has no prior Foundation stable release to supersede.
  Composition Coherence (§6.4) is verified at the Applied stage.
- **O-RC-4.** No Pack, Runtime, Engine, SDK, Plugin, Workspace, or Project is instantiated
  by this Release. APES remains Paused.

## 6. Migration Plan

**Migration Plan:** not applicable at Stage A Draft. Per Schema Standard §12.2,
`Migration-Plan` is required when `Compatibility-Statement` declares a breaking change.
This Release declares **no breaking change** (no prior stable release to break); the
migration slot is recorded as "none required for first RC" per FD-0004 §15.

## 7. Authorizing FD

- **Authorizing-FD:** FD-0004-authorize-foundation-rc-1
- **Path:** `FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md`
- **Status at Stage A:** Pending (Stage A — Decision Package Preparation).
- **Required status at Applied stage:** Ratified (per Release Specification §7.2).
- **Approver:** Human Architect (role-based; no personal identity data fabricated).
- **Ratification mechanism:** Stage B (Human Approval and Application) per
  `approval-workflow.md` §5 and `foundation-decision-policy.md` §8.

## 8. Release Lifecycle Status

### 8.1 Current Lifecycle Stage

**Stage:** **1 (Draft)** per `release-specification.md` §4.2.

### 8.2 Stage Inputs and Outputs

Per `release-specification.md` §4.2 (Stage 1 — Draft):

**Inputs satisfied at Stage A:**

1. A list of Foundation artifacts proposed for inclusion (Standards, Policies, FDs,
   FRFCs) — enumerated in §5.2, §5.3, §5.4, §5.5.
2. The proposed target `Foundation-Version-New` — `1.0.0-rc.1` (a valid SemVer bump
   from `0.1.0-dev`).
3. The proposed Authorizing FD(s) — FD-0004 (Pending).

**Outputs produced at Stage A:**

1. This Release instance
   (`FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`) declaring the proposed
   Contents, Manifest, Authorizing FD, target Foundation Version, and Release Manager.

### 8.3 Transition Conditions (per Release Specification §4.2)

- **Structure Gate (`quality-gate-standard.md` §5.3.1):** to be evaluated at the
  Submitted stage.
- **Isolation Gate (§5.3.4):** to be evaluated at the Submitted stage.
- **Transition:** Draft → Submitted (per §4.3) at Stage B initiation by Human Architect
  with Release Manager signature.

### 8.4 Forbidden at Stage A

Per §4.2:

- Submission
- Review
- Approval
- Application
- FOUNDATION/VERSION advancement
- git operations
- external publication

### 8.5 Lifecycle Hooks Status (per Schema Standard §12.5)

| Transition | Hook | Status at Stage A |
|---|---|---|
| `Draft` → `Submitted` | Eligibility section verified; `FOUNDATION/VERSION` not yet changed. | Pending — eligibility section verified at Stage A; `FOUNDATION/VERSION` not changed. |
| `Submitted` → `Approved` | `Release-Date` set; `FOUNDATION/VERSION` updated to `Foundation-Version-New`; Manifest uploaded. | Pending — Stage B Applied stage. |
| `Approved` → `Superseded` | A later Release takes effect; `Superseded By:` populated. | Not applicable — first RC. |

## 9. Release Manager

- **Release Manager Role:** Foundation Release Manager (per `roles-and-authority.md`).
- **Delegation:** per `roles-and-authority.md` §5. **The Release Manager SHALL NOT
  delegate Approval of a Release of type `rc` or `ga`** per `release-specification.md`
  §7.3.
- **Identity:** role-based only; no personal name, handwritten signature, email
  address, or other identity data fabricated (per `governance-model.md` §5.3 and
  `roles-and-authority.md` §1).

## 10. References

### 10.1 Authorizing Instruments

- **FD-0004-authorize-foundation-rc-1** — Authorizing FD for this Release
  (`FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md`).
- **FD-0003-approve-foundation-baseline** — Approves the 15-component baseline
  enumerated in §5.2 and §5.3.
- **FD-0001-ratify-constitution** — Ratifies the Constitution.
- **FD-0002-adopt-foundation-change-principle** — Codifies the Foundation Change
  Principle.
- **FRFC-0001-foundation-change-principle** — Foundation Change Principle text.
- **REVIEW-FOUNDATION-RELEASE-GATE-01** — Approved with Notes (2026-08-04, Human
  Architect); Overall Verdict RELEASE GATE PASS WITH CONDITIONS; Blocking Finding
  Count: 0.

### 10.2 Binding Governance Documents

- **Constitution** v0.1.0-draft — `FOUNDATION/01-Constitution/constitution.md`.
- **Governance Model** v0.1.1-draft — `FOUNDATION/02-Governance/governance-model.md`.
- **Approval Workflow** v0.1.0-draft — `FOUNDATION/02-Governance/approval-workflow.md`.
- **Change-Control Policy** v0.1.1-draft — `FOUNDATION/02-Governance/change-control-policy.md`.
- **Foundation Decision Policy** v0.1.0-draft — `FOUNDATION/09-Decisions/foundation-decision-policy.md`.
- **Roles and Authority** v0.1.0-draft — `FOUNDATION/02-Governance/roles-and-authority.md`.

### 10.3 Binding Standards

- **Directory Standard** v0.1.0-draft — `FOUNDATION/03-Standards/directory-standard.md`
  (reserves `FOUNDATION/16-Releases/`).
- **Schema Standard** v0.1.0-draft — `FOUNDATION/03-Standards/schema-standard.md`
  (Release Schema §12; Manifest Schema §8).
- **Quality Gate Standard** v0.1.0-draft —
  `FOUNDATION/03-Standards/quality-gate-standard.md` (16 Quality Gates applied at
  Applied stage).
- **Release Specification** v0.1.0-draft — `FOUNDATION/03-Standards/release-specification.md`
  (the binding instrument for this Release).

### 10.4 Cross-Reference Targets

- Foundation Task table: `FOUNDATION/README.md` Task table.
- Foundation Changelog: `CHANGELOG.md`.
- Foundation Decision index: `FOUNDATION/09-Decisions/`.

## 11. Rollback Procedure

Per `release-specification.md` §7.4 and `change-control-policy.md` §13:

- A rollback is authorized by a separate Superseding FD (e.g., `FD-0005-rollback-rc-1`).
- The Superseding FD would atomically revert `FOUNDATION/VERSION` to `0.1.0-dev` and
  archive this Release Manifest.
- **The rollback procedure is not invoked at Stage A or Stage B Applied stage**; it is
  a future governance event recorded here for completeness and future use.

## 12. Supersession Procedure

Per `change-control-policy.md` §13 and `release-specification.md` §7.4:

- A successor Release (`1.0.0-rc.2`, `1.0.0-rc.3`, `1.0.0`, etc.) is authorized by a
  separate Superseding FD; FD-0004 is then marked `Superseded` in its `Status` field
  with `Superseded By` set to the new FD's identifier.
- This Release would be marked `Superseded` upon Application of a successor Release
  that declares this Release in its `Supersedes:` field.
- Retrospective review is scheduled at the next Foundation Validation Cycle.

## 13. Git and External-Publication Boundary

This Release does **not** authorize any of the following at Stage A or Stage B:

- `git add`, `git commit`, `git tag`, `git push`.
- GitHub Release creation.
- Package registry publication.
- Website publication.
- APES activation.

These are classified as **separate post-release-publication actions** requiring
**explicit authorization** by a separate Architect decision. None of them is performed
at Stage A.

## 14. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0-rc.1 (Draft) | 2026-08-04 | Foundation Release Builder | Initial Stage A Draft. Authored per Architect Decision 2026-08-04 Part B. Eligible for transition to Submitted at Stage B. All seven RC conditions (RC-1 through RC-7) Pending. Foundation Invariant 2026-08-03 preserved. `FOUNDATION/VERSION` unchanged at `0.1.0-dev`. Manifest entries enumerated per Schema Standard §8.4 (22 entries). Authorizing FD: FD-0004 (Pending). Lifecycle Stage: 1 (Draft). |

---

*End of Release — Research-OS Foundation 1.0.0-rc.1 (Stage A Draft) v1.0.0-rc.1.*
