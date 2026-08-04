# 02-Governance

This directory holds the **Governance Model** of Research-OS Foundation. It is the operational layer that turns the Provisional Constitution (`v0.1.0-draft`) into an executable governance system.

The artifacts here define:

- The governance hierarchy and its conflict-resolution rules.
- Roles, authority, and separation-of-duties.
- Approval, change-control, and disagreement workflows.
- The Foundation Decision (FD) mechanism.
- The RFC and ADR mechanisms.
- The process by which the Constitution itself is ratified.

These artifacts are **technology-independent**, **project-independent**, and **implementation-independent**. They govern only the rules under which any Project may exist.

See [`governance-model.md`](./governance-model.md) for the top-level governance model and [`./README.md`](./README.md) (this file) for directory scope.

## Status

- All governance artifacts in this directory are **Draft / In Review** under Foundation version `0.1.0-dev`.
- The Constitution (`v0.1.0-draft`) remains **Provisional** until `FD-0001` is ratified by a human Architect.
- `FD-0001` is **Ratified** (2026-08-03) — see [`FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md`](../09-Decisions/FD-0001-ratify-constitution.md).

## Future work

- Operating procedures for each role (Architect, Builder, Auditor, Reviewer, Maintainer, Release Manager, Project Owner, Contributor).
- Templates for governance records (already enumerated; templates are reserved for a future governance cycle).

## Out of scope

- Platform Standards (Tasks 03–04).
- Engines, Runtime, SDKs, Plugins, Workspaces (Tasks 05–11).
- Project policies, Packs, Sprints, Releases (post-Foundation).
- Any Project-specific governance rule (e.g., APES-specific rules are forbidden by Constitution §11.4).
