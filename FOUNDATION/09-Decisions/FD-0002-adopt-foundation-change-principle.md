# FD-0002 — Adopt the Foundation Change Principle (per FRFC-0001)

**ID:** FD-0002
**Title:** Adopt the Foundation Change Principle as binding Foundation governance
**Status:** Ratified
**Version:** 0.1.0-draft
**Date:** 2026-08-03
**Owner:** Architect
**Approver:** Human Architect — Role-based approval (no personal name, signature, or identity data; per Architect Decision, 2026-08-03, Part B)
**Related Constitution Version:** v0.1.0-draft (Ratified by FD-0001)
**Related RFC:** FRFC-0001-foundation-change-principle (Approved per Architect Decision, 2026-08-03, Part A)
**Supersedes:** none
**Superseded By:** none
**Dependencies:** FD-0001 (Constitution ratification); FRFC-0001 (Approved); Foundation Task 02 (Governance); `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/02-Governance/governance-model.md`; `FOUNDATION/02-Governance/change-control-policy.md`.
**Decision Scope:** Adoption of a normative Foundation Change Principle; patching of existing Governance Model and Change Control Policy to make the Principle operational.
**Last Transition:** Builder (Patch Cycle 01) → `Pending Ratification`, 2026-08-03; Human Architect → `Ratified`, 2026-08-03 (per Architect Decision, 2026-08-03, Part B).

---

## §1. Context

Research-OS Foundation FRFC-0001 — Foundation Change Principle was Approved on 2026-08-03 per Architect Decision, Part A (Disposition: Approved with Notes). The Principle text (FRFC-0001 §4.1) is:

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

Per FRFC-0001 §10 Step 6 and per `approval-workflow.md`, RFC approval alone is not binding; the Principle becomes Foundation governance only upon the ratification of an implementing FD. This FD fulfills that role. This FD is the separately and explicitly authorized implementing FD permitted by Architect Decision, 2026-08-03, Part B.

## §2. Decision

**The Architect adopts the Foundation Change Principle (FRFC-0001 §4.1) as binding Foundation governance of Research-OS Foundation, effective upon the Architect's approval of this FD.**

Upon adoption:

- The Foundation Change Principle is binding on all future Foundation work.
- The existing `FOUNDATION/02-Governance/governance-model.md` and `FOUNDATION/02-Governance/change-control-policy.md` are patched to make the Principle operational.
- The patched governance artifacts cross-reference this FD.
- `CHANGELOG.md` records the adoption with date and FD reference.
- No new Foundation Standard or Policy is created.
- No Foundation artifact outside `FOUNDATION/02-Governance/governance-model.md` and `FOUNDATION/02-Governance/change-control-policy.md` is modified by this FD.
- The Foundation Constitution is not amended by this FD.
- `FOUNDATION/VERSION` is unchanged.

## §3. Binding Principle Text (Verbatim)

The Foundation Change Principle, as adopted by this FD, reads (verbatim, per FRFC-0001 §4.1):

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

## §4. Binding Clarifications

The following clarifications are adopted together with the Principle text and are equally binding:

### §4.1 Triggered Validation

A Validation Cycle may be triggered by any of the following (per FRFC-0001 §5.3.1):

1. Scheduled cadence.
2. Project-triggered.
3. Implementation-triggered.
4. Audit-triggered.
5. Incident-triggered.
6. Security-triggered.
7. Compatibility-triggered.
8. Externally triggered (material legal, dependency, platform, or operational change).

A trigger alone does not authorize a Foundation patch. The triggered Validation Cycle must still record the observed gap, capture evidence, determine Foundation relevance, and recommend whether an RFC is necessary.

### §4.2 Emergency Handling

Emergency conditions do not bypass evidence, review, or human authority. The process may use an expedited Validation and RFC review but must still produce (per FRFC-0001 §10.9):

1. Evidence.
2. RFC or emergency change record (as permitted by existing governance).
3. Human approval.
4. Patch audit.
5. Retrospective review.

No new emergency governance artifact class is created by this FD. If current governance does not support an emergency record, the expedited application uses the existing `EMERGENCY-FD-NNNN-<slug>.md` mechanism only.

### §4.3 Non-Architectural Maintenance Exclusions

The following records do not count as Foundation architectural expansion when they are required by an existing authorized process and introduce no new authority or architecture (per FRFC-0001 §9.1):

- E-1: RFC proposal records.
- E-2: Audit records.
- E-3: Report records.
- E-4: Review records.
- E-5: Evidence records.
- E-6: Authorized correction records.
- E-7: Status reconciliation records.

These exclusions apply only when the records do not change Foundation meaning, authority, scope, behavior, architecture, compatibility, permissions, or lifecycle. The standing scope, naming, and approval controls of `governance-model.md`, `change-control-policy.md`, `rfc-policy.md`, `schema-standard.md`, and `directory-standard.md` remain binding on all excluded records.

### §4.4 Repair-vs-Expansion Rule

A change that repairs, clarifies, or reconciles an existing Foundation artifact without altering its meaning, authority, scope, behavior, architecture, compatibility, permissions, or lifecycle is a **non-architectural maintenance** change and does not require an FRFC. A change that does any of those things is **Foundation expansion** and requires an FRFC and a Ratified FD.

A status-consistency wording reconciliation across a cycle (such as the reconciliation recorded for FRFC-0001 by Architect Decision, 2026-08-03, Part A Note N-1) is a permitted non-architectural maintenance change when it (a) does not alter the RFC substance, (b) does not introduce or remove any artifact, and (c) is documented in the audit trail of the cycle.

### §4.5 Rollback and Retrospective Review

Where a Foundation patch is applied under this Principle and is later found to introduce a defect or unintended consequence, the patch may be rolled back through a superseding FD. Every patch applied under this Principle requires a retrospective review no later than the next Foundation Validation Cycle.

## §5. Affected Artifacts (Patched by This FD)

This FD patches the following existing Foundation governance artifacts only:

1. `FOUNDATION/02-Governance/governance-model.md` — adds the Foundation Change Principle as a binding governance rule (§6.1, §6.2 below).
2. `FOUNDATION/02-Governance/change-control-policy.md` — adds operational workflow, triggered Validation definitions, non-architectural maintenance exclusions, expedited emergency handling, repair-vs-expansion rules, and rollback/retrospective review requirements.

No other artifact is modified by this FD.

## §6. Governance Model Patch (Required Content)

The patched `governance-model.md` must include, at minimum:

### §6.1 Foundation Change Principle as Binding Rule

A new section declaring the Foundation Change Principle (the verbatim text from §3 above) as a binding governance rule of the Research-OS Foundation, referencing FRFC-0001 and FD-0002.

### §6.2 Scope of the Principle

A new section stating that the Principle applies to all Foundation artifacts (Constitution, FDs, Standards, RFCs, ADRs, Engines, SDKs, Plugins, Workspaces, Builder Packs, Releases) and to all Foundation roles.

### §6.3 Validation, RFC, and Patch Workflow

A new section declaring that the operational workflow for the Principle is governed by `change-control-policy.md` (as patched by this FD).

### §6.4 Reference to FD-0002

The new sections cross-reference `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` as the source of binding authority.

## §7. Change Control Policy Patch (Required Content)

The patched `change-control-policy.md` must include, at minimum:

### §7.1 Operational Workflow

A normative workflow diagram that codifies the five-step Foundation Change Principle:

```
┌─────────────────────────┐
│  1. Validation Cycle    │
│  (gap discovered +      │
│   evidence captured)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. RFC Proposed        │
│  (FRFC/PRFC/RRFC per    │
│   rfc-policy.md)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. RFC Reviewed +      │
│     Approved            │
│  (Human Architect +     │
│   Reviewer)             │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  4. Implementing FD     │
│     Ratified            │
│  (per foundation-       │
│   decision-policy.md)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. Foundation Patched  │
│     Through Approved    │
│     Governance Process  │
│  (existing artifacts    │
│   only; Audit +         │
│   Report + Review)      │
└─────────────────────────┘
```

### §7.2 Triggered Validation Definitions

A normative list of the eight Triggered Validation Cycle triggers (per §4.1 above).

### §7.3 Non-Architectural Maintenance Exclusions

A normative enumeration of the seven excluded record classes (per §4.3 above) and the conditions under which exclusion applies.

### §7.4 Expedited Emergency Handling

A normative enumeration of the five-step expedited emergency application requirements (per §4.2 above), with explicit statement that no new emergency governance artifact class is created.

### §7.5 Repair-vs-Expansion Rules

A normative statement of the distinction between non-architectural maintenance (no FRFC required) and Foundation expansion (FRFC + Ratified FD required), including the status-consistency wording reconciliation rule (per §4.4 above).

### §7.6 Rollback and Retrospective Review

A normative statement that a patch applied under the Principle may be rolled back through a superseding FD and that every patch requires a retrospective review no later than the next Foundation Validation Cycle.

### §7.7 Reference to FD-0002

The new sections cross-reference `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` as the source of binding authority.

## §8. Constitution Boundary

This FD does **not** amend the Constitution. The Constitution at `FOUNDATION/01-Constitution/constitution.md` (version v0.1.0-draft, Ratified by FD-0001) is not modified by this FD. Any future amendment to the Constitution requires a separate FD that declares `amends-constitution: true` (Constitution §17.2), carries a MAJOR version bump, includes a Migration Plan, and is approved by the Architect through the constitutional amendment workflow.

## §9. Other Hard Prohibitions

The following actions are prohibited by this FD and remain prohibited under the adopted Principle:

1. Create a new Foundation Standard.
2. Create a new Foundation Policy.
3. Create a new FD other than this FD (and any future FD explicitly authorized by a separate Architect instruction).
4. Change `FOUNDATION/VERSION`.
5. Declare an RC.
6. Create or execute a Pack.
7. Instantiate a Workspace or Project.
8. Implement Runtime, Engine, SDK, or Plugin.
9. Migrate APES.
10. Perform git operations.
11. Fabricate a personal name, signature, email address, or other identity data.

## §10. Quality Gates

This FD satisfies the following Quality Gates:

1. **Completeness.** This FD carries all required FD sections: Context, Decision, Binding Principle, Binding Clarifications, Affected Artifacts, Governance Model Patch requirements, Change Control Policy Patch requirements, Constitution Boundary, Hard Prohibitions, Quality Gates, Current Status.
2. **Compliance.** The patched governance artifacts conform to Constitution §11, `schema-standard.md`, and `directory-standard.md`.
3. **Cross Reference.** All affected artifacts, the patched governance artifacts, the implementing FD, and FRFC-0001 are named and resolved.
4. **Isolation.** The Principle applies only to Foundation artifacts; no Project-specific governance, lifecycle, schema, or implementation rule is introduced.
5. **Scope Compliance.** Only the allowed artifacts (Governance Model, Change Control Policy) are patched.
6. **Security Boundary.** No new artifact class is introduced; no ratification scope is expanded; the human approval boundary is preserved.

## §11. Patch Review

The Patch Cycle 01 implementation is reviewed in `FOUNDATION/07-Reviews/REVIEW-FRFC-0001-implementation.md` (Disposition: Pending human Architect). Foundation returns to Freeze State after Patch Review approval.

## §12. Current Status

This FD is **Ratified** as of 2026-08-03. The Architect's disposition was issued as part of the Architect Decision "Approve FRFC-0001 and Authorize Foundation Patch Cycle 01" on 2026-08-03, Part B, with explicit directive to:

- Transition this FD from `Pending Ratification` to `Ratified`.
- Apply the patches specified in §5–§7 to the existing `FOUNDATION/02-Governance/governance-model.md` and `FOUNDATION/02-Governance/change-control-policy.md`.
- Update `CHANGELOG.md` and `FOUNDATION/README.md` to reflect the adoption.
- Create the three Patch Cycle 01 implementation records at the Architect-specified paths.

## §13. Change Log

| Date | Actor | Change |
|---|---|---|
| 2026-08-03 | Foundation Builder (per Architect Decision, 2026-08-03, Part B) | Initial authoring. Status: `Pending Ratification`. |
| 2026-08-03 | Human Architect (per Architect Decision, 2026-08-03, Part B) | Status transitioned to `Ratified`. |

---

*End of FD-0002 — Adopt the Foundation Change Principle (per FRFC-0001) v0.1.0-draft (Ratified, 2026-08-03).*