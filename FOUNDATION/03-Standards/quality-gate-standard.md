# Research-OS Foundation — Quality Gate Standard

**Status:** Draft / In Review
**Version:** 0.1.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/quality-gate-standard.md`
**Supersedes:** none
**Related:** Constitution §3 (Design Principles); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); `governance-model.md` §2 (Hierarchy), §6 (Artifact Types), §7 (Status Lifecycle); `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `directory-standard.md` §4, §6, §8; `schema-standard.md` §4–§12; `pack-standard.md` §17 (Pack Quality Gate); `runtime-specification.md` §8 (Quality Gate Integration), §10 (Runtime Security Boundary); `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard operationalizes **Constitution §11 (Quality Gate)** for the Research-OS Foundation. It declares the **canonical form** of a Foundation Quality Gate: what the Quality Gate IS, what it is NOT, how it evolves through its Lifecycle, what Types of Gates exist, how each Gate Evaluates a subject artifact, how Gates relate to the Audit / Review / Report records, how Failures are Handled, how a Release Quality Gate operates, and how the Standard itself Versions and Migrates.

This Standard does **not** implement validators. It does **not** implement scoring engines. It does **not** create automation. It declares the **contract** that a validator (whether human or machine-assisted) must satisfy.

### §1.2 In-Scope

1. The **Quality Gate Lifecycle** (5 stages: Draft Gate, Review Gate, Approval Gate, Release Candidate Gate, Stable Gate).
2. The **Quality Gate Types** (6 Gates: Structure Gate, Consistency Gate, Cross Reference Gate, Isolation Gate, Scope Compliance Gate, Security Boundary Gate).
3. The **Quality Gate Evaluation Model** (4 outcomes: PASS, FAIL, BLOCKED, REPAIR REQUIRED).
4. The **Quality Gate Audit Relationship** (Audit responsibility, Audit evidence, Audit report).
5. The **Quality Gate Review Relationship** (Reviewer role, Approval boundary, Human decision).
6. The **Quality Gate Failure Handling** (Correction cycle, Re-review, Escalation).
7. The **Quality Gate Release Quality Gate** (RC requirements, Stable release requirements, Final approval).
8. The **Quality Gate Compatibility** (Version changes, Migration, Future extension).

### §1.3 Out-of-Scope

1. **Validator implementation** — no source code, no CLI, no scripts, no automated checking tools.
2. **CI/CD integration** — no continuous integration pipelines, no GitHub Actions workflows, no build pipelines.
3. **Scoring engine** — no quantitative scoring, no aggregation algorithms, no ranking.
4. **Auto-rejection** — no machine decides rejection without human review.
5. **Engine / Runtime / SDK / Plugin / Workspace implementation** — these are downstream deliverables.
6. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts.
7. **APES migration or Project-specific governance** — APES remains a paused Project.
8. **Sprint execution** — no Sprint is executed in this Foundation task.

---

## §2. Normative Status

### §2.1 Conformance

A subject artifact is said to **pass a Quality Gate** if and only if every applicable Quality Gate Type returns an Evaluation outcome of `PASS` (per §5). A subject artifact is said to **fail a Quality Gate** if any applicable Quality Gate Type returns an outcome of `FAIL`, `BLOCKED`, or `REPAIR REQUIRED` (per §5). The Application of Gates to subject artifacts is governed by §5 (Evaluation Model) and §8 (Failure Handling).

### §2.2 Technology-Neutrality

This Standard is **technology-neutral**. It does not bind to any programming language, framework, serialization format, operating system, validation library, scoring algorithm, CI/CD tool, or workflow engine. The Quality Gate Types, Lifecycle stages, Evaluation Model outcomes, and Failure Handling rules are expressed as natural-language contract clauses. A concrete implementation may map these clauses to a specific technology; until such a mapping exists, a Quality Gate is conformant if its behavior matches the natural-language clauses.

### §2.3 Conflict Resolution

If any clause of this Standard conflicts with:
- the Constitution (v0.1.0-draft or any successor) — **the Constitution prevails**;
- an active Foundation Decision (FD-NNNN with status `Ratified`) — **the FD prevails**;
- any other Foundation Standard (Directory, Schema, Pack, Runtime) — **the more-specific Standard prevails** for the conflict zone, after cross-reference check;
- a Project-local rule — **the Foundation Standard prevails** (Constitution §1).

---

## §3. Quality Gate Purpose

### §3.1 Definition

A **Quality Gate** is the formal Foundation procedure that determines whether a subject artifact meets the **four mandatory criteria** of Constitution §11 — **Completeness**, **Compliance**, **Cross Reference**, and **Isolation** — as elaborated by the six Quality Gate Types (§4) and the four Evaluation outcomes (§5), and as recorded in a paired **Audit Report** (§6) and **Review Record** (§7).

### §3.2 What a Quality Gate IS

A Quality Gate IS:
- a **deterministic, repeatable procedure** that produces a single Evaluation outcome per Gate Type;
- a **separation-of-duties instrument** between the Builder (who authors), the Auditor (who audits), and the Reviewer (who approves);
- a **four-criteria gate** that operationalizes Constitution §11.1–§11.4;
- a **lifecycle-bound procedure** that advances a subject artifact from one Lifecycle stage to the next (per §4);
- a **fail-safe instrument**: in the absence of a positive PASS verdict, the artifact **does not advance**;
- a **human-bounded procedure**: the final disposition is always a human decision (§7);
- a **release-blocking instrument**: a `FAIL` or `BLOCKED` outcome blocks the artifact's transition to the next Lifecycle stage.

### §3.3 What a Quality Gate IS NOT

A Quality Gate IS NOT:
- an **automated CI/CD pipeline** — automation assists the Builder and Auditor but does not replace human review;
- a **scoring or ranking mechanism** — Gates return outcomes, not numeric scores;
- a **machine-authoritative decision** — the final disposition is always human;
- an **auto-rejection mechanism** — `FAIL` requires human disposition (§7.3), not machine rejection;
- a **tool or product** — this Standard declares the contract, not a specific tool;
- a **one-time check** — Gates apply at every Lifecycle stage transition;
- a **substitute for the Constitution** — Gates operationalize §11 but do not replace it;
- a **Project-specific instrument** — the Quality Gate Types and Evaluation Model are Foundation-wide (project-independent per §11.4).

---

## §4. Quality Gate Lifecycle

### §4.1 Overview

The Quality Gate Lifecycle declares **five ordered stages** that a subject artifact traverses from initial authoring to Stable status. At each transition, the applicable Quality Gate Types (§4.2) are applied. A subject artifact may not skip a stage. A subject artifact may not transition with an unresolved `FAIL`, `BLOCKED`, or `REPAIR REQUIRED` outcome.

```
Draft Gate → Review Gate → Approval Gate → Release Candidate Gate → Stable Gate
```

### §4.2 Stage Definitions

#### §4.2.1 Stage 1 — Draft Gate

**Purpose:** Verify that a draft artifact satisfies the Structure Gate (§4.3.1) and the Scope Compliance Gate (§4.3.5) before it enters the formal Review pipeline.

**Subject status:** `Draft`.

**Applicable Gates:** Structure Gate; Scope Compliance Gate.

**Outcome policy:** A `PASS` outcome advances the artifact to `In Review`. A `FAIL` or `REPAIR REQUIRED` outcome returns the artifact to `Draft` with a repair instruction (§8.1).

**Forbidden outcomes at this stage:** `BLOCKED` is reserved for §4.2.3 onward; a Draft Gate cannot return `BLOCKED`.

#### §4.2.2 Stage 2 — Review Gate

**Purpose:** Verify that an `In Review` artifact satisfies all six Quality Gate Types (§4.3) and produces an Audit Report (§6).

**Subject status:** `In Review`.

**Applicable Gates:** All six — Structure, Consistency, Cross Reference, Isolation, Scope Compliance, Security Boundary.

**Outcome policy:** A `PASS` outcome on all six Gates advances the artifact to `Pending Approval`. Any `FAIL`, `BLOCKED`, or `REPAIR REQUIRED` outcome triggers the Failure Handling procedure (§8).

**Audit hook:** An Audit Report (`FOUNDATION/04-Audits/AUDIT-<subject-id>.md`) is generated per §6.

#### §4.2.3 Stage 3 — Approval Gate

**Purpose:** Verify that a `Pending Approval` artifact has been formally reviewed and approved by the assigned Reviewer(s), producing a Review Record (§7).

**Subject status:** `Pending Approval`.

**Applicable Gates:** Cross Reference Gate (re-verify all Reviewer references); Scope Compliance Gate (re-verify against the original Scope Declaration).

**Outcome policy:** A `PASS` outcome (i.e., a signed Review Record with disposition `Approved`) advances the artifact to `Approved`. A `Rejected` Review Record disposition returns the artifact to `Draft`. An unresolved `BLOCKED` outcome halts the Lifecycle and triggers Escalation (§8.3).

**Reviewer rule:** The Reviewer **must not** be the Builder who authored the artifact (separation of duties per Constitution §5).

#### §4.2.4 Stage 4 — Release Candidate Gate

**Purpose:** Verify that an `Approved` artifact, when aggregated with all other `Approved` artifacts of a release, meets the Release Quality Gate (§9).

**Subject status:** `Approved` → aggregated into a Release Candidate (RC).

**Applicable Gates:** All six Gates applied to the **RC aggregate** (i.e., the set of all `Approved` artifacts in the RC). A `FAIL` on any single artifact fails the RC aggregate.

**Outcome policy:** A `PASS` outcome advances the RC to `RC Verified`. A `FAIL` outcome blocks the RC; individual artifacts may be re-submitted through Stage 1.

**RC artifact:** A `Release Candidate` is not a single artifact; it is the **set** of all `Approved` artifacts proposed for the release. The Quality Gate at this stage evaluates the **aggregate**.

#### §4.2.5 Stage 5 — Stable Gate

**Purpose:** Verify that a `RC Verified` aggregate has been formally released and meets the Stable Release Requirements (§9.2). After this stage, the artifact is `Stable` and enters the Deprecation Policy (§12).

**Subject status:** `RC Verified` → `Stable`.

**Applicable Gates:** Stability Gate (no further changes permitted; structural lock applied); Final Approval Gate (signed Stable Release Record).

**Outcome policy:** A `PASS` outcome advances the aggregate to `Stable`. A `FAIL` outcome triggers an emergency patch cycle and re-application of Stages 3 and 4.

**Stability rule:** Once an artifact is `Stable`, it may not be modified in place. Changes require a new Draft Gate cycle (§12.3).

### §4.3 Stage Transition Table

| From | To | Trigger | Required Gate Verdict |
|---|---|---|---|
| (none) | Draft | Authoring | n/a |
| Draft | In Review | Builder submits | Draft Gate: `PASS` |
| In Review | Pending Approval | Audit Report filed | Review Gate: `PASS` on all six Gates |
| Pending Approval | Approved | Reviewer signs | Approval Gate: signed Review Record with disposition `Approved` |
| Approved | RC aggregate | Release Manager collects | n/a (aggregation) |
| RC aggregate | RC Verified | RC Gate applied | Release Candidate Gate: `PASS` on aggregate |
| RC Verified | Stable | Final Approval signed | Stable Gate: `PASS` on Stability + Final Approval |

---

## §5. Quality Gate Types

### §5.1 Overview

The Foundation recognizes **six Quality Gate Types**. Each Type operationalizes one or more of the four §11 Quality Gate criteria (Completeness, Compliance, Cross Reference, Isolation). Every Quality Gate Type returns an Evaluation outcome drawn from the Evaluation Model (§5.4).

### §5.2 Type Roster

| # | Type | §11 Criterion | Purpose |
|---|---|---|---|
| 1 | Structure Gate | Completeness | Verifies the artifact's structural form (header fields, sections, length, required parts). |
| 2 | Consistency Gate | Compliance | Verifies internal consistency (no contradictions within the artifact). |
| 3 | Cross Reference Gate | Cross Reference | Verifies all references resolve and back-references exist per Constitution §10. |
| 4 | Isolation Gate | Isolation | Verifies semantic project-independence (per §11.4). |
| 5 | Scope Compliance Gate | Compliance | Verifies that the artifact honors its §15.5 Per-Task Scope Declaration. |
| 6 | Security Boundary Gate | Compliance | Verifies that the artifact does not introduce security boundary violations. |

### §5.3 Type Definitions

#### §5.3.1 Structure Gate

**Criterion:** Completeness (§11.1).

**Verifies:**
- All required header fields are present (per `schema-standard.md` §3.2 — `Status`, `Version`, `Foundation Version`, `Constitution Version`, `Path`, `Supersedes`, `Related`).
- All required sections are present per the artifact's Standard or Schema.
- The artifact declares its `Status`, `Version`, and `Foundation Version` consistently with the on-disk filename and the Foundation Version registry.

**PASS condition:** Every required field and section is present, and the declared values are consistent with the Foundation registry.

**FAIL condition:** Any required field or section is missing, or any declared value is inconsistent.

**REPAIR REQUIRED condition:** A field or section is present but malformed (e.g., wrong field name, wrong section ordering) — repairable by edit.

#### §5.3.2 Consistency Gate

**Criterion:** Compliance (§11.2).

**Verifies:**
- The artifact's clauses do not contradict each other.
- The artifact does not assert a fact that another clause of the same artifact denies.
- The artifact's declared status (e.g., `Draft / In Review`) is consistent with its declared version (e.g., `0.1.0-draft`).
- Cross-clause terminology is consistent (same term used for the same concept throughout).

**PASS condition:** No internal contradiction detected.

**FAIL condition:** Two or more clauses of the artifact assert incompatible facts.

**REPAIR REQUIRED condition:** Inconsistent terminology that can be resolved by renaming or clarification.

#### §5.3.3 Cross Reference Gate

**Criterion:** Cross Reference (§11.3).

**Verifies:**
- Every reference to a Constitution §, an FD, a Standard, a Policy, an RFC, an ADR, or any other Foundation artifact resolves to a real, on-disk artifact.
- Every reference uses the form mandated by Constitution §10 (path or §-reference).
- Every artifact referenced by this artifact has a back-reference (the Referenced-by clause).
- The Manifest (per `schema-standard.md` §8) declares all contained references.

**PASS condition:** Every forward reference resolves, every back-reference exists, and the Manifest is complete.

**FAIL condition:** Any reference fails to resolve to a real artifact.

**REPAIR REQUIRED condition:** A reference is correct in form but uses an outdated slug or version that can be updated.

**BLOCKED condition:** A reference points to an artifact whose status is `Frozen` or `Archived` and that artifact's replacement is not yet available.

#### §5.3.4 Isolation Gate

**Criterion:** Isolation (§11.4) — **semantic** project-independence rule.

**Verifies:**
- The artifact contains no reference to a specific Project (e.g., APES, any other Project name).
- The artifact's normative rules remain valid in the absence of any Project.
- The artifact does not introduce Project-specific governance, lifecycle, schema, or implementation rules.
- The artifact's `Related:` header field does not list any Project as a normative dependency.

**PASS condition:** The artifact is semantically Project-independent.

**FAIL condition:** The artifact contains a Project-specific rule or required reference that prevents it from being valid without that Project.

**REPAIR REQUIRED condition:** A Project reference is incidental (e.g., a comment or example) and can be removed without affecting normative content.

#### §5.3.5 Scope Compliance Gate

**Criterion:** Compliance (§11.2) — operationalizes §15.5 Per-Task Scope Declaration.

**Verifies:**
- The artifact honors its declared Allowed Files (§15.5).
- The artifact does not introduce any Forbidden File (§15.5).
- The artifact honors its declared Inputs (§15.5).
- The artifact produces its declared Outputs (§15.5).
- The artifact honors its declared Dependencies (§15.5).
- The artifact honors its declared Quality Gates (§15.5).
- The artifact honors its declared Stop Condition (§15.5).

**PASS condition:** Every Allowed File is present; no Forbidden File is present; Inputs / Outputs / Dependencies / Quality Gates / Stop Condition are honored as declared.

**FAIL condition:** A Forbidden File is present, or a declared Allowed File is missing, or a Stop Condition is violated (e.g., the artifact proceeds past its declared stop point).

**REPAIR REQUIRED condition:** A declared Output is malformed or incomplete (e.g., a Report missing a required section).

#### §5.3.6 Security Boundary Gate

**Criterion:** Compliance (§11.2) — operationalizes the Security Boundary contract.

**Verifies:**
- The artifact does not introduce or require code execution (e.g., no source code, no executable scripts, no machine code).
- The artifact does not introduce or require sub-process spawning.
- The artifact does not introduce or require network access (e.g., no API keys, no endpoint URLs in normative clauses).
- The artifact does not introduce or require auto-commit, auto-approve, or auto-rejection (i.e., no autonomous decisions that bypass human review).
- The artifact does not introduce isolation violations (e.g., shared mutable state across Projects, cross-Project writes).
- For Runtime / Engine / SDK / Plugin artifacts (when they exist): the artifact honors the Runtime Security Boundary declared in `runtime-specification.md` §10.

**PASS condition:** No security boundary violation.

**FAIL condition:** The artifact requires code execution, sub-process spawning, network access, auto-decision, or isolation violation.

**REPAIR REQUIRED condition:** The artifact contains security-relevant content that can be removed (e.g., an example URL or a sample API key).

### §5.4 Evaluation Model

The Foundation recognizes **four Evaluation outcomes**. Every Quality Gate Type returns exactly one outcome per evaluation. Outcomes are not numeric scores; they are categorical labels.

#### §5.4.1 PASS

**Meaning:** The artifact satisfies every check that the Quality Gate Type performs.

**Consequence:** The artifact advances to the next Lifecycle stage (or remains eligible to advance if all other applicable Gates also return `PASS`).

#### §5.4.2 FAIL

**Meaning:** The artifact violates one or more checks that the Quality Gate Type performs, and the violation is **not repairable** within the artifact itself (e.g., a structural form violation that requires a new Draft cycle).

**Consequence:** The artifact is returned to `Draft` (per §8.1 Correction Cycle). A new Draft Gate cycle is required.

#### §5.4.3 BLOCKED

**Meaning:** The evaluation cannot proceed because an external dependency is unresolved (e.g., a referenced artifact has not yet been produced, or a referenced artifact is in a `Frozen` state without a successor).

**Consequence:** The Lifecycle halts pending the resolution of the external dependency. Escalation (§8.3) may be invoked if the dependency is not resolved within the agreed SLA.

#### §5.4.4 REPAIR REQUIRED

**Meaning:** The artifact has a defect that is **repairable** by an in-place edit (e.g., a malformed field, an outdated reference, an incidental Project mention).

**Consequence:** The artifact is returned to `Draft` with a specific repair instruction. The repair is performed by the Builder; the artifact re-enters the Draft Gate cycle.

### §5.5 Outcome Precedence

When multiple Quality Gate Types are applied to a subject artifact, the **overall Lifecycle outcome** is determined by the following precedence (highest severity wins):

```
FAIL > BLOCKED > REPAIR REQUIRED > PASS
```

A single `FAIL` outcome from any applicable Gate blocks the artifact's advancement, regardless of `PASS` outcomes from other Gates.

### §5.6 Outcome Declaration

Every Gate evaluation **must** declare:
1. The Quality Gate Type applied (per §5.2).
2. The outcome (one of `PASS`, `FAIL`, `BLOCKED`, `REPAIR REQUIRED`).
3. The evidence (per §6.2 — the specific check, clause, or reference that produced the outcome).
4. The consequence (per §5.4 — the Lifecycle transition or repair instruction).
5. The Auditor identity (per §6.1).

A Gate evaluation that omits any of these five elements is **non-conformant** with this Standard.

---

## §6. Audit Relationship

### §6.1 Audit Responsibility

The **Auditor** is the role responsible for applying the six Quality Gate Types (§5.2) to a subject artifact and producing an **Audit Report** (per §6.3). Per Constitution §5, the Auditor is a separate role from the Builder (who authored the artifact) and the Reviewer (who approves it). In the Foundation cycle, the Builder performs a **self-audit** (§15.4) at the Review Gate (Stage 2), and a designated **Auditor** performs an **independent audit** at the same stage.

**Self-audit:** A Builder self-audit produces an Audit Report filed at `FOUNDATION/04-Audits/AUDIT-<subject-id>.md`. The self-audit declares the Builder identity, the subject, the six Gates applied, and the outcome per Gate.

**Independent audit:** A designated Auditor (human Architect or assigned Foundation reviewer) reviews the self-audit and may affirm, amend, or reject the self-audit verdict. An independent audit produces either an `Affirmed` or `Amended` Audit Report.

**Conflict rule:** If the Builder's self-audit verdict and the Auditor's independent verdict disagree, the **independent verdict prevails** (Constitution §5 — separation of duties).

### §6.2 Audit Evidence

Audit evidence is the **specific, cited material** that supports each Gate outcome. Evidence **must** include:
- The **clause, section, field, or rule** evaluated (with its exact text or a stable locator).
- The **outcome** declared (per §5.4).
- The **rationale** (a one-sentence explanation of why the evidence supports the outcome).

Evidence that omits the locator or rationale is **non-conformant**. The evidence locator may use one of the following forms:
- `§X.Y` — for a section reference within the artifact.
- `§X.Y.Z` — for a sub-clause reference.
- `<path>:<line>` — for an on-disk reference.
- `<header-field-name>` — for a header-field reference.

### §6.3 Audit Report

The Audit Report is the formal Foundation artifact that records the Audit. It is filed at `FOUNDATION/04-Audits/AUDIT-<subject-id>.md` (per `directory-standard.md` §6). The Audit Report **must** contain the elements defined in `schema-standard.md` §9 (Audit Schema) and the Audit Relationship clauses of this Standard.

**Required Audit Report sections:**
1. Audit metadata (ID, Foundation Version, Constitution Version, Date, Auditor identity, Subject, Verdict).
2. Audit method (the procedure followed, the tools used, the scope).
3. Quality Gate criteria evaluation (per the six Gates, each with outcome + evidence + rationale).
4. §15.5 Per-Task Scope Declaration compliance (if applicable).
5. Findings (severity-graded list of observations, defects, or notes).
6. Verdict (`PASS` if all Gates return `PASS` and §15.5 is honored; `FAIL` otherwise).

The Audit Report is **immutable-on-Approved**: once the Audit is filed and the artifact advances to `Approved`, the Audit Report may not be edited (per `governance-model.md` §8). Subsequent amendments require a new Audit cycle.

---

## §7. Review Relationship

### §7.1 Reviewer Role

The **Reviewer** is the role responsible for evaluating the Audit Report (§6) and the subject artifact, and for issuing a formal **Review Record** with a disposition. Per Constitution §5, the Reviewer:
- **must not** be the Builder who authored the artifact;
- **must not** be the Auditor who produced the Audit Report (separation of duties);
- **must** have access to the Constitution, the relevant Standard(s), the relevant Policy(s), and the Audit Report;
- **must** declare their identity, qualifications, and any conflict of interest in the Review Record.

In the Foundation cycle, the **human Architect** is the default Reviewer for Foundation Standards. For Project-local artifacts (downstream), the Reviewer is assigned per `approval-workflow.md` and the applicable Project governance.

### §7.2 Approval Boundary

The **approval boundary** is the stage transition between `Pending Approval` and `Approved` (per §4.2.3). The Reviewer acts **only** at the approval boundary; the Reviewer does not author content, does not edit the artifact, and does not amend the Audit Report.

**Permitted Reviewer actions at the approval boundary:**
1. Read the artifact.
2. Read the Audit Report.
3. Read all referenced Foundation artifacts.
4. Record observations and questions.
5. Issue a Review Record with one of the four dispositions (per §7.3).

**Forbidden Reviewer actions at the approval boundary:**
1. Edit the artifact.
2. Amend the Audit Report.
3. Bypass the Audit Report (the Reviewer **must not** approve an artifact whose Audit Report is missing or whose Verdict is not `PASS`).
4. Approve on behalf of another Reviewer.
5. Delegate the disposition to a non-Reviewer.

### §7.3 Reviewer Disposition

The Reviewer issues one of the following dispositions:

| Disposition | Meaning | Consequence |
|---|---|---|
| `Approved` | The Reviewer affirms the artifact and the Audit Report. | Artifact advances to `Approved`. |
| `Approved with Notes` | The Reviewer affirms the artifact but records non-blocking notes. | Artifact advances to `Approved`; notes are recorded for future amendments. |
| `Rejected` | The Reviewer rejects the artifact. | Artifact returns to `Draft`; a new Draft Gate cycle is required. |
| `Blocked` | The Reviewer cannot proceed because an external dependency is unresolved. | Lifecycle halts; Escalation (§8.3) may be invoked. |

**Default rule:** A disposition of `Approved` is the only disposition that advances the artifact to `Approved`. Any other disposition blocks the advancement.

### §7.4 Human Decision Principle

The final disposition is **always** a human decision. No machine, no automation, no CI/CD pipeline may issue a Reviewer disposition. Per Constitution §5 and §15.4, the human Reviewer is the locus of authority for the approval boundary.

This principle is **non-negotiable**. Even if every Quality Gate Type returns `PASS` and the Audit Verdict is `PASS`, the artifact **may not** advance to `Approved` without a human disposition of `Approved` (or `Approved with Notes`).

---

## §8. Failure Handling

### §8.1 Correction Cycle

When an applicable Quality Gate Type returns `FAIL` or `REPAIR REQUIRED`:
1. The Audit Report records the failed Gate(s) with locator and rationale (§6.2).
2. The artifact returns to `Draft` status.
3. The Builder performs the correction:
   - For `FAIL`: a new Draft Gate cycle is initiated; the original artifact is replaced by a corrected draft.
   - For `REPAIR REQUIRED`: the Builder applies the specific repair instruction in-place.
4. The corrected artifact re-enters the Review Gate (Stage 2).

The Correction Cycle **must not** exceed three iterations per artifact per Lifecycle stage. If three Correction Cycles fail, the artifact is **escalated** (§8.3).

### §8.2 Re-review

After a Correction Cycle, the artifact re-enters the Review Gate (Stage 2) with the same Audit Report structure (or an amended Audit Report if the defect warrants). Re-review **must** include:
1. Re-application of every Quality Gate Type that previously failed.
2. Confirmation that the repair instruction was followed.
3. Declaration of the new outcome per Gate.

A Re-review may not skip Gates, may not relax criteria, and may not issue an `Approved` disposition without passing all six Gates.

### §8.3 Escalation

If a Correction Cycle (§8.1) fails three times, or if a `BLOCKED` outcome persists, the artifact is **escalated** to the human Architect. The Escalation procedure is defined in `disagreement-and-escalation.md` and proceeds via the following route:

1. The Builder files an Escalation Record at `FOUNDATION/02-Governance/escalation-records.md` (or its successor per `directory-standard.md` §6).
2. The human Architect reviews the artifact, the Audit Report, the Correction Cycle history, and the Reviewer's disposition.
3. The human Architect issues one of:
   - A **manual override** that returns the artifact to `Draft` with explicit instructions.
   - A **deferral** that places the artifact in a `Frozen` status pending resolution of the blocking dependency.
   - A **withdrawal** that removes the artifact from the active Lifecycle.

Escalation is the **terminal** Failure Handling step. No further automated cycle follows Escalation without Architect intervention.

---

## §9. Release Quality Gate

### §9.1 RC Requirements

A **Release Candidate (RC)** is the aggregate of all `Approved` artifacts proposed for a release. The RC Quality Gate evaluates the **aggregate**, not individual artifacts (per §4.2.4).

**RC aggregate requirements:**
1. Every artifact in the aggregate has status `Approved`.
2. Every artifact in the aggregate has an Audit Report with verdict `PASS`.
3. Every artifact in the aggregate has a Review Record with disposition `Approved` (or `Approved with Notes`).
4. No artifact in the aggregate has an outstanding `REPAIR REQUIRED` or `BLOCKED` outcome.
5. The aggregate's Cross Reference Gate is re-verified: every cross-artifact reference resolves.
6. The aggregate's Isolation Gate is re-verified: the aggregate, taken as a whole, remains semantically Project-independent.
7. The aggregate declares a `Release Manifest` (per `schema-standard.md` §8 and `schema-standard.md` §12 Release Schema).

**RC Verdict:**
- `PASS` — all seven requirements satisfied.
- `FAIL` — any requirement fails.
- `BLOCKED` — an external dependency (e.g., a required artifact not yet `Approved`) prevents evaluation.

### §9.2 Stable Release Requirements

A **Stable release** is an RC that has passed the RC Quality Gate (§9.1) and has received Final Approval (§9.3).

**Stable release requirements (additional to §9.1):**
1. The RC Quality Gate has been `PASS` for at least one Reviewer-confirmed cycle.
2. No critical-severity findings are open.
3. No major-severity findings are open.
4. All minor-severity findings have documented disposition (resolved, deferred with rationale, or accepted).
5. The Final Approval (§9.3) has been signed by the human Architect (and any other required signatory per the applicable Policy).

**Stable Verdict:** `PASS` (Stable) or `FAIL` (revert to RC).

### §9.3 Final Approval

The **Final Approval** is the human disposition that transitions the RC aggregate from `RC Verified` to `Stable`. The Final Approval is recorded at `FOUNDATION/07-Reviews/REVIEW-<release-id>.md` (or its successor path per `directory-standard.md` §6).

**Final Approval contents:**
1. The release identity (RC ID, target version, target date).
2. The Reviewer identity (must be the human Architect for Foundation RC; downstream Projects may have additional signatories).
3. The disposition (`Stable` or `Revoke`).
4. The signature block (Reviewer Name, Review Date, Signature).

**Rule:** A `Stable` disposition is the only disposition that advances the release to `Stable`. A `Revoke` disposition returns the aggregate to `RC` with required corrections.

### §9.4 Foundation RC Gate

Per Constitution §14, the Foundation `v1.0.0-rc.1` RC gate is the **only** Foundation RC gate. It is reserved for the Foundation Release Candidate task (Task 12 per `approval-workflow.md`). No Foundation artifact may declare `v1.0.0-rc.1` or `v1.0.0` before Task 12 passes review.

---

## §10. Compatibility

### §10.1 Version Changes

This Standard declares its version using Semantic Versioning (SemVer) per Constitution §8. The version is recorded in the header field `Version:` and matches the on-disk filename suffix (per `directory-standard.md` §10).

**Version bump triggers:**
- **MAJOR** (X.0.0): a non-backward-compatible change to a Quality Gate Type (§5.2), a Lifecycle stage (§4.2), or an Evaluation outcome (§5.4).
- **MINOR** (0.X.0): a backward-compatible addition of a new sub-clause, a new outcome sub-type, or a new evidence locator form (§6.2).
- **PATCH** (0.0.X): a typo fix, formatting change, or clarification that does not alter normative content.

**Pre-release tags:**
- `0.1.0-draft` — initial draft, in active Foundation cycle.
- `0.1.0-rc.1` — reserved for Task 12 only.
- `1.0.0` — the first Stable Foundation release (gated by Task 12).

### §10.2 Migration Rules

When this Standard changes in a non-backward-compatible way (MAJOR bump), a **Migration Plan** must be produced. The Migration Plan declares:
1. The previous version (e.g., `0.1.0`).
2. The new version (e.g., `1.0.0`).
3. The list of breaking changes (with locator and rationale).
4. The list of artifacts affected by the breaking changes.
5. The Migration procedure (per-artifact edit, re-audit, re-review).

The Migration Plan is filed at `FOUNDATION/02-Governance/migration-plans/` (or its successor path) and is reviewed per `change-control-policy.md`.

### §10.3 Future Extension

Future extensions to this Standard follow Constitution §13 (Future Extension Policy):
1. Extensions are **additive-only**. A future extension may add a new Quality Gate Type, a new Lifecycle stage, a new Evaluation outcome, or a new evidence locator form. An extension may not remove or weaken an existing Gate, stage, or outcome.
2. An extension that weakens an existing Gate requires a new FD and ratification per `foundation-decision-policy.md`.
3. Extensions are recorded in `CHANGELOG.md` under the `Added` heading per the artifact's lifecycle (per `governance-model.md` §7).

---

## §11. Cross References

Per Constitution §10 (Cross Reference Policy), this Standard declares the following mandatory references.

**Constitution references:**
- §1 (Governance Hierarchy) — precedence rules
- §2 (Compatibility Policy) — three version surfaces
- §3 (Design Principles) — twelve binding principles
- §5 (Role Model) — Builder / Auditor / Reviewer separation
- §6 (RFC Governance) — RFC class lifecycle
- §7 (Decision Records) — FD format and activation
- §8 (Versioning Policy) — SemVer bump triggers
- §9 (Naming Convention) — header field form
- §10 (Cross Reference Policy) — mandatory references
- §11 (Quality Gate) — four criteria; this Standard operationalizes them
- §12 (Deprecation Policy) — six-state model for deprecated Gates
- §13 (Future Extension Policy) — additive-only extensions
- §14 (Success Criteria) — Foundation Complete, RC, Stable, Platform Stable, Production Ready
- §15 (Foundation Task Protocol) — §15.3 Hard Prohibitions, §15.4 Self-audit, §15.5 Per-Task Scope
- §15.3 — Hard Prohibitions
- §15.4 — Self-audit rule
- §15.5 — Per-Task Scope Declaration

**Standard references:**
- `directory-standard.md` §4 (top-level layout), §6 (per-class storage paths), §8 (reserved directories), §10 (path-validation rules)
- `schema-standard.md` §3.2 (Standard headers), §4 (Evidence Schema), §5 (Report Schema), §6 (Review Schema), §7 (Statistics Schema), §8 (Manifest Schema), §9 (Audit Schema), §10 (Task Schema), §11 (Pack Schema), §12 (Release Schema)
- `pack-standard.md` §17 (Pack Quality Gate) — Pack-specific Quality Gate integration
- `runtime-specification.md` §8 (Quality Gate Integration), §10 (Runtime Security Boundary) — Runtime-specific Quality Gate integration

**Policy references:**
- `governance-model.md` §2 (Hierarchy), §6 (Artifact Types), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession)
- `approval-workflow.md`
- `change-control-policy.md`
- `disagreement-and-escalation.md`
- `roles-and-authority.md`
- `rfc-policy.md`
- `foundation-decision-policy.md`
- `adr-policy.md`

**Back-references (this Standard is referenced by):**
- (none yet — this Standard is new at `0.1.0-draft`; back-references will be added by future Standards that integrate with the Quality Gate)

---

## §12. Relationship to Other Artifacts

### §12.1 To the Constitution

This Standard operationalizes **Constitution §11 (Quality Gate)** and does not contradict any clause of the Constitution. If a future Constitution amendment changes §11, this Standard must be updated to reflect the new clause (per `change-control-policy.md`).

### §12.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for Audit Reports (`FOUNDATION/04-Audits/`) and Review Records (`FOUNDATION/07-Reviews/`).
- **Schema Standard** — declares the Audit Schema (§9), Review Schema (§6), Report Schema (§5), Evidence Schema (§4), Manifest Schema (§8), and Release Schema (§12) that this Standard requires.
- **Pack Standard** — declares a Pack-specific Quality Gate (§17) that is compatible with the six Foundation Gates (§5.2).
- **Runtime Specification** — declares the Runtime Quality Gate Integration (§8) and Runtime Security Boundary (§10) that the Security Boundary Gate (§5.3.6) verifies.

### §12.3 To Policies

- **Approval Workflow** — declares the Reviewer's approval procedure that this Standard references in §7.
- **Change Control Policy** — declares the procedure for amending this Standard.
- **Disagreement and Escalation** — declares the Escalation procedure (§8.3) that this Standard references.
- **Roles and Authority** — declares the role boundaries (Builder / Auditor / Reviewer) that this Standard references in §6.1 and §7.1.

### §12.4 To Future Artifacts

Future artifacts that may reference this Standard include Engine Specifications (downstream), SDK Specifications (downstream), and Project-local Quality Gate profiles (downstream, when Projects exist).

---

## §13. Ratification

This Standard is **Draft / In Review** at version `0.1.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0007-ratify-quality-gate-standard.md` is created in this Foundation task.

**Ratification path (when invoked by a future Foundation cycle):**
1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition (`Approved`, `Approved with Notes`, `Rejected`, or `Blocked`).
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0007-ratify-quality-gate-standard.md` per `foundation-decision-policy.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.
5. After Ratification, this Standard's `Status:` header field is updated to `Ratified` and its `Version:` may advance per §10.1.

Until `FD-0007` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

---

## §14. Acknowledgments

This Standard is built on the Foundation work of Tasks 01–06, specifically:
- Task 01 — Constitution (v0.1.0-draft, Provisional).
- Task 02 — Governance Model, Roles & Authority, Approval Workflow, Change-Control Policy, Disagreement & Escalation.
- Task 03 — Directory Standard.
- Task 04 — Schema Standard.
- Task 05 — Builder Pack Standard.
- Task 06 — Builder Runtime Specification.

This Standard is **technology-neutral** and **project-independent**. It contains no language binding, no framework binding, no serialization binding, no operating-system binding, no Project-specific rule, no validator implementation, no scoring engine, no automation, no CI/CD, no GitHub Actions workflow, no engine / runtime / SDK / plugin implementation, and no Pack instance.

---

*End of quality-gate-standard.md v0.1.0-draft (Draft / In Review).*