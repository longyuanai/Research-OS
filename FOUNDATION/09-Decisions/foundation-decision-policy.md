# Foundation Decision (FD) Policy

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/09-Decisions/foundation-decision-policy.md`
**Related:** `governance-model.md`; `approval-workflow.md`; `change-control-policy.md`; Constitution v0.1.0-draft §7.

---

## 1. Purpose

This document operationalizes the **Foundation Decision (FD)** mechanism defined in Constitution §7. It defines the FD purpose, naming, numbering, required metadata, required sections, status lifecycle, approval authority, supersession rules, amendment rules, immutability requirements, and relationship to RFCs, ADRs, and the Constitution.

## 2. FD Purpose

An FD is the **binding mechanism for architectural change** at the Foundation level. It records a decision made by the Architect that:

- Ratifies, supersedes, or amends a Foundation artifact.
- Approves a Foundation Standard, RFC, or ADR.
- Authorizes a new Project, Engine, SDK, Plugin, or Workspace.
- Resolves a disagreement escalated per `disagreement-and-escalation.md`.
- Issues an emergency correction (with `EMERGENCY-` prefix).
- Records any other architectural decision within Foundation scope.

An FD is **not** a discussion record (that is an RFC or ADR), **not** a Project-internal decision (that is a PD), and **not** a routine operation (that is a Maintainer action).

## 3. Naming

Required filename pattern:

```
FD-NNNN-short-title.md
```

- `FD-` literal prefix.
- `NNNN` — zero-padded four-digit sequential number (e.g., `0001`, `0002`).
- `-short-title` — lowercase ASCII slug, max 64 characters; describe the decision in 1–5 words.
- Filenames are stable identifiers; they are not renamed even if the decision's scope shifts.

**Special prefixes:**

- `EMERGENCY-FD-NNNN-<slug>.md` — emergency corrections; see `governance-model.md` §10.
- `RATIFY-FD-NNNN-<slug>.md` — permitted but not required for ratification FDs; the numeric ID alone is sufficient.

## 4. Numbering

FDs are numbered **sequentially** within Foundation scope:

- The first FD is `FD-0001`.
- Each subsequent FD receives the next integer.
- **Numbers are never reused**, even for withdrawn, rejected, or superseded FDs.
- Gaps in numbering are not permitted; the next issued FD must use `last + 1`.
- Emergency FDs share the same numeric sequence as ordinary FDs (no separate numbering).
- Withdrawn FDs retain their number and remain in `FOUNDATION/09-Decisions/`.

## 5. Required Metadata (Header)

Every FD must declare the following metadata in its header:

| Field | Required? | Description |
|---|---|---|
| `ID` | yes | `FD-NNNN-<slug>` |
| `Title` | yes | short imperative phrase |
| `Status` | yes | `Pending Ratification` \| `Draft` \| `In Review` \| `Approved` \| `Ratified` \| `Superseded` \| `Rejected` \| `Withdrawn` \| `Archived` |
| `Version` | yes | SemVer string (e.g., `0.1.0-draft`) |
| `Date` | yes | ISO-8601 date of issue |
| `Owner` | yes | the role(s) responsible for the decision (typically `Architect`) |
| `Approver` | yes | the human Architect (when ratified) |
| `Related Constitution Version` | yes | the Constitution version this FD operates against (e.g., `0.1.0-draft`) |
| `Supersedes` | conditional | list of FD IDs superseded (if any) |
| `Superseded By` | conditional | FD ID that superseded this one (set after supersession) |
| `Dependencies` | conditional | list of FD/RFC/ADR/STD IDs this FD depends on |
| `Decision Scope` | yes | `Ratification` \| `Standard Approval` \| `RFC Approval` \| `ADR Approval` \| `Supersession` \| `Amendment` \| `Emergency Correction` \| `Disagreement Resolution` \| `Project Authorization` \| `Release Authorization` \| `Other` |
| `ratifies-constitution` | conditional | if `Decision Scope = Ratification`, the Constitution version being ratified |
| `amends-constitution` | conditional | if `Decision Scope = Amendment`, the Constitution version being amended |
| `Last Transition` | yes | actor + ISO-8601 date of last status change |

Missing required fields cause the FD to fail the Quality Gate (§11 Completeness).

## 6. Required Sections (Body)

Every FD must contain the following sections, in this order:

1. **ID, Title, Status, Date** — header fields.
2. **Context** — what triggered the decision; what problem it solves; what alternatives were considered.
3. **Decision** — what was decided; the exact normative statement.
4. **Consequences** — positive, negative, and neutral consequences of the decision.
5. **Affected Artifacts** — list of artifacts this FD modifies, supersedes, or ratifies.
6. **Migration Plan** (if applicable) — required for breaking changes (Constitution §12).
7. **References** — Constitution sections, FDs, FRFCs, ADRs, Standards, or external resources cited.
8. **Approver** — signature block (filled at ratification).
9. **Change Log** — record of changes to the FD itself (typically empty for a single-issue FD; populated if amended).

Missing required sections cause the FD to fail the Quality Gate.

## 7. Status Lifecycle

FDs traverse the lifecycle defined in `approval-workflow.md`. The typical path is:

```
Draft (or Pending Ratification, if AI-prepared)
  → Submitted
  → In Review
  → Approved
  → Ratified
  → (later) Superseded | Archived
```

A `Rejected` or `Withdrawn` FD is terminal (unless explicitly revived by a new FD).

**`Pending Ratification`** is the initial state of an FD prepared by an AI agent on behalf of a human Architect. The FD remains in this state until an explicit human approval is supplied. No AI agent may transition an FD out of `Pending Ratification` to `Ratified`.

## 8. Approval Authority

- **Ratification.** The human Architect (Constitution §7.4, §17.3).
- **Reviewer approval.** Required before ratification (per `approval-workflow.md` §5).
- **No self-approval.** The Architect who drafted the FD may not ratify it; a different Architect (or a designated human with the Architect role for that decision) must sign.

## 9. Supersession Rules

An FD may be superseded only by another FD that:

- Has a higher or equal status (typically `Ratified` supersedes `Ratified`).
- Explicitly declares `Supersedes: <FD-ID>` in its header.
- Becomes binding only after the superseding FD's ratification.

Supersession does not erase the original FD; it transitions the original to `Superseded` and updates its header to include `Superseded By: <new-FD-ID>`.

## 10. Amendment Rules

An FD may be amended by issuing a **new FD** that explicitly references the original. The original is not edited in place. The new FD may:

- Modify the original's scope.
- Add new affected artifacts.
- Extend the migration plan.

The original FD's header is updated to reference the amending FD; its content remains immutable.

## 11. Immutability Requirements

Once an FD enters `Ratified` status, its content is **immutable**. The only mutable fields are:

- `Status:` line.
- `Last Transition:` line.
- `Superseded By:` line (added when superseded).

All other fields and body sections are locked. Corrections require a new FD.

## 12. Relationship to RFCs, ADRs, and Constitution

### 12.1  Relationship to RFCs

- An FD may ratify an FRFC (Foundation RFC), in which case the FRFC's content is incorporated into the FD's `Decision` section or referenced as an appendix.
- An FD may reject an FRFC, in which case the FRFC enters `Rejected` state.
- An FD may supersede a prior FRFC's ratification by issuing a new FD.

### 12.2  Relationship to ADRs

- An FD may approve an ADR (Architecture Decision Record), in which case the ADR becomes binding within its declared scope.
- An FD may supersede an ADR by issuing a new FD that contradicts the ADR.

### 12.3  Relationship to the Constitution

- An FD may ratify the Constitution (only the first time, via `FD-0001` in the current sequence).
- An FD may amend the Constitution, provided it carries the `amends-constitution: true` flag and is processed through the constitutional amendment workflow (Constitution §17.2).
- An FD may not contradict the Constitution (Constitution §1 L1 > L2).

## 13. FD Storage

All FDs are stored in `FOUNDATION/09-Decisions/` with the following structure:

```
FOUNDATION/09-Decisions/
├── README.md
├── foundation-decision-policy.md
├── FD-0001-ratify-constitution.md
├── FD-0002-...md
└── ...
```

`Rejected`, `Withdrawn`, `Superseded`, and `Archived` FDs remain in this directory; their `Status:` line is updated but they are not moved.

## 14. Audit Trail

Every FD transition leaves an audit trail:

- `Status:` and `Last Transition:` lines.
- The Review Record (`REVIEW-FOUNDATION-NN-<slug>.md`) that approved the FD.
- A `CHANGELOG.md` entry.

The Audit Report for any Foundation Task that involves an FD verifies that the audit trail is complete.

---

*End of Foundation Decision Policy v0.1.0-draft.*
