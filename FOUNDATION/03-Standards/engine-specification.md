# Research-OS Foundation — Engine Specification

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/engine-specification.md`
**Supersedes:** none
**Related:** Constitution §3 (Design Principles); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); `governance-model.md` §2, §6, §7, §8; `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `directory-standard.md` §4, §6, §8; `schema-standard.md` §4 (Evidence), §5 (Report), §6 (Review), §7 (Statistics), §8 (Manifest), §9 (Audit), §10 (Task), §11 (Pack), §12 (Release); `pack-standard.md` §6, §11, §12, §13, §17; `runtime-specification.md` §4, §6, §7, §8, §10, §11; `quality-gate-standard.md` §4, §5, §6, §7, §8, §9, §10; `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard declares the canonical *form* of a Foundation **Engine**. An Engine is the L5 component that performs a single, narrowly-scoped Foundation function: rendering prompts, auditing artifacts, gathering evidence, computing statistics, producing reports, or building subject artifacts. This Standard defines six Engine Specifications — **Prompt Engine**, **Audit Engine**, **Evidence Engine**, **Statistics Engine**, **Report Engine**, and **Builder Engine** — each with Purpose, Responsibility, Inputs, Outputs, Lifecycle, Dependencies, Quality Gate, Security Boundary, Compatibility, and Future Extensions.

This Standard does **not** implement any Engine. It does **not** write Engine code. It declares the *contract* a conformant Engine must satisfy.

### §1.2 In-Scope

1. The six Engine Specifications (§§3–§8), each declaring the ten required attributes.
2. The shared Engine Architecture (§9): an Engine's logical structure, its relationship to the Runtime, its Quality Gate integration, and its Security Boundary.
3. The shared Engine Lifecycle (§10): the eleven stages an Engine traverses from initial declaration to Active deployment.
4. Engine Compatibility rules (§11): version surfaces, migration, future extensions (additive-only).
5. Cross-references to Constitution, Standards, and Policies (§12).

### §1.3 Out-of-Scope

1. **Engine implementation** — no source code, no CLI, no scripts, no executables.
2. **Runtime implementation** — no Runtime source, no Runtime package.
3. **SDK implementation** — no SDK source, no SDK package.
4. **Plugin implementation** — no Plugin manifest, no Plugin source.
5. **MCP / agent / API implementation** — none.
6. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts.
7. **APES migration or Project-specific governance** — APES remains a paused Project.
8. **Sprint execution** — no Sprint is executed in this Foundation task.

---

## §2. Normative Status

### §2.1 Conformance

An implementation is said to **conform to this Standard** if and only if every Engine Specification it claims to satisfy is honored end-to-end (Purpose, Responsibility, Inputs, Outputs, Lifecycle, Dependencies, Quality Gate, Security Boundary, Compatibility, Future Extensions). A partial implementation is **non-conformant**.

### §2.2 Technology-Neutrality

This Standard is **technology-neutral**. It does not bind to any programming language, framework, serialization format, operating system, AI model, prompt template format, or inference engine. The Engine Specifications are expressed as natural-language contract clauses. A concrete implementation may map these clauses to a specific technology; until such a mapping exists, an Engine is conformant if its behavior matches the natural-language clauses.

### §2.3 Conflict Resolution

If any clause of this Standard conflicts with:
- the Constitution — **the Constitution prevails**;
- an active FD — **the FD prevails**;
- any other Foundation Standard (Directory, Schema, Pack, Runtime, Quality Gate) — **the more-specific Standard prevails** for the conflict zone, after cross-reference check;
- a Project-local rule — **the Foundation Standard prevails** (Constitution §1).

---

## §3. Prompt Engine Specification

### §3.1 Purpose

The **Prompt Engine** is the Foundation Engine that **composes** a structured prompt from a Mission, a Pack, a Task, and a Governance context. The Prompt Engine does not interpret the prompt; it produces the prompt artifact (per `schema-standard.md` §10) and hands it to the Runtime for delivery to a downstream agent.

### §3.2 Responsibility

- Compose prompts from Mission + Pack + Task + Governance inputs.
- Apply the Mission's prompt template rules (if any).
- Resolve all variables and references.
- Produce a structured prompt artifact conforming to `schema-standard.md` §10 (Task Schema) and `pack-standard.md` §9 (Task Specification).
- Refuse to execute the prompt.
- Refuse to call any AI model or inference engine.

### §3.3 Inputs

1. **Mission** — `MISSION-<id>.md` (per `pack-standard.md` §7).
2. **Pack** — `PACK-<id>.md` + Manifest (per `pack-standard.md` §5, §6).
3. **Task** — `TASK-<id>.md` (per `pack-standard.md` §9).
4. **Governance context** — Constitution Version + Foundation Version + applicable FD list (per `runtime-specification.md` §6.5).

### §3.4 Outputs

1. **Prompt artifact** — a structured file conforming to `schema-standard.md` §10 (Task Schema) and §4 (Evidence Schema).
2. **Prompt Manifest** — a Manifest entry declaring the prompt's inputs, output, and Foundation provenance.
3. **Prompt Audit hook** — an audit-ready record of the prompt's composition (input locators, variable resolutions, applied template rules).

### §3.5 Lifecycle

1. **Declare** — receive Mission + Pack + Task + Governance context.
2. **Validate** — verify inputs conform to their respective schemas; reject malformed inputs.
3. **Compose** — assemble prompt from inputs + template rules.
4. **Resolve** — substitute all variables and references.
5. **Emit** — produce prompt artifact + Manifest + Audit hook.
6. **Handoff** — deliver to Runtime; do not execute.
7. **Stop** — emit termination record; do not continue past handoff.

### §3.6 Dependencies

- `schema-standard.md` §10 (Task Schema), §4 (Evidence Schema).
- `pack-standard.md` §7 (Mission), §9 (Task), §6 (Manifest Rules).
- `runtime-specification.md` §6 (Runtime Input Specification).

### §3.7 Quality Gate

Every Prompt Engine **must** apply the six Foundation Quality Gate Types (per `quality-gate-standard.md` §5) to its own output:
- **Structure Gate** — prompt artifact has all required fields.
- **Consistency Gate** — no internal contradiction.
- **Cross Reference Gate** — every reference resolves.
- **Isolation Gate** — prompt is project-independent (no APES mention).
- **Scope Compliance Gate** — prompt honors Mission's declared scope.
- **Security Boundary Gate** — prompt does not embed executable code, network endpoints, or auto-action triggers.

A Prompt Engine that returns a non-`PASS` outcome on any Gate **must not** handoff to the Runtime.

### §3.8 Security Boundary

The Prompt Engine **forbidden actions**:
1. Execute the prompt.
2. Call an AI model, inference engine, or external service.
3. Emit executable code (no `.py`, `.js`, `.ts`, `.sh`, `.ps1`, `.bat`).
4. Spawn sub-processes.
5. Access the network.
6. Auto-approve, auto-commit, or auto-reject any artifact.
7. Bypass the Runtime handoff (the Prompt Engine produces a prompt; the Runtime delivers it).
8. Embed secrets, credentials, or API keys in the prompt.

### §3.9 Compatibility

- **Version surface:** `PromptEngine.Version`, `PromptEngine.FoundationVersion`, `PromptEngine.ConstitutionVersion` (per `runtime-specification.md` §11).
- **Migration:** MAJOR version bumps require a Migration Plan per `quality-gate-standard.md` §10.2.
- **Future Extensions:** additive-only per Constitution §13. New template rules may be added; existing rules may not be weakened without an FD.

### §3.10 Future Extensions

- New prompt template rules (additive).
- New variable substitution modes (e.g., conditional, contextual) — additive.
- New Manifest fields — additive.
- New Audit hook fields — additive.

---

## §4. Audit Engine Specification

### §4.1 Purpose

The **Audit Engine** is the Foundation Engine that **applies** the six Foundation Quality Gate Types (per `quality-gate-standard.md` §5) to a subject artifact and produces an **Audit Report** (per `schema-standard.md` §9) plus a **Verdict**.

### §4.2 Responsibility

- Apply the six Quality Gate Types to the subject artifact.
- For each Gate, gather evidence (per `quality-gate-standard.md` §6.2).
- Determine the outcome (`PASS`, `FAIL`, `BLOCKED`, `REPAIR REQUIRED`).
- Produce an Audit Report at `FOUNDATION/04-Audits/AUDIT-<subject-id>.md`.
- Produce a Verdict (`PASS` if all six Gates return `PASS`; otherwise `FAIL`).
- Refuse to bypass any Gate; refuse to override a Gate verdict without Escalation.

### §4.3 Inputs

1. **Subject artifact** — the file(s) under audit.
2. **Subject metadata** — `id`, `version`, `FoundationVersion`, `ConstitutionVersion`, `path`, `declared Status`.
3. **§15.5 Per-Task Scope Declaration** (if applicable) — Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition.
4. **Foundation registry** — the Constitution, Standards, Policies, FDs, and any other Foundation artifacts referenced by the subject.

### §4.4 Outputs

1. **Audit Report** — `FOUNDATION/04-Audits/AUDIT-<subject-id>.md` (per `schema-standard.md` §9).
2. **Verdict** — `PASS` or `FAIL`.
3. **Findings list** — severity-graded (Minor, Major, Critical).
4. **Evidence list** — one per Gate, with locator + outcome + rationale.

### §4.5 Lifecycle

1. **Receive** — accept subject + metadata + §15.5 Scope (if applicable).
2. **Apply Gate 1 — Structure** — verify required fields and sections.
3. **Apply Gate 2 — Consistency** — verify no internal contradictions.
4. **Apply Gate 3 — Cross Reference** — verify all references resolve.
5. **Apply Gate 4 — Isolation** — verify semantic project-independence.
6. **Apply Gate 5 — Scope Compliance** — verify §15.5 honored.
7. **Apply Gate 6 — Security Boundary** — verify no security boundary violations.
8. **Aggregate** — compute overall Verdict per outcome precedence (`FAIL > BLOCKED > REPAIR REQUIRED > PASS`).
9. **Emit** — produce Audit Report + Verdict + Findings + Evidence.
10. **File** — write the Audit Report to the on-disk path.
11. **Stop** — emit termination record.

### §4.6 Dependencies

- `quality-gate-standard.md` §5 (six Gate Types), §6 (Audit Relationship).
- `schema-standard.md` §9 (Audit Schema).
- `directory-standard.md` §6 (per-class storage paths).
- `runtime-specification.md` §7.2 (Audit output specification).

### §4.7 Quality Gate

The Audit Engine **must** apply the six Gates to its own Audit Report before filing. This is a **self-audit** (per Constitution §15.4 and `quality-gate-standard.md` §6.1). A non-conformant Audit Report **must not** be filed.

### §4.8 Security Boundary

The Audit Engine **forbidden actions**:
1. Modify the subject artifact (Auditor must not author; separation of duties).
2. Bypass a Gate (every Gate must be applied).
3. Override a Gate verdict without Escalation (per `quality-gate-standard.md` §8.3).
4. Execute the subject artifact's content.
5. Spawn sub-processes for evaluation.
6. Access the network to resolve references (resolution is local; non-resolving references are recorded as `FAIL` evidence).
7. Auto-approve the subject.

### §4.9 Compatibility

- **Version surface:** `AuditEngine.Version`, `AuditEngine.FoundationVersion`, `AuditEngine.ConstitutionVersion`.
- **Migration:** when a Gate Type is added, modified, or removed, a Migration Plan is required.
- **Future Extensions:** additive-only. New Gate Types may be added via a Foundation amendment (per Constitution §13); existing Gates may not be weakened without an FD.

### §4.10 Future Extensions

- New Gate Types (e.g., Accessibility Gate, Performance Gate) — additive.
- New evidence locator forms (per `quality-gate-standard.md` §6.2) — additive.
- New severity levels (e.g., Info, Blocker) — additive.
- New Audit Report sections — additive.

---

## §5. Evidence Engine Specification

### §5.1 Purpose

The **Evidence Engine** is the Foundation Engine that **collects, organizes, and emits** evidence supporting or refuting a claim, an Audit, or a Report. Evidence is the verifiable artifact that grounds every Audit finding and every Report assertion.

### §5.2 Responsibility

- Accept evidence requests from the Audit Engine, the Report Engine, and the Runtime.
- Collect raw evidence from on-disk artifacts (the Foundation registry).
- Verify that evidence exists and is current (not stale).
- Organize evidence into structured records (per `schema-standard.md` §4).
- Emit evidence records with locator, content reference, and provenance.
- Refuse to invent evidence; refuse to fabricate or extrapolate.

### §5.3 Inputs

1. **Evidence request** — `subject-id`, `claim-id`, `gate-id`, or `report-id` (the consumer that needs evidence).
2. **Locator** — `§X.Y` or `<path>:<line>` (per `quality-gate-standard.md` §6.2).
3. **Foundation registry** — the on-disk Foundation artifacts available for evidence gathering.

### §5.4 Outputs

1. **Evidence record** — per `schema-standard.md` §4 (Evidence Schema): `id`, `subject-id`, `claim-id` or `gate-id`, `locator`, `content-reference`, `provenance`, `collected-at`, `collector-id`.
2. **Evidence Manifest** — a Manifest entry per `schema-standard.md` §8.
3. **Stale-evidence flag** — a flag attached to any evidence record whose source has changed since collection.

### §5.5 Lifecycle

1. **Receive request** — accept evidence request + locator.
2. **Resolve locator** — find the on-disk artifact (or fail with `NOT_FOUND`).
3. **Verify currency** — check the artifact's current state against the request's expected state.
4. **Extract** — read the relevant section / line / field.
5. **Package** — wrap in an Evidence record.
6. **Emit** — produce Evidence record + Manifest entry.
7. **Stop** — emit termination record.

### §5.6 Dependencies

- `schema-standard.md` §4 (Evidence Schema), §8 (Manifest Schema).
- `directory-standard.md` §4, §6.
- `quality-gate-standard.md` §6.2 (evidence locator forms).

### §5.7 Quality Gate

The Evidence Engine **must** apply the six Gates to its Evidence records. A record that fails the Structure Gate, the Cross Reference Gate, or the Isolation Gate **must not** be emitted.

### §5.8 Security Boundary

The Evidence Engine **forbidden actions**:
1. Invent, fabricate, or extrapolate evidence.
2. Execute any artifact's content.
3. Modify any source artifact (read-only).
4. Spawn sub-processes.
5. Access the network.
6. Auto-approve or auto-reject a claim based on evidence.

### §5.9 Compatibility

- **Version surface:** `EvidenceEngine.Version`, `EvidenceEngine.FoundationVersion`, `EvidenceEngine.ConstitutionVersion`.
- **Migration:** when evidence locator forms change, a Migration Plan is required.
- **Future Extensions:** additive-only. New evidence types (e.g., Log Evidence, Trace Evidence) may be added.

### §5.10 Future Extensions

- New evidence types (additive).
- New locator forms (additive).
- New provenance metadata (additive).
- New stale-evidence detection strategies (additive).

---

## §6. Statistics Engine Specification

### §6.1 Purpose

The **Statistics Engine** is the Foundation Engine that **computes** descriptive statistics over a collection of Foundation artifacts, Records, or Reports. Statistics are quantitative summaries, never subjective scoring or ranking.

### §6.2 Responsibility

- Accept a query (artifact class, time range, status filter, version filter).
- Collect the matching artifacts.
- Compute descriptive statistics (count, distribution, mean, median, variance, percentile — categorical and numeric).
- Produce a Statistics artifact per `schema-standard.md` §7.
- Refuse to perform ranking, scoring, or aggregation that biases the Quality Gate.
- Refuse to infer or extrapolate beyond the input data.

### §6.3 Inputs

1. **Query** — artifact class, filters (status, version, time range, author).
2. **Input set** — the matched artifacts.
3. **Statistic types** — which descriptive statistics to compute.

### §6.4 Outputs

1. **Statistics artifact** — per `schema-standard.md` §7 (Statistics Schema): `id`, `query`, `population-size`, `distribution`, `summary-statistics`, `computed-at`, `computer-id`.
2. **Statistics Manifest** — Manifest entry declaring input set, statistic types, and Foundation provenance.

### §6.5 Lifecycle

1. **Receive query** — accept query parameters.
2. **Collect** — gather matching artifacts.
3. **Validate** — verify each artifact has the required fields for the requested statistics.
4. **Compute** — calculate descriptive statistics.
5. **Package** — wrap in a Statistics artifact.
6. **Emit** — produce Statistics artifact + Manifest.
7. **Stop** — emit termination record.

### §6.6 Dependencies

- `schema-standard.md` §7 (Statistics Schema), §8 (Manifest Schema).
- `directory-standard.md` §6.
- `runtime-specification.md` §7.4 (Statistics output specification).

### §6.7 Quality Gate

The Statistics Engine **must** apply the six Gates to its Statistics artifact. A non-conformant artifact **must not** be emitted.

### §6.8 Security Boundary

The Statistics Engine **forbidden actions**:
1. Perform ranking, scoring, or weighted aggregation (descriptive statistics only).
2. Infer, extrapolate, or predict beyond the input data.
3. Execute any artifact's content.
4. Modify any source artifact.
5. Spawn sub-processes.
6. Access the network.
7. Auto-decide a Quality Gate outcome based on statistics.

### §6.9 Compatibility

- **Version surface:** `StatisticsEngine.Version`, `StatisticsEngine.FoundationVersion`, `StatisticsEngine.ConstitutionVersion`.
- **Migration:** when statistic types change, a Migration Plan is required.
- **Future Extensions:** additive-only. New descriptive statistics may be added; existing statistics may not be weakened.

### §6.10 Future Extensions

- New descriptive statistics (additive).
- New filter dimensions (additive).
- New output formats (additive).

---

## §7. Report Engine Specification

### §7.1 Purpose

The **Report Engine** is the Foundation Engine that **composes** a structured Report (per `schema-standard.md` §5) from a set of inputs — Audit Reports, Evidence records, Statistics artifacts, and direct inputs. The Report Engine produces the eight-section Task Report (per Constitution §15) and other Foundation Reports.

### §7.2 Responsibility

- Accept Report inputs (Audit Reports, Evidence, Statistics, direct input).
- Apply the Report template (per `schema-standard.md` §5).
- Resolve cross-references to source artifacts.
- Produce a Report artifact at `FOUNDATION/06-Reports/REPORT-<id>.md`.
- Refuse to assert facts not grounded in evidence.
- Refuse to bypass or override an Audit Verdict.

### §7.3 Inputs

1. **Report template** — per `schema-standard.md` §5 (Report Schema).
2. **Audit Reports** — referenced artifacts at `FOUNDATION/04-Audits/AUDIT-<id>.md`.
3. **Evidence records** — per `schema-standard.md` §4.
4. **Statistics artifacts** — per `schema-standard.md` §7.
5. **Direct input** — free-form text or structured input from the Builder.

### §7.4 Outputs

1. **Report artifact** — `FOUNDATION/06-Reports/REPORT-<id>.md` (per `schema-standard.md` §5).
2. **Report Manifest** — Manifest entry declaring inputs, sources, and Foundation provenance.
3. **Report Audit hook** — an audit-ready record of the Report's composition.

### §7.5 Lifecycle

1. **Receive** — accept Report template + inputs.
2. **Validate inputs** — verify Audit Reports have `PASS` verdicts (or document a `FAIL` verdict with rationale).
3. **Compose** — assemble sections per template.
4. **Resolve references** — bind all references to source artifacts.
5. **Emit** — produce Report artifact + Manifest + Audit hook.
6. **File** — write the Report to the on-disk path.
7. **Stop** — emit termination record.

### §7.6 Dependencies

- `schema-standard.md` §5 (Report Schema), §4 (Evidence), §7 (Statistics), §8 (Manifest), §9 (Audit).
- `directory-standard.md` §6.
- `runtime-specification.md` §7.3 (Report output specification).
- `quality-gate-standard.md` §9 (Release Quality Gate, for RC-level Reports).

### §7.7 Quality Gate

The Report Engine **must** apply the six Gates to its Report artifact. A Report with a `FAIL` Audit Verdict in its source **must not** be filed as `PASS`.

### §7.8 Security Boundary

The Report Engine **forbidden actions**:
1. Assert facts not grounded in evidence.
2. Bypass or override an Audit Verdict.
3. Execute any source artifact's content.
4. Modify any source artifact.
5. Spawn sub-processes.
6. Access the network.
7. Auto-approve the Report.

### §7.9 Compatibility

- **Version surface:** `ReportEngine.Version`, `ReportEngine.FoundationVersion`, `ReportEngine.ConstitutionVersion`.
- **Migration:** when Report templates change, a Migration Plan is required.
- **Future Extensions:** additive-only. New Report templates, new sections, new bindings — additive.

### §7.10 Future Extensions

- New Report templates (additive).
- New Report sections (additive).
- New input types (additive).

---

## §8. Builder Engine Specification

### §8.1 Purpose

The **Builder Engine** is the Foundation Engine that **produces** subject artifacts (Standards, Audits, Reports, Reviews, Decisions, etc.) per a Builder's instructions, subject to the Builder's §15.5 Per-Task Scope Declaration. The Builder Engine operates within a strict boundary: it produces artifacts but does not approve, audit, or release them.

### §8.2 Responsibility

- Accept a Builder instruction set (Mission + Pack + Task + Governance).
- Accept the §15.5 Per-Task Scope Declaration (Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition).
- Produce the declared Outputs (artifacts).
- Honor the Allowed Files list and the Forbidden Files list.
- Honor the Stop Condition (do not proceed past the declared stop point).
- Refuse to approve, audit, release, or sign off on any artifact.

### §8.3 Inputs

1. **Builder instructions** — Mission + Pack + Task + Governance (per `runtime-specification.md` §6).
2. **§15.5 Per-Task Scope Declaration** — Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition.
3. **Foundation registry** — Constitution, Standards, Policies, FDs.

### §8.4 Outputs

1. **Subject artifacts** — files at the declared paths (Allowed Files only).
2. **Builder Audit hook** — an audit-ready record of the Builder's compliance with its own §15.5 Scope.
3. **Builder Manifest** — Manifest entry declaring all produced artifacts and their provenance.

### §8.5 Lifecycle

1. **Receive instructions** — accept instructions + §15.5 Scope.
2. **Validate Scope** — verify Allowed Files, Forbidden Files, Inputs, Outputs, Dependencies, Quality Gates, Stop Condition are well-formed.
3. **Compose** — produce artifacts per Allowed Files only.
4. **Self-audit** — apply the six Gates to its own outputs (per Constitution §15.4).
5. **Emit** — produce artifacts + Builder Audit hook + Manifest.
6. **Stop** — emit termination record; do not proceed past Stop Condition.

### §8.6 Dependencies

- `pack-standard.md` §3–§17 (Builder Pack).
- `runtime-specification.md` §6, §7 (Runtime Input / Output).
- `quality-gate-standard.md` §5, §6 (Gates + self-audit).
- `directory-standard.md` §4, §6, §8, §10.

### §8.7 Quality Gate

The Builder Engine **must** apply the six Gates to its own outputs as a **self-audit** (per Constitution §15.4). If the self-audit returns `FAIL` on any Gate, the Builder Engine **must not** emit; it must return to Compose with a repair instruction.

### §8.8 Security Boundary

The Builder Engine **forbidden actions**:
1. Approve, audit, release, or sign off on any artifact.
2. Create any Forbidden File (per §15.5 Scope).
3. Execute any source artifact's content.
4. Modify any artifact outside the Allowed Files list.
5. Spawn sub-processes.
6. Access the network.
7. Auto-commit, auto-push, or auto-tag via git.
8. Proceed past the Stop Condition (per §15.5).

### §8.9 Compatibility

- **Version surface:** `BuilderEngine.Version`, `BuilderEngine.FoundationVersion`, `BuilderEngine.ConstitutionVersion`.
- **Migration:** when §15.5 Scope schema changes, a Migration Plan is required.
- **Future Extensions:** additive-only. New Builder instructions types may be added.

### §8.10 Future Extensions

- New instruction types (additive).
- New output artifact classes (additive).
- New self-audit dimensions (additive).

---

## §9. Shared Engine Architecture

### §9.1 Logical Structure

Every Engine conforms to a single logical structure:

```
Inputs → Lifecycle → Outputs
         ↓
   Quality Gate (self-audit per Constitution §15.4)
         ↓
   Security Boundary (forbidden actions list)
```

### §9.2 Engine-to-Runtime Relationship

An Engine operates **under** the Runtime (per `runtime-specification.md` §4). The Runtime invokes the Engine, supplies inputs, and receives outputs. The Engine does not invoke the Runtime; the Engine is **called** by the Runtime, not the other way around.

### §9.3 Engine-to-Engine Relationship

Engines may call other Engines via the Runtime only. Direct Engine-to-Engine calls (bypassing the Runtime) are **forbidden** (separation of duties + audit trail).

### §9.4 Engine Audit Trail

Every Engine invocation **must** produce an audit-ready record (per `schema-standard.md` §9) that is filed alongside the Engine's output. The audit record declares inputs, outputs, lifecycle stages traversed, Quality Gate outcomes, and the Engine identity.

---

## §10. Shared Engine Lifecycle

### §10.1 Eleven Lifecycle Stages

Every Engine traverses these stages per invocation:

1. **Declare** — receive invocation request.
2. **Validate inputs** — verify inputs conform to declared schemas.
3. **Plan** — compute lifecycle plan (which Gates to apply, which outputs to emit).
4. **Compose** — perform the Engine's primary function.
5. **Self-audit** — apply the six Gates to its own outputs (per Constitution §15.4).
6. **Resolve references** — bind all references to source artifacts.
7. **Emit** — produce outputs + audit record.
8. **File** — write outputs to declared paths.
9. **Notify** — signal completion to the Runtime.
10. **Hand off** — release control back to the Runtime.
11. **Stop** — emit termination record; do not continue past handoff.

### §10.2 Failure Handling

If any stage fails:
- The Engine **must not** proceed to subsequent stages.
- The Engine emits a failure record (per `quality-gate-standard.md` §5.4 outcomes).
- The Runtime receives the failure record and applies Failure Handling (per `quality-gate-standard.md` §8).

### §10.3 Idempotence

An Engine invocation is **idempotent** if invoked twice with identical inputs and Governance context: the second invocation produces outputs that are byte-identical to the first (excluding timestamps). Every Engine declares its idempotence guarantee in its Compatibility section.

---

## §11. Compatibility

### §11.1 Version Surfaces

Every Engine declares three version surfaces (per `runtime-specification.md` §11):

- `Engine.Version` — the Engine's own SemVer version.
- `Engine.FoundationVersion` — the Foundation Version it targets.
- `Engine.ConstitutionVersion` — the Constitution Version it honors.

### §11.2 Migration Rules

A non-backward-compatible change (MAJOR SemVer bump) requires a Migration Plan per `quality-gate-standard.md` §10.2. The Plan declares the previous version, the new version, the breaking changes, the affected artifacts, and the Migration procedure.

### §11.3 Future Extensions

Per Constitution §13, future Engine extensions are **additive-only**:
- New input types, output types, lifecycle stages, audit fields — additive.
- Existing inputs, outputs, stages, fields may not be removed or weakened.
- A weakening requires a new FD and ratification per `foundation-decision-policy.md`.

---

## §12. Cross References

Per Constitution §10 (Cross Reference Policy), this Standard declares the following mandatory references.

**Constitution references:**
- §1 (Governance Hierarchy)
- §2 (Compatibility Policy)
- §3 (Design Principles)
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
- §15 (Foundation Task Protocol); §15.3, §15.4, §15.5

**Standard references:**
- `directory-standard.md` §4, §6, §8, §10
- `schema-standard.md` §4 (Evidence), §5 (Report), §6 (Review), §7 (Statistics), §8 (Manifest), §9 (Audit), §10 (Task), §11 (Pack), §12 (Release)
- `pack-standard.md` §3–§17
- `runtime-specification.md` §4, §6, §7, §8, §10, §11
- `quality-gate-standard.md` §4, §5, §6, §7, §8, §9, §10

**Policy references:**
- `governance-model.md` §2, §6, §7, §8
- `approval-workflow.md`
- `change-control-policy.md`
- `disagreement-and-escalation.md`
- `roles-and-authority.md`
- `rfc-policy.md`
- `foundation-decision-policy.md`
- `adr-policy.md`

**Back-references (this Standard is referenced by):**
- (none yet — this Standard is new at `0.1.0-draft`; back-references will be added by future Standards)

---

## §13. Relationship to Other Artifacts

### §13.1 To the Constitution

This Standard operationalizes the Engine concept under Constitution §§11, §13, and §15. It does not contradict any clause of the Constitution.

### §13.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for Engine Specifications, Audit Reports, Reports, and Reviews.
- **Schema Standard** — declares the Evidence, Report, Statistics, Manifest, Audit, Task, Pack, and Release Schemas that Engines consume and emit.
- **Pack Standard** — declares the Mission, Program, Task, and Deliverable templates that the Prompt Engine and Builder Engine consume.
- **Runtime Specification** — declares the Runtime that invokes Engines and supplies their inputs.
- **Quality Gate Standard** — declares the six Gates and the Evaluation Model that Engines apply to their own outputs.

### §13.3 To Future Artifacts

Future artifacts that may reference this Standard include SDK Specifications (downstream), Plugin Specifications (downstream), Workspace Specifications (downstream), and Project-local Engine profiles (downstream, when Projects exist).

---

## §14. Ratification

This Standard is **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0008-ratify-engine-specification.md` is created in this Foundation task.

**Ratification path (when invoked by a future Foundation cycle):**
1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition.
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0008-ratify-engine-specification.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.

Until `FD-0008` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

---

*End of engine-specification.md v0.1.0-draft (Draft / In Review).*