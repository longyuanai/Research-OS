# Research-OS — Validation Cycle 04 — Minimal Implementation Activation

**Status:** Draft
**Version:** 0.1.0-draft
**Foundation Version:** 1.0.0-rc.1
**Path:** `VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md`
**Supersedes:** none
**Related:** [FRFC-0003 Draft](../../FOUNDATION/08-RFCs/FRFC-0003-activate-platform-implementation-profile.md),
[FRFC-0003 self-Audit F-01](../../FOUNDATION/04-Audits/AUDIT-FRFC-0003-activate-platform-implementation-profile.md#f-01--validation-step-1-evidence-is-not-yet-accepted),
[Validation 04 Audit](../05-Validation-Audit/AUDIT-VALIDATION-04.md),
[Validation 04 Review](../06-Validation-Review/REVIEW-VALIDATION-04.md),
[Directory Standard](../../FOUNDATION/03-Standards/directory-standard.md),
[Runtime Specification](../../FOUNDATION/03-Standards/runtime-specification.md),
[Pack Standard](../../FOUNDATION/03-Standards/pack-standard.md),
[Change-Control Policy](../../FOUNDATION/02-Governance/change-control-policy.md),
[FD-0002](../../FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md),
[FD-0003](../../FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md),
[FD-0004](../../FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md),
[Implementation Plan](../../IMPLEMENTATION-PLAN.md)
**Constitution Version:** 0.1.0-draft (Ratified by FD-0001, 2026-08-03)
**Validation Cycle:** 04 (Triggered Validation Cycle — Implementation-triggered)
**Validator:** Research-OS Validation Builder (Builder role; read-only analysis)
**Report Date:** 2026-08-05
**Trigger:** A Builder adversarial self-audit of the Draft FRFC-0003 proposal found
that Validation Cycle 01 did not determine whether the implementation gap requires
claiming only `11-Runtime` or naming all reserved prefixes `11`–`15`.

---

> **Scope boundary.** This cycle is read-only with respect to Foundation normative
> artifacts. It records evidence and a provisional recommendation only. It does not
> approve or submit FRFC-0003, create or ratify an FD, patch a Standard, claim a path,
> add an ADR or dependency, create a Builder Pack, activate APES, or write Runtime code.

## 1. Executive Summary

The docs-first Foundation RC defines Pack and Runtime contracts but contains no
executable implementation. The smallest useful next work product is an offline Pack
Validator that safely reads and validates Foundation-compatible Pack artifacts and
emits deterministic, auditable integrity evidence without executing instructions,
calling a model, or accessing the network.

The current Directory Standard reserves prefix `11-` for future Builder Runtime /
Engines but does not assign the exact path `FOUNDATION/11-Runtime/`. It also requires a
new top-level Foundation path to be named in the Standard and the Foundation README
before artifacts may be placed there. Therefore the first implementation requires a
Foundation-level additive directory decision.

The same evidence does **not** establish an immediate need for concrete SDK, Plugin,
Workspace, or executable Quality Gate directories. Naming `12-SDKs` through
`15-Quality-Gates` now would create unused architectural surface and exceed the
validated implementation need.

**Provisional recommendation:** use a narrowed FRFC-0003 to claim only
`FOUNDATION/11-Runtime/`; leave prefixes `12`–`15` in their current generic reserved
state. The Directory Standard change is a backward-compatible **Minor** change to that
artifact, not a Constitution amendment. Technology choices remain in a later F-ADR.
This recommendation is not accepted Step-1 evidence until an independent Validation
Audit returns `PASS` or `PASS with Notes`, a Human Reviewer records `Approved` or
`Approved with Notes`, and a distinct Human Architect accepts the cycle for FCP Step 1.

## 2. Trigger and Scope Declaration

### 2.1 Trigger Classification

This is an **Implementation-triggered** cycle under
[Change-Control Policy §9 trigger 3](../../FOUNDATION/02-Governance/change-control-policy.md#9-triggered-validation-definitions).
The Builder observed a Foundation-relevant scope gap while preparing the explicitly
authorized [Draft FRFC-0003 scope](../../FOUNDATION/08-RFCs/FRFC-0003-activate-platform-implementation-profile.md#4-scope): existing evidence proved that implementation was missing, but did not prove the proposed five-directory activation was necessary. The trigger evidence is recorded directly in [FRFC self-Audit F-01](../../FOUNDATION/04-Audits/AUDIT-FRFC-0003-activate-platform-implementation-profile.md#f-01--validation-step-1-evidence-is-not-yet-accepted).

### 2.2 Allowed Files

- `VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md`
- `VALIDATION/05-Validation-Audit/AUDIT-VALIDATION-04.md`
- `VALIDATION/06-Validation-Review/REVIEW-VALIDATION-04.md`

### 2.3 Forbidden Files and Actions

- all Foundation normative artifacts during this Validation cycle;
- FRFC status transition, FD creation, Standard or README patch;
- `FOUNDATION/11-*` through `15-*` creation;
- dependency, lock, source, test, workflow, database, container, or Runtime files;
- Builder Pack, Workspace, Project, APES, model, network, Git publication, or release
  action.

### 2.4 Inputs

1. [Directory Standard](../../FOUNDATION/03-Standards/directory-standard.md), especially
   §§3.2, 5.1, 5.2, 6, 7.1, 8, and 10.2.
2. [Runtime Specification](../../FOUNDATION/03-Standards/runtime-specification.md).
3. [Pack Standard](../../FOUNDATION/03-Standards/pack-standard.md).
4. [Quality Gate Standard](../../FOUNDATION/03-Standards/quality-gate-standard.md).
5. [Validation Cycle 01 Report](REPORT-VALIDATION-01.md), especially §§4.1, 4.4, 9,
   and 10.
6. [Validation Cycle 01 Audit](../05-Validation-Audit/AUDIT-VALIDATION-01.md) and
   [Review](../06-Validation-Review/REVIEW-VALIDATION-01.md).
7. [Foundation Baseline Report](../../FOUNDATION/06-Reports/REPORT-FOUNDATION-BASELINE-01.md).
8. [Change-Control Policy](../../FOUNDATION/02-Governance/change-control-policy.md).
9. [RFC Policy](../../FOUNDATION/08-RFCs/rfc-policy.md).
10. [FD-0003](../../FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md),
    which binds the exact current Directory Standard baseline version.
11. [FD-0004](../../FOUNDATION/09-Decisions/FD-0004-authorize-foundation-rc-1.md),
    whose `16-Releases` history is evidence of a direct FD path claim but is not a
    complete precedent for this stricter post-RC route.
12. [Implementation Plan](../../IMPLEMENTATION-PLAN.md), as non-normative supporting
    design only.

### 2.5 Outputs, Quality Gates, and Stop Condition

Outputs are this Report, its Builder self-Audit, and a Pending human Review. The cycle
must satisfy evidence accuracy, Foundation relevance, minimality, cross-reference,
isolation, compatibility, and security-boundary checks. It stops with the Review
Pending; no later governance or implementation step is auto-authorized.

## 3. Validation Questions and Evidence-Based Findings

### Q1. What executable capability is actually missing?

Validation Cycle 01 found that Pack authoring and Runtime behavior are defined at the
contract level, but concrete Pack execution and Runtime invocation require post-
Foundation implementation. Its Remaining Risk RR3 records that no concrete Runtime,
Engine, SDK, or Plugin implementation exists. Its recommendation also warns that a
Builder Pack created before Runtime implementation would be non-executable.

The current repository contains specifications and governance records, not an
executable Runtime package. The validated gap is therefore **implementation**, not a
missing conceptual Standard.

**Finding:** a concrete implementation slice is justified, but Cycle 01 did not
determine the directory scope of that slice.

### Q2. What is the smallest useful implementation slice?

The first slice needs to prove that the Foundation contracts are machine-checkable
before introducing orchestration or side effects. The minimum capability is:

- safely parse the canonical human-reviewable source artifacts and declared structured
  metadata as untrusted data;
- validate IDs, versions, states, dependencies, permissions, stop conditions, and
  cross-references;
- emit deterministic, auditable machine-readable validation and integrity results;
- provide a local/offline user interface for validation; and
- include valid and invalid fixtures plus unit, property, integration, and security
  boundary tests.

It does not need a model, network, LangGraph, database, API server, Workspace
provisioner, Plugin adapter, SDK, or real Pack instance.

Markdown/YAML Front Matter, canonical JSON, SHA-256, and
`research-os validate <pack>` remain non-binding implementation candidates in the
technical plan; a later F-ADR must choose or replace them.

**Finding:** an offline Pack Validator capability is the minimum evidence-producing
work product; its serialization, hash algorithm, and command surface are not selected
by this Validation cycle.

### Q3. Which reserved Foundation path is required for that slice?

Directory Standard §5.1 reserves prefix `11-` for future Builder Runtime / Engines.
The Validator belongs to that implementation boundary: it is the read/validate/compile
front edge of the Builder Runtime and can include its fixtures and tests under the same
authorized tree.

Placing it under `10-ADRs`, `03-Standards`, a new root `src/`, or a Project tree would
violate the declared storage purpose or introduce a different unapproved layout.

**Finding:** only `FOUNDATION/11-Runtime/` is required for Phase 1.

### Q4. Are exact names for prefixes 12–15 required now?

No. The first slice has no SDK distribution, Plugin execution, Workspace provisioning,
or independent executable Quality Gate product. Tests and fixtures needed by the Pack
Validator can remain under its authorized Runtime tree. The Directory Standard already
preserves prefixes 12–15 for future use without requiring their exact names today.

Claiming all four names would not unlock any acceptance criterion for the offline
Validator. It would instead make unused component boundaries appear approved and raise
the risk of placeholder or framework-first expansion.

**Finding:** prefixes 12–15 must remain unchanged and unclaimed in this cycle.

### Q5. Can `11-Runtime` be created under the existing Standard without a Foundation
change?

No implementation artifact can be added ad hoc. Directory Standard:

- lists the current Foundation layout in §3.2;
- reserves `11-` in §5.1 and permits a reserved prefix to be claimed by an FD or a
  future Standard in §5.2;
- forbids artifacts in reserved directories until a Task or FD authorizes them in §6;
- requires a new top-level path to be named in the Standard and Foundation README in
  §7.1; and
- requires a valid path to be listed in §3.2 or added by an FD in §8.

These clauses support a governed additive path assignment, not immediate code creation.
FD-0004's creation of `16-Releases` shows that an FD can directly claim a reserved
prefix, but that history did not fully reconcile §7.1 and is not repeated as a complete
precedent. This cycle selects the stricter Standard + README + FD path.

**Finding:** a Foundation FRFC and implementing FD are necessary before the controlled
Directory Standard / README patch. A separately approved post-RC governed-work-unit
mechanism is also required before implementation because Constitution Tasks 01–12 are
closed.

### Q6. What is the change classification and version impact?

Adding one previously reserved top-level path without moving or invalidating existing
paths is backward compatible under Directory Standard §10.2 and Change-Control Policy
§2.2, which support a **Minor Foundation change**. Directory Standard §11 also says
generically that “Path mutations are Major changes,” creating a classification tension.
The more specific additive rule supports the provisional Minor recommendation, but the
implementing proposal must repair that wording and the Human Architect must confirm the
classification.

The proposed patch should advance the Directory Standard from `0.1.0-draft` to
`0.2.0-draft`, refresh its `Foundation Version` field to the then-current
`1.0.0-rc.1`, add the required transition metadata, update the exact normative rows,
update the Foundation README Layout, and add a versioned CHANGELOG entry. It does not
amend the Constitution, move the RC tag, or by itself change `FOUNDATION/VERSION`.

**Finding:** provisionally Minor and non-breaking; FRFC + FD + Audit + Review are
required, and no consumer migration appears necessary. The §10.2/§11 wording conflict
must be resolved before the classification becomes binding.

### Q7. Where do implementation technology choices belong?

Python, `uv`, Pydantic, Typer, Markdown/YAML, JSON, SHA-256, FastAPI, PostgreSQL, and
LangGraph are implementation choices, not Directory Standard or Validation semantics.
The technical plan may recommend candidates, but a later F-ADR must select formats,
integrity algorithm, command surface, dependencies, versions, licenses, lock-file
policy, supported platforms, and adapter boundaries before implementation manifests
appear.

**Finding:** technology choices belong in an F-ADR after directory-patch approval, not
in the FRFC's normative Standard text.

### Q8. Is FRFC-0003 recommended?

Yes, but only after narrowing it to the validated need and only after this Validation
cycle is human-reviewed. The FRFC should:

1. claim only `FOUNDATION/11-Runtime/`;
2. provide the exact Directory Standard, README, header, version, and CHANGELOG patch,
   including reconciliation of the existing FD-0004-authorized `16-Releases` path;
3. keep prefixes 12–15 unchanged;
4. require a separate Ratified implementing FD;
5. require patch Audit/Report/Review before an ADR or governed implementation work
   unit;
6. require the Human Architect to approve the lawful post-RC work-unit mechanism and
   limit its first work product to the offline Pack Validator; and
7. preserve APES, Pack instance, Runtime execution, model, network, and external side-
   effect prohibitions.

**Finding:** a narrowed FRFC is recommended; the original five-path Draft is not.

## 4. Alternatives Matrix

| Option | Compliance | Delivers Phase 1 | Scope Cost | Result |
|---|---|---|---|---|
| A. Put code in an existing governance directory | Fails path purpose and isolation | No | High | Reject |
| B. Add a root `src/` package without Foundation path authority | Fails current root/layout rules | Yes technically | High | Reject |
| C. Claim only `FOUNDATION/11-Runtime/` through FRFC/FD/patch | Compliant if all gates pass | Yes | Lowest | **Recommend** |
| D. Name `11-Runtime` through `15-Quality-Gates` now | Governance route can be made compliant | Yes | Unvalidated expansion | Reject now |
| E. Start a real Builder Pack or APES pilot first | Lacks executable validator and Project authority | No | Highest | Reject |

## 5. Foundation Relevance Assessment

The gap is Foundation-relevant because the canonical address of a Foundation Runtime
implementation is governed by the L3 Directory Standard. It cannot be solved solely by
a repository-level ADR. The behavioral implementation can remain non-normative and
replaceable, but the top-level path assignment requires the Foundation Change
Principle's five-step route.

This is a narrow path-governance change. It does not justify new Foundation Standards,
new artifact classes, or Project-specific rules.

## 6. Compatibility, Security, and Isolation

- Existing Foundation paths, IDs, and cross-references remain valid.
- Prefixes 12–15 retain their existing generic reservation.
- Canonical human-reviewable source artifacts remain authoritative; any derived
  machine-readable representation is evidence only.
- Structured metadata is parsed as untrusted data without object construction or
  content execution; the concrete format and parser remain F-ADR choices.
- Path resolution rejects traversal, absolute escape, and symlink escape.
- Inputs are never executed as instructions.
- The first slice has no model, network, plugin, subprocess, database, or external Git
  capability.
- Secret values are prohibited in sources, fixtures, errors, and logs.
- No APES or other Project data, lifecycle, or governance enters Foundation code/tests.
- Builder, Auditor, Reviewer, and Architect approval boundaries remain explicit.

## 7. Risks and Controls

| Risk | Likelihood | Impact | Control |
|---|---|---|---|
| `11-Runtime` naming is mistaken for code authorization | Medium | High | Separate FRFC, FD, patch, ADR, governed-work-unit, and implementation Review gates |
| Validator scope grows into orchestration | Medium | High | Offline behavior and explicit prohibitions in FRFC/work-unit scope |
| Future prefixes are prematurely populated | Medium | High | Leave 12–15 unchanged; no placeholders or `.gitkeep` |
| Technology leaks into normative Standards | Medium | High | Record choices in F-ADR and adapters only |
| Untrusted source or structured metadata escapes the repository | Medium | High | Non-executing parser, bounded resolver, adversarial tests; format choice deferred to F-ADR |
| A Builder self-check is treated as independent approval | Medium | High | Mark Audit non-binding and keep Review Pending |

## 8. Recommended Governance Sequence

```text
Validation 04 Report + Builder self-Audit
→ independent Validation Audit
→ independent Human Review Approved / Approved with Notes
→ distinct Human Architect acceptance of Step-1 evidence
→ narrowed FRFC-0003 Draft
→ independent Audit + independent Human Review + Human Architect approval
→ FD-0006 Pending package + Ratification
→ exact Directory Standard / Foundation README / CHANGELOG patch
→ patch Audit + Report + Human Review
→ F-ADR for implementation choices
→ Human Architect-approved post-RC work-unit mechanism
→ explicitly scoped offline Pack Validator work unit
→ code, tests, Audit, Report, Human Review
```

No gate in this sequence is satisfied by creating this Report.

## 9. Provisional Conclusion and Stop Condition

**Provisional conclusion:** the validated minimal path is to claim only
`FOUNDATION/11-Runtime/`. The proposed five-path activation is over-broad for the
current evidence. A narrowed FRFC is necessary because the path change is Foundation-
wide and normative; an ADR alone is insufficient.

**Stop condition:** reached. Validation 04 remains Draft while its Builder self-Audit
is FAIL. No formal human Review is requested until an independent Audit returns PASS or
PASS with Notes. FRFC-0003 must remain Draft and must not be Submitted, approved, or
used to create FD-0006 while this evidence is pending.

## 10. Change Log

| Version | Date | Change |
|---|---|---|
| `0.1.0-draft` | 2026-08-05 | Created implementation-triggered evidence record; compared one-path and five-path activation; recommended only `11-Runtime`; held all next steps for human Review. |

---

*End of Validation Cycle 04 Report — Draft / provisional, 2026-08-05.*
