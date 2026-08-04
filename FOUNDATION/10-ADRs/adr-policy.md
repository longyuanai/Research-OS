# ADR Policy (Foundation)

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/10-ADRs/adr-policy.md`
**Related:** `governance-model.md`; `rfc-policy.md`; Constitution v0.1.0-draft §7.

---

## 1. Purpose

This document operationalizes the **Architecture Decision Record (ADR)** mechanism introduced in Task 02 as a new artifact class. ADRs record significant architectural decisions — both within the Foundation and within individual Repos or Projects — in a lightweight, searchable, and auditable form.

ADRs are **not** normative. They record what was decided and why. They are ratified by an FD, PD, or RD that points to them; the ADR itself does not change Foundation rules.

## 2. Why a New Artifact Class

Foundation previously had two normative mechanisms:

- **FDs** — bind architectural change.
- **FRFCs / PRFCs / RRFCs** — propose architectural change for review (FRFC: Foundation-wide normative; PRFC: Project-local normative; RRFC: Release planning, scope, exceptions, or governance).

Neither recorded *implementation-level* decisions (e.g., "we will use SQLite for the FD ledger", "we will use JSON for FD metadata") in a discoverable way. ADRs fill that gap: they capture **non-normative** but **significant** decisions that future contributors and Reviewers need to know about.

ADRs are introduced by Task 02 because:

- The Foundation has accumulated implementation choices (e.g., FD metadata format) that were made without a record.
- Future Tasks (03–12) will make more such choices.
- A consistent ADR format improves discoverability and prevents re-litigation.

## 3. ADR Scope

ADRs may be issued at three levels:

- **Foundation-level ADR (F-ADR)** — concerns a Foundation artifact, mechanism, or platform-wide choice. Stored in `FOUNDATION/10-ADRs/`.
- **Project-level ADR (P-ADR)** — concerns a single Project. Stored in `PROJECTS/<project>/10-ADRs/`.
- **Repo-level ADR (R-ADR)** — concerns a single repository implementation. Stored within the Repo.

This policy governs **F-ADRs** primarily; P-ADRs and R-ADRs follow the same pattern with scope-specific naming. Repository implementation or architecture decisions normally use ADRs (when non-normative) or a PRFC (when normative within a Project), depending on scope.

## 4. Naming Convention

All ADRs follow the pattern:

```
ADR-NNNN-short-title.md
```

- `ADR-` literal prefix.
- `NNNN` — zero-padded four-digit sequential number (e.g., `0001`, `0002`).
- `-short-title` — lowercase ASCII slug, max 64 characters; describe the decision in 1–5 words.

Numbers are **scope-scoped**: a Foundation `ADR-NNNN` and a Project `ADR-NNNN` share the numeric portion independently. Numbers are never reused within a scope.

**Optional prefix** to indicate scope:

- `F-ADR-NNNN-<slug>.md` — Foundation-level.
- `P-ADR-NNNN-<slug>.md` — Project-level.
- `R-ADR-NNNN-<slug>.md` — Repo-level.

Either bare `ADR-NNNN` (when scope is clear from storage location) or scoped prefix is acceptable.

## 5. Required Header

Every ADR must declare the following metadata:

| Field | Required? | Description |
|---|---|---|
| `ID` | yes | `ADR-NNNN-<slug>` (or scoped variant) |
| `Title` | yes | short imperative phrase |
| `Status` | yes | see §7 |
| `Version` | yes | SemVer string |
| `Date` | yes | ISO-8601 |
| `Author` | yes | the deciding individual(s) |
| `Scope` | yes | `Foundation` \| `Project` \| `Repo` |
| `Related Constitution Version` | conditional | required if Scope = Foundation |
| `Related Project Version` | conditional | required if Scope = Project |
| `Related Repo Version` | conditional | required if Scope = Repo (repository implementation) |
| `Decided By` | yes | FD/PD/RD ID that ratified the ADR, or `Operational Decision` if not separately ratified |
| `Supersedes` | conditional | ADR ID(s) superseded |
| `Superseded By` | conditional | set after supersession |
| `Last Transition` | yes | actor + ISO-8601 date of last status change |

## 6. Required Sections (Body)

Every ADR must contain:

1. **ID, Title, Status, Date** — header.
2. **Context** — the situation and the question being decided.
3. **Decision** — what was decided, with the exact chosen option.
4. **Consequences** — positive, negative, and neutral consequences.
5. **Alternatives Considered** — what else was considered and why each was rejected.
6. **References** — Constitution sections, FDs/PDs/RDs, FRFCs/PRFCs/RRFCs, external resources.
7. **Change Log** — record of edits.

ADRs are concise; a typical ADR is 1–3 pages.

## 7. Status Lifecycle

ADRs traverse:

```
Draft (or Pending Ratification, if AI-prepared)
  → Proposed
  → Accepted (after FD/PD/RD ratification, or after Operational Decision)
  → Superseded (later, by a new ADR)
  → Deprecated (still in force but flagged for replacement)
  → Rejected | Withdrawn (terminal)
```

## 8. ADR vs FD vs RFC

| Artifact | Purpose | Normative? | Lifecycle |
|---|---|---|---|
| **FD** | Bind architectural change at the Foundation level | **Yes** | Draft → Ratified → Superseded |
| **FRFC / PRFC / RRFC** | Propose normative change for review | **No** (proposal only) | Draft → Approved/Rejected → Withdrawn |
| **ADR** | Record a significant non-normative architectural decision | **No** (record only) | Draft → Accepted → Superseded/Deprecated |

ADRs do **not** replace FDs or RFCs. When a decision is normative (changes a rule, schema, or interface), use an FD. When a decision is significant but non-normative (chooses an implementation, library, or pattern), use an ADR.

## 9. Authority

- **Foundation ADR.** May be proposed by any role. Becomes **Accepted** when:
  - An FD explicitly references and ratifies it, **or**
  - A Reviewer approves it as an Operational Decision in the absence of a normative change.
- **Project ADR.** Becomes Accepted via a PD or a Reviewer-approved Operational Decision.
- **Repo ADR.** Becomes Accepted via an FD, PD, or a Reviewer-approved Operational Decision; repo-level architectural decisions are not normally promoted to FD unless they have Foundation-wide implications.

ADRs prepared by AI agents (e.g., the Foundation Builder) enter `Pending Ratification` until a human Reviewer or approver explicitly accepts them.

## 10. Supersession and Amendment

- **Supersession.** A new ADR may supersede an old ADR by referencing it in `Supersedes:` and being marked `Accepted`. The old ADR transitions to `Superseded`.
- **Amendment.** An ADR's content is **immutable** once `Accepted`. Corrections require a new ADR that supersedes the original.

## 11. ADR Storage

- **F-ADRs:** `FOUNDATION/10-ADRs/`.
- **P-ADRs:** `PROJECTS/<project>/10-ADRs/`.
- **R-ADRs:** within the repository implementation (e.g., `repos/<repo>/.adrs/` or equivalent).

This directory (`FOUNDATION/10-ADRs/`) holds F-ADRs only.

## 12. ADR vs Comment in Code

ADRs are **separate from code comments**. Code comments explain *what the code does*; ADRs explain *why a particular approach was chosen*. ADRs may link to code, but the ADR text is the canonical record.

## 13. Creation Restriction in Task 02

**Task 02 does not create any ADRs** unless implementation choices made in Task 02 require recording. The Task 02 governance choices are documented in the policy files themselves; no ADR is issued solely to describe a Task 02 decision.

If a Task 02 implementation choice were to be recorded as an ADR, it would enter `Pending Ratification` and require human approval before transitioning to `Accepted`.

## 14. Audit Trail

Every ADR transition leaves an audit trail:

- `Status:` and `Last Transition:` lines.
- Cross-reference to the FD/PD/RD that ratified it (or the Operational Decision).
- A `CHANGELOG.md` entry when the ADR is accepted (when significant).

---

*End of ADR Policy v0.1.0-draft.*