# 09-Decisions

This directory holds the **Foundation Decision Records (FDs)** of Research-OS Foundation.

FDs are the binding mechanism for architectural change at the Foundation level. They are defined by Constitution v0.1.0-draft (Ratified) §7 and operationalized by `foundation-decision-policy.md` (this directory).

## Status

- `FD-0001-ratify-constitution.md` is **Ratified** (Status: Ratified; Date: 2026-08-03; Approver: Human Architect). The Constitution is **Ratified** at v0.1.0-draft.
- `FD-0002-adopt-foundation-change-principle.md` is **Ratified** (Status: Ratified; Date: 2026-08-03; Approver: Human Architect). The Foundation Change Principle is **binding** through FD-0002.
- `FD-0003-approve-foundation-baseline.md` is **Ratified** (Status: Ratified; Date: 2026-08-04; Approver: Human Architect). FD-0003 collectively approves the 15 candidate baseline components (5 governance artifacts + 10 Foundation Standards) enumerated in REPORT-FOUNDATION-BASELINE-01.md §4.3. The FD records the binding baseline authority derivation text for the exact versions enumerated; the 15 candidates retain `Draft / In Review` document-level status (in-place header status promotion is deferred to a future FD cycle).
- `FD-0004-authorize-foundation-rc-1.md` is **Ratified** (2026-08-04). It authorizes the internally Applied Foundation `1.0.0-rc.1` Release but does not authorize external publication. A separate Human Architect instruction authorized the docs-first GitHub Pre-release, completed on 2026-08-05.
- `FD-0005-implement-first-rc-prerequisite-repair.md` is **Ratified** (2026-08-04). It implements Approved FRFC-0002; the authorized single-file §9.2 repair advanced Release Specification from `0.1.0-draft` to `0.2.0-draft` and passed its repair Audit and Review.
- Five FDs are now Ratified.

## Contents

| File | Status | Description |
|---|---|---|
| `README.md` | (this file) | Index for the FD directory |
| `foundation-decision-policy.md` | Draft / In Review | Operational FD policy |
| `FD-0001-ratify-constitution.md` | **Ratified** (2026-08-03) | Ratify Constitution v0.1.0-draft |
| `FD-0002-adopt-foundation-change-principle.md` | **Ratified** (2026-08-03) | Adopt Foundation Change Principle (FRFC-0001) |
| `FD-0003-approve-foundation-baseline.md` | **Ratified** (2026-08-04) | Collectively approve 15 candidate baseline components |
| `FD-0004-authorize-foundation-rc-1.md` | **Ratified** (2026-08-04) | Authorize internally Applied Foundation `1.0.0-rc.1`; external Pre-release is a separate 2026-08-05 action |
| `FD-0005-implement-first-rc-prerequisite-repair.md` | **Ratified** (2026-08-04) | Implement Approved FRFC-0002 through an exact controlled patch; repair applied and approved |

## Naming

All FDs follow the pattern `FD-NNNN-short-title.md`. See `foundation-decision-policy.md` §3.

## Future Work

- The separately authorized external publication of `v1.0.0-rc.1` completed on 2026-08-05 as a docs-first GitHub Pre-release. Any Stable, package-registry, successor RC, or expanded publication remains a separate future action.
- A future FD **may** perform in-place header status promotion for the 15 candidate baseline components (currently `Draft / In Review`) only if scope warrants and the FCP workflow is followed. This is recorded as Condition C-2 in FD-0003 §9.
- A future FD **may** address O-2 (pre-existing `v`-prefix inconsistency) only if version governance meaning or policy is changed (per Validation Cycle 02 Review Note A-4). O-2 is Open Observation, Non-blocking.
- A future FD **may** supersede FD-0003 if a future Validation Cycle or Audit identifies a defect, per `foundation-decision-policy.md` §9 and `change-control-policy.md` §13 (rollback).

## Out of Scope

- Project Decisions (PDs) — those are stored in `PROJECTS/<project>/09-Decisions/` post-Foundation.
- Disagreement Records (DIS-) — also stored here, once raised.
- RFCs and ADRs — stored in `FOUNDATION/08-RFCs/` and `FOUNDATION/10-ADRs/` respectively.

## Dependencies

- Constitution v0.1.0-draft (Ratified by FD-0001) §7 — defines FD format and authority.
- FD-0002 (Ratified) and FRFC-0001 (Approved) — binding Foundation Change Principle.
- Task 02 Governance artifacts — operationalize FD mechanism.
- Foundation Baseline Decision Cycle 01 (FD-0003, Ratified 2026-08-04) — collectively approves the 15 candidate baseline components.
- Human Architect approval — required for ratification.
