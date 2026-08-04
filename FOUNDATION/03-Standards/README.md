# Research-OS Foundation — Standards

**Status:** Draft / In Review
**Path:** `FOUNDATION/03-Standards/`
**Foundation Version:** 1.0.0-rc.1 (internally Applied; not published)
**Constitution Version:** v0.1.0-draft (Ratified)
**Related:** Constitution §9 (Naming Convention); `FOUNDATION/02-Governance/governance-model.md`; `FOUNDATION/03-Standards/directory-standard.md`

---

This directory holds **Foundation Standards** — L3 normative specifications that operationalize the Constitution. Standards are named per Constitution §9:

```
STD-<area>-vX.Y.Z.md
```

## Index

| Standard | Version | Status | Purpose |
|---|---|---|---|
| [directory-standard.md](./directory-standard.md) | 0.1.0-draft | Draft / In Review | Canonical directory layout, per-class storage paths, numbered-prefix convention, reserved directories, path-mutation rules, path-validation rules. Created by Task 03. |
| [schema-standard.md](./schema-standard.md) | 0.1.0-draft | Draft / In Review | Canonical shape (field, header, section, validation, lifecycle) of every Foundation artifact class: Evidence, Report, Review, Statistics, Manifest, Audit, Task, Pack, Release. Technology-neutral. Created by Task 04. |
| [pack-standard.md](./pack-standard.md) | 0.1.0-draft | Draft / In Review | Canonical shape, content, lifecycle, and quality criteria of a Builder Pack; defines Mission, Program, Task, and Deliverable templates; Pack Manifest rules; Pack Audit/Review/Report hooks; Pack versioning and dependency rules. Technology-neutral. Created by Task 05. |
| [runtime-specification.md](./runtime-specification.md) | 0.1.0-draft | Draft / In Review | Canonical contract for the Builder Runtime: Runtime Purpose, Runtime Architecture, Runtime Lifecycle (12 stages), Runtime Input Specification (Mission, Pack, Task, Schema, Governance), Runtime Output Specification (Artifacts, Audit, Reports, Reviews, Status), Quality Gate Integration, Human-in-the-loop Model, Runtime Security Boundary, Runtime Compatibility. Technology-neutral. Created by Task 06. |
| [quality-gate-standard.md](./quality-gate-standard.md) | 0.1.0-draft | Draft / In Review | Canonical contract for the Foundation Quality Gate: Quality Gate Purpose, Quality Gate Lifecycle (5 stages: Draft → Review → Approval → RC → Stable), Quality Gate Types (6 Gates: Structure, Consistency, Cross Reference, Isolation, Scope Compliance, Security Boundary), Gate Evaluation Model (4 outcomes: PASS, FAIL, BLOCKED, REPAIR REQUIRED), Audit Relationship, Review Relationship, Failure Handling, Release Quality Gate, Compatibility. Technology-neutral. Created by Task 07. |
| [engine-specification.md](./engine-specification.md) | 0.1.0-draft | Draft / In Review | Canonical contracts for the six Foundation Engines (Prompt, Audit, Evidence, Statistics, Report, Builder); each Engine declares Purpose, Responsibility, Inputs, Outputs, Lifecycle, Dependencies, Quality Gate, Security Boundary, Compatibility, Future Extensions. Shared 11-stage Engine Lifecycle and Shared Engine Architecture. Technology-neutral. Created by Task 08. |
| [sdk-specification.md](./sdk-specification.md) | 0.1.0-draft | Draft / In Review | Canonical contracts for the five Foundation SDKs (Project, Builder, Migration, Release, Plugin); each SDK declares Purpose, Interface Boundary, Inputs, Outputs, Dependencies, Versioning, Compatibility, Security Rules, Extension Model. Shared SDK Architecture, 9-stage SDK Lifecycle, Permission Model for Plugin SDK. Technology-neutral. Created by Task 09. |
| [plugin-specification.md](./plugin-specification.md) | 0.1.0-draft | Draft / In Review | Canonical contract for the Foundation Plugin: Plugin Architecture Purpose, Plugin Boundary Model, 9-stage Plugin Lifecycle (Registration, Discovery, Validation, Permission Approval, Activation, Execution, Audit, Disable, Removal), Plugin Interface Specification (Input Contract, Output Contract, Metadata, Version, Compatibility), Permission Model (Allowed / Restricted / Default-Denied / Human Approval Boundary / Isolation Rules), Security Model (Trust Boundary, Sandboxing Concept, Data Access Rules, Credential Handling Rules), seven concrete Platform Plugin Specifications (GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor), Compatibility (Version, Migration, Extension, Supersession). Technology-neutral and project-independent. Created by Task 10. |
| [workspace-specification.md](./workspace-specification.md) | 0.1.0-draft | Draft / In Review | Canonical contract for the Foundation Workspace: Workspace Architecture Purpose (persistent, bounded, audited context for Builder Pack execution by Builder Runtime), Workspace Boundary Model (5-layer diagram, 10 Boundary Rules, 9 Boundary Crossing Points), 8-stage Workspace Lifecycle (Request, Provision, Initialize, Activate, Execute, Audit, Deactivate, Archive), Workspace Interface Specification (Input Contract, Output Contract, 19-field Metadata, Versioning, Compatibility), Workspace Permission and Security Model (7 Allowed / 7 Restricted / 7 Default-Denied Permissions, Human Approval Boundary at 4 Lifecycle stages, 10 Isolation Rules, 6 Credential Handling Rules, Security Boundary), three co-equal Workspace Types (Mission, Project — not instantiated during Foundation phase — Foundation), Cross-Workspace Interaction Rules (default-denied), Workspace Compatibility (Version, Migration, Extension, Supersession). Technology-neutral and project-independent. Created by Task 11. |
| [release-specification.md](./release-specification.md) | 0.2.0-draft | Draft / In Review; binding through FD-0003 + FD-0005 | Canonical contract for the Foundation Release. Its first-RC prerequisites were repaired under Approved FRFC-0002 and Ratified FD-0005; the Foundation `1.0.0-rc.1` Release is internally Applied under Ratified FD-0004 and remains externally unpublished. |

## Future Standards (Reserved)

| Standard | Task | Purpose |
|---|---|---|
| *(none)* | Task 08 (now complete) | Engine Specifications. |
| *(none)* | Task 09 (now complete) | SDK Specifications. |
| *(none)* | Task 10 (now complete) | Plugin Specification. |
| *(none)* | Task 11 (now complete) | Workspace Specification. |
| *(none)* | Task 12 (now complete) | Release Specification. |

The Standards in this directory are normative at L3 of the governance hierarchy (`FOUNDATION/02-Governance/governance-model.md` §2). They may not contradict the Constitution or any active FD.

> **Current authority note.** All ten Standards retain `Draft / In Review` document-level status. Ratified FD-0003 collectively binds the exact baseline versions instead of creating one ratification FD per Standard. Release Specification `0.2.0-draft` is additionally bound by Ratified FD-0005's exact controlled repair.

> **Task-sequence note.** Task 12 — Release Specification is the **twelfth and final** Foundation Task. All 12 Foundation Tasks are complete. Subsequent governance cycles approved the baseline, repaired the first-RC prerequisites, and internally applied Foundation `1.0.0-rc.1`.

> **Post-repair status.** Release Specification §9.2 conditions 1 and 2 were repaired through FRFC-0002 and FD-0005; condition 3 was preserved verbatim. Ratified FD-0004 satisfied the repaired authorization boundary and internally applied `1.0.0-rc.1`. External publication, git tagging, Pack generation, Workspace activation, and Project activation remain outside this action and were not performed.

---

*End of README.*
