# Approval Workflow

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/02-Governance/approval-workflow.md`
**Related:** `governance-model.md`; `roles-and-authority.md`; Constitution v0.1.0-draft §15.

---

## 1. Purpose

This document defines the **approval workflow** that every governance artifact must traverse from initial drafting to binding status. It enumerates the permitted states, the permitted transitions between states, who may trigger each transition, and what evidence must exist before a transition is allowed.

## 2. The Nine Canonical States

Every governance artifact's lifecycle is governed by the following nine states:

| # | State | Meaning |
|---|---|---|
| 1 | **Draft** | Under construction. May be revised freely. |
| 2 | **Submitted** | Author has declared the artifact ready for review. |
| 3 | **In Review** | Reviewer is examining the artifact. No edits except typo fixes. |
| 4 | **Changes Requested** | Reviewer requests edits. Author resumes work. |
| 5 | **Approved** | Reviewer accepts the artifact. |
| 6 | **Ratified** | Architect (with signature) makes the artifact binding. Used only for ratification-eligible artifacts: Constitution, FDs. |
| 7 | **Superseded** | The artifact has been replaced by a later one. |
| 8 | **Rejected** | The artifact is denied. Terminal. |
| 9 | **Archived** | Retained for history; no references accepted. Terminal. |

A **tenth state**, `Pending Ratification`, is permitted for artifacts (notably FDs) that require human approval and have been prepared by an AI agent on the user's behalf. `Pending Ratification` is functionally equivalent to `Submitted` but explicitly records that the next transition requires an explicit human approval action.

## 3. Permitted Transitions

The following transitions are permitted. Any transition not listed here is **forbidden** and must be escalated per `disagreement-and-escalation.md`.

### 3.1  From `Draft`

- `Draft → Submitted` (Author)
- `Draft → Withdrawn` (Author) — see note below

> *Note.* `Withdrawn` is treated as a terminal state when reached from `Draft`. The artifact is archived with a `Status: Withdrawn` header and a `Withdrawn By:` and `Withdrawn Date:` line.

### 3.2  From `Submitted`

- `Submitted → In Review` (Reviewer)
- `Submitted → Changes Requested` (Reviewer)
- `Submitted → Withdrawn` (Author)

### 3.3  From `In Review`

- `In Review → Approved` (Reviewer)
- `In Review → Changes Requested` (Reviewer)
- `In Review → Rejected` (Reviewer)

### 3.4  From `Changes Requested`

- `Changes Requested → Submitted` (Author, on resubmission)
- `Changes Requested → Withdrawn` (Author)

### 3.5  From `Approved`

- `Approved → Ratified` (Architect, with signature) — only for ratification-eligible artifacts
- `Approved → Rejected` (Architect or Reviewer) — overrides prior approval
- `Approved → Superseded` (Architect, via FD)
- `Approved → Archived` (Architect)

### 3.6  From `Pending Ratification`

- `Pending Ratification → Ratified` (Architect, with signature and explicit human approval)
- `Pending Ratification → Changes Requested` (Architect)
- `Pending Ratification → Withdrawn` (Author)
- `Pending Ratification → Rejected` (Architect)

### 3.7  From `Ratified`

- `Ratified → Superseded` (Architect, via FD)
- `Ratified → Archived` (Architect)

### 3.8  From terminal states

`Rejected`, `Withdrawn`, and `Archived` are terminal. They may not transition to any other state.

`Superseded` is semi-terminal: it may transition to `Archived` (Architect) but not back to any active state.

## 4. Who May Trigger Each Transition

| Transition | Required Actor | Additional Constraints |
|---|---|---|
| `Draft → Submitted` | Author | Author must declare scope per §15.5 if applicable. |
| `Submitted → In Review` | Reviewer | Reviewer must be independent of Author (per `roles-and-authority.md`). |
| `In Review → Approved` | Reviewer | Reviewer must cite Quality Gate criteria met. |
| `In Review → Changes Requested` | Reviewer | Reviewer must enumerate specific changes. |
| `In Review → Rejected` | Reviewer | Reviewer must cite Quality Gate criteria failed. |
| `Changes Requested → Submitted` | Author | Author must address each change request. |
| `Approved → Ratified` | Architect | Architect's signature required in header. |
| `Pending Ratification → Ratified` | Human Architect | **Explicit human approval required.** No AI impersonation. |
| `Approved / Ratified → Superseded` | Architect | Via FD with `supersedes:` declaration. |
| `Approved / Ratified → Archived` | Architect | Via FD. |
| Any state → `Withdrawn` | Author | Only from non-terminal states. |
| `Submitted → Rejected` | Reviewer | Allowed without passing through `In Review` (e.g., scope rejection). |

## 5. Which Transitions Require Human Approval

The following transitions **always require an explicit human approval**:

| Transition | Human Approver |
|---|---|
| `Draft → Submitted` for any Foundation artifact | Human (the author must be human, or the Builder must be acting under explicit human instruction) |
| `Submitted → In Review` for the Constitution | Human Reviewer (Architect or designated Reviewer) |
| `In Review → Approved` for an active Standard or active FD | Human Reviewer |
| `Approved → Ratified` for the Constitution | Human Architect |
| `Pending Ratification → Ratified` | **Human Architect** — no AI may trigger this |
| `Approved → Superseded` | Human Architect |
| Any transition that affects the Constitution's normative content | Human Architect |

For lower-stakes transitions (e.g., a Builder Report), an automated or AI-assisted workflow may trigger the transition provided a Human has approved the underlying Task.

## 6. Evidence Required Before Approval

Before any transition to `Approved` or `Ratified`, the following evidence must exist and be cited in the artifact or its accompanying Review Record:

1. **Quality Gate evidence.** The artifact must have passed all four Quality Gate criteria (Constitution §11):
   - Completeness — all required sections, fields, evidence placeholders, and references present.
   - Compliance — no violation of Constitution, active Standards, active FDs, or Compatibility Policy.
   - Cross Reference — every applicable reference present and resolvable.
   - Isolation — no out-of-scope content; project-independent.

2. **Audit evidence.** An Audit Report (`AUDIT-<scope>-<NN>-<slug>.md`) must exist, must have been performed by an Auditor independent of the Builder, and must confirm all four Quality Gate criteria.

3. **Reviewer evidence.** A Review Record (`REVIEW-<scope>-<NN>-<slug>.md`) must exist with the Reviewer's signature and disposition.

4. **Change-log evidence.** Any change since the previous version must be recorded in `CHANGELOG.md` with a clear, non-normative summary.

5. **Conflict-of-interest evidence.** Any declared conflict of interest (per `roles-and-authority.md` §2) must be recorded in the Review Record.

6. **For FDs**: an explicit `ratifies: ...`, `supersedes: ...`, or `amends-constitution: ...` flag as applicable.

## 7. Special Workflows

### 7.1  Constitution ratification workflow

1. Task 01 produces the Provisional Constitution (`v0.1.0-draft`).
2. Task 02 produces `FD-0001` in `Pending Ratification` status.
3. **Human Architect** reviews the Constitution and `FD-0001`.
4. On explicit human approval:
   - `FD-0001` transitions `Pending Ratification → Ratified`.
   - Constitution header's `Status:` line updates from `Provisional` to `Ratified`.
   - `CHANGELOG.md` records the ratification.
5. If the Architect does not approve, `FD-0001` transitions to `Changes Requested` or `Withdrawn`. The Constitution remains `Provisional`.

### 7.2  Standard amendment workflow

1. A Builder drafts the Standard amendment.
2. The Builder produces a `FRFC-NNNN-<slug>.md` proposing the amendment.
3. The FRFC moves through `Draft → Submitted → In Review → Approved | Rejected`.
4. On approval, an `FD-NNNN-<slug>.md` is issued that approves the FRFC and ratifies the amended Standard.
5. The Standard's header `Status:` and version update.

### 7.3  Emergency-change workflow

See `governance-model.md` §10 (Emergency-Change Restrictions). All emergency changes are followed by a normal FD within seven (7) days.

## 8. Audit Trail

Every transition must leave an audit trail:

- A `Status:` line in the artifact's header.
- A `Last Transition:` line recording the actor and ISO-8601 date.
- For `Approved` and `Ratified`: a Review Record or FD reference.

The Audit Report (`AUDIT-...`) verifies that the audit trail is complete.

---

*End of Approval Workflow v0.1.0-draft.*
