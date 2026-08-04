# FRFC-0001 — Foundation Change Principle

**ID:** `FRFC-0001-foundation-change-principle`
**Title:** Establish the Foundation Change Principle as binding Foundation governance
**Status:** Approved
**Version:** 0.1.0-draft
**Date:** 2026-08-03
**Author:** Foundation Builder (per `roles-and-authority.md`; per Architect Authorization, 2026-08-03, Part B); reviewed and approved by Human Architect per Architect Decision, 2026-08-03, Part A
**Related Constitution Version:** v0.1.0-draft (Ratified by FD-0001)
**Supersedes:** none
**Superseded By:** none
**Decision Scope:** Establish a normative Foundation Change Principle that constrains how new Foundation artifacts may be introduced; define Foundation expansion; enumerate changes that require RFC approval and changes that constitute permitted non-architectural maintenance; propose a governance workflow; identify candidate patch targets without applying any patch.
**Affected Artifacts (proposed, not modified in this RFC cycle):** Constitution change-control provisions (proposed); `FOUNDATION/02-Governance/governance-model.md` (proposed); `FOUNDATION/02-Governance/change-control-policy.md` (proposed); Foundation Freeze rules (proposed); `FOUNDATION/README.md` Rules of Engagement (proposed).
**Migration Plan:** not required (this RFC proposes a new governance principle; if approved, the implementing FD would carry a Migration Plan describing how existing frozen-artifact rules are reconciled with the new principle).
**Last Transition:** In Review → Approved, 2026-08-03 (Human Architect per Architect Decision, Part A; implementing FD authorized separately per Part B).

> **Status note.** The current RFC lifecycle status is `Approved` (transitioned from `Draft` per Architect Decision, 2026-08-03, Part A). All five files in the FRFC-0001 cycle consistently identify the FRFC-0001 lifecycle status as `Approved`. Each companion artifact retains its own applicable document or review status (Audit `Verdict: PASS`; Review `Disposition: Approved with Notes`; Report `Draft / In Review` per its own schema). **Revision history (2026-08-03, Architect Revision Cycle 01):** an earlier version of this RFC recorded initial status as `Proposed`. Architect Review disposition `Revision Required` (2026-08-03) identified that `Proposed` is not in the `rfc-policy.md` §5 enum and that an Architect instruction permitting authorship does not silently amend the RFC Policy. Status was corrected to `Draft` per `rfc-policy.md` §5. The correction is recorded as Audit finding F-1 (Resolved). On 2026-08-03, status was further transitioned from `Draft` to `Approved` per Architect Decision, Part A. RFC Policy §5 enum is unchanged.

**Related:** Constitution v0.1.0-draft §3 (Design Principles), §7 (Foundation Decisions), §9 (Naming Convention), §10 (Cross Reference Policy), §11 (Quality Gate), §12 (Deprecation Policy), §13 (Future Extension Policy), §15 (Foundation Task Protocol); `FOUNDATION/02-Governance/governance-model.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/02-Governance/approval-workflow.md`; `FOUNDATION/02-Governance/disagreement-and-escalation.md`; `FOUNDATION/02-Governance/roles-and-authority.md`; `FOUNDATION/08-RFCs/rfc-policy.md`; `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md`; `FOUNDATION/03-Standards/schema-standard.md`; `FOUNDATION/03-Standards/directory-standard.md`; `VALIDATION/04-Validation-Report/REPORT-VALIDATION-01.md`; `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-01.md`; `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-01.md`; `FOUNDATION/04-Audits/AUDIT-FOUNDATION-01-foundation-change-principle.md`; `FOUNDATION/06-Reports/REPORT-FOUNDATION-01-foundation-change-principle.md`; `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-01-foundation-change-principle.md`; Correction Cycle 01 (Architect Authorization, 2026-08-03).

---

## §1. Summary

This RFC proposes to establish a normative **Foundation Change Principle** that constrains how new Foundation artifacts may be introduced. The Principle requires (1) that the need be discovered during a Validation Cycle, (2) that the gap be documented with evidence, (3) that an RFC be proposed, (4) that the RFC be reviewed and approved, and (5) that the Foundation be patched through the approved governance process. The Principle explicitly rejects the use of "idea alone" as sufficient cause to expand the Foundation.

The RFC defines **Foundation expansion**, enumerates the categories of change that constitute Foundation expansion and therefore require RFC approval, identifies a set of changes that constitute permitted non-architectural maintenance and do not require an RFC, and proposes a governance workflow. The RFC identifies candidate patch targets (existing governance artifacts) but does **not** modify any patch target in this RFC cycle; implementation requires a separate approved FD.

## §2. Validation Evidence

This RFC is grounded only in evidence already produced by prior Foundation cycles. No new validation findings are invented.

### §2.1 Evidence from Validation Cycle 01

**Source:** `VALIDATION/04-Validation-Report/REPORT-VALIDATION-01.md` (entire document); `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-01.md` (entire document); `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-01.md` (entire document).

**Findings relied upon:**

- The Validation Plan declared seven Validation Objectives across eight categories evaluating Foundation fitness (`validation-plan.md` §3, §4).
- The Validation Report identified gaps G1–G4 and simplifications S1–S3 (`REPORT-VALIDATION-01.md` §9). Among these, G1–G4 are observed gaps in Foundation expansion discipline: gaps that suggest the Foundation lacks a normative procedure constraining how new artifacts may be introduced.
- The Validation Audit identified 10 findings (all Informational / Low) (`AUDIT-VALIDATION-01.md` §4). None are blocking. The Audit confirms the 8-category evaluation reached its verdict.
- The Validation Review recorded an **Approved with Notes** disposition on 2026-08-03 (`REVIEW-VALIDATION-01.md` §4).
- The Foundation Readiness Score is 81/100 — Good (`REPORT-VALIDATION-01.md` §8).
- The Recommended Next Phase identified by the Report is **Maintenance Cycle** (`REPORT-VALIDATION-01.md` §10).

### §2.2 Evidence from FD-0001 Scope Repair

**Source:** `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md` §8.

**Findings relied upon:**

- During the prior ratification cycle, the proposed Foundation Change Principle was inserted into `FD-0001` §8 and into `FOUNDATION/README.md` Rules of Engagement and into the `CHANGELOG.md` ratification-record section as if it were approved, ratified, effective, or binding.
- The Constitution text (the artifact FD-0001 is authorized to ratify) does **not** itself contain the Foundation Change Principle; FD-0001 §3 explicitly states that the FD "does **not** modify the Constitution's content."
- The five-point principle text therefore appeared in FD-0001 §8 as a normative augmentation of the FD's scope — an augmentation that the FD's `ratifies-constitution: 0.1.0-draft` flag does not authorize.

### §2.3 Evidence from Correction Cycle 01

**Source:** `FOUNDATION/04-Audits/AUDIT-FOUNDATION-01-foundation-change-principle.md` (entire document); `FOUNDATION/06-Reports/REPORT-FOUNDATION-01-foundation-change-principle.md` (entire document); `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-01-foundation-change-principle.md` (entire document).

**Findings relied upon:**

- The Correction Audit verified (verdict PASS; finding-count 0) that the Foundation Change Principle is **not** represented as approved, ratified, adopted, effective, or binding in `FD-0001`, `FOUNDATION/README.md`, or `CHANGELOG.md`.
- The Correction Audit recorded the version-sequence discrepancy as an unresolved Observation (`AUDIT-FOUNDATION-01-…` §4.1 O-1).
- The Correction Report recorded the non-normative note inserted in `FD-0001` §8: "Validation Cycle 01 identified a potential governance gap concerning evidence-driven Foundation expansion. Resolution is deferred to a separately proposed and approved Foundation RFC. No governance principle is adopted, ratified, or rendered binding by this FD." (`REPORT-FOUNDATION-01-…` §3).
- The Correction Review recorded a disposition of **Approved with Notes** on 2026-08-03, with three non-blocking Notes (file-count wording, correction-cycle numbering ambiguity, version-sequence ambiguity) (`REVIEW-FOUNDATION-01-…` §6, §7).

### §2.4 Identified Risk of Uncontrolled Foundation Expansion

**Source:** This RFC, derived from the above evidence.

**Findings relied upon:**

- The FD-0001 scope repair demonstrates that an architectural change (the proposed Foundation Change Principle) was inserted into binding Foundation records without an RFC and without human-Reviewer approval. The repair was performed by the Architect under explicit Authorization (Correction Cycle 01), not by an approved RFC.
- The Foundation currently lacks a normative procedure (other than the RFC Policy itself, which applies to proposed changes after they are initiated) that requires Validation-discovered evidence before a new artifact is proposed.
- Without such a principle, a Builder role (or any other role) could introduce a new Foundation artifact motivated by "idea alone" — an internal intuition, a stylistic preference, a perceived gap, or an external suggestion — without first producing Validation evidence or an RFC.

### §2.5 Identified Risk of Expanding Foundation Architecture From Ideas Without Validation Evidence

**Findings relied upon:** derived from the above.

- The Foundation's `Foundry Freeze State` (per Architect Authorization, 2026-08-03) is the only existing procedural control preventing arbitrary expansion during the post-Freeze phase. Freeze State governs timing (no changes during Freeze) but does not by itself constrain the **substance** of post-Freeze expansion.
- Without a substantive principle, post-Freeze expansion decisions depend on Architect discretion alone, with no normative requirement for Validation evidence or RFC review. This creates a single-point-of-failure risk: a future Architect decision could introduce new Foundation architecture without the discipline that Validation evidence and RFC review provide.

## §3. Problem Statement

The Research-OS Foundation currently lacks a normative governance principle that requires:

1. **Evidence basis** — a new Foundation artifact must be motivated by a Validation-discovered gap (or equivalent recorded evidence), not by an idea alone.
2. **RFC discipline** — a new Foundation artifact must be proposed, reviewed, and approved through the RFC workflow before it is patched into the Foundation.
3. **Separation of approval from implementation** — RFC approval does not automatically authorize implementation; the Architect must explicitly combine approval and patch authorization.
4. **Patch governance** — implementation of an approved RFC must proceed through the approved governance process (Audit, Report, Review), not by ad-hoc modification.

The absence of such a principle was demonstrated by the FD-0001 scope repair and Correction Cycle 01, in which a five-point principle was inserted into binding Foundation records without RFC review or approval.

The problem is **not** that the principle is wrong or that the principle should not become Foundation governance. The problem is that the principle was introduced into Foundation records through a path that did not satisfy the Foundation's own governance rules. The Foundation currently has no normative rule that would have prevented this. RFC-0001 proposes to establish such a rule.

## §4. Proposed Principle

### §4.1 Normative Text (Proposed)

The following text is proposed to become the binding **Foundation Change Principle** if and only if this RFC is approved and the implementing FD is ratified:

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

### §4.2 Authority and Effect (Proposed)

If approved and ratified, the Foundation Change Principle becomes a binding governance rule of the Research-OS Foundation. It applies to every Foundation role (Builder, Auditor, Reviewer, Maintainer, Architect) and to every Foundation artifact. A violation of the Principle is a governance defect; an artifact introduced in violation of the Principle is **non-conformant** and is subject to Correction Cycle treatment.

### §4.3 Relationship to the RFC Policy (Proposed)

The Foundation Change Principle is **complementary** to `FOUNDATION/08-RFCs/rfc-policy.md`. The RFC Policy specifies the workflow once an RFC has been initiated. The Foundation Change Principle specifies the conditions under which an RFC may be initiated and the conditions under which a new artifact may be introduced. The two together form a complete governance loop:

- The Principle answers "**may** this artifact be introduced?" (gating rule).
- The Policy answers "**how** is this artifact reviewed and approved?" (workflow).

Neither subsumes the other.

## §5. Definitions

### §5.1 Foundation Expansion

**Foundation expansion** is either:

1. **Creating a new Foundation artifact** — any artifact not previously present at the path where it would be introduced, regardless of its class (Constitution provision, Governance document, Standard, Policy, FD, ADR, Audit, Report, Review, Evidence, Manifest, Statistics, RFC, Pack, Release, Workspace, Project, Engine, Runtime, SDK, Plugin specification).
2. **Modifying an existing Foundation artifact in a way that expands** any of the following:
   - **Authority** — granting new decision rights, approval rights, or veto rights to any role.
   - **Scope** — extending the artifact's subject matter, applicability, or boundary.
   - **Behavior** — changing the artifact's procedural, lifecycle, or execution rules.
   - **Architecture** — adding new schemas, directories, paths, classes, or interfaces.
   - **Permissions** — granting or expanding access to protected operations.
   - **Compatibility obligations** — adding new backward/forward compatibility guarantees.
   - **Lifecycle stages** — adding, removing, or reordering artifact lifecycle states.
   - **Governance roles** — creating, removing, merging, or splitting roles.
   - **Artifact classes** — creating or removing a class of Foundation artifact.
   - **Execution boundaries** — changing what the Foundation governs vs. what is delegated to Projects.

### §5.2 Foundation Artifact

A **Foundation artifact** is any artifact stored within the `FOUNDATION/` directory tree of the Research-OS repository and governed by the Constitution.

### §5.3 Validation Cycle

A **Validation Cycle** is a Foundation-level evaluation cycle declared under the Foundation Task Protocol (`Constitution §15`) whose purpose is to read Foundation artifacts, evaluate their fitness, document gaps and risks, and produce a Validation Report, Validation Audit, and Validation Review. Validation Cycle 01 is the first such cycle.

#### §5.3.1 Triggered Validation Cycle (Normative Definition)

A Validation Cycle may be triggered by any of the following triggers:

1. **Scheduled.** A Validation Cycle declared on a fixed schedule (e.g., periodic Foundation fitness review) or as part of a declared Maintenance Cycle.
2. **Project-triggered.** A Project encounters a Foundation-scoped gap during Project execution and requests a Foundation Validation to assess the gap.
3. **Implementation-triggered.** A Foundation implementation step (e.g., authoring a Standard, applying a patch) reveals a governance gap that requires Validation evidence.
4. **Audit-triggered.** A Foundation Audit identifies a gap that exceeds the Audit scope and requires a full Validation Cycle to evaluate.
5. **Incident-triggered.** A Foundation-level incident (e.g., a documented scope violation, a documented correction cycle, a recurring pattern of correction cycles) triggers a Validation Cycle to evaluate the underlying governance gap.
6. **Security-triggered.** A documented security concern (e.g., a vulnerability in a Standard, an unauthorized access pattern) triggers a Validation Cycle to evaluate the security posture of the affected Foundation artifacts.
7. **Compatibility-triggered.** A documented compatibility concern (e.g., a breaking change in a Foundation dependency, a cross-Foundation-Project compatibility break) triggers a Validation Cycle to evaluate Foundation compatibility obligations.
8. **Externally triggered.** A material legal, dependency, platform, or operational change in the external environment triggers a Validation Cycle to evaluate the change's Foundation impact.

**Important.** A trigger alone does **not** authorize a Foundation patch. A triggered Validation Cycle must still:

- Record the observed gap as Evidence.
- Capture the evidence in a Foundation artifact consistent with `schema-standard.md` §4.
- Determine whether the gap is Foundation-relevant.
- Recommend whether an RFC is necessary.

The recommendation to author an RFC is a recommendation only; the RFC itself remains subject to the full RFC Policy lifecycle.

### §5.4 Evidence

**Evidence** is a Foundation artifact (per `schema-standard.md` §4) that records an observation, measurement, or fact retrieved or generated during Foundation work. Evidence may take the form of a Validation Report, Audit finding, Review disposition, observed gap, risk record, or other documented observation.

### §5.5 Patch

A **Patch** is any modification to a Foundation artifact that introduces Foundation expansion (per §5.1). Patches are the implementation acts governed by the Foundation Change Principle.

### §5.6 RFC

An **RFC** (Request for Comments) is a Foundation artifact defined by `rfc-policy.md`. For Foundation-level changes, an **FRFC** (Foundation RFC) is required.

## §6. Scope

### §6.1 In Scope

This RFC proposes:

1. A normative Foundation Change Principle (per §4).
2. A definition of Foundation expansion (per §5.1).
3. A classification of changes into those requiring RFC approval (§8) and those constituting permitted non-architectural maintenance (§9).
4. A governance workflow (§10).
5. A human-approval boundary (§11).
6. Candidate patch targets (§12) — proposed, **not** modified.
7. Compatibility, security, and isolation impact analysis (§13, §14).
8. Risks, alternatives, acceptance criteria, rollback plan, and review questions (§15–§19).
9. Decision status (§20).

### §6.2 Out of Scope (Explicitly Excluded)

This RFC **does not address** any of the following unrelated issues. Each requires separate evidence and separate authorization:

1. Constitution version sequence (the `v0.X` vs. `vX.Y.Z-prerelease` discrepancy; absence of an on-disk `v0.2` Constitution file).
2. `-draft` suffix semantics (whether ratification removes the suffix).
3. Correction Cycle numbering conventions (the `01` co-numbering observation recorded in `REVIEW-FOUNDATION-01-…` §6 N-2).
4. Collective Foundation Standard ratification.
5. Foundation RC release.
6. Runtime implementation.
7. Builder Pack generation.
8. APES migration.
9. Amendment of the RFC status lifecycle (changing `Proposed` to `Draft` in this RFC is compliance repair, **not** an amendment of the RFC Policy).

Each excluded item requires separate evidence and separate authorization. Changing `Proposed` to `Draft` in this RFC is compliance repair; it does not amend `rfc-policy.md` §5.

## §7. Foundation Expansion Criteria

A change constitutes **Foundation expansion** (and therefore requires an RFC) if **any** of the following hold:

| # | Criterion | Example |
|---|---|---|
| C-1 | Creates a new Constitution provision | New §18 added to the Constitution. |
| C-2 | Creates a new Governance document | New policy in `FOUNDATION/02-Governance/`. |
| C-3 | Creates a new Foundation Standard | New entry in `FOUNDATION/03-Standards/`. |
| C-4 | Creates a new Foundation Policy | New normative rule that binds Foundation behavior. |
| C-5 | Creates a new Foundation architectural Decision | New FD that augments Foundation architecture. |
| C-6 | Creates a new schema | New class definition in `schema-standard.md`. |
| C-7 | Creates a new protocol | New workflow that governs Foundation behavior. |
| C-8 | Creates a new role | New role in `roles-and-authority.md`. |
| C-9 | Creates a new lifecycle stage | New status added to `governance-model.md` §7. |
| C-10 | Creates a new architectural directory | New numbered prefix in `directory-standard.md`. |
| C-11 | Creates a new Engine, Runtime, SDK, Plugin, Workspace, Pack, Project, or Release specification class | New artifact class definition. |
| C-12 | Modifies an existing artifact in a way that expands authority, scope, behavior, architecture, permissions, compatibility obligations, lifecycle stages, governance roles, artifact classes, or execution boundaries | Per §5.1.2. |

A change that does **not** match any criterion in this table does not constitute Foundation expansion and may proceed without an RFC (subject to the standing change-control policy).

## §8. Changes Requiring RFC Approval

Any change that satisfies **any** criterion C-1 through C-12 of §7 requires RFC approval. The approval workflow is defined by `rfc-policy.md` and `approval-workflow.md`.

A change proposed by a role that lacks the authority to make the change is **not** exempt from the RFC requirement solely on grounds of role; the RFC workflow is required regardless.

A change that has been documented as a correction (per Correction Cycle 01, `REVIEW-FOUNDATION-01-…` §7 disposition) is **not** exempt from the RFC requirement solely on grounds of being a correction; the correction cycle addresses **scope violations**, not the introduction of new Foundation artifacts.

## §9. Allowed Non-Architectural Maintenance

The following changes do **not** constitute Foundation expansion and may proceed without an RFC, provided they preserve the existing meaning of every artifact they touch:

| # | Action | Constraint |
|---|---|---|
| M-1 | Spelling corrections | No semantic change. |
| M-2 | Grammar corrections | No semantic change. |
| M-3 | Formatting repairs | No semantic change. |
| M-4 | Broken-link repairs | Cross-reference target must remain the same artifact. |
| M-5 | Incorrect cross-reference repairs | Cross-reference must be updated to point to the same artifact the original referenced. |
| M-6 | Metadata reconciliation | Metadata field must remain semantically equivalent; e.g., correcting a date format or a version field that was inadvertently mistyped. |
| M-7 | Status updates explicitly authorized by an approved decision | The approved decision must be cited. |
| M-8 | Required Audit, Report, Review, and Evidence records | Records required by `schema-standard.md` or by an approved RFC. |
| M-9 | Accidental model or tool markup removal | The removed markup must be demonstrably accidental (e.g., leaked reasoning tags, tool-internal markers) and must not be part of the artifact's intended content. |
| M-10 | Removal of content added outside authorized scope | The removed content must be demonstrably out-of-scope per the citing Architect or Reviewer instruction; the citation must be recorded. |

Any change affecting **meaning, authority, scope, behavior, architecture, compatibility, permissions, or lifecycle** remains governed by RFC approval regardless of whether it appears in this table.

If uncertainty exists about whether a change is non-architectural maintenance, the change **must** be processed through an RFC; the default is governance, not exemption.

### §9.1 Artifact Exclusions (Normative)

The following records do **not** count as Foundation architectural expansion when they are required by an existing authorized process and introduce no new authority, no new architecture, and no new schema:

| # | Excluded Artifact | Reason for Exclusion |
|---|---|---|
| E-1 | RFC proposal records (FRFC, RRFC, PRFC) | Required by `rfc-policy.md`; carry no authority beyond what the RFC Policy specifies. |
| E-2 | Audit records (per `schema-standard.md` §9) | Required by Constitution §11 Quality Gate; verify but do not expand. |
| E-3 | Report records (per `schema-standard.md` §5) | Required by the Task Protocol; record but do not expand. |
| E-4 | Review records (per `schema-standard.md` §6) | Required by the Task Protocol; record dispositions but do not expand. |
| E-5 | Evidence records (per `schema-standard.md` §4) | Required by the Foundation Change Principle (clause 2); record observations but do not expand. |
| E-6 | Authorized correction records (e.g., Correction Cycle 01 artifacts) | Required by `change-control-policy.md` scope-violation treatment; record scope repair but do not expand. |
| E-7 | Status reconciliation records | Required to reconcile artifact status with current state; record reconciliation but do not expand. |

These exclusions apply **only** when the listed records are:

- Required by an existing authorized process (Constitution, Standard, Policy, approved FD, or approved RFC).
- Substantive scope is limited to the record's class per `schema-standard.md` §4–§9.
- Free of new authority, new architecture, or new schema beyond what the existing authorized process already permits.

Excluded records **remain subject to** the standing scope, naming, and approval controls of the Foundation (e.g., `directory-standard.md`, `schema-standard.md`, `roles-and-authority.md`, `approval-workflow.md`). If a record would introduce new authority, architecture, schema, or scope beyond its class, it does **not** qualify for exclusion; it requires an RFC.

## §10. Governance Workflow

The Foundation Change Principle, if approved and ratified, governs expansion through the following workflow:

```
Validation discovers a Foundation gap
        ↓
Evidence is recorded
        ↓
A Foundation RFC is proposed
        ↓
RFC Audit and human Review
        ↓
Architect disposition
        ↓
Separate Foundation Patch authorization
        ↓
Patch implementation
        ↓
Patch Audit and Review
        ↓
Foundation returns to Freeze State
```

### §10.1 Workflow Steps

1. **Validation discovers a Foundation gap.** A Validation Cycle, Audit, or Review identifies a gap in Foundation governance, schema, workflow, or scope. The gap is recorded as Evidence (per `schema-standard.md` §4).
2. **Evidence is recorded.** The Evidence record identifies the gap, the conditions under which it was observed, the limitations of the observation, and the consuming artifact.
3. **A Foundation RFC is proposed.** A Builder, Auditor, Reviewer, Maintainer, Architect, or Project Owner authors an FRFC (or RRFC, if release-governance-scoped). The RFC must declare its evidence basis (§2 above for this RFC; the same pattern applies generally).
4. **RFC Audit and human Review.** The RFC is audited against the §11 Quality Gate (`AUDIT-FRFC-…`) and reviewed by the human Architect (`REVIEW-FRFC-…`).
5. **Architect disposition.** The Architect records a disposition on the RFC Review: `Approved`, `Approved with Notes`, `Rejected`, `Withdrawn`. The disposition may include required corrections.
6. **Separate Foundation Patch authorization.** RFC approval does **not** automatically authorize implementation. The Architect must issue a **separate, explicit authorization** for the patch. The patch authorization may be combined with the RFC approval on the same Review record (per the Architect's discretion), but the combination must be explicit and recorded.
7. **Patch implementation.** The implementing FD (or PRFC/PD, RRFC/RD, depending on class) is authored, audited, and reviewed. The patch modifies the target artifacts.
8. **Patch Audit and Review.** The patch's FD (or equivalent) is audited and reviewed.
9. **Foundation returns to Freeze State.** After the patch is complete, the Foundation returns to its prior Freeze State unless the patch itself modifies the Freeze State.

### §10.9 Emergency Handling (Normative Clarification)

The Foundation Change Principle does **not** permit emergency conditions to bypass evidence, RFC review, or human approval authority. For an urgent security, integrity, or availability risk affecting the Foundation, the process uses an **expedited** application of the existing mechanisms — it does **not** invent a new emergency governance artifact class.

For an emergency Foundation change, the expedited application requires:

1. **Evidence.** A documented record of the urgent security, integrity, or availability risk. The evidence may be condensed but must identify the risk, the affected artifacts, and the basis for the urgency.
2. **RFC or emergency change record.** Either:
   - An RFC authored under the existing RFC Policy lifecycle with an expedited path to `Submitted → In Review → Approved`, **or**
   - An emergency change record authored under the existing governance mechanisms (e.g., `change-control-policy.md` §5, if such a mechanism exists in the current governance).

   If the current governance does **not** support an emergency record, this RFC does **not** invent one; the RFC only recommends an expedited application of the existing mechanisms. The implementing FD or a subsequent RFC may establish such a mechanism if the Foundation baseline decision supports it.
3. **Human approval.** The disposition is recorded by the human Architect (or designated human Reviewer) per `roles-and-authority.md`. AI agents may not approve emergency changes on behalf of humans.
4. **Patch audit.** The emergency patch is audited against the §11 Quality Gate after the fact. The audit may be condensed but must verify scope, cross-reference, isolation, and security boundary compliance.
5. **Retrospective review.** A retrospective Review is recorded after the patch, capturing: the urgency basis, the expedited path used, the audit outcome, and any follow-on governance actions (e.g., an RFC to formalize the emergency handling mechanism).

The emergency handling above is an **expedited application** of existing mechanisms; it is **not** an exemption from evidence, RFC review, or human approval. No new emergency governance artifact class is created by this RFC.

## §11. Human Approval Boundary

The Foundation Change Principle, if approved and ratified, preserves the **human approval boundary** as defined by `roles-and-authority.md`:

- **All RFCs** require human Architect (or designated human Reviewer) disposition. AI agents may author RFCs but may not approve them.
- **All FDs** require human Architect signature. AI agents may not sign FDs on behalf of humans.
- **All Reviews** require human Reviewer (Architect or designated) signature. AI agents may not fabricate personal name, signature, email, or other identity data.
- **All Architect decisions** are explicit instructions issued by the human Architect role.

The Foundation Change Principle does not modify the human approval boundary; it reinforces it by requiring evidence and RFC review before any governance change.

## §12. Proposed Patch Targets

If this RFC is approved and a separate implementing FD is authorized, the implementing FD may patch the following existing governance artifacts. **No patch target is modified in this RFC cycle.**

| # | Candidate Patch Target | Proposed Patch |
|---|---|---|
| PT-1 | Constitution change-control provisions | Add a new §18 (or equivalent) that establishes the Foundation Change Principle as a binding governance rule. The Constitution amendment requires a separate constitutional-amendment FD with a Migration Plan and a MAJOR version bump (per `Constitution §17.2`). |
| PT-2 | `FOUNDATION/02-Governance/governance-model.md` | Add a new section that defines Foundation expansion and references the Foundation Change Principle. |
| PT-3 | `FOUNDATION/02-Governance/change-control-policy.md` | Add a new section that requires Validation evidence before Foundation artifact introduction. |
| PT-4 | Foundation Freeze rules (currently recorded in the Architect Authorizations) | Codify Freeze rules as governance artifacts (not as ad-hoc Architect instructions). |
| PT-5 | `FOUNDATION/README.md` Rules of Engagement | Replace the current "Pending governance proposal (non-normative)" note with a binding reference to the ratified Principle, once the Principle is ratified. |

The implementing FD must demonstrate that **no existing governance artifact can correctly contain the Principle** before proposing a new Standard. **No new Standard is proposed by this RFC.**

## §13. Compatibility Impact

If the Foundation Change Principle is approved and ratified:

- **Backward compatibility.** No existing Foundation artifact is invalidated by the Principle's adoption; existing artifacts remain at their current versions and statuses. Existing Validation evidence (Validation Cycle 01, FD-0001, Correction Cycle 01) is preserved.
- **Forward compatibility.** The Principle establishes a forward-binding rule that applies to all subsequent Foundation expansion.
- **Migration compatibility.** No breaking change to existing artifact shapes or workflows is required. The Principle adds a **precondition** (Validation evidence + RFC review) for future expansion; it does not retroactively invalidate existing artifacts.

A MAJOR version bump of the Constitution would be required if PT-1 is patched (per `Constitution §17.2`); other patch targets (PT-2 through PT-5) would carry PATCH or MINOR bumps per their respective schemas.

## §14. Security and Isolation Impact

### §14.1 Security Impact

The Principle **increases** the Foundation's security posture by requiring:

- Evidence basis for new artifacts (reduces the risk of artifacts introduced without justification).
- RFC review for Foundation expansion (introduces a multi-step review process that is harder to bypass than ad-hoc modification).
- Separation of RFC approval from patch authorization (introduces a second authorization gate that requires explicit Architect action).

### §14.2 Isolation Impact

The Principle **preserves** Foundation isolation:

- Project-specific governance, lifecycle, schema, or implementation rules remain out of Foundation scope.
- The Principle applies only to Foundation artifacts; it does not extend the Foundation's authority into Projects.
- The Principle does not modify the Project-Foundation boundary.

### §14.3 Threat Model

The Principle addresses the threat of **uncontrolled Foundation expansion** motivated by idea alone. It does **not** address:

- Threats to Project isolation (governed by other artifacts).
- Threats to artifact integrity (governed by `schema-standard.md`).
- Threats to the Foundation's runtime behavior (no Runtime exists at Foundation RC pre-release).

## §15. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-1 | The Principle becomes a **gatekeeping mechanism** that blocks legitimate Foundation work. | Medium | The Principle requires Validation evidence and RFC review; it does not require the Validation Cycle to succeed — it requires the cycle to discover and document the gap. Legitimate work can proceed once evidence is recorded. |
| R-2 | The Principle's definition of "Foundation expansion" is too narrow and misses a category of change. | Medium | The definition (§5.1, §7) is intentionally enumerated with explicit categories (C-1 through C-12). The default is governance, not exemption (per §9). Future gaps are addressed through subsequent RFCs. |
| R-3 | The Principle is misinterpreted as applying to Project artifacts. | Low | The Principle explicitly applies to Foundation artifacts (§5.2). The Isolation Impact (§14.2) restates this. |
| R-4 | The Principle creates an unbounded Validation Cycle burden on every Foundation change. | Medium | The Principle requires Validation evidence, not a new Validation Cycle. Existing Validation Cycle outputs may be cited. A future RFC may define "Validation evidence" thresholds; this RFC deliberately leaves thresholds to the implementing FD. |
| R-5 | The Principle is approved without an implementing FD, leaving the Foundation in an ambiguous state. | Medium | RFC approval does not automatically authorize implementation (§10 step 6). A separate explicit patch authorization is required. The Foundation remains Frozen until the implementing FD is approved. |
| R-6 | The patch targets (PT-1 through PT-5) conflict with each other or with existing governance. | Low | The implementing FD must demonstrate compatibility among patch targets and with existing governance. Conflicts are resolved per `disagreement-and-escalation.md`. |
| R-7 | The Constitution amendment (PT-1) requires a MAJOR version bump that conflicts with the current Freeze State. | Low | The MAJOR version bump is a precondition of the amendment, not a contradiction with Freeze State. The amendment is the path by which the Freeze is adjusted; the Freeze is the state until amendment. |

## §16. Alternatives Considered

| # | Alternative | Reason Rejected |
|---|---|---|
| A-1 | Do not establish a normative Principle; continue with ad-hoc discipline. | Ad-hoc discipline failed once (FD-0001 scope repair). A normative rule is required to make the discipline enforceable. |
| A-2 | Establish the Principle as a non-normative recommendation. | A non-normative recommendation has no governance weight. The purpose of this RFC is to establish a binding rule. |
| A-3 | Establish the Principle as a Foundation Standard rather than a Constitution amendment. | A Foundation Standard is sufficient for some categories (PT-2, PT-3, PT-5), but the Principle's role as the **gating rule** for all Foundation expansion is best housed in the Constitution. A Standard would be subordinate and could be overridden by a higher-authority document. |
| A-4 | Combine the Principle's RFC approval and patch authorization in a single step. | The Architect's Authorization for this RFC explicitly separates the two steps (§10 step 6). Combining them removes the second authorization gate and weakens the Principle's enforceability. |
| A-5 | Apply the Principle retroactively to existing Foundation artifacts (e.g., re-validate FD-0001). | The Principle's §13 (Compatibility Impact) preserves existing artifacts. Retroactive application would invalidate the Foundation's existing work without evidence basis. |
| A-6 | Author the implementing FD as part of this RFC. | The Architect's Authorization (§10 step 6, Hard Prohibitions) explicitly forbids implementation in the RFC cycle. A separate FD is required. |

## §17. Acceptance Criteria

This RFC is **acceptable** for transition from `Proposed` to `Submitted` (or to any other RFC Policy §5 status) if and only if all of the following hold:

| # | Criterion | Verified By |
|---|---|---|
| AC-1 | The RFC's evidence basis is grounded only in Validation Cycle 01, FD-0001 Scope Repair, Correction Cycle 01, and the risks derived from those. No additional validation findings are invented. | Audit `AUDIT-FRFC-0001-…` |
| AC-2 | The proposed Principle text matches §4.1 verbatim. | Architect Review |
| AC-3 | The definition of Foundation expansion (§5.1) is unambiguous and complete with respect to §7's criteria. | Architect Review |
| AC-4 | The list of changes requiring RFC approval (§8) is consistent with §7's criteria. | Audit |
| AC-5 | The list of permitted non-architectural maintenance (§9) does not include any change affecting meaning, authority, scope, behavior, architecture, compatibility, permissions, or lifecycle. | Audit |
| AC-6 | The governance workflow (§10) is consistent with `rfc-policy.md` and `approval-workflow.md`. | Audit |
| AC-7 | The human approval boundary (§11) is preserved and not weakened. | Audit |
| AC-8 | The proposed patch targets (§12) are existing governance artifacts and no new Standard is proposed. | Audit |
| AC-9 | The Compatibility Impact (§13) does not retroactively invalidate existing artifacts. | Audit |
| AC-10 | The Security and Isolation Impact (§14) preserves Project isolation. | Audit |
| AC-11 | The Risks (§15), Alternatives (§16), and Acceptance Criteria (§17) are complete. | Architect Review |
| AC-12 | The Rollback Plan (§18) is feasible. | Architect Review |
| AC-13 | The Review Questions (§19) are non-trivial and address the Principle's substantive claims. | Architect Review |
| AC-14 | The Decision Status (§20) records the current status as `Proposed` and identifies the next transition. | Audit |

## §18. Rollback Plan

If this RFC is approved and the implementing FD is ratified, and if subsequent Foundation work demonstrates that the Principle creates an unacceptable burden or is misinterpreted, the rollback path is:

1. A new FRFC is proposed to **withdraw or modify** the Foundation Change Principle.
2. The withdrawing FRFC carries a Migration Plan describing how artifacts introduced under the Principle are reconciled.
3. The withdrawing FRFC follows the same workflow as any other Foundation expansion (per §10): Validation evidence, RFC review, Architect disposition, separate patch authorization.
4. If the Principle is housed in the Constitution (PT-1), the rollback requires a Constitution amendment (per `Constitution §17.2`) with a MAJOR version bump.

If this RFC is **rejected**, no patch occurs and the Foundation continues with ad-hoc discipline (the status quo). The rejection does not require a rollback because no patch was applied.

## §19. Review Questions

The Architect is invited to consider the following questions during Review:

| # | Question |
|---|---|
| Q-1 | Is the proposed Principle text (§4.1) the right rule for the Research-OS Foundation? |
| Q-2 | Does the definition of Foundation expansion (§5.1) cover all categories of change that should require RFC approval? |
| Q-3 | Is the list of permitted non-architectural maintenance (§9) appropriately bounded? |
| Q-4 | Is the governance workflow (§10) consistent with the existing RFC and approval workflows? |
| Q-5 | Should the Principle be housed in the Constitution (PT-1), in the Governance Model (PT-2), in the Change-Control Policy (PT-3), or in some combination? |
| Q-6 | Are the proposed patch targets (§12) the right artifacts to modify, or are there others? |
| Q-7 | Does the Compatibility Impact (§13) adequately address backward and forward compatibility? |
| Q-8 | Are the Risks (§15) complete and accurately assessed? |
| Q-9 | Are the Alternatives (§16) the right set, or are there others that should be considered? |
| Q-10 | What is the right threshold for "Validation evidence" — i.e., does every Foundation change require a full Validation Cycle, or can a single Audit finding or Review observation count as evidence? (This RFC deliberately leaves this to the implementing FD; the Architect may wish to provide guidance.) |

## §20. Decision Status

### §20.1 Current Status

**Status:** `Approved` (transitioned from `Draft` per Architect Decision, 2026-08-03, Part A; in conformance with `rfc-policy.md` §5 Status Lifecycle).

**Revision history (2026-08-03).** An earlier version of this RFC recorded initial status as `Proposed`, which is not in the `rfc-policy.md` §5 enum. Architect Revision Cycle 01 (2026-08-03) corrected the status to `Draft`. The correction is recorded as Audit finding F-1 (Resolved). Per the Architect's instruction: "Architect authorization permits authorship of an RFC but does not silently amend the RFC Policy." Changing `Proposed` to `Draft` is compliance repair, **not** an amendment of the RFC Policy. The Architect Decision, 2026-08-03, Part A subsequently transitioned the RFC from `Draft` to `Approved` (Disposition: Approved with Notes).

### §20.2 Required Next Transitions

The RFC has traversed the following transitions:

| # | Transition | Authority | Date |
|---|---|---|---|
| 1 | `Draft` → `Submitted` (implicit during authoring) | Foundation Builder submits the RFC alongside the Audit, Report, and Review. | 2026-08-03 |
| 2 | `Submitted` → `In Review` (implicit during review cycle) | Human Architect begins Review. | 2026-08-03 |
| 3 | `In Review` → `Approved with Notes` | Human Architect records disposition on the Review. | 2026-08-03 (Architect Decision, Part A) |
| 4 | (co-issued) `Approved` → separate Foundation Patch authorization | Human Architect issues explicit patch authorization (Architect Decision, 2026-08-03, Part B). Implementing FD (FD-0002) drafted and ratified under Patch Cycle 01. | 2026-08-03 |

The Foundation Builder does not auto-transition.

### §20.3 Hard Prohibitions (Restated)

The following actions were prohibited in the FRFC-0001 authoring and Revision Cycle 01 and remain binding in the implementation cycle:

- Modify the Constitution.
- Modify FD-0001.
- Modify Foundation governance or policies **without** an implementing FD ratified by the Architect.
- Modify Foundation Standards.
- Modify `FOUNDATION/README.md`.
- Modify `CHANGELOG.md`.
- Create a new Standard.
- Create a new Policy.
- Create a new FD (except the implementing FD-0002 explicitly authorized by Architect Decision, Part B).
- Implement the proposed Principle without an approved FRFC and an implementing FD.
- Change `FOUNDATION/VERSION`.
- Declare an RC.
- Create or execute a Pack.
- Instantiate a Workspace or Project.
- Implement Runtime, Engine, SDK, or Plugin.
- Migrate APES.
- Perform git operations.

### §20.4 Closing Statement

This RFC is **approved**. Per Architect Decision, 2026-08-03, Part A, the disposition is **Approved with Notes** with three non-blocking Notes (N-1 status-consistency wording reconciliation; N-2 Constitution version-sequence discrepancy remains out of scope; N-3 patch implementation cycle is recorded separately). The Foundation Change Principle text in §4.1 is binding Foundation governance **upon ratification of the implementing FD (FD-0002)**; the RFC's approval alone is not yet binding. The Foundation remains Frozen except for changes authorized through approved RFCs (per `FOUNDATION/README.md` Current Status and per the Foundation Freeze State established by Architect Authorization, 2026-08-03).

---

## §21. Change Log

| Date | Actor | Change |
|---|---|---|
| 2026-08-03 | Foundation Builder (per Architect Authorization, 2026-08-03, Part B) | Initial authoring. Status: `Proposed`. |
| 2026-08-03 | Foundation Builder (per Architect Revision Cycle 01, 2026-08-03) | Status corrected to `Draft` per Architect disposition `Revision Required`. Added normative definition of Triggered Validation Cycle (§5.3.1). Added normative clarification of Emergency Handling (§10.9). Added normative Artifact Exclusions (§9.1). Five-clause Principle text (§4.1) preserved verbatim. Audit finding F-1 recorded as Resolved. |
| 2026-08-03 | Human Architect (per Architect Decision, 2026-08-03, Part A) | Status transitioned from `Draft` to `Approved`. Disposition: Approved with Notes. Three non-blocking Notes recorded (N-1 status-consistency wording; N-2 Constitution version-sequence out of scope; N-3 patch cycle authorized separately). Implementing FD (FD-0002) authorized separately per Architect Decision, Part B. |

---

*End of FRFC-0001-foundation-change-principle.md v0.1.0-draft (Draft).*