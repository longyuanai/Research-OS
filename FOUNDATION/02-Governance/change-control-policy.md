# Change-Control Policy

**Status:** Draft / In Review
**Version:** 0.1.1-draft (Patched 2026-08-03 per FD-0002; Foundation Change Principle operationalized)
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/02-Governance/change-control-policy.md`
**Related:** `governance-model.md` (v0.1.1-draft, patched); `approval-workflow.md`; Constitution v0.1.0-draft §8, §12; FD-0002 (Ratified, 2026-08-03); FRFC-0001 (Approved, 2026-08-03).
**Last Patch:** 2026-08-03, Foundation Patch Cycle 01, per FD-0002 §7 (operational workflow, triggered Validation, exclusions, emergency handling, repair-vs-expansion, rollback).

---

## 1. Purpose

This document defines the **change-control policy** for Research-OS Foundation artifacts. It establishes the categories of change (patch, minor, major, breaking, emergency), the required workflows for each, and the rules that prevent silent normative drift.

**No silent normative change is permitted.** Every change to a normative artifact must be reflected in:

- An updated header (`Status:`, `Version:`, `Last Transition:`).
- A `CHANGELOG.md` entry.
- An FD, RFC, or ADR record (as appropriate).
- An updated version per SemVer (Constitution §8).

## 2. Change Categories

### 2.1  Patch changes

- **Definition.** Backward-compatible corrective change: typo fix, clarification, link repair, formatting.
- **Version bump.** PATCH (e.g., `0.1.0 → 0.1.1`).
- **Workflow.** Maintainer within FD-bounded scope, or Builder with Reviewer approval.
- **Required records.** `CHANGELOG.md` entry; updated header.
- **FD required?** No, unless the change touches an `active` Standard's normative content.

### 2.2  Minor changes

- **Definition.** Backward-compatible additive change: new section, new optional field, new example, new rule that does not invalidate existing rules.
- **Version bump.** MINOR (e.g., `0.1.0 → 0.2.0`).
- **Workflow.** FRFC + FD (Foundation-level) or PRFC + PD (Project-level).
- **Required records.** FRFC, FD, `CHANGELOG.md`, Audit, Review.
- **FD required?** Yes, for Foundation-level changes.

### 2.3  Major changes

- **Definition.** Breaking change to normative content. Existing consumers may need to update.
- **Version bump.** MAJOR (e.g., `0.1.0 → 1.0.0` or `1.0.0 → 2.0.0`).
- **Workflow.** FRFC + FD + Migration Plan + Ratification.
- **Required records.** FRFC, FD, Migration Plan, `CHANGELOG.md`, Audit, Review, supersession of prior version.
- **FD required?** Yes.
- **Constitution amendments** always qualify as Major changes.

### 2.4  Breaking changes

- **Definition.** A change that invalidates a previously valid consumer. Detected by:
  - Removal of a section, rule, or field.
  - Renaming of an artifact class or identifier.
  - Change in a Quality Gate criterion.
  - Change in cross-reference rules.
- **Version bump.** MAJOR.
- **Workflow.** Major change workflow (above).
- **Migration.** A Migration Plan is mandatory; the previous version enters `Migration Required` state (Constitution §12) for at least one Foundation minor version before being Archived.

### 2.5  Emergency corrections

- **Definition.** A correction that cannot wait for normal change-control cycles (security, data integrity, legal exposure).
- **Workflow.** Emergency FD (`EMERGENCY-FD-NNNN-<slug>.md`) + post-hoc normal FD within seven (7) calendar days.
- **Scope.** Limited to the immediate correction. No opportunistic changes permitted.
- **Exclusions.** Foundation Constitution amendments are never eligible for emergency change.

### 2.6  Constitution amendments

- **Definition.** Any change to the Constitution's normative content.
- **Workflow.** FRFC + FD with `amends-constitution: true` flag + MAJOR bump + Migration Plan.
- **Approval.** Architect only, with explicit ratification.
- **Supersession.** Prior Constitution version enters Archived.

### 2.7  Foundation changes

- **Definition.** Any change to Foundation-level artifacts (Constitution, FDs, Standards, RFCs, ADRs, Engines, SDKs, Plugins, Workspaces).
- **Workflow.** Depends on the artifact (see §2.1–§2.6).
- **FD required?** Yes, for any normative Foundation change beyond PATCH.

### 2.8  Project-local changes

- **Definition.** Changes confined to a single Project (e.g., a Sprint scope change, a Project-internal Standard).
- **Workflow.** PRFC + PD; no Foundation FD required, unless the change affects cross-Project interfaces.
- **Records.** Project `CHANGELOG.md`; PD record; PRFC record.

## 3. Migration Requirements

When a breaking change is introduced:

1. **Migration Plan.** The FD must include a Migration Plan as an appendix or referenced artifact.
2. **Migration Standard.** If the breaking change affects a Standard, a Migration Standard (`STD-<area>-MIG-vX.Y.Z.md`) must be published.
3. **Migration Required state.** The previous version enters `Migration Required` per Constitution §12.
4. **Migration window.** At least one Foundation minor version must elapse before the previous version is Archived.
5. **Consumer notification.** All known consumers must be notified via a Project RFC or a Project Decision, depending on scope.

## 4. Compatibility Review Requirements

Before any change is approved, a **Compatibility Review** must be performed and recorded in the FRFC or FD:

- Does the change preserve backward compatibility (Constitution §2.2)?
- Does it preserve forward compatibility where promised?
- Does it require migration per §3 above?
- Does it invalidate any active cross-references?
- Does it affect any Quality Gate criterion?
- Does it affect the Compatibility Policy (§2) itself?

A negative answer to any question triggers the appropriate workflow (Major change, Migration Plan, etc.).

## 5. Changelog Requirements

Every change to a normative Foundation artifact must be recorded in `CHANGELOG.md` under a versioned heading:

```
## [<Artifact> v<X.Y.Z>] — <YYYY-MM-DD>

### Added
- <new feature>

### Changed
- <behavior change>

### Deprecated
- <soon-to-be-removed feature>

### Removed
- <removed feature>

### Fixed
- <bug fix>

### Security
- <security fix>
```

The changelog entry must reference the FD or RFC that authorized the change.

## 6. Decision-Record Requirements

The following table summarizes which change categories require which decision records:

| Category | FD | FRFC / PRFC | ADR | Migration Plan | Audit | Review |
|---|---|---|---|---|---|---|
| Patch (non-normative) | optional | no | no | no | optional | yes |
| Minor (Foundation) | yes | yes (FRFC) | optional | no | yes | yes |
| Major (Foundation) | yes | yes (FRFC) | yes | yes | yes | yes |
| Constitution amendment | yes | yes (FRFC) | yes | yes | yes | yes |
| Emergency correction | yes (EMERGENCY-) | optional | no | optional | yes (post-hoc) | yes (post-hoc) |
| Project-local | no (PD only) | yes (PRFC) | optional | no | optional | yes |

## 7. Prohibited Silent Changes

The following are explicitly forbidden and constitute Hard Prohibitions (Constitution §15.3):

- Editing a `Ratified` or `Approved` artifact's content (rather than issuing a new superseding artifact).
- Removing a section without explicit amendment (§13 additive-only).
- Reverting a `Superseded` artifact to `Approved` without a new FD.
- Falsifying a version, status, or changelog entry.
- Bypassing the FRFC step by issuing an FD directly without proposal review.
- Auto-promoting an artifact to `Ratified` via AI without human approval.

Violations are Foundation-level incidents requiring a disposition FD.

## 8. Operational Workflow (Foundation Change Principle)

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 (Approved, 2026-08-03). Binding Foundation governance.**

### 8.1 Five-Step Workflow

The Foundation Change Principle (FRFC-0001 §4.1) is operationalized by the following five-step workflow. No new Foundation artifact may be introduced except by traversing all five steps in order. Each step produces a required record.

```
┌─────────────────────────┐
│  1. Validation Cycle    │
│  (gap discovered +      │
│   evidence captured)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. RFC Proposed        │
│  (FRFC/PRFC/RRFC per    │
│   rfc-policy.md)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. RFC Reviewed +      │
│     Approved            │
│  (Human Architect +     │
│   Reviewer)             │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  4. Implementing FD     │
│     Ratified            │
│  (per foundation-       │
│   decision-policy.md)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. Foundation Patched  │
│     Through Approved    │
│     Governance Process  │
│  (existing artifacts    │
│   only; Audit +         │
│   Report + Review)      │
└─────────────────────────┘
```

### 8.2 Step Records

Each step produces a required record:

| Step | Required Record(s) |
|---|---|
| 1. Validation Cycle | Evidence record (gap description, captured evidence, Foundation relevance assessment) |
| 2. RFC Proposed | FRFC / PRFC / RRFC per `rfc-policy.md` |
| 3. RFC Reviewed + Approved | Audit + Review records per `schema-standard.md` |
| 4. Implementing FD Ratified | FD per `foundation-decision-policy.md` |
| 5. Foundation Patched | `CHANGELOG.md` entry + Audit + Report + Review records; updated header |

### 8.3 Step 1 — Validation Cycle

A Validation Cycle is required before any RFC may be proposed. The cycle records the observed gap, captures evidence, determines Foundation relevance, and recommends whether an RFC is necessary. The cycle may be triggered by any of the eight Triggered Validation triggers (§9).

A trigger alone does not authorize a Foundation patch. The triggered Validation Cycle must still produce the required Step-1 evidence before any RFC may be proposed.

### 8.4 Step 2 — RFC Proposed

The RFC must conform to `rfc-policy.md` §4 (Required Header) and §6 (Required Sections). The RFC must reference the Validation Cycle evidence in its `Related:` field.

### 8.5 Step 3 — RFC Reviewed and Approved

Per `rfc-policy.md` §5 and `approval-workflow.md`, an RFC transitions through `Submitted → In Review → Approved`. The Reviewer produces a Review record per `schema-standard.md` §6. The Architect (Human) produces the final approval.

### 8.6 Step 4 — Implementing FD Ratified

Per FRFC-0001 §10 Step 6 and `approval-workflow.md`, RFC approval alone is not binding. The Principle becomes Foundation governance only upon the ratification of an implementing FD. The FD is the vehicle by which an approved RFC becomes binding Foundation governance.

### 8.7 Step 5 — Foundation Patched Through Approved Governance Process

The FD authorizes a patch of existing Foundation governance artifacts only. The patch is applied by editing existing artifacts (no new artifact class is introduced). The patch produces Audit + Report + Review records per `schema-standard.md`. The Review record has Disposition Pending human Architect until the human Architect reviews and approves the patch.

### 8.8 Idea Alone

Per FRFC-0001 §4.1, **idea alone is never sufficient to expand the Foundation**. An idea that has not traversed Steps 1–5 does not authorize any Foundation change, regardless of its source (Builder proposal, Reviewer recommendation, Architect directive, or external trigger).

## 9. Triggered Validation Definitions

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 §5.3.1. Binding Foundation governance.**

A Validation Cycle may be triggered by any of the following eight triggers. Each trigger names the condition and the required evidence form.

| # | Trigger | Condition | Required Evidence Form |
|---|---|---|---|
| 1 | **Scheduled cadence** | A periodic Foundation Validation Cycle is reached (per `validation-cycle-policy.md` if present; otherwise per Architect directive). | Date + cadence reference |
| 2 | **Project-triggered** | A Project (post-Foundation) reports a Foundation-relevant gap via PRFC or PD. | PRFC/PD reference + observed gap |
| 3 | **Implementation-triggered** | Builder or Maintainer observes a Foundation-relevant gap during declared-scope work. | Evidence record + declared scope reference |
| 4 | **Audit-triggered** | An Audit record identifies a Foundation-relevant finding. | Audit reference + finding citation |
| 5 | **Incident-triggered** | A Foundation-level incident is recorded (security, data integrity, legal). | Incident reference + severity assessment |
| 6 | **Security-triggered** | A security vulnerability or exposure is identified with Foundation implications. | Security report + impact assessment |
| 7 | **Compatibility-triggered** | A compatibility break or consumer-impacting change is identified. | Compatibility Review + consumer list |
| 8 | **Externally triggered** | A material external change occurs (legal, dependency, platform, operational). | External reference + Foundation impact assessment |

A trigger alone does not authorize a Foundation patch. The triggered Validation Cycle must still produce the Step-1 evidence (§8.3) and traverse Steps 2–5 before any patch may be applied.

## 10. Non-Architectural Maintenance Exclusions

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 §9.1. Binding Foundation governance.**

### 10.1 Excluded Record Classes

The following records do not count as Foundation architectural expansion when they are required by an existing authorized process and introduce no new authority or architecture:

- **E-1:** RFC proposal records (FRFC/PRFC/RRFC).
- **E-2:** Audit records.
- **E-3:** Report records.
- **E-4:** Review records.
- **E-5:** Evidence records.
- **E-6:** Authorized correction records.
- **E-7:** Status reconciliation records.

### 10.2 Exclusion Conditions

These exclusions apply **only when** the records do not change any of the following Foundation properties:

- Meaning.
- Authority.
- Scope.
- Behavior.
- Architecture.
- Compatibility.
- Permissions.
- Lifecycle.

If a record alters any of the above properties, it is Foundation expansion and requires the full Steps 1–5 workflow (§8).

### 10.3 Standing Controls

The standing scope, naming, and approval controls of `governance-model.md`, `change-control-policy.md`, `rfc-policy.md`, `schema-standard.md`, and `directory-standard.md` remain binding on all excluded records. No excluded record may claim authority outside its authorized scope.

## 11. Expedited Emergency Handling

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 §10.9. Binding Foundation governance.**

### 11.1 Emergency Conditions

Emergency conditions do not bypass evidence, review, or human authority. They permit an expedited application of the five-step workflow (§8), but every step still produces its required record.

### 11.2 Five-Step Expedited Application

The expedited application still produces:

1. **Evidence.** Abridged but sufficient evidence capturing the emergency condition.
2. **RFC or emergency change record.** Either an expedited RFC or an `EMERGENCY-FD-NNNN-<slug>.md` artifact per §2.5.
3. **Human approval.** Explicit Human Architect approval; no AI impersonation.
4. **Patch audit.** Post-hoc Audit record within seven (7) calendar days.
5. **Retrospective review.** A normal-cycle Review record within seven (7) calendar days.

### 11.3 No New Emergency Governance Artifact Class

No new emergency governance artifact class is created by FD-0002. The expedited application uses the existing `EMERGENCY-FD-NNNN-<slug>.md` mechanism (§2.5) only. Foundation Constitution amendments remain ineligible for emergency change (§2.5, §2.6).

## 12. Repair-vs-Expansion Rules

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 §4.1, §9.1. Binding Foundation governance.**

### 12.1 Non-Architectural Maintenance

A change that repairs, clarifies, or reconciles an existing Foundation artifact without altering its meaning, authority, scope, behavior, architecture, compatibility, permissions, or lifecycle is a **non-architectural maintenance** change and does not require an FRFC.

Examples of non-architectural maintenance include:

- Typo fix, formatting correction, or link repair.
- Header metadata update (`Status:`, `Version:`, `Last Transition:`).
- Status-consistency wording reconciliation across a cycle (when conditions of §12.3 are met).
- Cross-reference repair that does not change scope.
- `CHANGELOG.md` entry for an already-approved change.

### 12.2 Foundation Expansion

A change that alters any of the Foundation properties listed in §10.2 is **Foundation expansion** and requires the full Steps 1–5 workflow (§8), including an FRFC and a Ratified FD.

Examples of Foundation expansion include:

- Addition of a new section with new normative content.
- Removal of a section, rule, or field.
- Renaming of an artifact class or identifier.
- Change in a Quality Gate criterion.
- Change in cross-reference rules.
- Change in authority, scope, or permissions.

### 12.3 Status-Consistency Wording Reconciliation

A status-consistency wording reconciliation across a cycle (such as the reconciliation recorded for FRFC-0001 by Architect Decision, 2026-08-03, Part A Note N-1) is a permitted non-architectural maintenance change when it:

- (a) does not alter the RFC substance;
- (b) does not introduce or remove any artifact;
- (c) is documented in the audit trail of the cycle.

Any wording change that does not meet all three conditions is Foundation expansion and requires the full workflow.

### 12.4 Distinction in Practice

When in doubt, the Builder must classify the change as Foundation expansion and apply the full workflow. The classification is itself subject to Reviewer challenge per `approval-workflow.md`.

## 13. Rollback and Retrospective Review

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 §10. Binding Foundation governance.**

### 13.1 Rollback

Where a Foundation patch is applied under the Foundation Change Principle and is later found to introduce a defect or unintended consequence, the patch may be rolled back through a superseding FD. The superseding FD must:

- Reference the original FD that introduced the patch.
- Specify the rollback scope (full rollback, partial rollback, or supersession with replacement).
- Update the `CHANGELOG.md` to record the rollback.
- Produce a Review record with disposition.

### 13.2 Retrospective Review

Every patch applied under the Foundation Change Principle requires a **retrospective review** no later than the next Foundation Validation Cycle. The retrospective review:

- Confirms whether the patch achieved its stated objective.
- Records any defect, unintended consequence, or compatibility issue.
- Determines whether a superseding FD is required (rollback, refinement, or supersession).
- Is itself an Audit record per `schema-standard.md`.

## 14. Source of Binding Authority

This section (and §§8–13) derives its binding authority from:

- `FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md` (Approved, 2026-08-03 per Architect Decision, Part A).
- `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` (Ratified, 2026-08-03 per Architect Decision, Part B).
- `FOUNDATION/02-Governance/governance-model.md` §14 (binding Principle text).

---

*End of Change-Control Policy v0.1.1-draft (Patched per FD-0002, 2026-08-03).*
