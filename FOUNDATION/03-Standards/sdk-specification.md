# Research-OS Foundation — SDK Specification

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/sdk-specification.md`
**Supersedes:** none
**Related:** Constitution §3 (Design Principles); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); `governance-model.md` §2, §6, §7, §8; `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `directory-standard.md` §4, §6, §8, §10; `schema-standard.md` §4–§12; `pack-standard.md` §3–§17; `runtime-specification.md` §4, §6, §7, §8, §10, §11; `quality-gate-standard.md` §5, §6, §7, §8, §9, §10; `engine-specification.md` §3–§11; `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard declares the canonical *form* of a Foundation **SDK** (Software Development Kit). An SDK is the L5 component that defines an **Interface Boundary** between two Foundation artifacts (or between a Foundation artifact and a Project artifact), exposing a stable set of Inputs and Outputs and Versioning rules. This Standard defines five SDK Specifications — **Project SDK**, **Builder SDK**, **Migration SDK**, **Release SDK**, and **Plugin SDK** — each with Purpose, Interface Boundary, Inputs, Outputs, Dependencies, Versioning, Compatibility, Security Rules, Extension Model.

This Standard does **not** implement any SDK. It does **not** write SDK code. It does **not** publish packages or libraries. It declares the *contract* a conformant SDK must satisfy.

### §1.2 In-Scope

1. The five SDK Specifications (§§3–§7), each declaring the nine required attributes.
2. The shared SDK Architecture (§8): the conceptual model of an Interface Boundary and its relationship to the Foundation Runtime, Engines, and Projects.
3. The SDK Lifecycle (§9): the lifecycle stages an SDK interface contract traverses.
4. SDK Compatibility rules (§10): version surfaces, migration, future extensions (additive-only).
5. Cross-references to Constitution, Standards, and Policies (§11).

### §1.3 Out-of-Scope

1. **SDK implementation** — no source code, no packages, no published libraries.
2. **API implementation** — no REST / GraphQL / RPC / OpenAPI / Protobuf bindings.
3. **CLI / Plugin / Runtime / Engine implementation** — none.
4. **MCP / agent implementation** — none.
5. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts.
6. **APES migration or Project-specific governance** — APES remains a paused Project.
7. **Sprint execution** — no Sprint is executed in this Foundation task.

---

## §2. Normative Status

### §2.1 Conformance

An implementation is said to **conform to this Standard** if and only if every SDK Specification it claims to satisfy is honored end-to-end (Purpose, Interface Boundary, Inputs, Outputs, Dependencies, Versioning, Compatibility, Security Rules, Extension Model). A partial implementation is **non-conformant**.

### §2.2 Technology-Neutrality

This Standard is **technology-neutral**. It does not bind to any programming language, framework, package manager, serialization format, transport protocol, or operating system. The SDK Specifications are expressed as natural-language contract clauses. A concrete implementation may map these clauses to a specific technology; until such a mapping exists, an SDK is conformant if its behavior matches the natural-language clauses.

### §2.3 Conflict Resolution

If any clause of this Standard conflicts with:
- the Constitution — **the Constitution prevails**;
- an active FD — **the FD prevails**;
- any other Foundation Standard — **the more-specific Standard prevails** for the conflict zone, after cross-reference check;
- a Project-local rule — **the Foundation Standard prevails** (Constitution §1).

---

## §3. Project SDK Specification

### §3.1 Purpose

The **Project SDK** defines the **Interface Boundary** between the Foundation and a Project (such as APES, when it becomes active). It declares how a Project consumes Foundation artifacts, what a Project may and may not invoke, and what the Foundation guarantees to a conformant Project.

### §3.2 Interface Boundary

The Project SDK Interface Boundary separates **Foundation** (the platform) from **Project** (the tenant). Across this boundary:
- The Foundation exposes: the Runtime, the Engines, the Audit / Review / Report records, the Standards, the Policies.
- The Project consumes: the above, via the Interface Boundary contract.
- The Project may **not** modify Foundation artifacts directly; modification requires an FD (per `foundation-decision-policy.md`).

**Boundary rules:**
1. A Project invocation of Foundation components is mediated by the Runtime (per `runtime-specification.md` §4). Direct invocation is **forbidden**.
2. A Project may read but not write Foundation artifacts (immutability per `governance-model.md` §8).
3. A Project may propose amendments via FRFC (per `rfc-policy.md`) or ADRs (per `adr-policy.md`), but may not unilaterally amend.

### §3.3 Inputs

1. **Project identity** — Project ID, Project name, Project version (per `schema-standard.md` §10).
2. **Foundation registry** — the Constitution, Standards, Policies, FDs available to the Project.
3. **Project scope declaration** — the Project's declared scope, Allowed Files, Forbidden Files (parallel to Foundation §15.5).

### §3.4 Outputs

1. **Project artifact set** — the Project's declared artifacts.
2. **Project Audit hook** — an audit-ready record of Project invocations of Foundation components.
3. **Project Foundation-binding declaration** — a declaration that the Project conforms to the Foundation Interface Boundary.

### §3.5 Dependencies

- `runtime-specification.md` §4 (Runtime — mandatory invocation mediator).
- `engine-specification.md` (Engines — invoked via Runtime).
- `schema-standard.md` §10 (Task), §11 (Pack).
- `pack-standard.md` §3–§17 (Builder Pack — used by Project).
- `quality-gate-standard.md` §5 (Project outputs must satisfy the six Gates).
- `governance-model.md` §6 (artifact types), §8 (immutability).

### §3.6 Versioning

- **Version surface:** `ProjectSDK.Version`, `ProjectSDK.FoundationVersion`, `ProjectSDK.ConstitutionVersion`.
- **Bump triggers:** MAJOR (non-backward-compatible Interface Boundary change); MINOR (additive new Project capability); PATCH (typo fix / clarification).
- **Pre-release tags:** `0.1.0-draft` (initial draft); `0.1.0-rc.1` (reserved for Project RC); `1.0.0` (first Stable Project SDK).

### §3.7 Compatibility

- **Backward:** a Project built against `ProjectSDK.Version = X` continues to work against `X.Y.Z` where `Y ≤ n` and `Z ≤ m` (within MINOR / PATCH).
- **Forward:** `ProjectSDK.Version = X.Y.Z` continues to work against `X.Y.(Z+1)`.
- **Migration:** MAJOR bumps require a Migration Plan (per `quality-gate-standard.md` §10.2).

### §3.8 Security Rules

1. A Project **may not** modify Foundation artifacts (immutability).
2. A Project **may not** invoke Foundation components directly (must go through Runtime).
3. A Project **may not** bypass the Audit Engine (every Project invocation must produce an Audit hook).
4. A Project **may not** declare itself compatible with a Foundation Version that has not been approved (per `governance-model.md` §7).
5. A Project **may not** access the network, execute arbitrary code, or spawn sub-processes outside the Runtime's permission scope (per `runtime-specification.md` §10).

### §3.9 Extension Model

Per Constitution §13 (Future Extension Policy), the Project SDK is extended **additively-only**:
- New Interface Boundary clauses — additive.
- New Project invocation types — additive.
- New Project audit fields — additive.

Weakening an existing Interface Boundary requires a new FD and ratification.

---

## §4. Builder SDK Specification

### §4.1 Purpose

The **Builder SDK** defines the **Interface Boundary** between a Builder (human or agent) and the Foundation's Builder Engine (per `engine-specification.md` §8). It declares the Builder's instructions surface, the Builder's allowed operations, and what the Builder Engine guarantees to the Builder.

### §4.2 Interface Boundary

The Builder SDK Interface Boundary separates **Builder** (the author of subject artifacts) from **Builder Engine** (the executor under §15.5 Scope).

**Boundary rules:**
1. The Builder submits instructions via the Builder Engine (per `engine-specification.md` §8.3), never directly to the Runtime or other Engines.
2. The Builder submits a §15.5 Per-Task Scope Declaration alongside every instruction set; the Builder Engine validates the Scope before producing outputs.
3. The Builder **may not** bypass the self-audit (per `engine-specification.md` §8.7) — every Builder Engine output is self-audited.

### §4.3 Inputs

1. **Builder instruction set** — Mission + Pack + Task + Governance (per `runtime-specification.md` §6).
2. **§15.5 Per-Task Scope Declaration** — Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition.
3. **Builder identity** — Builder ID, Builder role, Builder credentials (per `roles-and-authority.md`).

### §4.4 Outputs

1. **Subject artifacts** — files at the declared paths (Allowed Files only).
2. **Builder Audit hook** — an audit-ready record of the Builder's compliance with its own §15.5 Scope (per `engine-specification.md` §8.4).
3. **Builder Manifest** — Manifest entry per `schema-standard.md` §8.

### §4.5 Dependencies

- `engine-specification.md` §8 (Builder Engine — the executor).
- `pack-standard.md` §3–§17 (Builder Pack).
- `runtime-specification.md` §6 (Runtime inputs).
- `quality-gate-standard.md` §5, §6 (Gates + self-audit).
- `directory-standard.md` §4, §6, §8, §10 (storage paths).
- `schema-standard.md` §8 (Manifest), §9 (Audit).
- Constitution §15.5 (Per-Task Scope Declaration).

### §4.6 Versioning

- **Version surface:** `BuilderSDK.Version`, `BuilderSDK.FoundationVersion`, `BuilderSDK.ConstitutionVersion`.
- **Bump triggers:** MAJOR (non-backward-compatible Builder instruction surface change); MINOR (additive new Builder capability); PATCH (typo fix / clarification).
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Builder SDK RC), `1.0.0` (first Stable Builder SDK).

### §4.7 Compatibility

- **Backward:** a Builder built against `BuilderSDK.Version = X` continues to work against `X.Y.Z` where `Y ≤ n` and `Z ≤ m` (within MINOR / PATCH).
- **Forward:** `BuilderSDK.Version = X.Y.Z` continues to work against `X.Y.(Z+1)`.
- **Migration:** MAJOR bumps require a Migration Plan.

### §4.8 Security Rules

1. The Builder **may not** approve, audit, release, or sign off on its own outputs (separation of duties per Constitution §5).
2. The Builder **may not** create Forbidden Files (per §15.5 Scope).
3. The Builder **may not** execute any source artifact's content.
4. The Builder **may not** modify any artifact outside its Allowed Files list.
5. The Builder **may not** spawn sub-processes, access the network, or commit code without explicit Runtime mediation.
6. The Builder **may not** proceed past its declared Stop Condition (per §15.5).
7. The Builder **may not** auto-commit, auto-push, or auto-tag via git.

### §4.9 Extension Model

- New Builder instruction types — additive.
- New §15.5 Scope schema fields — additive.
- New Builder Audit hook fields — additive.

Weakening requires a new FD.

---

## §5. Migration SDK Specification

### §5.1 Purpose

The **Migration SDK** defines the **Interface Boundary** for migrating Foundation artifacts across Foundation Versions, Constitution Versions, or Standard Versions. It declares how a Migration is initiated, what the migration tool may modify, and what the Foundation guarantees during migration.

### §5.2 Interface Boundary

The Migration SDK Interface Boundary separates **Pre-Migration** (the old version) from **Post-Migration** (the new version).

**Boundary rules:**
1. A Migration is initiated only via an FD (per `foundation-decision-policy.md`) — ad-hoc migrations are **forbidden**.
2. The Migration may modify artifacts only per the Migration Plan filed alongside the FD.
3. The Migration may not invent artifacts (no fabrication).
4. The Migration may not bypass the Quality Gate (every migrated artifact is re-audited per `quality-gate-standard.md` §5).
5. The Migration produces a Migration Record (input list, output list, diff list, audit verdict per artifact) per `schema-standard.md` §4 (Evidence) and §9 (Audit).

### §5.3 Inputs

1. **Migration Plan** — the FD's Migration Plan (per `quality-gate-standard.md` §10.2).
2. **Source artifact set** — the artifacts to migrate (with declared previous version).
3. **Target artifact set** — the empty slots where migrated artifacts will be written.
4. **Migration metadata** — Migration ID, Migration date, Migration executor identity.

### §5.4 Outputs

1. **Migrated artifacts** — the artifacts at the new version, with updated header fields.
2. **Migration Record** — input list, output list, diff list, audit verdict per artifact.
3. **Migration Audit hook** — an audit-ready record of the Migration.

### §5.5 Dependencies

- `foundation-decision-policy.md` (FD is the gating mechanism).
- `change-control-policy.md` (Change-control procedure).
- `quality-gate-standard.md` §10.2 (Migration Plan format).
- `schema-standard.md` §4 (Evidence), §9 (Audit).
- `directory-standard.md` §4, §6 (storage paths).
- `governance-model.md` §7 (status lifecycle — migrated artifacts may transition status).

### §5.6 Versioning

- **Version surface:** `MigrationSDK.Version`, `MigrationSDK.FoundationVersion`, `MigrationSDK.ConstitutionVersion`.
- **Bump triggers:** MAJOR (non-backward-compatible Migration Plan schema change); MINOR (additive new Migration capability); PATCH (typo fix / clarification).
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Migration SDK RC), `1.0.0` (first Stable Migration SDK).

### §5.7 Compatibility

- **Backward:** the Migration SDK continues to support all previous MAJOR versions for which a Migration Plan exists.
- **Forward:** a Migration Plan is required for any new MAJOR version bump.
- **Migration:** when the Migration SDK itself changes, a Migration-of-Migration-SDK Plan is required.

### §5.8 Security Rules

1. The Migration **may not** be initiated without an FD (no ad-hoc migrations).
2. The Migration **may not** invent artifacts (no fabrication).
3. The Migration **may not** modify artifacts outside the Migration Plan scope.
4. The Migration **may not** bypass the Quality Gate (every migrated artifact is re-audited).
5. The Migration **may not** execute any artifact's content.
6. The Migration **may not** spawn sub-processes, access the network, or perform git operations outside the explicit Migration Plan.

### §5.9 Extension Model

- New Migration Plan fields — additive.
- New Migration Record sections — additive.
- New Migration verification strategies — additive.

Weakening requires a new FD.

---

## §6. Release SDK Specification

### §6.1 Purpose

The **Release SDK** defines the **Interface Boundary** between the Foundation Release Manager (per Constitution §5) and the Foundation Release artifacts (per `schema-standard.md` §12 Release Schema). It declares how a Release is initiated, what the Release Manager may modify, and what the Foundation guarantees at Release.

### §6.2 Interface Boundary

The Release SDK Interface Boundary separates **Pre-Release** (the RC aggregate) from **Post-Release** (the Stable artifact set).

**Boundary rules:**
1. A Release is initiated only after a `PASS` RC Quality Gate verdict (per `quality-gate-standard.md` §9.1).
2. The Release Manager **may not** modify RC artifacts during Release (immutability).
3. The Release Manager **may not** skip the Final Approval (per `quality-gate-standard.md` §9.3).
4. The Release produces a Release Manifest (per `schema-standard.md` §12) and a Release Record.
5. The Release may not be reversed except via a new Release cycle (Release reversal is itself a Release).

### §6.3 Inputs

1. **RC aggregate** — the set of `Approved` artifacts proposed for release (per `quality-gate-standard.md` §9.1).
2. **Release Plan** — target version, target date, Release Manager identity.
3. **Release Manifest template** — per `schema-standard.md` §12 (Release Schema).

### §6.4 Outputs

1. **Release Manifest** — at `FOUNDATION/06-Reports/RELEASE-<release-id>.md` (per `schema-standard.md` §12).
2. **Release Record** — at `FOUNDATION/07-Reviews/REVIEW-<release-id>.md` (per `schema-standard.md` §6).
3. **Stable artifact set** — the artifacts whose status transitions from `RC Verified` to `Stable`.

### §6.5 Dependencies

- `quality-gate-standard.md` §9 (Release Quality Gate — gating mechanism).
- `schema-standard.md` §12 (Release Schema), §6 (Review Schema), §8 (Manifest Schema).
- `directory-standard.md` §6 (storage paths).
- `governance-model.md` §7 (status lifecycle).
- `foundation-decision-policy.md` (FD for Stable release).
- `change-control-policy.md` (Change-control for Release).
- Constitution §5 (Role Model — Release Manager role).
- Constitution §14 (Success Criteria — Stable milestone).

### §6.6 Versioning

- **Version surface:** `ReleaseSDK.Version`, `ReleaseSDK.FoundationVersion`, `ReleaseSDK.ConstitutionVersion`.
- **Bump triggers:** MAJOR (non-backward-compatible Release Manifest schema change); MINOR (additive new Release capability); PATCH (typo fix / clarification).
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Foundation RC), `1.0.0` (first Stable Foundation release — gated by Task 12).

### §6.7 Compatibility

- **Backward:** a Release Manifest at `X.Y.Z` remains valid as long as the underlying Foundation Version has not changed in a breaking way.
- **Forward:** new Release Manifest fields are additive.
- **Migration:** MAJOR bumps require a Migration Plan.

### §6.8 Security Rules

1. The Release Manager **may not** modify RC artifacts during Release.
2. The Release Manager **may not** skip the Final Approval.
3. The Release Manager **may not** bypass the RC Quality Gate.
4. The Release Manager **may not** execute any artifact's content during Release.
5. The Release Manager **may not** spawn sub-processes or access the network outside the explicit Release Plan.
6. The Release Manager **may not** perform git operations outside the explicit Release Plan (no auto-tag without Final Approval).

### §6.9 Extension Model

- New Release Manifest sections — additive.
- New Release Record fields — additive.
- New Release verification strategies — additive.

Weakening requires a new FD.

---

## §7. Plugin SDK Specification

### §7.1 Purpose

The **Plugin SDK** defines the **Interface Boundary** between a third-party Plugin (e.g., GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) and the Foundation. It declares how a Plugin integrates with the Foundation, what Permissions it requests, and what the Foundation guarantees to a conformant Plugin.

This SDK Specification is the **form** of the Plugin contract. The concrete Plugin Specifications for GitHub, Obsidian, MCP, Claude, Codex, VSCode, and Cursor are reserved for the Plugin Specification task (Task 10 — forthcoming).

### §7.2 Interface Boundary

The Plugin SDK Interface Boundary separates **Foundation** (the platform) from **Plugin** (the third-party extension).

**Boundary rules:**
1. A Plugin integrates with the Foundation **only** via the Plugin SDK Interface Boundary; direct file system access, network access, or code execution outside the Boundary is **forbidden**.
2. A Plugin declares its requested Permissions (per §7.8); the Foundation grants Permissions on a least-privilege basis.
3. A Plugin may not modify Foundation artifacts (immutability).
4. A Plugin may not invoke Foundation components directly; invocation must be mediated by the Runtime.
5. A Plugin may not extend the Foundation Interface Boundary unilaterally; extensions require a Plugin Specification amendment (per `change-control-policy.md`).

### §7.3 Inputs

1. **Plugin identity** — Plugin ID, Plugin name, Plugin version, Plugin vendor.
2. **Plugin Permission request** — the set of Permissions the Plugin requests (per §7.8).
3. **Plugin scope declaration** — Allowed Operations, Forbidden Operations (parallel to Foundation §15.5).
4. **Plugin Foundation-binding declaration** — declaration that the Plugin conforms to the Plugin SDK.

### §7.4 Outputs

1. **Plugin artifact set** — the Plugin's artifacts (UI elements, command handlers, integrations).
2. **Plugin Audit hook** — an audit-ready record of Plugin operations.
3. **Plugin Foundation-binding declaration** — a signed declaration of conformance.

### §7.5 Dependencies

- `runtime-specification.md` §10 (Runtime Security Boundary — Plugin must honor).
- `engine-specification.md` (Engines — Plugin may not invoke directly).
- `quality-gate-standard.md` §5 (Plugin outputs must satisfy the six Gates).
- `schema-standard.md` §4 (Evidence), §9 (Audit).
- `governance-model.md` §8 (immutability).
- Constitution §5 (Role Model — Plugin is a non-human actor; its scope is bounded).

### §7.6 Versioning

- **Version surface:** `PluginSDK.Version`, `PluginSDK.FoundationVersion`, `PluginSDK.ConstitutionVersion`, plus `Plugin.Version`.
- **Bump triggers:** MAJOR (non-backward-compatible Plugin Interface Boundary change); MINOR (additive new Plugin capability); PATCH (typo fix / clarification).
- **Pre-release tags:** `0.1.0-draft`, `0.1.0-rc.1` (reserved for Plugin SDK RC), `1.0.0` (first Stable Plugin SDK).

### §7.7 Compatibility

- **Backward:** a Plugin built against `PluginSDK.Version = X` continues to work against `X.Y.Z` where `Y ≤ n` and `Z ≤ m` (within MINOR / PATCH).
- **Forward:** `PluginSDK.Version = X.Y.Z` continues to work against `X.Y.(Z+1)`.
- **Migration:** MAJOR bumps require a Migration Plan.

### §7.8 Permission Model

A Plugin declares the Permissions it requests. The Foundation grants Permissions on a **least-privilege** basis. A Plugin **may not** perform any operation for which it has not been granted Permission.

**Permission classes:**
1. **Read Foundation Artifacts** — read-only access to designated Foundation files.
2. **Emit Evidence** — produce Evidence records on behalf of the user.
3. **Invoke Runtime-mediated Components** — invoke Foundation components via the Runtime, never directly.
4. **No Network** — by default, a Plugin has no network access; explicit Permission required.
5. **No Code Execution** — by default, a Plugin may not execute arbitrary code; explicit Permission required.
6. **No File System Writes Outside Scope** — by default, a Plugin may not write to disk outside its declared scope; explicit Permission required.
7. **No Git Operations** — by default, a Plugin may not perform git operations; explicit Permission required.

### §7.9 Extension Model

- New Permission classes — additive.
- New Plugin integration points — additive.
- New Plugin Audit hook fields — additive.

Weakening requires a new FD.

---

## §8. Shared SDK Architecture

### §8.1 Conceptual Model

Every SDK conforms to a single conceptual model:

```
Producer (Foundation / Engine / Builder / Release Manager / Migration tool / Project)
       │
       │  writes
       ▼
Interface Boundary (declared in this Standard)
       │
       │  reads
       ▼
Consumer (Builder / Project / Migration tool / Release Manager / Plugin)
```

The Interface Boundary is **bidirectional** (each SDK may declare both producer-side and consumer-side clauses). The Boundary is **declarative** (the SDK declares the Boundary; the implementation conforms to the declaration).

### §8.2 SDK-to-Runtime Relationship

Every SDK is mediated by the Runtime (per `runtime-specification.md` §4). The Runtime enforces the Interface Boundary at every invocation. A Producer or Consumer that bypasses the Runtime is in violation of the SDK contract.

### §8.3 SDK-to-Engine Relationship

Engines (per `engine-specification.md`) operate under the Runtime. SDKs invoke Engines only via the Runtime; direct SDK-to-Engine calls are **forbidden** (separation of duties + audit trail).

### §8.4 SDK-to-Project Relationship

A Project SDK (§3) is the only SDK that defines an Interface Boundary with a Project. All other SDKs operate within the Foundation. A Project that bypasses the Project SDK is in violation of Foundation governance.

### §8.5 SDK Audit Trail

Every SDK invocation **must** produce an audit-ready record (per `schema-standard.md` §9) declaring: the SDK identity, the invocation context, the Inputs / Outputs, the Boundary clauses invoked, and the outcome.

---

## §9. SDK Lifecycle

The SDK Lifecycle declares the stages an Interface Boundary contract traverses:

1. **Propose** — an FRFC proposes a new SDK Interface Boundary (per `rfc-policy.md`).
2. **Draft** — the SDK Specification is drafted as a Foundation Standard.
3. **Review** — the Standard is reviewed per `quality-gate-standard.md` §4 (Review Gate).
4. **Approve** — the human Architect signs the Review Record.
5. **Ratify** — an FD ratifies the Standard (per `foundation-decision-policy.md`).
6. **Active** — the SDK is active and conformant implementations may be built.
7. **Deprecated** — when a successor SDK is ratified; the SDK enters `Deprecated` status (per `governance-model.md` §7 and Constitution §12).
8. **Frozen** — when no further changes are permitted; only security updates.
9. **Archived** — when the SDK is no longer supported.

The Foundation `v1.0.0-rc.1` RC gate (reserved for Task 12) applies to SDK Specifications as to all Foundation Standards.

---

## §10. Compatibility

### §10.1 Version Surfaces

Every SDK declares four version surfaces (per `runtime-specification.md` §11):

- `SDK.Version` — the SDK's own SemVer version.
- `SDK.FoundationVersion` — the Foundation Version it targets.
- `SDK.ConstitutionVersion` — the Constitution Version it honors.
- (For Plugin SDK only) `Plugin.Version` — the Plugin's own version.

### §10.2 Migration Rules

A non-backward-compatible change (MAJOR SemVer bump) requires a Migration Plan per `quality-gate-standard.md` §10.2. The Plan declares the previous version, the new version, the breaking changes, the affected SDKs / Projects / Plugins, and the Migration procedure.

### §10.3 Future Extensions

Per Constitution §13, future SDK extensions are **additive-only**:
- New Interface Boundary clauses, new input/output types, new Permission classes, new lifecycle stages — additive.
- Existing Interface Boundary clauses, types, Permissions, stages may not be removed or weakened.
- A weakening requires a new FD and ratification per `foundation-decision-policy.md`.

---

## §11. Cross References

Per Constitution §10 (Cross Reference Policy), this Standard declares the following mandatory references.

**Constitution references:** §§1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15.3, 15.4, 15.5.

**Standard references:**
- `directory-standard.md` §4, §6, §8, §10
- `schema-standard.md` §4 (Evidence), §5 (Report), §6 (Review), §7 (Statistics), §8 (Manifest), §9 (Audit), §10 (Task), §11 (Pack), §12 (Release)
- `pack-standard.md` §3–§17
- `runtime-specification.md` §4, §6, §7, §8, §10, §11
- `quality-gate-standard.md` §5, §6, §7, §8, §9, §10
- `engine-specification.md` §3–§11

**Policy references:** `governance-model.md` §2/§6/§7/§8; `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`.

**Back-references (this Standard is referenced by):**
- (none yet — this Standard is new at `0.1.0-draft`; back-references will be added by the Plugin Specification Task 10)

---

## §12. Relationship to Other Artifacts

### §12.1 To the Constitution

This Standard operationalizes the SDK concept under Constitution §§1, 5, 11, 13, and 15. It does not contradict any clause of the Constitution.

### §12.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for SDK Specifications.
- **Schema Standard** — declares the schemas (Evidence, Audit, Manifest, Release, Pack, Task) that SDKs consume and emit.
- **Pack Standard** — declares the Builder Pack, which is consumed by the Builder SDK and the Project SDK.
- **Runtime Specification** — declares the Runtime, which mediates every SDK invocation.
- **Quality Gate Standard** — declares the six Gates, which every SDK output must satisfy.
- **Engine Specification** — declares the Engines, which are invoked via the Runtime (and therefore indirectly via SDKs).

### §12.3 To Future Artifacts

Future artifacts that may reference this Standard include the **Plugin Specification** (Task 10, forthcoming — declares the concrete Plugin Specifications for GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) and the **Workspace Specification** (Task 11, forthcoming).

---

## §13. Ratification

This Standard is **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0009-ratify-sdk-specification.md` is created in this Foundation task.

**Ratification path:**
1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition.
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0009-ratify-sdk-specification.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.

Until `FD-0009` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

---

*End of sdk-specification.md v0.1.0-draft (Draft / In Review).*