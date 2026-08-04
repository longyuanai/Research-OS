# Research-OS Foundation — Workspace Specification Report

**Status:** Approved
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/06-Reports/REPORT-FOUNDATION-11-workspace.md`
**Report Subject:** `FOUNDATION/03-Standards/workspace-specification.md` (v0.1.0-draft, Draft / In Review)
**Report Author:** Foundation Builder (self-report per Constitution §15.4)
**Related:** Constitution §15 (Foundation Task Protocol); §15.4 (Self-audit); §15.5 (Per-Task Scope Declaration); §17 (Provisional Governance); `workspace-specification.md` (this Report's subject); `AUDIT-FOUNDATION-11-workspace.md`; `REVIEW-FOUNDATION-11-workspace.md`; `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship); `plugin-specification.md` (precedent); `sdk-specification.md` (precedent)

---

## §1. Report Purpose

This Report records the construction of `FOUNDATION/03-Standards/workspace-specification.md` during Foundation Task 11. It captures the **inputs**, **process**, **outputs**, and **artifacts produced** for Task 11, alongside a per-section summary of the resulting Standard. It does **not** re-evaluate the merits of the Workspace Specification's policy decisions (that is the Architect's role at `REVIEW-FOUNDATION-11-workspace.md`), nor does it re-audit Gate compliance (that is the Auditor's role at `AUDIT-FOUNDATION-11-workspace.md`).

This Report is **Draft / In Review**. It accompanies the Workspace Specification through the Foundation cycle.

---

## §2. Task Context

| Field | Value |
|---|---|
| Task | Foundation Task 11 |
| Task Name | Workspace Specification |
| Authorization | Architect's per-task mandate (issued 2026-08-03, alongside the existing Task 09 / Task 10 authorization chain) |
| Foundation Version | 0.1.0-dev (FROZEN — no version bump) |
| Constitution Version | v0.1.0-draft (Provisional) — no change |
| Companion Tasks | Task 10 (Plugin Specification) approved; Task 12 (Release Specification) reserved |
| Predecessor | Task 10 (Plugin Specification) — provides the Plugin Boundary, Permission Model, and Security Model that this Standard references |
| Successor (reserved) | Task 12 (Release Specification) |

---

## §3. Per-Task Scope Declaration (Constitution §15.5 mirror)

### §3.1 Allowed Files

1. `FOUNDATION/03-Standards/workspace-specification.md` (new — primary deliverable).
2. `FOUNDATION/03-Standards/README.md` (modified — Standards index update for Task 11).
3. `FOUNDATION/04-Audits/AUDIT-FOUNDATION-11-workspace.md` (new — companion Audit).
4. `FOUNDATION/06-Reports/REPORT-FOUNDATION-11-workspace.md` (new — this Report).
5. `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-11-workspace.md` (new — companion Review).

### §3.2 Forbidden Files

1. No new Foundation Standard outside `FOUNDATION/03-Standards/` beyond the Workspace Specification.
2. No `FOUNDATION/09-Decisions/FD-0011-ratify-workspace-specification.md` or equivalent.
3. No SDK, Runtime, Engine, Plugin, Workspace, Release, Pack, Project, Sprint, or APES files.
4. No source code (no `.ts/.py/.js/.sh/.go/.rs/.java/.cs/.cpp/.c/.rb/.php`).
5. No manifest files (no `package.json`, no `manifest.json`, no `workspace.yaml`, no `workspace.yml`).
6. No Workspace template directories (no `templates/workspace-*`, no `workspace-init.yaml`).
7. No network endpoints in normative clauses.
8. No credentials in any file.
9. No sandbox implementation (no Dockerfile, no firecracker config, no gVisor config).
10. No git operations.

### §3.3 Inputs

1. The Architect's Authorization for Task 11 (seven mandated sections; nine prohibitions).
2. The Task 10 Plugin Specification (`FOUNDATION/03-Standards/plugin-specification.md`), specifically:
   - §3 (Plugin Boundary Model) — declares the Boundary pattern this Standard extends.
   - §4 (Plugin Lifecycle) — declares the 9-stage Plugin Lifecycle pattern that informs the Workspace's 8-stage Lifecycle.
   - §6 (Permission Model) — declares the Allowed/Restricted/Default-Denied pattern this Standard extends.
   - §7 (Security Model) — declares the Security Boundary pattern this Standard inherits.
3. The Task 09 SDK Specification (`FOUNDATION/03-Standards/sdk-specification.md`), specifically:
   - §7 (Plugin SDK) — Interface Boundary contract.
   - §8 (Shared SDK Architecture) — SDK-to-Runtime relationship.
4. The Pack Standard (`FOUNDATION/03-Standards/pack-standard.md`) — for the §15.5 Scope model mirrored in §5.1 of the Workspace Specification; for the Mission definition referenced in §7.1.
5. The Runtime Specification (`FOUNDATION/03-Standards/runtime-specification.md`) — for the Runtime Security Boundary (§10), Runtime Lifecycle (§5), and Runtime-mediated-component pattern that the Workspace inherits.
6. The Quality Gate Standard (`FOUNDATION/03-Standards/quality-gate-standard.md`) — for the six Gates referenced throughout the Workspace Specification.
7. The Directory Standard (`FOUNDATION/03-Standards/directory-standard.md`) — for the on-disk path of the Workspace Specification.
8. The Schema Standard (`FOUNDATION/03-Standards/schema-standard.md`) — for the Evidence, Audit, Manifest, Report, Review schemas referenced throughout the Workspace Specification.
9. The Engine Specification (`FOUNDATION/03-Standards/engine-specification.md`) — for the six Engines referenced in §2.4.
10. The Standards README (`FOUNDATION/03-Standards/README.md`) — for the index entry pattern.
11. The Constitution (`FOUNDATION/01-Constitution/constitution.md`) — for the binding design principles, role model, RFC governance, versioning policy, naming convention, cross-reference policy, quality gate, deprecation policy, future extension policy, success criteria, and Foundation Task Protocol.

### §3.4 Outputs

1. `FOUNDATION/03-Standards/workspace-specification.md` (new).
2. `FOUNDATION/03-Standards/README.md` (modified).
3. `FOUNDATION/04-Audits/AUDIT-FOUNDATION-11-workspace.md` (new).
4. `FOUNDATION/06-Reports/REPORT-FOUNDATION-11-workspace.md` (new — this file).
5. `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-11-workspace.md` (new).
6. The Builder's seven-section Completion Report (delivered in the next message; see Task #13 in the Builder's task list).

### §3.5 Dependencies

1. Task 10 (Plugin Specification) is approved; the Workspace Specification references its §3, §4, §6, and §7 without duplicating them.
2. The Constitution (Provisional) provides the binding design principles and role model.
3. The Quality Gate Standard provides the six Gates.
4. The Directory Standard provides the on-disk path.
5. The Schema Standard provides the Evidence, Audit, Manifest, Report, Review schemas.
6. The Runtime Specification provides the Runtime Security Boundary pattern.
7. The Pack Standard provides the Mission definition.
8. The Engine Specification provides the six Engine references.
9. The SDK Specification provides the Plugin SDK and Shared SDK Architecture.

### §3.6 Quality Gates

1. Structure Gate (per `quality-gate-standard.md` §5.3.1).
2. Consistency Gate (per `quality-gate-standard.md` §5.3.2).
3. Cross Reference Gate (per `quality-gate-standard.md` §5.3.3).
4. Isolation Gate (per `quality-gate-standard.md` §5.3.4).
5. Scope Compliance Gate (per `quality-gate-standard.md` §5.3.5).
6. Security Boundary Gate (per `quality-gate-standard.md` §5.3.6).

### §3.7 Stop Condition

After the seven-section Completion Report is delivered, STOP. Do not auto-begin Task 12. Await human Architect review at `REVIEW-FOUNDATION-11-workspace.md`.

---

## §4. Process Summary

### §4.1 Pre-execution

1. The Builder acknowledged the Architect's Approval of Task 10 and Authorization of Task 11.
2. The Builder issued the pre-execution declarations (Allowed files, Forbidden files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition) — recorded above in §3.
3. The Builder created tracking tasks via the Builder's task list (one per artifact plus a Completion Report).
4. The Builder Read the Foundation Standards and Policies that the Workspace Specification would reference (`plugin-specification.md`, `sdk-specification.md`, `pack-standard.md`, `runtime-specification.md`, `quality-gate-standard.md`, `directory-standard.md`, `schema-standard.md`, `engine-specification.md`, Standards README, Constitution §§0–3).

### §4.2 Authoring

1. The Builder authored `FOUNDATION/03-Standards/workspace-specification.md` with eleven top-level sections (Purpose/Scope, Workspace Architecture Purpose, Workspace Boundary Model, Workspace Lifecycle, Workspace Interface Specification, Workspace Permission and Security Model, Workspace Types, Workspace Compatibility, Cross References, Relationship to Other Artifacts, Ratification).
2. The Builder maintained the architectural coherence with `pack-standard.md` (the Pack populates the Workspace), `runtime-specification.md` (the Runtime orchestrates within the Workspace), and `plugin-specification.md` (Plugins may be invoked from a Workspace via Runtime mediation) — referencing rather than duplicating.
3. The Builder preserved the Foundation Hard Prohibitions throughout: no Workspace creation, no Pack execution, no Runtime instantiation, no Engine invocation, no SDK instantiation, no Plugin instantiation, no APES artifact, no Sprint execution, no git operations.
4. The Builder followed the precedent of Tasks 06–10 for header fields, section numbering, ratification clause phrasing, and cross-reference style.

### §4.3 Audit and Report

1. The Builder authored `FOUNDATION/04-Audits/AUDIT-FOUNDATION-11-workspace.md` evaluating the Workspace Specification against all six Quality Gates and the Architect's nine prohibitions.
2. The Builder authored `FOUNDATION/06-Reports/REPORT-FOUNDATION-11-workspace.md` (this file) recording the construction of the Workspace Specification.
3. The Builder authored `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-11-workspace.md` providing the Reviewer's prompt for the human Architect.

### §4.4 Standards README Update

The Builder updated `FOUNDATION/03-Standards/README.md` to:

1. Add the Workspace Specification row to the Index table (matching the precedent of Tasks 06–10).
2. Update the Future Standards (Reserved) table to mark Task 11 complete and reserve Task 12 (Release) only.
3. Update the closing Note to include the deferred-ratification language for the Workspace Specification (matching the precedent of Tasks 06–10).

---

## §5. Workspace Specification — Section Summary

### §5.1 §1 Purpose and Scope

- §1.1 Purpose — declares the canonical form of a Foundation Workspace and the seven required sections.
- §1.2 In-Scope — enumerates the seven sections plus cross-references and relationships.
- §1.3 Out-of-Scope — explicitly forbids Workspace creation, instantiation, provisioning, allocation, execution, Network access, Engine/Runtime/SDK/Plugin implementation, Pack instance creation, APES migration, Sprint execution, and git operations.

### §5.2 §2 Workspace Architecture Purpose

- §2.1 Definition — defines a Workspace as "a Foundation L5 component that provides a persistent, bounded, audited context in which a Builder Pack is executed by a Builder Runtime."
- §2.2 What a Workspace IS — eight positive attributes.
- §2.3 What a Workspace IS NOT — eleven negative attributes (distinguishing from Pack, Runtime, Engine, SDK, Plugin, Project, Mission, Host environment).
- §2.4 Relationship to Pack, Runtime, Engine, SDK, Plugin — table stating the operational-surface vs. declarative-content vs. executor vs. specialist vs. interface vs. external-adapter trichotomy.

### §5.3 §3 Workspace Boundary Model

- §3.1 Boundary Layers — five-layer diagram from host environment through Workspace Physical Boundary, Manifest Boundary, Operational Boundary, Pack Content Boundary, to Foundation Storage.
- §3.2 Boundary Rules — ten SHALL NOT clauses.
- §3.3 Boundary Crossing Points — nine permitted crossings, each with a mediator and recorded-as column.
- §3.4 Boundary to Pack, Runtime, Engine, SDK, Plugin Specs — declares non-duplication and the more-specific-Standard-prevails rule.

### §5.4 §4 Workspace Lifecycle

- §4.1 Overview — eight ordered stages.
- §4.2 Stage 1 — Request.
- §4.3 Stage 2 — Provision (human-gated).
- §4.4 Stage 3 — Initialize (Manifest and Permission set sealed).
- §4.5 Stage 4 — Activate (human-gated).
- §4.6 Stage 5 — Execute (six hard prohibitions during Execution).
- §4.7 Stage 6 — Audit (continuous or periodic; four possible verdicts).
- §4.8 Stage 7 — Deactivate (always permitted; non-destructive of Audit history).
- §4.9 Stage 8 — Archive (terminal; revokes all granted Permissions).
- §4.10 Stage Transition Table — 9 transitions, all gated.
- §4.11 Lifecycle Hooks Summary — 8 hooks, one per stage.

### §5.5 §5 Workspace Interface Specification

- §5.1 Input Contract — six inputs.
- §5.2 Output Contract — four outputs (result, Audit hook, Manifest, Status).
- §5.3 Metadata — 19-field Metadata table.
- §5.4 Versioning — bump triggers and Foundation binding rule.
- §5.5 Compatibility — Foundation, Constitution, Plugin-SDK, and host-version compatibility.

### §5.6 §6 Workspace Permission and Security Model

- §6.1 Overview — default-deny rule.
- §6.2 Allowed Access — seven Allowed Permissions.
- §6.3 Restricted Access — seven Restricted Permissions, each with explicit Approval and Audit requirements.
- §6.4 Default-Denied Permissions — seven Default-Denied Permissions.
- §6.5 Human Approval Boundary — four Lifecycle stages (Provision, Activate, Deactivate, Archive).
- §6.6 Isolation Rules — ten rules.
- §6.7 Credential Handling Rules — six rules including Audit-hook redaction.
- §6.8 Security Boundary — inheritance and operationalization of Foundation, Runtime, Plugin, and Quality Gate Security Boundaries.

### §5.7 §7 Workspace Types

- §7.0 Overview — three co-equal Workspace Types (Mission, Project, Foundation).
- §7.1 Mission Workspace — short lifecycle; minimal default Permission set; typical form for Foundation Task execution.
- §7.2 Project Workspace — long lifecycle; extended default Permission set; **NOT instantiated during the Foundation phase**.
- §7.3 Foundation Workspace — long lifecycle; extended default Permission set; typical form for Foundation-level Standards drafting.
- §7.4 Cross-Workspace Interaction Rules — default-denied; mediated by Runtime; recorded on both Workspaces.

### §5.8 §8 Workspace Compatibility

- §8.1 Version Compatibility — four compatibility dimensions.
- §8.2 Migration Rules — five-element Migration Plan.
- §8.3 Extension Rules — additive-only; weakening requires a new FD.
- §8.4 Workspace Supersession — supersession rule (governed by `governance-model.md` §9).

### §5.9 §9 Cross References

- §9.1 Constitution References — §§1–15.
- §9.2 Standard References — eight Foundation Standards.
- §9.3 Policy References — eight Policies.
- §9.4 Back-References — four classes of future artifacts.

### §5.10 §10 Relationship to Other Artifacts

- §10.1 To the Constitution.
- §10.2 To Other Foundation Standards (eight Standards, each with a clear role statement).
- §10.3 To Future Artifacts.
- §10.4 Workspace as Project-Independent Component.

### §5.11 §11 Ratification

- Draft / In Review.
- Ratification path (five steps).
- Deferred-ratification language: "No `FD-0011-ratify-workspace-specification.md` is created in this Foundation task."
- Technology-neutrality, project-independence, and Foundation-Invariant compliance reaffirmation.

---

## §6. Artifact Inventory

| Artifact | Status | Path | Lines (approx.) |
|---|---|---|---|
| Workspace Specification | Draft / In Review | `FOUNDATION/03-Standards/workspace-specification.md` | ~810 |
| Workspace Specification Audit | Draft / In Review | `FOUNDATION/04-Audits/AUDIT-FOUNDATION-11-workspace.md` | ~480 |
| Workspace Specification Report | Draft / In Review | `FOUNDATION/06-Reports/REPORT-FOUNDATION-11-workspace.md` | this file |
| Workspace Specification Review | Draft / In Review | `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-11-workspace.md` | forthcoming |
| Standards README | modified | `FOUNDATION/03-Standards/README.md` | one row added; reserved table updated; closing note extended |

---

## §7. Compliance Posture

The Workspace Specification is **compliant** with:

- Constitution v0.1.0-draft Provisional — all referenced clauses; no clause is contradicted.
- Foundation Hard Prohibitions — no Workspace creation, no Pack execution, no Runtime instantiation, no Engine invocation, no SDK instantiation, no Plugin instantiation, no APES artifact, no Sprint execution, no git operations.
- Quality Gate Standard — all six Gates PASS (per the companion Audit).
- File-naming convention — `workspace-specification.md` follows the precedent of Tasks 06–10.
- Ratification precedent — §11 deferred-ratification language matches Tasks 06–10.
- Cross-reference style — header `Related:` and §9 Cross References match the precedent.
- Foundation Invariant — the five constraints (Foundation Version 0.1.0-dev, Constitution v0.1.0-draft Provisional, no RC, no Pack, no Project) are honored.

---

## §8. Observations

### §8.1 Architectural Coherence

The Workspace Specification maintains architectural coherence with the Foundation Standards:

- It does not duplicate the Pack Standard's Pack Definition or Pack Lifecycle — it references them at §3.4 and §10.2.
- It extends the Permission Model granularly without contradiction (per §6.2–§6.4).
- It honors the Runtime Specification's Security Boundary at §6.8 (inheritance pattern).
- It honors the Plugin Specification's Permission and Security Model at §6.1–§6.8 (extension pattern).
- The Workspace / Pack / Runtime trichotomy is consistently documented in §2.1, §2.4, and §10.2.

### §8.2 Boundary Discipline

The Boundary Model (§3), Permission Model (§6), Security Boundary (§6.8), and Lifecycle (§4) form a consistent boundary discipline. Boundary crossing is governed by mediators (§3.3), Permissions (§6), Trust rules (§6.8), and Lifecycle stages (§4). The Cross-Workspace Interaction Rules (§7.4) extend this discipline to inter-Workspace coordination.

### §8.3 Fail-Closed Stance

The Workspace Specification is fail-closed by default. Permissions, Credentials, Network access, Git operations, and Cross-Workspace Interaction are all default-denied. The Human Approval Boundary is enforced at four Lifecycle stages by the Architect, the Builder (within scope), the Reviewer, or an FD.

### §8.4 Lifecycle Integrity

The 8-stage Lifecycle is internally consistent. Every stage has an explicit transition condition, a required artifact, and a recorded hook. The Lifecycle is conservative — it cannot be skipped; it cannot be transitioned with an unresolved failure, ungranted Permission, or unaudited operation.

### §8.5 Future Extensions

The Compatibility section (§8) declares extension rules that:

- Allow additive Capabilities (new Permission classes, new Boundary crossing points, new Lifecycle stages, new Workspace Types).
- Prohibit weakening (removing Capabilities, lowering the Security Boundary, removing Lifecycle stages, re-classifying default-deny as default-allow).
- Require a new FD for weakening.

### §8.6 Project-Independence

The Workspace Specification is project-independent. No Project owns any Workspace; no Workspace is restricted to any Project. APES (the first Project) MAY consume a Foundation-defined Workspace post-Foundation, but no Foundation-defined Workspace is APES-specific. Project Workspace (§7.2) is declared as a contract for downstream instantiation but is **NOT instantiated during the Foundation phase**, honoring the Foundation Invariant.

### §8.7 Workspace Type Co-Equality

The three Workspace Types (Mission, Project, Foundation) are declared as co-equal in specification. Differences are limited to declared scope, declared Permission set, and declared Lifecycle cadence — not normative precedence. No Workspace Type is privileged over another.

---

## §9. Limitations of the Report

This Report has the following **limitations**, declared openly:

1. **Specification-only report.** This Report describes the construction of the Workspace Specification document. It does not describe Workspace implementations (none exist), Workspace instances (none exist), or Workspace runtime behavior (no Workspace is running).
2. **Foundation-only report.** This Report describes Foundation-level work. Project-level work (e.g., a future APES-specific Workspace instance) is not in scope.
3. **Self-report.** This Report is a Builder self-report per Constitution §15.4 and `quality-gate-standard.md` §7. The Report records its self-report nature openly.
4. **Provisional Constitution basis.** This Report describes work against Constitution v0.1.0-draft Provisional. Any ratified Constitution clause that differs from a Provisional clause may require re-reporting.
5. **Pre-Review.** This Report is pre-Review. The Architect's Review (at `REVIEW-FOUNDATION-11-workspace.md`) MAY amend observations in this Report.

---

## §10. Ratification Status

This Report is **Draft / In Review**. Its formal ratification is deferred and conditional; no `FD-0011-report-workspace-specification.md` is created in this Foundation task. The Report accompanies the Workspace Specification through the Foundation cycle and is reviewed at `REVIEW-FOUNDATION-11-workspace.md`.

> **Note.** No `FD-0011` (whether ratification of the Workspace Specification, the Audit, the Report, or the Review) is created during Task 11. The existence of such FDs is **deferred** and **conditional**.

---

*End of REPORT-FOUNDATION-11-workspace.md v0.1.0-draft (Draft / In Review).*
