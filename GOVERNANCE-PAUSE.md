# Research-OS Foundation 治理暂停记录

**Status:** Non-normative — 事实陈述，非规范变更
**Version:** 1.0.0
**Foundation Version at Pause:** `1.0.0-rc.1`
**Baseline Commit:** `77b9ec6ae77ccf12d21cc8dbdf15c640d65010de`
**Recorded By:** Human Architect
**Date:** 2026-08-20

> 本文件不修改任何 Foundation 规范工件，不撤销任何已 Ratified 的决定，
> 也不是 Foundation Decision。它记录一个关于项目运行状态的事实：
> Foundation 治理周期自本日起暂停。

---

## §1 暂停声明

本人以 **Human Architect** 身份，自本记录之日起暂停 Research-OS Foundation
的治理周期运作。

**暂停范围：**

- 不再启动新的 Validation Cycle。
- 不再推进现有 Validation Cycle 04 与 05 至 Review 或 Architect 处分阶段。
- 不再提交、审查或批准任何 FRFC。
- 不再签发任何新的 Foundation Decision。
- 不创建 `FOUNDATION/11-` 至 `15-` 目录、ADR、Pack、Workspace 或 Project。

**不在暂停范围内（继续有效）：**

- Constitution 保持 **Ratified**。
- `FD-0001` 至 `FD-0005` 保持 **Ratified**，其授权与约束继续有效。
- Foundation 保持 `1.0.0-rc.1`，保持 **Frozen** 状态。
- 已发布的 `v1.0.0-rc.1` tag 与 GitHub Pre-release 不受影响。
- 全部既有 Audit、Report、Review 记录保持其当前状态，作为历史证据保留。

本记录**不是**对 Foundation 的废弃、作废或终止。

---

## §2 停止点快照

暂停时的确切状态。恢复时以此为准。

### §2.1 Foundation

| 项 | 状态 |
|---|---|
| Foundation 版本 | `1.0.0-rc.1`（internally Applied，externally published as Pre-release） |
| Constitution | Ratified（FD-0001, 2026-08-03），版本 `0.1.0-draft` |
| Foundation Tasks 01–12 | 全部 completed |
| Foundation Decisions | FD-0001 … FD-0005，全部 Ratified |
| 10 个 Standards / 5 个治理件 | 文档级 `Draft / In Review`；约束力来自 FD-0003 对确切版本的批准 |
| 基线 commit | `77b9ec6ae77ccf12d21cc8dbdf15c640d65010de` |

### §2.2 Validation Cycle 04 — **暂停**（非进行中）

| 记录 | 状态 |
|---|---|
| `REPORT-VALIDATION-04.md` | `Draft` / `0.2.0-draft`，ID 为 `EVID-FOUNDATION-0004-...`，SHA-256 `1512A3D279C2E2BC22957571CD41A4B8FE312A2A3763A7EFBB96924A3C677BCF` |
| `AUDIT-VALIDATION-04.md` | Builder 自审，`Draft` / `FAIL`，历史证据 |
| `AUDIT-VALIDATION-04-independent-audit.md` | 独立人类 Audit，`FAIL`（针对 `0.1.0-draft`），历史证据 |
| `AUDIT-VALIDATION-04-correction-01-independent-audit.md` | 独立人类跟进 Audit，**`PASS`**，关闭 IA-03 与 IA-06 |
| `REVIEW-VALIDATION-04.md` | **`Pending`** — 未完成，暂停于此 |
| Human Architect Step-1 acceptance | **无** — 未完成，暂停于此 |

**已通过的门：** 独立 Audit。
**未通过的门：** Human Review、Architect Step-1 acceptance。

⚠️ 两份独立 Audit 均声明「若审计期间文件发生变更，本记录作废」，并钉在
commit `77b9ec6`。恢复时若基线已变，须在新基线上重做。

### §2.3 Validation Cycle 05 — **暂停**（非进行中）

| 记录 | 状态 |
|---|---|
| `EVID-FOUNDATION-0005-report-status-lifecycle.md` | `Draft`，**未提交，无内容哈希** |
| `AUDIT-VALIDATION-05-report-status-lifecycle.md` | Builder 自审，`PASS with Notes` |
| `REVIEW-VALIDATION-05-report-status-lifecycle.md` | **`Pending` / `HOLD`** |
| 独立 Audit | **无** |

⚠️ Evidence 尚未冻结。恢复前必须先提交取得哈希，否则独立 Auditor 没有可审计的
稳定对象。

**已确认的实质结论（保留价值）：** C6 冲突真实存在。`schema-standard.md` §5.2 的
Report Status 枚举与 §5.5 的 `Draft → In Review` 转换、`quality-gate-standard.md`
§4.2.1 的 `Draft` 主体状态、§4.3 的 `Pending Approval`、以及 `governance-model.md`
§7 的更宽生命周期之间存在互不相容。24 份 Report 中 15 份在枚举内、9 份在枚举外。

### §2.4 FRFC-0003 — **暂停于 Draft**

`Draft` / `0.2.0-draft`。四条 Major 未闭：

- **F-01** Validation Step-1 证据未被独立接受
- **F-02** 无独立 Auditor 认证 FRFC 包
- **F-06** 非 Task Report 无 schema 可解析的 Task-ID
- **F-07** 关闭的 Tasks 01–12 未提供 post-RC 工作单元机制

**F-07 是最深的结构性阻塞：** 即使其余全部解决，仍不存在任何合法机制可以签发
实现工作单元。

### §2.5 已知的下游不一致（暂停时未修）

修正后的 `REPORT-VALIDATION-04` 撤回了「唯一路径」结论，但以下位置仍断言排他性：

```
FOUNDATION/README.md:69      "The evidence provisionally supports only 11-Runtime"
FRFC-0003:85                 "provisionally recommends only 11-Runtime"
REVIEW-FRFC-0003:29          预设了已被撤回的前提
REVIEW-VALIDATION-04.md:104  描述已被取代的结论
```

**恢复时必须先处理这一项**，否则任何 Reviewer 会读到互相矛盾的两套结论。

---

## §3 暂停理由

Research-OS Foundation 的治理体系为**多人组织**设计。其角色分离要求由以下条款
构成，且相互叠加：

```
Constitution §5              任一人不得在同一工件上担任多于一个角色
roles-and-authority §5.5     Auditor 不得同时是 Builder 或 Reviewer
roles-and-authority §3.3     Architect 不得撰写 Builder 工件（含 Audit）
roles-and-authority §12      AI 代理固定为 Builder 角色，不得担任
                             Architect / Reviewer / Release Manager
```

本项目当前为**单人维护 + AI Builder**。在该配置下：

- Builder ↔ Auditor 分离**可以**满足（AI 是 Builder，人是 Auditor）。
- Auditor ↔ Reviewer ↔ Architect 分离**无法**满足 —— 三个角色只有一个真人可用。

因此单个 Validation Cycle 最多推进到「独立 Audit 完成」，**必然停在 Review 门槛**。
这已在 Cycle 04 与 Cycle 05 上各发生一次，并由 Cycle 04 的独立 Audit 记录为
观察 OBS-02。

继续启动新的治理周期，只会累积无法闭合的记录，并使已完成的审计证据随基线漂移
而失效。暂停是在该约束下的合理处置，而非执行失败。

---

## §4 MVP 脱钩声明

**自本记录之日起，`.codex-mvp-phase1/` 作为独立实验原型推进，不受 Foundation
治理门禁约束。**

**这意味着：**

- MVP 的代码、测试、文档变更**不需要** Validation Cycle、FRFC、FD 或人工 Review 授权。
- MVP 的产物**不是** Foundation 工件，不适用 Constitution §9 命名规范、
  §11 Quality Gate 或 Schema Standard。
- MVP 的任何状态、结论或版本号**不代表** Foundation 的任何立场。

**同时意味着（限制）：**

- MVP **不因此获得**任何 Foundation 授权。它没有、也不会自动获得
  `FOUNDATION/11-Runtime/` 或任何 Foundation 路径。
- MVP **不得**写入 `FOUNDATION/**` 或 `VALIDATION/**`。
- 将来若要把 MVP 纳入 Foundation，须**另行**走完整的 Validation → RFC → FD →
  受控补丁流程；本记录不预先授权任何部分。

**暂停时的 MVP 状态：** 198 个测试通过（Python 3.12.13 与 3.14.6），
行覆盖率 87.8%，`ruff check` 全仓通过。

---

## §5 恢复条件与遗留项

### §5.1 恢复的前置条件

恢复治理周期需要**其中之一**：

| 路径 | 需要 |
|---|---|
| **A** 引入真人 | 两名区别于 AI Builder、且互不相同的真人，分别担任 Reviewer 与 Architect |
| **B** 修订角色规则 | 一轮完整 FCP 循环，正式定义单人维护者模式下的角色分离等价机制。**注意：该循环自身也需要三方角色，因此启动时仍需一次显式的减配例外** |
| **C** 显式减配 | Human Architect 显式接受非独立 Audit，并设置补偿控制（强制 AI 对抗性复核、Auditor 与 Reviewer 间强制时间间隔、每份记录标注 `role-separation: reduced`、设有效期）。**代价：该先例会被后续所有周期援引** |

**恢复的第一个动作（无论选哪条路）：** 处理 §2.5 的下游不一致。

### §5.2 遗留观察项（已记录，未处分）

以下七条来自 `AUDIT-VALIDATION-04-independent-audit.md` §4.B。它们不属于任何
周期的 Subject，**没有任何现有 Review 会处理它们**。暂停期间保持未处分。

| ID | 内容 |
|---|---|
| **OBS-01** | `VALIDATION/` 的路径授权未明确 —— Directory Standard §3.1 未列出该根目录 |
| **OBS-02** | 后续独立 Human Reviewer 与 Human Architect 当前不可用 |
| **OBS-03** | Builder 自审 V04-F1 的 Subject 与实际批评对象错位 |
| **OBS-04** | Builder 自审 V04-O2 记录的是预期流程状态，非缺陷 |
| **OBS-05** | 仓库未规范化 Markdown anchor 解析算法 |
| **OBS-06** | Cycle 01 Audit 的独立性与现行标准不一致（Builder 兼 Auditor 却判 PASS；严重度词表不合 Schema §9.4） |
| **OBS-07** | Cycle 01 Review 的处分与支撑核对表不一致（§4 有 `Approved with Notes`，§3 有 37 处 `To be filled by Architect` 空白） |

**OBS-06 与 OBS-07 影响面最大** —— Cycle 01 的证据被 26 份仓库文件引用，
含 FD-0001 与 FRFC-0001/FD-0002 两条主线。若将来采用严格的审计独立性标准，
一致性要求同一标准回溯适用于 Cycle 01。

### §5.3 不设期限

本暂停**不设恢复期限**。设定期限而到期未恢复，会使本记录本身失效。

**「永久暂停」是一个可接受的终局。** Foundation `1.0.0-rc.1` 作为一套写完的、
自洽的、已发布的治理规范，其价值不依赖于是否被继续执行。

---

## §6 本记录不做什么

- 不修改任何 Foundation 规范工件
- 不撤销 FD-0001 至 FD-0005
- 不作废 Cycle 04 的独立 Audit（它仍是有效的历史记录）
- 不是 Foundation Decision，不需要 FRFC、Audit 或 Review
- 不授权任何实现、目录、依赖、Pack、Project 或 APES 工作
- 不承诺恢复

---

*End of Governance Pause Record. Non-normative.*
