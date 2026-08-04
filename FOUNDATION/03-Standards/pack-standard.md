# Research-OS Foundation — Builder Pack Standard

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/03-Standards/pack-standard.md`
**Supersedes:** none
**Related:** Constitution v0.1.0-draft (Provisional) §1, §2, §3, §4, §6, §9, §10, §11, §13, §14, §15; `FOUNDATION/02-Governance/governance-model.md` §6, §7; `FOUNDATION/02-Governance/approval-workflow.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/02-Governance/disagreement-and-escalation.md`; `FOUNDATION/02-Governance/roles-and-authority.md`; `FOUNDATION/03-Standards/directory-standard.md`; `FOUNDATION/03-Standards/schema-standard.md` §11 Pack Schema; `FOUNDATION/08-RFCs/rfc-policy.md`; `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/10-ADRs/adr-policy.md`

---

## 1. Purpose and Scope

This Builder Pack Standard defines the **canonical shape, content, lifecycle, and quality criteria** of a *Builder Pack* — the L5 unit by which a Foundation Project bundles a coherent set of Foundation artifacts (Standards, Decisions, Missions, Programs, Tasks, Deliverables, Audit/Review/Report records) for execution under the Foundation Task Protocol.

A Pack is the bridge between **declarative governance** (Constitution, Standards, FDs) and **operational execution** (a Mission run by a Future Builder). This Standard is the L3 Foundation Standard that operationalizes Constitution §4 (Lifecycle Model) and §15 (Foundation Task Protocol) for the Pack concept.

**Scope.** This Standard governs:

1. The Pack definition (what a Pack is, what it is not).
2. The Pack lifecycle (status transitions, immutability, supersession).
3. The Pack structure (directory tree, manifest, content placement).
4. The Pack manifest rules (the Manifest schema a Pack must instantiate).
5. The Mission specification (what a Mission is, what it must declare).
6. The Program specification (how a Pack may decompose a Mission into Programs).
7. The Task specification (how a Pack may decompose a Program into Tasks).
8. The Deliverable specification (what a Task produces, how it is verified).
9. Pack Audit requirement (Audit Hooks a Pack must declare).
10. Pack Review requirement (Review Hooks a Pack must declare).
11. Pack Report requirement (Report Hooks a Pack must declare).
12. Artifact management (the artifacts a Pack may bundle, where they live).
13. Pack dependency rules (the constraints on Pack-on-Pack references).
14. Pack versioning rules (how a Pack version is assigned, when it bumps).
15. The Pack Quality Gate (the four §11 hooks applied to a Pack as a whole).

**Out of scope.**

- **Concrete Pack instances.** This Standard does **not** create a `PACK-00-foundation-pack.md`, a `PACK-01-*.md`, or any other Pack artifact. It defines the *form* a Pack must take; the first Foundation Pack is a Task 12 deliverable.
- **Mission execution.** A Pack describes a Mission; it does not run one. The Builder Runtime (Task 06) is the L5 component that *interprets* a Pack; the Builder Pack Standard does not.
- **Concrete serialization / Engine / SDK / Plugin / Workspace.** This Standard is **technology-neutral**. No Engine binding, no runtime binding, no SDK binding, no language binding, no serialization binding.
- **Project-specific Pack instances.** APES, or any other Project, may issue a Pack conforming to this Standard — but **no Project-specific Pack is created in Task 05**.
- **Foundation-version bump.** A Pack is **not** the same as a Release (§12 Release Schema). A Pack aligns with a `Foundation Version`; it does not change it.

## 2. Normative Status

This Builder Pack Standard is **Draft / In Review** at Foundation `0.1.0-dev`, Constitution `v0.1.0-draft` (Provisional). It is the L3 Foundation Standard that operationalizes the **Pack Schema** declared in `schema-standard.md` §11.

**Conformance.** A future Builder Pack is conformant with this Standard if and only if:

- It instantiates the `Pack Schema` declared in `schema-standard.md` §11, AND
- It satisfies every requirement in §4–§15 of this Standard, AND
- Its enclosed artifacts (Standards, Manifests, Audits, Reviews, Reports, Evidence, Decisions, RFCs, ADRs) conform to the Foundation artifact schemas declared in `schema-standard.md` §4–§12, AND
- It is bundled under the storage declaration declared in §3 below.

**Conflict resolution.** Per `governance-model.md` §4:

1. Constitution prevails.
2. Higher `Status:` prevails.
3. Later SemVer version prevails.
4. Later ISO-8601 date prevails.
5. Higher-numbered ID prevails.
6. Otherwise escalate.

Where this Standard and the Constitution appear to conflict, the Constitution prevails. Where this Standard and an active FD appear to conflict, the FD prevails if its `Status:` is `Ratified`; otherwise this Standard governs provisionally.

**Technology neutrality.** This Standard does not bind the Foundation to any Engine, Runtime, SDK, Plugin, Workspace, serialization format, or schema-engine. A consumer (Builder Runtime, Engine, Validator) claims conformance by demonstrating that for every requirement in §4–§15, the same field set, required-set, optional-set, and validation rules are enforced. The mapping between Pack requirements and a concrete execution is the consumer's responsibility (and is itself a Task 06 deliverable).

## 3. Pack Definition

### 3.1  Definition

A **Builder Pack** (hereafter "Pack") is a Foundation artifact that:

- Declares a single, coherent **Mission** (a goal bounded by success criteria and exit conditions).
- Optionally decomposes the Mission into one or more **Programs** (logical groupings of work).
- Optionally decomposes each Program into one or more **Tasks** (a single cycle of work under the Foundation Task Protocol — Constitution §15).
- Bundles the **Deliverables**, **Audit Records**, **Review Records**, and **Reports** produced by the execution of its Tasks.
- Bundles the **Standards**, **Manifests**, **Evidence**, **Decisions**, **RFCs**, and **ADRs** that the Mission depends on.
- Is **immutable** once the Pack enters `Approved` status (§4) — corrections are made by issuing a new Pack version, not by editing the original.
- Carries a single `Pack-ID` and a single `Version` (SemVer per Constitution §8).

### 3.2  What a Pack is NOT

A Pack is **not**:

- A Release. A Pack does not move `FOUNDATION/VERSION`. (`foundation-decision-policy.md` and `schema-standard.md` §12 govern Release semantics.)
- A Project. A Pack may be issued by a Project; it does not *constitute* a Project. (Project subtree is governed by `directory-standard.md` §6.)
- Code, an Engine, a Runtime, an SDK, a Plugin, or a Workspace. A Pack declares *what* is to be done; the *how* is a separate L5 specification.
- Mutable post-Approval. A Pack may be superseded by a later Pack; it may not be edited in place (`governance-model.md` §8 immutability rule).

### 3.3  Pack Identification

A Pack is identified by:

- `Pack-ID` — kebab-case identifier; matches the pattern `PACK-<scope>-<slug>` (see `schema-standard.md` §11.1).
- `Version` — SemVer per Constitution §8.
- `Pack-Type` — one of `Standard`, `Decision`, `Release`, `Tool` (per `schema-standard.md` §11.2). For Foundation work, the typical `Pack-Type` is `Standard` (a Pack that bundles a Standard and its companion Audit/Report/Review records) or `Decision` (a Pack that bundles a Foundation Decision and its supporting evidence).

### 3.4  Pack Scope

A Pack's `Scope` declares which Foundation level the Pack binds to:

- `FOUNDATION` — the Pack is normative at the Foundation level (post-`v1.0.0-rc.1`).
- `PROJECT-<code>` — the Pack is normative at the Project level (post-Foundation).
- `MISSION-<id>` — the Pack is bound to a single Mission (the most common form for execution-focused Packs).

## 4. Pack Lifecycle

The Pack lifecycle aligns with the Governance Status Lifecycle (`governance-model.md` §7) and the Pack Schema's Lifecycle Hooks (`schema-standard.md` §11.6).

### 4.1  Status Sequence

A Pack transitions through the following statuses, in order:

| # | Status | Set By | Next Statuses |
|---|---|---|---|
| 1 | `Draft` | Author | `Submitted`, `Withdrawn` |
| 2 | `Submitted` | Author | `In Review`, `Changes Requested`, `Withdrawn` |
| 3 | `In Review` | Reviewer | `Approved`, `Changes Requested`, `Rejected` |
| 4 | `Changes Requested` | Reviewer | `Submitted` (resubmission), `Withdrawn` |
| 5 | `Approved` | Reviewer | `Superseded`, `Archived` |
| 6 | `Superseded` | Architect (via FD) | `Archived` |
| 7 | `Archived` | Architect | (terminal) |
| 8 | `Rejected` | Reviewer / Architect | (terminal) |
| 9 | `Withdrawn` | Author | (terminal) |

A Pack **may not** be assigned `Ratified` status. Ratification is reserved for the Constitution and for FDs (`governance-model.md` §7). A Pack that aspires to bind at Foundation level must be elevated to a Foundation Decision via an FD.

### 4.2  Immutability on Approved

Once a Pack enters `Approved` status, its content is **immutable** (`governance-model.md` §8). The following actions are forbidden on an `Approved` Pack:

- Editing any field in the Pack Manifest.
- Adding, removing, or replacing any bundled artifact.
- Changing the `Hash` of the Pack or any of its contents.
- Changing the `Version`.
- Reassigning the `Status:`.

The only permitted transition out of `Approved` is `Superseded` (via a new Pack version) or `Archived` (via an FD).

### 4.3  Supersession

A Pack may be superseded by a later Pack. The supersession follows the rules in `governance-model.md` §9:

1. The new Pack declares `Supersedes: <old-Pack-ID>` in its header.
2. The old Pack's `Status:` is updated to `Superseded` (header-only edit; content untouched).
3. The old Pack's `Superseded By:` header field is populated with the new Pack's ID.

### 4.4  Lifecycle Hooks

The Pack Schema (`schema-standard.md` §11.6) declares the normative lifecycle hooks. A Pack that transitions between statuses without performing the corresponding hooks is **Invalid**.

| Transition | Required Hook |
|---|---|
| `Draft` → `Submitted` | All `Contents` populated; `Hash` computed (per §14.3 versioning). |
| `Submitted` → `Approved` | `Approved-By` and `Approved-At` set; optional signing note; manifests sealed. |
| `Approved` → `Superseded` | A new Pack with `Supersedes: <old-Pack-ID>` is created; the old Pack's header line is updated. |
| `Approved` → `Archived` | An FD directs the archive; the artifact is retained per `governance-model.md` §8. |

## 5. Pack Structure

### 5.1  Top-Level Files

A Pack is a **directory** with the following mandatory layout:

```
<pack-root>/
├── MANIFEST-<pack-id>.md             ← required (per §6)
├── CONTENTS-<pack-id>.md            ← required (per §6.4) — human-readable contents
├── PACK-<pack-id>.md                  ← required (the Pack header block per Schema §11)
├── README-<pack-id>.md              ← optional — human-readable introduction
├── standards/                        ← required iff Pack bundles one or more Standards
│   └── <standard-files>.md
├── decisions/                        ← required iff Pack bundles one or more FDs
│   └── <fd-files>.md
├── rfc/                              ← required iff Pack bundles one or more RFCs
│   └── <rfc-files>.md
├── adr/                              ← required iff Pack bundles one or more ADRs
│   └── <adr-files>.md
├── manifests/                        ← required iff Pack bundles Manifests
│   └── <manifest-files>.md
├── missions/                         ← required iff Pack is Mission-bundling
│   └── <mission-files>.md
├── programs/                         ← required iff Pack bundles Programs
│   └── <program-files>.md
├── tasks/                            ← required iff Pack bundles Tasks
│   └── <task-files>.md
├── deliverables/                     ← required iff Pack declares Deliverables
│   └── <deliverable-files>.md
├── audits/                           ← required iff Pack bundles Audits
│   └── <audit-files>.md
├── reviews/                          ← required iff Pack bundles Reviews
│   └── <review-files>.md
├── reports/                          ← required iff Pack bundles Reports
│   └── <report-files>.md
├── evidence/                         ← required iff Pack bundles Evidence
│   └── <evidence-files>.md
└── stats/                            ← required iff Pack bundles Statistics
    └── <stats-files>.md
```

A Pack directory MUST contain at least one of: `standards/`, `decisions/`, `rfc/`, `adr/`, or `missions/`. A Pack that bundles none of these is **Invalid**.

### 5.2  Optional Sub-Structures

A Pack may additionally contain:

- `examples/` — example instances illustrating the Pack's schema. Subject to `governance-model.md` §11.4 (Isolation).
- `migrations/` — migration plans for backward-incompatible Pack supersession (per §14.4).
- `signatures/` — signing artifacts (technology-neutral format).

### 5.3  Storage and Identity

The Foundation does **not yet** reserve a `FOUNDATION/16-Releases/` directory; Packs created during the Foundation phase are stored alongside the corresponding `Mission` / `Decision` / `Standard` they bundle, **or** under a project-declared directory. The first `FOUNDATION/16-Releases/` directory will be created at Task 12.

A Pack's full path is:

```
<pack-root>/   (the directory containing MANIFEST-<pack-id>.md)
```

The Pack's `Path` header field MUST equal the canonical relative path of the `MANIFEST-<pack-id>.md` file (per `schema-standard.md` §11.2).

### 5.4  Pack Headers

Every Pack-level file (`MANIFEST-<pack-id>.md`, `CONTENTS-<pack-id>.md`, `PACK-<pack-id>.md`, `README-<pack-id>.md`) MUST carry the six standard header fields defined in `schema-standard.md` §3.2 and the Pack-specific fields in `schema-standard.md` §11.2.

## 6. Pack Manifest Rules

### 6.1  Manifest Schema

A Pack's Manifest conforms to the `Manifest Schema` (`schema-standard.md` §8). The Manifest is the **authoritative** enumeration of the Pack's contents; any artifact present in the Pack directory but absent from the Manifest is **Invalid**; any artifact listed in the Manifest but absent from the Pack directory is **Invalid**.

### 6.2  Required Manifest Fields

The Manifest MUST declare:

| Field | Required | Source |
|---|---|---|
| `Status` | R | `schema-standard.md` §8.2 |
| `Version` | R | `schema-standard.md` §8.2 |
| `Foundation Version` | R | `schema-standard.md` §8.2 |
| `Path` | R | `schema-standard.md` §8.2 |
| `Supersedes` | R | `schema-standard.md` §8.2; `none` for the first version |
| `Related` | R | `schema-standard.md` §8.2; must include the Pack ID |
| `Collection` | R | `schema-standard.md` §8.2; equals the Pack ID |
| `Generated-At` | R | `schema-standard.md` §8.2; ISO-8601 timestamp |
| `Entry-Count` | R | `schema-standard.md` §8.2; equals `len(Entries)` |
| `Hash` | O | `schema-standard.md` §8.2; recommended |

### 6.3  Required Manifest Sections

The Manifest MUST contain the four sections declared in `schema-standard.md` §8.3: Purpose, Entries, Integrity, References.

### 6.4  Contents Document

A Pack MUST also include a `CONTENTS-<pack-id>.md` file that is a **human-readable** rendering of the Manifest. The Contents document is **not** a substitute for the Manifest; it is a companion that lists the same artifacts in the same order, with a one-line description of each entry. The Contents document carries the same `Version` and `Generated-At` as the Manifest.

### 6.5  Manifest Entry Discipline

Every Manifest entry MUST satisfy:

- `Path` — relative to the Pack root.
- `Class` — one of `Standard`, `Decision`, `RFC`, `ADR`, `Audit`, `Review`, `Report`, `Manifest`, `Evidence`, `Stats`, `Task`, `Pack`, `Release`, `Other`. (Mirrors `schema-standard.md` §8.4.)
- `ID` — the artifact's identifier (per `schema-standard.md` §3.4 and the relevant class schema).
- `Status` — the artifact's `Status:` at `Generated-At`.
- `Version` — SemVer.
- `Hash` — recomputed at `Generated-At`.

A Manifest entry whose `Hash` does not match the bundled file's digest at validation time is an **Integrity failure** (per `schema-standard.md` §8.5 and §15 of this Standard).

## 7. Mission Specification

### 7.1  Mission Definition

A **Mission** is a Foundation-level concept that declares a bounded goal, its success criteria, its exit conditions, and the Programs or Tasks that fulfill it. A Mission is the **root** of the Pack's execution subtree.

A Mission is identified by `MISSION-<scope>-<slug>` and stored under `<pack-root>/missions/`.

### 7.2  Mission Header

A Mission document MUST carry the six standard headers (`schema-standard.md` §3.2) plus the following Mission-specific fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `Mission-ID` | R | string | Unique identifier; matches `MISSION-<scope>-<slug>` pattern. |
| `Owner` | R | role | The role responsible for the Mission (per `roles-and-authority.md`). |
| `Start-Date` | C | date (ISO-8601) | Required when `Status:` is `In Progress` or later. |
| `Target-Date` | O | date (ISO-8601) | Optional target completion date. |
| `Success-Criteria` | R | list:string | Itemized list of conditions that mark the Mission complete. |
| `Exit-Conditions` | R | list:string | Itemized list of conditions that mark the Mission *terminated* (success or failure). |
| `Exit-Status` | C | enum:`Success`,`Failure`,`Cancelled`,`Superseded` | Required when `Status:` is `Closed` or `Archived`. |
| `Status` | R | enum:`Draft`,`Authorized`,`In Progress`,`Submitted`,`Approved`,`Closed`,`Rejected`,`Withdrawn`,`Superseded`,`Archived` | Per `governance-model.md` §7 and the lifecycle in §4.1 of this Standard. |
| `Programs` | O | list:ref:`MISSION-<scope>-<slug>` | Listed Programs (see §8). |
| `FD-Authorization` | O | ref:`FD-NNNN` | The FD that authorizes the Mission (required for Foundation-level Missions). |

### 7.3  Mission Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | One paragraph: what the Mission accomplishes. |
| §2 Goal | R | The Mission's bounded goal. |
| §3 Success Criteria | R | Mirrors `Success-Criteria` header field. |
| §4 Exit Conditions | R | Mirrors `Exit-Conditions` header field. |
| §5 Programs | C | Required if Programs are declared. |
| §6 Dependencies | R | Cross-references to other Packs, FDs, or Standards. |
| §7 References | R | Cross-references to Constitution §15, Governance Model §7, this Standard. |

### 7.4  Mission Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Authorized` | `FD-Authorization` populated (if Mission is Foundation-level). |
| `Authorized` → `In Progress` | `Start-Date` set; Programs / Tasks begin. |
| `In Progress` → `Submitted` | All Programs / Tasks complete; Reports / Audits / Reviews submitted. |
| `Submitted` → `Approved` | Architect disposition recorded in the Pack Review. |
| `Approved` → `Closed` | `Exit-Status` set; Mission archived. |

### 7.5  Mission Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §7.2 required fields and §7.3 required sections present. |
| Compliance | `Success-Criteria` and `Exit-Conditions` are non-empty; `Exit-Status` populated iff `Status` is `Closed` or `Archived`. |
| Cross Reference | Every `Programs` entry resolves; every `FD-Authorization` resolves. |
| Isolation | Mission is technology-neutral; no Project-specific rule. |

## 8. Program Specification

### 8.1  Program Definition

A **Program** is a logical grouping of one or more Tasks within a Mission. A Program is optional — a Mission may be carried out without Programs (Tasks directly under the Mission). A Program is identified by `PROGRAM-<scope>-<slug>` and stored under `<pack-root>/programs/`.

### 8.2  Program Header

| Field | Required | Type | Description |
|---|---|---|---|
| `Program-ID` | R | string | Unique identifier. |
| `Mission` | R | ref:`Mission-ID` | The parent Mission. |
| `Owner` | R | role | The owning role. |
| `Start-Date` | C | date | Required when `Status:` is `In Progress` or later. |
| `Target-Date` | O | date | Optional target date. |
| `Tasks` | R | list:ref:`Task-ID` | The Tasks this Program groups (1..*). |
| `Status` | R | enum:`Draft`,`Authorized`,`In Progress`,`Submitted`,`Approved`,`Closed`,`Rejected`,`Withdrawn`,`Superseded`,`Archived` | |
| `FD-Authorization` | O | ref:`FD-NNNN` | Optional authorization FD. |

### 8.3  Program Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | One paragraph: what the Program groups. |
| §2 Tasks | R | List of Task references. |
| §3 Dependencies | R | Cross-references to siblings (Programs). |
| §4 References | R | Cross-references to parent Mission, Constitution §15, this Standard. |

### 8.4  Program Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §8.2 required fields and §8.3 required sections present. |
| Compliance | `Tasks` has 1..* entries; `Mission` resolves. |
| Cross Reference | Every `Tasks` entry resolves; every `FD-Authorization` resolves. |
| Isolation | Program is technology-neutral; no Project-specific rule. |

## 9. Task Specification

### 9.1  Task Definition

A **Task** is a single cycle of work under the Foundation Task Protocol (Constitution §15). A Task is the **atomic unit** of Builder accountability. A Task is identified by `TASK-<scope>-<NN>-<slug>` (per `schema-standard.md` §10.1) and stored under `<pack-root>/tasks/`.

### 9.2  Task Schema Compliance

A Pack-internal Task MUST conform to the **Task Schema** declared in `schema-standard.md` §10, including:

- The header block fields (`schema-standard.md` §10.2).
- The §15.5 Per-Task Scope Declaration sub-block (`schema-standard.md` §10.3).
- The required sections (`schema-standard.md` §10.4).
- The audit hooks (`schema-standard.md` §10.5).
- The lifecycle hooks (`schema-standard.md` §10.6).

### 9.3  Task-Specific Additions for Packs

A Task that is bundled in a Pack MUST additionally declare:

- `Pack-ID` — the parent Pack.
- `Mission-ID` — the parent Mission (transitive).
- `Program-ID` — the parent Program (if any).
- `Deliverables` — list of deliverable references the Task produces (see §10).

### 9.4  Task Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All `schema-standard.md` §10.2 required fields and §10.4 required sections present; Pack-specific additions from §9.3 present. |
| Compliance | `Pack-ID`, `Mission-ID` resolve; `Deliverables` is consistent with the Pack's Deliverables. |
| Cross Reference | Every referenced Pack / Mission / Program / Deliverable resolves. |
| Isolation | Task is technology-neutral; no Project-specific rule. |

## 10. Deliverable Specification

### 10.1  Deliverable Definition

A **Deliverable** is the artifact produced by a Task. A Deliverable is the **evidence** that a Task's success criteria are met. A Deliverable may be an Evidence record, a Report, a Standard, a Decision, an ADR, an RFC, or any other Foundation artifact class (per `schema-standard.md` §4–§12).

A Deliverable is identified by `DELIVERABLE-<scope>-<slug>` and stored under `<pack-root>/deliverables/`. The identifier is a **logical** label; the Deliverable's underlying artifact retains its own class-specific ID and `Path`.

### 10.2  Deliverable Header

| Field | Required | Type | Description |
|---|---|---|---|
| `Deliverable-ID` | R | string | Unique identifier. |
| `Task` | R | ref:`Task-ID` | The producing Task. |
| `Artifact-Class` | R | enum:`Standard`,`Decision`,`RFC`,`ADR`,`Audit`,`Review`,`Report`,`Evidence`,`Stats`,`Manifest`,`Pack`,`Release`,`Other` | The class of the underlying artifact. |
| `Artifact-ID` | R | ref:`Artifact-ID` | The underlying artifact's actual ID. |
| `Status` | R | enum:`Draft`,`Submitted`,`In Review`,`Approved`,`Rejected`,`Withdrawn`,`Superseded`,`Archived` | The Deliverable's status. |
| `Verification-Method` | R | string | How the Deliverable is verified (technology-neutral). |
| `Verified-By` | C | role | Required when `Status:` is `Approved`. |
| `Verified-At` | C | date | Required when `Status:` is `Approved`. |

### 10.3  Deliverable Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | One paragraph: what the Deliverable is. |
| §2 Specification | R | The normative content of the Deliverable. |
| §3 Verification | R | How the Deliverable is verified (mirrors `Verification-Method`). |
| §4 Limitations | R | Known limits or caveats. |
| §5 References | R | Cross-references to the producing Task, the Pack, the Mission. |

### 10.4  Deliverable Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §10.2 required fields and §10.3 required sections present. |
| Compliance | `Artifact-Class` matches the underlying artifact's class; `Artifact-ID` resolves to an existing artifact. |
| Cross Reference | `Task` resolves; the underlying artifact's `Status:` is `Approved` or `Ratified`. |
| Isolation | Deliverable is technology-neutral; no Project-specific rule. |

## 11. Audit Requirement

### 11.1  Pack Audit Trigger

A Pack MUST be subjected to a §11 Quality Gate Audit before it may enter `Approved` status. The Audit is recorded in an `Audit Report` (per `schema-standard.md` §9) and named `AUDIT-PACK-<pack-id>.md`.

### 11.2  Pack-Level Audit Hooks

The Pack Audit MUST apply the following four §11 Quality Gate criteria at the Pack level (in addition to the per-artifact audits in `schema-standard.md`):

| §11 Criterion | Pack-Level Rule |
|---|---|
| Completeness | All 15 required sections of this Standard are honored; all required folders of §5.1 exist; all required fields in §3.2 / §6.2 / §7.2 / §8.2 / §9.2 / §10.2 are present. |
| Compliance | Every bundled artifact is conformant with its class schema (`schema-standard.md` §4–§12); the Pack is technology-neutral; no Foundation-level hard prohibition is violated. |
| Cross Reference | Every cross-reference to a Constitution section, a Standard, a Policy, an FD, or a bundled artifact resolves; the Pack `Related:` header field is populated. |
| Isolation | The Pack contains no Project-specific rule; every normative rule remains valid in the absence of any Project. |

### 11.3  Pack Cycle

A Pack Audit may produce:

- `Verdict: PASS` — the Pack is eligible for `Approved` status.
- `Verdict: PASS with Notes` — the Pack is eligible for `Approved` status with the noted observations recorded.
- `Verdict: FAIL` — the Pack is **not** eligible for `Approved` status; the Audit Report's `Findings` enumerate the defects.

A Pack with `Verdict: FAIL` MUST NOT be transitioned to `Approved` status (§4.4).

## 12. Review Requirement

### 12.1  Pack Review Trigger

A Pack that has passed the Pack Audit (§11) MUST be subjected to a human Review before it may enter `Approved` status. The Review is recorded in a `Review Record` (per `schema-standard.md` §6) and named `REVIEW-PACK-<pack-id>.md`.

### 12.2  Reviewer

The Reviewer of a Pack is the **Role** declared in the Pack's `Owner` header field, escalated to the Architect when the Pack is Foundation-level. The Reviewer is identified by name in the Review Record's `Reviewer` header field. The Reviewer MUST NOT be the same individual as the Pack's `Author` (per `governance-model.md` §5 separation-of-duties rules).

### 12.3  Review Disposition

The Reviewer records one of the following dispositions in the `Review-Disposition` field of the Review Record:

| Disposition | Meaning | Next Status |
|---|---|---|
| `Approved` | The Pack is accepted. | `Approved` |
| `Approved with Notes` | The Pack is accepted with notes recorded in `Reviewer-Notes`. | `Approved` |
| `Changes Requested` | The Pack requires edits. | `Changes Requested` |
| `Rejected` | The Pack is denied. | `Rejected` |

### 12.4  Review Record Requirements

The Review Record MUST declare:

- `Subject` — the Pack ID.
- `Reviewer` — the reviewing role.
- `Review-Date` — ISO-8601 date.
- `Signature` — the human Architect's signature (per `schema-standard.md` §6.2 `Signature` conditional rule; non-fabricable per `governance-model.md` §5.3).
- `Disposition` — one of the four values in §12.3.
- `Required Corrections` — populated iff `Disposition` is `Changes Requested` or `Rejected`.

## 13. Report Requirement

### 13.1  Pack Report

A Pack Author produces a **Pack Report** that summarizes the Pack's contents, its audits, and its reviews. The Report is recorded in a `Builder Report` (per `schema-standard.md` §5) and named `REPORT-PACK-<pack-id>.md`.

### 13.2  Report Required Sections

The Pack Report MUST contain the eight sections declared in `schema-standard.md` §5.3:

1. Summary
2. Files Created (the Pack directory contents)
3. Files Modified (cross-references and Manifest entries)
4. Acceptance Checklist (the 15 sections of this Standard)
5. Verification (Pack Audit verdict, Review disposition, Integrity checks)
6. Remaining Limitations (open issues, deferred items)
7. Git Status (branch, commit, push, tag — none for first Pack)
8. Next Recommended Task (e.g., Migration Plan, Supersession Pack)

### 13.3  Pack Report Submission

The Pack Report, the Pack Audit, and the Pack Review are submitted together. The Pack Builder stops after submission and does not begin any further work until the Architect approves the Pack.

## 14. Artifact Management

### 14.1  Permitted Bundled Artifacts

A Pack may bundle the following Foundation artifact classes (per `schema-standard.md` §4–§12):

| Class | Source Schema | Pack Storage |
|---|---|---|
| Standard | `schema-standard.md` §4 (and other Standards) | `<pack-root>/standards/` |
| Decision (FD) | `schema-standard.md` §4 (FD-namespace) | `<pack-root>/decisions/` |
| RFC (FRFC, RRFC) | `schema-standard.md` §4 (RFC-namespace) | `<pack-root>/rfc/` |
| ADR | `schema-standard.md` §4 (ADR-namespace) | `<pack-root>/adr/` |
| Audit | `schema-standard.md` §9 | `<pack-root>/audits/` |
| Review | `schema-standard.md` §6 | `<pack-root>/reviews/` |
| Report | `schema-standard.md` §5 | `<pack-root>/reports/` |
| Evidence | `schema-standard.md` §4 | `<pack-root>/evidence/` |
| Statistics | `schema-standard.md` §7 | `<pack-root>/stats/` |
| Manifest | `schema-standard.md` §8 | `<pack-root>/manifests/` |
| Task | `schema-standard.md` §10 | `<pack-root>/tasks/` |
| Mission | This Standard §7 | `<pack-root>/missions/` |
| Program | This Standard §8 | `<pack-root>/programs/` |
| Deliverable | This Standard §10 | `<pack-root>/deliverables/` |
| Pack-Container | `schema-standard.md` §11 | `<pack-root>/PACK-<pack-id>.md` |

### 14.2  Forbidden Bundled Artifacts

A Pack **may not** bundle any of the following, because they are not Foundation artifacts and are reserved for their respective L5 specifications:

- Engine source files or specifications (Task 06 — Builder Runtime; Task 08 — Engine Specifications).
- SDK source files or specifications (Task 09).
- Plugin source files or specifications (Task 10).
- Workspace implementations (Task 11).
- Release artifacts (Task 12 — except that a Release declares a Pack's relationship to a `Foundation-Version`).
- Serialization, schema-engine, or runtime-binding artifacts (no JSON-Schema, YAML, OpenAPI, Protobuf, etc.).

### 14.3  Pack Containment Rule

A Pack **may not** contain another Pack. The recursion terminates at the Pack itself. A Pack can reference another Pack via `Related:` (per `schema-standard.md` §11.2) but cannot embed it.

### 14.4  Atomicity

A Pack is **atomic** at the Manifest level: every entry in the Manifest is either present-and-conformant or the Pack is **Invalid**. Partial Packs are forbidden.

## 15. Pack Dependency Rules

A Pack may declare dependencies on other Packs, FDs, RFCs, Standards, or external artifacts. Dependencies are declared in the Pack's `Dependencies` section (per §16.1) and in the `Related:` header field.

### 15.1  Dependency Forms

A Pack dependency is one of:

| Form | Meaning |
|---|---|
| `requires:<ID>@<version-spec>` | The Pack cannot be executed without the named artifact at the named version range. |
| `references:<ID>` | The Pack references the named artifact for context but does not require it. |
| `supersedes:<ID>` | The Pack supersedes the named artifact (per `governance-model.md` §9). |

### 15.2  Dependency Rules

A Pack dependency MUST satisfy:

1. **Resolvability.** Every `requires:` and `references:` dependency target must resolve to an existing artifact (Constitution §10.1).
2. **Foundation-Version compatibility.** Every `requires:` dependency's `Foundation Version` MUST be `<= Pack.FoundationVersion` (a Pack cannot require a Foundation version newer than its own).
3. **No circular dependencies.** A Pack MUST NOT depend, directly or transitively, on itself.
4. **Immutability propagation.** If a `requires:` dependency is `Superseded`, the Pack's Author MUST issue a new Pack version that either updates the dependency or removes it.

### 15.3  Forbidden Dependencies

A Pack **may not** depend on:

- A Pack that is in `Draft`, `Rejected`, or `Withdrawn` status.
- A Foundation Decision that is in `Pending Ratification` status (per `governance-model.md` §7 — Pending Ratification is not binding).
- A Standard that is in `Draft` status only. A `Draft` Standard may be referenced but not required.

## 16. Pack Versioning Rules

### 16.1  Version Surfaces

A Pack carries three version surfaces:

- `Pack.Version` — the Pack's SemVer version (per Constitution §8).
- `Pack.FoundationVersion` — the Foundation version the Pack binds to (per `FOUNDATION/VERSION`).
- `Pack.ConstitutionVersion` — the Constitution version the Pack binds to (per `constitution.md` header).

### 16.2  SemVer Bump Rules

A Pack's `Version` is bumped per Constitution §8:

| Bump | Trigger |
|---|---|
| **MAJOR** | A breaking change to the Pack's Mission, Success Criteria, Exit Conditions, or Program decomposition. |
| **MINOR** | A backward-compatible addition (e.g., a new Program, a new Task, a new Deliverable). |
| **PATCH** | A backward-compatible correction (e.g., a typo, a cross-reference fix, a Manifest re-hash). |

### 16.3  Pre-Release Tags

A Pack may carry a pre-release tag per Constitution §8, e.g., `0.1.0-alpha.1`, `0.1.0-rc.1`. The tag does not affect the Pack's binding to the Foundation; it is descriptive only.

### 16.4  Hash Computation

The Pack's `Hash` is computed over the canonical concatenation of the Manifest entries' `Hash`es, in `Entries` order. The hash algorithm is **not** bound by this Standard; the algorithm and digest format are recorded in the Manifest's `Integrity` section (`schema-standard.md` §8.3).

### 16.5  Versioning and Migration

A MAJOR-version bump of a Pack requires a Migration Plan (per §14.4 of this Standard and `directory-standard.md` §10.4). The Migration Plan is stored under `<pack-root>/migrations/`.

## 17. The Pack Quality Gate

### 17.1  Overview

The Pack Quality Gate is the **Pack-level** application of the four §11 Quality Gate criteria. The Gate is a single `Verdict` (`PASS`, `PASS with Notes`, `FAIL`) computed from the Pack Audit (§11.2) and the Pack Review (§12.3).

### 17.2  Gate Outcomes

| Audit Verdict | Review Disposition | Pack Quality Gate |
|---|---|---|
| `PASS` | `Approved` | `Approved` |
| `PASS` | `Approved with Notes` | `Approved with Notes` |
| `PASS` | `Changes Requested` | `Changes Requested` |
| `PASS` | `Rejected` | `Rejected` |
| `PASS with Notes` | `Approved` | `Approved with Notes` |
| `PASS with Notes` | `Approved with Notes` | `Approved with Notes` |
| `PASS with Notes` | `Changes Requested` | `Changes Requested` |
| `PASS with Notes` | `Rejected` | `Rejected` |
| `FAIL` | (any) | `Rejected` |

### 17.3  Gate Output

The Pack Quality Gate verdict is recorded in the Pack Report (`schema-standard.md` §5), the Pack Audit (`schema-standard.md` §9), and the Pack Review (`schema-standard.md` §6 `Disposition Summary` table). A Pack that enters `Approved` status without a `PASS` or `PASS with Notes` Gate verdict is **Invalid**.

### 17.4  Pack Quality Gate Audit Hooks

The Pack-level §11 Quality Gate MUST apply the following additional checks:

| §11 Criterion | Pack-Level Rule |
|---|---|
| Completeness | All 15 required sections of this Standard are honored; all required folders in §5.1 are present; all required fields in §3.2 / §6.2 / §7.2 / §8.2 / §9.2 / §10.2 are populated. |
| Compliance | Every bundled artifact satisfies `schema-standard.md` §4–§12; the Pack is technology-neutral; no Hard Prohibition is violated; Versioning Rules (§16) honored. |
| Cross Reference | Every dependency (§15) resolves; every cross-reference in this Standard resolves; the Manifest's `Entries` table matches the on-disk Pack directory. |
| Isolation | The Pack contains no Project-specific rule; every Mission, Program, Task, and Deliverable is technology-neutral and project-independent. |

## 18. Cross References

### 18.1  Mandatory References (Constitution §10.1)

This Standard references:

- Constitution §1 (Governance Hierarchy)
- Constitution §2 (Compatibility Policy)
- Constitution §3 (Design Principles)
- Constitution §4 (Lifecycle Model)
- Constitution §6 (RFC Governance)
- Constitution §9 (Naming Convention)
- Constitution §10 (Cross Reference Policy)
- Constitution §11 (Quality Gate)
- Constitution §13 (Future Extension Policy)
- Constitution §14 (Success Criteria)
- Constitution §15 (Foundation Task Protocol)

### 18.2  Companion Standards and Policies

- `FOUNDATION/03-Standards/directory-standard.md` — Per-class storage paths (`§4`).
- `FOUNDATION/03-Standards/schema-standard.md` — Pack Schema (`§11`), Manifest Schema (`§8`), Task Schema (`§10`), Audit Schema (`§9`), Review Schema (`§6`), Report Schema (`§5`), Evidence Schema (`§4`).
- `FOUNDATION/02-Governance/governance-model.md` §6 — Artifact Types.
- `FOUNDATION/02-Governance/governance-model.md` §7 — Governance Status Lifecycle.
- `FOUNDATION/02-Governance/approval-workflow.md` — Status transition authority.
- `FOUNDATION/02-Governance/change-control-policy.md` — Pack mutations require an FD.
- `FOUNDATION/02-Governance/disagreement-and-escalation.md` — Pack conflicts.
- `FOUNDATION/02-Governance/roles-and-authority.md` — Role assignments.
- `FOUNDATION/08-RFCs/rfc-policy.md` — RFC schema inputs.
- `FOUNDATION/09-Decisions/foundation-decision-policy.md` — FD schema inputs.
- `FOUNDATION/10-ADRs/adr-policy.md` — ADR schema inputs.

### 18.3  Back-References

A Pack that conforms to this Standard should reference this Standard in its `Related:` header field:

```
Related: Builder Pack Standard v0.1.0-draft (FOUNDATION/03-Standards/pack-standard.md)
```

## 19. Compatibility

### 19.1  Version Surfaces

- **This Standard's version.** Header `Version: 0.1.0-draft`. Bump rules per Constitution §8.
- **Foundation version.** `FOUNDATION/VERSION` (currently `0.1.0-dev`).
- **Constitution version.** `constitution.md` header (currently `v0.1.0-draft` Provisional).

### 19.2  Backward Compatibility

This Standard guarantees backward compatibility for:

- The 15 required sections enumerated by the Architect.
- The §5.1 directory layout.
- The Pack Schema fields (`schema-standard.md` §11).
- The §11 Quality Gate audit hooks.

A Pack Standard amendment may add new fields, sections, or sub-folders backward-compatibly. A Pack Standard amendment that removes a required field, section, or sub-folder is a MAJOR change and requires a Migration Plan per §19.4.

### 19.3  Forward Compatibility

Forward compatibility is not guaranteed. A consumer written against a future version of this Standard may not operate on the current version.

### 19.4  Migration Compatibility

Any backward-incompatible change to this Standard must:

1. Publish a Migration Plan (in this Standard's directory or in an accompanying `MIGRATION-STD-PACK-<NN>.md`).
2. Place the previous version in `Migration Required` state (Constitution §12).
3. Enumerate every breaking change in the new version's FD.

## 20. Relationship to Other Artifacts

- **Constitution §4 (Lifecycle Model).** This Standard implements the lifecycle stages of `Bootstrap → Alpha → Beta → Stable → Deprecated → Frozen → Archived` for the Pack concept.
- **Constitution §15 (Foundation Task Protocol).** The Pack's Task and Mission specifications are refinements of the §15 Task protocol.
- **Schema Standard §11 (Pack Schema).** This Standard is the *content* specification; the Schema Standard §11 is the *field* specification. The two are co-equal normative inputs.
- **Schema Standard §8 (Manifest Schema).** The Pack Manifest conforms to the Manifest Schema.
- **Schema Standard §10 (Task Schema).** Pack-internal Tasks conform to the Task Schema.
- **Directory Standard §4.** Defines where Pack artifacts live on disk.
- **Constitution §14 (Success Criteria).** A Pack that successfully completes a Mission contributes to the Foundation Success Criteria; the Pack itself is not a Success Criterion.
- **Change-Control Policy.** A Pack mutation is a Major change and requires an FD.

## 21. Ratification

This Builder Pack Standard is itself **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred** — no `FD-0005-ratify-pack-standard.md` is created in Task 05. The Foundation Builder prepares the Standard; the human Architect reviews it via `REVIEW-FOUNDATION-05-pack.md`.

A future FD may ratify or supersede this Standard only if required by the Constitution, a later approved governance decision, or the Task 12 Foundation RC review. Until any such FD is issued, this Standard governs Foundation work **provisionally**, alongside the Provisional Constitution, the Task 02 Governance Model, the Task 03 Directory Standard, and the Task 04 Schema Standard.

> Note: No `FD-0005-ratify-pack-standard.md` is created during Task 05. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action.
>
> Note: No `PACK-00-foundation-pack.md`, no `PACK-01-*.md`, no `MISSION-*.md`, no `PROGRAM-*.md`, no `DELIVERABLE-*.md` is created during Task 05. The Task 05 deliverable is the Standard; the first Pack is a Task 12 deliverable.

---

*End of Builder Pack Standard v0.1.0-draft.*
