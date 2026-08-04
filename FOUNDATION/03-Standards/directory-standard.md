# Research-OS Foundation — Directory Standard

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/03-Standards/directory-standard.md`
**Supersedes:** none
**Related:** Constitution v0.1.0-draft (Provisional) §1, §9, §10, §11; `FOUNDATION/02-Governance/governance-model.md`; `FOUNDATION/02-Governance/roles-and-authority.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/02-Governance/approval-workflow.md`; `FOUNDATION/02-Governance/disagreement-and-escalation.md`; `FOUNDATION/08-RFCs/rfc-policy.md`; `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/10-ADRs/adr-policy.md`

---

## 1. Purpose and Scope

This Directory Standard defines the **canonical directory layout** of the Research-OS Foundation repository. It binds the path conventions for every Foundation artifact class and establishes the rules for creating, renaming, removing, and reserving Foundation directories.

**Scope.** This Standard governs:

- The top-level directories of the `Research-OS` repository (under `FOUNDATION/`).
- The numbered-prefix convention used to order Foundation directories.
- The storage path for every Foundation artifact class declared in `governance-model.md` §6 and the Foundation Decision Policy.
- The reserved-directory list (paths that exist semantically but may not yet contain files).
- The path-mutation rules (when a directory may be created, renamed, removed, or split).
- The path-validation rules used by Reviewers and the Quality Gate.

**Out of scope.**

- Filename patterns for individual artifact classes — those are normative in the Foundation Decision Policy, the RFC Policy, the ADR Policy, the Audit/Review/Report policies, and the relevant Standards.
- Project-local directory layouts — those are governed by Project RFCs (PRFCs) issued after the Foundation `v1.0.0-rc.1` release (Task 12). Foundation defines the *shape* of Project layout; it does not instantiate it.
- Engine, SDK, Plugin, or Workspace internal directory layouts — those are governed by their own L5 specifications (Tasks 06, 08, 09, 10, 11 respectively).
- Mission, Program, and Work Package directory layouts — reserved execution concepts (per `governance-model.md` §2 note); their full Standards are not defined in Task 03.

## 2. Normative Status

This Directory Standard is **Draft / In Review** at Foundation `0.1.0-dev`, Constitution `v0.1.0-draft` (Provisional). It is the L3 Foundation Standard that operationalizes Constitution §9 (Naming Convention) for *directory paths* specifically.

**Conformance.** A Foundation artifact is conformant with this Standard if and only if:

- Its directory path is one of the paths defined in §3 (Top-level layout) and §4 (Per-class storage), OR
- Its directory path has been added by an FD-approved extension that explicitly references this Standard.

**Conflict resolution.** Per `governance-model.md` §4:

1. Constitution prevails.
2. Higher `Status:` prevails.
3. Later SemVer version prevails.
4. Later ISO-8601 date prevails.
5. Higher-numbered ID prevails.
6. Otherwise escalate.

Where this Standard and the Constitution appear to conflict, the Constitution prevails. Where this Standard and an active FD appear to conflict, the FD prevails if its `Status:` is `Ratified`; otherwise this Standard governs provisionally.

## 3. Top-level Layout

The Research-OS repository contains **two** top-level groups: `FOUNDATION/` (governing the platform) and the future `PROJECTS/` group (governing downstream research Projects, post-Foundation).

During the Foundation phase, **only** `FOUNDATION/` and project-independent meta files may exist at the repository root. Project-specific work is forbidden until Task 12 declares `v1.0.0-rc.1`.

### 3.1  Repository Root

| Path | Purpose | Mutability |
|---|---|---|
| `FOUNDATION/` | All Foundation artifacts. The only mutable top-level group during Foundation phase. | Mutable (subject to this Standard and FDs). |
| `CHANGELOG.md` | Top-level changelog. Records every Constitution, FD, and Foundation Standard change. | Mutable (per Change-Control Policy). |
| `LICENSE` | (Reserved) Project license. | Reserved; content out of scope for this Standard. |
| `README.md` | (Reserved) Top-level readme. | Reserved. |
| `.claude/` | Local tooling configuration. | Not part of Foundation governance. |
| `PROJECTS/` | (Reserved) Project directories. **No content permitted during Foundation phase.** | Reserved. |

> Note: `LICENSE`, root `README.md`, and `PROJECTS/` are reserved; this Standard does not create them. Foundation work continues under the existing `FOUNDATION/`-only layout.

### 3.2  FOUNDATION/ Subtree

The `FOUNDATION/` subtree is the canonical home of all Foundation artifacts. Its top-level subdirectories follow the **numbered-prefix convention** (§5). The current layout:

| Path | Purpose | Created By |
|---|---|---|
| `FOUNDATION/01-Constitution/` | The Constitution (`constitution.md`) and any constitutional annexes. | Task 01 |
| `FOUNDATION/02-Governance/` | Governance Model, Roles & Authority, Approval Workflow, Change-Control Policy, Disagreement & Escalation. | Task 02 |
| `FOUNDATION/03-Standards/` | **This Directory Standard and future Foundation Standards** (per Constitution §9 `STD-<area>-vX.Y.Z.md` pattern). | Task 03 |
| `FOUNDATION/04-Audits/` | Audit Reports (`AUDIT-FOUNDATION-<NN>-<slug>.md`). | Task 01+ |
| `FOUNDATION/05-Statistics/` | (Reserved) Statistical and quantitative artifacts at the Foundation level. | Reserved |
| `FOUNDATION/06-Reports/` | Builder Reports, including seven-section Task Reports (`REPORT-FOUNDATION-<NN>-<slug>.md`). | Task 01+ |
| `FOUNDATION/07-Reviews/` | Human Review Records (`REVIEW-FOUNDATION-<NN>-<slug>.md`). | Task 01+ |
| `FOUNDATION/08-RFCs/` | Foundation RFC policy and FRFC + RRFC records. PRFC records are not stored here (see §4.3). | Task 02 |
| `FOUNDATION/09-Decisions/` | Foundation Decision policy, FD records, and DIS- records. | Task 02 |
| `FOUNDATION/10-ADRs/` | ADR policy and F-ADR records. P-ADR and R-ADR records are not stored here (see §4.5). | Task 02 |
| `FOUNDATION/VERSION` | Foundation version file (currently `0.1.0-dev`). | Task 01 |
| `FOUNDATION/README.md` | Foundation index, layout summary, and current status. | Task 01, updated by each Task |

Future L3 Foundation Standards, L5 Engine/SDK/Plugin/Workspace specifications, and L6–L8 Project artifacts will appear in **new** top-level subdirectories following the same numbered-prefix convention. Each new top-level subdirectory must be authorized by an FD or by a future Foundation Standard that explicitly references this Directory Standard.

## 4. Per-class Storage Paths

Every Foundation artifact class declared in `governance-model.md` §6 has a **canonical storage path**. The path is binding once the artifact is created; a Foundation artifact may not be moved between paths except by an FD-approved supersession (§7).

### 4.1  Foundation Decision (FD)

- **Pattern:** `FOUNDATION/09-Decisions/FD-NNNN-<slug>.md`
- **Naming source:** Constitution §9; `FOUNDATION/09-Decisions/foundation-decision-policy.md`.
- **Supersession:** A superseded FD remains in place with `Status: Superseded` and a `Superseded By:` header reference. The superseding FD lives at its own path.

### 4.2  Foundation RFC (FRFC)

- **Pattern:** `FOUNDATION/08-RFCs/FRFC-NNNN-<slug>.md`
- **Naming source:** Constitution §9; `FOUNDATION/08-RFCs/rfc-policy.md` §2.1.
- **Storage:** `FOUNDATION/08-RFCs/`.
- **Notes:** FRFC records are co-located with the RFC policy and the RRFC records.

### 4.3  Project RFC (PRFC)

- **Pattern:** `PROJECTS/<project>/08-PRFCs/PRFC-<project>-NNNN-<slug>.md` (post-Foundation).
- **Naming source:** Constitution §9; `FOUNDATION/08-RFCs/rfc-policy.md` §2.2.
- **Storage:** **No PRFC directory exists in the Foundation subtree.** PRFCs are stored under the issuing Project's subtree. The Foundation does **not** provide a generic `FOUNDATION/08-RFCs/PRFC/` directory.
- **Foundation phase:** PRFC records may not be created during Foundation phase because no Project subtree exists. The pattern is reserved.

### 4.4  Release RFC (RRFC)

- **Pattern:** `FOUNDATION/08-RFCs/RRFC-NNNN-<slug>.md`
- **Naming source:** `FOUNDATION/08-RFCs/rfc-policy.md` §2.3.
- **Storage:** `FOUNDATION/08-RFCs/`.
- **Notes:** RRFC = Release RFC (release planning, scope, exceptions, or governance). RRFCs are co-located with FRFCs because both bind at Foundation level via FD.

### 4.5  Architecture Decision Record (ADR)

ADR records are split by scope:

| Scope | Pattern | Storage |
|---|---|---|
| **F-ADR** (Foundation) | `FOUNDATION/10-ADRs/ADR-NNNN-<slug>.md` | `FOUNDATION/10-ADRs/` |
| **P-ADR** (Project) | `PROJECTS/<project>/10-ADRs/ADR-<project>-NNNN-<slug>.md` (post-Foundation) | Project subtree |
| **R-ADR** (Repository) | n/a — repository implementation decisions normally use ADRs (when non-normative) or a PRFC (when normative within a Project), depending on scope. | n/a |

- **Naming source:** `FOUNDATION/10-ADRs/adr-policy.md`.
- **Storage:** `FOUNDATION/10-ADRs/` for F-ADRs. The Foundation does **not** create P-ADR or R-ADR directories; those are Project-local.

### 4.6  Audit Report

- **Pattern:** `FOUNDATION/04-Audits/AUDIT-<scope>-<NN>-<slug>.md`
- **Naming source:** Constitution §9; `FOUNDATION/02-Governance/governance-model.md` §6.
- **Storage:** `FOUNDATION/04-Audits/`. Project audit reports (post-Foundation) are stored under the Project's `04-Audits/` subtree.

### 4.7  Review Record

- **Pattern:** `FOUNDATION/07-Reviews/REVIEW-<scope>-<NN>-<slug>.md`
- **Naming source:** Constitution §9; `FOUNDATION/02-Governance/governance-model.md` §6.
- **Storage:** `FOUNDATION/07-Reviews/`. Project review records (post-Foundation) are stored under the Project's `07-Reviews/` subtree.

### 4.8  Builder / Task Report

- **Pattern:** `FOUNDATION/06-Reports/REPORT-<scope>-<NN>-<slug>.md`
- **Naming source:** Constitution §9; `FOUNDATION/02-Governance/governance-model.md` §6; Constitution §15.2.
- **Storage:** `FOUNDATION/06-Reports/`. Project reports (post-Foundation) are stored under the Project's `06-Reports/` subtree.

### 4.9  Disagreement Record (DIS-)

- **Pattern:** `FOUNDATION/09-Decisions/DIS-<scope>-<NN>-<slug>.md`
- **Naming source:** `FOUNDATION/02-Governance/governance-model.md` §6; `FOUNDATION/02-Governance/disagreement-and-escalation.md`.
- **Storage:** `FOUNDATION/09-Decisions/` (co-located with FD records because DIS- records may escalate into FDs).

### 4.10  Foundation Standard (STD-)

- **Pattern:** `FOUNDATION/03-Standards/STD-<area>-v<X>.<Y>.<Z>.md`
- **Naming source:** Constitution §9.
- **Storage:** `FOUNDATION/03-Standards/`.
- **Notes:** The Directory Standard is itself a Foundation Standard. Each new Foundation Standard is a separate file in `03-Standards/`.

### 4.11  Foundation README and Version

- `FOUNDATION/README.md` — Foundation index, layout summary, current status, task table.
- `FOUNDATION/VERSION` — Foundation version file (one-line SemVer). Read-only outside an FD-driven bump.

## 5. The Numbered-Prefix Convention

Top-level subdirectories of `FOUNDATION/` use a two-digit **numbered prefix** followed by a hyphen and a kebab-case scope name. The prefix is normative: it defines the order in which Foundation work proceeds and the type of artifact the directory contains.

### 5.1  Prefix Assignment

| Prefix | Scope | Numbering Source | Created By |
|---|---|---|---|
| `01-` | Constitution | Constitution §17 ratification sequence step 1 | Task 01 |
| `02-` | Governance | Constitution §17 ratification sequence step 2 | Task 02 |
| `03-` | Standards | Constitution §9 `STD-` pattern and §15 Task 03 | Task 03 |
| `04-` | Audits | Constitution §9 `AUDIT-` pattern | Task 01+ |
| `05-` | Statistics (reserved) | Constitution §9 `STATS-` pattern | Reserved |
| `06-` | Reports | Constitution §9 `REPORT-` pattern; §15.2 seven-section report | Task 01+ |
| `07-` | Reviews | Constitution §9 `REVIEW-` pattern | Task 01+ |
| `08-` | RFCs | Constitution §9 `FRFC-`/`PRFC-`/`RRFC-` patterns; Constitution §6 RFC governance | Task 02 |
| `09-` | Decisions | Constitution §9 `FD-` pattern; §7 Decision Records; §17 ratification sequence step 3 | Task 02 |
| `10-` | ADRs | `FOUNDATION/10-ADRs/adr-policy.md`; ADR storage convention | Task 02 |
| `11-` | (reserved) | Future Builder Runtime / Engines | Reserved |
| `12-` | (reserved) | Future SDKs | Reserved |
| `13-` | (reserved) | Future Plugins | Reserved |
| `14-` | (reserved) | Future Workspaces | Reserved |
| `15-` | (reserved) | Future Quality Gate artifacts | Reserved |
| `16-` | (reserved) | Future releases | Reserved |

### 5.2  Prefix Rules

- **Form.** Two digits, hyphen, scope name (`NN-scope-name`).
- **Lower bound.** Prefix `01`.
- **Upper bound.** Undefined; prefixes continue as the Foundation grows.
- **Density.** Prefixes need not be contiguous; gaps are permitted. `05-Statistics/` is reserved but empty, and so is `11-`–`16-` above.
- **Reuse.** A prefix, once assigned to a scope, is reserved for that scope. A reserved prefix may be **claimed** by an FD or by a future Foundation Standard that explicitly references this Directory Standard.
- **Reordering.** Reordering a prefix (e.g., promoting `04-` ahead of `03-`) requires an amendment of this Standard and a corresponding FD.
- **Display order.** Directory listings SHOULD sort by prefix order to make the layout read in the sequence the Foundation was built.

## 6. Reserved Directories

The following directories are **reserved** by this Standard. They may exist semantically (e.g., as targets for future artifacts) but they MUST NOT contain any artifact until a Foundation Task or FD authorizes their creation.

| Path | Reserved For |
|---|---|
| `FOUNDATION/05-Statistics/` | Foundation-level statistical and quantitative artifacts (`STATS-FOUNDATION-<NN>-<slug>.md`). |
| `FOUNDATION/11-` to `FOUNDATION/16-` | Future Foundation scope groups (Builder Runtime, Engines, SDKs, Plugins, Workspaces, Quality Gate artifacts, Releases). |
| `PROJECTS/` (at repository root) | Project subtrees (post-Foundation). |
| `PROJECTS/<project>/` | Individual Project roots (post-Foundation). |
| `PROJECTS/<project>/08-PRFCs/` | Project RFC storage (post-Foundation). |
| `PROJECTS/<project>/10-ADRs/` | Project ADR storage (post-Foundation). |

A reserved directory MAY be created on disk ahead of its first use to anchor the layout, but the Builder MUST NOT place any artifact in a reserved directory until the authorizing Task or FD has been completed.

## 7. Path-Mutation Rules

A Foundation path may be mutated only as follows.

### 7.1  Creating a new path

Creating a new top-level subdirectory under `FOUNDATION/` requires:

1. An unused numbered prefix assigned per §5.
2. A Foundation Task that has been authorized (per `FOUNDATION/README.md` Task table, `completed` or in progress under §15.5 scope).
3. An entry in this Standard (or a successor) that names the new path.
4. A corresponding Layout entry in `FOUNDATION/README.md`.

Creating a new subdirectory under an existing top-level subdirectory requires an FD or a Foundation Standard that authorizes it. Subdirectories may not be created ad hoc.

### 7.2  Renaming a path

A Foundation path may not be renamed except by an FD. The FD must:

- Identify the old path and the new path.
- Update all references in every Foundation artifact that points to the old path.
- Update `FOUNDATION/README.md` and this Standard.
- Apply the new path on disk.

### 7.3  Removing a path

A Foundation path may not be removed except by an FD that:

- Confirms no `active` artifact remains under the path.
- Confirms no `active` artifact references the path.
- Specifies the disposition of any `archived` artifacts (typically: leave on disk, update README).
- Updates `FOUNDATION/README.md` and this Standard.

### 7.4  Splitting a path

Splitting a top-level subdirectory into two subdirectories (e.g., splitting `03-Standards/` into `03-Standards/` and `03a-Documentation/`) is treated as a rename of part of the path and requires an FD. The new path must receive a new numbered prefix.

### 7.5  Supersession vs. Path mutation

A superseded artifact (e.g., a Superseded FD) **remains at its original path**; only its `Status:` and `Superseded By:` header lines change. Supersession is not a path mutation.

## 8. Path-Validation Rules

A path is **valid** for a Foundation artifact if and only if:

1. The top-level subdirectory exists in `FOUNDATION/` and is listed in §3.2 or has been added by an FD.
2. The path matches the per-class storage pattern declared in §4 (or by a successor Standard / FD).
3. The file's filename conforms to the Foundation Naming Convention (Constitution §9).
4. The file's filename slug obeys the slug rules (Constitution §9: lowercase ASCII letters, digits, and hyphens; max 64 chars; no leading/trailing hyphen; must describe content).
5. The path does not collide with an existing `active` artifact at the same pattern slot.

A path that violates any of the above is a **Foundation-level incident** requiring an FD per `disagreement-and-escalation.md`.

## 9. Cross References

### 9.1  Mandatory References (Constitution §10.1)

Per Constitution §10.1, this Standard must reference:

- Constitution §1 (Governance Hierarchy)
- Constitution §9 (Naming Convention)
- Constitution §10 (Cross Reference Policy)
- Constitution §11 (Quality Gate)

This Standard also cross-references:

- `FOUNDATION/02-Governance/governance-model.md` — artifact types table; conflict resolution.
- `FOUNDATION/02-Governance/approval-workflow.md` — status lifecycle (for path-mutation FDs).
- `FOUNDATION/02-Governance/change-control-policy.md` — change categories (Path-mutation is a Major change).
- `FOUNDATION/02-Governance/disagreement-and-escalation.md` — escalation for path conflicts.
- `FOUNDATION/02-Governance/roles-and-authority.md` — role responsibilities.
- `FOUNDATION/08-RFCs/rfc-policy.md` — RFC storage paths (FRFC, PRFC, RRFC).
- `FOUNDATION/09-Decisions/foundation-decision-policy.md` — FD storage path.
- `FOUNDATION/10-ADRs/adr-policy.md` — ADR storage paths (F-ADR, P-ADR).

### 9.2  Back-References

Each Foundation artifact that names a directory path should reference this Standard in its `Related:` header field. Project-level artifacts (post-Foundation) should reference this Standard from their Project-level Directory Standard (issued via PRFC).

## 10. Compatibility

### 10.1  Version Surfaces

- **This Standard's version.** Header `Version: 0.1.0-draft`. Bump rules per Constitution §8.
- **Foundation version.** `FOUNDATION/VERSION` (currently `0.1.0-dev`).
- **Constitution version.** `constitution.md` header (currently `v0.1.0-draft` Provisional).

### 10.2  Backward Compatibility

This Standard guarantees backward compatibility for:

- The numbered-prefix ordering and the form `NN-scope-name`.
- The top-level subdirectory names declared in §3.2.
- The per-class storage paths declared in §4.

Adding a new top-level subdirectory, adding a new per-class storage path, or extending the reserved list is backward-compatible. Renaming or removing an existing top-level subdirectory is **not** backward-compatible and requires a MAJOR version bump per Constitution §8 and a Migration Plan per §2.4.

### 10.3  Forward Compatibility

Forward compatibility is not guaranteed by this Standard. A consumer written against a future version of this Standard may not operate on the current version.

### 10.4  Migration Compatibility

Any backward-incompatible change to this Standard must:

1. Publish a Migration Plan (in this Standard's directory or in an accompanying `MIGRATION-STD-DIR-<NN>.md`).
2. Place the previous version in `Migration Required` state (Constitution §12).
3. Enumerate every breaking change in the new version's FD.

## 11. Relationship to Other Artifacts

- **Constitution §9 (Naming Convention).** Constitution §9 binds filename patterns; this Standard binds directory paths. Together they form the canonical address of every Foundation artifact.
- **`governance-model.md` §6 (Artifact Types).** Each artifact type declared in `governance-model.md` §6 has a per-class storage path declared in §4 above.
- **`foundation-decision-policy.md` / `rfc-policy.md` / `adr-policy.md`.** Those policies bind the **content** of each artifact class; this Standard binds the **path** of each artifact class.
- **Change-Control Policy.** Path mutations are Major changes and require an FD.
- **Disagreement and Escalation.** Path conflicts are escalated per `disagreement-and-escalation.md`.

## 12. Ratification

This Directory Standard is itself **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred** — no `FD-0003-ratify-directory-standard.md` is created in Task 03. The Foundation Builder prepares the Standard; the human Architect reviews it via `REVIEW-FOUNDATION-03-directory.md`.

A future FD may ratify or supersede this Standard only if required by the Constitution, a later approved governance decision, or the Task 12 Foundation RC review. Task 12 will decide whether separate ratification is necessary. Until any such FD is issued, this Standard governs Foundation work **provisionally**, alongside the Provisional Constitution and the Task 02 Governance Model.

> Note: No `FD-0003-ratify-directory-standard.md` is created during Task 03. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action.

---

*End of Directory Standard v0.1.0-draft.*
