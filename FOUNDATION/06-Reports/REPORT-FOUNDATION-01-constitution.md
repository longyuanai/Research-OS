# Task 01 Report — Constitution (incl. Task 01.1 Correction)

**Task:** 01 — Constitution
**Correction Cycle:** Task 01.1 — Constitution Versioning and Scope Correction
**Cycle:** Foundation v0.1.0-dev, Cycle 01
**Date:** 2026-08-03
**Builder:** Foundation Builder
**Status:** Approved

---

## 1. Summary

Task 01 produced a Provisional Constitution (`v0.1.0-draft`) as the supreme governance document for the Research-OS Foundation. The initial cycle applied v1.0.0-rc.1 semantics in error. Task 01.1 (this correction cycle) corrected the version, status, lifecycle, scope-control, and activation semantics. The Constitution now:

- Is marked **`Status: Provisional`** with version **`0.1.0-draft`**.
- Reflects the Foundation platform at **`0.1.0-dev`** (see `FOUNDATION/VERSION`).
- Cannot be formally ratified until **Task 02** instantiates the FD infrastructure; only then may `FD-0001` ratify it.
- Explicitly forbids claiming Foundation `v1.0.0-rc.1` or `v1.0.0` before **Task 12** passes review.
- Adds **§15.5 Per-Task Scope Declaration** requiring every Foundation Task (and correction cycle) to declare allowed/forbidden files, inputs, outputs, dependencies, quality gates, and stop condition.
- Rewrites **§11.4 Isolation** as a **semantic** project-independence rule (no APES-specific governance, lifecycle, schema, or implementation content), replacing the prior mention-count heuristic.

The Foundation remains **pre-RC**. No part of the platform may be described as having reached `v1.0.0-rc.1`.

---

## 2. Files Modified

| Path | Change (Task 01 cycle 1) | Change (Task 01.1 — this cycle) |
|---|---|---|
| `FOUNDATION/01-Constitution/constitution.md` | rewritten v0.2 → v1.0.0-rc.1 | corrected header (`Status: Provisional`, `Version: 0.1.0-draft`); corrected §2.1, §8.2, §8.3, §11.4, §14, §15 (added §15.5), §17 (non-circular ratification sequence) |
| `FOUNDATION/VERSION` | created `1.0.0-rc.1` | **corrected** to `0.1.0-dev` |
| `FOUNDATION/README.md` | updated status block | **corrected** Foundation Version section, Current Status block |
| `CHANGELOG.md` | prepended v1.0.0-rc.1 entry | **rewritten** to remove RC implication; new `v0.1.0-draft` entry added |
| `FOUNDATION/04-Audits/AUDIT-FOUNDATION-01-constitution.md` | created | **rewritten** to audit v0.1.0-draft and Task 01.1 corrections |
| `FOUNDATION/06-Reports/REPORT-FOUNDATION-01-constitution.md` | created | **rewritten** (this document) |
| `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-01-constitution.md` | created | **rewritten** below |

No file outside this allowed list was created or modified during Task 01.1. **No new directories** were created. **No Governance, FD, RFC, or Standard artifact was created.** **No Task 02 work has begun.**

---

## 3. Version Corrections

| Surface | Before (Task 01) | After (Task 01.1) |
|---|---|---|
| Constitution `Version` | `1.0.0-rc.1` | `0.1.0-draft` |
| Constitution `Status` | `draft (v1.0 RC — pending FD activation)` | `Provisional` |
| Foundation version (`FOUNDATION/VERSION`) | `1.0.0-rc.1` | `0.1.0-dev` |
| §2.1 (Version Surfaces) | listed `1.0.0-rc.1` | now lists `0.1.0-dev` / `0.1.0-draft` / unset |
| §8.2 (Pre-release Tags) | listed `1.0.0-rc.1` as a typical example | clarifies `1.0.0-rc.1` is reserved for Task 12 release |
| §8.3 (First-Release Rule) | "first release is `0.1.0`" | clarified: first version is `0.1.0-draft`; `1.0.0` requires all Tasks active and Task 12 review passed |
| §14.2 (Current Target) | implied Foundation RC was the immediate target without restricting declaration | now states: "no Foundation version, including the Constitution, may be described as having reached RC before Task 12 passes" |
| §15.3 (Hard Prohibitions) | omitted RC-declaration guard | added: "Declaring any Foundation version as having reached `1.0.0-rc.1` or `1.0.0` before Task 12 passes" is forbidden |
| §17.3 (Activation) | single-paragraph "FD-0001 records Architect's signature" (slightly circular) | replaced by **non-circular ratification sequence**: Task 01 → Task 02 → FD-0001 |
| §17.4 (Effective Date) | "upon activation" | "Upon ratification; until ratification, governs provisionally" |
| Footer | `End of Constitution v1.0.0-rc.1 (draft)` | `End of Constitution v0.1.0-draft (Provisional)` |
| CHANGELOG header | `[Unreleased] / Foundation v1.0.0-rc.1 (Draft)` | `[Unreleased] / Foundation v0.1.0-dev (Provisional, under development)` |
| CHANGELOG new entry | `[Constitution v1.0.0-rc.1] — 2026-08-03` | `[Constitution v0.1.0-draft] — 2026-08-03` |
| README Foundation Version | `1.0.0-rc.1` | `0.1.0-dev` + pre-RC note |
| README Current Status | "Foundation v1.0 RC: declared at Task 01" | "Foundation v1.0 RC: **not yet declared.** Task 12 is the only Foundation RC gate." |

---

## 4. Activation Corrections

**Before (Task 01 cycle 1):** The Constitution said activation happens "upon FD-0001" without explaining how FD-0001 itself comes to exist. This was mildly circular: the FD mechanism (defined in §7) presupposes a ratified Constitution, but ratification is defined to require an FD.

**After (Task 01.1):** §17.3 specifies a strict, non-circular sequence:

1. **Task 01 (this Task)** establishes the Constitution as a Provisional governance draft. It applies on a best-effort basis; nothing is formally binding.
2. **Task 02 (Governance)** establishes the Foundation Decision mechanism — the FD format, the `FOUNDATION/09-Decisions/` directory, and the rules under which FDs are issued. Until Task 02 is complete, no FD can exist.
3. **After Task 02**, an Architect-issued `FD-0001` may ratify this Constitution. Ratification requires the FD to record the Architect's signature and explicitly declare `ratifies-constitution: 0.1.0-draft`.
4. After ratification, prior versions (`v0.1`, `v0.2`) enter the Archived state.
5. Foundation `v1.0.0-rc.1` is declared only by Task 12.

This sequence has no cycle: each step produces the precondition for the next without presupposing its own ratification.

---

## 5. Scope-Control Corrections

**New §15.5 — Per-Task Scope Declaration (Mandatory):**

Every Foundation Task and correction cycle must begin with an explicit declaration of:

1. **Allowed files** — paths the Task may create or modify.
2. **Forbidden files** — paths the Task must not touch (all paths outside the allowed list by default).
3. **Inputs** — artifacts the Task consumes.
4. **Outputs** — artifacts the Task produces.
5. **Dependencies** — earlier Tasks whose completion is required.
6. **Quality gates** — which §11 criteria the Task must satisfy, plus any Task-specific criteria.
7. **Stop condition** — the trigger that ends the Task.

The Builder may not create or modify any file outside the declared allowed-file list. Any expansion requires explicit human approval recorded in the Task Report. A scope violation automatically fails §11.4 (Isolation), regardless of the content of the out-of-scope file.

**Task 01.1 itself satisfied §15.5** by declaring an explicit allowed-file list (the seven files listed above) and touching nothing outside it.

---

## 6. Acceptance Checklist

### 6.1  Versioning

- [x] Constitution `Version` set to `0.1.0-draft`
- [x] Constitution `Status` set to `Provisional`
- [x] `FOUNDATION/VERSION` set to `0.1.0-dev`
- [x] §2.1 reflects pre-RC values
- [x] §8.2 reserves `1.0.0-rc.1` for Task 12
- [x] §8.3 first-release rule gated by Task 12
- [x] CHANGELOG does not claim Foundation v1.0 RC was released
- [x] README does not claim Foundation v1.0 RC was reached
- [x] Header notes status is Provisional, not ratified

### 6.2  Activation

- [x] §17.3 specifies a non-circular ratification sequence
- [x] Task 02 is positioned as prerequisite for FD-0001
- [x] FD-0001 ratification requires explicit `ratifies-constitution: 0.1.0-draft` flag
- [x] Foundation `v1.0.0-rc.1` is gated exclusively by Task 12
- [x] §15.3 Hard Prohibitions extended with RC-declaration guard

### 6.3  Scope Control

- [x] §15.5 Per-Task Scope Declaration added
- [x] §15.5 lists all seven required declaration fields
- [x] §15.5 specifies automatic §11.4 failure on scope violation
- [x] Task 01.1 declared its own scope before editing

### 6.4  Project Independence (APES isolation)

- [x] §11.4 Isolation rewritten as a semantic project-independence rule
- [x] No mention-count rule remains
- [x] APES appears only as examples (not as the source of normative content)
- [x] Constitution remains valid in the complete absence of APES

### 6.5  Allowed-File Compliance

- [x] No file outside the declared allowed-file list was created
- [x] No file outside the declared allowed-file list was modified
- [x] No new directories were created
- [x] No Governance artifact, FD, RFC, Standard, or Engine was produced
- [x] No Task 02 work was begun

### 6.6  Hard Prohibitions (§15.3)

- [x] No Project Sprint begun
- [x] No Gap Analysis or Positioning performed
- [x] No Project Phase C entered
- [x] No Standard beyond what the Constitution defines created
- [x] No Project-specific Standard created
- [x] No Release begun
- [x] No Foundation `1.0.0-rc.1` or `1.0.0` claim made
- [x] No auto-commit / auto-push / auto-branch
- [x] No Scaffold / Engine / Runtime / Plugin / SDK built prematurely
- [x] No Sprint / Project / Project artifact modified

### 6.7  Quality Gate (§11)

- [x] Completeness (§11.1) — all sections + corrected header present
- [x] Compliance (§11.2) — no self-contradiction; no active Standard or FD to violate
- [x] Cross Reference (§11.3) — every applicable reference resolves
- [x] Isolation (§11.4) — semantic project-independence verified

---

## 7. Verification

### 7.1  Structural Verification

- `FOUNDATION/01-Constitution/constitution.md` begins with corrected header: `Status: Provisional`, `Version: 0.1.0-draft`, `Foundation Version: 0.1.0-dev`.
- All §0–§17 sections present; §15.5 added; §11.4 and §17.3 substantively rewritten.
- `FOUNDATION/VERSION` content is `0.1.0-dev`.
- `FOUNDATION/README.md` does not contain `1.0.0-rc.1` as a current Foundation version.
- `CHANGELOG.md` `[Unreleased]` block records the platform as `v0.1.0-dev (Provisional, under development)`.
- No new directories created during Task 01.1.

### 7.2  Semantic Verification

- The ratification sequence in §17.3 has no cycle.
- §11.4's project-independence rule is a property of the Constitution's normative content, not of how often APES is mentioned. Replacing "APES" with "Project X" in every APES example would not change any rule.
- §15.5 is operationalizable: every Task can declare its allowed files; the Audit can check for compliance.

### 7.3  Scope Verification

- Only the seven allowed files have been touched during Task 01.1.
- No Governance, FD, RFC, Standard, Engine, SDK, Plugin, or other Task 02–12 artifact exists.
- No Foundation Decisions directory has been created.

### 7.4  Quality Gate Verification

The Audit (`AUDIT-FOUNDATION-01-constitution.md`, rewritten this cycle) records explicit pass/fail for all four Quality Gate criteria, the Hard Prohibitions check, the §15.5 Scope Declaration check, and the six Task 01.1 correction requirements. All pass.

---

## 8. Remaining Limitations

1. **Constitution is Provisional.** No clause is formally binding. Until `FD-0001` is issued after Task 02, the Constitution governs on a best-effort basis.
2. **No `FD-0001`.** The FD infrastructure does not yet exist. Task 02 must complete before any FD can be issued.
3. **No `FOUNDATION/09-Decisions/` directory.** Reserved; created by Task 02.
4. **No `FOUNDATION/02-Standards/`, `03-Engines/`, `05-Statistics/`, `08-RFCs/` directories.** Reserved; created by Tasks 03–11.
5. **Naming table (§9)** is forward-compatible but a few rows (Builder Pack Manifests, Workspace Templates) are anticipated rather than defined. Tasks 05 and 11 will exercise these.
6. **No git commit.** Per Hard Prohibition §15.3 and §15.4, no commit was created. The Builder leaves commit decisions to the human approver.
7. **§15.5 is new.** No prior Task was executed under this rule. Its operational effects will be observable starting with Task 02.

---

## 9. Git Status

Repository is **not** under git. No commit was made during Task 01.1.

If git were initialized, the diff scope for Task 01.1 would be:

- **modified** — `FOUNDATION/01-Constitution/constitution.md`
- **modified** — `FOUNDATION/VERSION`
- **modified** — `FOUNDATION/README.md`
- **modified** — `CHANGELOG.md`
- **modified** — `FOUNDATION/04-Audits/AUDIT-FOUNDATION-01-constitution.md`
- **modified** — `FOUNDATION/06-Reports/REPORT-FOUNDATION-01-constitution.md`
- **modified** — `FOUNDATION/07-Reviews/REVIEW-FOUNDATION-01-constitution.md`

No new files; no new directories.

---

## 10. Recommended Next Task

**Task 02 — Governance.**

This recommendation is unchanged from the prior Report cycle. Rationale (refreshed):

- Task 02 instantiates the FD infrastructure (`FOUNDATION/09-Decisions/`, FD format operationalization) that **§17.3 of the corrected Constitution** now explicitly identifies as the prerequisite for ratification.
- Without Task 02, no FD can exist, and therefore the Constitution cannot be ratified. Foundation work cannot proceed formally without this step.
- Task 02 is the natural next step in §16's order: Constitution (draft) → Governance framework → Standards.
- The corrected Constitution itself defines the scope, dependencies, quality gates, and stop condition that Task 02 will declare at its start (per the new §15.5 rule).
- No Hard Prohibition (§15.3) blocks Task 02.
- No Governance, FD, RFC, or Standard artifact has been created during Task 01.1.

---

**STOP.** Awaiting human approval before starting Task 02.
