# RFC Policy (Foundation)

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/08-RFCs/rfc-policy.md`
**Related:** `governance-model.md`; `change-control-policy.md`; Constitution v0.1.0-draft §6, §12.

---

## 1. Purpose

This document operationalizes the **Request for Comments (RFC)** mechanism defined in Constitution §6. It defines the three RFC classes — FRFC, PRFC, RRFC — their purposes, naming, numbering, lifecycle, and the relationship between them and Foundation Decisions (FDs).

## 2. Three RFC Classes

### 2.1  FRFC — Foundation RFC

**Purpose.** Propose a normative change to a Foundation-level artifact (Constitution, Standard, Engine, SDK, Plugin, Workspace) or the Foundation platform as a whole.

**Scope.** Foundation-wide; binding after FD ratification.

**Example subjects.**

- A new Foundation Standard.
- An amendment to an existing Foundation Standard.
- A new Engine, SDK, Plugin, or Workspace definition.
- A cross-Project interface.

**Naming.** `FRFC-NNNN-short-title.md`.

**Outcome.** Approved → binding FD; Rejected → terminal; Withdrawn → terminal.

### 2.2  PRFC — Project RFC

**Purpose.** Propose a normative change to a single Project (e.g., APES) without affecting Foundation-level artifacts.

**Scope.** Project-bounded; binding after PD ratification within the Project's governance.

**Example subjects.**

- A new Project-level Standard.
- A change to a Project-internal Engine, SDK, Plugin, Workspace.
- A Sprint scope adjustment.
- A Project-internal deprecation.

**Naming.** `PRFC-NNNN-short-title.md`.

**Outcome.** Approved → binding PD within the Project; Rejected → terminal; Withdrawn → terminal.

**Out of scope.** Changes that affect cross-Project interfaces or Foundation artifacts. Such changes require an FRFC instead.

### 2.3  RRFC — Release RFC

**Purpose.** Propose a normative change to **release planning, release scope, release exceptions, or release governance** at the Foundation level.

**Scope.** Release-bounded; binding after FD ratification.

**Example subjects.**

- Release scope adjustments.
- Release exception requests (e.g., deferred deprecations, scope reductions).
- Release process changes (e.g., RC branch policy, release cadence).
- Release governance rules (e.g., Release Manager authority).

**Naming.** `RRFC-NNNN-short-title.md`.

**Outcome.** Approved → binding FD; Rejected → terminal; Withdrawn → terminal.

**Out of scope.** Repository implementation or repository architecture decisions. Such decisions normally use ADRs (when non-normative) or a PRFC (when normative within a Project), depending on their scope. A change that affects Foundation-wide normative artifacts uses an FRFC.

## 3. Naming Convention

All RFCs follow the pattern:

```
<CLASS>-NNNN-short-title.md
```

- `<CLASS>` — one of `FRFC`, `PRFC`, `RRFC`.
- `NNNN` — zero-padded four-digit sequential number within the class (e.g., `FRFC-0001`, `PRFC-0002`).
- `-short-title` — lowercase ASCII slug, max 64 characters; describe the proposal in 1–5 words.

Numbers are **class-scoped**: an `FRFC-NNNN` and a `PRFC-NNNN` share the numeric portion independently. Numbering is sequential within each class. Numbers are never reused.

## 4. Required Header (All RFCs)

Every RFC must declare the following metadata in its header:

| Field | Required? | Description |
|---|---|---|
| `ID` | yes | `<CLASS>-NNNN-<slug>` |
| `Title` | yes | short imperative phrase |
| `Status` | yes | see §5 |
| `Version` | yes | SemVer string (e.g., `0.1.0-draft`) |
| `Date` | yes | ISO-8601 |
| `Author` | yes | the proposing individual(s) |
| `Related Constitution Version` | yes | for FRFC and PRFC |
| `Related Project Version` | conditional | for PRFC |
| `Related Release Version` | conditional | for RRFC |
| `Supersedes` | conditional | RFC ID(s) superseded |
| `Superseded By` | conditional | set after supersession |
| `Decision Scope` | yes | brief statement of what the RFC proposes to change |
| `Affected Artifacts` | yes | list of artifacts the RFC modifies |
| `Migration Plan` | conditional | required for breaking changes |
| `Last Transition` | yes | actor + ISO-8601 date of last status change |

Missing required fields cause the RFC to fail the Quality Gate.

## 5. Status Lifecycle

RFCs traverse the following lifecycle (per `approval-workflow.md`):

```
Draft
  → Submitted
  → In Review
  → Approved (→ leads to FD/PD/Release decision) | Rejected
  → Withdrawn (terminal)
  → Superseded (later, by a new RFC) | Archived
```

Each transition is logged via `Status:` and `Last Transition:` lines.

## 6. Required Sections (Body)

Every RFC must contain:

1. **ID, Title, Status, Date** — header.
2. **Summary** — one-paragraph description.
3. **Motivation** — why the change is needed.
4. **Detailed Proposal** — exact normative text or interface change.
5. **Affected Artifacts** — list.
6. **Migration Plan** (if breaking).
7. **Drawbacks** — known costs and risks.
8. **Alternatives Considered** — what else was considered and why it was rejected.
9. **Open Questions** (if any) — unresolved items.
10. **References** — Constitution sections, FDs, ADRs, external resources.
11. **Change Log** — record of edits during the RFC's lifecycle.

Missing required sections cause the RFC to fail the Quality Gate.

## 7. Routing Rules

### 7.1  When to Use Each Class

A change uses an **FRFC** if:

- It modifies a Foundation-level artifact.
- It modifies a cross-Project interface.
- It creates a new Foundation Standard, Engine, SDK, Plugin, or Workspace.

A change uses a **PRFC** if:

- It is bounded within a single Project.
- It does not affect cross-Project interfaces or Foundation artifacts.

A change uses an **RRFC** if:

- It concerns release planning, release scope, release exceptions, or release governance.
- It does not modify Foundation-wide normative artifacts (which require an FRFC).

If the scope is unclear, the change must escalate to FRFC (the higher-authority layer) until scope is clarified.

### 7.2  Cross-Boundary Changes

A change that affects multiple layers must be processed at the highest affected layer:

- Foundation + Project → FRFC.
- Project + Release → FRFC.
- Foundation + Release → FRFC.

The higher-layer RFC must include cross-references to lower-layer RFCs and FDs/PDs that implement the change.

## 8. RFC-to-Decision Flow

| RFC Class | Decision Record | Approval Authority |
|---|---|---|
| FRFC | Foundation Decision (FD) | Architect (with Reviewer approval) |
| PRFC | Project Decision (PD) | Project Owner (with Reviewer approval) |
| RRFC | Foundation Decision (FD) | Architect (with Reviewer approval) |

The FD/PD explicitly references the RFC that proposed the change.

## 9. RFC Storage

- **FRFC** files: `FOUNDATION/08-RFCs/` with prefix `FRFC-`.
- **PRFC** files: `PROJECTS/<project>/08-RFCs/` (per Project layout) with prefix `PRFC-`.
- **RRFC** files: `FOUNDATION/08-RFCs/` with prefix `RRFC-`.

This directory (`FOUNDATION/08-RFCs/`) holds FRFC and RRFC records.

## 10. Multiple Parallel RFCs

When multiple RFCs concern overlapping artifacts:

- Each RFC is processed independently.
- Conflicts are resolved per `disagreement-and-escalation.md`.
- A new FRFC may supersede a prior FRFC only after the prior is `Withdrawn` or `Superseded`.

## 11. Audit Trail

Every RFC transition leaves an audit trail:

- `Status:` and `Last Transition:` lines.
- Cross-references to FDs, PDs, or RDs.
- A `CHANGELOG.md` entry when the RFC is approved.
- A Review Record (`REVIEW-FOUNDATION-NN-<slug>.md`).

## 12. RFC Authoring Rights

Any role may author an RFC, including Contributors, Builders, Auditors, Reviewers, Maintainers, Architects, and Project Owners. AI agents may author RFCs under the Builder role, but the RFC remains in `Draft` (or `Pending Ratification`) until a human contributor reviews and approves submission.

## 13. Creation Restriction in Task 02

**Task 02 (this Task) does not create any RFCs** unless a discovered blocking conflict requires one. Per Task 02 specification: *"Do not create an actual RFC in Task 02 unless necessary to resolve a discovered blocking conflict."* No such blocking conflict was discovered in Task 02; therefore, the directory contains only the policy file and the README.

---

*End of RFC Policy v0.1.0-draft.*