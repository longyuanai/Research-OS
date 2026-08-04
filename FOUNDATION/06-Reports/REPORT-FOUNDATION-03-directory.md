# Task Report — Foundation Task 03: Directory Standard

**Task ID:** FOUNDATION-03
**Task Name:** Directory Standard
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Task Version:** 0.1.0-draft
**Date:** 2026-08-03
**Builder:** Foundation Builder (Task 03 cycle)
**Status:** Approved

---

## 1. Summary

Task 03 establishes the **canonical directory layout** of the Research-OS Foundation. It creates the Foundation Standard that operationalizes Constitution §9 (Naming Convention) for *directory paths* and binds the storage location for every Foundation artifact class declared in `governance-model.md` §6.

The deliverable is `FOUNDATION/03-Standards/directory-standard.md`, an L3 Foundation Standard that defines:

- The top-level `FOUNDATION/` subtree and the numbered-prefix convention (`01-` to `16-` reserved).
- Per-class storage paths for every Foundation artifact (FD, FRFC, PRFC, RRFC, ADR, Audit, Review, Report, DIS-, Standard, README, VERSION).
- The reserved-directory list (paths that exist semantically but may not yet contain files).
- Path-mutation rules (create, rename, remove, split — each requires an FD).
- Path-validation rules (the five criteria a valid path must satisfy).
- Cross-references to Constitution, Governance Model, and all related Policies.
- Compatibility guarantees (backward, forward, migration) per Constitution §2.

The Standard is **Draft / In Review** at version `0.1.0-draft`, Foundation `0.1.0-dev`. Its ratification is **deferred and conditional** — no `FD-0003-ratify-directory-standard.md` is created in Task 03.

## 2. Files Created

The following files were created in the Task 03 cycle:

```
FOUNDATION/03-Standards/directory-standard.md
FOUNDATION/03-Standards/README.md
FOUNDATION/04-Audits/AUDIT-FOUNDATION-03-directory.md
FOUNDATION/06-Reports/REPORT-FOUNDATION-03-directory.md   (this file)
FOUNDATION/07-Reviews/REVIEW-FOUNDATION-03-directory.md
```

## 3. Files Modified

The following files were modified, within the allowed scope of Task 03:

```
FOUNDATION/README.md     (Layout table: added 03-Standards/ row; added Task 03 row)
CHANGELOG.md             (Task 03 entry added under Unreleased)
```

No other files were modified. Per §15.5, the Constitution (`FOUNDATION/01-Constitution/constitution.md`) and `FOUNDATION/VERSION` were not touched. The Task 02 deliverables (`FOUNDATION/02-Governance/**`, `08-RFCs/**`, `09-Decisions/**`, `10-ADRs/**`) were not touched.

## 4. Acceptance Checklist

- [x] Directory Standard created in `FOUNDATION/03-Standards/directory-standard.md`.
- [x] Standard declares `Status: Draft / In Review`, `Version: 0.1.0-draft`, `Foundation Version: 0.1.0-dev`.
- [x] Standard declares Path, Supersedes, and Related header fields.
- [x] §1 Purpose and Scope declared (purpose + in-scope + out-of-scope).
- [x] §2 Normative Status declared (conformance + conflict resolution).
- [x] §3 Top-level Layout declared (Repository root + `FOUNDATION/` subtree).
- [x] §4 Per-class Storage Paths declared for FD, FRFC, PRFC, RRFC, ADR, Audit, Review, Report, DIS-, Standard, README, VERSION (11 storage patterns).
- [x] §5 Numbered-Prefix Convention declared (16 prefixes: `01-` to `16-`).
- [x] §6 Reserved Directories declared (`05-Statistics/`, `11-`–`16-`, `PROJECTS/`, `PROJECTS/<project>/08-PRFCs/`, `PROJECTS/<project>/10-ADRs/`).
- [x] §7 Path-Mutation Rules declared (create, rename, remove, split, supersession-not-mutation).
- [x] §8 Path-Validation Rules declared (five validity criteria).
- [x] §9 Cross References declared (Constitution §10.1 mandatory + back-references).
- [x] §10 Compatibility declared (version surfaces + backward/forward/migration).
- [x] §11 Relationship to Other Artifacts declared.
- [x] §12 Ratification declared as **deferred and conditional**; no `FD-0003` automatic.
- [x] Index README created for `03-Standards/`.
- [x] `FOUNDATION/README.md` Layout table updated; Task 03 row added.
- [x] `CHANGELOG.md` updated with Task 03 entry under Unreleased.
- [x] Audit Report created (PASS on all four §11 criteria; PASS on §15.5 scope).
- [x] Review Record created (Reviewer-ready).
- [x] Constitution not edited.
- [x] `FOUNDATION/VERSION` not edited.
- [x] No git operations performed.
- [x] No FRFC, RRFC, PRFC, FD, ADR, or other governance artifact created.
- [x] No Project-specific (APES) governance, lifecycle, schema, or implementation rules introduced.
- [x] No Sprint 4 (or any Sprint) executed.
- [x] No Foundation version change.
- [x] Hard Prohibitions (Constitution §15.3) observed.
- [x] §15.5 Per-Task Scope Declaration honored.

## 5. Verification

The following manual verifications were performed:

1. **Constitution not edited.** `FOUNDATION/01-Constitution/constitution.md` retains its `Status: Provisional` header and v0.1.0-draft content.
2. **FOUNDATION/VERSION unchanged.** Still `0.1.0-dev`.
3. **FD-0001 unchanged.** `FOUNDATION/09-Decisions/FD-0001-ratify-constitution.md` remains in `Pending Ratification` status.
4. **No `1.0.0-rc.1` declared.** No artifact, file, or report claims Foundation RC or Foundation v1.0.
5. **No `FD-0003` created.** `FOUNDATION/09-Decisions/` contains only `FD-0001` and the policy; no `FD-0003-*.md` exists.
6. **APES not codified.** No APES-specific governance, lifecycle, schema, or implementation rules in the Directory Standard. APES remains a paused Project (post-Foundation) without a Project subtree.
7. **No git operations.** No commit, push, branch, or tag was created.
8. **No Task 04 start.** Task 04 (Schema Standard) has not begun; this report ends with the Builder awaiting human approval.
9. **Storage path coverage.** All 11 Foundation artifact classes declared in `governance-model.md` §6 and the relevant Policies have explicit storage paths in `directory-standard.md` §4.
10. **Numbered-prefix coverage.** All 16 prefixes (current and reserved) are listed in `directory-standard.md` §5.1.

## 6. Remaining Limitations

1. **Directory Standard is Draft / In Review.** Its formal ratification is **deferred and conditional** — not an automatic next action via `FD-0003`.
2. **No Schema Standard, Pack Standard, Runtime Specification, or Quality Gate Standard yet.** Task 03 establishes the directory in which they will live; the Standards themselves are Tasks 04, 05, 06, 07.
3. **Foundation version unchanged.** Foundation remains `0.1.0-dev`; the `v1.0.0-rc.1` tag remains reserved for Task 12.
4. **Constitution unchanged.** Constitution remains `v0.1.0-draft` Provisional until `FD-0001` is ratified.
5. **Provisional governance.** Until `FD-0001` is ratified, Foundation work continues under Constitution §17.4 (Provisional governance on a best-effort basis).
6. **The on-disk filename is `directory-standard.md`, not `STD-DIR-v0.1.0-draft.md`.** The slug-style filename follows the development-draft convention used in Tasks 01–02 (e.g., `governance-model.md` rather than `STD-GOV-...md`); the formal `STD-DIR-vX.Y.Z.md` pattern (Constitution §9) is reserved for ratification. This is consistent with Constitution §8.3 first-release rule and with the precedent established by Task 02.

## 7. Git Status

- **Branch.** None (the working tree is not a git repository per the project meta-context).
- **Commit.** None.
- **Push.** None.
- **Tag.** None.

All Task 03 deliverables exist on disk only.

## 8. Next Recommended Task

After the human Architect reviews and approves Task 03:

- If **approved**: the Architect may authorize the start of **Task 04 — Schema Standard** (allowed files only per Task 04's scope declaration). Task 04 will produce `FOUNDATION/03-Standards/STD-SCHEMA-v0.1.0-draft.md` (or its development-draft filename equivalent) and its accompanying Audit/Report/Review records.
- If **corrections required**: the Architect specifies the corrections; the Foundation Builder revises the deliverables and re-presents this Task Report.

**STOP. Awaiting human review. Do not commit. Do not push. Do not begin Task 04.**

---

*End of REPORT-FOUNDATION-03-directory v0.1.0-draft.*
