# Research-OS Foundation — Plugin Specification

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/plugin-specification.md`
**Supersedes:** none
**Related:** Constitution §3 (Design Principles); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); `governance-model.md` §2, §6, §7, §8; `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `directory-standard.md` §4, §6, §8, §10; `schema-standard.md` §4–§12; `pack-standard.md` §3–§17; `runtime-specification.md` §4, §6, §7, §8, §10, §11; `quality-gate-standard.md` §5, §6, §7, §8, §9, §10; `engine-specification.md` §3–§11; `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture); `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard declares the canonical *form* of a Foundation **Plugin**: the L5 component that adapts an external platform (e.g., GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) to the Foundation Interface Boundary declared in `sdk-specification.md` §7 (Plugin SDK). A Plugin is the *only* L5 component authorized to cross a **third-party trust boundary**; every other L5 component (Runtime, Engine, SDK, Workspace) operates inside the Foundation trust boundary.

This Standard:

1. Defines the **Plugin Architecture Purpose** (§2).
2. Defines the **Plugin Boundary Model** — where a Plugin terminates and the Foundation continues (§3).
3. Defines the **Plugin Lifecycle** — the nine ordered stages a Plugin instance traverses (§4).
4. Defines the **Plugin Interface Specification** — Input Contract, Output Contract, Metadata, Version, Compatibility (§5).
5. Defines the **Permission Model** — Allowed Access, Restricted Access, Human Approval Boundary, Isolation Rules (§6).
6. Defines the **Security Model** — Trust Boundary, Sandboxing Concept, Data Access Rules, Credential Handling Rules (§7).
7. Defines the **Platform Plugin Specifications** for GitHub, Obsidian, MCP, Claude, Codex, VSCode, and Cursor — each declaring Purpose, Integration Boundary, Expected Capability, Input, Output, Security Constraints (§8).
8. Defines the **Compatibility** rules — Version compatibility, Migration rules, Extension rules (§9).

This Standard does **not** implement any Plugin. It does **not** install, connect, configure, or activate any Plugin on any host. It does **not** write Plugin source code, manifest files, extension manifests, server files, or deployment packages. It does **not** create runtime environments, sandboxes, or credential vaults. It declares the *contract* a conformant Plugin specification must satisfy.

### §1.2 In-Scope

1. The **plugin architecture purpose** (§2).
2. The **plugin boundary model** (§3).
3. The **plugin lifecycle** — nine stages (§4).
4. The **plugin interface specification** — Input Contract, Output Contract, Metadata, Versioning, Compatibility (§5).
5. The **plugin permission model** — Allowed Access, Restricted Access, Human Approval Boundary, Isolation Rules (§6).
6. The **plugin security model** — Trust Boundary, Sandboxing Concept, Data Access Rules, Credential Handling Rules (§7).
7. The **platform plugin specifications** for GitHub, Obsidian, MCP, Claude, Codex, VSCode, and Cursor — seven concrete Platform Plugin Specifications, each declaring Purpose, Integration Boundary, Expected Capability, Input, Output, Security Constraints (§8).
8. The **compatibility** rules — Version compatibility, Migration rules, Extension rules (§9).
9. Cross-references to Constitution, Standards, and Policies (§10).
10. Relationship to Constitution, other Standards, and future artifacts (§11).

### §1.3 Out-of-Scope

1. **Plugin implementation** — no source code, no manifest files, no extension bundles, no MCP server implementations, no VSCode extension packages, no Cursor extension bundles, no Claude integration manifests, no Codex integration packages, no GitHub App code, no Obsidian plugin manifests.
2. **Plugin installation, configuration, registration, or activation** — no third-party account connections, no OAuth flows, no API key capture, no vault population.
3. **Network access** — no live calls to any third-party service; no endpoint URLs in normative clauses; no secrets in repository.
4. **Sandbox implementation** — no Docker, no firecracker, no gVisor, no process-isolation mechanism; the Sandbox Concept is named only.
5. **MCP server creation** — no `server.py`, no `transport.ts`, no protocol binding; the MCP Plugin Specification is contract-only.
6. **VSCode / Cursor extension creation** — no `package.json` contributes blocks, no extension entrypoints.
7. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts.
8. **APES migration or Project-specific governance** — APES remains a paused Project.
9. **Sprint execution** — no Sprint is executed in this Foundation task.
10. **Plugin boundary to Pack or SDK duplication** — the Plugin Specification references `sdk-specification.md` §7 (Plugin SDK); it does not duplicate it.

---

## §2. Plugin Architecture Purpose

### §2.1 Definition

A **Plugin** is a Foundation L5 component that:

- Lives **outside** the Foundation trust boundary for execution purposes, but conforms **inside** the Foundation Interface Boundary for governance purposes.
- Adapts one third-party host platform (e.g., GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) to the Foundation's Plugin SDK contract (`sdk-specification.md` §7).
- Declares an explicit **Permission set** (`§6`) — least-privilege by default; privileges granted only on Approval.
- Passes through **nine Lifecycle stages** (`§4`) — Registration → Discovery → Validation → Permission Approval → Activation → Execution → Audit → Disable → Removal.
- Produces an **Audit hook** on every operation (`§4.6`, `§5.2`).
- Is **technology-mapped** by its host platform (e.g., a VSCode plugin runs as a Node.js extension; an MCP plugin runs as an MCP server; an Obsidian plugin runs in the Obsidian vault sandbox), but the **specification** is technology-neutral.

### §2.2 What a Plugin IS

A Plugin IS:

- a **trust-bounded adapter** between a third-party host platform and the Foundation;
- a **least-privilege actor** — privileges held to the minimum required for declared capabilities;
- a **contract-conformant agent** — every Plugin declares its compliance with the Plugin SDK (§7 of `sdk-specification.md`) and this Standard;
- a **lifecycle-bounded instance** — every Plugin instance traverses the nine Lifecycle stages with explicit transitions and Audit hooks;
- a **human-gated actor** — Activation requires explicit human Approval (`§4.4`); Removal is always permitted (`§4.9`);
- a **fail-closed actor** — unknown Permissions are denied; undeclared Capabilities are rejected.

### §2.3 What a Plugin IS NOT

A Plugin IS NOT:

- a **Foundation Engine** — Engines are internal to the Foundation trust boundary; Plugins are not (per `engine-specification.md` §3 and §11);
- a **Foundation SDK** — SDKs are internal interface contracts; Plugins are the *external adapter* (per `sdk-specification.md` §7 and §8);
- a **Foundation Pack** — Packs are immutable execution units; Plugins are mutable instances under Audit (per `pack-standard.md` §3 and §4);
- a **Foundation Runtime** — the Runtime mediates all Plugin invocations through the Plugin SDK (per `runtime-specification.md` §4);
- an **autonomous decision-maker** — every Plugin invocation that would alter Foundation state requires Audit and, where required, human Approval;
- a **trust conduit** — a Plugin is **not** allowed to forward Foundation credentials to other Plugins, Projects, or hosts;
- a **Project-specific adapter** — a Plugin conforms to the Foundation Interface Boundary; it is not owned by any Project during the Foundation phase.

### §2.4 Relationship to SDK, Engine, Runtime

| Component | Trust Boundary | Purpose |
|---|---|---|
| Plugin (this Standard) | **Crosses** third-party boundary into Foundation | Adapt third-party host to Foundation Interface Boundary |
| Plugin SDK (`sdk-specification.md` §7) | Inside Foundation | Define Interface Boundary contract |
| Engine (`engine-specification.md`) | Inside Foundation | Execute Engine workflows under Runtime |
| Runtime (`runtime-specification.md`) | Inside Foundation | Mediate every invocation across all components |

A Plugin MAY be **invoked** by a Runtime-mediated Engine (e.g., the Builder Engine calling a Plugin to surface external content). A Plugin MAY **emit** Foundation artifacts (Evidence, Audit) into Foundation storage. A Plugin MAY **not** invoke Foundation components directly; every invocation is mediated by the Runtime (per `runtime-specification.md` §4 and `sdk-specification.md` §7.2).

---

## §3. Plugin Boundary Model

### §3.1 Boundary Layers

The Plugin Boundary is **layered**. From the third-party host inward:

```
┌────────────────────────────────────────────┐
│ Third-Party Host Platform                  │   ← third-party trust (out of Foundation control)
│ (GitHub / Obsidian / MCP / Claude /        │
│  Codex / VSCode / Cursor / …)              │
├────────────────────────────────────────────┤
│ Host Adapter Surface                       │   ← third-party host's plugin model
│ (GitHub App, Obsidian plugin slot,         │
│  MCP server, Claude tool, Codex config,    │
│  VSCode extension API, Cursor extension)   │
├────────────────────────────────────────────┤
│ Plugin Instance (the Plugin)               │   ← THIS Standard's primary subject
│ - Operates with Permission-scoped          │
│   capabilities; emits Audit hooks.         │
├────────────────────────────────────────────┤
│ Plugin SDK Interface Boundary              │   ← sdk-specification.md §7
│ - All Plugin ↔ Foundation traffic.         │
├────────────────────────────────────────────┤
│ Foundation Runtime                         │   ← runtime-specification.md §4
│ - Mediates every invocation.               │
├────────────────────────────────────────────┤
│ Foundation Engines / Storage / Audit       │   ← engine-specification.md; storage
└────────────────────────────────────────────┘
```

### §3.2 Boundary Rules

1. A Plugin integrates with the Foundation **only** through the Plugin SDK Interface Boundary (per `sdk-specification.md` §7.2 and §8.1); direct file system access, network access, or code execution outside the Boundary is **forbidden**.
2. A Plugin SHALL declare its requested Permissions (per §6); the Foundation grants Permissions on a **least-privilege** basis (per `sdk-specification.md` §7.8).
3. A Plugin SHALL NOT modify Foundation artifacts directly; modification is mediated by the Runtime and recorded in an Audit hook.
4. A Plugin SHALL NOT invoke Foundation components directly; invocation is mediated by the Runtime.
5. A Plugin SHALL NOT extend the Foundation Interface Boundary unilaterally; extensions require a Plugin Specification amendment (per `change-control-policy.md`).
6. A Plugin SHALL NOT relay Foundation credentials, tokens, or secrets to the third-party host beyond what the Permission set expressly authorizes (per §7.4).
7. A Plugin SHALL NOT permit the third-party host to invoke Foundation components without first passing the Plugin SDK Interface Boundary and the Runtime's Audit hook.

### §3.3 Boundary Crossing Points

Only the following Boundary crossings are permitted:

| Direction | Mediator | Recorded As |
|---|---|---|
| Third-party host → Plugin (data event) | Host Adapter Surface | Plugin Audit hook (`§5.2`) |
| Plugin → Plugin SDK Interface Boundary (call) | Plugin SDK | Plugin Audit hook |
| Plugin SDK → Runtime | Runtime | Runtime Audit hook (`runtime-specification.md` §10) |
| Runtime → Foundation Storage | Runtime | Manifest entry + Audit hook |
| Foundation Storage → Plugin (read-back) | Runtime | Plugin Audit hook |
| Plugin → Third-party host (response) | Host Adapter Surface | Plugin Audit hook |

A Boundary crossing that is not mediated by the indicated component, or that is not recorded as indicated, is a **Boundary violation** (per §7 and `quality-gate-standard.md` §5.3.6).

### §3.4 Boundary to SDK Spec

This Standard **references** `sdk-specification.md` §7 (Plugin SDK Specification) for the Interface Boundary contract and §8 (Shared SDK Architecture) for the SDK-to-Runtime relationship. This Standard **does not duplicate** the SDK Specification; wherever this Standard and the SDK Specification appear to overlap, the SDK Specification prevails for Interface-Boundary clauses, and this Standard prevails for Plugin-specific clauses (Lifecycle, Permission Model, Security Model, Platform Plugin Specifications).

---

## §4. Plugin Lifecycle

### §4.1 Overview

Every Plugin instance traverses **nine ordered stages**. A Plugin may not skip a stage. A Plugin may not transition with an unresolved failure, ungranted Permission, or unaudited operation.

```
Registration → Discovery → Validation → Permission Approval →
Activation → Execution → Audit → Disable → Removal
```

### §4.2 Stage 1 — Registration

**Purpose:** Declare the Plugin's existence, identity, vendor, and intended host.

**Subject state:** `Unregistered`.

**Inputs:**
1. Plugin identity (`§5.3`) — Plugin ID, Plugin name, Plugin version, Plugin vendor.
2. Host platform declaration — one of the seven Platform Plugins enumerated in §8 (or a future FRFC-approved host).
3. Plugin manifest — natural-language Manifest entry per `schema-standard.md` §8 declaring the Plugin's intended Permission set and declared Capabilities.

**Outputs:**
1. A `Plugin Registration Record` (`PLUGIN-<host>-<slug>-registration.md`) declaring the Plugin's identity and intended host.
2. A placeholder in the Plugin Registry (logical only; no concrete implementation requires Foundation registry storage at this Standard).

**Transition condition:** The Registration Record passes the Structure Gate (per `quality-gate-standard.md` §5.3.1) and the Isolation Gate (§5.3.4).

**Forbidden at this stage:** activation, execution, Audit hook emission against Foundation storage.

### §4.3 Stage 2 — Discovery

**Purpose:** Make the Plugin discoverable to authorized Foundation actors (Builder, Runtime, Reviewer).

**Subject state:** `Registered`.

**Inputs:**
1. The Registration Record (§4.2).
2. A Discovery Index entry — a logical pointer in the Plugin Registry.

**Outputs:**
1. The Plugin is listed in the Discovery Index against its host platform and Permission tier.

**Transition condition:** The Discovery Index entry passes the Cross Reference Gate (per `quality-gate-standard.md` §5.3.3).

**Forbidden at this stage:** Activation, Execution, Permission grants.

### §4.4 Stage 3 — Validation

**Purpose:** Verify that the Plugin's declared Capabilities and Permissions are internally consistent, conformant with `sdk-specification.md` §7, and contain no Boundary violations.

**Subject state:** `Discovered`.

**Inputs:**
1. The Registration Record.
2. The Plugin's declared Permission set.
3. The Plugin's declared Capability list.

**Outputs:**
1. A `Plugin Validation Report` (`PLUGIN-<host>-<slug>-validation.md`) declaring each Gate outcome (per `quality-gate-standard.md` §5.3).

**Applicable Gates:**
- **Structure Gate** (§5.3.1) — fields and sections are well-formed.
- **Consistency Gate** (§5.3.2) — Permission set and Capability list are internally consistent.
- **Cross Reference Gate** (§5.3.3) — every cross-reference resolves.
- **Isolation Gate** (§5.3.4) — no Project-specific rule; remains valid without any Project.
- **Scope Compliance Gate** (§5.3.5) — the Plugin honors its declared scope.
- **Security Boundary Gate** (§5.3.6) — no Permissions violate the Security Boundary (per §7).

**Transition condition:** All six Gates return `PASS`.

**Forbidden at this stage:** Activation, Execution, network access, file system write.

### §4.5 Stage 4 — Permission Approval

**Purpose:** A human Reviewer (or the Builder's authorized Approver, when the Plugin is Foundation-level) reviews the Permission set and decides what is granted, denied, or conditioned.

**Subject state:** `Validated`.

**Inputs:**
1. The Plugin Validation Report.
2. The Plugin's requested Permission set.
3. The Reviewer's identity and role (per `roles-and-authority.md`).

**Outputs:**
1. A `Permission Approval Record` (`PLUGIN-<host>-<slug>-permission-approval.md`) declaring each Permission as `Granted`, `Denied`, `Granted with Conditions`, or `Deferred`.
2. The granted Permission set becomes the Plugin's operational scope.

**Reviewer rule:** The Reviewer SHALL NOT be the individual who authored the Plugin Registration Record or Validation Report (separation of duties per Constitution §5 and `quality-gate-standard.md` §7.1).

**Default policy:** Permissions are **denied unless explicitly granted** (least-privilege). Default-denied Permissions:
- Network access (`§6.2.4`).
- Code execution (`§6.2.5`).
- File system writes outside declared scope (`§6.2.6`).
- Git operations (`§6.2.7`).
- Credential forwarding (`§7.4`).

**Transition condition:** The Permission Approval Record is signed by the Reviewer with disposition `Approved` or `Approved with Conditions`.

**Forbidden at this stage:** Activation, Execution, Audit hook emission against Foundation storage (the Audit hook for the Approval itself is emitted but does not represent Plugin activity).

### §4.6 Stage 5 — Activation

**Purpose:** Promote the Plugin from `Approved` to `Active` so it may begin Execution.

**Subject state:** `Approved` → `Active`.

**Inputs:**
1. The Permission Approval Record.
2. The signed Activation request (Builder / Runtime operator).

**Outputs:**
1. An `Activation Record` (`PLUGIN-<host>-<slug>-activation.md`) recording the activation timestamp, the granted Permission set, the Foundation Version, and the actor.
2. The Plugin is registered as `Active` in the Plugin Registry.

**Transition condition:** Signed Activation request + Permission Approval Record + a positive Stage-3 Validation Report.

**Forbidden at this stage:** any operation outside the granted Permission set; any operation before the Audit hook infrastructure is reachable.

### §4.7 Stage 6 — Execution

**Purpose:** The Plugin performs its declared Capabilities within its granted Permissions, emitting Audit hooks on every operation.

**Subject state:** `Active` → `Executing`.

**Inputs:**
1. Host Adapter events (third-party host events, e.g., a GitHub webhook, an Obsidian file event, an MCP tool call, a Claude tool invocation, a Codex CLI trigger, a VSCode command, a Cursor hook).
2. Runtime-mediated Foundation calls.

**Outputs:**
1. Plugin operations (reads, writes, network calls, computations) bounded by the granted Permission set.
2. An **Audit hook per operation** (§5.2) — every Plugin operation produces an Audit hook declaring the operation identity, the granted Permission invoked, the Input / Output, the Boundary clauses crossed, and the outcome.

**Transition condition:** The Plugin emits an `Idle` or `Stopped` status when no operations are pending (a Plugin may return to `Active` for further events without re-entering Stages 2–5).

**Hard prohibitions during Execution:**
1. The Plugin SHALL NOT exceed its granted Permission set.
2. The Plugin SHALL NOT operate without an Audit hook pathway to the Foundation Audit storage (per `directory-standard.md` §6).
3. The Plugin SHALL NOT bypass the Runtime for any Foundation invocation.
4. The Plugin SHALL NOT auto-commit, auto-tag, or auto-push via git; git operations require explicit human Approval and are explicit Permissions (`§6.2.7`).
5. The Plugin SHALL NOT persist credentials across Activation cycles except via an explicit Credential Handling Rule (`§7.4`).

### §4.8 Stage 7 — Audit

**Purpose:** Verify that the Plugin's Execution history complies with the granted Permission set, the Security Boundary, and the six Foundation Quality Gates.

**Subject state:** `Executing` → `Audited`.

**Inputs:**
1. The Plugin's Audit hook stream.
2. The granted Permission set (from §4.5).
3. The Plugin's declared Capabilities.

**Outputs:**
1. A `Plugin Audit Report` (`PLUGIN-<host>-<slug>-audit.md`) declaring per-operation outcomes against the six Gates and the Security Boundary.
2. Findings — observations, defects, near-misses.
3. Audit Verdict — `PASS`, `PASS with Notes`, `FAIL`, or `BLOCKED` (per `quality-gate-standard.md` §5.4).

**Frequency:** Audit MAY be continuous (every operation) or periodic (e.g., end-of-cycle), at the discretion of the Reviewer and per the host platform's cadence. Continuous Audit is preferred for high-Permission Plugins.

**Transition condition:** Audit Verdict `PASS` returns the Plugin to `Active` for further Execution; `PASS with Notes` returns the Plugin to `Active` with recorded observations; `FAIL` advances the Plugin to `Disable` (§4.9); `BLOCKED` halts the Lifecycle pending Escalation (per `disagreement-and-escalation.md`).

### §4.9 Stage 8 — Disable

**Purpose:** Suspend the Plugin's Execution privileges while preserving its Audit history. Disable is **always permitted** (no Permission required to Disable — per `sdk-specification.md` §7.2 immutability protections).

**Subject state:** `Active / Audited` → `Disabled`.

**Inputs:**
1. A signed `Disable Request` — by the Reviewer, the Builder (within scope), or the human Architect.
2. Reason code — `Audit Failure`, `Permission Scope Violation`, `Boundary Violation`, `Operator Request`, `End of Cycle`, `Security Incident`.

**Outputs:**
1. A `Disable Record` (`PLUGIN-<host>-<slug>-disable.md`) recording the reason, timestamp, and actor.
2. The Plugin's effective state is `Disabled` — it cannot Execute; its Audit history is preserved.

**Transition condition:** Disable Request signed + Reason Code populated.

**Note:** Disable is **non-destructive** — the Plugin's prior Audit history, Registration, Validation, and Permission Approval records are retained per `directory-standard.md` §4 and `governance-model.md` §8 immutability rule.

### §4.10 Stage 9 — Removal

**Purpose:** Decommission the Plugin from the active Plugin Registry. Removal is a terminal action; the Plugin's records are retained per `governance-model.md` §8 (immutability) and `directory-standard.md` (artifact retention), but the Plugin SHALL NOT be re-activated except via a new Registration cycle (§4.2).

**Subject state:** `Disabled` → `Removed`.

**Inputs:**
1. A signed `Removal Request` — by the human Architect or by an FD.
2. Reason code — `End of Life`, `Host Platform Decommissioned`, `Security Incident`, `Capability Superseded`.

**Outputs:**
1. A `Removal Record` (`PLUGIN-<host>-<slug>-removal.md`) recording the reason, timestamp, and actor.
2. The Plugin is removed from the active Plugin Registry; the Audit history is retained.
3. The Plugin's Permission set is **revoked** — no residual Permission persists.

**Transition condition:** Removal Request signed + Reason Code populated + revocation of all granted Permissions recorded.

**Note:** Removal is **non-destructive of audit trail** — Removal preserves evidence; it disables future actions.

### §4.11 Stage Transition Table

| From | To | Trigger | Required Verdict |
|---|---|---|---|
| (none) | `Unregistered` | Registration filed | n/a |
| `Unregistered` | `Registered` | Discovery Index entry created | Structure Gate `PASS`; Isolation Gate `PASS` |
| `Registered` | `Discovered` | Discovery Index passes | Cross Reference Gate `PASS` |
| `Discovered` | `Validated` | Validation Report filed | All six Gates `PASS` |
| `Validated` | `Approved` | Permission Approval Record signed | Reviewer disposition `Approved` |
| `Approved` | `Active` | Activation Record signed | Signed Activation + Approval + Validation |
| `Active` | `Executing` | Host event / Runtime call | Granted Permission invoked |
| `Executing` | `Audited` | Audit Report filed | Audit Verdict `PASS` or `PASS with Notes` |
| `Active` / `Audited` | `Disabled` | Disable Request signed | Reason Code populated |
| `Disabled` | `Removed` | Removal Request signed | Reason Code + Permission revocation |

### §4.12 Lifecycle Hooks Summary

| Hook | Stage | Required Artifact |
|---|---|---|
| `Plugin-Registration-Hook` | 1 | Registration Record |
| `Plugin-Discovery-Hook` | 2 | Discovery Index entry |
| `Plugin-Validation-Hook` | 3 | Validation Report |
| `Plugin-Permission-Approval-Hook` | 4 | Permission Approval Record |
| `Plugin-Activation-Hook` | 5 | Activation Record |
| `Plugin-Execution-Hook` | 6 | Per-operation Audit hook |
| `Plugin-Audit-Hook` | 7 | Audit Report |
| `Plugin-Disable-Hook` | 8 | Disable Record |
| `Plugin-Removal-Hook` | 9 | Removal Record |

A Plugin instance whose corresponding `*-Hook` is missing is **Invalid** at the relevant stage.

---

## §5. Plugin Interface Specification

### §5.1 Input Contract

A Plugin SHALL accept the following **Input Contract**:

1. **Plugin identity** — Plugin ID, Plugin name, Plugin version, Plugin vendor (per `sdk-specification.md` §7.3).
2. **Host Adapter event** — the host's typed event (e.g., GitHub webhook payload, Obsidian file event, MCP tool call, Claude tool invocation, Codex CLI trigger, VSCode command, Cursor hook). The host event format is **opaque** to the Foundation; the Foundation accepts whatever the host presents.
3. **Runtime context** — the Foundation Version, the Constitution Version, the Plugin SDK Version, the Plugin's granted Permission set, the Plugin's Foundation-binding declaration.
4. **Declared Capability invocation** — a named Capability drawn from the Plugin's declared Capability list (§5.3 metadata).
5. **§15.5-equivalent Scope Declaration** — a per-Plugin Scope declaring Allowed Operations, Forbidden Operations, Inputs, Outputs, Boundaries. Mirrors `pack-standard.md` §15.5 and `runtime-specification.md` §6.

The Foundation SHALL reject any Plugin Input that does not satisfy the Input Contract. The Plugin SHALL reject any Input that does not arrive through the Plugin SDK Interface Boundary.

### §5.2 Output Contract

A Plugin SHALL emit the following **Output Contract**:

1. **Plugin result** — the result of the Capability invocation (success, no-op, error). The result type is declared in the Plugin's Manifest entry (`schema-standard.md` §8).
2. **Plugin Audit hook** (per `sdk-specification.md` §7.4 and §8.5) — a structured record of every operation, declaring:
   - **Plugin-ID** and **Plugin-Version**.
   - **Operation** — the Capability invoked.
   - **Permission-Invoked** — the granted Permission exercised.
   - **Input-Digest** — a stable digest of the Input (no Input content is recorded unless the Capability explicitly declares it; the digest protects auditability without leaking payload data).
   - **Output-Digest** — a stable digest of the Output (same protection).
   - **Boundary-Clauses-Crossed** — the set of Boundary Rules (§3.2) exercised.
   - **Outcome** — `Success`, `No-Op`, `Error`, `Permission-Denied`, `Boundary-Violation`.
   - **Timestamp** — ISO-8601.
   - **Host-Event-Digest** — a stable digest of the originating host event (privacy-preserving).
3. **Plugin Manifest** — the Plugin's Manifest entry per `schema-standard.md` §8 (re-emitted on Activation and on Capability changes).

The Foundation SHALL accept Audit hooks in the Output Contract form; an Audit hook missing any of the above fields is **Invalid** and triggers a Boundary Violation (§7).

### §5.3 Metadata

The Plugin's Metadata is the persistent descriptive payload that travels with the Plugin instance. Required fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `Plugin-ID` | R | string | Unique identifier; pattern `PLUGIN-<host>-<slug>` |
| `Plugin-Name` | R | string | Human-readable name |
| `Plugin-Version` | R | SemVer | Per Constitution §8 |
| `Plugin-Vendor` | R | string | Author/vendor identifier |
| `Plugin-Host` | R | enum:`github`,`obsidian`,`mcp`,`claude`,`codex`,`vscode`,`cursor` | The host platform (per §8) |
| `Plugin-Description` | R | string | One-paragraph human-readable description |
| `Plugin-Capabilities` | R | list:string | Declared Capability list (each Capability is a string identifier) |
| `Plugin-Required-Permissions` | R | list:Permission | Requested Permissions (per §6) |
| `Plugin-Granted-Permissions` | R | list:Permission | Granted Permissions (post §4.5) |
| `Plugin-SDK-Version` | R | SemVer | Targeted `sdk-specification.md` version |
| `Plugin-Foundation-Version` | R | SemVer | Targeted Foundation Version |
| `Plugin-Constitution-Version` | R | SemVer | Targeted Constitution Version |
| `Plugin-Scope-Declaration` | R | Scope | Allowed / Forbidden Operations, Inputs, Outputs, Boundaries |
| `Plugin-Compatibility-Profile` | R | Compatibility | Per §9 |
| `Plugin-Supersedes` | O | string | Previous Plugin ID (if superseding) |
| `Plugin-Superseded-By` | C | string | Set when superseded |

### §5.4 Versioning

- **Version surface:** `Plugin.Version`, `Plugin-SDK-Version`, `Plugin-Foundation-Version`, `Plugin-Constitution-Version`.
- **Bump triggers:**
  - **MAJOR** — non-backward-compatible Plugin capability surface change.
  - **MINOR** — additive new Capability within granted Permissions.
  - **PATCH** — typo fix, clarification, re-bind to a newer Foundation minor without Capability changes.
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Plugin RC), `1.0.0` (first Stable Plugin).
- **Foundation binding:** A Plugin SHALL NOT declare a Foundation Version newer than its Plugin-SDK-Version.

### §5.5 Compatibility

A Plugin's Compatibility Profile declares Compatibility with:

- **Foundation versions** — the Plugin's Plugin-Foundation-Version is its declared compatibility floor; compatible with `>= Plugin-Foundation-Version` and `< Plugin-SDK-Version.Major + 1`. (A Plugin bound to `0.1.0` is not automatically compatible with `1.0.0`; a new Foundation Major requires a new Manifest version.)
- **Constitution versions** — the Plugin SHALL NOT invoke clauses past its Plugin-Constitution-Version.
- **Host platform versions** — the Plugin declares the range of host platform versions it supports (technology-neutral, e.g., `GitHub Apps >= <n>`; the platform-specific number is recorded in §8 platform specifications).
- **Plugin-SDK versions** — the Plugin SHALL be compatible with the Plugin-SDK Version recorded in its Manifest; new SDK versions require a new Plugin Version (per §9.3).

---

## §6. Permission Model

### §6.1 Overview

The Permission Model binds Plugin operations to **explicitly granted capabilities**. Permissions are **default-denied**; a Permission is granted only when a Reviewer records an explicit grant in the Permission Approval Record (§4.5). The Foundation honors **least-privilege**: a Plugin receives no Permission it does not request, and every requested Permission is reviewed individually.

### §6.2 Allowed Access

The following Permissions MAY be granted. Each is granted individually; **no Permission is implicit from another**.

| # | Permission | Description |
|---|---|---|
| 1 | `Read Foundation Artifacts` | Read-only access to designated Foundation files via Runtime mediation |
| 2 | `Emit Evidence` | Produce Evidence records (per `schema-standard.md` §4) on behalf of the user |
| 3 | `Emit Audit` | Produce Audit hooks (per `§5.2` and `schema-standard.md` §9) |
| 4 | `Invoke Runtime-mediated Components` | Invoke Foundation components via the Runtime, never directly |
| 5 | `Read Host Adapter Event` | Receive host events delivered via the Plugin SDK Interface Boundary |
| 6 | `Write Plugin Local State` | Write to a designated, scoped Plugin-local store (no Foundation artifact modification) |

### §6.3 Restricted Access

The following Permissions are **restricted** — they MAY be granted only with explicit human Approval and additional Security Boundary controls. None are granted by default.

| # | Permission | Restriction |
|---|---|---|
| 7 | `Restricted Network Access` | Granted only with declared endpoints, declared request shapes, declared authentication method, and Audit on every request |
| 8 | `Restricted Code Execution` | Granted only with declared execution envelope (sandbox scope) and Audit on every invocation |
| 9 | `Restricted File System Access` | Granted only with declared paths (read and/or write), per-path Audit, and per-path declaration |
| 10 | `Restricted Git Operations` | Granted only with declared git verb(s) and an external Approval hook before each invocation |
| 11 | `Restricted Credential Forwarding` | Granted only with declared forwarding target, declared credential scope, and on-hook Audit; the Foundation SHALL redact secret material in Audit hooks (§7.4) |
| 12 | `Restricted Foundation Write` | Granted only for declared Foundation artifact classes (e.g., Evidence, Audit) and only via the Runtime-mediated write path |

### §6.4 Default-Denied Permissions

The following Permissions are **default-denied**. A Permission Approval Record MAY grant them, but the Foundation treats them as restricted:

- `Network Access (unrestricted)` — denied unless the Restricted Permission is granted with declared endpoints.
- `Code Execution (unrestricted)` — denied unless the Restricted Permission is granted with declared envelope.
- `File System Writes Outside Scope` — denied unless the Restricted Permission is granted with declared paths.
- `Git Operations` — denied unless the Restricted Permission is granted with declared verbs and external Approval.
- `Credential Forwarding` — denied unless the Restricted Permission is granted with declared target and scope.
- `Foundation Artifact Modification` — denied; Plugins modify Foundation artifacts only through `Restricted Foundation Write` and only via the Runtime-mediated path.

### §6.5 Human Approval Boundary

The Human Approval Boundary is the **stage transition** between Validation (§4.4) and Permission Approval (§4.5). The Reviewer — a human role per Constitution §5 — decides each requested Permission individually.

The Human Approval Boundary is enforced by:

1. The signed Permission Approval Record (§4.5) listing each Permission as `Granted`, `Denied`, `Granted with Conditions`, `Deferred`.
2. The Foundation's refusal to honor any Permission not listed as `Granted` (or `Granted with Conditions` whose conditions are satisfied).
3. The runtime's enforcement of every granted Permission's declared scope (e.g., if the Permission declares endpoints, calls to undeclared endpoints are denied).
4. The Audit hook emitted for each Approval decision, capturing Reviewer identity, decision timestamp, and reason codes.

No machine, automation, or CI/CD pipeline may substitute for the human Reviewer at this boundary (per Constitution §5 and `quality-gate-standard.md` §7.4).

### §6.6 Isolation Rules

1. A Plugin SHALL operate only within its granted Permission set.
2. A Plugin SHALL NOT share state with another Plugin instance unless an explicit `Inter-Plugin Communication` Permission has been granted and the other Plugin is identified by ID in the Permission grant.
3. A Plugin SHALL NOT read or write Foundation artifacts outside its declared Scope (§5.1).
4. A Plugin SHALL NOT forward Foundation credentials, tokens, or secrets to a third-party host except as permitted by §7.4 and a granted `Restricted Credential Forwarding` Permission.
5. A Plugin SHALL NOT bypass the Runtime for any Foundation invocation.
6. A Plugin SHALL NOT install, configure, or activate another Plugin; only the human Reviewer or the Builder (within scope) MAY issue Registration, Validation, Permission Approval, Activation, Disable, or Removal requests.
7. A Plugin's Audit history SHALL remain isolated from other Plugins' Audit histories; only the human Reviewer and the Architect MAY view cross-Plugin Audit.

---

## §7. Security Model

### §7.1 Trust Boundary

A Plugin crosses a **third-party trust boundary**. The third-party host (e.g., GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) is **not** part of the Foundation trust boundary. The Trust Boundary is therefore a line that separates:

- **Foundation-trusted code** — Runtime, Engines, SDKs, Foundation storage, Foundation Audit logs.
- **Plugin code** — executes under host-Adapter control, with Audit hooks emitted across the Boundary.
- **Third-party-host code** — executes outside the Foundation's control; the Plugin only receives its events through the host Adapter Surface (§3.1) and only emits responses through the Plugin SDK Interface Boundary.

The Trust Boundary rule is: **Foundation trust does not extend to third-party hosts**. The Plugin SHALL treat every host event as untrusted input. The Foundation SHALL treat every Plugin operation as bounded by the granted Permission set; the Foundation SHALL NOT extend trust to the Plugin code itself beyond the granted Permissions.

### §7.2 Sandboxing Concept

The Plugin's execution environment is the host Adapter Surface, which provides the **sandboxing** (technology-neutral). The host's sandboxing mechanism is host-specific (e.g., a GitHub Action runs in a GitHub-provided runner; an MCP server runs in the host that spawned it; a VSCode extension runs in the Extension Host process; an Obsidian plugin runs in the Obsidian vault sandbox).

The sandbox concept is normative:

1. The Plugin SHALL execute within the host-provided sandbox; it SHALL NOT escape the sandbox through file system traversal, privilege escalation, or process spawning.
2. The Foundation SHALL honor the host's sandboxing decisions; the Foundation does not run Plugins directly.
3. The Plugin SHALL declare its intended sandbox scope in its Scope Declaration (§5.1) so the host and the Foundation have a record of expected behavior.
4. A sandbox escape (detected via Audit hook anomaly, host-reported event, or Boundary Violation) is a **Security Incident** that advances the Plugin to `Disable` (§4.9).

The Plugin Specification does **not** prescribe a particular sandbox technology; the host is responsible.

### §7.3 Data Access Rules

1. **Read direction (third-party host → Plugin → Foundation).** The Plugin MAY read host-provided data and emit a Foundation representation (e.g., an Evidence record) only within the granted `Read Host Adapter Event` and `Restricted Network Access` Permissions.
2. **Write direction (Foundation → Plugin → third-party host).** The Plugin MAY write to the third-party host only through a granted `Restricted Network Access` Permission with declared endpoints; every write is Audit-hooked.
3. **Payload rules.** The Plugin SHALL redact secret-bearing fields (API keys, tokens, passwords, session cookies, private keys) from Plugin-emitted Evidence and Audit hooks unless an explicit `Restricted Credential Forwarding` Permission is granted and the redaction policy is enforced.
4. **Data residency.** The Plugin SHALL NOT transfer Foundation data outside the Foundation's declared storage region without an explicit `Restricted Network Access` Permission whose declared endpoints and residency target are recorded.
5. **Retention.** The Plugin SHALL declare the retention period of any data it stores in Plugin-local state. Foundation Audit hooks are retained per `governance-model.md` §8; the Plugin's Plugin-local state is **not** Foundation storage.
6. **Discovery.** The Plugin SHALL NOT discover Foundation artifacts by enumeration, crawling, or scanning; only declared and approved artifact references are addressable.

### §7.4 Credential Handling Rules

1. **Default rule.** Credentials are **default-denied**. A Plugin SHALL NOT request, capture, store, or forward credentials except under an explicit `Restricted Credential Forwarding` Permission.
2. **No secret material in Audit hooks.** The Plugin SHALL NOT record secret-bearing fields in Audit hooks; the Audit hook records `digest` and `redacted-flag` only. The redacted-flag triggers an out-of-band review by the human Architect if asserted.
3. **Credential isolation.** A Plugin's granted credentials are scoped to the Permission; the Foundation SHALL NOT reuse credentials across Permissions, Plugins, or Projects.
4. **Credential rotation.** A Plugin SHALL NOT rotate Foundation-managed credentials; rotation is a Foundation-level operation mediated by the Runtime and gated by a signed Review Record.
5. **Credential revocation.** Disable (§4.9) and Removal (§4.10) of a Plugin revoke all granted credential Permissions; no residual credential access persists.
6. **OAuth flows.** If a host uses OAuth (e.g., GitHub Apps, MCP, Claude), the Plugin SHALL NOT embed a long-lived client secret; the Plugin SHALL use the host's intended OAuth flow and SHALL emit Audit hooks for every token exchange.
7. **No credential exfiltration.** The Plugin SHALL NOT relay Foundation credentials to a third-party host beyond what the Permission set expressly authorizes; exfiltration is a Security Incident.

---

## §8. Platform Plugin Specifications

### §8.0 Overview

This section specifies the **seven concrete Platform Plugin Specifications** listed in the Architect's mandate: **GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor**. Each specification defines:

- **Purpose**
- **Integration Boundary**
- **Expected Capability**
- **Input**
- **Output**
- **Security Constraints**

This section declares the contract only. No Platform Plugin is implemented, installed, connected, or activated in this Standard. The seven specifications are co-equal; none supersedes another.

All seven specifications conform to `sdk-specification.md` §7 (Plugin SDK), §3.2 Boundary Rules, §6 Permission Model, §7 Security Model of this Standard, and `runtime-specification.md` §10 (Runtime Security Boundary — Plugins must honor).

---

### §8.1 GitHub Plugin

**Purpose.** A Plugin that adapts the GitHub host platform (GitHub.com or a self-hosted GitHub Enterprise instance) to the Foundation Plugin SDK. The GitHub Plugin surfaces GitHub events (issues, pull requests, comments, workflow runs, releases) as Foundation Evidence and emits Audit hooks for every read and write.

**Integration Boundary.** The Plugin integrates through the GitHub Apps model (technology-neutral boundary descriptor: GitHub Apps deliver webhooks to a configured endpoint and receive API calls through a token-scoped interface). The Foundation's Runtime mediates every API call. The GitHub App's permissions, when registered on GitHub, declare the GitHub-side scope; the Foundation's Permission Model declares the Foundation-side scope. The two scopes are recorded separately and audited separately.

**Expected Capability.** The GitHub Plugin MAY:
- Receive GitHub webhook events on the registered endpoint and translate them into Foundation Evidence records (e.g., a pull request comment becomes an Evidence record; a workflow run becomes a Stats record).
- Read declared GitHub resources (issues, PRs, comments, releases, workflow runs) via the GitHub API.
- Write declarative annotations back to GitHub (e.g., a status check, a comment) under a granted `Restricted Foundation Write` Permission.

**Input.**
1. GitHub webhook payload (issues, pull_request, issue_comment, workflow_run, release, push, etc.).
2. GitHub API responses (read results).
3. Foundation Runtime context (the Plugin's granted Permission set, Foundation Version, Plugin-SDK Version).

**Output.**
1. Foundation Evidence records (per `schema-standard.md` §4) emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every operation.
3. Optional GitHub annotations (status checks, comments) under `Restricted Foundation Write`.

**Security Constraints.**
1. The Plugin SHALL NOT request a GitHub App permission broader than its declared Foundation Permission; the Foundation-side Permission set is the binding scope.
2. The Plugin SHALL NOT embed a long-lived GitHub App private key in Foundation storage; key handling is governed by `§7.4`.
3. The Plugin SHALL redact `X-Hub-Signature-256` and equivalent secret material from Audit hooks.
4. The Plugin SHALL NOT write to a GitHub repository or issue without a `Restricted Foundation Write` Permission that names the target repository and the writing Capability.
5. The Plugin SHALL NOT use GitHub Actions as a code-execution channel without a `Restricted Code Execution` Permission; Foundation Policy treats arbitrary Actions as out of scope.
6. The Plugin SHALL audit every webhook event with a digest (the payload itself is not recorded in Foundation storage unless promoted to Evidence).

---

### §8.2 Obsidian Plugin

**Purpose.** A Plugin that adapts the Obsidian knowledge-base host (a local-first markdown vault) to the Foundation Plugin SDK. The Obsidian Plugin surfaces vault events (file create/modify/delete, plugin events, search results) as Foundation Evidence and emits Audit hooks for every operation.

**Integration Boundary.** The Plugin integrates through Obsidian's plugin model: an Obsidian plugin is loaded by the Obsidian app into its JavaScript-enabled extension sandbox within the user's vault. The Foundation's Runtime is contacted through a declared endpoint or local IPC; the Obsidian app itself remains the host. The boundary is the vault directory boundary: the Plugin SHALL NOT read or write files outside the user's vault directory unless an explicit `Restricted File System Access` Permission has been granted.

**Expected Capability.** The Obsidian Plugin MAY:
- Receive vault events (file changes, plugin loads, command invocations, workspace changes) and translate them into Foundation Evidence.
- Read declared notes and metadata via Obsidian's API within the user's vault.
- Emit declarative annotations to the vault (e.g., a marker note, a YAML frontmatter update) under a granted `Restricted Foundation Write` Permission.

**Input.**
1. Obsidian vault events (file create, modify, delete; plugin event; ribbon action; command palette).
2. Obsidian API results (metadata, links, search).
3. Foundation Runtime context.

**Output.**
1. Foundation Evidence records emitted via the Runtime.
2. Foundation Audit hooks for every operation.
3. Optional vault annotations under `Restricted Foundation Write`.

**Security Constraints.**
1. The Plugin SHALL NOT traverse the vault directory boundary without a `Restricted File System Access` Permission naming the target paths.
2. The Plugin SHALL NOT execute arbitrary JavaScript beyond Obsidian's own plugin sandboxing model.
3. The Plugin SHALL NOT exfiltrate vault content to a network endpoint without a `Restricted Network Access` Permission naming the endpoint.
4. The Plugin SHALL redact bearer tokens, API keys, or credentials present in vault notes from Audit hooks and Evidence records; the redacted-flag triggers out-of-band review.
5. The Plugin SHALL NOT install or activate another Obsidian plugin or community plugin.
6. The Plugin SHALL audit every vault event with a digest.

---

### §8.3 MCP Plugin

**Purpose.** A Plugin that adapts an MCP (Model-Context-Protocol) host to the Foundation Plugin SDK. The MCP Plugin surfaces MCP tool calls and resources as Foundation Evidence and emits Audit hooks for every operation. The MCP Plugin occupies the special role of **transport mediator** in third-party AI-tooling ecosystems; its specification is intentionally conservative.

**Integration Boundary.** The Plugin integrates through the MCP model: an MCP host (e.g., an AI agent runtime) issues MCP requests to MCP servers (which are the "tools"); the Foundation's MCP Plugin accepts the MCP server side of the boundary. The Foundation's Runtime mediates every MCP request; the Foundation treats every MCP request as untrusted input and every MCP response as bounded by the granted Permission set.

**Expected Capability.** The MCP Plugin MAY:
- Accept MCP requests from declared MCP hosts and translate them into Foundation Capabilities (read, search, fetch, transform, emit).
- Emit MCP-formatted responses (text, structured content, error codes) back to the MCP host.
- Read declared MCP resources (per the MCP resource model) under a `Read Host Adapter Event` Permission.

**Input.**
1. MCP request (method, params, id) from the MCP host.
2. MCP resource notifications.
3. Foundation Runtime context.

**Output.**
1. Foundation Evidence records (per `schema-standard.md` §4) emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every operation, declaring the MCP method and digest of params.
3. MCP responses (text content, structured content, error code) under the granted Permission.

**Security Constraints.**
1. The Plugin SHALL treat every MCP request as untrusted input; payload validation is required before any Capability invocation.
2. The Plugin SHALL declare the set of MCP methods it serves in its Manifest; undeclared methods receive `Permission-Denied`.
3. The Plugin SHALL NOT execute arbitrary code in response to an MCP request; execution is bounded by the host's sandbox and by the granted `Restricted Code Execution` Permission.
4. The Plugin SHALL NOT forward MCP-bearer tokens to a third-party host beyond the declared MCP host list.
5. The Plugin SHALL audit every MCP request and response with a digest; payloads containing credentials are redacted in Audit hooks.
6. The Plugin SHALL NOT register MCP resources the Plugin does not own; the Foundation's Plugin-local state is the Plugin's scope boundary.

---

### §8.4 Claude Plugin

**Purpose.** A Plugin that adapts the Claude host (Claude.ai, Claude API, Claude Code CLI, or a Claude-compatible interface) to the Foundation Plugin SDK. The Claude Plugin surfaces Claude-conversation events, tool calls, and skill artifacts as Foundation Evidence and emits Audit hooks for every operation.

**Integration Boundary.** The Plugin integrates through Claude's tool-use boundary: a Claude host invokes "tools" via a structured request; the Foundation's Claude Plugin accepts the tool side of the boundary. The Foundation's Runtime mediates every tool call; the Foundation treats every tool call as untrusted input.

**Expected Capability.** The Claude Plugin MAY:
- Accept tool invocations from Claude hosts and translate them into Foundation Capabilities.
- Emit structured tool results back to Claude hosts.
- Read declared Claude-managed resources (per the Claude-Plugin model) under a `Read Host Adapter Event` Permission.

**Input.**
1. Tool invocation request (name, input) from a Claude host.
2. Claude-managed resource notifications (e.g., file events, project state).
3. Foundation Runtime context.

**Output.**
1. Foundation Evidence records emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every tool invocation.
3. Structured tool results (text, JSON, error) under the granted Permission.

**Security Constraints.**
1. The Plugin SHALL treat every tool invocation as untrusted input and SHALL validate inputs against declared input schemas.
2. The Plugin SHALL declare the set of tool names it serves in its Manifest; undeclared tool names receive `Permission-Denied`.
3. The Plugin SHALL NOT execute arbitrary code in response to a tool call.
4. The Plugin SHALL NOT forward Claude-API keys or session tokens beyond the declared scope.
5. The Plugin SHALL redact secret-bearing fields from Audit hooks.
6. The Plugin SHALL audit every tool invocation with a digest.

---

### §8.5 Codex Plugin

**Purpose.** A Plugin that adapts the Codex CLI (or a Codex-compatible CLI interface) to the Foundation Plugin SDK. The Codex Plugin surfaces Codex command events, shell-output streams, and integration triggers as Foundation Evidence and emits Audit hooks for every operation.

**Integration Boundary.** The Plugin integrates through the Codex CLI boundary: a Codex-compatible CLI invokes the Plugin through a declared integration entrypoint; the Foundation's Runtime mediates every invocation. The Plugin SHALL treat every Codex command as untrusted input.

**Expected Capability.** The Codex Plugin MAY:
- Accept integration triggers from a Codex-compatible CLI and translate them into Foundation Capabilities.
- Emit structured results (text, JSON, exit codes) back to the CLI.
- Read Codex-managed resources (per the Codex integration model) under a `Read Host Adapter Event` Permission.

**Input.**
1. Codex CLI integration trigger (subcommand, args, flags, stdin content).
2. Codex-managed resource events.
3. Foundation Runtime context.

**Output.**
1. Foundation Evidence records emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every Codex invocation.
3. Structured results (stdout, exit code, structured JSON) under the granted Permission.

**Security Constraints.**
1. The Plugin SHALL treat every Codex CLI invocation as untrusted input and SHALL validate args and stdin against declared schemas.
2. The Plugin SHALL declare the set of CLI subcommands it serves in its Manifest; undeclared subcommands receive `Permission-Denied`.
3. The Plugin SHALL NOT execute arbitrary shell code beyond the Codex CLI's own model.
4. The Plugin SHALL NOT forward Codex-bearer tokens or session credentials beyond the declared scope.
5. The Plugin SHALL redact secret-bearing fields (API keys, environment variables, stdin payloads) from Audit hooks.
6. The Plugin SHALL audit every Codex invocation with a digest.

---

### §8.6 VSCode Plugin

**Purpose.** A Plugin that adapts the VSCode host (Visual Studio Code, including forks such as VSCodium, code-server, and OpenVSCode Server) to the Foundation Plugin SDK. The VSCode Plugin surfaces VSCode extension events, command invocations, and editor-state changes as Foundation Evidence and emits Audit hooks for every operation.

**Integration Boundary.** The Plugin integrates through VSCode's extension model: an extension runs in a Node.js-based Extension Host process under the VSCode extension sandbox; the Foundation's Runtime is contacted via a declared local endpoint, IPC, or message bus. The Plugin SHALL treat every editor event as untrusted input.

**Expected Capability.** The VSCode Plugin MAY:
- Receive extension events (extension activation, command invocations, editor changes, file open/close, workspace changes) and translate them into Foundation Evidence.
- Emit structured results back to the editor (status bar items, output channel entries, decorations, webviews) under the granted Permission.
- Read declared workspace resources (files, settings) under the granted Permission.

**Input.**
1. VSCode extension event (activation, command, editor change, file event, workspace event).
2. Foundation Runtime context.

**Output.**
1. Foundation Evidence records emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every extension event.
3. Structured UI elements (status bar, output channel, decorations, webview updates) under the granted Permission.

**Security Constraints.**
1. The Plugin SHALL execute only within the VSCode Extension Host sandbox; the Plugin SHALL NOT escape via Node.js `child_process`, `require('fs')` outside the declared scope, or other escape mechanisms.
2. The Plugin SHALL declare the set of VSCode commands and events it serves in its Manifest; undeclared commands or events receive `Permission-Denied`.
3. The Plugin SHALL NOT execute arbitrary code in response to a workspace event.
4. The Plugin SHALL NOT forward VSCode-bearer tokens, Git credentials, or session credentials beyond the declared scope.
5. The Plugin SHALL redact secret-bearing fields from Audit hooks.
6. The Plugin SHALL audit every extension event with a digest.

---

### §8.7 Cursor Plugin

**Purpose.** A Plugin that adapts the Cursor host (Cursor IDE, an AI-augmented VSCode fork) to the Foundation Plugin SDK. The Cursor Plugin surfaces Cursor extension events, AI-completion events, and editor-state changes as Foundation Evidence and emits Audit hooks for every operation.

**Integration Boundary.** The Plugin integrates through Cursor's extension model: Cursor follows the VSCode extension model (§8.6) with additional Cursor-specific AI-completion events. The Foundation's Runtime is contacted through a declared local endpoint or IPC. The Plugin SHALL treat every editor event as untrusted input.

**Expected Capability.** The Cursor Plugin MAY:
- Receive Cursor extension events (extension activation, AI-completion events, command invocations, editor changes) and translate them into Foundation Evidence.
- Emit structured results back to the editor (status bar items, AI-completion suggestions, decorations, output channel entries) under the granted Permission.
- Read declared workspace resources under the granted Permission.

**Input.**
1. Cursor extension event (activation, AI completion, command, editor change, workspace change).
2. Foundation Runtime context.

**Output.**
1. Foundation Evidence records emitted via the Runtime.
2. Foundation Audit hooks (per `§5.2`) for every event.
3. Structured UI elements (status bar, completion items, decorations, output channel) under the granted Permission.

**Security Constraints.**
1. The Plugin SHALL inherit all VSCode-plugin Security Constraints (§8.6), as Cursor follows the VSCode extension model.
2. The Plugin SHALL declare the set of Cursor-specific events and AI-completion channels it serves in its Manifest; undeclared events or channels receive `Permission-Denied`.
3. The Plugin SHALL redact AI-completion context that contains secret-bearing fields from Audit hooks.
4. The Plugin SHALL audit every Cursor event with a digest, including the AI-completion context digest.
5. The Plugin SHALL NOT relay AI-completion results to a third-party host beyond a declared `Restricted Network Access` Permission with declared endpoints.

---

## §9. Compatibility

### §9.1 Version Compatibility

A Plugin declares its Compatibility Profile (`§5.3`). Compatibility is enforced as:

- **Foundation-version compatibility.** A Plugin bound to `Plugin-Foundation-Version = X.Y.Z` is compatible with Foundation versions `>= X.Y.Z` and `< (Plugin-SDK-Version.Major).0.0` (a Plugin bound to `0.1.0` is not automatically compatible with `1.0.0`; a new Foundation Major requires a new Manifest version).
- **Constitution-version compatibility.** A Plugin SHALL NOT invoke clauses past its `Plugin-Constitution-Version`; clauses from a newer Constitution require a new Plugin Version.
- **Plugin-SDK-version compatibility.** A Plugin SHALL be compatible with the Plugin-SDK Version recorded in its Manifest; new SDK versions require a new Plugin Version (`§9.3`).
- **Host-version compatibility.** A Plugin SHALL declare the host platform version range it supports; the host-version range is recorded in §8 platform specifications.

### §9.2 Migration Rules

When a Plugin's compatibility breaks (e.g., a new Foundation Major version, a new Plugin SDK version, or a host platform breaking change), a **Plugin Migration Plan** is required. The Plan declares:

1. The previous Plugin Version.
2. The new Plugin Version.
3. The list of breaking changes (with locator and rationale).
4. The list of artifacts affected (the Plugin instance, its Registration, Validation, Permission Approval, and Audit history).
5. The Migration procedure (per-event re-validation, per-Permission re-approval, re-Activation).

The Plan is filed at a path recorded in `directory-standard.md` §4 (place-holder: `<plugin-root>/MIGRATION-<plugin-id>-<from>-<to>.md`). The Plan is reviewed per `change-control-policy.md` and requires the same Reviewer separation-of-duties rule.

### §9.3 Extension Rules

Per Constitution §13 (Future Extension Policy), Plugin extensions are **additive-only**:

- New Capabilities — additive (a new Capability is added by a new Plugin MINOR version).
- New Permissions — additive (a new Permission class may be defined by a new Plugin MINOR version, but the Foundation SHALL honor the existing default-deny rule for the new Permission class until explicitly granted).
- New Boundary crossing points — additive (new entries in §3.3 may be added by a new Plugin MINOR version).
- New Lifecycle stages — additive (a new stage may be inserted in §4 by a new Plugin MAJOR version, because it is a Protocol change).

**Weakening requires a new FD:**

- Removing an existing Capability from a granted Permission set.
- Lowering the Security Boundary (relaxing §7 constraints).
- Changing the Lifecycle to remove a stage.
- Re-classifying a default-denied Permission as default-allowed.

### §9.4 Plugin Supersession

A Plugin MAY be superseded by a later Plugin. The supersession follows the rules in `governance-model.md` §9:

1. The new Plugin declares `Supersedes: <old-Plugin-ID>` in its Metadata (§5.3).
2. The old Plugin's Status is updated to `Superseded` (header-only edit; content untouched).
3. The old Plugin's `Superseded-By` Metadata field is populated with the new Plugin's ID.

A Superseded Plugin MAY NOT be re-activated except via a new Registration cycle (§4.2) and a new Manifest version.

---

## §10. Cross References

Per Constitution §10 (Cross Reference Policy), this Standard declares the following mandatory references.

### §10.1 Constitution References

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

### §10.2 Standard References

- `directory-standard.md` §4 (top-level layout), §6 (per-class storage), §8 (reserved directories), §10 (path-validation).
- `schema-standard.md` §4 (Evidence), §5 (Report), §6 (Review), §7 (Statistics), §8 (Manifest), §9 (Audit), §10 (Task), §11 (Pack), §12 (Release).
- `pack-standard.md` §3–§17 (Builder Pack — declares the §15.5 Scope model this Standard mirrors in §5.1).
- `runtime-specification.md` §4 (Runtime inputs), §6 (Runtime outputs), §7 (Lifecycle), §8 (Quality Gate Integration), §10 (Runtime Security Boundary — Plugins must honor), §11 (Compatibility).
- `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship), §7 (Review Relationship), §8 (Failure Handling), §9 (Release Quality Gate), §10 (Compatibility).
- `engine-specification.md` §3–§11.
- `sdk-specification.md` §7 (Plugin SDK — Interface Boundary contract this Standard conforms to), §8 (Shared SDK Architecture).

### §10.3 Policy References

- `governance-model.md` §2 (Hierarchy), §6 (Artifact Types), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession).
- `approval-workflow.md`.
- `change-control-policy.md`.
- `disagreement-and-escalation.md`.
- `roles-and-authority.md`.
- `rfc-policy.md`.
- `foundation-decision-policy.md`.
- `adr-policy.md`.

### §10.4 Back-References

This Standard is referenced by:

- *Future Standards.* The next Foundation Standards (Workspace — Task 11; Release — Task 12) MAY reference this Standard.
- *Future Plugin Specifications.* Concrete Plugin instance manifests (e.g., a future `PLUGIN-github-<slug>.md`) SHALL reference this Standard and `sdk-specification.md` §7.
- *Future Plugins.* A concrete Plugin implementation SHALL reference this Standard in its `Related:` Metadata field.

---

## §11. Relationship to Other Artifacts

### §11.1 To the Constitution

This Standard operationalizes the Plugin concept for the Foundation, drawing on Constitution §§1, 3, 5, 9, 10, 11, 12, 13, 15. It does not contradict any clause of the Constitution. If a future Constitution amendment changes a referenced §, this Standard must be updated to reflect the new clause (per `change-control-policy.md`).

### §11.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for the Standards, Audits, Reports, and Reviews produced by this Standard.
- **Schema Standard** — declares the Evidence (§4), Audit (§9), Manifest (§8), Report (§5), Review (§6) schemas that this Standard references.
- **Pack Standard** — declares the Builder Pack and the §15.5 Scope model that this Standard mirrors in §5.1.
- **Runtime Specification** — declares the Runtime that mediates every Plugin invocation (per §2.4 and §3.3).
- **Quality Gate Standard** — declares the six Gates that every Plugin Validation Report and Audit Report applies.
- **Engine Specification** — declares the Engines (Builder, Audit, Evidence, Statistics, Report, Prompt) that consume Plugin-emitted artifacts.
- **SDK Specification** — declares the Plugin SDK (§7) and the Shared SDK Architecture (§8) that this Standard conforms to. This Standard **references** the SDK Specification; it does not duplicate it.

### §11.3 To Future Artifacts

Future artifacts that may reference this Standard include:

- **Workspace Specification** (Task 11) — may declare how Plugins integrate with a Workspace.
- **Foundation Pack instances** (Task 12) — may bundle this Standard and its companion Audit / Report / Review records.
- **Plugin instance specifications** (downstream, post-Foundation) — each Plugin instance SHALL reference this Standard and `sdk-specification.md` §7.
- **Project Plugin instances** (downstream, post-Foundation) — issued by Projects; each SHALL reference this Standard and SHALL conform to the Project Plugin section.

### §11.4 Plugin as Project-Independent Component

This Standard is **technology-neutral** and **project-independent**. No Plugin defined here is owned by any Project; no Plugin is restricted to any Project; no Project-local rule binds a Plugin during the Foundation phase. APES (the first Project) MAY consume a Foundation-defined Plugin post-Foundation, but no Foundation-defined Plugin is APES-specific.

---

## §12. Ratification

This Standard is **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0010-ratify-plugin-specification.md` is created in this Foundation task.

**Ratification path (when invoked by a future Foundation cycle):**

1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition (`Approved`, `Approved with Notes`, `Rejected`, `Blocked`).
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0010-ratify-plugin-specification.md` per `foundation-decision-policy.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.
5. After Ratification, this Standard's `Status:` header field is updated to `Ratified` and its `Version:` may advance per §9.1.

Until `FD-0010` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

> **Note.** No `FD-0010-ratify-plugin-specification.md` is created during Task 10. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action. The Foundation Builder prepares this Standard and the companion Audit / Report / Review; the human Architect reviews it through `REVIEW-FOUNDATION-10-plugin.md`.

> **Note.** This Standard is **technology-neutral**, **project-independent**, and **implementation-independent**. It contains no Plugin source code, no Plugin manifest file, no extension bundle, no MCP server, no VSCode extension, no Cursor extension, no Claude integration, no Codex integration, no GitHub connection, no Obsidian vault modification, no network endpoint, no credential capture, no sandbox implementation, no Engine / Runtime / SDK / Pack implementation. The seven Platform Plugin Specifications are co-equal and contract-only.

---

*End of plugin-specification.md v0.1.0-draft (Draft / In Review).*
