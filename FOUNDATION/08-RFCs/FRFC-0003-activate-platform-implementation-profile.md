# Research-OS — Foundation RFC 0003 — Activate the Platform Implementation Profile

**Status:** Draft
**Version:** 0.2.0-draft
**Foundation Version:** 1.0.0-rc.1
**Path:** `FOUNDATION/08-RFCs/FRFC-0003-activate-platform-implementation-profile.md`
**Supersedes:** none
**Related:** [Validation 04 Report](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md),
[Validation 04 Builder Self-Audit](../../VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-04.md),
[Validation 04 Pending Review](../../VALIDATION/06-Validation-Review/REVIEW-VALIDATION-04.md),
[FRFC-0003 Builder Self-Audit](../04-Audits/AUDIT-FRFC-0003-activate-platform-implementation-profile.md),
[FRFC-0003 Builder Report](../06-Reports/REPORT-FRFC-0003-activate-platform-implementation-profile.md),
[FRFC-0003 Pending Review](../07-Reviews/REVIEW-FRFC-0003-activate-platform-implementation-profile.md),
[Directory Standard](../03-Standards/directory-standard.md),
[Change-Control Policy](../02-Governance/change-control-policy.md),
[FD-0002](../09-Decisions/FD-0002-adopt-foundation-change-principle.md),
[FD-0003](../09-Decisions/FD-0003-approve-foundation-baseline.md),
[Implementation Plan](../../IMPLEMENTATION-PLAN.md)
**ID:** FRFC-0003-activate-platform-implementation-profile
**Title:** Activate the Platform Implementation Profile
**Date:** 2026-08-05
**Author:** Research-OS Foundation Builder (Builder role)
**Related Constitution Version:** 0.1.0-draft (Ratified via FD-0001, 2026-08-03)
**Superseded By:** none
**Decision Scope:** Name and govern only `FOUNDATION/11-Runtime/`; prefixes
`12`–`15` remain unchanged, unclaimed, and absent. The existing FD-0004-authorized
`16-Releases` path is historical reconciliation only and is not a new activation
scope of FRFC-0003.
**Affected Artifacts:** [Directory Standard](../03-Standards/directory-standard.md),
[Foundation README](../README.md), and [CHANGELOG](../../CHANGELOG.md); future
`FOUNDATION/11-Runtime/` creation remains separately gated.
**Migration Plan:** Additive and backward compatible; no existing path moves, no data
migration, and no consumer migration are required.
**Last Transition:** Remained Draft and narrowed from five proposed paths to only
`11-Runtime` after Builder adversarial self-Audit, 2026-08-05.
**Trigger:** Human instruction to execute the revised technical plan authorized Draft
preparation only. Validation Cycle 04 was then opened after self-Audit found the earlier
five-path evidence insufficient. Neither instruction is approval of this RFC.

---

## 0. Governance Hold

Validation Cycle 04 has not received an independent Audit or human Review disposition.
The FRFC self-Audit remains `FAIL`. This Draft must not transition to Submitted, In
Review, or Approved and must not be used to create FD-0006, patch the Foundation,
create a directory, add an ADR/dependency, or write implementation code.

## 1. Summary

This RFC proposes the smallest governed transition from the published docs-first
Foundation RC to an executable implementation: assign the exact canonical path
`FOUNDATION/11-Runtime/` to reserved prefix `11-`, preserve its existing Builder
Runtime and Engines meaning, and define the gates for a later offline Pack Validator
work unit. The legal post-RC work-unit mechanism remains an explicit Human Architect
question because Constitution Tasks 01–12 are closed. Prefixes `12`–`15` remain exactly as they are today: generic, unclaimed, and
absent. Approval of this RFC would permit preparation of a separate implementing FD;
it would not itself patch the Directory Standard or authorize code.

## 2. Motivation

[Validation Cycle 01](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-01.md)
established that Pack and Runtime behavior are defined at the contract level while
concrete Runtime execution remains unimplemented. It did not determine the directory
scope of that implementation and did not justify naming five top-level areas.

[Validation Cycle 04](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md)
was therefore opened to evaluate the exact post-RC gap. Its provisional finding is
that the smallest useful work product is an offline Pack Validator and that only
`FOUNDATION/11-Runtime/` is required. SDK, Plugin, Workspace, and standalone executable
Quality Gate products are not needed for that slice.

The Directory Standard reserves prefix `11-` for Builder Runtime / Engines but does not
name `FOUNDATION/11-Runtime/`. Its stricter path rules require the exact path to appear
in the Standard and Foundation README before lawfully authorized post-RC work may place
artifacts there. Creating code in a root `src/`, governance directory, or unnamed reserved path
would be non-compliant.

## 3. Validation Evidence and Current Limitation

The proposed scope is based on:

1. [Validation 04 Report §§3–5](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md),
   which compares one-path and five-path activation, assesses Foundation relevance,
   and provisionally recommends only `11-Runtime`.
2. [Validation 04 Builder Self-Audit](../../VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-04.md),
   which is Draft/FAIL because no independent Auditor has certified the evidence.
3. [Validation 04 Pending Review](../../VALIDATION/06-Validation-Review/REVIEW-VALIDATION-04.md),
   which carries no date, signature, or disposition.
4. [Validation 01 Report §§4.1, 4.4, 9, and 10](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-01.md),
   supporting only the underlying concrete Runtime implementation gap.
5. [Foundation Baseline Report](../06-Reports/REPORT-FOUNDATION-BASELINE-01.md),
   confirming the earlier Validation cycle's historical disposition.

Because Validation 04 is not yet accepted, these materials support Draft design work
only. They do not yet satisfy the binding Step-1 gate for RFC submission.

## 4. Scope

### 4.1 In Scope

- claim only the exact canonical path `FOUNDATION/11-Runtime/`;
- preserve the prefix's Builder Runtime and Engines purpose;
- classify and pin the exact additive Directory Standard / README / CHANGELOG patch;
- distinguish path naming from authorization to create a directory or content;
- define the first later implementation capability as an offline Pack Validator only,
  without inventing its still-unresolved post-RC work-unit mechanism;
- require an F-ADR before implementation dependencies appear;
- define compatibility, rollout, rollback, security, evidence, and human gates.

### 4.2 Out of Scope

- naming or claiming prefixes `12-`, `13-`, `14-`, or `15-`;
- changing any Constitution, Pack, Runtime, Engine, SDK, Plugin, Workspace, Quality
  Gate, Schema, Release, or Governance semantic contract;
- creating FD-0006, an ADR, `FOUNDATION/11-Runtime/`, source, tests, dependencies,
  lock files, workflows, databases, containers, or APIs in this cycle;
- model or network calls, Runtime execution, a real Pack or Workspace;
- `PROJECTS/`, APES, private/project data, Sprint work, or migration;
- changing `FOUNDATION/VERSION`, the published tag, the Pre-release, or RC contents.

## 5. Detailed Proposal

### 5.1 Canonical Path Assignment

After this RFC is independently audited, human-reviewed, approved by a distinct Human
Architect, and implemented by a separately Ratified FD and controlled patch, prefix
`11-` will have the canonical path:

| Prefix | Canonical Path | Preserved Purpose | State After Path Patch |
|---|---|---|---|
| `11-` | `FOUNDATION/11-Runtime/` | Concrete Builder Runtime and Engine implementation artifacts | Named but absent/reserved; no content until the post-RC work-unit mechanism and an equivalent §15.5 scope are human-approved |

Prefixes `12-` through `15-` remain unchanged in the Directory Standard. This RFC
does not assign them exact names, create them on disk, or authorize placeholder files.

### 5.2 Naming Is Not Activation

The controlled path patch establishes a canonical address only. The directory must
remain absent until all of the following are complete:

1. Validation 04 is accepted by a human disposition.
2. FRFC-0003 receives an independent Audit, independent Human Review, and Human
   Architect approval, with all roles separated.
3. A separate implementing FD is Ratified.
4. The exact Standard/README/CHANGELOG patch is applied, audited, reported, and
   human-reviewed.
5. An F-ADR records implementation choices and is accepted under the applicable
   authority.
6. The Human Architect resolves the lawful post-RC governed-work-unit mechanism, and a
   separate work unit declares a scope at least equivalent to Constitution §15.5 and is
   explicitly authorized.

No instruction to “continue,” no GitHub Draft PR, and no path name silently satisfies
one of these gates.

### 5.3 First Implementation Capability (Work-Unit Mechanism Unresolved)

The first work unit, if its governance mechanism is separately resolved and later
authorized, is limited to an offline deterministic Pack Validator that:

- safely parses canonical source artifacts and declared structured metadata as
  untrusted data without executing content;
- maps Pack, Mission, Program, Task, Deliverable, Evidence, Manifest, Audit, Review,
  and Report semantics into strongly validated intermediate models;
- validates paths, IDs, versions, dependencies, states, permissions, stop conditions,
  and cross-references with stable error identifiers;
- emits deterministic machine-readable validation and integrity results;
- exposes a local/offline validation interface; and
- includes valid/invalid fixtures and unit, property, integration, and security tests.

The work unit must not call a model, access the network, run Pack instructions, provision a
Workspace, load a Plugin, mutate inputs, access Project/APES data, or perform external
Git/publication actions. Its fixtures and executable conformance rules remain inside
the authorized Runtime work tree; no `15-` path is needed.

### 5.4 Technology Choice Boundary

Python, `uv`, Pydantic, Typer, Markdown/YAML, JSON, SHA-256, a concrete CLI name,
FastAPI, PostgreSQL, and LangGraph remain non-normative implementation options. A later
F-ADR must select formats, integrity algorithm, command surface, and only the
dependencies actually needed for the authorized slice; it must also record licenses,
supported versions, lock-file/reproducibility policy, and Domain Kernel adapter
boundaries. The first offline slice does not require FastAPI, PostgreSQL, or LangGraph.

### 5.5 Exact Governance Sequence

```text
Validation 04 independent Audit + human Review/Architect disposition
→ FRFC-0003 independent Audit + Human Review + Human Architect approval
→ FD-0006 Pending package + Human Ratification
→ exact Directory Standard / Foundation README / CHANGELOG patch
→ patch Audit + Report + Human Review
→ F-ADR acceptance
→ Human Architect-approved post-RC work-unit mechanism
→ authorized offline Pack Validator work unit
→ implementation + tests + Audit + Report + Human Review
```

## 6. Proposed Normative Patch

This section pins the maximum patch that a future implementing FD may authorize. The
actual patch date and Ratified FD reference must be verified at application time.

### 6.1 Change Classification and Version

- **Classification:** provisionally Minor, backward-compatible additive Foundation
  change under Directory Standard §10.2 and Change-Control Policy §2.2.
- **Classification conflict to repair:** Directory Standard §11 currently says all
  “Path mutations are Major changes.” The patch below narrows that sentence so an
  additive reserved-prefix claim is Minor while rename/remove/split remain Major.
- **Directory Standard:** `0.1.0-draft` → `0.2.0-draft`.
- **Foundation Version field in patched Standard:** `1.0.0-rc.1`.
- **Foundation platform version:** unchanged by this patch; no release is declared.
- **Migration:** provisionally none; no existing path is renamed, removed, or
  invalidated. The Human Architect must confirm the classification conflict before the
  patch is eligible for authorization.

### 6.2 Directory Standard Identity and Stale-State Reconciliation

The implementing patch must replace the common header with the following verified
values, append FRFC-0003 / FD-0002 / FD-0003 / the Ratified implementing FD as
resolvable `Related` links, and use the actual application date:

```md
**Status:** Draft / In Review
**Version:** 0.2.0-draft
**Foundation Version:** 1.0.0-rc.1
**Path:** `FOUNDATION/03-Standards/directory-standard.md`
**Supersedes:** none
**Related:** [Constitution](../01-Constitution/constitution.md),
[Governance Model](../02-Governance/governance-model.md),
[Roles and Authority](../02-Governance/roles-and-authority.md),
[Change-Control Policy](../02-Governance/change-control-policy.md),
[Approval Workflow](../02-Governance/approval-workflow.md),
[Disagreement and Escalation](../02-Governance/disagreement-and-escalation.md),
[RFC Policy](../08-RFCs/rfc-policy.md),
[Foundation Decision Policy](../09-Decisions/foundation-decision-policy.md),
[ADR Policy](../10-ADRs/adr-policy.md),
[FRFC-0003](../08-RFCs/FRFC-0003-activate-platform-implementation-profile.md),
[FD-0002](../09-Decisions/FD-0002-adopt-foundation-change-principle.md),
[FD-0003](../09-Decisions/FD-0003-approve-foundation-baseline.md),
[FD-0006](../09-Decisions/FD-0006-activate-platform-implementation-profile.md)
**Last Transition:** Additive `FOUNDATION/11-Runtime/` path assignment applied under
FRFC-0003 and the Ratified implementing FD, <actual-date>.
```

Replace Directory Standard §2's first paragraph with:

```md
This Directory Standard is **Draft / In Review** at version `0.2.0-draft`, Foundation `1.0.0-rc.1`, and Constitution `0.1.0-draft` (Ratified by FD-0001). Binding amended-baseline authority for this exact Standard version derives from the Ratified implementing FD that approves FRFC-0003 and the controlled patch. It remains the L3 Foundation Standard that operationalizes Constitution §9 (Naming Convention) for directory paths specifically.
```

In §3.2 replace the `FOUNDATION/VERSION` row with:

```md
| `FOUNDATION/VERSION` | Foundation version file (currently `1.0.0-rc.1`). | Task 01; last changed by the applied RC decision |
```

In §10.1 replace all three Version Surfaces bullets with:

```md
- **This Standard's version.** Header `Version: 0.2.0-draft`. Bump rules per Constitution §8.
- **Foundation version.** `FOUNDATION/VERSION` (currently `1.0.0-rc.1`).
- **Constitution version.** `constitution.md` header (currently `0.1.0-draft`, Ratified by FD-0001).
```

Replace Directory Standard §12 with:

```md
## 12. Ratification and Binding Authority

This Directory Standard remains **Draft / In Review** at document version `0.2.0-draft`. Binding amended-baseline authority for this exact version derives from the Ratified implementing FD that approves FRFC-0003 and this controlled patch. The document-level Draft / In Review status remains distinct from FD-derived binding authority.

The Constitution is Ratified by FD-0001, the Foundation Change Principle is binding through FD-0002, and the prior Directory Standard exact version was part of the baseline approved by FD-0003. The Task 03 text deferring a hypothetical standalone `FD-0003-ratify-directory-standard.md` is historical and does not negate the later Ratified implementing FD for this exact amendment.

Any later amendment or supersession must follow the Foundation Change Principle and state the exact affected version, compatibility impact, and binding authority.
```

Replace the footer with:

```md
*End of Directory Standard v0.2.0-draft.*
```

### 6.3 Directory Standard §3.2 Rows

Append these exact rows after `FOUNDATION/10-ADRs/` and before
`FOUNDATION/VERSION`. The `16-Releases` row reconciles an existing FD-0004-authorized
path; it is not a new claim by FRFC-0003:

```md
| `FOUNDATION/11-Runtime/` | Canonical top-level path for concrete Builder Runtime and Engine implementation artifacts. The path is named but absent until a separately governed and explicitly authorized post-RC work unit creates its first real artifact. | Future work unit after its post-RC governance mechanism and scope are human-approved |
| `FOUNDATION/16-Releases/` | Canonical top-level path for Foundation Release instances and release evidence. | Release Specification; Ratified FD-0004 §11; existing path reconciliation only |
```

### 6.4 Directory Standard §5.1 Row

Replace the current `11-` and `16-` rows with:

```md
| `11-` | Runtime and Engines (`FOUNDATION/11-Runtime/`; named but absent) | Constitution §15 Tasks 06 and 08; Runtime and Engine Specifications; FRFC-0003 | Reserved until a separately governed and explicitly authorized post-RC work unit |
| `16-` | Releases (`FOUNDATION/16-Releases/`; existing active path) | Release Specification; Ratified FD-0004 §11 | FD-0004 Stage A creation; reconciled into this Standard by the implementing FD |
```

Rows `12-` through `15-` are otherwise unchanged.

In §5.2 replace the `Density` bullet with:

```md
- **Density.** Prefixes need not be contiguous; gaps are permitted. `05-Statistics/` and prefixes `12-`–`15-` remain reserved and empty. Prefix `11-` is canonically named but remains absent; prefix `16-` is the existing active `FOUNDATION/16-Releases/` path authorized by FD-0004.
```

### 6.5 Directory Standard §6 Rows

Replace §6's opening paragraph, the existing broad `FOUNDATION/11-` to
`FOUNDATION/16-` row, and the paragraph after the table with the following exact text:

```md
The table distinguishes named-but-absent or generically reserved paths from an existing active path. A named or generically reserved path MUST remain absent and MUST contain no artifact until the applicable governance and work-unit authority are complete. An existing active path remains governed by its recorded authorizing decision.

| `FOUNDATION/11-Runtime/` | Concrete Builder Runtime and Engine implementation artifacts. Canonically named but absent/reserved; no artifact is permitted until the implementing FD patch gate, the post-RC work-unit governance mechanism, and an approved scope at least equivalent to Constitution §15.5 are complete. |
| `FOUNDATION/12-` to `FOUNDATION/15-` | Future Foundation scope groups remain generically reserved under §5.1 and are not named or activated by FRFC-0003. |
| `FOUNDATION/16-Releases/` | Existing Foundation Release instances and release evidence authorized by FD-0004. This row reconciles existing history and is not a new activation by FRFC-0003. |

`FOUNDATION/11-Runtime/` MUST NOT be created early or anchored by a placeholder file. Prefixes `12-`–`15-` remain absent until separately governed. `FOUNDATION/16-Releases/` is already active under FD-0004 and is not altered by this section.
```

This RFC does not alter or reinterpret any pre-existing `16-Releases` artifact,
decision, lifecycle, or publication authority; the exact row only makes the Directory
Standard agree with the already-authorized on-disk state.

### 6.6 Directory Standard §7.1 Replacements and Addition

Replace item 1 with:

```md
1. An unused numbered prefix assigned per §5, or a reserved prefix claimed under §5.2 by the applicable approved governance.
```

Replace item 2 with:

```md
2. A Foundation Task authorized under Constitution §15, or a post-RC governed work unit whose legal mechanism, authority, and scope have been separately approved by the Human Architect through the applicable Foundation governance process.
```

Append:

```md
For `FOUNDATION/11-Runtime/`, appearance in §3.2 and §5.1 assigns a canonical path only. It does not create the directory or authorize content. The path MUST remain absent until (a) the implementing FD is Ratified, (b) the authorized Directory Standard / Foundation README patch passes Audit and human Review, and (c) the Human Architect has separately approved a lawful post-RC governed-work-unit mechanism whose Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, and Stop Condition are at least equivalent to Constitution §15.5.
```

### 6.7 Foundation README Layout Row

Append after `10-ADRs/`:

```md
| `11-Runtime/` | Canonical path for concrete Builder Runtime and Engine implementation artifacts. Named/reserved; absent until a separately governed post-RC work unit and an equivalent §15.5 scope are human-approved. |
| `16-Releases/` | Existing canonical path for Foundation Release instances and release evidence, authorized by Ratified FD-0004. |
```

The README must state that prefixes 12–15 remain generically reserved and unclaimed,
and that the `16-Releases` line is an existing-state reconciliation rather than scope
newly granted by FRFC-0003.

### 6.8 Directory Standard §11 Classification Repair

In §9.1 replace the Change-Control Policy cross-reference line with:

```md
- `FOUNDATION/02-Governance/change-control-policy.md` — change categories (an additive reserved-prefix claim follows §10.2 and Change-Control Policy §2.2; breaking rename, removal, or split operations are Major path mutations).
```

Replace the current Change-Control Policy relationship bullet with:

```md
- **Change-Control Policy.** Claiming an already reserved prefix by adding a new backward-compatible top-level path is a Minor additive change under §10.2 and Change-Control Policy §2.2. Renaming, removing, splitting, or otherwise invalidating an existing path is a Major change and requires the applicable migration controls.
```

### 6.9 Versioned CHANGELOG Entry

The future patch must add:

```md
## [Directory Standard v0.2.0-draft] — <actual-date>

### Added
- Assigned the canonical `FOUNDATION/11-Runtime/` path for future concrete Builder Runtime and Engine implementation artifacts under FRFC-0003 and the Ratified implementing FD.

### Changed
- Reconciled the Directory Standard header, §2, §3.2, §5.1, §5.2, §6, §7.1, §9.1, §10.1, §11, §12, footer, and matching Foundation README Layout entries for version `0.2.0-draft`; path naming remains distinct from directory/content authorization.
- Recorded the already-authorized `FOUNDATION/16-Releases/` path without changing its artifacts, lifecycle, or publication authority.
- Clarified that claiming a reserved prefix additively is Minor while rename/remove/split operations remain Major, subject to the Human Architect's approved classification.
- Required a separately approved post-RC governed-work-unit mechanism and scope before any implementation artifact may create `FOUNDATION/11-Runtime/`.

### Notes
- Prefixes `12`–`15` remain unchanged, generically reserved, unclaimed, and absent. No Runtime code, Pack, Project, APES, Foundation version, tag, or Release change is included.
```

## 7. Affected Artifacts

| Artifact | Current State | Maximum Future Effect |
|---|---|---|
| [Directory Standard](../03-Standards/directory-standard.md) | `0.1.0-draft`; `11-` generic reserved | `0.2.0-draft`; exact `11-Runtime` path and activation guard |
| [Foundation README](../README.md) | Layout ends at `10-ADRs/` although `16-Releases` already exists under FD-0004 | Add the named/reserved/absent `11-Runtime` row and reconcile the existing `16-Releases` row |
| [CHANGELOG](../../CHANGELOG.md) | No Directory Standard v0.2.0 entry | Add exact versioned entry after future patch |
| `FOUNDATION/11-Runtime/` | Does not exist | Created only by a later governed work unit after its legal mechanism and scope are human-approved, not by the RFC/FD patch |
| Prefixes `12`–`15` | Generic reserved | Unchanged and unclaimed |
| `FOUNDATION/VERSION` | `1.0.0-rc.1` | Unchanged |

## 8. Compatibility and Migration

The change is additive: no existing path, identifier, artifact, or cross-reference is
invalidated. Existing consumers that ignore unknown future directories continue to
work. No migration plan or deprecation window is required. Any future move, split, or
removal of `11-Runtime` would be a separate breaking change with its own governance.

The published `v1.0.0-rc.1` tag remains immutable. Main-branch post-RC work must not be
described as part of the tagged RC; any later release decision is separate.

## 9. Security and Isolation

- Inputs are untrusted data, never executable instructions.
- Any structured-metadata parser must use a safe non-object-constructing mode; YAML is
  only a non-binding candidate.
- Path resolution must reject traversal, absolute escape, and symlink escape.
- The serialization and integrity mechanism selected by the future F-ADR must produce
  deterministic results across its declared supported platforms.
- Secrets must not enter source, fixtures, events, logs, reports, or exceptions.
- The first implementation work unit is offline: no model, network, plugin, database,
  or external side effect.
- No Project/APES path, data, credential, lifecycle, or governance may enter the
  Foundation implementation.
- Builder, Auditor, Reviewer, and Architect duties remain role-separated.

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Path name is treated as code authority | Medium | High | Separate FD, patch Review, ADR, governed work-unit authorization, and implementation Review |
| Runtime slice grows into orchestration | Medium | High | Exact offline-validator behavior and prohibitions |
| Prefixes 12–15 are populated early | Medium | High | They remain unnamed/unclaimed; no placeholders |
| Technology becomes normative | Medium | High | F-ADR plus Domain Kernel/adapter boundary |
| Unsafe input escapes scope | Medium | High | Safe loader, bounded resolver, adversarial tests |
| Draft/self-Audit is mistaken for approval | Medium | High | Current FAIL verdict and explicit governance hold |

## 11. Acceptance Criteria

FRFC-0003 may be submitted only when:

1. Validation 04 receives an independent Audit and human Review/Architect disposition
   accepting its Step-1 evidence;
2. an independent Auditor confirms the revised FRFC package;
3. the unresolved non-Task Report `Task-ID` / scope-schema question receives explicit
   Human Architect disposition or a compliant record form;
4. the Human Architect approves a lawful post-RC work-unit mechanism and its minimum
   scope schema, or explicitly removes implementation authorization from this RFC;
5. the Human Architect confirms the Minor/Major classification reconciliation;
6. all Markdown references resolve and the exact patch remains internally consistent;
7. no `11-*`–`15-*` directory, FD, ADR, dependency, code, Pack, Project, or APES
   artifact has been created by the proposal cycle.

Approval requires a Human Reviewer and a distinct Human Architect after submission.
Approval satisfies only FCP Step 3; all later gates remain separate.

## 12. Rollout and Rollback

Rollout follows §5.5 without compression. Before a Standard patch, withdrawal has no
path or data effect. After a path-only patch but before implementation, a superseding
FD may revert only the named path/README/CHANGELOG metadata while preserving governance
evidence. After implementation begins, any rollback requires a separate decision that
preserves Audit/Report/Review evidence and explicitly disposes of implementation
artifacts. No destructive rollback is implicit.

## 13. Drawbacks

- The governance path is longer than creating a Python package immediately.
- One more Validation and multiple role-separated reviews add coordination cost.
- Keeping Phase 1 offline delays orchestration and a visible multi-agent demo.

These costs keep the first executable slice measurable, reversible, and within the
evidence actually available.

## 14. Alternatives Considered

1. **Name 11–15 now.** Rejected: current evidence supports only Runtime validation;
   four names would be unused architectural expansion.
2. **Use a root `src/`.** Rejected: not authorized by the current Directory Standard.
3. **Place code under `10-ADRs` or `03-Standards`.** Rejected: wrong artifact purpose.
4. **Use an ADR without FRFC.** Rejected: an ADR cannot amend a Foundation path rule.
5. **Start a real Pack or APES pilot first.** Rejected: no validator or Project authority.
6. **Build full Runtime/LangGraph first.** Rejected: unnecessarily expands side effects
   before deterministic artifact validation is proven.

## 15. Open Questions

Three architecture/process questions remain and may not be answered by the Builder:

1. What governed work-unit mechanism replaces or extends the closed Constitution Tasks
   01–12 for post-RC implementation, and what schema makes its authority resolvable?
2. How must this non-Task FRFC Builder Report satisfy or be exempted from the Report
   Schema's Task-ID hook?
3. Does the Human Architect confirm that claiming a reserved prefix additively is Minor
   after the proposed §11 reconciliation, or require a Major/migration route instead?

## 16. References

- [Constitution](../01-Constitution/constitution.md)
- [Directory Standard](../03-Standards/directory-standard.md)
- [Schema Standard](../03-Standards/schema-standard.md)
- [Change-Control Policy](../02-Governance/change-control-policy.md)
- [Roles and Authority](../02-Governance/roles-and-authority.md)
- [Approval Workflow](../02-Governance/approval-workflow.md)
- [RFC Policy](rfc-policy.md)
- [FD-0002 — Foundation Change Principle](../09-Decisions/FD-0002-adopt-foundation-change-principle.md)
- [FD-0003 — exact-version Foundation baseline](../09-Decisions/FD-0003-approve-foundation-baseline.md)
- [FD-0004 — existing `16-Releases` authorization](../09-Decisions/FD-0004-authorize-foundation-rc-1.md)
- [Validation Cycle 04 package](../../VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md)
- [Implementation Plan](../../IMPLEMENTATION-PLAN.md) — non-normative

## 17. Change Log

| Version | Date | Change |
|---|---|---|
| `0.1.0-draft` | 2026-08-05 | Initial Draft proposed naming prefixes 11–15 and used Validation 01 as Step-1 evidence. |
| `0.2.0-draft` | 2026-08-05 | Remained Draft; opened Validation 04; narrowed scope to only `11-Runtime`; expanded the proposed patch across header/§2/§3.2/§5.1/§5.2/§6/§7.1/§9.1/§10.1/§11/§12/footer/README/CHANGELOG; reconciled existing `16-Releases` history without granting new scope; made formats and hash/CLI choices non-binding; recorded post-RC work-unit, Report Schema, classification, and role-separation blockers. |

## 18. Decision Status

**Status: Draft. Process: blocked by open Major findings.** No approval, FD, path, ADR,
implementation, Pack, Project, APES, or release authority exists. The Builder stops at
the failed self-Audit and Pending Validation/FRFC Review gates.

---

*End of FRFC-0003 — Activate the Platform Implementation Profile — v0.2.0-draft.*
