# Task Report — Foundation Task 09: SDK Specification

**Task ID:** FOUNDATION-09
**Task Name:** SDK Specification
**Foundation Version:** 0.1.0-dev
**Constitution Version:** v0.1.0-draft (Provisional)
**Task Version:** 0.1.0-draft
**Date:** 2026-08-03
**Builder:** Foundation Builder (Task 09 cycle)
**Status:** Approved

---

## 1. Summary

Task 09 establishes the **canonical contracts** for five Foundation SDKs — the L5 components that define Interface Boundaries between Foundation artifacts and between Foundation and Project / Plugin / Builder / Migration tool / Release Manager. It produces an L3 Foundation Standard that declares, for any future SDK implementation, the SDK Specification format with nine required attributes per SDK: Purpose, Interface Boundary, Inputs, Outputs, Dependencies, Versioning, Compatibility, Security Rules, Extension Model.

The deliverable is `FOUNDATION/03-Standards/sdk-specification.md`, a 13-section Standard that defines five SDK Specifications:

- **§3 Project SDK Specification** — Foundation ↔ Project boundary; 5 security rules; Versioning + Compatibility + Extension Model.
- **§4 Builder SDK Specification** — Builder ↔ Builder Engine boundary; 7 security rules; honors §15.5 Per-Task Scope.
- **§5 Migration SDK Specification** — Pre-Migration ↔ Post-Migration boundary; 6 security rules; FD-gated.
- **§6 Release SDK Specification** — Pre-Release ↔ Post-Release boundary; 6 security rules; gated by RC Quality Gate.
- **§7 Plugin SDK Specification** — Foundation ↔ Plugin boundary; 7 Permission classes (least-privilege); concrete Plugin Specifications reserved for Task 10.

The Standard also defines Shared SDK Architecture (§8), SDK Lifecycle (9 stages) (§9), and Compatibility rules (§10). The Standard is **Draft / In Review** at version `0.1.0-draft`, Foundation `0.1.0-dev`. It is **technology-neutral** — no language binding, no framework binding, no serialization binding, no transport-protocol binding, no package-manager binding, no operating-system binding. Its ratification is **deferred and conditional** — no `FD-0009-ratify-sdk-specification.md` is created in Task 09.

Critically, **no SDK implementation is created**. No SDK source code, no `sdk/` directory, no packages, no published libraries, no APIs, no CLI, no plugins, no Runtime, no Pack execution. The Specification defines the *contracts* future SDKs must satisfy; the implementations are downstream deliverables.

## 2. Files Created

```
FOUNDATION/03-Standards/sdk-specification.md
FOUNDATION/04-Audits/AUDIT-FOUNDATION-09-sdk.md
FOUNDATION/06-Reports/REPORT-FOUNDATION-09-sdk.md   (this file)
FOUNDATION/07-Reviews/REVIEW-FOUNDATION-09-sdk.md
```

## 3. Files Modified

```
FOUNDATION/03-Standards/README.md   (SDK Specification row added; Future Standards list updated; Note updated)
FOUNDATION/README.md                (Task 08 marked approved; Task 09 row added)
FOUNDATION/07-Reviews/REVIEW-FOUNDATION-08-engine.md   (disposition set to Approved per Architect authorization)
CHANGELOG.md                        (Task 09 entry under Unreleased)
```

Per §15.5, the Constitution and `FOUNDATION/VERSION` were not touched. The Task 01, 02, 02.1, 03, 04, 05, 06, 07, and 08 deliverables were not edited.

## 4. Acceptance Checklist

- [x] SDK Specification created in `FOUNDATION/03-Standards/sdk-specification.md`.
- [x] Specification declares `Status: Draft / In Review`, `Version: 0.1.0-draft`, `Foundation Version: 0.1.0-dev`.
- [x] §1 Purpose and Scope declared.
- [x] §2 Normative Status declared.
- [x] **Project SDK Specification (§3)** with all 9 attributes.
- [x] **Builder SDK Specification (§4)** with all 9 attributes; honors §15.5.
- [x] **Migration SDK Specification (§5)** with all 9 attributes; FD-gated.
- [x] **Release SDK Specification (§6)** with all 9 attributes; gated by RC Quality Gate.
- [x] **Plugin SDK Specification (§7)** with all 9 attributes; 7 Permission classes.
- [x] §8 Shared SDK Architecture declared.
- [x] §9 SDK Lifecycle declared with 9 stages.
- [x] §10 Compatibility declared (4 version surfaces for Plugin; 3 for others; Migration + additive-only).
- [x] §11 Cross References declared.
- [x] §12 Relationship to Other Artifacts declared.
- [x] §13 Ratification declared as deferred and conditional; no `FD-0009` automatic.
- [x] Specification is **technology-neutral** — no language / framework / serialization / transport-protocol / package-manager / OS binding.
- [x] Specification is **project-independent** — no APES mention.
- [x] No SDK source code, no `sdk/` directory.
- [x] No packages, no published libraries, no APIs, no CLI, no plugins, no runtime.
- [x] No Pack instance, no Mission execution.
- [x] No Sprint 4 (or any Sprint) executed.
- [x] No Foundation version change.
- [x] No git operations.
- [x] Index README updated.
- [x] `FOUNDATION/README.md` Task 08 marked approved; Task 09 row added.
- [x] `CHANGELOG.md` Task 09 entry under Unreleased.
- [x] Audit Report created (PASS on all four §11 criteria; 3 Minor observations).
- [x] Review Record created (Reviewer-ready, Pending).
- [x] Hard Prohibitions (§15.3) observed.
- [x] §15.5 Per-Task Scope Declaration honored.

## 5. Verification

1. **Constitution not edited.** `constitution.md` retains `Status: Provisional`.
2. **FOUNDATION/VERSION unchanged.** Still `0.1.0-dev`.
3. **No `1.0.0-rc.1` declared.**
4. **No `FD-0003` through `FD-0009` created.**
5. **APES not codified.** No APES-specific rules in the SDK Specification.
6. **No SDK implementation.** No source code, no `sdk/` directory, no packages, no APIs.
7. **No Pack instance created.**
8. **No engine / runtime / SDK / plugin / workspace / release artifacts.**
9. **No git operations.**
10. **Task 08 disposition set.** `REVIEW-FOUNDATION-08-engine.md` updated to `Approved`.
11. **Coverage.** All 5 SDK Specifications present; all 9 attributes per SDK; Shared Architecture; 9-stage Lifecycle; Compatibility rules; cross references.
12. **Technology-neutrality.** No language / framework / serialization / transport-protocol / package-manager / OS binding.
13. **Project-independence.** No APES mention.

## 6. Remaining Limitations

1. **SDK Specification is Draft / In Review.** Ratification deferred and conditional.
2. **No SDK implementation exists.** Contracts declared; implementations are downstream deliverables.
3. **No formal contract language.** Natural-language clauses; future mapping to formal interface contract language is a downstream deliverable.
4. **No SDK invocation.** No SDK is invoked in Task 09.
5. **Concrete Plugin Specifications (GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor) are reserved for Task 10.** The Plugin SDK Specification declares the *form* of the Plugin contract; the concrete Plugin Specifications are Task 10 deliverables.
6. **Foundation version unchanged.** `0.1.0-dev`; `v1.0.0-rc.1` reserved for Task 12.
7. **The on-disk filename is `sdk-specification.md`, not `STD-SDK-v0.1.0-draft.md`.** Slug-style filename; formal pattern reserved for ratification.

## 7. Git Status

- **Branch.** None (working tree is not a git repository).
- **Commit.** None.
- **Push.** None.
- **Tag.** None.

All Task 09 deliverables exist on disk only.

## 8. Next Recommended Task

After the human Architect reviews and approves Task 09:

- If **approved**: the Architect may authorize the start of **Task 10 — Plugin Specification** (allowed files only per Task 10's scope declaration). Task 10 will produce the L3 Foundation Standard that declares the concrete Plugin Specifications for GitHub, Obsidian, MCP, Claude, Codex, VSCode, Cursor — each with Plugin Purpose, Plugin Boundary, Interface Contract, Permission Model, Input/Output Model, Security Isolation, Version Compatibility, Extension Lifecycle. **No plugin implementation. No plugin installation. No external service connections. No MCP server. No extensions. No integrations.**
- If **corrections required**: the Architect specifies the corrections; the Foundation Builder revises the deliverables and re-presents this Task Report.

**STOP. Awaiting human review. Do not commit. Do not push. Do not begin Task 10.**

---

*End of REPORT-FOUNDATION-09-sdk v0.1.0-draft.*
