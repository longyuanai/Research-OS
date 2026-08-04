# Research-OS Foundation — Builder Runtime Specification

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Path:** `FOUNDATION/03-Standards/runtime-specification.md`
**Supersedes:** none
**Related:** Constitution v0.1.0-draft (Provisional) §1, §2, §3, §4, §6, §9, §10, §11, §13, §14, §15; `FOUNDATION/02-Governance/governance-model.md` §6, §7, §8, §9; `FOUNDATION/02-Governance/approval-workflow.md`; `FOUNDATION/02-Governance/change-control-policy.md`; `FOUNDATION/02-Governance/disagreement-and-escalation.md`; `FOUNDATION/02-Governance/roles-and-authority.md`; `FOUNDATION/03-Standards/directory-standard.md`; `FOUNDATION/03-Standards/schema-standard.md` §4–§12; `FOUNDATION/03-Standards/pack-standard.md` §3–§17; `FOUNDATION/08-RFCs/rfc-policy.md`; `FOUNDATION/09-Decisions/foundation-decision-policy.md`; `FOUNDATION/10-ADRs/adr-policy.md`

---

## 1. Purpose and Scope

### 1.1  Purpose

This Builder Runtime Specification defines the **contract** for a Builder Runtime — the L5 component that *interprets* a Builder Pack and drives a Mission, its Programs, its Tasks, and its Deliverables through the Foundation Task Protocol (Constitution §15).

The Runtime is to the Pack as the **executor** is to a declarative bundle: it does not decide what to do (that is the Pack's Mission, Programs, Tasks, and Deliverables); it does not decide whether to do it (that is the human Architect's review); it decides **how** to do it under the constraints declared by this Specification.

The Runtime Specification is the bridge between the **declarative** Pack Standard (`pack-standard.md`) and a future **imperative** runtime implementation. This Specification is normative; the implementation is a separate downstream artifact (and is **not** created in Task 06).

### 1.2  In Scope

This Specification defines:

1. Runtime Purpose — what the Runtime is for, what it is not for.
2. Runtime Architecture — the abstract components and their relationships.
3. Runtime Lifecycle — the 12 stages of a Runtime cycle.
4. Runtime Input Specification — Mission, Pack, Task, Schema, Governance inputs.
5. Runtime Output Specification — Artifacts, Audit, Reports, Reviews, Status.
6. Quality Gate Integration — validation point, failure handling, repair cycle, approval blocking.
7. Human-in-the-loop Model — approval boundary, stop condition, manual override.
8. Runtime Security Boundary — permission scope, forbidden actions, isolation rules.
9. Runtime Compatibility — version handling, migration rules, future extensions.

### 1.3  Out of Scope

This Specification does **not** create:

- Any runtime implementation. **No runtime source code is written.** No runtime directory, no source files, no test files, no executables.
- Any CLI. **No `cli/` directory, no command-line interface.**
- Any scripts. **No `.sh`, `.ps1`, `.bat`, `.py`, `.js`, `.ts` orchestrator scripts.**
- Any agents. **No Agent definitions, no agent templates.**
- Any MCP server. **No MCP server implementation.**
- Any SDK. **No SDK source, no SDK package.**
- Any plugin. **No plugin definition, no plugin manifest.**
- Any engine. **No Prompt Engine, Audit Engine, Evidence Engine, Statistics Engine, Report Engine, Builder Engine, or any other engine.**
- Any validator. **No standalone validator implementation.**
- Any Pack instance. **No `PACK-00`, no `PACK-01`.** No Mission execution.
- Any APES files. **No APES migration, no APES Project subtree.**
- Any git operations. **No commit, push, branch, or tag.**
- Any Foundation Decision (`FD-0006-ratify-runtime-specification.md`) — ratification is **deferred and conditional**.

This Specification is **technology-neutral**: no language binding, no framework binding, no serialization binding, no operating-system binding. The Runtime Specification is normative *behavior*; a concrete Runtime implementation is downstream (and is **not** a Task 06 deliverable).

## 2. Normative Status

This Builder Runtime Specification is **Draft / In Review** at Foundation `0.1.0-dev`, Constitution `v0.1.0-draft` (Provisional). It is the L3 Foundation Standard that operationalizes the **Pack** concept (declared in `pack-standard.md`) for *execution*.

**Conformance.** A future Builder Runtime is conformant with this Specification if and only if:

- For every requirement in §3–§9, the Runtime's behavior matches the contract (in natural language or in a formally expressed normative form), AND
- The Runtime produces artifacts that conform to `schema-standard.md` §4–§12, AND
- The Runtime respects the lifecycle, immutability, and supersession rules of `governance-model.md` §6–§9, AND
- The Runtime honors the four §11 Quality Gate criteria at every stage.

**Conflict resolution.** Per `governance-model.md` §4:

1. Constitution prevails.
2. Higher `Status:` prevails.
3. Later SemVer version prevails.
4. Later ISO-8601 date prevails.
5. Higher-numbered ID prevails.
6. Otherwise escalate.

Where this Specification and the Constitution appear to conflict, the Constitution prevails. Where this Specification and an active FD appear to conflict, the FD prevails if its `Status:` is `Ratified`; otherwise this Specification governs provisionally.

**Technology neutrality.** This Specification does not bind the Foundation to any language, framework, runtime, SDK, plugin, MCP server, or serialization format. A consumer (Builder Runtime, validator, simulator, harness) claims conformance by demonstrating that for every requirement in §3–§9, the same contract holds. The mapping between the contract and a concrete execution is the consumer's responsibility.

## 3. Runtime Purpose

### 3.1  Definition

A **Builder Runtime** is a Foundation component that:

- Loads a Mission, a Pack, and a Task declaration.
- Validates that the Pack's scope, dependencies, schemas, and governance inputs are intact.
- Drives a single Task through the 12 stages of the Runtime Lifecycle (§5).
- Generates the artifacts required by `schema-standard.md` §4–§12 (Audit, Report, Review, Evidence, Statistics, Manifest, Task, Pack, Release).
- Halts at every Human Approval boundary (§7) and awaits disposition.
- Records all transitions in a Status log (§6.5) for Foundation audit.

### 3.2  What the Runtime IS

A Builder Runtime IS:

- **Declarative-driven.** The Runtime interprets a Pack; it does not invent one.
- **Cycle-bound.** A Runtime cycle is bounded by a single Task; multi-Task execution is a future Runtime cycle.
- **Auditable.** Every Runtime action is recorded in an Audit Report.
- **Human-supervised.** Every state-changing action passes through a Human Approval boundary.
- **Schema-conformant.** Every emitted artifact conforms to the relevant Foundation schema.
- **Project-independent.** The Runtime does not assume any Project; it operates on Foundation artifacts.

### 3.3  What the Runtime IS NOT

A Builder Runtime IS NOT:

- **Autonomous.** The Runtime does not decide what to do. The Mission, Program, Task, and Deliverable declarations decide; the Runtime executes.
- **Self-modifying.** The Runtime does not edit its own specification. Amendments require an FD.
- **Self-elevating.** The Runtime does not approve its own actions. Human approval is required at every state transition (per §7).
- **A scheduler.** The Runtime does not manage multiple concurrent Tasks. Each Runtime cycle is bounded by a single Task.
- **A network service.** The Runtime is not an HTTP server, a WebSocket server, an MCP server, or a long-running daemon (per §8.2).
- **A code generator.** The Runtime does not write executable code (per §8.2).
- **An autonomous agent.** The Runtime is not an Agent in the multi-agent sense; it does not delegate to sub-agents (per §8.2).
- **An APES-bound executor.** The Runtime does not assume APES or any other Project. It operates on Foundation artifacts.

## 4. Runtime Architecture

### 4.1  Component Model

The Runtime is composed of six **abstract components**. These are normative *roles*; the concrete mapping to software modules is a downstream concern.

| Component | Role |
|---|---|
| `Input Loader` | Reads Mission, Pack, Task, Schema, Governance inputs and prepares them in a normalized form. |
| `Scope Validator` | Verifies that the Pack's scope is consistent with the Foundation Version, the Constitution Version, and the active FDs. |
| `Dependency Resolver` | Verifies that every `requires:` and `references:` dependency declared by the Pack (per `pack-standard.md` §15) resolves and is version-compatible. |
| `Task Executor` | Carries out the body of a single Task. Produces Deliverables. |
| `Artifact Generator` | Emits the artifacts required by `schema-standard.md` §4–§12: Evidence, Statistics, Audit, Report, Review, Manifest. |
| `Human Gate` | Halts at every state transition that requires human disposition (per §7). |

### 4.2  Data Flow

```
[Input Loader] → [Scope Validator] → [Dependency Resolver] →
[Task Executor] → [Artifact Generator] → [Human Gate] → [Audit / Report / Review]
```

The data flow is **linear within a cycle** but **cyclic across cycles**: each cycle's Audit/Report/Review feeds the next cycle's input. Multi-cycle behavior is described in `pack-standard.md` §4 (Pack Lifecycle) and `governance-model.md` §7 (Governance Status Lifecycle).

### 4.3  Component Properties

Every Runtime component MUST satisfy:

- **Deterministic-input behavior.** Given the same inputs, the component produces the same outputs (subject to §4.4 — non-determinism is bounded by the Audit log).
- **Auditable.** Every component emits at least one Audit `Finding` per cycle.
- **Schema-conformant.** Every artifact the component emits conforms to the relevant `schema-standard.md` schema.
- **Stateless across cycles** (with one exception — the Audit log). A component MAY persist data only via the Audit log and the Schema-conformant artifacts it emits.

### 4.4  Bounded Non-Determinism

A Runtime MAY exhibit bounded non-determinism in:

- The order of `Finding` rows in an Audit Report (subject to `schema-standard.md` §9 Finding rule).
- The order of `Entries` in a Manifest (subject to `schema-standard.md` §8 Manifest rule).
- The temporal ordering of `Review-Date` and `Approved-At` headers.

A Runtime MUST NOT exhibit unbounded non-determinism in:

- The set of artifacts produced (a cycle's output set is fully determined by its inputs).
- The Lifecycle stages traversed (per §5, a cycle traverses exactly the 12 stages in order).
- The Quality Gate verdict (per §6, the verdict is deterministic given the Audit findings and the Review disposition).

## 5. Runtime Lifecycle

### 5.1  Overview

A Builder Runtime cycle traverses **exactly twelve stages**, in order:

1. Initialize
2. Load Mission
3. Load Pack
4. Validate Scope
5. Validate Dependencies
6. Execute Task
7. Generate Artifacts
8. Generate Audit
9. Generate Report
10. Generate Review
11. Human Approval
12. Continue / Stop

A Runtime that skips a stage is **Invalid**. A Runtime that adds a stage is **Invalid** (extensions require an FD per `governance-model.md` §13).

### 5.2  Stage Specifications

#### Stage 1 — Initialize

| Property | Value |
|---|---|
| Inputs | Foundation Version, Constitution Version, Runtime Version, Runtime Run-ID. |
| Outputs | Runtime Run record (Foundation artifact of class `Other`, with `Run-ID`, `Started-At`, `Builder-Role`). |
| Allowed actions | Read Foundation metadata; emit Run record. |
| Forbidden actions | Mutate Foundation metadata; load any Mission or Pack. |
| Stop condition | Failure to read Foundation Version → Runtime halts and emits an Audit `Finding` with severity `Critical`. |

#### Stage 2 — Load Mission

| Property | Value |
|---|---|
| Inputs | `Mission-ID` (parameter to the cycle). |
| Outputs | In-memory Mission record (not yet persisted). |
| Allowed actions | Read Mission file from `FOUNDATION/03-Standards/` (or `<pack-root>/missions/`); verify Mission header. |
| Forbidden actions | Mutate Mission; execute Mission Programs. |
| Stop condition | Mission not found, Mission header invalid, Mission in `Withdrawn` / `Rejected` status → halt with `Critical` finding. |

#### Stage 3 — Load Pack

| Property | Value |
|---|---|
| Inputs | Mission's Pack reference (per `pack-standard.md` §7.2 `FD-Authorization` and the Pack's `Related:` field). |
| Outputs | In-memory Pack record (Manifest + Contents + all bundled artifacts). |
| Allowed actions | Read Pack directory; parse Manifest and Contents; load each bundled artifact's header. |
| Forbidden actions | Mutate Pack; load Programs or Tasks. |
| Stop condition | Pack not found, Manifest inconsistent with directory, Integrity check fails → halt with `Critical` finding. |

#### Stage 4 — Validate Scope

| Property | Value |
|---|---|
| Inputs | Mission, Pack, Foundation Version, Constitution Version, active FDs. |
| Outputs | Scope Validation Report (Audit `Finding` set). |
| Allowed actions | Compare Pack's `FoundationVersion`, `ConstitutionVersion`, and `Status` against active Foundation state; emit `Finding` rows. |
| Forbidden actions | Mutate Pack; downgrade Scope; bypass Scope mismatch. |
| Stop condition | Scope mismatch (e.g., Pack requires a Foundation Version newer than the Runtime's Foundation Version) → halt with `Critical` finding. |

#### Stage 5 — Validate Dependencies

| Property | Value |
|---|---|
| Inputs | Pack's `Dependencies` (per `pack-standard.md` §15), Manifest entries. |
| Outputs | Dependency Validation Report (Audit `Finding` set). |
| Allowed actions | Resolve every `requires:` and `references:` dependency; verify Foundation-Version compatibility; check for circular dependencies; emit `Finding` rows. |
| Forbidden actions | Skip a `requires:` dependency; allow a forbidden dependency (per `pack-standard.md` §15.3). |
| Stop condition | Unresolved `requires:` dependency; circular dependency; forbidden dependency → halt with `Critical` finding. |

#### Stage 6 — Execute Task

| Property | Value |
|---|---|
| Inputs | Pack's selected Task (per `pack-standard.md` §9.3 and the Task's `Pack-ID`, `Mission-ID`, `Program-ID`). |
| Outputs | In-memory Deliverable records (per `pack-standard.md` §10); in-memory Evidence records. |
| Allowed actions | Read Task declaration; read Task's `Verification-Method`; produce Deliverable records. |
| Forbidden actions | Modify Foundation state; bypass the Human Gate; emit Pack-status transitions without approval. |
| Stop condition | Task body fails its declared `Verification-Method` → halt with `Major` finding; the Runtime does not auto-retry. |

#### Stage 7 — Generate Artifacts

| Property | Value |
|---|---|
| Inputs | Stage 6 outputs (Deliverables, Evidence, Statistics, Manifest, Pack, Release — per `schema-standard.md` §4–§12). |
| Outputs | Persisted Foundation artifacts (one or more of: Evidence, Statistics, Audit, Report, Review, Manifest, Task, Pack, Release). |
| Allowed actions | Write artifacts to the paths declared in `directory-standard.md` §4; emit Manifest entries. |
| Forbidden actions | Write artifacts to reserved or non-conformant paths (per `directory-standard.md` §8); emit non-schema-conformant artifacts. |
| Stop condition | Path validation failure; schema validation failure; Manifest entry missing → halt with `Major` finding. |

#### Stage 8 — Generate Audit

| Property | Value |
|---|---|
| Inputs | All Audit `Finding` rows collected from Stages 1–7. |
| Outputs | Persisted Audit Report (per `schema-standard.md` §9) named `AUDIT-<Run-ID>.md`. |
| Allowed actions | Compose Audit Report with §11 Quality Gate criteria verdicts; emit Verdict (`PASS`, `PASS with Notes`, `FAIL`). |
| Forbidden actions | Suppress `Major` or `Critical` findings; downgrade a `Critical` finding to `Minor`; bypass the Verdict. |
| Stop condition | Audit Verdict is `FAIL` → halt with `Critical` finding and proceed to Stage 11 (Human Approval) for disposition. |

#### Stage 9 — Generate Report

| Property | Value |
|---|---|
| Inputs | Stage 7 outputs (Artifacts), Stage 8 output (Audit Verdict), Stage 6 inputs (Task, Deliverables). |
| Outputs | Persisted Task Report (per `schema-standard.md` §5) named `REPORT-<Run-ID>.md`. |
| Allowed actions | Compose the eight-section report: Summary, Files Created, Files Modified, Acceptance Checklist, Verification, Remaining Limitations, Git Status, Next Recommended Task. |
| Forbidden actions | Omit a section; include non-Foundation content. |
| Stop condition | Report cannot be written → halt with `Critical` finding. |

#### Stage 10 — Generate Review

| Property | Value |
|---|---|
| Inputs | Stage 7 outputs, Stage 8 output, Stage 9 output. |
| Outputs | Persisted Review Record (per `schema-standard.md` §6) named `REVIEW-<Run-ID>.md`, with `Disposition: Pending`. |
| Allowed actions | Compose Review Record with Disposition `Pending`, Materials Reviewed, Required Corrections (empty), Reviewer Notes (empty). |
| Forbidden actions | Pre-fill a human disposition; fabricate a Signature; mark the Review as `Approved` without human input. |
| Stop condition | Review Record cannot be written → halt with `Critical` finding. |

#### Stage 11 — Human Approval

| Property | Value |
|---|---|
| Inputs | Stage 8 Audit Verdict, Stage 9 Report, Stage 10 Review Record. |
| Outputs | Review Record with `Disposition` field populated by human Architect (`Approved`, `Approved with Notes`, `Changes Requested`, `Rejected`). |
| Allowed actions | Halt the Runtime; present materials to the human Architect; record the human disposition. |
| Forbidden actions | Auto-approve; auto-reject; simulate a human disposition; bypass the human gate. |
| Stop condition | Human Architect does not supply a disposition within the declared timeout (or fails to act) → Runtime remains halted; no auto-resume. |

#### Stage 12 — Continue / Stop

| Property | Value |
|---|---|
| Inputs | Stage 11 disposition. |
| Outputs | Status transition (per `governance-model.md` §7); next cycle's Run record (if continuing). |
| Allowed actions | If disposition is `Approved` or `Approved with Notes`, transition the affected artifacts to their next status; if disposition is `Changes Requested` or `Rejected`, halt the cycle and emit the Repair Cycle per §6.3. |
| Forbidden actions | Continue past a `Changes Requested` or `Rejected` disposition without a new Run record. |
| Stop condition | Disposition is `Rejected` → Runtime halts the Mission (transitions Mission to `Closed` with `Exit-Status: Failure`); no further cycles. |

### 5.3  Stage Transition Record

Every Runtime cycle produces a **Stage Transition Record** (an Audit `Finding` of class `Stage Transition`) recording:

- `From-Stage`
- `To-Stage`
- `At` (ISO-8601 timestamp)
- `Run-ID`
- `Cycle-ID`

The Stage Transition Record is bound to the Audit Report and is the **authoritative** ordering of the cycle.

### 5.4  Cross-Cycle Behavior

The Runtime is **cycle-bounded**: each cycle processes exactly one Task. Cross-cycle behavior (i.e., running a second Task after the first Task is approved) is governed by:

- `pack-standard.md` §4 (Pack Lifecycle).
- `governance-model.md` §7 (Governance Status Lifecycle).
- This Specification §6.4 (Approval Blocking).

The Runtime does **not** auto-chain Tasks. Each cycle requires a separate Runtime invocation (per §8.2 — no long-running daemon).

## 6. Runtime Input Specification

### 6.1  Overview

The Runtime accepts five categories of inputs: **Mission**, **Pack**, **Task**, **Schema**, and **Governance**. Every input is a Foundation artifact (or a reference to one) and conforms to the relevant `schema-standard.md` schema.

### 6.2  Mission Input

| Field | Source | Required |
|---|---|---|
| `Mission-ID` | `pack-standard.md` §7.2 | R |
| `Status` | `pack-standard.md` §7.2 | R |
| `FD-Authorization` | `pack-standard.md` §7.2 | C — required when Mission is Foundation-level |
| `Success-Criteria` | `pack-standard.md` §7.2 | R |
| `Exit-Conditions` | `pack-standard.md` §7.2 | R |
| `Programs` | `pack-standard.md` §7.2 | O |
| `Start-Date` | `pack-standard.md` §7.2 | C — required when Status is `In Progress` or later |

The Runtime validates the Mission input against the schema (per `schema-standard.md` §3 and §10 Mission sub-rules). A Mission input that fails validation halts the cycle (per §5.2 Stage 2).

### 6.3  Pack Input

| Field | Source | Required |
|---|---|---|
| `Pack-ID` | `pack-standard.md` §3.3 | R |
| `Version` | `pack-standard.md` §3.3 | R |
| `Pack-Type` | `pack-standard.md` §3.3 | R |
| `Scope` | `pack-standard.md` §3.4 | R |
| `Status` | `pack-standard.md` §4.1 | R |
| `FoundationVersion` | `pack-standard.md` §16.1 | R |
| `ConstitutionVersion` | `pack-standard.md` §16.1 | R |
| `Supersedes` | `pack-standard.md` §4.3 | R |
| `Dependencies` | `pack-standard.md` §15.1 | O (but validated when present) |
| `Path` | `pack-standard.md` §5.3 | R |

The Runtime validates the Pack input against the schema (per `schema-standard.md` §11 Pack Schema). A Pack input that fails validation halts the cycle (per §5.2 Stage 3).

### 6.4  Task Input

| Field | Source | Required |
|---|---|---|
| `Task-ID` | `schema-standard.md` §10.1 | R |
| `Pack-ID` | `pack-standard.md` §9.3 | R (when Task is in a Pack) |
| `Mission-ID` | `pack-standard.md` §9.3 | R (when Task is in a Mission) |
| `Program-ID` | `pack-standard.md` §9.3 | O |
| `Deliverables` | `pack-standard.md` §9.3 | R |
| `Verification-Method` | `schema-standard.md` §10.2 + `pack-standard.md` §10.2 | R |

The Runtime validates the Task input against the Task Schema (per `schema-standard.md` §10). A Task input that fails validation halts the cycle (per §5.2 Stage 6).

### 6.5  Schema Input

The Runtime accepts a **schema bundle** that declares the schemas the Runtime must enforce. The schema bundle is referenced by the Pack's `Schema-Version` field and resolves to a list of `schema-standard.md` §4–§12 schema references. The Runtime:

- Reads the schemas it must enforce.
- Verifies that every emitted artifact conforms to the relevant schema.
- Halts if a schema is missing, unreadable, or in a non-`Approved` / non-`Ratified` status.

The schema bundle does **not** contain a concrete serialization binding (per `schema-standard.md` §2). The Runtime is technology-neutral and may map the normative field specifications to a concrete form internally.

### 6.6  Governance Input

The Runtime accepts the **active governance state** as a governance input:

| Field | Source | Required |
|---|---|---|
| `Constitution Version` | `constitution.md` header | R |
| `Foundation Version` | `FOUNDATION/VERSION` | R |
| `Active FDs` | `FOUNDATION/09-Decisions/` | R — list of FDs with `Status: Ratified` |
| `Active Standards` | `FOUNDATION/03-Standards/` | R — list of Standards with `Status: Approved` or `Ratified` |
| `Active Policies` | `FOUNDATION/02-Governance/` | R — list of Policies with `Status: Approved` or `Ratified` |
| `Role Bindings` | `roles-and-authority.md` | R — current role-to-individual mapping |

The Runtime validates the governance input and halts if any required reference is missing or in an invalid status.

## 7. Runtime Output Specification

### 7.1  Overview

The Runtime produces five categories of outputs: **Artifacts**, **Audit**, **Reports**, **Reviews**, and **Status**. Every output conforms to the relevant `schema-standard.md` schema.

### 7.2  Artifacts

The Runtime emits the following artifact classes per `schema-standard.md` §4–§12:

| Class | Schema | When Emitted |
|---|---|---|
| Evidence | §4 | Stage 6 or Stage 7 |
| Statistics | §7 | Stage 7 (when the Task produces quantitative output) |
| Manifest | §8 | Stage 7 (when the Task produces a Manifest) |
| Task | §10 | Stage 7 (when the Task is a Pack-internal Task) |
| Pack | §11 | Stage 7 (when the cycle produces or modifies a Pack) |
| Release | §12 | Stage 7 (when the cycle produces a Release — restricted per §15.3) |
| Other | §13 (planned) | Stage 1 (Run record) |

Every emitted artifact carries:

- The `Pack-ID` and `Mission-ID` of the producing cycle (where applicable).
- The `Run-ID` of the producing Runtime cycle.
- A `Verification-Method` reference.
- An `Audit-Hook` reference (per `schema-standard.md` §9 Audit Hooks).

### 7.3  Audit

The Runtime emits an **Audit Report** per Stage 8 (§5.2). The Audit Report conforms to `schema-standard.md` §9 and includes:

- One `Finding` per Stage 1–7 audit observation.
- One `Finding` per Stage Transition (per §5.3).
- A §11 Quality Gate Verdict (`PASS`, `PASS with Notes`, `FAIL`).
- A `Pack-Audit-Verdict` when the cycle produces a Pack (per `pack-standard.md` §11.3).

### 7.4  Reports

The Runtime emits a **Task Report** per Stage 9 (§5.2). The Task Report conforms to `schema-standard.md` §5 and contains the eight sections:

1. Summary
2. Files Created
3. Files Modified
4. Acceptance Checklist
5. Verification
6. Remaining Limitations
7. Git Status
8. Next Recommended Task

### 7.5  Reviews

The Runtime emits a **Review Record** per Stage 10 (§5.2). The Review Record conforms to `schema-standard.md` §6 with `Disposition: Pending` until the human Architect supplies a disposition in Stage 11.

### 7.6  Status

The Runtime emits a **Status log** that records every transition through the Runtime Lifecycle. The Status log is itself an artifact of class `Other` (per `schema-standard.md` §13, planned) and records:

- `Run-ID`
- `Cycle-ID`
- `From-Stage` → `To-Stage`
- `At` (ISO-8601)
- `Actor` (human / Runtime / system)
- `Notes`

The Status log is **append-only** — a Runtime that edits or deletes Status entries is **Invalid**.

## 8. Quality Gate Integration

### 8.1  Validation Point

The Runtime applies the four §11 Quality Gate criteria at **every stage boundary**. A stage transition that fails any criterion produces an Audit `Finding` of severity `Minor` (cosmetic), `Major` (correctable), or `Critical` (halting).

| Criterion | Source | Applied At |
|---|---|---|
| Completeness | `constitution.md` §11.1 | Stages 2, 3, 6, 7, 9, 10 |
| Compliance | `constitution.md` §11.2 | Stages 2, 3, 4, 5, 7, 8 |
| Cross Reference | `constitution.md` §11.3 | Stages 2, 3, 4, 5, 6, 7, 9 |
| Isolation | `constitution.md` §11.4 | Stages 1, 4, 6 |

### 8.2  Failure Handling

A Runtime MUST handle failures as follows:

| Severity | Handling |
|---|---|
| `Minor` | Recorded in Audit; Runtime continues. |
| `Major` | Recorded in Audit; Runtime continues but emits a `Major` `Finding` row in the Audit Verdict; the `Acceptance Checklist` of the Report (`schema-standard.md` §5.3) is `unchecked` for the affected criterion. |
| `Critical` | Recorded in Audit; Runtime halts; the cycle does not proceed to Stage 11 until a human Architect supplies a disposition. |

A Runtime that suppresses a `Major` or `Critical` finding is **Invalid**. A Runtime that downgrades a `Critical` to `Minor` is **Invalid**.

### 8.3  Repair Cycle

A cycle whose disposition is `Changes Requested` or `Rejected` triggers a **Repair Cycle**:

1. The Runtime records the disposition in the Review Record (`Required Corrections` populated).
2. The Runtime emits an Audit Report for the failed cycle (per §5.2 Stage 8).
3. The Runtime halts; it does **not** auto-retry.
4. The Author issues a new Pack version (per `pack-standard.md` §16.2) or a revised Task declaration.
5. A new Runtime cycle is initiated by the Architect (with the corrected inputs).

A Runtime that auto-retries without a new cycle invocation is **Invalid**.

### 8.4  Approval Blocking

Stage 11 (Human Approval) is a **blocking gate**. The Runtime:

- Halts at Stage 11.
- Does not transition to Stage 12 until the human Architect supplies a disposition.
- Does not auto-resume on timeout, error, or any other signal.
- Does not bypass the gate, simulate the human, or pre-fill the disposition.

A Runtime that proceeds to Stage 12 without an explicit human disposition is **Invalid**.

## 9. Human-in-the-loop Model

### 9.1  Approval Boundary

The Runtime's approval boundary is **Stage 11** (per §5.2). Every Runtime cycle passes through Stage 11. The Architect's disposition determines:

- `Approved` or `Approved with Notes` → Runtime proceeds to Stage 12; affected artifacts transition to `Approved` status.
- `Changes Requested` → Runtime halts; Repair Cycle initiated (per §8.3).
- `Rejected` → Runtime halts; Mission transitions to `Closed` with `Exit-Status: Failure`.

### 9.2  Stop Condition

The Runtime MUST stop at the following conditions:

- After Stage 11 (every cycle) — until human disposition.
- After a `Critical` Audit finding (any stage) — until human disposition.
- After a `Rejected` Review disposition — terminal; no further cycles.
- On a `Constitution` or `Foundation Version` mismatch detected at Stage 4 — terminal.

The Runtime MUST NOT auto-resume past any stop condition.

### 9.3  Manual Override

The Architect may issue a **Manual Override** at any point in the cycle. A Manual Override:

- Is recorded in the Review Record's `Reviewer-Notes` field.
- Is signed (per `schema-standard.md` §6 `Signature` rule).
- Is acknowledged by the Runtime as an override of the normal Stage flow.

A Runtime that ignores a Manual Override is **Invalid**.

A Manual Override may NOT:

- Bypass the §11 Quality Gate (the Quality Gate is normative per `constitution.md` §11).
- Bypass a `Critical` finding (a `Critical` finding is halting per §8.2).
- Approve a Foundation-version change (per `constitution.md` §15.3).
- Approve a Pack-status transition that violates `governance-model.md` §7.

## 10. Runtime Security Boundary

### 10.1  Permission Scope

The Runtime's permission scope is **bounded** to:

| Permission | Scope |
|---|---|
| Read | Foundation artifacts in `FOUNDATION/`; project artifacts in `projects/`. |
| Write | New artifacts produced by the current cycle; Stage Transition Record. |
| Audit | Audit Report, Manifest, Stage Transition Record. |
| Status | Status log (append-only). |

The Runtime MAY **not**:

- Modify existing Foundation artifacts after they have entered `Approved` / `Ratified` status (immutability per `governance-model.md` §8).
- Modify `constitution.md`, `VERSION`, or any active FD / Standard / Policy (per `constitution.md` §15.3 Hard Prohibitions).
- Modify another Runtime's Audit Report, Manifest, or Stage Transition Record.
- Modify files outside `FOUNDATION/` (or its declared project subtree).

### 10.2  Forbidden Actions

The following actions are **forbidden** and a Runtime that performs any of them is **Invalid**:

1. **Executing arbitrary code.** The Runtime does not load or execute code at runtime; it interprets declarative Foundation artifacts.
2. **Spawning sub-processes.** The Runtime does not invoke shell commands, child processes, or external binaries.
3. **Network access.** The Runtime does not initiate outbound network connections.
4. **Auto-commit / auto-push.** The Runtime does not perform git operations; per `constitution.md` §15.3 and `governance-model.md` §10.
5. **Auto-approve.** The Runtime does not auto-approve any artifact; per §9.1.
6. **Self-modification.** The Runtime does not edit its own specification or implementation.
7. **Cross-Foundation-write.** The Runtime does not write to another Foundation's directory tree.
8. **Cross-Project-write.** The Runtime does not write to a Project subtree unless explicitly authorized by an FD.
9. **Code generation.** The Runtime does not generate executable code; per §3.3.
10. **Engine instantiation.** The Runtime does not instantiate Prompt / Audit / Evidence / Statistics / Report / Builder / any other Engine.
11. **MCP server instantiation.** The Runtime does not instantiate an MCP server.
12. **Agent delegation.** The Runtime does not delegate to sub-agents.
13. **SDK instantiation.** The Runtime does not instantiate an SDK or Plugin.
14. **Validator instantiation.** The Runtime does not invoke a validator module (validation is intrinsic to the Runtime's schema-conformance check; per §6.5).

### 10.3  Isolation Rules

The Runtime operates under three isolation rules:

1. **Cycle isolation.** Within a cycle, the Runtime MAY only access the inputs declared by §6 and the artifacts produced by Stages 1–10 of the same cycle. Cross-cycle access requires a new cycle invocation.
2. **Path isolation.** The Runtime writes only to paths declared in `directory-standard.md` §4. It does not write outside its declared scope.
3. **Project isolation.** The Runtime is project-independent; it does not assume any Project. Project-specific work requires the Project subtree and a per-Project Runtime profile (a downstream specification; not a Task 06 deliverable).

## 11. Runtime Compatibility

### 11.1  Version Surfaces

The Runtime declares three version surfaces:

- `Runtime.Version` — the Runtime Specification version (SemVer per `constitution.md` §8). Currently `0.1.0-draft`.
- `Runtime.FoundationVersion` — the Foundation version the Runtime is built against. Currently `0.1.0-dev`.
- `Runtime.ConstitutionVersion` — the Constitution version the Runtime is built against. Currently `v0.1.0-draft` Provisional.

A Runtime that targets a Foundation Version newer than its own is **Invalid**. A Runtime that targets a Constitution Version older than its own is **Invalid**.

### 11.2  Migration Rules

A Runtime that targets a newer Foundation Version than its inputs MUST emit a **Migration Plan**:

1. The Migration Plan enumerates every breaking change between the input's Foundation Version and the Runtime's Foundation Version.
2. The Migration Plan is stored at `FOUNDATION/03-Standards/runtime-specification.md` `MIGRATION-RUNTIME-<NN>.md` (planned).
3. The Migration Plan is bundled in the Pack's `migrations/` directory (per `pack-standard.md` §14.4).
4. The Migration Plan requires Architect approval (per `governance-model.md` §9 — Major change).

A Runtime that runs without a Migration Plan across a Foundation Version boundary is **Invalid**.

### 11.3  Future Extensions

Future extensions to the Runtime Specification MUST follow `constitution.md` §13 (Future Extension Policy):

- **Additive only.** New stages, new sub-components, new Audit Hooks, new Schema inputs may be added backward-compatibly.
- **Non-regression.** Existing requirements MUST continue to hold.
- **FD-driven.** Any extension that breaks backward compatibility requires an FD.

A Runtime that introduces a non-additive, non-FD-driven extension is **Invalid**.

### 11.4  Schema Standard Compatibility

The Runtime Specification MUST be updated whenever `schema-standard.md` adds a new schema class, removes a schema class, or changes a schema's required-field set. Such updates are recorded in `CHANGELOG.md` and reviewed by the Architect.

## 12. Cross References

### 12.1  Mandatory References (Constitution §10.1)

This Specification references:

- Constitution §1 (Governance Hierarchy)
- Constitution §2 (Compatibility Policy)
- Constitution §3 (Design Principles)
- Constitution §4 (Lifecycle Model)
- Constitution §6 (RFC Governance)
- Constitution §9 (Naming Convention)
- Constitution §10 (Cross Reference Policy)
- Constitution §11 (Quality Gate)
- Constitution §13 (Future Extension Policy)
- Constitution §14 (Success Criteria)
- Constitution §15 (Foundation Task Protocol)

### 12.2  Companion Standards and Policies

- `FOUNDATION/03-Standards/directory-standard.md` — per-class storage paths (§4); reserved directories (§8); path-mutation rules (§9); path-validation rules (§10).
- `FOUNDATION/03-Standards/schema-standard.md` — Evidence (§4), Report (§5), Review (§6), Statistics (§7), Manifest (§8), Audit (§9), Task (§10), Pack (§11), Release (§12).
- `FOUNDATION/03-Standards/pack-standard.md` — Pack lifecycle (§4), Pack structure (§5), Manifest rules (§6), Mission (§7), Program (§8), Task (§9), Deliverable (§10), Audit/Review/Report hooks (§11–§13), Artifact management (§14), Dependency rules (§15), Versioning rules (§16), Quality Gate (§17).
- `FOUNDATION/02-Governance/governance-model.md` §6 — Artifact Types.
- `FOUNDATION/02-Governance/governance-model.md` §7 — Governance Status Lifecycle.
- `FOUNDATION/02-Governance/governance-model.md` §8 — Immutability.
- `FOUNDATION/02-Governance/governance-model.md` §9 — Supersession.
- `FOUNDATION/02-Governance/governance-model.md` §13 — Additive-only extensions.
- `FOUNDATION/02-Governance/approval-workflow.md` — Status transition authority.
- `FOUNDATION/02-Governance/change-control-policy.md` — Mutation rules.
- `FOUNDATION/02-Governance/disagreement-and-escalation.md` — Disputes.
- `FOUNDATION/02-Governance/roles-and-authority.md` — Role assignments.
- `FOUNDATION/08-RFCs/rfc-policy.md` — RFC schema inputs.
- `FOUNDATION/09-Decisions/foundation-decision-policy.md` — FD schema inputs.
- `FOUNDATION/10-ADRs/adr-policy.md` — ADR schema inputs.

### 12.3  Back-References

A Runtime implementation that conforms to this Specification should reference this Specification in its documentation:

```
Conforms to: Builder Runtime Specification v0.1.0-draft (FOUNDATION/03-Standards/runtime-specification.md)
```

## 13. Relationship to Other Artifacts

- **Constitution §15 (Foundation Task Protocol).** The Runtime operationalizes the §15 Task protocol — Initialize → … → Continue/Stop.
- **Pack Standard.** The Runtime is the executor of the Pack form. The Pack declares *what*; the Runtime declares *how*.
- **Schema Standard.** Every artifact the Runtime emits conforms to a `schema-standard.md` schema.
- **Directory Standard.** Every artifact the Runtime writes goes to a path declared in `directory-standard.md` §4.
- **Governance Model.** The Runtime's Status log is a projection of `governance-model.md` §7 onto a single cycle.
- **Constitution §11 (Quality Gate).** The Runtime's Quality Gate Integration (§8) is the operational form of §11.
- **Constitution §14 (Success Criteria).** A Runtime that completes a cycle contributes to the Foundation Success Criteria; the Runtime itself is not a Success Criterion.
- **Change-Control Policy.** A Runtime Specification amendment is a Major change and requires an FD.

## 14. Ratification

This Builder Runtime Specification is itself **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred** — no `FD-0006-ratify-runtime-specification.md` is created in Task 06. The Foundation Builder prepares the Specification; the human Architect reviews it via `REVIEW-FOUNDATION-06-runtime.md`.

A future FD may ratify or supersede this Specification only if required by the Constitution, a later approved governance decision, or the Task 12 Foundation RC review. Until any such FD is issued, this Specification governs Foundation work **provisionally**, alongside the Provisional Constitution, the Task 02 Governance Model, the Task 03 Directory Standard, the Task 04 Schema Standard, and the Task 05 Pack Standard.

> Note: No `FD-0006-ratify-runtime-specification.md` is created during Task 06. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action.
>
> Note: No `runtime/` directory, no runtime source code, no CLI, no scripts, no agents, no MCP server, no SDK, no plugins, no engines, no validators, no Pack execution, and no APES files are created during Task 06. The Task 06 deliverable is the Specification; the first Runtime implementation is a future deliverable.

---

*End of Builder Runtime Specification v0.1.0-draft.*