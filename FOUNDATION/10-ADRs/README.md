# 10-ADRs

This directory holds **Foundation-level Architecture Decision Records (F-ADRs)** of Research-OS Foundation. P-ADRs (Project-level) and R-ADRs (Repo-level) are stored elsewhere — see `adr-policy.md` §11.

## Status

- The ADR mechanism is established by `adr-policy.md`.
- **No ADRs exist yet.** Task 02 does not create ADRs unless implementation choices require recording. No such requirement arose in Task 02.

## Contents

| File | Status | Description |
|---|---|---|
| `README.md` | (this file) | Index for the ADR directory |
| `adr-policy.md` | Draft / In Review | Operational ADR policy |

## What is an ADR

An **Architecture Decision Record (ADR)** captures a **significant, non-normative** architectural decision — for example, "use JSON for FD metadata" or "use SQLite for the FD ledger". ADRs are lighter-weight than FDs and RFCs; they document *what was decided and why* without changing Foundation rules.

ADRs are **not** normative. They become binding when an FD/PD explicitly ratifies them or when a Reviewer-approved Operational Decision accepts them.

## Why ADRs Are a New Artifact Class

Foundation previously had:

- **FDs** — normative architectural decisions.
- **RFCs** — proposals for normative change.

Neither captured implementation-level choices in a discoverable form. ADRs fill that gap.

## Future Work

- `ADR-0001-...` and beyond, as Foundation Tasks 03–12 require architectural decision records.
- A ratification cycle for the ADR policy itself (anticipated as a follow-on).

## Naming

ADRs follow `ADR-NNNN-short-title.md` (Foundation scope). See `adr-policy.md` §4.

## Out of Scope

- Foundation Decisions (FDs) — stored in `FOUNDATION/09-Decisions/`.
- Foundation RFCs (FRFCs) and Release RFCs (RRFCs) — stored in `FOUNDATION/08-RFCs/`.
- Project Decisions (PDs) and Project ADRs — stored within Project directories.

## Dependencies

- Constitution v0.1.0-draft (Provisional) §7 — defines decision mechanisms.
- Task 02 Governance artifacts — operationalize the ADR mechanism.
- Foundation FD mechanism — required for ADR ratification when an ADR is normative-binding.