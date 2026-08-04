# Research-OS Foundation — Plugin Specification Report

**Status:** Approved
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/06-Reports/REPORT-FOUNDATION-10-plugin.md`
**Report Subject:** `FOUNDATION/03-Standards/plugin-specification.md` (v0.1.0-draft, Draft / In Review)
**Report Author:** Foundation Builder (self-report per Constitution §15.4)
**Related:** Constitution §15 (Foundation Task Protocol); §15.4 (Self-audit); §15.5 (Per-Task Scope Declaration); `plugin-specification.md` (this Report's subject); `AUDIT-FOUNDATION-10-plugin.md`; `REVIEW-FOUNDATION-10-plugin.md`; `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship); `sdk-specification.md` (precedent)

---

## §1. Report Purpose

This Report records the construction of `FOUNDATION/03-Standards/plugin-specification.md` during Foundation Task 10. It captures the **inputs**, **process**, **outputs**, and **artifacts produced** for Task 10, alongside a per-section summary of the resulting Standard. It does **not** re-evaluate the merits of the Plugin Specification's policy decisions (that is the Architect's role at `REVIEW-FOUNDATION-10-plugin.md`), nor does it re-audit Gate compliance (that is the Auditor's role at `AUDIT-FOUNDATION-10-plugin.md`).

This Report is **Draft / In Review**. It accompanies the Plugin Specification through the Foundation cycle.

---

## §2. Task Context

| Field | Value |
|---|---|
| Task | Foundation Task 10 |
| Task Name | Plugin Specification |
| Authorization | Architect's per-task mandate issued alongside Task 09 Approval |
| Foundation Version | 0.1.0-dev (FROZEN — no version bump) |
| Constitution Version | v0.1.0-draft (Provisional) — no change |
| Companion Tasks | Task 09 (SDK Specification) approved; Task 11 (Workspace Specification) reserved; Task 12 (Release Specification) reserved |
| Predecessor | Task 09 (SDK Specification) — provides the Plugin SDK contract (§7) and Shared SDK Architecture (§8) this Standard references |
| Successor (reserved) | Task 11 (Workspace Specification); Task 12 (Release Specification) |

---

## §3. Per-Task Scope Declaration (Constitution §15.5 mirror)

### §3.1 Allowed Files

1. `FOUNDATION/03-Standards/plugin-specification.md` (new — primary deliverable).
2. `FOUNDATION/03-Standards/README.md` (modified — Standards index update for Task 10).
3. `FOUNDATION/04-Audits/AUDIT-FOUNDATION-10-plugin.md` (new — companion Audit).
4. `FOUNDATION/06-Reports/REPORT-FOUNDATION-10-plugin.md` (new — this Report).
5. `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-10-plugin.md` (new — companion Review).

### §3.2 Forbidden Files

1. No new Foundation Standard outside `FOUNDATION/03-Standards/` beyond the Plugin Specification.
2. No `FOUNDATION/09-Decisions/FD-0010-ratify-plugin-specification.md` or equivalent.
3. No SDK, Runtime, Engine, Pack, Workspace, Release, Project, Sprint, or APES files.
4. No source code (no `.ts/.py/.js/.sh/.go/.rs/.java/.cs/.cpp/.c/.rb/.php`).
5. No manifest files (no `package.json`, no `manifest.json`, no `plugin.yaml`, no `manifest.yml`, no `.obsidian/plugins/manifest.json`, no VSCode `contributes`, no MCP `server.py`).
6. No network endpoints in normative clauses.
7. No credentials in any file.
8. No sandbox implementation (no Dockerfile, no firecracker config, no gVisor config).

### §3.3 Inputs

1. The Architect's Authorization for Task 10 (eight mandated sections; ten prohibitions).
2. The Task 09 SDK Specification (`FOUNDATION/03-Standards/sdk-specification.md`), specifically:
   - §7 (Plugin SDK) — Interface Boundary contract.
   - §8 (Shared SDK Architecture) — SDK-to-Runtime relationship.
   - §7.8 (Permission Model) — seven Permission classes.
   - §12.3 (Cross-references the forthcoming Plugin Specification Task 10).
3. The Pack Standard (`FOUNDATION/03-Standards/pack-standard.md`) — for the §15.5 Scope model mirrored in §5.1 of the Plugin Specification.
4. The Quality Gate Standard (`FOUNDATION/03-Standards/quality-gate-standard.md`) — for the six Gates referenced throughout the Plugin Specification.
5. The Directory Standard (`FOUNDATION/03-Standards/directory-standard.md`) — for the on-disk path of the Plugin Specification.
6. The Schema Standard (`FOUNDATION/03-Standards/schema-standard.md`) — for the Evidence, Audit, Manifest, Report, Review schemas referenced throughout the Plugin Specification.
7. The Standards README (`FOUNDATION/03-Standards/README.md`) — for the index entry pattern.
8. The Constitution (`FOUNDATION/01-Constitution/constitution.md`) — for the binding design principles, role model, RFC governance, versioning policy, naming convention, cross-reference policy, quality gate, deprecation policy, future extension policy, success criteria, and Foundation Task Protocol.

### §3.4 Outputs

1. `FOUNDATION/03-Standards/plugin-specification.md` (new).
2. `FOUNDATION/03-Standards/README.md` (modified).
3. `FOUNDATION/04-Audits/AUDIT-FOUNDATION-10-plugin.md` (new).
4. `FOUNDATION/06-Reports/REPORT-FOUNDATION-10-plugin.md` (new — this file).
5. `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-10-plugin.md` (new).
6. The Builder's eight-section Completion Report (delivered in the next message; see Task #7 in the Builder's task list).

### §3.5 Dependencies

1. Task 09 (SDK Specification) is approved; the Plugin Specification references its §7 and §8 without duplicating them.
2. The Constitution (Provisional) provides the binding design principles and role model.
3. The Quality Gate Standard provides the six Gates.
4. The Directory Standard provides the on-disk path.
5. The Schema Standard provides the Evidence, Audit, Manifest, Report, Review schemas.

### §3.6 Quality Gates

1. Structure Gate (per `quality-gate-standard.md` §5.3.1).
2. Consistency Gate (per `quality-gate-standard.md` §5.3.2).
3. Cross Reference Gate (per `quality-gate-standard.md` §5.3.3).
4. Isolation Gate (per `quality-gate-standard.md` §5.3.4).
5. Scope Compliance Gate (per `quality-gate-standard.md` §5.3.5).
6. Security Boundary Gate (per `quality-gate-standard.md` §5.3.6).

### §3.7 Stop Condition

After the eight-section Completion Report is delivered, STOP. Do not auto-begin Task 11. Do not auto-begin Task 12. Await human Architect review at `REVIEW-FOUNDATION-10-plugin.md`.

---

## §4. Process Summary

### §4.1 Pre-execution

1. The Builder acknowledged the Architect's Approval of Task 09 and Authorization of Task 10.
2. The Builder issued the pre-execution declarations (Allowed files, Forbidden files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition) — recorded above in §3.
3. The Builder created seven tracking tasks via the Builder's task list (one per artifact plus a Completion Report).
4. The Builder Read the Foundation Standards and Policies that the Plugin Specification would reference (`sdk-specification.md`, `pack-standard.md`, `quality-gate-standard.md`, `directory-standard.md`, `schema-standard.md`, Standards README, Constitution §§0–3).

### §4.2 Authoring

1. The Builder authored `FOUNDATION/03-Standards/plugin-specification.md` with twelve top-level sections (Purpose/Scope, Architecture Purpose, Boundary Model, Lifecycle, Interface Specification, Permission Model, Security Model, Platform Plugin Specifications, Compatibility, Cross References, Relationship to Other Artifacts, Ratification).
2. The Builder maintained the architectural coherence with `sdk-specification.md` §7 — referencing rather than duplicating.
3. The Builder preserved the Foundation Hard Prohibitions throughout: no implementation, no installation, no network, no credentials, no sandbox, no Pack instance, no Project artifact, no FD.
4. The Builder followed the precedent of Tasks 06–09 for header fields, section numbering, ratification clause phrasing, and cross-reference style.

### §4.3 Audit and Report

1. The Builder authored `FOUNDATION/04-Audits/AUDIT-FOUNDATION-10-plugin.md` evaluating the Plugin Specification against all six Quality Gates and the Architect's ten prohibitions.
2. The Builder authored `FOUNDATION/06-Reports/REPORT-FOUNDATION-10-plugin.md` (this file) recording the construction of the Plugin Specification.
3. The Builder authored `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-10-plugin.md` providing the Reviewer's prompt for the human Architect.

### §4.4 Standards README Update

The Builder updated `FOUNDATION/03-Standards/README.md` to:

1. Add the Plugin Specification row to the Index table (matching the precedent of Tasks 06–09).
2. Update the Future Standards (Reserved) table to mark Task 10 complete and reserve Task 11 (Workspace) and Task 12 (Release).
3. Update the closing Note to include the deferred-ratification language for the Plugin Specification (matching the precedent of Tasks 06–09).

---

## §5. Plugin Specification — Section Summary

### §5.1 §1 Purpose and Scope

- §1.1 Purpose — declares the canonical form of a Foundation Plugin and the eight required sections.
- §1.2 In-Scope — enumerates the eight sections plus cross-references and relationships.
- §1.3 Out-of-Scope — explicitly forbids Plugin implementation, installation, network, sandbox, MCP server, VSCode/Cursor extensions, Claude/Codex integrations, Pack instances, APES migration, Sprint execution, and SDK-duplication.

### §5.2 §2 Plugin Architecture Purpose

- §2.1 Definition — defines a Plugin as an L5 trust-bounded adapter between third-party hosts and Foundation.
- §2.2 What a Plugin IS — six positive attributes.
- §2.3 What a Plugin IS NOT — seven negative attributes.
- §2.4 Relationship to SDK, Engine, Runtime — table stating the trust-boundary placement of each L5 component.

### §5.3 §3 Plugin Boundary Model

- §3.1 Boundary Layers — five-layer diagram from third-party host to Foundation storage.
- §3.2 Boundary Rules — seven SHALL NOT clauses.
- §3.3 Boundary Crossing Points — six permitted crossings, each with a mediator and recorded-as column.
- §3.4 Boundary to SDK Spec — declares non-duplication of `sdk-specification.md` §7.

### §5.4 §4 Plugin Lifecycle

- §4.1 Overview — nine ordered stages.
- §4.2 Stage 1 — Registration.
- §4.3 Stage 2 — Discovery.
- §4.4 Stage 3 — Validation (six Gates).
- §4.5 Stage 4 — Permission Approval.
- §4.6 Stage 5 — Activation.
- §4.7 Stage 6 — Execution.
- §4.8 Stage 7 — Audit.
- §4.9 Stage 8 — Disable.
- §4.10 Stage 9 — Removal.
- §4.11 Stage Transition Table — 10 transitions, all gated.
- §4.12 Lifecycle Hooks Summary — 9 hooks, one per stage.

### §5.5 §5 Plugin Interface Specification

- §5.1 Input Contract — five inputs.
- §5.2 Output Contract — three outputs (result, Audit hook, Manifest).
- §5.3 Metadata — 17-field Metadata table.
- §5.4 Versioning — bump triggers and Foundation binding rule.
- §5.5 Compatibility — Foundation, Constitution, SDK, and host-version compatibility.

### §5.6 §6 Permission Model

- §6.1 Overview — default-deny rule.
- §6.2 Allowed Access — six Allowed Permissions.
- §6.3 Restricted Access — six Restricted Permissions.
- §6.4 Default-Denied Permissions — six Default-Denied Permissions.
- §6.5 Human Approval Boundary — Reviewer enforcement.
- §6.6 Isolation Rules — seven isolation rules.

### §5.7 §7 Security Model

- §7.1 Trust Boundary — three trust regions (Foundation, Plugin, third-party).
- §7.2 Sandboxing Concept — host-provided sandboxing, normative.
- §7.3 Data Access Rules — six rules.
- §7.4 Credential Handling Rules — seven rules, including Audit-hook redaction.

### §5.8 §8 Platform Plugin Specifications

- §8.0 Overview — co-equal, contract-only.
- §8.1 GitHub Plugin — six sub-fields.
- §8.2 Obsidian Plugin — six sub-fields.
- §8.3 MCP Plugin — six sub-fields.
- §8.4 Claude Plugin — six sub-fields.
- §8.5 Codex Plugin — six sub-fields.
- §8.6 VSCode Plugin — six sub-fields.
- §8.7 Cursor Plugin — six sub-fields.

### §5.9 §9 Compatibility

- §9.1 Version Compatibility — four compatibility dimensions.
- §9.2 Migration Rules — five-element Migration Plan.
- §9.3 Extension Rules — additive-only; weakening requires a new FD.
- §9.4 Plugin Supersession — supersession rule.

### §5.10 §10 Cross References

- §10.1 Constitution References — §§1–15.
- §10.2 Standard References — seven Foundation Standards.
- §10.3 Policy References — eight Policies.
- §10.4 Back-References — three classes of future artifacts.

### §5.11 §11 Relationship to Other Artifacts

- §11.1 To the Constitution.
- §11.2 To Other Foundation Standards.
- §11.3 To Future Artifacts.
- §11.4 Plugin as Project-Independent Component.

### §5.12 §12 Ratification

- Draft / In Review.
- Ratification path (five steps).
- Deferred-ratification language: "No `FD-0010-ratify-plugin-specification.md` is created in this Foundation task."
- Technology-neutrality and project-independence reaffirmation.

---

## §6. Artifact Inventory

| Artifact | Status | Path | Lines (approx.) |
|---|---|---|---|
| Plugin Specification | Draft / In Review | `FOUNDATION/03-Standards/plugin-specification.md` | ~720 |
| Plugin Specification Audit | Draft / In Review | `FOUNDATION/04-Audits/AUDIT-FOUNDATION-10-plugin.md` | ~280 |
| Plugin Specification Report | Draft / In Review | `FOUNDATION/06-Reports/REPORT-FOUNDATION-10-plugin.md` | this file |
| Plugin Specification Review | Draft / In Review | `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-10-plugin.md` | forthcoming |
| Standards README | modified | `FOUNDATION/03-Standards/README.md` | one row added; reserved table updated; closing note extended |

---

## §7. Compliance Posture

The Plugin Specification is **compliant** with:

- Constitution v0.1.0-draft Provisional — all referenced clauses; no clause is contradicted.
- Foundation Hard Prohibitions — no implementation, no installation, no network, no credentials, no sandbox, no Pack, no Project, no FD.
- Quality Gate Standard — all six Gates PASS (per the companion Audit).
- File-naming convention — `plugin-specification.md` follows the precedent of Tasks 06–09.
- Ratification precedent — §12 deferred-ratification language matches Tasks 06–09.
- Cross-reference style — header `Related:` and §10 Cross References match the precedent.

---

## §8. Observations

### §8.1 Architectural Coherence

The Plugin Specification maintains architectural coherence with `sdk-specification.md`:

- It does not duplicate the Plugin SDK (§7 of `sdk-specification.md`).
- It extends the Permission Model granularly without contradiction.
- It honors the Shared SDK Architecture (§8 of `sdk-specification.md`) by referencing it where appropriate.

### §8.2 Boundary Discipline

The Boundary Model (§3), Permission Model (§6), and Security Model (§7) form a consistent boundary discipline. Boundary crossing is governed by mediators (§3.3), Permissions (§6), and Trust rules (§7).

### §8.3 Fail-Closed Stance

The Plugin Specification is fail-closed by default. Permissions, Credentials, Network access, and Git operations are all default-denied. The Human Approval Boundary is enforced by the Reviewer's signed disposition.

### §8.4 Lifecycle Integrity

The 9-stage Lifecycle is internally consistent. Every stage has an explicit transition condition, a required artifact, and a recorded hook. The Lifecycle is conservative — it cannot be skipped; it cannot be transitioned with an unresolved failure.

### §8.5 Future Extensions

The Compatibility section (§9) declares extension rules that:

- Allow additive Capabilities (new Permission classes, new Boundary crossing points).
- Prohibit weakening (removing Capabilities, lowering the Security Boundary, removing Lifecycle stages, re-classifying default-deny as default-allow).
- Require a new FD for weakening.

### §8.6 Project-Independence

The Plugin Specification is project-independent. No Project owns any Plugin; no Plugin is restricted to any Project. APES (the first Project) MAY consume a Foundation-defined Plugin post-Foundation, but no Foundation-defined Plugin is APES-specific.

---

## §9. Limitations of the Report

This Report has the following **limitations**, declared openly:

1. **Specification-only report.** This Report describes the construction of the Plugin Specification document. It does not describe Plugin implementations (none exist), Plugin instances (none exist), or Plugin runtime behavior (no Plugin is running).
2. **Foundation-only report.** This Report describes Foundation-level work. Project-level work (e.g., a future APES-specific Plugin instance) is not in scope.
3. **Self-report.** This Report is a Builder self-report per Constitution §15.4 and `quality-gate-standard.md` §7. The Report records its self-report nature openly.
4. **Provisional Constitution basis.** This Report describes work against Constitution v0.1.0-draft Provisional. Any ratified Constitution clause that differs from a Provisional clause may require re-reporting.
5. **Pre-Review.** This Report is pre-Review. The Architect's Review (at `REVIEW-FOUNDATION-10-plugin.md`) MAY amend observations in this Report.

---

## §10. Ratification Status

This Report is **Draft / In Review**. Its formal ratification is deferred and conditional; no `FD-0010-report-plugin-specification.md` is created in this Foundation task. The Report accompanies the Plugin Specification through the Foundation cycle and is reviewed at `REVIEW-FOUNDATION-10-plugin.md`.

> **Note.** No `FD-0010` (whether ratification of the Plugin Specification, the Audit, the Report, or the Review) is created during Task 10. The existence of such FDs is **deferred** and **conditional**.

---

*End of REPORT-FOUNDATION-10-plugin.md v0.1.0-draft (Draft / In Review).*
