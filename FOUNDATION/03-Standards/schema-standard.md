# Research-OS Foundation — Schema Standard

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/03-Standards/schema-standard.md`
**Supersedes:** none
**Related:** Constitution v0.1.0-draft (Provisional) §2, §3, §9, §10, §11, §12, §13, §15; `FOUNDATION/03-Standards/directory-standard.md`; `FOUNDATION/02-Governance/governance-model.md` §6, §7; `FOUNDATION/02-Governance/approval-workflow.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/02-Governance/disagreement-and-escalation.md`; `FOUNDATION/02-Governance/roles-and-authority.md`; `FOUNDATION/08-RFCs/rfc-policy.md`; `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/10-ADRs/adr-policy.md`

---

## 1. Purpose and Scope

This Schema Standard defines the **canonical shape** of every Foundation artifact class used by Research-OS. A schema is a normative specification of the fields, headers, sections, validation rules, and lifecycle hooks that an artifact of a given class must instantiate. This Standard is the L3 Foundation Standard referenced by the Constitution §9 (Naming Convention) and by `governance-model.md` §6 (Artifact Types).

**Scope.** This Standard governs:

1. The field and section structure of every Foundation artifact class enumerated in `governance-model.md` §6 and in the Foundation Decision Policy, RFC Policy, ADR Policy, and Audit / Review / Report workflows.
2. The required headers, required sections, and required cross-references for each artifact class.
3. The validation criteria that the §11 Quality Gate audits apply to each artifact class.
4. The lifecycle hooks that couple each schema to the Governance Status Lifecycle (`governance-model.md` §7).

**Out of scope.**

- Project-local schemas (post-Foundation) — those are governed by Project RFCs (PRFCs) issued after the Foundation `v1.0.0-rc.1` release (Task 12). The Foundation defines the *shape of Project schemas*; it does not instantiate them.
- Engine, SDK, Plugin, or Workspace internal data shapes — those are governed by their own L5 specifications (Tasks 05–11).
- Serialization, transfer syntax, file format, or schema-engine binding — this Standard is **technology-neutral**. No JSON, YAML, XML, Protocol Buffers, JSON-Schema, OpenAPI, or other format binding is mandated. The schemas are normative field specifications; concrete serialization is a downstream Engine decision (Task 06).
- Implementations, code, executables, generators, validators, or runtime — explicitly out of scope for Task 04.

## 2. Normative Status

This Schema Standard is **Draft / In Review** at Foundation `0.1.0-dev`, Constitution `v0.1.0-draft` (Provisional). It is the L3 Foundation Standard that operationalizes Constitution §9 (Naming Convention) for *artifact shape* and §10 (Cross Reference Policy) for *required field form*.

**Conformance.** A Foundation artifact is conformant with this Standard if and only if:

- Its class is one of the nine classes defined in §4–§12 below, AND
- Its declared fields, sections, and cross-references satisfy the required-set, optional-set, and validation rules for that class, AND
- Its declared headers obey Constitution §9 (Naming Convention) and the Directory Standard §4 (Per-class storage paths).

**Conflict resolution.** Per `governance-model.md` §4:

1. Constitution prevails.
2. Higher `Status:` prevails.
3. Later SemVer version prevails.
4. Later ISO-8601 date prevails.
5. Higher-numbered ID prevails.
6. Otherwise escalate.

Where this Standard and the Constitution appear to conflict, the Constitution prevails. Where this Standard and an active FD appear to conflict, the FD prevails if its `Status:` is `Ratified`; otherwise this Standard governs provisionally.

**Technology neutrality.** This Standard does not bind the Foundation to any serialization format, schema-engine, validator, or runtime. A consumer (Engine, SDK, validator) claims conformance by demonstrating that for every artifact class in §4–§12, the same field set, required-set, optional-set, and validation rules are enforced. The mapping between schema fields and a concrete representation is the consumer's responsibility.

## 3. Schema Conventions

All nine schemas in §4–§12 share the following conventions.

### 3.1  Field Specification Form

Each field is documented as a tuple:

| Column | Meaning |
|---|---|
| Field | The kebab-case or snake-case identifier of the field. |
| Required | `R` (required, always present), `O` (optional, may be omitted), `C` (conditional, required when the stated condition holds). |
| Multiplicity | `1` (exactly one), `0..1` (zero or one), `0..*` (zero or more), `1..*` (one or more). |
| Type | A normative type description. Use `string`, `integer`, `decimal`, `boolean`, `date` (ISO-8601), `datetime` (ISO-8601 with timezone), `enum:<value-list>`, `ref:<path>`, `struct:<schema-id>`, `list:<type>`, `map<string,type>`. |
| Description | A normative prose description of the field's meaning and constraints. |

### 3.2  Header Block

Every Foundation artifact must include a header block consisting of six header fields, in this order:

1. `Status:` — value from the Governance Status Lifecycle (`governance-model.md` §7).
2. `Version:` — SemVer per Constitution §8.
3. `Foundation Version:` — the value of `FOUNDATION/VERSION` at the time the artifact was created or last revised.
4. `Path:` — the canonical directory path (Directory Standard §4).
5. `Supersedes:` — the ID of any artifact this one supersedes, or `none`.
6. `Related:` — a comma-separated list of cross-reference targets (Constitution §10).

### 3.3  Required Sections

Every schema §4–§12 declares a `Required Sections` table. The builder must include each section in the artifact body; the named section may be empty only if the schema explicitly marks it `empty-allowed: yes`.

### 3.4  Cross-Reference Form

Per Constitution §10.1, every artifact must reference:

- The Constitution version it is bound to (`Constitution v<X>.<Y>.<Z>`).
- The Foundation Decision (if any) that authorizes its class.
- The Foundation Standard (if any) that defines its shape.
- The companion policies (Governance, Approval Workflow, Change-Control, Disagreement & Escalation) where applicable.

References appear in the `Related:` header field and in the body via inline citations.

### 3.5  Validation Hooks

Each schema declares an `Audit Hooks` table that maps each §11 Quality Gate criterion to the specific validation rule that the §11 audit applies to instances of this class. The artifact is **Invalid** if any hook fails.

### 3.6  Lifecycle Hooks

Each schema declares a `Lifecycle Hooks` table that maps each Governance Status Lifecycle transition (per `governance-model.md` §7) to the side effects the artifact must record on entering that status. Lifecycle hooks are normative; an artifact that enters a status without performing the corresponding hooks is **Invalid**.

## 4. Evidence Schema

### 4.1  Class

**Evidence** is a Foundation artifact that records an observation, measurement, or fact retrieved or generated during Foundation work. Evidence is the L7 unit of record on which the Foundation's audit, review, and assertion chain is built. An Evidence record is the *lowest* class in the Foundation artifact hierarchy that is independently auditable.

**Identifier form.** `EVID-<scope>-NNNN-<slug>.md`. The `scope` is `FOUNDATION` for Foundation artifacts, or a Project code (post-Foundation). The Foundation does not bind a particular Evidence storage path; Evidence instances are stored at the location that the issuing workflow declares (Builder report appendices, Audit attachments, Review records, Pack manifests, or Project-local subtrees).

### 4.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`In Review`,`Approved`,`Archived`,`Withdrawn` | Evidence is not eligible for `Ratified` status (only FDs and Constitution are). |
| `Version` | R | 1 | string (SemVer) | Per Constitution §8. |
| `Foundation Version` | R | 1 | string (SemVer) | `FOUNDATION/VERSION` at creation. |
| `Path` | R | 1 | ref:`directory-standard.md` §4 | Storage path. |
| `Supersedes` | R | 1 | ref:`Evidence-ID` or `none` | See `governance-model.md` §9. |
| `Related` | R | 1..* | list:ref | At least one: the consuming artifact (Report, Audit, Review, Pack, Manifest). |
| `ID` | R | 1 | string (matches header pattern) | Unique Evidence identifier. |
| `Collected-At` | R | 1 | datetime (ISO-8601) | When the evidence was originally observed. |
| `Collected-By` | R | 1 | role (per `roles-and-authority.md`) | The role that collected the evidence. |
| `Source` | R | 1 | string | Human-readable description of the source. Not a runtime reference. |
| `Method` | O | 0..1 | string | How the evidence was produced. |
| `Hash` | O | 0..1 | string (hex digest) | Optional content hash for tamper detection. |
| `Attachments` | O | 0..* | list:ref:`Attachment` | External references; the attachment format is **not** bound by this Standard. |

### 4.3  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | One sentence: what this evidence records. |
| §2 Observation | R | The observation itself, in a technology-neutral form. |
| §3 Conditions | R | The conditions under which the observation was made. |
| §4 Limitations | R | Known limits, biases, or caveats. |
| §5 References | R | Cross-references to the consuming artifact and any policy section. |

### 4.4  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §4.2 required fields present; all §4.3 required sections present. |
| Compliance | `Status:` is in the allowed set; `Collected-At` is ISO-8601; `ID` matches the header pattern. |
| Cross Reference | Every `Related:` target resolves; `Source` is human-readable. |
| Isolation | No Project-specific domain content; the observation is expressible without reference to any Project (e.g., APES). |

### 4.5  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | Author sets `Submitted-At` field (optional). |
| `Submitted` → `In Review` | Reviewer attaches a Review Record reference. |
| `In Review` → `Approved` | `Approved-By` and `Approved-At` fields populated (optional); the artifact is now consumable. |
| `Approved` → `Archived` | `Archived-At` populated (optional). |
| any → `Superseded` | `Superseded By:` field populated; the original record remains at its path. |

## 5. Report Schema

### 5.1  Class

**Report** is a Foundation artifact produced by a Builder describing what was done, what was found, and what remains to be done under the Foundation Task Protocol (`Constitution §15`). Reports are the primary mechanism by which a Builder is held accountable for the work performed under a Task. The Foundation distinguishes **Task Reports** (eight-section, per Task 04+) and **Builder Reports** (general).

**Identifier form.** `REPORT-<scope>-<NN>-<slug>.md`. `scope` is `FOUNDATION` for Foundation-level Reports. Storage: `FOUNDATION/06-Reports/` (Directory Standard §4.8).

### 5.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`In Review`,`Approved`,`Changes Requested`,`Withdrawn` | (Builder Reports follow the standard set.) |
| `Version` | R | 1 | string (SemVer) | Per Constitution §8. |
| `Foundation Version` | R | 1 | string (SemVer) | `FOUNDATION/VERSION` at creation. |
| `Path` | R | 1 | ref:`directory-standard.md` §4.8 | Storage path. |
| `Supersedes` | R | 1 | ref:`Report-ID` or `none` | |
| `Related` | R | 1..* | list:ref | Must include the Task ID, the Audit Record, and the Review Record. |
| `Task-ID` | R | 1 | string | The Foundation Task being reported on. |
| `Builder` | R | 1 | role | The Builder role that produced the report. |
| `Date` | R | 1 | date (ISO-8601) | Report date. |
| `Foundation-Version-Target` | R | 1 | string (SemVer) | The Foundation version the report accepts as binding. |

### 5.3  Required Sections (Task Report, eight-section)

Per Constitution §15.2 and the Architect's instruction for Task 04, the eight required sections are:

| # | Section | Required? | Notes |
|---|---|---|---|
| 1 | Summary | R | One paragraph: what this Task did. |
| 2 | Files Created | R | Path-relative list. |
| 3 | Files Modified | R | Path-relative list. |
| 4 | Acceptance Checklist | R | Mirrors the §15.5 scope declaration. |
| 5 | Verification | R | Step-by-step verification of Hard Prohibitions and §11 Quality Gate. |
| 6 | Remaining Limitations | R | Honest list of what is NOT done. |
| 7 | Git Status | R | Branch, commit, push, tag (or "none" for each). |
| 8 | Next Recommended Task | R | One sentence: the next Task the Architect should authorize. |

For non-Task Reports (general Builder Reports), sections 1–8 are required but the section titles may be re-named to suit the report's purpose, provided the eight-section structure is preserved.

### 5.4  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All eight sections present; all §5.2 required fields present. |
| Compliance | `Status:` is in the allowed set; `Task-ID` resolves to a Foundation Task in the Task table; `Foundation-Version-Target` matches `FOUNDATION/VERSION`. |
| Cross Reference | `Related:` targets include the Task ID, Audit, and Review and resolve. |
| Isolation | No Project-specific governance, lifecycle, schema, or implementation rule. |

### 5.5  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `In Review` | Submitted alongside the Audit and Review Records for the same Task. |
| `In Review` → `Approved` | Architect disposition recorded in the Review Record. |
| `In Review` → `Changes Requested` | Architect specifies the corrections in the Review Record. |
| `Approved` → (stop) | The Builder stops; no further Task work proceeds until the Architect authorizes the next Task. |

## 6. Review Schema

### 6.1  Class

**Review** is a Foundation artifact that records the human Architect's or Reviewer's disposition of a Task, a Standard, a Decision, or an RFC. The Review Record is the only Foundation artifact that may carry a human disposition. It is binding when its `Status:` is `Approved`.

**Identifier form.** `REVIEW-<scope>-<NN>-<slug>.md`. Storage: `FOUNDATION/07-Reviews/` (Directory Standard §4.7).

### 6.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Pending`,`Approved`,`Approved with Notes`,`Changes Requested`,`Rejected`,`Withdrawn` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | |
| `Path` | R | 1 | ref:`directory-standard.md` §4.7 | |
| `Supersedes` | R | 1 | ref:`Review-ID` or `none` | |
| `Related` | R | 1..* | list:ref | Includes the Subject, the Audit Report, and the Task Report. |
| `Subject` | R | 1 | ref:`Artifact-ID` | The artifact under review. |
| `Reviewer` | R | 1 | role | The reviewing role. |
| `Review-Date` | C | 0..1 | date (ISO-8601) | Required when `Status:` is not `Pending`. |
| `Signature` | C | 0..1 | string | Required when `Status:` is `Approved` or `Approved with Notes`. May not be fabricated (per `governance-model.md` §5.3). |

### 6.3  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | What this Review records. |
| §2 Materials Reviewed | R | Enumerated list of artifacts examined. |
| §3 Disposition Checkboxes | R | Itemized checkbox list (one per §11 criterion and per §4 §4.3 / §5.3 / etc. requirement). |
| §4 Authorization for Next Step | R | Section that explicitly authorizes (or holds) the next Task. |
| §5 Required Corrections | C | Required when `Status:` is `Changes Requested` or `Rejected`; otherwise omitted. |
| §6 Reviewer Notes | O | Optional free-form notes. |
| §7 Disposition Summary | R | A table summarizing the Reviewer, Date, Signature, and Authorization. |

### 6.4  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §6.2 required fields present; all §6.3 required sections present. |
| Compliance | `Status:` is in the allowed set; `Signature` is present iff `Status:` is `Approved` or `Approved with Notes`; `Review-Date` is present iff `Status:` is not `Pending`. |
| Cross Reference | `Subject` resolves; every `Related:` target resolves. |
| Isolation | Project-independence preserved across Disposition Checkboxes. |

### 6.5  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Pending` → `Approved` | `Review-Date` and `Signature` populated; `Authorization for Next Step` populated. |
| `Pending` → `Changes Requested` | `Required Corrections` section populated with itemized corrections. |
| `Pending` → `Rejected` | `Required Corrections` section populated; the Builder must not retry the same Task. |

## 7. Statistics Schema

### 7.1  Class

**Statistics** is a Foundation artifact that records a quantitative measurement of Foundation work, such as FD counts by status, RFC counts by class, audit findings by severity, or count of Foundation artifacts under `FOUNDATION/VERSION`. Statistics is **descriptive**, not authoritative: it summarizes what is on disk; it does not modify or supersede the artifacts it summarizes.

**Identifier form.** `STATS-<scope>-<NN>-<slug>.md`. Storage: `FOUNDATION/05-Statistics/` (Directory Standard §6 — directory reserved; no files until Task 12).

### 7.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`Approved`,`Archived` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | |
| `Path` | R | 1 | ref:`directory-standard.md` §6 | |
| `Supersedes` | R | 1 | ref:`Stats-ID` or `none` | |
| `Related` | R | 1..* | list:ref | The source set of artifacts summarized. |
| `Scope` | R | 1 | ref:`scope` | `FOUNDATION`, a Project code, or a sub-scope. |
| `As-Of` | R | 1 | datetime (ISO-8601) | Snapshot timestamp. |
| `Method` | R | 1 | string | Description of how the statistic was computed. **No runtime binding.** |
| `Count` | O | 0..* | list:struct:`Statistic` | One entry per reported metric. |

### 7.3  Statistics Sub-Structure

A `Statistic` struct is:

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Name` | R | 1 | string | The metric name (e.g., `FD.count.Pending-Ratification`). |
| `Value` | R | 1 | decimal | The numeric value. |
| `Unit` | O | 0..1 | string | The unit of measure. |
| `Source-Reference` | R | 1 | ref:`Artifact-ID` | The artifact(s) whose state contributed to the value. |

### 7.4  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | What was measured and why. |
| §2 Method | R | The computation method (technology-neutral). |
| §3 Results | R | One table per reported metric. |
| §4 Limitations | R | Known gaps in the snapshot (e.g., "FD-0001 counted once even though it cycles through Pending Ratification"). |
| §5 References | R | Cross-references to the source artifacts. |

### 7.5  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §7.2 required fields and §7.4 required sections present. |
| Compliance | `As-Of` is ISO-8601; `Method` is human-readable; every `Count[*].Source-Reference` resolves. |
| Cross Reference | Every `Source-Reference` resolves; every `Related:` target resolves. |
| Isolation | No Project-specific quantitative metric; methodology is technology-neutral. |

### 7.6  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | All `Count` entries populated. |
| `Submitted` → `Approved` | Snapshot is locked; later edits must be a new `STATS-...` record. |

## 8. Manifest Schema

### 8.1  Class

**Manifest** is a Foundation artifact that enumerates the contents of a collection: a Foundation Pack, a Release, a Project subtree, or a Workspace. A Manifest is **declarative** — it does not change the contents; it records what is present and how the contents relate to each other. A Manifest is the primary cross-reference target for downstream validators.

**Identifier form.** `MANIFEST-<scope>-<slug>.md`. Storage: declared by the owning collection (e.g., a Pack's `MANIFEST-<pack>.md` lives alongside the Pack; a Release's Manifest lives at the Release root post-Foundation).

### 8.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`Approved`,`Archived` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | |
| `Path` | R | 1 | ref:`directory-standard.md` §4 | Path of the Manifest itself. |
| `Supersedes` | R | 1 | ref:`Manifest-ID` or `none` | |
| `Related` | R | 1..* | list:ref | The collection being enumerated. |
| `Collection` | R | 1 | ref:`Collection-ID` | The Pack, Release, Project, or Workspace this manifest describes. |
| `Generated-At` | R | 1 | datetime (ISO-8601) | Snapshot timestamp. |
| `Entry-Count` | R | 1 | integer | Number of entries in the manifest. |
| `Hash` | O | 0..1 | string (hex digest) | Optional digest of the manifest contents. |

### 8.3  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | What collection is enumerated. |
| §2 Entries | R | A table of `Entry` structs (see §8.4). |
| §3 Integrity | R | Hashes, signing notes (technology-neutral). |
| §4 References | R | Cross-references to the owning collection. |

### 8.4  Entry Sub-Structure

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Path` | R | 1 | string | Path-relative entry path. |
| `Class` | R | 1 | enum:`FD`,`FRFC`,`RRFC`,`PRFC`,`ADR`,`Audit`,`Review`,`Report`,`Evidence`,`Standard`,`Manifest`,`Stats`,`Task`,`Pack`,`Release`,`Other` | Artifact class. |
| `ID` | R | 1 | string | Identifier of the entry. |
| `Status` | R | 1 | enum:`...` (per class) | Status of the entry at `Generated-At`. |
| `Version` | R | 1 | string (SemVer) | Version of the entry. |
| `Hash` | O | 0..1 | string (hex digest) | Optional digest. |

### 8.5  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §8.2 required fields and §8.3 required sections present. |
| Compliance | `Collection` resolves to a known collection; `Entry-Count` equals `len(Entries)`. |
| Cross Reference | Every `Entry.ID` resolves to an extant artifact. |
| Isolation | Manifest is technology-neutral; no schema-engine binding. |

### 8.6  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | All entries populated; `Hash` recomputed (optional). |
| `Submitted` → `Approved` | Manifest is locked; re-validation produces a new Manifest. |

## 9. Audit Schema

### 9.1  Class

**Audit** is a Foundation artifact that records the result of a §11 Quality Gate audit against a given Subject. An Audit is the formal mechanism by which a Foundation artifact is certified to meet the four §11 criteria (Completeness, Compliance, Cross Reference, Isolation). An Audit Record is itself subject to the Quality Gate — a missing Audit hook is itself a Compliance defect.

**Identifier form.** `AUDIT-<scope>-<NN>-<slug>.md`. Storage: `FOUNDATION/04-Audits/` (Directory Standard §4.6).

### 9.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`Approved`,`Changes Requested`,`Rejected` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | |
| `Path` | R | 1 | ref:`directory-standard.md` §4.6 | |
| `Supersedes` | R | 1 | ref:`Audit-ID` or `none` | |
| `Related` | R | 1 | list:ref | The Subject being audited. |
| `Audit-ID` | R | 1 | string (matches header pattern) | |
| `Subject` | R | 1 | ref:`Artifact-ID` | The artifact audited. |
| `Auditor` | R | 1 | role | The auditing role. |
| `Audit-Standard` | R | 1 | ref:`Constitution §11` | Always the §11 Quality Gate, unless explicitly extended by an FD. |
| `Audit-Date` | R | 1 | date (ISO-8601) | |
| `Verdict` | R | 1 | enum:`PASS`,`PASS with Notes`,`FAIL` | Overall verdict. |
| `Finding-Count` | R | 1 | integer | Count of findings (zero or more). |

### 9.3  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Audit Scope | R | Subject, criteria, and exclusions. |
| §2 Quality Gate Results | R | One sub-section per §11 criterion. |
| §3 Per-Task Scope Verification | C | Required when the Audit accompanies a Task; verifies §15.5 scope. |
| §4 Findings | R | Itemized list (Critical, Major, Minor, Observation). Empty if `Finding-Count: 0`. |
| §5 Audit Conclusion | R | Restates the verdict. |

### 9.4  Finding Sub-Structure

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Severity` | R | 1 | enum:`Critical`,`Major`,`Minor`,`Observation` | |
| `Criterion` | R | 1 | enum:`Completeness`,`Compliance`,`Cross Reference`,`Isolation` | |
| `Ref` | R | 1 | ref:`path#section` | Where the defect lies. |
| `Summary` | R | 1 | string | Compressed label. |
| `Description` | R | 1 | string | Prose description. |
| `Failure-Scenario` | R | 1 | string | Concrete input or state that triggers the defect. |
| `Recommendation` | O | 0..1 | string | Suggested fix. |

### 9.5  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §9.2 required fields and §9.3 required sections present. |
| Compliance | `Audit-Standard` resolves to Constitution §11; `Verdict` is in the allowed set; `Verdict` is `PASS` or `PASS with Notes` only if `Finding-Count` is zero or all findings are `Observation`. |
| Cross Reference | `Subject` resolves; every `Finding.Ref` resolves. |
| Isolation | Audit methodology is technology-neutral; no Project-specific rule. |

### 9.6  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | Submitted with the Report and Review for the same Task. |
| `Submitted` → `Approved` | Findings are absorbed into the Builder's next Task Report. |
| `Submitted` → `Changes Requested` | The Builder revises the Subject and re-runs the Audit. |

## 10. Task Schema

### 10.1  Class

**Task** is a Foundation artifact that defines a single cycle of work under the Foundation Task Protocol (Constitution §15). A Task is the unit of accountability for the Builder role. Each Task produces a Task Report, an Audit Record, and a Review Record. Tasks are **declared** by the Architect (or by the Builder under §15.5) and **closed** when the Architect approves the Review Record.

**Identifier form.** `TASK-<scope>-<NN>-<slug>.md`. Storage: alongside the Task Report (typically `FOUNDATION/06-Reports/`), or in a Task index at the Foundation level. The Foundation does not yet maintain a per-Task file at `FOUNDATION/03-Standards/`; the Task Schema is normative for any future Task-tracking artifact.

### 10.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Authorized`,`In Progress`,`Submitted`,`Approved`,`Changes Requested`,`Rejected`,`Withdrawn` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | The Foundation version the Task targets. |
| `Path` | R | 1 | ref:`directory-standard.md` §4 | |
| `Supersedes` | R | 1 | ref:`Task-ID` or `none` | |
| `Related` | R | 1..* | list:ref | The Foundation Task list, the prior Task's Report, the Targets Standard. |
| `Task-ID` | R | 1 | string (matches header pattern) | `FOUNDATION-<NN>` for Foundation Tasks. |
| `Name` | R | 1 | string | Human-readable Task name. |
| `Owner` | R | 1 | role | The Builder role. |
| `Authorization-Date` | C | 0..1 | date (ISO-8601) | Required when `Status:` is `Authorized` or later. |
| `Completion-Date` | C | 0..1 | date (ISO-8601) | Required when `Status:` is `Approved`. |
| `Foundation-Version-Target` | R | 1 | string (SemVer) | The Foundation version the Task targets. |

### 10.3  Task Scope Declaration (Constitution §15.5)

Every Task must declare its scope as a structured block. The Task Schema does not bind the field names beyond the section names; the schema declares the *required sub-sections* of the scope declaration.

| Sub-Section | Required? | Purpose |
|---|---|---|
| `Allowed Files` | R | Files that may be created or updated. |
| `Forbidden Files` | R | Files that must not be touched. |
| `Inputs` | R | Artifacts and policies the Task depends on. |
| `Outputs` | R | Artifacts the Task will produce. |
| `Dependencies` | R | Task IDs and Foundation Decisions that gate the Task. |
| `Quality Gates` | R | The §11 hooks and any Task-specific gates. |
| `Stop Condition` | R | The phase after which the Builder halts and awaits human approval. |

### 10.4  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | One paragraph: what this Task does. |
| §2 Task Scope Declaration | R | The §15.5 structured block. |
| §3 Hard Prohibitions Acknowledged | R | Itemized list of §15.3 prohibitions observed. |
| §4 Acceptance Criteria | R | Itemized list mirroring the Acceptance Checklist. |
| §5 References | R | Cross-references to the prior Task, the Constitution, and the Standard being produced. |

### 10.5  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §10.2 required fields and §10.4 required sections present. |
| Compliance | `Status:` is in the allowed set; `Authorization-Date` populated iff `Status` is `Authorized` or later; `Completion-Date` populated iff `Status` is `Approved`. |
| Cross Reference | Every item in `Related:` resolves; `Foundation-Version-Target` matches `FOUNDATION/VERSION`. |
| Isolation | No Project-specific governance, lifecycle, schema, or implementation rule. |

### 10.6  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Authorized` | `Authorization-Date` set; the Builder may begin work. |
| `Authorized` → `In Progress` | Builder creates the Task Report, Audit, and Review drafts. |
| `In Progress` → `Submitted` | All three companion artifacts submitted. |
| `Submitted` → `Approved` | `Completion-Date` set; the next Task is now eligible for authorization. |
| `Submitted` → `Changes Requested` | The Builder revises and re-submits. |
| `Submitted` → `Rejected` | The Task terminates; the next Task may be a different scope. |

## 11. Pack Schema

### 11.1  Class

**Pack** is a Foundation artifact that bundles a coherent set of Foundation artifacts (a Standard, a Manifest, and its companion Audit/Report/Review records) for distribution or review. A Pack is **immutable** once Approved — corrections are made by issuing a new Pack version. Foundation Packs are the L5 unit of distribution for Foundation Standards.

**Identifier form.** `PACK-<scope>-<slug>.md` (the Pack manifest) plus the bundled files. The Foundation does not yet define a storage location for Packs; the pack directory is announced by the issuing FD or Standard.

### 11.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`Approved`,`Archived` | |
| `Version` | R | 1 | string (SemVer) | |
| `Foundation Version` | R | 1 | string (SemVer) | The Foundation version the Pack targets. |
| `Path` | R | 1 | ref:`directory-standard.md` §4 | Path of the Pack manifest. |
| `Supersedes` | R | 1 | ref:`Pack-ID` or `none` | |
| `Related` | R | 1..* | list:ref | Every artifact bundled in the Pack. |
| `Pack-ID` | R | 1 | string (matches header pattern) | |
| `Pack-Type` | R | 1 | enum:`Standard`,`Decision`,`Release`,`Tool` | The kind of Pack. |
| `Contents` | R | 1..* | list:struct:`Pack-Entry` | The bundled artifacts. |
| `Hash` | R | 1 | string (hex digest) | Digest of the Pack contents. |
| `Approved-By` | C | 0..1 | role | Required when `Status:` is `Approved`. |
| `Approved-At` | C | 0..1 | date (ISO-8601) | Required when `Status:` is `Approved`. |

### 11.3  Pack-Entry Sub-Structure

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Path` | R | 1 | string | Path of the bundled file. |
| `Class` | R | 1 | enum:`Standard`,`Decision`,`RFC`,`ADR`,`Audit`,`Review`,`Report`,`Manifest`,`Other` | |
| `ID` | R | 1 | string | Identifier of the bundled artifact. |
| `Version` | R | 1 | string (SemVer) | |
| `Hash` | R | 1 | string (hex digest) | Digest of the bundled file. |

### 11.4  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | What this Pack bundles. |
| §2 Contents | R | The `Pack-Entry` table. |
| §3 Integrity | R | Hash strategy; signing notes (technology-neutral). |
| §4 References | R | Cross-references to related Standards and FDs. |
| §5 Acceptance Notification | R | How downstream consumers are notified. |

### 11.5  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §11.2 required fields and §11.4 required sections present. |
| Compliance | `Hash` is present; every `Contents[*].Hash` matches the bundled file's digest. |
| Cross Reference | Every `Contents[*].ID` resolves; every `Related:` target resolves. |
| Isolation | Pack is technology-neutral; no Project-specific rule. |

### 11.6  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | All `Contents` populated; `Hash` computed. |
| `Submitted` → `Approved` | `Approved-By` and `Approved-At` set; the Pack is immutable. |
| `Approved` → `Archived` | The Pack is superseded by a later Pack. |

## 12. Release Schema

### 12.1  Class

**Release** is a Foundation artifact that declares a Foundation version state milestone (e.g., `0.1.0-dev`, `0.1.0-rc.1`, `1.0.0`). A Release is the **only** artifact that may move the Foundation version (`FOUNDATION/VERSION`) forward. The Foundation RC gate is reserved for Task 12; until then, no Release may declare `1.0.0-rc.1` or `1.0.0` (Constitution §15.3 hard prohibition).

**Identifier form.** `RELEASE-<scope>-<slug>.md`. Storage: post-Foundation (the Foundation does not create a `FOUNDATION/16-Releases/` directory until Task 12).

### 12.2  Header Block

| Field | Required | Multiplicity | Type | Description |
|---|---|---|---|---|
| `Status` | R | 1 | enum:`Draft`,`Submitted`,`Approved`,`Superseded`,`Archived` | |
| `Version` | R | 1 | string (SemVer) | The version declared by this Release. |
| `Foundation Version` | R | 1 | string (SemVer) | The Foundation version *before* this Release is applied. |
| `Path` | R | 1 | ref:`directory-standard.md` §4 | |
| `Supersedes` | R | 1 | ref:`Release-ID` or `none` | |
| `Related` | R | 1..* | list:ref | The authorizing FD; the Manifest; the Packs. |
| `Release-ID` | R | 1 | string (matches header pattern) | |
| `Release-Type` | R | 1 | enum:`dev`,`alpha`,`beta`,`rc`,`ga` | Per Constitution §8. |
| `Foundation-Version-New` | R | 1 | string (SemVer) | The Foundation version *after* this Release is applied. |
| `Authorizing-FD` | R | 1 | ref:`FD-NNNN` | The FD that authorizes the Release. |
| `Manifest` | R | 1 | ref:`Manifest-ID` | The Manifest of the Release. |
| `Compatibility-Statement` | R | 1 | string | Backward/forward/migration statement per Constitution §2. |
| `Migration-Plan` | O | 0..1 | ref:`Migration-Plan-ID` | Required when `Compatibility-Statement` declares a breaking change. |
| `Release-Manager` | R | 1 | role | The Release Manager role. |
| `Release-Date` | C | 0..1 | date (ISO-8601) | Required when `Status:` is `Approved`. |

### 12.3  Required Sections

| Section | Required? | Notes |
|---|---|---|
| §1 Purpose | R | What this Release declares. |
| §2 Eligibility | R | Pre-conditions checked (e.g., Constitution ratified, Standards approved, Hard Prohibitions cleared). |
| §3 Version Impact | R | `Foundation-Version-Target` pre vs. post. |
| §4 Compatibility | R | Backward, forward, migration statements. |
| §5 Manifest | R | Embeds or references the Release Manifest. |
| §6 Migration Plan | C | Required when `Migration-Plan` is present; else omitted. |
| §7 References | R | Cross-references to authorizing FD, Packs, and Standards. |

### 12.4  Audit Hooks

| §11 Criterion | Rule |
|---|---|
| Completeness | All §12.2 required fields and §12.3 required sections present. |
| Compliance | `Release-Type` is in the allowed set; `Authorizing-FD` resolves; `Foundation-Version-New` is a valid SemVer bump from `Foundation-Version`; no `rc` or `ga` Release before Task 12 passes (per §15.3). |
| Cross Reference | `Authorizing-FD` resolves; `Manifest` resolves; every `Related:` target resolves. |
| Isolation | Release is technology-neutral; no Project-specific rule. |

### 12.5  Lifecycle Hooks

| Transition | Hook |
|---|---|
| `Draft` → `Submitted` | Eligibility section verified; `FOUNDATION/VERSION` not yet changed. |
| `Submitted` → `Approved` | `Release-Date` set; `FOUNDATION/VERSION` updated to `Foundation-Version-New`; Manifest uploaded. |
| `Approved` → `Superseded` | A later Release takes effect; `Superseded By:` populated. |

## 13. Cross References

### 13.1  Mandatory References (Constitution §10.1)

This Standard references:

- Constitution §1 (Governance Hierarchy)
- Constitution §2 (Compatibility Policy)
- Constitution §3 (Design Principles)
- Constitution §9 (Naming Convention)
- Constitution §10 (Cross Reference Policy)
- Constitution §11 (Quality Gate)
- Constitution §12 (Deprecation Policy)
- Constitution §13 (Future Extension Policy)
- Constitution §15 (Foundation Task Protocol)

### 13.2  Companion Standards and Policies

- `FOUNDATION/03-Standards/directory-standard.md` — Per-class storage paths (`§4`).
- `FOUNDATION/02-Governance/governance-model.md` §6 — Artifact Types.
- `FOUNDATION/02-Governance/governance-model.md` §7 — Governance Status Lifecycle.
- `FOUNDATION/02-Governance/approval-workflow.md` — Transition authority.
- `FOUNDATION/02-Governance/change-control-policy.md` — Field mutations require an FD.
- `FOUNDATION/02-Governance/disagreement-and-escalation.md` — Schema conflicts.
- `FOUNDATION/02-Governance/roles-and-authority.md` — Role assignments.
- `FOUNDATION/08-RFCs/rfc-policy.md` — RFC schema inputs.
- `FOUNDATION/09-Decisions/foundation-decision-policy.md` — FD schema inputs.
- `FOUNDATION/10-ADRs/adr-policy.md` — ADR schema inputs.

### 13.3  Back-References

Every Foundation artifact that conforms to one of the nine schemas should reference this Standard in its `Related:` header field, with the schema identifier: `Related: Schema Standard v0.1.0-draft (Evidence Schema / Report Schema / ...)`.

## 14. Compatibility

### 14.1  Version Surfaces

- **This Standard's version.** Header `Version: 0.1.0-draft`. Bump rules per Constitution §8.
- **Foundation version.** `FOUNDATION/VERSION` (currently `0.1.0-dev`).
- **Constitution version.** `constitution.md` header (currently `v0.1.0-draft` Provisional).

### 14.2  Backward Compatibility

This Standard guarantees backward compatibility for:

- The presence of each of the nine schemas; new schemas may be added, none removed without a MAJOR bump.
- The required-field sets; required fields may be added (additive growth) but may not be removed.
- The required-section sets; required sections may be added but may not be removed.
- The §11 Quality Gate audit hooks per schema; new hooks may be added but may not be silently removed.

A schema's enumeration may be **extended** backward-compatibly (new `Status:` values, new fields, new sections). A schema's enumeration may not be **contracted** without a MAJOR bump and a Migration Plan per §2.4.

### 14.3  Forward Compatibility

Forward compatibility is not guaranteed. A consumer written against a future version of this Standard may not operate on the current version.

### 14.4  Migration Compatibility

Any backward-incompatible change to this Standard must:

1. Publish a Migration Plan (in this Standard's directory or in an accompanying `MIGRATION-STD-SCHEMA-<NN>.md`).
2. Place the previous version in `Migration Required` state (Constitution §12).
3. Enumerate every breaking change in the new version's FD.

## 15. Relationship to Other Artifacts

- **Constitution §9 (Naming Convention).** Constitution §9 binds filename patterns and the `STD-<area>-vX.Y.Z.md` convention. This Standard binds the *field shape* of each artifact class.
- **Directory Standard.** The Directory Standard binds the *path* of each artifact class; this Standard binds the *shape* of each artifact class. Together they form the canonical address and form of every Foundation artifact.
- **`governance-model.md` §6 (Artifact Types).** Each artifact type declared in `governance-model.md` §6 has a schema defined in §4–§12 of this Standard.
- **`governance-model.md` §7 (Governance Status Lifecycle).** Each schema in §4–§12 declares its Lifecycle Hooks in its own section.
- **Foundation Decision Policy, RFC Policy, ADR Policy.** Those policies define the **content rules** for each artifact class; this Standard defines the **shape rules**. They are co-equal normative inputs.
- **Change-Control Policy.** A schema mutation is a Major change and requires an FD.
- **Disagreement and Escalation.** Schema conflicts are escalated per `disagreement-and-escalation.md`.

## 16. Ratification

This Schema Standard is itself **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred** — no `FD-0004-ratify-schema-standard.md` is created in Task 04. The Foundation Builder prepares the Standard; the human Architect reviews it via `REVIEW-FOUNDATION-04-schema.md`.

A future FD may ratify or supersede this Standard only if required by the Constitution, a later approved governance decision, or the Task 12 Foundation RC review. Until any such FD is issued, this Standard governs Foundation work **provisionally**, alongside the Provisional Constitution, the Task 02 Governance Model, and the Task 03 Directory Standard.

> Note: No `FD-0004-ratify-schema-standard.md` is created during Task 04. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action.

---

*End of Schema Standard v0.1.0-draft.*
