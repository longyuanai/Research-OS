# Research-OS Foundation — Release Specification

**Status:** Draft / In Review
**Version:** 0.2.0-draft
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Path:** `FOUNDATION/03-Standards/release-specification.md`
**Supersedes:** none
**Related:** Constitution §1 (Governance Hierarchy); §2 (Compatibility Policy); §3 (Design Principles); §4 (Lifecycle Model); §5 (Role Model); §6 (RFC Governance); §7 (Decision Records); §8 (Versioning Policy); §9 (Naming Convention); §10 (Cross Reference Policy); §11 (Quality Gate); §12 (Deprecation Policy); §13 (Future Extension Policy); §14 (Success Criteria); §15 (Foundation Task Protocol); §17 (Provisional Governance); `governance-model.md` §2 (Hierarchy), §3 (Role Model), §6 (Artifact Types — Release), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession), §13 (Additive-only extensions); `directory-standard.md` §4, §6, §8, §10; `schema-standard.md` §11 (Pack Schema), §12 (Release Schema); `pack-standard.md` §3–§21; `runtime-specification.md` §4 (Runtime Architecture), §7 (Runtime Output Specification), §10 (Runtime Security Boundary), §11 (Runtime Compatibility); `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship), §7 (Review Relationship), §8 (Failure Handling), §9 (Release Quality Gate), §10 (Compatibility); `engine-specification.md` §3–§11; `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture); `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model); `workspace-specification.md` §2 (Workspace Architecture Purpose), §3 (Workspace Boundary Model), §4 (Workspace Lifecycle), §6 (Permission and Security Model), §7 (Workspace Types), §8 (Workspace Compatibility); `approval-workflow.md`; `change-control-policy.md`; `disagreement-and-escalation.md`; `roles-and-authority.md`; `rfc-policy.md`; `foundation-decision-policy.md`; `adr-policy.md`

---

## §1. Purpose and Scope

### §1.1 Purpose

This Standard declares the canonical *form* of a Foundation **Release**: the L5 binding container that aggregates the Foundation's normative artifacts (Constitution, Standards, Policies, FDs, RFCs, ADRs, Engines, SDKs, Plugin Specifications, Workspace Specifications, Foundation Packs) into a coherent, versioned, ratifiable, integrity-protected Foundation version state. A Release is the **only** Foundation artifact that may advance the Foundation Version recorded in `FOUNDATION/VERSION` (per `schema-standard.md` §12 and Constitution §8).

A Release is distinct from:

- A **Foundation Pack** (`pack-standard.md`) — a Pack is a declarative *bundle* of Missions / Programs / Tasks / Deliverables; a Release is the *milestone* that aggregates Foundation normative artifacts.
- A **Workspace** (`workspace-specification.md`) — a Workspace is a persistent, bounded, audited *context* for Pack execution; a Release is the *coherent version state* declared for the Foundation.
- An **FD** (`foundation-decision-policy.md`) — an FD is a *decision* about the Foundation; a Release is the *aggregated state* declared when one or more FDs are ratified.
- A **Tag** — a tag is a *pointer*; a Release is a *declarative artifact* with a Manifest, Quality Gate verdict, Authorizing FD, and Release Manager disposition.

This Standard:

1. Defines the **Release Architecture Purpose** (§2).
2. Defines the **Release Boundary Model** — where a Release terminates and the Foundation / downstream consumers continue (§3).
3. Defines the **Release Lifecycle** — the seven ordered stages a Release traverses from Draft to Superseded (§4).
4. Defines the **Release Interface Specification** — Input Contract, Output Contract, Metadata, Versioning, Compatibility (§5).
5. Defines the **Release Composition Model** — what a Release MUST include, MAY include, and SHALL NOT include (§6).
6. Defines the **Release Versioning and Approval Model** — SemVer discipline, Authorizing FD, Release Manager disposition, Foundation Version advancement (§7).
7. Defines the **Release Compatibility** — Version compatibility, Migration rules, Extension rules, Supersession rules (§8).
8. Defines **Foundation Phase Constraints** — the five constraints preserved during the Foundation phase, including the prohibitions on `rc` and `ga` Release types until ratification (§9).

This Standard does **not** issue any Release. It does **not** declare a `0.1.0-rc.1` Release, a `1.0.0-rc.1` Release, or a `1.0.0` Release. It does **not** advance the Foundation Version. It does **not** create a Release Manifest. It does **not** invoke a Release Quality Gate. It does **not** issue an FD that authorizes a Release. It declares the *contract* a conformant Release specification must satisfy.

### §1.2 In-Scope

1. The **release architecture purpose** (§2).
2. The **release boundary model** — Release layer diagram, boundary rules, crossing points, relationship to Workspace and Pack boundaries (§3).
3. The **release lifecycle** — seven stages: Draft, Submitted, Under Review, Approved, Applied, Superseded, Withdrawn (§4).
4. The **release interface specification** — Input Contract, Output Contract, Metadata, Versioning, Compatibility (§5).
5. The **release composition model** — what a Release MUST / MAY / SHALL NOT contain (§6).
6. The **release versioning and approval model** — SemVer discipline, Foundation Version advancement, Authorizing FD, Release Manager disposition, Release Quality Gate (§7).
7. The **release compatibility** rules — Version compatibility, Migration rules, Extension rules, Supersession rules (§8).
8. The **Foundation Phase Constraints** — the five constraints preserved during the Foundation phase; the prohibition on `rc` and `ga` Release types until Task 12 ratification is invoked (§9).
9. Cross-references to Constitution, Standards, and Policies (§10).
10. Relationship to Constitution, other Standards, and future artifacts (§11).

### §1.3 Out-of-Scope

1. **Release issuance** — no `RELEASE-*.md` is created; no `FOUNDATION/16-Releases/` directory is created; no Release Manifest is created; no `FOUNDATION/VERSION` file is created or modified.
2. **Version advancement** — no `0.1.0-rc.1`, `1.0.0-rc.1`, or `1.0.0` Release is declared; no `FOUNDATION/VERSION` is bumped from `0.1.0-dev`.
3. **Foundation Decision (FD) creation** — no `FD-0012-ratify-release-specification.md` is created; no Release-authorizing FD is created.
4. **Network access** — no live calls to any host platform; no endpoint URLs in normative clauses; no secrets in repository.
5. **Engine / Runtime / SDK / Plugin / Workspace implementation** — these remain downstream deliverables; the Release Specification references them contractually only.
6. **Pack instance creation** — no `PACK-*.md`, no Mission / Program / Task / Deliverable artifacts, no Pack execution.
7. **APES migration or Project-specific governance** — APES remains a paused Project.
8. **Sprint execution** — no Sprint is executed in this Foundation task.
9. **No git operations** — no `git tag`, `git commit`, `git push`, `git branch`, no GitHub release, no remote operation.
10. **Foundation Phase Constraint violation** — Foundation Version remains `0.1.0-dev`; Constitution remains `v0.1.0-draft` Provisional; no `rc` Release is declared; no Pack is instantiated; no Project is instantiated.

---

## §2. Release Architecture Purpose

### §2.1 Definition

A **Release** is a Foundation L5 binding container that:

- **Aggregates** the Foundation's normative artifacts (Constitution, Standards, Policies, FDs, RFCs, ADRs, Engine Specifications, SDK Specifications, Plugin Specifications, Workspace Specifications, Foundation Packs) into a coherent, versioned, integrity-protected Foundation version state.
- **Advances** the Foundation Version recorded in `FOUNDATION/VERSION` (per `schema-standard.md` §12 and Constitution §8) — and is the **only** Foundation artifact that may do so.
- **Declares** a Release Manifest enumerating the contents of the Release (per `schema-standard.md` §8 and §12).
- **Passes** the Foundation Quality Gate's **Release Quality Gate** (per `quality-gate-standard.md` §9) before advancing the Foundation Version.
- **Is authorized** by a Foundation Decision (FD) issued by the human Architect per `foundation-decision-policy.md`.
- **Traverses** seven Lifecycle stages (per §4) — Draft → Submitted → Under Review → Approved → Applied → Superseded → Withdrawn.
- **Is technology-neutral** in specification; the **technology mapping** is downstream.
- **Is project-independent** during the Foundation phase; a Release MAY issue artifacts that downstream Projects consume, but no Release is Project-specific during the Foundation phase.

### §2.2 What a Release IS

A Release IS:

- a **binding container** — it binds the Foundation's normative artifacts into a single coherent state;
- a **version state milestone** — it declares a Foundation Version state (e.g., `0.1.0-dev`, `0.1.0-rc.1`, `1.0.0`);
- a **declarative artifact** — it declares what is in the Release via its Manifest; it does not execute anything;
- a **ratification outcome** — every Release is authorized by an FD that has itself passed Review;
- a **human-gated artifact** — every Release requires a Release Manager disposition (per §7);
- a **fail-closed artifact** — a Release with unresolved Quality Gate findings, unresolved Audit defects, or unratified FDs cannot transition to `Approved`;
- a **technology-mappable but technology-neutral spec** — a Release is declared in natural-language contract; a concrete Release instance maps the contract to a host environment post-Foundation;
- a **supersession-bounded instance** — every Release instance has a defined Supersession path (per §8.4);
- a **Foundation-only artifact** during the Foundation phase — no Project owns a Release; no Release is restricted to any Project.

### §2.3 What a Release IS NOT

A Release IS NOT:

- a **Foundation Pack** — Packs are declarative bundles of Missions / Programs / Tasks / Deliverables; Releases are aggregated version-state milestones (per `pack-standard.md` §3).
- a **Builder Workspace** — Workspaces are persistent, bounded, audited contexts for Pack execution; Releases are aggregated version-state declarations (per `workspace-specification.md` §2).
- a **Builder Runtime** — Runtimes are executors; Releases are aggregated declarations (per `runtime-specification.md` §3).
- a **Foundation Engine** — Engines are L5 specialist components inside the Foundation trust boundary; Releases aggregate Foundation artifacts (per `engine-specification.md` §3).
- a **Foundation SDK** — SDKs are interface contracts; Releases are aggregated declarations (per `sdk-specification.md` §3).
- a **Foundation Plugin** — Plugins are external adapters; Releases do not cross third-party trust boundaries (per `plugin-specification.md` §2).
- a **Foundation Decision (FD)** — FDs are decisions; Releases are aggregated states (per `foundation-decision-policy.md`).
- a **Release Candidate (RC) tag** during the Foundation phase — `rc` and `ga` Release types are **forbidden** during the Foundation phase per §9 and Constitution §15.3.
- a **Git tag** — a Release declares an aggregated state; a git tag is one possible *pointer* to that state, not the state itself.
- a **Project migration trigger** — a Release MAY be consumed by a Project, but the Release does not migrate any Project; Project migration is a Project-level operation.
- a **trust conduit** — a Release does not relay Foundation credentials between Workspaces or to a Project (per §6).
- a **Project-specific scope** during the Foundation phase — no Release is owned by any Project; no Release is restricted to any Project.

### §2.4 Relationship to Foundation Components

| Component | Role | Relationship to Release |
|---|---|---|
| Constitution (`FOUNDATION/01-Constitution/`) | Foundational governance | A Release MAY amend the Constitution only via an Authorizing FD; the Constitution's Version is recorded in the Release Manifest |
| Standards (`FOUNDATION/03-Standards/`) | L3 normative specifications | A Release aggregates ratified Standards and declares each Standard's Version at Release time |
| Policies (`FOUNDATION/02-Governance/`) | L3 governance policies | A Release aggregates ratified Policies and declares each Policy's Version at Release time |
| FDs (`FOUNDATION/09-Decisions/`) | Decisions | A Release is authorized by one or more FDs; the FDs are listed in the Release Manifest |
| RFCs (`FOUNDATION/08-RFCs/`) | Proposals | A Release MAY aggregate FRFCs / RRFCs that have reached `Accepted` status |
| ADRs (`FOUNDATION/10-ADRs/`) | Architecture Decision Records | A Release MAY aggregate ADRs that have reached `Accepted` status |
| Engines (`FOUNDATION/03-Standards/engine-specification.md`) | L5 specialist components | A Release aggregates Engine Specifications; concrete Engine instances are post-Foundation |
| SDKs (`FOUNDATION/03-Standards/sdk-specification.md`) | L5 interface contracts | A Release aggregates SDK Specifications; concrete SDK instances are post-Foundation |
| Plugins (`FOUNDATION/03-Standards/plugin-specification.md`) | L5 external adapters | A Release aggregates Plugin Specifications; concrete Plugin instances are post-Foundation |
| Workspaces (`FOUNDATION/03-Standards/workspace-specification.md`) | L5 persistent contexts | A Release aggregates Workspace Specifications; concrete Workspace instances are post-Foundation |
| Foundation Packs (`FOUNDATION/03-Standards/pack-standard.md`) | L5 declarative bundles | A Release MAY aggregate Foundation Packs that have passed the Release Quality Gate |
| Manifest (`schema-standard.md` §8) | Declarative contents list | A Release has a Manifest that enumerates every artifact in the Release |
| Quality Gate (`quality-gate-standard.md` §9) | Release gating | A Release MUST pass the Release Quality Gate before advancing the Foundation Version |

A Release is the **outer aggregator**. The Constitution is **the root**. The Standards / Policies / FDs / RFCs / ADRs / Engines / SDKs / Plugins / Workspaces / Packs are **the contents**. The Manifest is **the contents list**. The Quality Gate is **the gate**.

---

## §3. Release Boundary Model

### §3.1 Boundary Layers

The Release Boundary is **layered**. From the outside (downstream consumer) inward:

```
┌────────────────────────────────────────────────┐
│ Downstream Consumer                            │   ← Project / external system / future
│                                                │     Foundation-version consumer
├────────────────────────────────────────────────┤
│ Release Physical Boundary                      │   ← on-disk Release directory
│ (release directory, hash manifest)              │     (FOUNDATION/16-Releases/ — reserved)
├────────────────────────────────────────────────┤
│ Release Manifest Boundary                      │   ← what the Release declares as in-scope
│ (Manifest entries, declared Versions,           │     (per schema-standard.md §8, §12)
│  declared Authorizing FDs)                     │
├────────────────────────────────────────────────┤
│ Release Approval Boundary                      │   ← what the Release has been authorized to declare
│ (FD authorizations, Release Manager            │     (per foundation-decision-policy.md)
│  disposition, Release Quality Gate verdict)    │
├────────────────────────────────────────────────┤
│ Release Composition Boundary                   │   ← what the Release contains
│ (Constitution, Standards, Policies, FDs,       │
│  RFCs, ADRs, Engine Specs, SDK Specs,          │
│  Plugin Specs, Workspace Specs, Packs)         │
├────────────────────────────────────────────────┤
│ Foundation Storage                             │   ← Foundation artifact storage (per directory-standard.md)
└────────────────────────────────────────────────┘
```

### §3.2 Boundary Rules

1. A Release integrates with the Foundation **only** through the Manifest, the Authorizing FD, and the Release Quality Gate; direct file system modification outside the Release Boundary is **forbidden**.
2. A Release SHALL declare its Contents via its Manifest (per §6 and `schema-standard.md` §8, §12); the Manifest SHALL exhaustively enumerate every artifact in the Release.
3. A Release SHALL NOT modify Foundation artifacts outside its declared Contents (§6); modification is mediated by the Release Manager and recorded in the Release Audit hook.
4. A Release SHALL NOT advance the Foundation Version without a valid Authorizing FD and a passing Release Quality Gate verdict.
5. A Release SHALL NOT include any artifact whose Version is newer than the Foundation Version the Release declares as `Foundation-Version-New`.
6. A Release SHALL NOT include any artifact that has not passed the Foundation Quality Gate (per `quality-gate-standard.md` §5, §9).
7. A Release SHALL NOT include any Project-specific artifact during the Foundation phase.
8. A Release SHALL NOT relay Foundation credentials, tokens, or secrets to a Project or to a downstream consumer beyond what the Manifest expressly declares.
9. A Release SHALL NOT bypass the Release Quality Gate; every Release MUST pass the Gate before advancing to `Approved`.
10. A Release SHALL be **bounded**: its declared Contents, declared Versions, declared Authorizing FD(s), and declared Manifest shall together exhaustively describe what the Release contains and what it MAY do.

### §3.3 Boundary Crossing Points

Only the following Boundary crossings are permitted:

| Direction | Mediator | Recorded As |
|---|---|---|
| Authorizing FD → Release (input) | FD Manifest | Release Audit hook |
| Release Manifest → Release Quality Gate | Manifest + Quality Gate | Quality Gate Audit hook + Release Audit hook |
| Release Quality Gate → Release (verdict) | Quality Gate Standard §9 | Quality Gate Audit hook + Release Audit hook |
| Release Manager → Release (disposition) | Release Manager role | Release Audit hook |
| Release → Foundation Version (`FOUNDATION/VERSION`) | Release + FD + Manifest | `FOUNDATION/VERSION` updated atomically with Audit hook |
| Release → Foundation Storage | Release Manifest + Directory Standard | Manifest entry + Audit hook |
| Release → Downstream Consumer (output) | Release Manifest | Downstream consumer's Audit hook |
| Previous Release → New Release (Supersession) | Supersession rule (§8.4) | Supersession Audit hook on both Releases |

A Boundary crossing that is not mediated by the indicated component, or that is not recorded as indicated, is a **Boundary violation** (per §7 and `quality-gate-standard.md` §5.3.6).

### §3.4 Boundary to Pack, Runtime, Engine, SDK, Plugin, Workspace Specs

This Standard **references** but does **not duplicate**:

- `pack-standard.md` §3 (Pack Definition), §4 (Pack Lifecycle), §6 (Manifest rules), §11–§13 (Audit/Review/Report hooks), §16 (Versioning), §21 (Release hooks).
- `runtime-specification.md` §4 (Runtime Architecture), §7 (Runtime Output Specification), §10 (Runtime Security Boundary), §11 (Runtime Compatibility).
- `engine-specification.md` §3–§11.
- `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture).
- `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model), §8 (Platform Plugin Specifications).
- `workspace-specification.md` §2 (Workspace Architecture Purpose), §3 (Workspace Boundary Model), §4 (Workspace Lifecycle), §6 (Permission and Security Model), §7 (Workspace Types), §8 (Workspace Compatibility).

This Standard focuses on the Release's aggregated version-state declaration. Wherever this Standard and another Foundation Standard appear to overlap, the more-specific Standard prevails for the overlap zone, after cross-reference check (per `governance-model.md` §4 Conflict Resolution).

---

## §4. Release Lifecycle

### §4.1 Overview

Every Release instance traverses **seven ordered stages**. A Release may not skip a stage. A Release may not transition with an unresolved failure, unratified FD, or unaudited operation.

```
Draft → Submitted → Under Review → Approved → Applied → Superseded → Withdrawn
```

### §4.2 Stage 1 — Draft

**Purpose:** Compose the Release's intended Contents, Manifest, Authorizing FD(s), and target Foundation Version.

**Subject state:** `Undrafted` → `Draft`.

**Inputs:**
1. A list of Foundation artifacts proposed for inclusion (Standards, Policies, FDs, RFCs, ADRs, Engine Specs, SDK Specs, Plugin Specs, Workspace Specs, Foundation Packs).
2. The proposed target `Foundation-Version-New` (a valid SemVer bump from the current `FOUNDATION/VERSION`).
3. The proposed Authorizing FD(s) (per `foundation-decision-policy.md`).
4. The Release Manager (per `roles-and-authority.md`).

**Outputs:**
1. A `Release Draft Record` (`RELEASE-<scope>-<slug>-draft.md`) declaring the proposed Contents, Manifest, Authorizing FD(s), target Foundation Version, and Release Manager.

**Transition condition:** The Draft Record passes the Structure Gate (per `quality-gate-standard.md` §5.3.1) and the Isolation Gate (§5.3.4).

**Forbidden at this stage:** Submission, Review, Approval, Application.

### §4.3 Stage 2 — Submitted

**Purpose:** File the Release Draft with the Reviewer and queue it for the Release Quality Gate.

**Subject state:** `Draft` → `Submitted`.

**Inputs:**
1. The Release Draft Record.
2. A signed Submission request (Release Manager).
3. The proposed Release Quality Gate verdict declaration.

**Outputs:**
1. A `Release Submission Record` (`RELEASE-<scope>-<slug>-submission.md`) recording the submission timestamp, the Release Manager, and the queued Gate verdict declaration.

**Transition condition:** Signed Submission request + Draft Record filed.

**Forbidden at this stage:** Approval, Application, Foundation Version advancement.

### §4.4 Stage 3 — Under Review

**Purpose:** Execute the Release Quality Gate (per `quality-gate-standard.md` §9) against the Release's Contents, Manifest, and Authorizing FD(s).

**Subject state:** `Submitted` → `Under Review`.

**Inputs:**
1. The Release Submission Record.
2. The Release Manifest.
3. The Authorizing FD(s).
4. The Release's proposed Contents (Constitution, Standards, Policies, FDs, RFCs, ADRs, Engine Specs, SDK Specs, Plugin Specs, Workspace Specs, Foundation Packs).

**Outputs:**
1. A `Release Quality Gate Report` (per `quality-gate-standard.md` §9) declaring per-Content outcomes against the six Gates and the Release Quality Gate.
2. Findings — observations, defects, near-misses.
3. Gate Verdict — `PASS`, `PASS with Notes`, `FAIL`, or `BLOCKED` (per `quality-gate-standard.md` §5.4).

**Transition condition:** Gate Verdict `PASS` advances to `Approved`; `PASS with Notes` advances to `Approved` with recorded observations; `FAIL` returns to `Draft`; `BLOCKED` halts the Lifecycle pending Escalation.

**Forbidden at this stage:** Approval before Gate Verdict recorded.

### §4.5 Stage 4 — Approved

**Purpose:** Ratify the Release by the Release Manager, recording the Authorizing FD and the Gate Verdict.

**Subject state:** `Under Review` → `Approved`.

**Inputs:**
1. The Release Quality Gate Report.
2. The Release Submission Record.
3. A signed Approval disposition by the Release Manager.

**Outputs:**
1. A `Release Approval Record` (`RELEASE-<scope>-<slug>-approval.md`) recording the Approval timestamp, the Gate Verdict, the Authorizing FD(s), and the Release Manager.
2. The Release is registered as `Approved` — it is now eligible to advance the Foundation Version.

**Transition condition:** Signed Approval disposition + `PASS` or `PASS with Notes` Gate Verdict.

**Forbidden at this stage:** Application before Foundation Version advancement is authorized.

### §4.6 Stage 5 — Applied

**Purpose:** Advance the Foundation Version recorded in `FOUNDATION/VERSION` to the Release's `Foundation-Version-New` and commit the Release to Foundation Storage.

**Subject state:** `Approved` → `Applied`.

**Inputs:**
1. The Release Approval Record.
2. The Authorizing FD(s).
3. The Release Manifest.

**Outputs:**
1. A `Release Application Record` (`RELEASE-<scope>-<slug>-application.md`) recording the application timestamp, the Foundation Version transition, and the Release Manager.
2. `FOUNDATION/VERSION` is updated atomically to `Foundation-Version-New`.
3. The Release's Contents are committed to Foundation Storage at the declared paths.

**Transition condition:** Signed Application disposition + atomic Foundation Version update + Manifest committed.

**Forbidden at this stage:** Supersession before Application is recorded.

**Note:** Application is **non-destructive of prior Releases** — a prior Applied Release's records are retained per `governance-model.md` §8 (Immutability) and `directory-standard.md` §4 (artifact retention).

### §4.7 Stage 6 — Superseded

**Purpose:** Mark the Release as superseded by a later Release. Supersession is automatic upon Application of a later Release that declares this Release in its `Supersedes:` field.

**Subject state:** `Applied` → `Superseded`.

**Inputs:**
1. A later Release's Application Record.
2. The later Release's `Supersedes:` field naming this Release.

**Outputs:**
1. The superseded Release's `Superseded-By:` Metadata field is populated with the later Release's ID.
2. The superseded Release's Status is updated to `Superseded` (header-only edit; content untouched per `governance-model.md` §8).

**Transition condition:** Later Release's Application Record references this Release in `Supersedes:`.

**Note:** Supersession is **non-destructive** — the superseded Release's records are retained.

### §4.8 Stage 7 — Withdrawn

**Purpose:** Cancel a Release before it reaches `Applied`. Withdrawal is permitted only at Draft, Submitted, Under Review, or Approved stages.

**Subject state:** `Draft / Submitted / Under Review / Approved` → `Withdrawn`.

**Inputs:**
1. A signed Withdrawal request — by the Release Manager, the human Architect, or by an FD.
2. Reason code — `Quality Gate Failure`, `Authorizing FD Withdrawn`, `Scope Change`, `Conflict Resolution`, `Operator Request`.

**Outputs:**
1. A `Release Withdrawal Record` (`RELEASE-<scope>-<slug>-withdrawal.md`) recording the reason, timestamp, and actor.
2. The Release's Status is updated to `Withdrawn`.

**Transition condition:** Withdrawal Request signed + Reason Code populated.

**Note:** Withdrawal is **non-destructive of audit trail** — Withdrawal preserves evidence; it cancels the Release.

### §4.9 Stage Transition Table

| From | To | Trigger | Required Verdict |
|---|---|---|---|
| (none) | `Undrafted` | Draft initiation | n/a |
| `Undrafted` | `Draft` | Draft Record filed | Structure Gate `PASS`; Isolation Gate `PASS` |
| `Draft` | `Submitted` | Submission signed | Release Manager signature |
| `Submitted` | `Under Review` | Quality Gate initiated | Gate evaluation commenced |
| `Under Review` | `Approved` | Approval signed | Gate Verdict `PASS` or `PASS with Notes` + Release Manager signature |
| `Approved` | `Applied` | Application signed | Atomic Foundation Version update + Manifest committed |
| `Applied` | `Superseded` | Later Release applied | Later Release's `Supersedes:` field names this Release |
| `Draft / Submitted / Under Review / Approved` | `Withdrawn` | Withdrawal signed | Reason Code populated |

### §4.10 Lifecycle Hooks Summary

| Hook | Stage | Required Artifact |
|---|---|---|
| `Release-Draft-Hook` | 1 | Draft Record |
| `Release-Submission-Hook` | 2 | Submission Record |
| `Release-Review-Hook` | 3 | Quality Gate Report |
| `Release-Approval-Hook` | 4 | Approval Record |
| `Release-Application-Hook` | 5 | Application Record |
| `Release-Supersession-Hook` | 6 | (Superseded-By field populated) |
| `Release-Withdrawal-Hook` | 7 | Withdrawal Record |

A Release instance whose corresponding `*-Hook` is missing is **Invalid** at the relevant stage.

---

## §5. Release Interface Specification

### §5.1 Input Contract

A Release SHALL accept the following **Input Contract**:

1. **Release identity** — Release ID, Release name, Release version, Release type (`dev` / `alpha` / `beta` / `rc` / `ga`), Release vendor (per §5.3).
2. **Release Contents** — the declared list of Foundation artifacts the Release aggregates (per §6 and `schema-standard.md` §8, §12).
3. **Release Manifest** — the Manifest enumerating every artifact in the Release (per `schema-standard.md` §8 and §12).
4. **Authorizing FD(s)** — the FD(s) that authorize the Release (per `foundation-decision-policy.md`).
5. **Foundation Version transition** — the `Foundation-Version` (before) and `Foundation-Version-New` (after) the Release declares.
6. **Release Manager** — the role assigned per `roles-and-authority.md`.
7. **Constitution Version** and **Foundation Version** at the time of Submission.

The Foundation SHALL reject any Release Input that does not satisfy the Input Contract. The Release SHALL reject any Input that does not arrive through the Release Quality Gate.

### §5.2 Output Contract

A Release SHALL emit the following **Output Contract**:

1. **Release result** — the result of Release Application (`Applied`, `Withdrawn`, `Superseded`). The result type is declared in the Release's Manifest (per `schema-standard.md` §8, §12).
2. **Release Audit hook** (per `schema-standard.md` §9 and `runtime-specification.md` §7.3) — a structured record of every Release transition, declaring:
   - **Release-ID** and **Release-Version**.
   - **Operation** — the Release Lifecycle stage transition.
   - **FD-Invoked** — the Authorizing FD exercised.
   - **Manifest-Digest** — a stable digest of the Manifest (no Manifest content is recorded unless the operation explicitly declares it).
   - **Foundation-Version-Transition** — the `Foundation-Version` (before) and `Foundation-Version-New` (after).
   - **Boundary-Clauses-Crossed** — the set of Boundary Rules (§3.2) exercised.
   - **Outcome** — `Success`, `No-Op`, `Error`, `Permission-Denied`, `Boundary-Violation`.
   - **Timestamp** — ISO-8601.
   - **Actor** — the Release Manager.
3. **Release Manifest** — the Release's Manifest entry per `schema-standard.md` §8 and §12 (re-emitted on every transition).
4. **Release Status** — the current Lifecycle stage (per §4) emitted on every transition.

The Foundation SHALL accept Audit hooks in the Output Contract form; an Audit hook missing any of the above fields is **Invalid** and triggers a Boundary Violation (§3).

### §5.3 Metadata

The Release's Metadata is the persistent descriptive payload that travels with the Release instance. Required fields:

| Field | Required | Type | Description |
|---|---|---|---|
| `Release-ID` | R | string | Unique identifier; pattern `RELEASE-<scope>-<slug>` |
| `Release-Name` | R | string | Human-readable name |
| `Release-Version` | R | SemVer | The version declared by this Release (per Constitution §8) |
| `Release-Type` | R | enum:`dev`,`alpha`,`beta`,`rc`,`ga` | The Release type (per Constitution §8 and §9 below) |
| `Release-Vendor` | R | string | Author/vendor identifier |
| `Release-Description` | R | string | One-paragraph human-readable description |
| `Release-Contents` | R | list:ref | The Foundation artifacts aggregated by this Release (per §6) |
| `Release-Manifest` | R | ref:`Manifest-ID` | The Manifest enumerating the Release's Contents (per §6) |
| `Release-Authorizing-FDs` | R | list:ref:`FD-NNNN` | The FD(s) authorizing the Release |
| `Foundation-Version` | R | SemVer | The Foundation Version *before* this Release is applied |
| `Foundation-Version-New` | R | SemVer | The Foundation Version *after* this Release is applied |
| `Constitution-Version` | R | SemVer | The Constitution Version at Submission time |
| `Release-Manager` | R | role | The Release Manager role (per `roles-and-authority.md`) |
| `Release-Date` | C | date (ISO-8601) | Required when Status is `Approved` or `Applied` |
| `Release-Supersedes` | O | ref:`Release-ID` | Previous Release ID (if superseding) |
| `Release-Superseded-By` | C | ref:`Release-ID` | Set when superseded |
| `Release-Compatibility-Profile` | R | Compatibility | Per §8 |

### §5.4 Versioning

- **Version surface:** `Release-Version`, `Foundation-Version`, `Foundation-Version-New`, `Constitution-Version`, `Release-Type`.
- **Bump triggers:**
  - **MAJOR** — non-backward-compatible Foundation change; Constitution amendment; new L5 component class.
  - **MINOR** — additive new Foundation component; new Standard; new Foundation Pack; backward-compatible.
  - **PATCH** — typo fix, clarification, re-bind to a newer Foundation minor without structural changes.
- **Pre-release tags:** `0.1.0-dev`, `0.1.0-rc.1`, `1.0.0-rc.1`, `1.0.0` (reserved for Release types per §9 and `schema-standard.md` §12).
- **Foundation binding:** A Release SHALL NOT declare a `Foundation-Version-New` that is older than `Foundation-Version`.
- **Foundation Phase binding (this cycle):** Per §9 and Constitution §15.3, the current Foundation Version is `0.1.0-dev`; a Release of type `rc` or `ga` is **forbidden** during the Foundation phase until an Authorizing FD declares the Foundation ready for RC.

### §5.5 Compatibility

A Release's Compatibility Profile declares Compatibility with:

- **Foundation versions** — the Release's `Foundation-Version-New` is its declared compatibility floor; compatible with `>= Foundation-Version-New` and `< next-Foundation-Major`.
- **Constitution versions** — the Release SHALL NOT invoke clauses past its `Constitution-Version`.
- **Plugin-SDK versions** — the Release SHALL aggregate Plugin-SDK versions consistent with the aggregated Plugin Specifications.
- **Host platform versions** — the Release declares the range of host platform versions it supports (technology-neutral).
- **Downstream consumer versions** — the Release SHALL declare the range of downstream consumer versions that may consume this Release.

---

## §6. Release Composition Model

### §6.1 MUST Contain

A Release MUST contain:

1. **The Constitution** at the `Constitution-Version` declared in the Release's Metadata (per `schema-standard.md` §12).
2. **Every Foundation Standard** declared in `FOUNDATION/03-Standards/README.md` as of the Release's `Foundation-Version-New`, at the Version declared in the Release's Manifest.
3. **Every Foundation Policy** declared in `FOUNDATION/02-Governance/` as of the Release's `Foundation-Version-New`, at the Version declared in the Release's Manifest.
4. **Every active Foundation Decision (FD)** at the time of the Release's Submission.
5. **Every Accepted Foundation RFC (FRFC)** at the time of the Release's Submission.
6. **Every Accepted Release RFC (RRFC)** at the time of the Release's Submission.
7. **Every Accepted Foundation ADR** at the time of the Release's Submission.
8. **The Release Manifest** enumerating every artifact in the Release (per `schema-standard.md` §8, §12).
9. **The Authorizing FD(s)** (per `foundation-decision-policy.md`).
10. **The Release Quality Gate Report** (per `quality-gate-standard.md` §9).

### §6.2 MAY Contain

A Release MAY contain:

1. **Foundation Packs** (`pack-standard.md`) that have passed the Release Quality Gate.
2. **Concrete Engine instances** (post-Foundation, declared by future Engine Specifications).
3. **Concrete SDK instances** (post-Foundation, declared by future SDK Specifications).
4. **Concrete Plugin instances** (post-Foundation, declared by future Plugin Specifications).
5. **Concrete Workspace instances** (post-Foundation, declared by future Workspace Specifications).
6. **Test Suites** declared by the Release Quality Gate.
7. **Tooling specifications** declared by future Tooling Standards.

### §6.3 SHALL NOT Contain

A Release SHALL NOT contain:

1. **Source code** that implements Foundation components (the Foundation is normative, not executable during the Foundation phase).
2. **Credentials**, tokens, or secrets.
3. **Project-specific artifacts** during the Foundation phase.
4. **Workspace templates** that instantiate Workspaces.
5. **Pack instances** that execute Missions / Programs / Tasks / Deliverables.
6. **Network endpoints** in normative clauses.
7. **Sandbox configurations** (no Dockerfile, no firecracker config, no gVisor config).
8. **Git operation directives** beyond the Release Manifest's declared Git references.

### §6.4 Composition Coherence

A Release's Contents MUST be **coherent**:

- Every Standard referenced in the Release's Manifest MUST be at a Version compatible with `Foundation-Version-New`.
- Every FD referenced in the Release's Manifest MUST be at a Status of `Approved` or `Superseded`.
- Every RFC and ADR referenced MUST be at a Status of `Accepted`.
- Every Foundation Pack included MUST have passed the Release Quality Gate.
- No two artifacts in the Release may declare conflicting clauses; conflict resolution follows `governance-model.md` §4.

A Release whose Contents fail coherence check SHALL be returned to `Draft` (§4.2) with a recorded failure finding.

---

## §7. Release Versioning and Approval Model

### §7.1 SemVer Discipline

The Foundation Version recorded in `FOUNDATION/VERSION` follows SemVer discipline (per Constitution §8):

- **MAJOR** — non-backward-compatible Foundation change; Constitution amendment; new L5 component class.
- **MINOR** — additive new Foundation component; new Standard; new Foundation Pack; backward-compatible.
- **PATCH** — typo fix, clarification, re-bind to a newer Foundation minor without structural changes.

### §7.2 Authorizing FD

Every Release MUST be authorized by one or more FDs issued per `foundation-decision-policy.md`. The Authorizing FD(s) MUST:

1. Declare the Release's `Foundation-Version-New` as a valid SemVer bump from the prior `Foundation-Version`.
2. List every artifact the Release aggregates.
3. Be at a Status of `Approved` or `Superseded`.
4. Be recorded in the Release's Manifest.

A Release without an Authorizing FD SHALL NOT transition from `Approved` to `Applied` (§4.6).

### §7.3 Release Manager Disposition

The Release Manager (per `roles-and-authority.md`) MUST sign every Release transition (§4). The Release Manager MAY delegate per `roles-and-authority.md` §5 but SHALL NOT delegate Approval of a Release of type `rc` or `ga`.

### §7.4 Foundation Version Advancement

Foundation Version advancement occurs **only** at the `Applied` stage (§4.6). The advancement is **atomic**: `FOUNDATION/VERSION` is updated to `Foundation-Version-New` in a single committed operation that includes the Release Manifest. A partial advancement is a **Boundary Violation**.

The Foundation Version MAY be advanced **only** if:

1. The Release has reached `Approved` (§4.5).
2. The Authorizing FD(s) are at `Approved` or `Superseded`.
3. The Release Quality Gate has returned `PASS` or `PASS with Notes`.
4. The Release Manager has signed the Application.
5. No Conflict Resolution is pending (`governance-model.md` §4).

### §7.5 Release Quality Gate

The Release MUST pass the Release Quality Gate (per `quality-gate-standard.md` §9) before advancing to `Approved`. The Gate evaluates:

1. **Manifest Coherence** — every declared artifact is present and at the declared Version.
2. **FD Authorization** — every Authorizing FD is valid and at `Approved` or `Superseded`.
3. **Standard Compliance** — every aggregated Standard passes its own Quality Gate (Structure, Consistency, Cross Reference, Isolation, Scope Compliance, Security Boundary).
4. **Composition Coherence** — per §6.4.
5. **Boundary Compliance** — per §3.
6. **Release-Type Compliance** — the Release's declared `Release-Type` is consistent with the Foundation's current Lifecycle stage (per §9).

### §7.6 Human Approval Boundary

The Human Approval Boundary is enforced at:

1. **Submission (§4.3)** — Release Manager signs the Submission.
2. **Approval (§4.5)** — Release Manager signs the Approval disposition.
3. **Application (§4.6)** — Release Manager signs the Application disposition.
4. **Withdrawal (§4.8)** — Release Manager, human Architect, or FD signs the Withdrawal.

No machine, automation, or CI/CD pipeline may substitute for the human Release Manager at any boundary (per Constitution §5 and `quality-gate-standard.md` §7.4).

---

## §8. Release Compatibility

### §8.1 Version Compatibility

A Release declares its Compatibility Profile (§5.3). Compatibility is enforced as:

- **Foundation-version compatibility.** A Release with `Foundation-Version-New = X.Y.Z` is compatible with Foundation versions `>= X.Y.Z` and `< next-Foundation-Major`.
- **Constitution-version compatibility.** A Release SHALL NOT invoke clauses past its `Constitution-Version`.
- **Plugin-SDK-version compatibility.** A Release SHALL aggregate Plugin-SDK versions consistent with the aggregated Plugin Specifications.
- **Host-version compatibility.** A Release SHALL declare the host platform version range it supports.
- **Downstream-consumer compatibility.** A Release SHALL declare the range of downstream consumer versions that may consume it.

### §8.2 Migration Rules

When a Release's compatibility breaks (e.g., a new Foundation Major version, a new Constitution amendment, or a host platform breaking change), a **Release Migration Plan** is required. The Plan declares:

1. The previous Release Version and the new Release Version.
2. The list of breaking changes (with locator and rationale).
3. The list of downstream consumers affected.
4. The Migration procedure (per-consumer re-validation, per-Standard re-grant, per-Release re-Approval).
5. The expected Migration timeline.

The Plan is filed at a path recorded in `directory-standard.md` §4 (place-holder: `<release-root>/MIGRATION-<release-id>-<from>-<to>.md`). The Plan is reviewed per `change-control-policy.md` and requires the same Reviewer separation-of-duties rule.

### §8.3 Extension Rules

Per Constitution §13 (Future Extension Policy), Release extensions are **additive-only**:

- **New artifact classes** — additive (a new artifact class may be added to §6.1 by a new Release MAJOR version, because it is a Protocol change).
- **New Release types** — additive (a new Release type may be added to §5.3 by a new Release MAJOR version).
- **New Lifecycle stages** — additive (a new stage may be inserted in §4 by a new Release MAJOR version, because it is a Protocol change).
- **New Foundation components** — additive (a new L5 component class may be added by a new Release MAJOR version).

**Weakening requires a new FD:**

- Removing an artifact class from §6.1 (MUST Contain).
- Lowering the Release Quality Gate (relaxing §7.5).
- Changing the Lifecycle to remove a stage.
- Re-classifying a default-denied Composition rule as default-allowed.
- Re-classifying `rc` or `ga` Release types as permitted during the Foundation phase (without explicit FD).

### §8.4 Release Supersession

A Release MAY be superseded by a later Release. The supersession follows the rules in `governance-model.md` §9:

1. The new Release declares `Supersedes: <old-Release-ID>` in its Metadata (§5.3).
2. The old Release's Status is updated to `Superseded` (header-only edit; content untouched).
3. The old Release's `Superseded-By` Metadata field is populated with the new Release's ID.
4. The Foundation Version transition is recorded in both Releases' Audit hooks.

A Superseded Release SHALL NOT be re-Applied except via a new Submission cycle (§4.2).

---

## §9. Foundation Phase Constraints

### §9.1 The Five Constraints

Per the Foundation Invariant (per memory `foundation-invariant-2026-08-03.md`), until Task 12 ratification is invoked, the Foundation preserves the following five constraints:

1. **Foundation Version remains `0.1.0-dev`** — no version bump to `0.1.0-rc.1`, `1.0.0-rc.1`, or `1.0.0`.
2. **Constitution remains `v0.1.0-draft` Provisional** — no Constitution amendment; no change to the Provisional label.
3. **No RC Release** — no Release of type `rc` is declared during the Foundation phase.
4. **No Pack instantiated** — no `PACK-*.md` file is created; no Pack execution.
5. **No Project instantiated** — no Project-specific artifact is created; APES remains a paused Project.

The Release Specification does **not** violate any of these constraints. The Specification is **declared** during Task 12; the **first Release** is a future deliverable, contingent on a separate Foundation cycle.

### §9.2 Prohibition on `rc` and `ga` Release Types

During the Foundation phase:

- A Release of type `rc` is **forbidden** (per Constitution §15.3 Hard Prohibitions).
- A Release of type `ga` is **forbidden**.
- A Release of type `dev` is the **only** Release type permitted during the Foundation phase.

The first `rc` Release may be declared **only** when:

1. The Constitution has reached a Human-Architect-ratified state explicitly
   authorizing first-RC declaration, as recorded by a separate Authorizing FD
   that names the Constitution ratification state and the scope of first-RC
   authorization.
2. Every Foundation Standard has been either (a) ratified via an Authorizing FD,
   or (b) bound to an exact version by an aggregated-approval FD whose binding
   scope has been ratified by a Human Architect and has not been contested by
   any active FD or normative artifact.
3. The Foundation Invariant is **explicitly released** by an Authorizing FD.

Until those three conditions are met, no Release may declare `rc` or `ga`.

### §9.3 No v1.0.0 Release

A Release declaring `Foundation-Version-New = 1.0.0` is **forbidden** during the Foundation phase. The first Release of type `ga` declaring `1.0.0` MAY be declared **only** when the Foundation Invariant is released per §9.2.

### §9.4 No GitHub Release

A Release SHALL NOT issue a GitHub Release (or any other public-versioning-system Release) during the Foundation phase. The Release exists as an on-disk Foundation artifact at a path declared in `directory-standard.md` §4 (place-holder: `FOUNDATION/16-Releases/` — reserved, not instantiated during Foundation phase).

### §9.5 No Pack, Runtime, Engine, SDK, Plugin, Workspace, Project

A Release SHALL NOT instantiate any Foundation component during the Foundation phase:

- No Pack instance (no `PACK-*.md`).
- No Runtime instance (no Runtime source code, no Runtime cycle invocation).
- No Engine instance (no Engine source code, no Engine invocation).
- No SDK instance (no SDK source code, no SDK instantiation).
- No Plugin instance (no Plugin source code, no Plugin activation).
- No Workspace instance (no `WORKSPACE-*.md`, no on-disk Workspace directory tree).
- No Project instance (no APES artifact, no Project-specific governance).

A Release whose Contents violate any of these prohibitions SHALL fail the Release Quality Gate (§7.5) with `FAIL` verdict.

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
- §17 (Provisional Governance)

### §10.2 Standard References

- `directory-standard.md` §4 (top-level layout), §6 (per-class storage paths), §8 (reserved directories), §10 (path-validation).
- `schema-standard.md` §8 (Manifest), §9 (Audit), §12 (Release Schema) — primary references for the Release schema.
- `pack-standard.md` §3 (Pack Definition), §4 (Pack Lifecycle), §6 (Manifest rules), §11–§13 (Audit/Review/Report hooks), §16 (Versioning), §21 (Release hooks).
- `runtime-specification.md` §4 (Runtime Architecture), §5 (Runtime Lifecycle), §7 (Runtime Output Specification), §10 (Runtime Security Boundary), §11 (Runtime Compatibility).
- `quality-gate-standard.md` §5 (Quality Gate Types), §6 (Audit Relationship), §7 (Review Relationship), §8 (Failure Handling), §9 (Release Quality Gate), §10 (Compatibility).
- `engine-specification.md` §3–§11.
- `sdk-specification.md` §7 (Plugin SDK), §8 (Shared SDK Architecture).
- `plugin-specification.md` §3 (Plugin Boundary Model), §4 (Plugin Lifecycle), §6 (Permission Model), §7 (Security Model), §8 (Platform Plugin Specifications).
- `workspace-specification.md` §2 (Workspace Architecture Purpose), §3 (Workspace Boundary Model), §4 (Workspace Lifecycle), §6 (Permission and Security Model), §7 (Workspace Types), §8 (Workspace Compatibility).

### §10.3 Policy References

- `governance-model.md` §2 (Hierarchy), §3 (Role Model), §4 (Conflict Resolution), §6 (Artifact Types), §7 (Status Lifecycle), §8 (Immutability), §9 (Supersession), §13 (Additive-only extensions).
- `approval-workflow.md`.
- `change-control-policy.md`.
- `disagreement-and-escalation.md`.
- `roles-and-authority.md`.
- `rfc-policy.md`.
- `foundation-decision-policy.md`.
- `adr-policy.md`.

### §10.4 Back-References

This Standard is referenced by:

- *Future Releases.* Concrete Release instances (post-Foundation) SHALL reference this Standard and SHALL pass the Release Quality Gate per `quality-gate-standard.md` §9.
- *Future Foundation Decisions (FDs).* An FD that authorizes a Release SHALL reference this Standard's §7.2 (Authorizing FD) and §7.5 (Release Quality Gate).
- *Future Foundation Packs.* A Foundation Pack that bundles Foundation Standards SHALL reference this Standard (per `pack-standard.md` §21).
- *Future Plugin instances.* Plugin instances bundled by a Release SHALL reference this Standard and the Plugin Specification.
- *Future Workspace instances.* Workspace instances bundled by a Release SHALL reference this Standard and the Workspace Specification.
- *Future Project Workspaces.* Project Workspaces that consume a Release SHALL reference this Standard.

---

## §11. Relationship to Other Artifacts

### §11.1 To the Constitution

This Standard operationalizes the Release concept for the Foundation, drawing on Constitution §§1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17. It does not contradict any clause of the Constitution. If a future Constitution amendment changes a referenced §, this Standard must be updated to reflect the new clause (per `change-control-policy.md`).

### §11.2 To Other Foundation Standards

- **Directory Standard** — declares the storage paths for Standards, Audits, Reports, Reviews, and (post-Foundation) Releases produced by this Standard. §8 reserves `FOUNDATION/16-Releases/` for Releases.
- **Schema Standard** — declares the Manifest (§8), Audit (§9), and Release (§12) schemas that this Standard references.
- **Pack Standard** — declares the Builder Pack that a Release MAY bundle.
- **Runtime Specification** — declares the Runtime that mediates Release Quality Gate execution.
- **Quality Gate Standard** — declares the six Gates and the Release Quality Gate (§9) that gate every Release.
- **Engine Specification** — declares the Engines (Builder, Audit, Evidence, Statistics, Report, Prompt) invoked during a Release.
- **SDK Specification** — declares the SDKs (Project, Builder, Migration, Release, Plugin) that a Release aggregates.
- **Plugin Specification** — declares the Plugin boundary that Releases honor when bundling Plugin instances.
- **Workspace Specification** — declares the Workspace that a Release MAY bundle.

### §11.3 To Future Artifacts

Future artifacts that may reference this Standard include:

- **First Foundation Release** (post-Foundation, contingent on Foundation Invariant release) — a concrete Release instance (e.g., `RELEASE-foundation-v1.0.0.md`) that bundles the Foundation Standards and authorizes the Foundation Version transition.
- **Release-authorizing FDs** (post-Foundation) — FDs that authorize the first Foundation Release.
- **Foundation Packs** (post-Foundation) — Packs that bundle Foundation Standards.
- **Project Workspace instances** (post-Foundation) — Workspaces that consume a Foundation Release.

### §11.4 Release as Project-Independent Component

This Standard is **technology-neutral** and **project-independent**. No Release defined here is owned by any Project; no Release is restricted to any Project; no Project-local rule binds a Release during the Foundation phase. APES (the first Project) MAY consume a Foundation-defined Release post-Foundation, but no Foundation-defined Release is APES-specific.

During the Foundation phase, no Release is instantiated. The Release Specification declares the contract; the first Release instance is a future deliverable, contingent on a separate Foundation cycle and explicit Foundation Invariant release.

---

## §12. Ratification

This Standard is **Draft / In Review** at version `0.2.0-draft`. Its formal ratification is **deferred and conditional** — no `FD-0012-ratify-release-specification.md` is created in this Foundation task.

**Ratification path (when invoked by a future Foundation cycle):**

1. The human Architect reviews this Standard and the accompanying Audit, Report, and Review.
2. The Architect issues a Review Record disposition (`Approved`, `Approved with Notes`, `Rejected`, `Blocked`).
3. On `Approved`, a future task creates `FOUNDATION/09-Decisions/FD-0012-ratify-release-specification.md` per `foundation-decision-policy.md`.
4. The FD transitions this Standard from `Draft / In Review` to `Ratified`.
5. After Ratification, this Standard's `Status:` header field is updated to `Ratified` and its `Version:` may advance per §5.4.

Until `FD-0012` is created (if ever), this Standard remains Draft / In Review and is **non-normative**. Foundation work proceeds per Constitution §17.4 (Provisional governance on a best-effort basis).

> **Note.** No `FD-0012-ratify-release-specification.md` is created during Task 12. The existence of such an FD is **deferred** and **conditional**; it is not an automatic next action. The Foundation Builder prepares this Standard and the companion Audit / Report / Review; the human Architect reviews it through `REVIEW-FOUNDATION-12-release.md`.

> **Note.** This Standard is **technology-neutral**, **project-independent**, and **implementation-independent**. It contains no Release source code, no Release Manifest, no `FOUNDATION/16-Releases/` directory, no Release Quality Gate invocation, no Foundation Version advancement, no Authorizing FD, no Pack execution, no Runtime instantiation, no Engine instantiation, no SDK instantiation, no Plugin instantiation, no Workspace instantiation, no Mission execution, no Task execution, no Deliverable production, no network endpoint, no credential capture, no sandbox implementation, no git operation, and no APES artifact. The Release types `rc` and `ga` are **forbidden** during the Foundation phase per §9 and Constitution §15.3.

> **Note.** Per the Foundation invariant (per memory `foundation-invariant-2026-08-03.md`), until Task 12 ratification is invoked the Foundation preserves five constraints: Foundation Version `0.1.0-dev`; Constitution `v0.1.0-draft` Provisional; no RC; no Pack; no Project. The Release Specification does not violate any of these constraints. **Releasing** the Foundation Invariant is the responsibility of a future Foundation cycle that issues an Authorizing FD; this Standard declares the **contract** for that future release, not the release itself.

> **Note.** This is the **twelfth and final Foundation Task** in the 12-Task Foundation sequence. The Builder has authored Standards 03 (Directory), 04 (Schema), 05 (Pack), 06 (Runtime), 07 (Quality Gate), 08 (Engine), 09 (SDK), 10 (Plugin), 11 (Workspace), and 12 (Release). All ten Standards are Draft / In Review. The Builder has not issued any FD. The Builder has not advanced the Foundation Version. The Builder awaits the Architect's review.

### §12.1 Controlled Repair Change Log

| Version | Date | Authority | Change |
|---|---|---|---|
| `0.2.0-draft` | 2026-08-04 | FRFC-0002 (Approved with Notes) + FD-0005 (Ratified) | Replaced §9.2 conditions 1 and 2 with the exact approved first-RC prerequisite semantics; preserved condition 3 and all surrounding prohibitions; advanced only the Standard version. |

---

*End of release-specification.md v0.2.0-draft (Draft / In Review).*
