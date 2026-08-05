# Research-OS Foundation

This directory is the canonical home of Research-OS Foundation artifacts.

The Foundation is governed by [`01-Constitution/constitution.md`](./01-Constitution/constitution.md). Any artifact created here MUST satisfy the Constitution and the Quality Gate defined therein.

## Foundation Version

`1.0.0-rc.1` — internally Applied and externally published as a GitHub
Pre-release. See [`VERSION`](./VERSION) and the
[`v1.0.0-rc.1` Release](https://github.com/longyuanai/Research-OS/releases/tag/v1.0.0-rc.1).

> The Foundation content baseline is local commit `620312b`. Annotated tag
> `v1.0.0-rc.1` points to publication-wrapper commit `139d455`, whose only tree
> additions are the root Apache-2.0 `LICENSE` and `.gitattributes`; the 25-entry
> Foundation Manifest is unchanged. The tag is publicly available at
> `longyuanai/Research-OS`; no registry publication, Pack, Runtime, Workspace,
> Project, or APES activation is implied.

## Layout

| Path | Purpose |
|---|---|
| `01-Constitution/` | The supreme governance document of Research-OS. |
| `02-Governance/` | Governance Model, Roles & Authority, Approval Workflow, Change-Control Policy, Disagreement & Escalation. |
| `03-Standards/` | Foundation Standards (e.g., `directory-standard.md`). Reserved for L3 normative specifications. |
| `04-Audits/` | Audit artifacts verifying compliance with the Quality Gate. |
| `05-Statistics/` | (Reserved) Statistical and quantitative artifacts. |
| `06-Reports/` | Reports produced by Engines and Builders (incl. seven-section Task Reports). |
| `07-Reviews/` | Human Review records and dispositions. |
| `08-RFCs/` | Foundation RFC policy (`rfc-policy.md`) and FRFC and RRFC records. |
| `09-Decisions/` | Foundation Decision policy and FD records (FD-0001 through FD-0005 Ratified). |
| `10-ADRs/` | Architecture Decision Record policy (`adr-policy.md`) and F-ADR records. |

The numbered prefixes above are normative; they define the order in which Foundation work proceeds.

## Current Status

- **Constitution:** **Ratified** by `FD-0001` on 2026-08-03 (`ratifies-constitution: 0.1.0-draft`). See `../CHANGELOG.md` for history.
- **Foundation Change Principle:** **Ratified and binding** by `FD-0002` on 2026-08-03 per Architect Decision, Part B. Implemented through existing governance artifacts only (`governance-model.md` §14; `change-control-policy.md` §§8–14). See `FOUNDATION/08-RFCs/FRFC-0001-foundation-change-principle.md` (Approved) and `FOUNDATION/09-Decisions/FD-0002-adopt-foundation-change-principle.md` (Ratified).
- **Foundation Baseline:** **Collectively Approved** by `FD-0003` on 2026-08-04 per Architect Decision, Part B. FD-0003 approves 5 governance artifacts (`governance-model.md`, `roles-and-authority.md`, `approval-workflow.md`, `change-control-policy.md`, `disagreement-and-escalation.md`) and 10 Foundation Standards (`directory-standard.md`, `schema-standard.md`, `pack-standard.md`, `runtime-specification.md`, `quality-gate-standard.md`, `engine-specification.md`, `sdk-specification.md`, `plugin-specification.md`, `workspace-specification.md`, `release-specification.md`) for the exact versions enumerated in FD-0003 §6. The 15 candidates retain `Draft / In Review` document-level status; binding baseline authority derives from Ratified FD-0003 for the exact version enumerated. See `FOUNDATION/09-Decisions/FD-0003-approve-foundation-baseline.md`.
- **Foundation Phase:** Foundation Baseline Approval cycle closed (FD-0003 Ratified, 2026-08-04). Foundation Baseline Review Cycle 01 closed (REVIEW-FOUNDATION-BASELINE-01 Disposition: Approved with Notes, 2026-08-04).
- **Foundation v1.0 RC:** **internally Applied** as `1.0.0-rc.1` on 2026-08-04 under Ratified FD-0004. Annotated tag `v1.0.0-rc.1` seals that Foundation content plus the two-file publication wrapper described above and was externally published as a docs-first GitHub Pre-release on 2026-08-05 under a separate Human Architect instruction. FD-0004 itself does not authorize external publication.
- **First-RC prerequisite repair:** `FRFC-0002` is **Approved with Notes** (2026-08-04). Its §9.2 repair was implemented under Ratified FD-0005, audited PASS with Notes, reviewed Approved with Notes, and reconciled into the RC package before Stage B.
- **Implementing decision:** `FD-0005` is **Ratified** (2026-08-04; Review Approved with Notes). Release Specification `0.2.0-draft` repair is applied and approved.
- **Foundation Version:** `1.0.0-rc.1` (internally Applied).
- **First Project:** APES (paused; Frozen).
- **Foundation:** Frozen except for changes authorized through approved RFCs. The Foundation Patch Cycle 01 (per Architect Decision, 2026-08-03, Part B; Closeout Reconciliation 2026-08-03) was a narrowly scoped patch window only; the Foundation Freeze was preserved throughout. The authorized Patch Cycle closes after human Review approval, and the Foundation resumes its normal Frozen posture.

## Rules of Engagement

- One Foundation Task per cycle (see Constitution §15).
- Seven-section report after every Task.
- Human approval required before the next Task.
- No auto-commit, no auto-push, no auto-continue.

**Foundation Change Principle (binding per FD-0002, 2026-08-03):** No new Foundation artifact may be introduced unless (1) the need is discovered during a Validation Cycle; (2) the gap is documented with evidence; (3) an RFC is proposed; (4) the RFC is reviewed and approved; (5) the Foundation is patched through the approved governance process. Idea alone is never sufficient to expand the Foundation. Operational workflow codified in `FOUNDATION/02-Governance/change-control-policy.md` §8.

## Post-RC Implementation Direction

The non-normative [Research-OS Technical Implementation Plan](../IMPLEMENTATION-PLAN.md)
compares six active open-source agent/research platforms and proposes a minimal,
evidence-first implementation path. It does not activate Runtime, Pack, Workspace,
Project, or APES work; those changes still require their applicable governance cycle.

[Validation Cycle 04](../VALIDATION/04-Validation-Report/REPORT-VALIDATION-04.md) and
[FRFC-0003](08-RFCs/FRFC-0003-activate-platform-implementation-profile.md) are now
prepared as **blocked Draft governance work**. The evidence provisionally supports
only `FOUNDATION/11-Runtime/`; prefixes `12`–`15` remain unchanged and unclaimed. Both
Builder self-Audits are `Draft / FAIL`, both human Reviews remain Pending, and the RFC
is not eligible for submission. It creates no implementation directory, FD, Standard
patch, ADR, dependency, Pack, Project, or APES artifact. Independent Audit, human
Validation disposition, and Human Architect resolution of the non-Task Report schema
fit are the next gates.

## Foundation Tasks (per Constitution §15)

| # | Task | Status |
|---|---|---|
| 01 | Constitution | **completed (ratified by FD-0001 on 2026-08-03)** |
| 02 | Governance | **completed (approved; Review status reconciled 2026-08-04)** |
| 02.1 | Governance Terminology & Hierarchy Correction | **completed (approved; Review status reconciled 2026-08-04)** |
| 03 | Directory Standard | **completed (approved)** |
| 04 | Schema Standard | **completed (approved)** |
| 05 | Builder Pack Standard | **completed (approved)** |
| 06 | Builder Runtime Specification | **completed (approved)** |
| 07 | Quality Gate | **completed (approved)** |
| 08 | Engine Specifications | **completed (approved)** |
| 09 | SDK Specifications | **completed (approved)** |
| 10 | Plugin Specification | **completed (collectively approved by FD-0003)** |
| 11 | Workspace Specification | **completed (collectively approved by FD-0003)** |
| 12 | Release Specification | **completed (FD-0003 baseline approval; FD-0005 repair applied and approved)** |
| — | Validation Cycle 01 | **completed (Approved with Notes)** |
