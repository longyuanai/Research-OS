# Research-OS Foundation — Workspace Specification

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/workspace-specification.md`
**Supersedes:** none
**Related:** Constitution §3 (Design Principles); §4 (Lifecycle Model); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); `governance-model.md` §2 (Hierarchy), §6 (Artifact Types), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession), §13 (Additive-only extensions); `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `directory-standard.md` §4, §6, §8, §10; `schema-standard.md` §4–§12; `pack-standard.md` §3–§17 (Builder Pack — the Workspace is the Pack's operational surface); `runtime-specification.md` §4 (Runtime Architecture), §5 (Runtime Lifecycle), §6 (Runtime Input Specification), §7 (Runtime Output Specification), §8 (Quality Gate Integration), §9 (Human-in-the-loop Model), §10 (Runtime Security Boundary), §11 (Runtime Compatibility); `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship), §7 (Review Relationship), §8 (Failure Handling), §9 (Release Quality Gate), §10 (Compatibility); `engine-specification.md` §3–§11; `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture); `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model), §8 (Platform Plugin Specifications); `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard declares the canonical *form* of a Foundation **Workspace**: the L5 component that provides a **persistent, bounded, audited context** for a Builder Pack's execution under the Builder Runtime. A Workspace is the **operational surface** that the Builder Pack populates and the Runtime orchestrates. It is distinct from a Pack (which is *declarative*) and a Runtime (which is the *executor*) — the Workspace is the *persistent context* in which Pack-driven execution happens, and it is the unit at which Projects host their research activity.

This Standard:

1. Defines the **Workspace Architecture Purpose** (§2).
2. Defines the **Workspace Boundary Model** — where a Workspace terminates and the Foundation / other Workspaces / the host environment continue (§3).
3. Defines the **Workspace Lifecycle** — the eight ordered stages a Workspace traverses from request to archival (§4).
4. Defines the **Workspace Interface Specification** — Input Contract, Output Contract, Metadata, Versioning, Compatibility (§5).
5. Defines the **Workspace Permission and Security Model** — Workspace Permission set, Workspace Security Boundary, Human Approval Boundary, Isolation Rules (§6).
6. Defines the **Workspace Types** — Mission Workspace, Project Workspace, Foundation Workspace, including their differences, their relationship to Foundation Standards, and their compatibility rules (§7).
7. Defines **Workspace Compatibility** — Version compatibility, Migration rules, Extension rules, Cross-Workspace interaction rules (§8).

This Standard does **not** implement any Workspace. It does **not** create, instantiate, configure, allocate, or archive a Workspace. It does **not** create any on-disk Workspace directory tree. It does **not** execute any Pack. It does **not** instantiate any Runtime, Engine, SDK, or Plugin. It declares the *contract* a conformant Workspace specification must satisfy.

### §1.2 In-Scope

1. The **workspace architecture purpose** (§2).
2. The **workspace boundary model** — Workspace layer diagram, boundary rules, crossing points, relationship to Runtime and Engine boundaries (§3).
3. The **workspace lifecycle** — eight stages: Request, Provision, Initialize, Activate, Execute, Audit, Deactivate, Archive (§4).
4. The **workspace interface specification** — Input Contract, Output Contract, Metadata, Versioning, Compatibility (§5).
5. The **workspace permission and security model** — Workspace Permission set, Workspace Security Boundary, Human Approval Boundary, Isolation Rules (§6).
6. The **workspace types** — Mission Workspace, Project Workspace, Foundation Workspace (§7).
7. The **workspace compatibility** rules — Version compatibility, Migration rules, Extension rules, Cross-Workspace interaction rules (§8).
8. Cross-references to Constitution, Standards, and Policies (§9).
9. Relationship to Constitution, other Standards, and future artifacts (§10).

### §1.3 Out-of-Scope

1. **Workspace implementation** — no Workspace source code, no Workspace initialization script, no Workspace template directory, no on-disk Workspace directory tree.
2. **Workspace creation, instantiation, provisioning, allocation** — no `workspace create`, no `workspace init`, no `workspace clone`, no workspace template instantiation.
3. **Workspace execution** — no Pack execution inside a Workspace; no Runtime cycle invocation; no Mission execution; no Task execution; no Deliverable production.
4. **Network access** — no live calls to any host platform; no endpoint URLs in normative clauses; no secrets in repository.
5. **Engine / Runtime / SDK / Plugin implementation** — these remain downstream deliverables; the Workspace Specification references them contractually only.
6. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts.
7. **APES migration or Project-specific governance** — APES remains a paused Project.
8. **Sprint execution** — no Sprint is executed in this Foundation task.
9. **No git operations** — per the Architect's prohibition and the Foundation invariant.

---

## §2. Workspace Architecture Purpose

### §2.1 Definition

A **Workspace** is a Foundation L5 component that:

- Provides a **persistent, bounded, audited context** in which a Builder Pack is executed by a Builder Runtime.
- Holds the **Workspace Manifest**, the **Audit history**, the **Evidence records**, and the **Status log** for a single Mission or a single Project.
- Declares an explicit **Workspace Permission set** (least-privilege by default).
- Passes through **eight Lifecycle stages** (§4) — Request → Provision → Initialize → Activate → Execute → Audit → Deactivate → Archive.
- Is **technology-neutral** in specification; the **technology mapping** is downstream.
- Is **project-independent** during the Foundation phase; a Workspace MAY be issued for a Project post-Foundation, but no Workspace is Project-specific during the Foundation phase.

### §2.2 What a Workspace IS

A Workspace IS:

- a **persistent context** — it survives across multiple Runtime cycles within its declared Mission or Project;
- a **bounded context** — its boundary is declared and audited; no Workspace crosses into another Workspace's declared scope;
- an **audited context** — every Workspace state transition produces an Audit hook;
- a **human-gated context** — Provision and Deactivate require human disposition;
- a **declarative-driven context** — the Pack populates the Workspace; the Runtime orchestrates the Pack within the Workspace;
- a **fail-closed context** — a Workspace with unresolved Boundary violations, unresolved Permissions, or unresolved Audit findings cannot transition;
- a **technology-mappable but technology-neutral spec** — a Workspace is declared in natural-language contract; a concrete implementation maps the contract to a host environment post-Foundation;
- a **lifecycle-bounded instance** — every Workspace instance traverses the eight Lifecycle stages with explicit transitions and Audit hooks.

### §2.3 What a Workspace IS NOT

A Workspace IS NOT:

- a **Foundation Pack** — Packs are declarative bundles; Workspaces are operational contexts (per `pack-standard.md` §3).
- a **Builder Runtime** — Runtimes are executors; Workspaces are contexts (per `runtime-specification.md` §3).
- a **Foundation Engine** — Engines are L5 components inside the Foundation trust boundary; Workspaces are L5 contexts that may host Pack-driven execution (per `engine-specification.md` §3).
- a **Foundation SDK** — SDKs are interface contracts; Workspaces are operational contexts (per `sdk-specification.md` §7).
- a **Foundation Plugin** — Plugins are external adapters that cross third-party trust boundaries; Workspaces do not cross third-party trust boundaries (per `plugin-specification.md` §2).
- a **Project** — a Workspace MAY be issued *for* a Project, but a Workspace is not itself a Project.
- a **Mission** — a Workspace MAY *host* a Mission, but a Workspace is not itself a Mission (per `pack-standard.md` §7.2).
- a **Host environment** — the host environment (the OS, the filesystem, the network, the cloud account) is upstream of the Workspace; the Workspace is the bounded context the host provides.
- an **autonomous decision-maker** — every Workspace transition requires human Approval (per §4 and §6).
- a **trust conduit** — a Workspace does not forward Foundation credentials between Workspaces or to a Project (per §6).
- a **Project-specific scope** during the Foundation phase — no Workspace is owned by any Project; APES (the first Project) MAY consume a Workspace post-Foundation, but no Workspace defined here is APES-specific.

### §2.4 Relationship to Pack, Runtime, Engine, SDK, Plugin

| Component | Role | Relationship to Workspace |
|---|---|---|
| Pack (`pack-standard.md`) | Declarative bundle | The Workspace is the operational surface the Pack populates |
| Runtime (`runtime-specification.md`) | Executor | The Runtime orchestrates Pack execution *inside* a Workspace |
| Engine (`engine-specification.md`) | Specialist | Engines are invoked by the Runtime *inside* a Workspace to perform declared operations |
| SDK (`sdk-specification.md`) | Interface contract | SDKs are how Workspaces and their inhabitants (Runtimes, Engines, Plugins) interact with Foundation interfaces |
| Plugin (`plugin-specification.md`) | External adapter | Plugins MAY be invoked from a Workspace via the Plugin SDK and Runtime mediation |

The Workspace is the **outer context**. The Pack is the **declarative content**. The Runtime is the **executor**. The Engines are **specialists**. The SDKs are **interfaces**. The Plugins are **external adapters**.

---

## §3. Workspace Boundary Model

### §3.1 Boundary Layers

The Workspace Boundary is **layered**. From the host environment inward:

```
┌────────────────────────────────────────────┐
│ Host Environment                           │   ← upstream of Foundation (OS, FS, network, cloud)
├────────────────────────────────────────────┤
│ Workspace Physical Boundary                │   ← on-disk directory / namespace / container
│ (storage allocation, mount points)         │
├────────────────────────────────────────────┤
│ Workspace Manifest Boundary                │   ← what the Workspace declares as in-scope
│ (Manifest entries, declared permissions)   │
├────────────────────────────────────────────┤
│ Workspace Operational Boundary             │   ← what the Workspace may execute
│ (Runtime cycles, Engine invocations,       │
│  Pack execution, Audit hooks)              │
├────────────────────────────────────────────┤
│ Pack Content Boundary                      │   ← what the Pack contains (per pack-standard.md)
│ (Mission, Programs, Tasks, Deliverables)   │
├────────────────────────────────────────────┤
│ Foundation Storage                         │   ← Foundation artifact storage (per directory-standard.md)
└────────────────────────────────────────────┘
```

### §3.2 Boundary Rules

1. A Workspace integrates with the Foundation **only** through the Runtime and the Plugin SDK Interface Boundary; direct file system access, network access, or code execution outside the Boundary is **forbidden**.
2. A Workspace SHALL declare its requested Permissions (per §6); the Foundation grants Permissions on a **least-privilege** basis.
3. A Workspace SHALL NOT modify Foundation artifacts outside its declared Scope (§5.1); modification is mediated by the Runtime and recorded in an Audit hook.
4. A Workspace SHALL NOT invoke Foundation components directly; invocation is mediated by the Runtime (per `runtime-specification.md` §4).
5. A Workspace SHALL NOT extend the Foundation Interface Boundary unilaterally; extensions require a Workspace Specification amendment.
6. A Workspace SHALL NOT relay Foundation credentials, tokens, or secrets to another Workspace, a Project, or a host beyond what the Permission set expressly authorizes (per §6).
7. A Workspace SHALL NOT permit the host to invoke Foundation components without first passing the Runtime's Audit hook.
8. A Workspace SHALL NOT permit another Workspace to read or modify its content without an explicit Cross-Workspace interaction Permission (§6, §8.4).
9. A Workspace SHALL NOT bypass the six Foundation Quality Gates (per `quality-gate-standard.md` §5.2); every Workspace Lifecycle stage is gated.
10. A Workspace SHALL be **bounded**: its declared Scope, declared Permission set, declared Lifecycle stage, and declared Manifest shall together exhaustively describe what the Workspace contains and what it may do.

### §3.3 Boundary Crossing Points

Only the following Boundary crossings are permitted:

| Direction | Mediator | Recorded As |
|---|---|---|
| Host environment → Workspace (input event) | Workspace Manifest | Workspace Audit hook |
| Workspace → Runtime (input) | Workspace Manifest + Runtime Interface | Runtime Audit hook + Workspace Audit hook |
| Runtime → Workspace (output) | Runtime Interface | Workspace Audit hook |
| Runtime → Foundation Storage | Runtime + Directory Standard | Manifest entry + Audit hook |
| Foundation Storage → Workspace (read-back) | Runtime | Workspace Audit hook |
| Workspace → Pack Content (read) | Pack Manifest | Workspace Audit hook |
| Engine → Workspace (output) | Runtime + Engine Interface | Engine Audit hook + Workspace Audit hook |
| Plugin → Workspace (output) | Runtime + Plugin SDK | Plugin Audit hook + Workspace Audit hook |
| Workspace → Host environment (response) | Workspace Physical Boundary | Workspace Audit hook |

A Boundary crossing that is not mediated by the indicated component, or that is not recorded as indicated, is a **Boundary violation** (per §6 and `quality-gate-standard.md` §5.3.6).

### §3.4 Boundary to Pack, Runtime, Engine, SDK, Plugin Specs

This Standard **references** but does **not duplicate**:

- `pack-standard.md` §3 (Pack Definition), §5 (Pack Structure), §6 (Manifest rules), §7 (Mission), §9 (Task), §10 (Deliverable), §15 (Dependency rules), §16 (Versioning).
- `runtime-specification.md` §4 (Runtime Architecture), §5 (Runtime Lifecycle), §6 (Runtime Input Specification), §7 (Runtime Output Specification), §8 (Quality Gate Integration), §9 (Human-in-the-loop Model), §10 (Runtime Security Boundary), §11 (Runtime Compatibility).
- `engine-specification.md` §3–§11.
- `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture).
- `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model).

This Standard focuses on the Workspace's persistent, bounded, audited context. Wherever this Standard and another Foundation Standard appear to overlap, the more-specific Standard prevails for the overlap zone, after cross-reference check (per `governance-model.md` §4 Conflict Resolution).

---

## §4. Workspace Lifecycle

### §4.1 Overview

Every Workspace instance traverses **eight ordered stages**. A Workspace may not skip a stage. A Workspace may not transition with an unresolved failure, ungranted Permission, or unaudited operation.

```
Request → Provision → Initialize → Activate → Execute → Audit → Deactivate → Archive
```

### §4.2 Stage 1 — Request

**Purpose:** Declare the Workspace's intended existence, identity, type, scope, and intended Mission or Project.

**Subject state:** `Unrequested`.

**Inputs:**
1. Workspace identity (`§5.3`) — Workspace ID, Workspace name, Workspace version, Workspace type (Mission / Project / Foundation per §7).
2. Workspace Scope Declaration (per §5.1 and §15.5 Per-Task Scope).
3. Workspace Manifest draft (natural-language declaration per `schema-standard.md` §8).

**Outputs:**
1. A `Workspace Request Record` (`WORKSPACE-<scope>-<slug>-request.md`) declaring the Workspace's identity, type, and intended Scope.

**Transition condition:** The Request Record passes the Structure Gate (per `quality-gate-standard.md` §5.3.1) and the Isolation Gate (§5.3.4).

**Forbidden at this stage:** Provision, Activation, Execution, Audit hook emission against Foundation storage.

### §4.3 Stage 2 — Provision

**Purpose:** Allocate the Workspace's physical boundary (storage path, declared scope, declared permissions, declared lifecycle stage). Provision is **gated by human Approval** — the Architect or the Builder (within scope) MUST sign the Provisioning request.

**Subject state:** `Requested` → `Provisioned`.

**Inputs:**
1. The Workspace Request Record (§4.2).
2. A signed Provisioning request (Architect or Builder within scope).
3. The Workspace's requested Permission set (§6).

**Outputs:**
1. A `Workspace Provisioning Record` (`WORKSPACE-<scope>-<slug>-provision.md`) recording the provisioning timestamp, the granted Permission set, the Workspace type, and the actor.
2. The Workspace's physical boundary is **declared** (a logical allocation, not an on-disk instantiation during the Foundation phase).

**Transition condition:** Signed Provisioning request + positive Stage-3 Validation report from a prior draft + granted Permission set.

**Forbidden at this stage:** Activation, Execution, Audit hook emission against Foundation storage.

### §4.4 Stage 3 — Initialize

**Purpose:** Prepare the Workspace for Activation by:
- Sealing the Workspace Manifest.
- Sealing the Permission set.
- Sealing the Lifecycle stage.
- Emitting a `Workspace Initialization Record`.

**Subject state:** `Provisioned` → `Initialized`.

**Inputs:**
1. The Workspace Provisioning Record.
2. The sealed Manifest.
3. The sealed Permission set.
4. The sealed Lifecycle stage declaration (`Initialized`).

**Outputs:**
1. A `Workspace Initialization Record` (`WORKSPACE-<scope>-<slug>-initialize.md`) recording the sealed Manifest, the sealed Permission set, and the actor.

**Transition condition:** Initialization Record signed + Manifest sealed + Permission set sealed.

**Forbidden at this stage:** Activation, Execution, Audit hook emission against Foundation storage (the Initialization hook is emitted but does not represent Pack activity).

### §4.5 Stage 4 — Activate

**Purpose:** Promote the Workspace from `Initialized` to `Active` so Pack execution may begin. Activation is **gated by human Approval** — the Architect or the Builder (within scope) MUST sign the Activation request.

**Subject state:** `Initialized` → `Active`.

**Inputs:**
1. The Workspace Initialization Record.
2. A signed Activation request (Architect or Builder within scope).

**Outputs:**
1. A `Workspace Activation Record` (`WORKSPACE-<scope>-<slug>-activation.md`) recording the activation timestamp, the granted Permission set, the Workspace type, the Foundation Version, and the actor.
2. The Workspace is registered as `Active`.

**Transition condition:** Signed Activation request + Workspace Initialization Record.

**Forbidden at this stage:** Execution before Audit hook infrastructure is reachable.

### §4.6 Stage 5 — Execute

**Purpose:** Pack execution happens inside the Workspace. The Workspace hosts Runtime cycles, Engine invocations, and Plugin invocations, each of which is mediated by the Runtime and recorded in the Workspace's Audit history.

**Subject state:** `Active` → `Executing`.

**Inputs:**
1. Runtime cycle requests (declared by the Pack; mediated by the Runtime).
2. Engine invocation requests (declared by the Pack; mediated by the Runtime).
3. Plugin invocation requests (declared by the Pack; mediated by the Runtime and Plugin SDK).

**Outputs:**
1. Pack-driven operations (Read, Write, Audit, Manifest, Status) bounded by the granted Permission set.
2. **Audit hooks per operation** (per §6.4 and `schema-standard.md` §9).

**Transition condition:** Pack execution requests mediated by the Runtime + Audit hooks recorded per operation.

**Hard prohibitions during Execution:**
1. The Workspace SHALL NOT exceed its granted Permission set.
2. The Workspace SHALL NOT operate without an Audit hook pathway to Foundation Audit storage.
3. The Workspace SHALL NOT bypass the Runtime for any Foundation invocation.
4. The Workspace SHALL NOT permit the Pack, Runtime, Engine, or Plugin to operate outside the declared Scope.
5. The Workspace SHALL NOT auto-commit, auto-tag, or auto-push via git (per the Architect's prohibition and the Foundation invariant).
6. The Workspace SHALL NOT persist credentials across Activation cycles except via an explicit Credential Handling Rule (§6.6).

### §4.7 Stage 6 — Audit

**Purpose:** Verify that the Workspace's Execution history complies with the granted Permission set, the Security Boundary, and the six Foundation Quality Gates.

**Subject state:** `Executing` → `Audited`.

**Inputs:**
1. The Workspace's Audit hook stream.
2. The granted Permission set (from §4.3).
3. The Workspace's declared Scope (from §4.2).
4. The Pack's Mission (from the Pack content).

**Outputs:**
1. A `Workspace Audit Report` (`WORKSPACE-<scope>-<slug>-audit.md`) declaring per-operation outcomes against the six Gates and the Security Boundary.
2. Findings — observations, defects, near-misses.
3. Audit Verdict — `PASS`, `PASS with Notes`, `FAIL`, or `BLOCKED` (per `quality-gate-standard.md` §5.4).

**Frequency:** Audit MAY be continuous (every operation) or periodic (e.g., end-of-cycle), at the discretion of the Reviewer and per the Workspace type's cadence. Continuous Audit is preferred for high-Permission Workspaces.

**Transition condition:** Audit Verdict `PASS` returns the Workspace to `Active` for further Execution; `PASS with Notes` returns the Workspace to `Active` with recorded observations; `FAIL` advances the Workspace to `Deactivate` (§4.8); `BLOCKED` halts the Lifecycle pending Escalation.

### §4.8 Stage 7 — Deactivate

**Purpose:** Suspend the Workspace's Execution privileges while preserving its Audit history. Deactivation is **always permitted** (no Permission required to Deactivate).

**Subject state:** `Active / Audited` → `Deactivated`.

**Inputs:**
1. A signed `Deactivation Request` — by the Architect, the Builder (within scope), or the Reviewer.
2. Reason code — `Audit Failure`, `Permission Scope Violation`, `Boundary Violation`, `Operator Request`, `End of Mission`, `Security Incident`.

**Outputs:**
1. A `Workspace Deactivation Record` (`WORKSPACE-<scope>-<slug>-deactivate.md`) recording the reason, timestamp, and actor.
2. The Workspace's effective state is `Deactivated` — it cannot Execute; its Audit history is preserved.

**Transition condition:** Deactivation Request signed + Reason Code populated.

**Note:** Deactivation is **non-destructive** — the Workspace's prior Audit history, Manifest, Provisioning, Initialization, and Activation records are retained per `governance-model.md` §8 (Immutability) and `directory-standard.md` §4 (artifact retention).

### §4.9 Stage 8 — Archive

**Purpose:** Decommission the Workspace from the active Workspace Registry. Archival is a terminal action; the Workspace's records are retained per `governance-model.md` §8 (Immutability) and `directory-standard.md` (artifact retention), but the Workspace SHALL NOT be re-activated except via a new Request cycle (§4.2).

**Subject state:** `Deactivated` → `Archived`.

**Inputs:**
1. A signed `Archival Request` — by the human Architect or by an FD.
2. Reason code — `End of Mission`, `Project Decommissioned`, `Host Decommissioned`, `Security Incident`, `Capability Superseded`.

**Outputs:**
1. A `Workspace Archival Record` (`WORKSPACE-<scope>-<slug>-archive.md`) recording the reason, timestamp, and actor.
2. The Workspace is removed from the active Workspace Registry; the Audit history is retained.
3. The Workspace's Permission set is **revoked** — no residual Permission persists.

**Transition condition:** Archival Request signed + Reason Code populated + revocation of all granted Permissions recorded.

**Note:** Archival is **non-destructive of audit trail** — Archival preserves evidence; it disables future actions.

### §4.10 Stage Transition Table

| From | To | Trigger | Required Verdict |
|---|---|---|---|
| (none) | `Unrequested` | Request filed | n/a |
| `Unrequested` | `Requested` | Request Record filed | Structure Gate `PASS`; Isolation Gate `PASS` |
| `Requested` | `Provisioned` | Provisioning signed | Provisioning Gate `PASS` |
| `Provisioned` | `Initialized` | Initialization Record filed | Manifest sealed; Permission set sealed |
| `Initialized` | `Active` | Activation signed | Signed Activation + Initialization Record |
| `Active` | `Executing` | Pack / Runtime / Engine / Plugin invocation | Granted Permission invoked + Runtime mediation |
| `Executing` | `Audited` | Audit Report filed | Audit Verdict `PASS` or `PASS with Notes` |
| `Active` / `Audited` | `Deactivated` | Deactivation signed | Reason Code populated |
| `Deactivated` | `Archived` | Archival signed | Reason Code + Permission revocation |

### §4.11 Lifecycle Hooks Summary

| Hook | Stage | Required Artifact |
|---|---|---|
| `Workspace-Request-Hook` | 1 | Request Record |
| `Workspace-Provisioning-Hook` | 2 | Provisioning Record |
| `Workspace-Initialization-Hook` | 3 | Initialization Record |
| `Workspace-Activation-Hook` | 4 | Activation Record |
| `Workspace-Execution-Hook` | 5 | Per-operation Audit hook |
| `Workspace-Audit-Hook` | 6 | Audit Report |
| `Workspace-Deactivation-Hook` | 7 | Deactivation Record |
| `Workspace-Archival-Hook` | 8 | Archival Record |

A Workspace instance whose corresponding `*-Hook` is missing is **Invalid** at the relevant stage.

---

## §5. Workspace Interface Specification

### §5.1 Input Contract

A Workspace SHALL accept the following **Input Contract**:

1. **Workspace identity** — Workspace ID, Workspace name, Workspace version, Workspace type, Workspace vendor (per §5.3).
2. **Workspace Scope Declaration** — declared Allowed Operations, declared Forbidden Operations, declared Inputs, declared Outputs, declared Boundaries (mirrors `pack-standard.md` §15.5 Per-Task Scope).
3. **Workspace Permission request** — the Permission set the Workspace requests (per §6).
4. **Pack binding** — the Pack (per `pack-standard.md`) the Workspace will host. A Workspace without a Pack binding is `Empty` and MAY NOT Execute (§4.6).
5. **Foundation Version and Constitution Version** — the versions the Workspace is bound to.
6. **Runtime, Engine, SDK, Plugin references** — the L5 components the Workspace will host, each by declared identifier.

The Foundation SHALL reject any Workspace Input that does not satisfy the Input Contract. The Workspace SHALL reject any Input that does not arrive through the Runtime or Plugin SDK Interface Boundary.

### §5.2 Output Contract

A Workspace SHALL emit the following **Output Contract**:

1. **Workspace result** — the result of Pack execution (success, no-op, error). The result type is declared in the Workspace's Manifest entry (per `schema-standard.md` §8).
2. **Workspace Audit hook** (per `schema-standard.md` §9 and `runtime-specification.md` §7.3) — a structured record of every operation, declaring:
   - **Workspace-ID** and **Workspace-Version**.
   - **Operation** — the L5 component operation (Pack execution, Engine invocation, Plugin invocation, Runtime cycle).
   - **Permission-Invoked** — the granted Permission exercised.
   - **Input-Digest** — a stable digest of the Input (no Input content is recorded unless the operation explicitly declares it).
   - **Output-Digest** — a stable digest of the Output (same protection).
   - **Boundary-Clauses-Crossed** — the set of Boundary Rules (§3.2) exercised.
   - **Outcome** — `Success`, `No-Op`, `Error`, `Permission-Denied`, `Boundary-Violation`.
   - **Timestamp** — ISO-8601.
   - **Actor** — the L5 component (Pack, Runtime, Engine, Plugin).
3. **Workspace Manifest** — the Workspace's Manifest entry per `schema-standard.md` §8 (re-emitted on Activation and on Scope changes).
4. **Workspace Status** — the current Lifecycle stage (per §4) emitted on every transition.

The Foundation SHALL accept Audit hooks in the Output Contract form; an Audit hook missing any of the above fields is **Invalid** and triggers a Boundary Violation (§6).

### §5.3 Metadata

The Workspace's Metadata is the persistent descriptive payload that travels with the Workspace instance. Required fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `Workspace-ID` | R | string | Unique identifier; pattern `WORKSPACE-<scope>-<slug>` |
| `Workspace-Name` | R | string | Human-readable name |
| `Workspace-Version` | R | SemVer | Per Constitution §8 |
| `Workspace-Type` | R | enum:`mission`,`project`,`foundation` | The Workspace type (per §7) |
| `Workspace-Vendor` | R | string | Author/vendor identifier |
| `Workspace-Description` | R | string | One-paragraph human-readable description |
| `Workspace-Scope-Declaration` | R | Scope | Allowed / Forbidden Operations, Inputs, Outputs, Boundaries |
| `Workspace-Required-Permissions` | R | list:Permission | Requested Permissions (per §6) |
| `Workspace-Granted-Permissions` | R | list:Permission | Granted Permissions (post §4.3) |
| `Workspace-Pack-Binding` | R | string | Pack ID the Workspace hosts |
| `Workspace-Runtime-Reference` | R | string | Runtime identifier |
| `Workspace-Engine-References` | O | list:string | Engine identifiers the Workspace invokes |
| `Workspace-Plugin-References` | O | list:string | Plugin identifiers the Workspace invokes |
| `Workspace-SDK-Version` | R | SemVer | Targeted `sdk-specification.md` version |
| `Workspace-Foundation-Version` | R | SemVer | Targeted Foundation Version |
| `Workspace-Constitution-Version` | R | SemVer | Targeted Constitution Version |
| `Workspace-Compatibility-Profile` | R | Compatibility | Per §8 |
| `Workspace-Supersedes` | O | string | Previous Workspace ID (if superseding) |
| `Workspace-Superseded-By` | C | string | Set when superseded |

### §5.4 Versioning

- **Version surface:** `Workspace.Version`, `Workspace-SDK-Version`, `Workspace-Foundation-Version`, `Workspace-Constitution-Version`.
- **Bump triggers:**
  - **MAJOR** — non-backward-compatible Workspace scope change or Permission-set change.
  - **MINOR** — additive new Permission class within declared Scope; additive new Engine reference.
  - **PATCH** — typo fix, clarification, re-bind to a newer Foundation minor without Scope changes.
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Workspace RC), `1.0.0` (first Stable Workspace).
- **Foundation binding:** A Workspace SHALL NOT declare a Foundation Version newer than its Workspace-SDK-Version.

### §5.5 Compatibility

A Workspace's Compatibility Profile declares Compatibility with:

- **Foundation versions** — the Workspace's Workspace-Foundation-Version is its declared compatibility floor; compatible with `>= Workspace-Foundation-Version` and `< Workspace-SDK-Version.Major + 1`.
- **Constitution versions** — the Workspace SHALL NOT invoke clauses past its Workspace-Constitution-Version.
- **Host platform versions** — the Workspace declares the range of host platform versions it supports (technology-neutral).
- **Plugin-SDK versions** — the Workspace SHALL be compatible with the Plugin-SDK Version recorded in its Manifest; new SDK versions require a new Workspace Version (per §8.3).

---

## §6. Workspace Permission and Security Model

### §6.1 Overview

The Workspace Permission Model binds Workspace operations to **explicitly granted capabilities**. Permissions are **default-denied**; a Permission is granted only when a Reviewer records an explicit grant in the Provisioning Record (§4.3) and the Activation Record (§4.5). The Foundation honors **least-privilege**: a Workspace receives no Permission it does not request, and every requested Permission is reviewed individually.

### §6.2 Allowed Access

The following Permissions MAY be granted. Each is granted individually; **no Permission is implicit from another**.

| # | Permission | Description |
|---|---|---|
| 1 | `Read Foundation Artifacts` | Read-only access to designated Foundation files via Runtime mediation |
| 2 | `Emit Evidence` | Produce Evidence records (per `schema-standard.md` §4) on behalf of the Pack |
| 3 | `Emit Audit` | Produce Audit hooks (per §5.2 and `schema-standard.md` §9) |
| 4 | `Invoke Runtime-mediated Components` | Invoke Foundation components (Runtime, Engine, Plugin, SDK) via the Runtime |
| 5 | `Host Pack Execution` | Host the execution of a bound Pack (per `pack-standard.md`) |
| 6 | `Write Workspace Local State` | Write to a designated, scoped Workspace-local store (no Foundation artifact modification) |
| 7 | `Read Pack Content` | Read the content of the bound Pack (per `pack-standard.md` §5) |

### §6.3 Restricted Access

The following Permissions are **restricted** — they MAY be granted only with explicit human Approval and additional Security Boundary controls. None are granted by default.

| # | Permission | Restriction |
|---|---|---|
| 8 | `Restricted Network Access` | Granted only with declared endpoints, declared request shapes, declared authentication method, and Audit on every request |
| 9 | `Restricted Code Execution` | Granted only with declared execution envelope (sandbox scope) and Audit on every invocation |
| 10 | `Restricted File System Access` | Granted only with declared paths (read and/or write), per-path Audit, and per-path declaration |
| 11 | `Restricted Git Operations` | Granted only with declared git verb(s) and an external Approval hook before each invocation (per the Architect's prohibition and the Foundation invariant) |
| 12 | `Restricted Credential Forwarding` | Granted only with declared forwarding target, declared credential scope, and on-hook Audit; the Foundation SHALL redact secret material in Audit hooks (§6.6) |
| 13 | `Restricted Foundation Write` | Granted only for declared Foundation artifact classes (e.g., Evidence, Audit) and only via the Runtime-mediated write path |
| 14 | `Restricted Cross-Workspace Interaction` | Granted only with declared target Workspace ID, declared operation type, and per-operation Audit (§8.4) |

### §6.4 Default-Denied Permissions

The following Permissions are **default-denied**. A Permission Approval Record MAY grant them, but the Foundation treats them as restricted:

- `Network Access (unrestricted)` — denied unless the Restricted Permission is granted with declared endpoints.
- `Code Execution (unrestricted)` — denied unless the Restricted Permission is granted with declared envelope.
- `File System Writes Outside Scope` — denied unless the Restricted Permission is granted with declared paths.
- `Git Operations` — denied unless the Restricted Permission is granted with declared verbs and external Approval.
- `Credential Forwarding` — denied unless the Restricted Permission is granted with declared target and scope.
- `Foundation Artifact Modification` — denied; Workspaces modify Foundation artifacts only through `Restricted Foundation Write` and only via the Runtime-mediated path.
- `Cross-Workspace Interaction` — denied unless the Restricted Permission is granted with declared target Workspace.

### §6.5 Human Approval Boundary

The Human Approval Boundary is enforced at:

1. **Provisioning (§4.3)** — Architect or Builder (within scope) signs the Provisioning Request.
2. **Activation (§4.5)** — Architect or Builder (within scope) signs the Activation Request.
3. **Deactivation (§4.8)** — Architect, Builder (within scope), or Reviewer signs the Deactivation Request.
4. **Archival (§4.9)** — Architect or FD signs the Archival Request.

The Foundation's refusal to honor any Permission not listed as `Granted` (or `Granted with Conditions` whose conditions are satisfied) is enforced by the Runtime (per `runtime-specification.md` §10.1).

No machine, automation, or CI/CD pipeline may substitute for the human Reviewer at any boundary (per Constitution §5 and `quality-gate-standard.md` §7.4).

### §6.6 Isolation Rules

1. A Workspace SHALL operate only within its granted Permission set.
2. A Workspace SHALL NOT share state with another Workspace unless an explicit `Cross-Workspace Interaction` Permission has been granted and the other Workspace is identified by ID in the Permission grant.
3. A Workspace SHALL NOT read or write Foundation artifacts outside its declared Scope (§5.1).
4. A Workspace SHALL NOT forward Foundation credentials, tokens, or secrets to another Workspace, a Project, or a host except as permitted by §6 and a granted `Restricted Credential Forwarding` Permission.
5. A Workspace SHALL NOT bypass the Runtime for any Foundation invocation.
6. A Workspace SHALL NOT install, configure, or activate another Workspace; only the Architect, the Builder (within scope), or an FD may issue Request, Provisioning, Initialization, Activation, Deactivation, or Archival requests.
7. A Workspace's Audit history SHALL remain isolated from other Workspaces' Audit histories; only the Architect, the Reviewer, and the Auditor may view cross-Workspace Audit.
8. A Workspace SHALL NOT execute a Pack whose `FoundationVersion` or `ConstitutionVersion` is newer than the Workspace's own.
9. A Workspace SHALL NOT execute a Pack whose declared Scope exceeds the Workspace's declared Scope.
10. A Workspace SHALL honor the Runtime Security Boundary (per `runtime-specification.md` §10) and the Plugin Security Boundary (per `plugin-specification.md` §7).

### §6.7 Credential Handling Rules

1. **Default rule.** Credentials are **default-denied**. A Workspace SHALL NOT request, capture, store, or forward credentials except under an explicit `Restricted Credential Forwarding` Permission.
2. **No secret material in Audit hooks.** The Workspace SHALL NOT record secret-bearing fields in Audit hooks; the Audit hook records `digest` and `redacted-flag` only.
3. **Credential isolation.** A Workspace's granted credentials are scoped to the Permission; the Foundation SHALL NOT reuse credentials across Permissions, Workspaces, or Projects.
4. **Credential rotation.** A Workspace SHALL NOT rotate Foundation-managed credentials; rotation is a Foundation-level operation mediated by the Runtime and gated by a signed Review Record.
5. **Credential revocation.** Deactivation (§4.8) and Archival (§4.9) of a Workspace revoke all granted credential Permissions; no residual credential access persists.
6. **No credential exfiltration.** The Workspace SHALL NOT relay Foundation credentials to a third-party host beyond what the Permission set expressly authorizes; exfiltration is a Security Incident.

### §6.8 Security Boundary

The Workspace's Security Boundary inherits and operationalizes:

- The Foundation Trust Boundary (Constitution §3 — Specification before Implementation; Foundation before Project).
- The Runtime Security Boundary (`runtime-specification.md` §10).
- The Plugin Security Boundary (`plugin-specification.md` §7).
- The Quality Gate Security Boundary (`quality-gate-standard.md` §5.3.6).

A Workspace that introduces a Boundary violation is **Invalid** and is returned to the Deactivation or Audit stage as appropriate.

---

## §7. Workspace Types

### §7.0 Overview

This section specifies the **three concrete Workspace Types** recognized by the Foundation:

1. **Mission Workspace** — hosts a single Builder Pack's Mission execution.
2. **Project Workspace** — hosts a single Project's research activity (post-Foundation).
3. **Foundation Workspace** — hosts Foundation-level work (Standards drafting, Decisions, RFCs).

The three Workspace Types are **co-equal in specification**; each conforms to this Standard, the Runtime Specification, and the Quality Gate Standard. The differences between them are **declared scope, declared permission set, and declared lifecycle cadence** — not normative precedence.

During the Foundation phase:

- **Mission Workspace** is the typical form for Foundation Task execution (Task 03 through Task 12 of the 12-Task Foundation sequence).
- **Project Workspace** is **not instantiated** during the Foundation phase; APES (the first Project) MAY consume a Project Workspace post-Foundation, but no Project Workspace is defined or populated here.
- **Foundation Workspace** is the typical form for Foundation-level Standards drafting.

### §7.1 Mission Workspace

**Purpose.** Hosts a single Builder Pack's Mission execution. A Mission Workspace is **bounded by a single Mission** and is **decommissioned when the Mission closes** (per `pack-standard.md` §7.2 Exit-Conditions).

**Lifecycle cadence.** Short — typically one to twelve Runtime cycles (per `runtime-specification.md` §5.1) bounded by the Mission.

**Permission set.** Default set:
- `Read Foundation Artifacts` (granted).
- `Emit Evidence` (granted).
- `Emit Audit` (granted).
- `Invoke Runtime-mediated Components` (granted).
- `Host Pack Execution` (granted).
- `Read Pack Content` (granted).
- `Write Workspace Local State` (granted).
- All other Permissions — default-denied.

**Archival rule.** A Mission Workspace is archived when the Mission's `Exit-Conditions` are met (per `pack-standard.md` §7.2) or when the Mission is `Closed`.

**Foundation-phase applicability.** Mission Workspace is the typical form for Foundation Task execution. The Workspace Specification itself is a Mission Workspace output for Task 11.

### §7.2 Project Workspace

**Purpose.** Hosts a single Project's research activity post-Foundation. A Project Workspace is **bounded by the Project's declared scope** (per Project governance, downstream).

**Lifecycle cadence.** Long — typically spans multiple Missions across the Project's lifetime.

**Permission set.** Default set (extends Mission Workspace defaults):
- All Mission Workspace default Permissions.
- `Restricted Foundation Write` (granted, for declared artifact classes only).
- `Restricted Cross-Workspace Interaction` (granted, for declared target Workspaces only).
- All other Permissions — default-denied.

**Archival rule.** A Project Workspace is archived when the Project is `Decommissioned` (per Project governance, downstream).

**Foundation-phase applicability.** Project Workspace is **not instantiated during the Foundation phase**. The Workspace Specification declares the Project Workspace's contract; Project Workspaces are populated post-Foundation.

### §7.3 Foundation Workspace

**Purpose.** Hosts Foundation-level work — Standards drafting, FDs, RFCs, ADRs. A Foundation Workspace is **bounded by the Foundation's declared scope** (per Constitution §1, §3, §15).

**Lifecycle cadence.** Long — typically spans multiple Foundation cycles across the Foundation's lifetime.

**Permission set.** Default set (extends Mission Workspace defaults):
- All Mission Workspace default Permissions.
- `Restricted Foundation Write` (granted, for declared Foundation artifact classes — Standards, FDs, RFCs, ADRs).
- `Restricted Cross-Workspace Interaction` (granted, for declared target Workspaces only).
- All other Permissions — default-denied.

**Archival rule.** A Foundation Workspace is archived when the Foundation is `Decommissioned` (a constitutional event, per Constitution §17).

**Foundation-phase applicability.** Foundation Workspace is the typical form for Foundation-level work. The Workspace Specification itself is hosted by a Foundation Workspace for Task 11.

### §7.4 Cross-Workspace Interaction Rules

Cross-Workspace Interaction is **default-denied**. A Workspace MAY interact with another Workspace only when:

1. The requesting Workspace holds a granted `Restricted Cross-Workspace Interaction` Permission (§6.3) naming the target Workspace by ID.
2. The target Workspace is in the `Active` or `Executing` Lifecycle stage (§4).
3. The interaction is mediated by the Runtime (per `runtime-specification.md` §4 and §10).
4. Every interaction is recorded as an Audit hook on both the requesting and target Workspace.
5. The interaction does not cross a third-party trust boundary (a Plugin is required for third-party boundary crossings, per `plugin-specification.md` §3.4).

Foundation-phase rule: **no Cross-Workspace Interaction occurs** during the Foundation phase (per `foundation-invariant-2026-08-03.md` — five constraints preserved until Task 12).

---

## §8. Workspace Compatibility

### §8.1 Version Compatibility

A Workspace declares its Compatibility Profile (§5.3). Compatibility is enforced as:

- **Foundation-version compatibility.** A Workspace bound to `Workspace-Foundation-Version = X.Y.Z` is compatible with Foundation versions `>= X.Y.Z` and `< (Workspace-SDK-Version.Major).0.0`.
- **Constitution-version compatibility.** A Workspace SHALL NOT invoke clauses past its `Workspace-Constitution-Version`.
- **Plugin-SDK-version compatibility.** A Workspace SHALL be compatible with the Plugin-SDK Version recorded in its Manifest; new SDK versions require a new Workspace Version.
- **Host-version compatibility.** A Workspace SHALL declare the host platform version range it supports.

### §8.2 Migration Rules

When a Workspace's compatibility breaks (e.g., a new Foundation Major version, a new Plugin SDK version, or a host platform breaking change), a **Workspace Migration Plan** is required. The Plan declares:

1. The previous Workspace Version.
2. The new Workspace Version.
3. The list of breaking changes (with locator and rationale).
4. The list of artifacts affected (the Workspace instance, its Request, Provisioning, Initialization, Activation, Audit history).
5. The Migration procedure (per-event re-validation, per-Permission re-grant, re-Activation).

The Plan is filed at a path recorded in `directory-standard.md` §4 (place-holder: `<workspace-root>/MIGRATION-<workspace-id>-<from>-<to>.md`). The Plan is reviewed per `change-control-policy.md` and requires the same Reviewer separation-of-duties rule.

### §8.3 Extension Rules

Per Constitution §13 (Future Extension Policy), Workspace extensions are **additive-only**:

- New Permissions — additive (a new Permission class may be defined by a new Workspace MINOR version, but the Foundation SHALL honor the existing default-deny rule for the new Permission class until explicitly granted).
- New Boundary crossing points — additive (new entries in §3.3 may be added by a new Workspace MINOR version).
- New Lifecycle stages — additive (a new stage may be inserted in §4 by a new Workspace MAJOR version, because it is a Protocol change).
- New Workspace Types — additive (a new Workspace Type may be defined by a new Workspace MAJOR version; Foundation declares the three Foundation-phase types at §7.1–§7.3).

**Weakening requires a new FD:**

- Removing an existing Permission from a granted Permission set.
- Lowering the Security Boundary (relaxing §6 constraints).
- Changing the Lifecycle to remove a stage.
- Re-classifying a default-denied Permission as default-allowed.
- Removing a Workspace Type.

### §8.4 Workspace Supersession

A Workspace MAY be superseded by a later Workspace. The supersession follows the rules in `governance-model.md` §9:

1. The new Workspace declares `Supersedes: <old-Workspace-ID>` in its Metadata (§5.3).
2. The old Workspace's Status is updated to `Superseded` (header-only edit; content untouched).
3. The old Workspace's `Superseded-By` Metadata field is populated with the new Workspace's ID.

A Superseded Workspace MAY NOT be re-activated except via a new Request cycle (§4.2) and a new Manifest version.

---

## §9. Cross References

Per Constitution §10 (Cross Reference Policy), this Standard declares the following mandatory references.

### §9.1 Constitution References

- §1 (Governance Hierarchy)
- §2 (Compatibility Policy)
- §3 (Design Principles)
- §4 (Lifecycle Model)
- §5 (Role Model)
- §6 (RFC Governance)
- §7 (Decision Records)
- §8 (Versioning Policy)
- §9 (Naming Convention)
- §10 (Cross Reference Policy)
- §11 (Quality Gate)
- §12 (Deprecation Policy)
- §13 (Future Extension Policy)
- §14 (Success Criteria)
- §15 (Foundation Task Protocol) — including §15.3 Hard Prohibitions, §15.4 Self-audit, §15.5 Per-Task Scope Declaration.

### §9.2 Standard References

- `directory-standard.md` §4 (top-level layout), §6 (per-class storage paths), §8 (reserved directories), §10 (path-validation).
- `schema-standard.md` §4 (Evidence), §5 (Report), §6 (Review), §7 (Statistics), §8 (Manifest), §9 (Audit), §10 (Task), §11 (Pack), §12 (Release).
- `pack-standard.md` §3 (Pack Definition), §4 (Pack Lifecycle), §5 (Pack Structure), §6 (Manifest rules), §7 (Mission), §8 (Program), §9 (Task), §10 (Deliverable), §11–§13 (Audit/Review/Report hooks), §15 (Dependency rules), §16 (Versioning).
- `runtime-specification.md` §4 (Runtime Architecture), §5 (Runtime Lifecycle), §6 (Runtime Input Specification), §7 (Runtime Output Specification), §8 (Quality Gate Integration), §9 (Human-in-the-loop Model), §10 (Runtime Security Boundary), §11 (Runtime Compatibility).
- `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship), §7 (Review Relationship), §8 (Failure Handling), §9 (Release Quality Gate), §10 (Compatibility).
- `engine-specification.md` §3–§11.
- `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture).
- `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model), §8 (Platform Plugin Specifications).

### §9.3 Policy References

- `governance-model.md` §2 (Hierarchy), §6 (Artifact Types), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession), §13 (Additive-only extensions).
- `approval-workflow.md`.
- `change-control-policy.md`.
- `disagreement-and-escalation.md`.
- `roles-and-authority.md`.
- `rfc-policy.md`.
- `foundation-decision-policy.md`.
- `adr-policy.md`.

### §9.4 Back-References

This Standard is referenced by:

- *Future Standards.* The Release Specification (Task 12) MAY reference this Standard.
- *Future Workspace instances.* A concrete Workspace instance (e.g., a future `WORKSPACE-foundation-workspace-spec.md`) SHALL reference this Standard, the Runtime Specification, and the Quality Gate Standard.
- *Future Pack instances.* A concrete Foundation Pack (Task 12 deliverable) MAY bundle the Workspace Specification.
- *Future Plugin instances.* Plugin instances hosted inside a Workspace SHALL reference this Standard.

---

## §10. Relationship to Other Artifacts

### §10.1 To the Constitution

This Standard operationalizes the Workspace concept for the Foundation, drawing on Constitution §§1, 3, 4, 5, 9, 10, 11, 12, 13, 15. It does not contradict any clause of the Constitution. If a future Constitution amendment changes a referenced §, this Standard must be updated to reflect the new clause (per `change-control-policy.md`).

### §10.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for Standards, Audits, Reports, and Reviews produced by this Standard.
- **Schema Standard** — declares the Evidence (§4), Audit (§9), Manifest (§8), Report (§5), Review (§6) schemas that this Standard references.
- **Pack Standard** — declares the Builder Pack that populates a Workspace. The Workspace is the operational surface; the Pack is the declarative content.
- **Runtime Specification** — declares the Runtime that orchestrates Pack execution inside a Workspace. The Runtime mediates every Workspace invocation.
- **Quality Gate Standard** — declares the six Gates that gate every Workspace Lifecycle stage.
- **Engine Specification** — declares the Engines (Builder, Audit, Evidence, Statistics, Report, Prompt) that are invoked inside a Workspace.
- **SDK Specification** — declares the Plugin SDK and Shared SDK Architecture that this Standard conforms to.
- **Plugin Specification** — declares the Plugin boundary that Workspaces honor when invoking Plugins.

### §10.3 To Future Artifacts

Future artifacts that may reference this Standard include:

- **Release Specification** (Task 12) — may declare how Workspaces integrate with a Release.
- **Foundation Pack instances** (Task 12) — may bundle this Standard and its companion Audit / Report / Review records.
- **Workspace instance specifications** (downstream, post-Foundation) — each Workspace instance SHALL reference this Standard.
- **Project Workspace instances** (downstream, post-Foundation) — issued by Projects; each SHALL reference this Standard and SHALL conform to the Project Workspace section.
- **Plugin instance specifications** (downstream) — Plugins hosted in a Workspace SHALL reference this Standard.

### §10.4 Workspace as Project-Independent Component

This Standard is **technology-neutral** and **project-independent**. No Workspace defined here is owned by any Project; no Workspace is restricted to any Project; no Project-local rule binds a Workspace during the Foundation phase. APES (the first Project) MAY consume a Foundation-defined Workspace post-Foundation, but no Foundation-defined Workspace is APES-specific.

During the Foundation phase, no Workspace is instantiated. The Workspace Specification declares the contract; the first Workspace instance is a future deliverable.

---

## §11. Ratification

This Standard is **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0011-ratify-workspace-specification.md` is created in this Foundation task.

**Ratification path (when invoked by a future Foundation cycle):**

1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition (`Approved`, `Approved with Notes`, `Rejected`, `Blocked`).
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0011-ratify-workspace-specification.md` per `foundation-decision-policy.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.
5. After Ratification, this Standard's `Status:` header field is updated to `Ratified` and its `Version:` may advance per §8.1.

Until `FD-0011` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

> **Note.** No `FD-0011-ratify-workspace-specification.md` is created during Task 11. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action. The Foundation Builder prepares this Standard and the companion Audit / Report / Review; the human Architect reviews it through `REVIEW-FOUNDATION-11-workspace.md`.

> **Note.** This Standard is **technology-neutral**, **project-independent**, and **implementation-independent**. It contains no Workspace source code, no Workspace template, no on-disk Workspace directory tree, no Workspace initialization script, no Pack execution, no Runtime instantiation, no Engine instantiation, no SDK instantiation, no Plugin instantiation, no Mission execution, no Task execution, no Deliverable production, no network endpoint, no credential capture, no sandbox implementation, no git operation, and no APES artifact. The three Workspace Types declared at §7.1–§7.3 are co-equal and contract-only.

> **Note.** Per the Foundation invariant (per memory `foundation-invariant-2026-08-03.md`), until Task 12 is complete the Foundation preserves five constraints: Foundation Version 0.1.0-dev; Constitution v0.1.0-draft Provisional; no RC; no Pack; no Project. The Workspace Specification does not violate any of these constraints.

---

*End of workspace-specification.md v0.1.0-draft (Draft / In Review).*