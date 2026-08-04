# Research-OS Constitution

**Status:** Ratified
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev (see `FOUNDATION/VERSION`)
**Effective:** upon ratification by `FD-0001` on 2026-08-03; per `FD-0001` Approver Signature and §17.3 Ratification Sequence
**Supersedes:** v0.2 (draft)
**Path:** `FOUNDATION/01-Constitution/constitution.md`
**Ratified By:** `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md` (Status: Ratified; ratifies-constitution: 0.1.0-draft)

> **Note on status.** This Constitution is **Ratified** as of 2026-08-03 by `FD-0001`. Per the Architect's Decision (2026-08-03): the Constitution's `Status:` is updated from `Provisional` to `Ratified`, but its `Version:` line remains `0.1.0-draft` because the version-semantics ambiguity (whether ratification removes the `-draft` suffix) is recorded for resolution in a subsequent Maintenance RFC rather than invented here. Foundation `v1.0.0-rc.1` is still **not** declared by this ratification; Task 12 remains the only Foundation RC gate (Constitution §14.1, §17.3 step 5; FD-0001 §4). Standards remain Draft / In Review; no Pack, no Workspace, no Project, no Engine, no SDK, no Plugin, no Runtime is created. APES remains Frozen. Foundation remains Frozen except for changes authorized through approved RFCs (Foundation Change Principle, recorded in FD-0001 §8).

---

## §0  Preamble

Research-OS is a long-term maintained **meta-platform** for hosting research repositories. It is not a single project, not a framework, not an application. It is a governed platform upon which unlimited research Projects will be built over time.

APES is the **first** Project hosted on Research-OS, but APES is not the platform. APES is one tenant. All architecture, all Standards, and all governance remain valid in the complete absence of APES.

This Constitution is **technology-independent**, **project-independent**, and **implementation-independent**. It does not prescribe languages, frameworks, vendors, or workflows specific to any Project. It governs only the rules under which any Project may exist.

No Project, no Standard, no Engine, no RFC, no FD, and no Builder may override this Constitution. Any conflict is resolved by the precedence rules in §1.

---

## §1  Governance Hierarchy

All Foundation artifacts are governed by the following seven-layer hierarchy. Higher layers override lower layers when in conflict.

| Layer | Artifact Type | Authority | Mutability |
|---|---|---|---|
| L1 | Constitution | Supreme | Only via amendment (§17) |
| L2 | Foundation Decision (FD) | Architectural | Only via superseding FD |
| L3 | Foundation RFC (FRFC) | Normative proposal | Accepted FDs may ratify |
| L4 | Platform Standard (STD) | Normative | Only via amendment + FD |
| L5 | Engine Specification | Normative for Engines | Only via amendment + FD |
| L6 | Project Standard, Sprint, Task, Release | Project scope | Project RFC (PRFC) |
| L7 | Builder artifact (Report, Audit, Review) | Operational | Builder-author |

**Conflict resolution rules:**

1. If a lower-layer artifact conflicts with a higher-layer artifact, the higher-layer artifact prevails.
2. If two artifacts at the same layer conflict, the artifact with the later `version` prevails.
3. If versions tie, the artifact with the later `date` prevails.
4. If dates tie, the artifact whose ID sorts later prevails.
5. Any unresolved conflict must be escalated via a new FRFC and resolved via a new FD.

**Normative references between layers are mandatory and bidirectional (§10).**

---

## §2  Compatibility Policy

### §2.1  Version Surfaces

Research-OS maintains three independent version surfaces:

- **Foundation version** — `FOUNDATION/VERSION` (currently `0.1.0-dev`).
- **Constitution version** — header of `constitution.md` (currently `0.1.0-draft`).
- **Per-Standard version** — header of each Standard (currently unset; each Standard starts at `0.1.0-draft` upon creation).

No version surface may be promoted to `1.0.0-rc.1` or `1.0.0` until the corresponding release milestone has passed review.

### §2.2  Backward Compatibility

An artifact is **backward-compatible** if any consumer written against its previous version continues to function without modification after the upgrade.

Foundation guarantees backward compatibility for:

- Constitution semantic structure (§0–§17 enumeration).
- Naming conventions (§9).
- Quality Gate criteria (§11).
- Foundation Task Protocol (§15).
- Cross Reference rules (§10).

### §2.3  Forward Compatibility

An artifact is **forward-compatible** if a consumer written against its newer version can operate on the older artifact without modification.

Foundation does not guarantee forward compatibility unless explicitly stated in an FD.

### §2.4  Migration Compatibility

When backward compatibility cannot be preserved:

1. A Migration Standard must be published.
2. The previous version enters the **Migration Required** state (§12).
3. Consumers must complete migration before the previous version is **Archived**.
4. The new version's FD must enumerate every breaking change.

### §2.5  Violation Handling

Any violation of the Compatibility Policy is a **Foundation-level incident** requiring:

- Immediate halt of the offending work.
- An Audit Report (`AUDIT-FOUNDATION-<NN>-<slug>.md`).
- An FD documenting disposition.
- A new version bump per §8.

---

## §3  Design Principles

The Foundation is built on the following principles. These expand and supersede the original ten Execution Principles (§16), which are preserved verbatim but subordinate.

1. **Platform before Project** — every decision must remain valid in the absence of any specific Project.
2. **Constitution before Standard** — no Standard may contradict the Constitution.
3. **Standard before Engine** — no Engine specification may be written before its normative Standard.
4. **Engine before Builder** — no Builder artifact may depend on an Engine that lacks a specification.
5. **Specification before Implementation** — Foundation phase delivers specifications only.
6. **Audit before Report** — every Report must be backed by an Audit.
7. **Review before Activation** — no artifact becomes `active` without human Review.
8. **Explicit over Implicit** — no hidden behavior, no inferred intent.
9. **Additive over Destructive** — extend, do not replace (§13).
10. **Reversible before Irreversible** — every irreversible action requires explicit Approval.
11. **Evidence over Assertion** — every claim must cite an Evidence artifact.
12. **Identity before Activity** — every actor's role is fixed before they act (§5).

These principles are **binding**. Any conflict with a lower-layer artifact is resolved in favor of the principle.

---

## §4  Lifecycle Model

Every Foundation artifact passes through seven stages. Transitions are governed by §4 exit criteria.

### §4.1  Stages

| Stage | Description | Exit Criterion |
|---|---|---|
| **Bootstrap** | Initial existence. May be referenced only by its own lineage. | Header completed; `Status: draft`. |
| **Draft** | Open for revision. Other artifacts may cite, not depend. | Reviewer assigns `Status: review`. |
| **Review** | Under human Review. No edits except typo fixes. | Reviewer issues a Review Record. |
| **Active** | Binding for the layer it occupies. | Reviewed and approved via FD (L2) or amendment (L1). |
| **Deprecated** | Discouraged for new use; remains supported for one minor version. | Migration Plan published; new FD published. |
| **Frozen** | No new use; only critical fixes. | Sunset date announced; FD published. |
| **Archived** | Removed from active use; retained for history. | No new references accepted. |

### §4.2  Transition Rules

- Transitions are **only forward**, except `Frozen → Active` (via new FD) and `Archived → Active` (forbidden).
- Any transition except `Bootstrap → Draft` requires a Review Record.
- `Active → Deprecated` requires a Migration Plan.
- `Frozen → Archived` requires a sunset period of at least one Foundation minor version.

### §4.3  Lifecycle Identifier

Every artifact must declare its `Status:` line in its header. Status values are limited to the seven stages above.

---

## §5  Role Model

Six roles exist in the Foundation. Each role has explicit, non-overlapping responsibilities.

| Role | Responsibility | Authority |
|---|---|---|
| **Architect** | Defines architecture; issues FDs; activates Standards. | Supreme within L2. Cannot write Builder artifacts. |
| **Builder** | Constructs Foundation artifacts within rules defined by the Architect. | L7 only. Cannot redefine architecture. |
| **Auditor** | Verifies compliance against this Constitution. | Issues Audit Reports. Cannot modify audited artifacts. |
| **Reviewer** | Performs human Review on artifacts in `review` status. | Issues Review Records; approves or rejects. |
| **Maintainer** | Performs corrections and routine updates within an approved scope. | FD-bounded; cannot change architecture. |
| **Release Manager** | Coordinates Foundation Releases. | FD-bounded; cannot modify content. |

**Boundary rules:**

- The Builder **cannot** redefine architecture. Any architectural question must be escalated to the Architect via FRFC.
- The Auditor **cannot** modify the audited artifact. Auditor findings are returned to the Builder for remediation.
- The Reviewer **cannot** be the same individual as the Builder for that artifact (separation of duties).
- The Release Manager **cannot** combine release decisions with content edits.
- No individual may hold more than one role on a single artifact.

**Activation:** The current Foundation Phase has only the Builder role active. All other roles are reserved for future Foundation Tasks and Project lifecycles.

---

## §6  RFC Governance

Three RFC types exist. Each serves a distinct scope.

### §6.1  Foundation RFC (FRFC)

- **Scope:** Foundation-wide changes (L1–L5 artifacts).
- **Numbering:** `FRFC-NNNN-<slug>.md`.
- **Approval:** Architect via FD.
- **Status values:** `proposed` → `accepted` → `rejected` | `withdrawn` | `superseded`.

### §6.2  Project RFC (PRFC)

- **Scope:** Project-specific changes (L6 artifacts within one Project).
- **Numbering:** `PRFC-<project>-NNNN-<slug>.md`.
- **Approval:** Project Lead via PD (Project Decision).
- **Status values:** `proposed` → `accepted` → `rejected` | `withdrawn` | `superseded`.

### §6.3  Research RFC (RRFC)

- **Scope:** Cross-Project research methodology (e.g., statistical methods, evidence grading).
- **Numbering:** `RRFC-NNNN-<slug>.md`.
- **Approval:** Architect via FD.
- **Status values:** `proposed` → `accepted` → `rejected` | `withdrawn` | `superseded`.

### §6.4  RFC Lifecycle

Every RFC passes through: `draft` → `proposed` → under `review` → `accepted` | `rejected` | `withdrawn` | `superseded`. Accepted FRFCs are ratified by an FD before becoming binding.

### §6.5  Naming

RFC titles follow §9. Filenames are stable; titles may be amended.

---

## §7  Decision Records

Foundation Decisions (FDs) are the binding mechanism for architectural change.

### §7.1  Format

```
FD-NNNN-<slug>.md
```

### §7.2  Mandatory Content

Every FD must contain:

1. **ID** — `FD-NNNN-<slug>`.
2. **Title** — short imperative phrase.
3. **Status** — `proposed` | `accepted` | `rejected` | `superseded`.
4. **Date** — ISO-8601 date of decision.
5. **Decider** — the Architect.
6. **Context** — what triggered the decision.
7. **Decision** — what was decided.
8. **Consequences** — positive, negative, and neutral.
9. **Supersedes** — list of superseded FDs (if any).
10. **References** — FRFCs, Standards, Constitution sections.

### §7.3  Numbering

FDs are numbered sequentially. Numbers are never reused. Withdrawn or rejected FDs retain their number.

### §7.4  Activation

An FD becomes `active` upon the Architect's signature recorded in its header. No FD is binding until active.

### §7.5  Storage

Active FDs are stored in `FOUNDATION/09-Decisions/`. Superseded FDs remain in place; their `Status:` line is updated.

---

## §8  Versioning Policy

### §8.1  Semantic Versioning

All Foundation artifacts follow Semantic Versioning `MAJOR.MINOR.PATCH` with optional pre-release tags.

| Bump | Trigger |
|---|---|
| **MAJOR** | Breaking change to normative content; amendment of this Constitution. |
| **MINOR** | Backward-compatible additive change; new section; new Standard. |
| **PATCH** | Backward-compatible corrective change; typo, clarification, link fix. |

### §8.2  Pre-release Tags

Pre-release tags use hyphen notation: `0.1.0-draft`, `0.2.0-dev`, `1.0.0-rc.1`, `1.0.0-beta.2`, `1.0.0-alpha.3`. Pre-release versions are **non-binding**. In particular:

- The `*-draft` tag is used by the Builder for artifacts under construction.
- The `*-dev` tag is used for the Foundation platform between Tasks.
- The `*-rc.*` tag is reserved for the **Foundation v1.0.0-rc.1** release declared by Task 12.
- No artifact may claim a `*-rc.*` tag before the corresponding release milestone has passed.

### §8.3  First-Release Rule

The first on-disk version of any artifact is `0.1.0-draft` (or `0.1.0-dev` for the Foundation platform itself). Promotion to `1.0.0` requires:

- All Foundation Tasks (Task 01 through Task 12) to be `active`; and
- The Foundation Release Candidate review (Task 12) to have passed.

No intermediate `1.0.0-rc.*` version may be issued before Task 12 passes review.

### §8.4  Version Co-location

Every artifact's version appears in its header. The Foundation version lives in `FOUNDATION/VERSION`.

---

## §9  Naming Convention

All Foundation and Project artifacts follow the naming table below. Filenames are stable identifiers.

| Class | Pattern | Example |
|---|---|---|
| Constitution | `constitution.md` | `FOUNDATION/01-Constitution/constitution.md` |
| Foundation README | `README.md` | `FOUNDATION/README.md` |
| Foundation Version | `VERSION` | `FOUNDATION/VERSION` |
| Foundation Standard | `STD-<area>-vX.Y.Z.md` | `STD-DIR-v1.0.0.md` |
| Engine Specification | `ENG-<engine>-vX.Y.Z.md` | `ENG-PROMPT-v1.0.0.md` |
| SDK Specification | `SDK-<name>-vX.Y.Z.md` | `SDK-BUILDER-v1.0.0.md` |
| Plugin Specification | `PLG-<plugin>-vX.Y.Z.md` | `PLG-MCP-v1.0.0.md` |
| Foundation RFC | `FRFC-NNNN-<slug>.md` | `FRFC-0001-naming.md` |
| Project RFC | `PRFC-<project>-NNNN-<slug>.md` | `PRFC-APES-0001-rubric.md` |
| Research RFC | `RRFC-NNNN-<slug>.md` | `RRFC-0001-evidence-grading.md` |
| Foundation Decision | `FD-NNNN-<slug>.md` | `FD-0001-activate-constitution.md` |
| Project Decision | `PD-<project>-NNNN-<slug>.md` | `PD-APES-0001-release.md` |
| Sprint | `SPRINT-<project>-<NN>-<slug>.md` | `SPRINT-APES-04-finalization.md` |
| Task | `TASK-<project>-<sprint>-<NN>-<slug>.md` | `TASK-APES-04-01-summary.md` |
| Audit | `AUDIT-<scope>-<NN>-<slug>.md` | `AUDIT-FOUNDATION-01-constitution.md` |
| Review | `REVIEW-<scope>-<NN>-<slug>.md` | `REVIEW-FOUNDATION-01-constitution.md` |
| Report | `REPORT-<scope>-<NN>-<slug>.md` | `REPORT-FOUNDATION-01-constitution.md` |
| Builder Pack | `PACK-<project>-<program>-<pack>.md` | `PACK-APES-RESEARCH-001.md` |
| Statistics | `STATS-<scope>-<NN>-<slug>.md` | `STATS-APES-01-descriptive.md` |
| Evidence | `EVID-<scope>-<NN>-<slug>.md` | `EVID-APES-01-rct-results.md` |
| Manifest | `MANIFEST-<scope>-<NN>-<slug>.json` | `MANIFEST-FOUNDATION-01-constitution.json` |

**Slug rules:** lowercase ASCII letters, digits, and hyphens; max 64 chars; no leading/trailing hyphen; must describe content.

**Naming is normative.** A filename that violates the table must be rejected by Review.

---

## §10  Cross Reference Policy

Every Foundation artifact must include a `References` section listing all artifacts it depends on or cites.

### §10.1  Mandatory References

| Artifact Type | Must Reference |
|---|---|
| Standard | Constitution §X (relevant section), related Standards |
| Engine Specification | Constitution §X, relevant Standards, related Engines |
| RFC | Constitution §X, related Standards, related FDs |
| FD | Constitution §X, the FRFC that proposed it (if any) |
| Builder Report | Constitution §X, the Task it reports on, related Audits/Reviews |
| Audit | The artifact audited, the Standard(s) used |
| Review | The artifact reviewed, the Audit (if any) |

### §10.2  Reference Form

References use the form `[Section §X.Y](../path/to/file.md#anchor)` and **must resolve**. Broken links are Quality Gate failures (§11).

### §10.3  Back-References

Every referenced artifact should, in turn, reference back to the referrer. Back-references may be maintained via Manifest (§10.4) when bidirectional is impractical.

### §10.4  Manifest

A Manifest (`MANIFEST-<scope>-<NN>-<slug>.json`) enumerates all artifacts in a scope with their forward and back references. Manifests are the source of truth for cross-reference integrity.

---

## §11  Quality Gate

Every Foundation artifact must pass **all four** Quality Gate criteria before human Review.

### §11.1  Completeness

All required sections, fields, evidence placeholders, and references specified by the Task are present and non-empty.

### §11.2  Compliance

The artifact does not violate the Constitution, any `active` Standard, any `active` FD, or the Compatibility Policy (§2).

### §11.3  Cross Reference

Every applicable reference (Constitution section, Standard, RFC, FD, Version) is present and resolvable (§10).

### §11.4  Isolation

No out-of-scope content. During Foundation phase specifically:

- No Project-specific **governance, lifecycle, schema, or implementation** rules may appear in any Foundation artifact. Projects may appear **only as examples** (e.g., "the first Project" or "Project X as illustration"), not as the source of normative content.
- No Engine code (only Engine specifications in their proper Task).
- No Standard content beyond what the Constitution itself defines.
- No Sprint, Task, Release, or Runtime artifacts.

**Project-independence rule.** The Constitution and all Foundation artifacts must remain valid in the complete absence of any specific Project, including APES. Project-independence is a **semantic** property: an artifact violates this criterion if its governance, lifecycle, schema, naming, or implementation rules depend on, or are derived from, a specific Project's characteristics — regardless of how many times (or how few) the Project is mentioned. Mentioning a Project as an example is permitted; encoding Project-specific rules is not.

### §11.5  Failure Handling

If any criterion fails, the artifact is **returned to the Builder** for revision. It is **not** presented for Review. The Builder must record the failure and remediation in the Task Report.

---

## §12  Deprecation Policy

Artifacts may be deprecated. Six states are recognized:

| State | Description |
|---|---|
| **Active** | Current normative source. |
| **Deprecated** | Discouraged for new use; remains supported for one Foundation minor version. |
| **Frozen** | No new use; only critical security/corrective fixes. |
| **Migration Required** | Backward-incompatible change planned; consumers must migrate. |
| **Archived** | Retained for history; no references accepted. |
| **Removed** | Physically deleted (only after Archived for one Foundation minor version). |

**Allowed transitions:**

- `Active → Deprecated → Frozen → Migration Required → Archived → Removed` (forward).
- `Frozen → Active` only via new FD.
- `Archived → Active` is **forbidden**.

Every transition requires an FD and a published Migration Plan.

---

## §13  Future Extension Policy

### §13.1  Additive-Only

Foundation extensions are **additive only**. New sections may be appended; existing sections may be clarified but not weakened; no section may be deleted without explicit amendment (§17).

### §13.2  Extension Procedure

1. A new FRFC proposes the extension.
2. The Architect reviews and either accepts (via FD) or rejects.
3. Accepted extensions are appended to the Constitution with the next MAJOR or MINOR bump.
4. All existing references are updated as needed.

### §13.3  Non-Regression Guarantee

No amendment may reduce the binding force of any existing clause. Where a clause appears weakened, an additional clause must be added that explicitly preserves the original force.

---

## §14  Success Criteria

The Foundation is declared complete when the following milestones are met.

### §14.1  Milestones

| Milestone | Trigger |
|---|---|
| **Foundation Complete** | Tasks 01–11 all `active`. |
| **Foundation RC** | Task 12 review passed; `v1.0.0-rc.1` published. **Task 12 is the only Foundation RC gate.** |
| **Foundation Stable** | One full review cycle with no MAJOR changes; `v1.0.0` published. |
| **Platform Stable** | At least one Project successfully built on Foundation `v1.0.0`. |
| **Production Ready** | Platform Stable maintained for three Foundation minor versions. |

### §14.2  Current Target

The current Foundation Mission targets **Foundation Complete** (Tasks 01–11) and **Foundation RC** (Task 12). No Foundation version, including the Constitution, may be described as having reached RC before Task 12 passes.

---

## §15  Foundation Task Protocol

### §15.1  One Task per Cycle

The Builder executes **exactly one** Foundation Task per cycle. The current Task list is:

1. Constitution
2. Governance
3. Directory Standard
4. Schema Standard
5. Builder Pack Standard
6. Builder Runtime Specification
7. Quality Gate
8. Engine Specifications
9. SDK Specifications
10. Plugin Specification
11. Workspace Specification
12. Foundation Release Candidate

After completing a Task, the Builder **stops** and **waits** for human approval.

### §15.2  Seven-Section Report

Every Task produces the following seven-section report:

1. **Summary**
2. **Files Modified**
3. **Acceptance Checklist**
4. **Verification**
5. **Remaining Limitations**
6. **Git Status**
7. **Recommended Foundation Task**

### §15.3  Hard Prohibitions

During the current Foundation phase, the following are forbidden:

- Beginning any Project Sprint (e.g., APES Sprint 4).
- Performing Gap Analysis or Positioning for any Project.
- Entering any Project Phase C.
- Creating any Standard beyond what the Constitution itself defines.
- Creating Project-specific Standards.
- Beginning any Release.
- Declaring any Foundation version as having reached `1.0.0-rc.1` or `1.0.0` before Task 12 passes.
- Auto-committing, auto-pushing, or auto-creating branches.
- Building Scaffold, Standards, Engines, Runtime, Plugin System, or SDK prematurely.
- Modifying any Sprint, any Project, or any Project artifact.

Violations are Foundation-level incidents requiring an FD.

### §15.4  Stop Conditions

The Builder **stops** when:

- The seven-section report is complete.
- A Quality Gate failure is detected (§11.5).
- A Hard Prohibition is encountered (§15.3).
- An ambiguous architectural question arises (escalate via FRFC).

The Builder **does not auto-continue**, **does not auto-commit**, and **does not auto-push**.

### §15.5  Per-Task Scope Declaration (Mandatory)

Every Foundation Task — and every correction cycle within a Task — must begin with an explicit **Scope Declaration** stating:

1. **Allowed files** — the complete list of paths the Task may create or modify.
2. **Forbidden files** — any paths the Task must not touch (typically: all paths outside the allowed list).
3. **Inputs** — artifacts the Task consumes (prior Tasks' outputs, Constitution sections, external references).
4. **Outputs** — artifacts the Task produces (deliverables, report, audit, review).
5. **Dependencies** — earlier Foundation Tasks whose completion the current Task requires.
6. **Quality gates** — which §11 criteria the Task must satisfy, plus any Task-specific criteria.
7. **Stop condition** — the trigger that ends the Task (typically: completion of the seven-section report and human approval).

**Scope Expansion Rule.** The Builder **may not** create or modify any file outside the declared allowed-file list. Any expansion requires explicit human approval recorded in the Task Report before the file is touched. The Quality Gate criterion §11.4 (Isolation) is automatically failed for any Task that violates this rule, regardless of whether the out-of-scope content is otherwise acceptable.

---

## §16  Execution Principles (Original Ten, Preserved Verbatim)

The following ten Execution Principles, originally defined in Constitution v0.1, are preserved verbatim and remain binding. They are subordinate to §3 (Design Principles) and §11 (Quality Gate).

1. **Builder First**
2. **Constitution First**
3. **Standard First**
4. **Engine First**
5. **Audit First**
6. **Statistics First**
7. **Report First**
8. **Review First**
9. **Human Approval Required**
10. **Never Skip Quality Gate**

---

## §17  Closing

### §17.1  Supersession

This Constitution supersedes all prior versions (`v0.1`, `v0.2`). Upon **ratification** (§17.3), prior versions enter the **Archived** state (§12). Until ratification, this version is the active Provisional draft; prior versions remain `draft` for reference.

### §17.2  Amendment

Amendments to this Constitution require:

1. A new FRFC proposing the change.
2. Acceptance via FD with explicit `amends-constitution: true` flag.
3. A MAJOR version bump (§8).
4. Migration Plan for any breaking change.

### §17.3  Ratification Sequence (Non-Circular)

Ratification of this Constitution follows a fixed sequence to avoid circular dependency:

1. **Task 01 (Constitution)** establishes this Constitution as a **Provisional** governance draft. Provisional governance applies on a best-effort basis; nothing in this Constitution is formally binding until ratified.
2. **Task 02 (Governance)** establishes the Foundation Decision mechanism (FDs, FDFC, RFCs) and instantiates the directory `FOUNDATION/09-Decisions/`. Until Task 02 is complete, **no FD can exist**.
3. **After Task 02**, an Architect-issued `FD-0001` may ratify this Constitution. Ratification requires the FD to record the Architect's signature and to explicitly declare `ratifies-constitution: 0.1.0-draft`.
4. **After ratification**, prior Constitution versions (`v0.1`, `v0.2`) enter the **Archived** state.
5. **Foundation v1.0.0-rc.1** is declared only by **Task 12** after review. No earlier Task may declare, imply, or anticipate Foundation RC status.

### §17.4  Effective Date

Upon **ratification** (§17.3), this Constitution is effective immediately and governs all subsequent Foundation work. Until ratification, it governs **provisionally** — its clauses are followed as a working draft but no clause is formally binding.

---

*End of Constitution v0.1.0-draft (Ratified by FD-0001 on 2026-08-03).*
