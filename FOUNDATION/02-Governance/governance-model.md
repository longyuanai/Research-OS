# Research-OS Foundation — Governance Model

**Status:** Draft / In Review
**Version:** 0.1.1-draft (Patched 2026-08-03 per FD-0002; Foundation Change Principle added as binding rule)
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/02-Governance/governance-model.md`
**Supersedes:** none
**Related:** Constitution v0.1.0-draft (Ratified by FD-0001); FD-0002 (Ratified, 2026-08-03); FRFC-0001 (Approved, 2026-08-03); FD-0001 (Ratified)
**Last Patch:** 2026-08-03, Foundation Patch Cycle 01, per FD-0002 §6 (binding Principle text added).

---

## 1. Purpose and Scope

This document defines the **operational governance model** of the Research-OS Foundation. It is the executable companion to the Constitution.

**Scope.** This model governs:

- All Foundation artifacts (Constitution, FDs, RFCs, ADRs, Standards, Engines, SDKs, Plugins, Workspaces, Builder Packs, Releases, and their lifecycle records).
- All Foundation roles (Architect, Builder, Auditor, Reviewer, Maintainer, Release Manager, Project Owner, Contributor).
- All decision processes (FD, RFC, ADR).
- All workflows (approval, change-control, disagreement, escalation).
- The ratification process for the Constitution itself.

**Out of scope.** Project-specific governance (Sprints, Packs, Tasks, Project RFCs) is governed by Project-level artifacts created after the Foundation v1.0.0-rc.1 release (Task 12). The Foundation defines the *shape* of Project governance; it does not instantiate it.

## 2. Governance Hierarchy

Foundation governance follows a **nine-level hierarchy**. Higher levels override lower levels when in conflict. This hierarchy is normative; no Foundation artifact may claim precedence over a higher level.

| Level | Artifact Class | Authority Source | Mutability |
|---|---|---|---|
| **L1** | Constitution (current ratified version) | Architect ratification (FD-0001) | Amendment only (§17 of Constitution) |
| **L2** | Ratified Foundation Decisions (`FD-*`) | Architect approval | Superseding FD only |
| **L3** | Foundation Standards | Architect approval (via FD) | Amendment + FD |
| **L4** | Approved RFCs (`FRFC-*`, `PRFC-*`, `RRFC-*`) and accepted ADRs (`ADR-*`) | Architect / Reviewer approval | Status lifecycle only |
| **L5** | Builder and Runtime specifications | Approved via FD or Standards | Specification amendment |
| **L6** | Project policies | Project Owner + applicable PD/PRFC | Project RFC |
| **L7** | Mission, Program, Pack, and Sprint rules | Project Lead | Project RFC |
| **L8** | Task and Work Package instructions | Builder scope, declared in §15.5 Scope Declaration | Task Report |
| **L9** | Generated artifacts and repository implementation | Builder-author under Task protocol | Supersession by later artifact |

**Lower levels may not override higher levels.** A lower-level artifact in conflict with a higher-level artifact is invalid to the extent of the conflict. Any conflict must be escalated per `disagreement-and-escalation.md`.

> Note: Mission, Program, and Work Package may be named as reserved execution concepts. Their full Standards are not defined in Task 02; that work belongs to later Foundation Tasks.

## 3. Authority Inheritance

Authority flows downward through the hierarchy. Each level derives its authority from the level above:

- **L1** — the Constitution defines the Foundation. No higher authority exists within the Foundation.
- **L2** — FDs derive their authority from the Constitution (Constitution §7).
- **L3** — Standards derive their authority from FDs that approve them.
- **L4** — RFCs and ADRs derive their authority from their approval flow (Architect for FRFC/ADR; Reviewer for ADR-lite).
- **L5** — Specifications derive their authority from L3 Standards or from L2 FDs.
- **L6–L9** — Project- and Task-level artifacts derive their authority from L3 Standards (when issued) and from L2 FDs that authorize their existence.

**Inheritance is strict.** If an artifact at level `n` claims authority that contradicts an artifact at level `m < n`, the lower-level claim is invalid.

## 4. Conflict-Resolution Priority

When two artifacts at the same level conflict, the following rules apply **in order**:

1. **Constitution prevails** — any conflict between the Constitution and any other artifact is resolved in favor of the Constitution, regardless of dates or versions.
2. **Higher status prevails** — between two artifacts at the same level, the artifact with the more advanced `Status:` (e.g., `ratified` > `accepted` > `proposed` > `draft`) prevails.
3. **Later version prevails** — if statuses tie, the artifact with the later SemVer version prevails.
4. **Later date prevails** — if versions tie, the artifact with the later ISO-8601 date prevails.
5. **Higher-numbered ID prevails** — if dates tie, the artifact whose ID sorts later (lexicographic) prevails.
6. **Escalate** — if none of the above resolves the conflict, the conflict is escalated per `disagreement-and-escalation.md` and resolved via FD or RFC.

## 5. Human Approval Boundaries

The Foundation distinguishes between decisions that **require human approval** and decisions that may be made by an automated or AI-assisted Builder under declared scope.

### 5.1  Decisions that always require human approval

- Ratification or amendment of the Constitution (L1).
- Issuance of a Foundation Decision (L2).
- Approval of a Foundation Standard (L3).
- Approval of a Foundation RFC (FRFC).
- Approval of a Foundation ADR.
- Constitution of a new Project on the Foundation.
- Declaration of a Foundation Release (any version promoted to `1.0.0-rc.1` or beyond).
- Any breaking change to an `active` Standard.

### 5.2  Decisions that may be made by a Builder under declared scope

- Drafting of any artifact (Builder may draft, but not approve).
- Production of Builder Reports, Audits, and Review records (Builder-author under §15 protocol).
- Implementation of approved work within declared scope (per §15.5 Per-Task Scope Declaration).
- Routine maintenance within an approved Maintainer scope (FD-bounded).

### 5.3  No AI impersonation of a human

No AI agent, including the Builder, may fabricate a human signature, approval timestamp, or approval identity. Where a decision requires human approval, the artifact must remain in a `Pending ...` status until an explicit human instruction supplies the approval.

## 6. Governance Artifact Types

The Foundation defines the following governance artifact types (in addition to those enumerated in Constitution §9):

| Type | Pattern | Storage | Owner |
|---|---|---|---|
| Foundation Decision | `FD-NNNN-<slug>.md` | `FOUNDATION/09-Decisions/` | Architect (per FD) |
| Foundation RFC | `FRFC-NNNN-<slug>.md` | `FOUNDATION/08-RFCs/` | Proposer + Architect |
| Project RFC | `PRFC-<project>-NNNN-<slug>.md` | `PROJECTS/<project>/08-PRFCs/` (post-Foundation) | Project Lead |
| Release RFC | `RRFC-NNNN-<slug>.md` | `FOUNDATION/08-RFCs/` | Release Manager |
| ADR | `ADR-NNNN-<slug>.md` | `FOUNDATION/10-ADRs/` (Foundation) or `PROJECTS/<project>/10-ADRs/` (Project) | Author + Reviewer |
| Review Record | `REVIEW-<scope>-<NN>-<slug>.md` | `FOUNDATION/07-Reviews/` (Foundation) or `PROJECTS/<project>/07-Reviews/` | Reviewer |
| Audit Report | `AUDIT-<scope>-<NN>-<slug>.md` | `FOUNDATION/04-Audits/` (Foundation) or `PROJECTS/<project>/04-Audits/` | Auditor |
| Builder Report | `REPORT-<scope>-<NN>-<slug>.md` | `FOUNDATION/06-Reports/` (Foundation) or `PROJECTS/<project>/06-Reports/` | Builder |
| Disagreement Record | `DIS-<scope>-<NN>-<slug>.md` | `FOUNDATION/09-Decisions/` (or Project equivalent) | Author of record |

## 7. Governance Status Lifecycle

Every governance artifact has a `Status:` line in its header. Permitted statuses:

| Status | Meaning | Who may set | Next statuses |
|---|---|---|---|
| `Draft` | Under construction; may be revised freely. | Author | `Submitted`, `Withdrawn` |
| `Submitted` | Author has declared the artifact ready for review. | Author | `In Review`, `Changes Requested`, `Withdrawn` |
| `In Review` | Reviewer is examining the artifact. No edits except typo fixes. | Reviewer | `Approved`, `Changes Requested`, `Rejected` |
| `Changes Requested` | Reviewer requests edits. Author resumes work. | Reviewer | `Submitted` (resubmission), `Withdrawn` |
| `Approved` | Reviewer accepts the artifact. | Reviewer | `Ratified`, `Rejected`, `Superseded`, `Archived` |
| `Ratified` | The artifact is binding (used only for ratification-eligible artifacts: FDs, Constitution). | Architect (signature) | `Superseded`, `Archived` |
| `Rejected` | The artifact is denied; archived. | Reviewer / Architect | (terminal) |
| `Withdrawn` | The author withdrew the artifact. | Author | (terminal) |
| `Superseded` | The artifact has been replaced by a later one. | Architect (via FD) | `Archived` |
| `Archived` | Retained for history; no references accepted. | Architect | (terminal) |
| `Pending Ratification` | The artifact awaits human approval; not binding. | Builder (when preparing on behalf) | `Ratified`, `Withdrawn` |

The full transition graph is defined in `approval-workflow.md`.

## 8. Record Retention

Governance records are retained **indefinitely** unless explicitly Archived. The following rules apply:

- All `Draft`, `Submitted`, `In Review`, `Approved`, `Ratified`, and `Rejected` records are retained.
- `Withdrawn` records are retained unless the author requests removal and the Architect approves.
- `Superseded` records are retained; their `Status:` line is updated to `Superseded`, and the new artifact is cross-referenced in their header.
- `Archived` records are retained; they remain searchable but cannot be cited by new `active` artifacts.

**Immutability.** Once a record enters `Ratified` or `Approved` status, its content is **immutable**. Corrections are made by issuing a new FD or ADR that supersedes the original; the original is never edited in place.

## 9. Supersession Rules

A governance artifact may be superseded only by:

- A higher-level artifact in the hierarchy (e.g., an FD may supersede a Standard).
- An artifact of the same level with later status / version / date / ID, applied per §4 above.
- An explicit FD that declares `supersedes: <ID>`.

Supersession requires:

1. An explicit declaration in the new artifact's header (`Supersedes: <ID>`).
2. A `Status: Superseded` update in the old artifact's header (not a content edit; only the header line changes).
3. A cross-reference back from the old artifact to the new one (`Superseded By: <ID>`).

## 10. Emergency-Change Restrictions

Emergency changes are permitted only when:

- An `active` artifact is producing harm (security, data integrity, legal).
- No normal-cycle change-control can complete in time to prevent the harm.

Emergency changes require:

- An `EMERGENCY-FD-NNNN-<slug>.md` artifact (FD with prefix `EMERGENCY-`).
- An immediate post-hoc review within seven (7) calendar days.
- A subsequent normal FD that either ratifies, modifies, or withdraws the emergency change.

**Foundation Constitution amendments are never eligible for emergency change.**

## 11. Relationship to the Constitution

This Governance Model is **subordinate to the Constitution** (Constitution §1, L1 > all). It does not contradict the Constitution and does not redefine its content. Where this document and the Constitution appear to conflict, the Constitution prevails.

The Constitution is ratified by `FD-0001`, which is itself created under this Governance Model. This is **non-circular**: the Provisional Constitution governs Foundation work on a best-effort basis (Constitution §17.3, §17.4); Task 02 establishes the FD mechanism that makes ratification possible; once FD-0001 is ratified, the Constitution enters `Ratified` status and governs formally.

## 12. Relationship to Future Standards and Projects

- **Foundation Standards** (Tasks 03–04, L3) elaborate the Constitution's normative rules into operational specifications. Standards may not contradict the Constitution or an active FD.
- **Engine, SDK, Plugin, Workspace specifications** (Tasks 05–11, L5) implement the Standards. They are subordinate to both Standards and FDs.
- **Projects** (post-Foundation, L6–L8) inherit Foundation governance. Projects may add Project-specific rules via PRFCs, but those rules may not contradict the Constitution, any active FD, or any active Foundation Standard.
- **Releases** (post-Foundation, declared via Foundation RC at Task 12) are coordinated by the Release Manager role and require FD approval.

## 13. Ratification of This Document

This Governance Model is itself **Draft / In Review**. Its formal ratification requires:

- A successful Quality Gate review (per the Audit and Review records accompanying this Task).
- An FD that ratifies this Governance Model and its companion documents.

A future FD **may** ratify or supersede governance artifacts only if required by:

- The Constitution,
- A later approved governance decision, or
- The Task 12 Foundation RC review.

Task 12 will decide whether separate ratification is necessary. Until any such FD is issued, this Model governs Foundation work **provisionally**, alongside the Provisional Constitution.

> Note: No `FD-0002-ratify-governance-model.md` is created during Task 02 or Task 02.1. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action.

## 14. Foundation Change Principle (Binding Rule)

> **Adopted by FD-0002 (Ratified, 2026-08-03) per FRFC-0001 (Approved, 2026-08-03). Binding Foundation governance.**

### 14.1 Principle Text (Verbatim)

The Foundation Change Principle, adopted as binding Foundation governance by FD-0002 §3, reads:

> **Foundation Change Principle**
>
> No new Foundation artifact may be introduced unless:
>
> 1. the need is discovered during a Validation Cycle;
> 2. the gap is documented with evidence;
> 3. an RFC is proposed;
> 4. the RFC is reviewed and approved;
> 5. the Foundation is patched through the approved governance process.
>
> **Idea alone is never sufficient to expand the Foundation.**

This text is the normative binding rule. No paraphrasing, semantic reinterpretation, or weakening is permitted by any future artifact unless introduced through an approved FRFC and a ratified implementing FD.

### 14.2 Scope of the Principle

The Foundation Change Principle applies to all Foundation artifacts, including but not limited to:

- The Constitution and its amendments.
- Foundation Decisions (FDs).
- Foundation Standards and Policies.
- Foundation RFCs (FRFCs) and Release RFCs (RRFCs).
- Architecture Decision Records (ADRs) when Foundation-level.
- Engine, SDK, Plugin, Workspace specifications.
- Builder Packs and Releases.
- All Foundation roles (Architect, Builder, Auditor, Reviewer, Maintainer, Release Manager, Project Owner, Contributor).

The Principle applies equally to all Foundation work regardless of source (Builder proposal, Reviewer recommendation, Architect directive, or external trigger).

### 14.3 Operational Workflow

The operational workflow for the Foundation Change Principle is governed by `FOUNDATION/02-Governance/change-control-policy.md` (as patched by FD-0002 §7). The workflow codifies the five steps:

1. Validation Cycle (gap discovered + evidence captured).
2. RFC proposed (FRFC/PRFC/RRFC per `rfc-policy.md`).
3. RFC reviewed and approved (Human Architect + Reviewer).
4. Implementing FD ratified (per `foundation-decision-policy.md`).
5. Foundation patched through approved governance process (existing artifacts only; Audit + Report + Review records).

### 14.4 Source of Binding Authority

This section derives its binding authority from:

- `FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md` (Approved, 2026-08-03 per Architect Decision, Part A).
- `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` (Ratified, 2026-08-03 per Architect Decision, Part B).

### 14.5 Precedence

The Foundation Change Principle is subordinate to the Constitution (Constitution §1, L1 > all). It does not amend, modify, or override the Constitution. Within the Constitution's authority, the Principle prevails over any lower-level artifact that contradicts it.

---

*End of Governance Model v0.1.1-draft (Patched per FD-0002, 2026-08-03).*
