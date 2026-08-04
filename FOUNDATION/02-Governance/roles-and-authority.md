# Roles and Authority

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/02-Governance/roles-and-authority.md`
**Related:** `governance-model.md`; Constitution v0.1.0-draft (Provisional) §5.

---

## 1. Purpose

This document enumerates the **eight roles** recognized by the Research-OS Foundation, defines the responsibility, authority, prohibited actions, required approvals, and conflict-of-interest restrictions for each, and codifies the separation-of-duties rule: **no role may approve its own work**.

The eight roles are:

1. Architect
2. Builder
3. Auditor
4. Reviewer
5. Maintainer
6. Release Manager
7. Project Owner
8. Contributor

Each role is fixed before the actor begins work (Constitution §3 Principle 12 — *Identity before Activity*).

## 2. Common Rules

The following rules apply to every role:

- **Separation of duties.** No individual may hold more than one role on a single artifact (Constitution §5).
- **No self-approval.** A role may not approve, ratify, or sign-off on an artifact it authored or substantially modified.
- **Conflict-of-interest declaration.** A role must declare any actual or apparent conflict of interest (e.g., financial interest, prior authorship of the same artifact) before acting. The declaration is recorded in the relevant governance record.
- **Authority is bounded.** A role's authority is exhausted at the boundary defined in this document. No role may exceed its declared authority even if explicitly invited.
- **AI agents are bound.** Any AI agent (including the Foundation Builder) acts under the Builder role by default. AI agents cannot hold the Architect, Reviewer, or Release Manager roles.

## 3. Architect

### 3.1  Responsibilities

- Defines the architecture of the Foundation (Constitution §0, §3, §13).
- Issues Foundation Decisions (FDs).
- Approves Foundation Standards (L3), Foundation RFCs (L4), and ADRs.
- Signs ratification of the Constitution.
- Approves Foundation Releases (any version promoted to `1.0.0-rc.1` or beyond).

### 3.2  Authority

- Supreme within L2 (Foundation Decisions).
- Final say on conflict resolution when lower-level mechanisms fail (per `disagreement-and-escalation.md`).
- May amend the Constitution (only via amendment procedure, Constitution §17.2).

### 3.3  Prohibited actions

- May not write Builder artifacts (Reports, Audits, Implementation).
- May not modify the Constitution directly; amendments require FRFC + FD + migration plan.
- May not fabricate approvals on behalf of other humans.

### 3.4  Required approvals

- All FDs require the Architect's signature for ratification.
- Constitution amendments require explicit `amends-constitution: true` flag in the FD.

### 3.5  Conflict-of-interest restrictions

- An Architect who drafted an artifact under review may not approve that artifact as Architect.
- An Architect who is also a Project Owner must declare the conflict and recuse from any FD affecting that Project.

### 3.6  Self-approval

**No.** The Architect may not approve an artifact they authored. Ratification of the Constitution requires an Architect distinct from the Constitution's author.

## 4. Builder

### 4.1  Responsibilities

- Constructs Foundation artifacts within the rules defined by the Architect.
- Executes Foundation Tasks under the Foundation Task Protocol (Constitution §15).
- Produces Builder Reports, Audit (self-audit), and Review records per Task.
- Declares Task scope per §15.5 Per-Task Scope Declaration.

### 4.2  Authority

- L7 and below (operational artifacts).
- May draft any Foundation artifact but may not approve it.
- May implement approved work but may not independently redefine architecture.

### 4.3  Prohibited actions

- May not redefine architecture.
- May not approve its own audit (a separate Reviewer must approve the Audit).
- May not ratify the Constitution.
- May not declare a Release.
- May not modify files outside the declared allowed-file list (§15.5).
- May not fabricate human signatures or approvals.
- May not impersonate the Architect.

### 4.4  Required approvals

- All Builder artifacts require Reviewer approval before becoming `active` or `ratified`.
- Any change to an active Standard requires a Foundation Decision (FD).
- Any change to Task scope requires explicit human approval recorded in the Task Report before the change is made.

### 4.5  Conflict-of-interest restrictions

- The Builder who authored an artifact may not serve as Reviewer for that artifact.
- The Builder may not self-assign role escalation; promotion to Reviewer for their own work is forbidden.

### 4.6  Self-approval

**No.** The Builder may not approve any artifact they authored, including their own Audit. The Audit must be confirmed by a Reviewer.

## 5. Auditor

### 5.1  Responsibilities

- Verifies compliance of Foundation artifacts against the Constitution, active Standards, and active FDs.
- Issues Audit Reports (`AUDIT-<scope>-<NN>-<slug>.md`).
- Records compliance gaps, version mismatches, scope-control violations, and cross-reference failures.

### 5.2  Authority

- May flag artifacts as non-compliant.
- May recommend halting of work that violates a Hard Prohibition (Constitution §15.3).
- May not modify audited artifacts.

### 5.3  Prohibited actions

- May not modify the audited artifact.
- May not declare an artifact Approved or Ratified (that is the Reviewer's and Architect's role, respectively).
- May not act as Reviewer for the same artifact.

### 5.4  Required approvals

- The Audit itself is reviewed by a separate Reviewer before its findings are binding.

### 5.5  Conflict-of-interest restrictions

- The Auditor may not be the same individual as the Builder or the Reviewer for the artifact audited.

### 5.6  Self-approval

**No.** The Auditor may not approve the artifact they audited. Approval is the Reviewer's role.

## 6. Reviewer

### 6.1  Responsibilities

- Performs human Review on artifacts in `Submitted` / `In Review` status.
- Issues Review Records (`REVIEW-<scope>-<NN>-<slug>.md`).
- Approves, requests changes, or rejects the artifact.

### 6.2  Authority

- May transition an artifact between `Submitted → In Review → Approved | Changes Requested | Rejected`.
- May not ratify the Constitution (Architect-only).
- May not approve a Release (Release Manager + Architect).

### 6.3  Prohibited actions

- May not be the same individual as the Builder or Auditor for the same artifact.
- May not modify the artifact beyond typo fixes during `In Review`.
- May not withhold approval arbitrarily; all decisions must cite the specific Quality Gate criterion (Constitution §11) that the artifact fails.

### 6.4  Required approvals

- Reviewer's signature is recorded in the Review Record.
- Constitutional ratification requires the Architect's signature in addition to the Reviewer's disposition.

### 6.5  Conflict-of-interest restrictions

- The Reviewer must be independent of the Builder (different individual).
- The Reviewer must disclose prior involvement (e.g., advisory role) before accepting the review.

### 6.6  Self-approval

**No.** The Reviewer may not have authored the artifact under review.

## 7. Maintainer

### 7.1  Responsibilities

- Performs corrections and routine updates within an FD-bounded scope.
- Updates links, fixes typos, applies approved patches.

### 7.2  Authority

- FD-bounded; cannot change architecture.
- May apply PATCH-level changes without additional FD, if bounded by an existing FD that authorizes the maintenance window.
- May not apply MINOR or MAJOR changes without a new FD.

### 7.3  Prohibited actions

- May not amend an active Standard beyond typo fixes.
- May not bypass the change-control policy.
- May not operate outside their FD-bounded scope.

### 7.4  Required approvals

- Maintainer scope is established by FD (`maintainer-scope: <ID>`).
- All Maintainer actions are recorded in the Maintainer's log (`MAINT-<scope>-<NN>.md`).

### 7.5  Conflict-of-interest restrictions

- A Maintainer who is also the Builder for the same artifact must recuse from Maintainer actions on it.

### 7.6  Self-approval

**No.** Maintainer actions require a separate Reviewer sign-off (or, for routine PATCHes, an Architect-bounded pre-approval).

## 8. Release Manager

### 8.1  Responsibilities

- Coordinates Foundation Releases.
- Produces Release Notes and Release Reports.
- Verifies that all Foundation Tasks required for the Release milestone have passed review.

### 8.2  Authority

- May declare a Release *candidate* but may not declare a Release `ratified`.
- May aggregate Release-blocker findings from Audits and Reviews.
- May not modify content of artifacts being released.

### 8.3  Prohibited actions

- May not combine Release decisions with content edits.
- May not declare a Release that contradicts an active FD or the Constitution.
- May not release an artifact whose Quality Gate has not been confirmed.

### 8.4  Required approvals

- Release ratification requires the Architect's signature.
- The Foundation RC (v1.0.0-rc.1) requires Task 12 review to have passed (Constitution §14.1).

### 8.5  Conflict-of-interest restrictions

- The Release Manager may not be the Builder or Maintainer for any artifact in the Release.

### 8.6  Self-approval

**No.** Release ratification is the Architect's authority.

## 9. Project Owner

### 9.1  Responsibilities

- Owns a Project hosted on Research-OS.
- Defines Project-level governance within Foundation constraints.
- Issues Project Decisions (PDs) and Project RFCs (PRFCs).

### 9.2  Authority

- Project-internal authority, bounded by Foundation governance (Constitution, FDs, Standards).
- May not amend Foundation-level artifacts.

### 9.3  Prohibited actions

- May not redefine Foundation governance.
- May not issue a PRFC that contradicts an active FD or Foundation Standard.

### 9.4  Required approvals

- New Projects require Foundation approval (FD-level) before instantiation.
- Major Project releases require Architect approval if they affect cross-Project interfaces.

### 9.5  Conflict-of-interest restrictions

- A Project Owner may not serve as Architect on FDs that directly affect their Project.

### 9.6  Self-approval

**No.** Project decisions that affect cross-Project concerns require independent Reviewer approval.

## 10. Contributor

### 10.1  Responsibilities

- Submits artifacts (RFCs, ADRs, Evidence, Reports) within their declared role.
- Follows the Foundation Task Protocol when assigned a Task.
- Reports disagreements per `disagreement-and-escalation.md`.

### 10.2  Authority

- Limited to drafting and submission.
- May not approve, ratify, or sign-off on any artifact.

### 10.3  Prohibited actions

- May not modify active artifacts directly.
- May not bypass Review.

### 10.4  Required approvals

- All Contributor artifacts require Reviewer approval.

### 10.5  Conflict-of-interest restrictions

- A Contributor who is also a Project Owner must declare the dual role and recuse from any review affecting their Project.

### 10.6  Self-approval

**No.** Contributors never approve their own work.

## 11. Cross-Role Boundaries

The following boundaries are non-negotiable:

| Boundary | Rule |
|---|---|
| Builder ↔ Architect | Builder drafts; Architect approves. The Builder may not become Architect for the same artifact. |
| Builder ↔ Reviewer | Builder may not review their own artifact. |
| Builder ↔ Auditor | Builder may not audit their own artifact (separation of duties for self-audits; self-audits must be confirmed by a separate Reviewer). |
| Auditor ↔ Reviewer | Auditor may not review the same artifact they audited. |
| Maintainer ↔ Reviewer | Maintainer may not review their own maintenance changes. |
| Release Manager ↔ Architect | Release Manager may not sign a Release; Architect signs. |
| Project Owner ↔ Architect | Project Owner may not sign FDs affecting their own Project. |
| AI agent ↔ Architect | AI agent may not act as Architect. |

## 12. AI Agents and the Builder Role

AI agents (including the Foundation Builder that produces this document) operate under the **Builder role** by default. They may:

- Draft artifacts.
- Produce Reports, self-Audits, and Review records.
- Implement work declared in a Task's scope.

AI agents **may not**:

- Self-approve their own work.
- Sign as Architect, Reviewer, or Release Manager.
- Fabricate human identities, signatures, or approval timestamps.
- Promote an artifact to `Ratified` status.

Where the Builder role produces an artifact that requires human approval (e.g., `FD-0001`), the artifact must remain in `Pending Ratification` status until an explicit human instruction supplies the approval.

---

*End of Roles and Authority v0.1.0-draft.*
