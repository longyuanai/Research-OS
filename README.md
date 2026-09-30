# Research-OS

Research-OS 是一个 **docs-first、evidence-first** 的 AI 研究执行系统：先把治理、
状态、证据、人工审批和可回放性定义清楚，再实现可运行的 Builder Pack 与
Runtime。

> **当前版本：`1.0.0-rc.1`（Release Candidate）**<br>
> 这是 Foundation 文档与治理基线，不是已经可运行的 AI 平台。仓库当前不包含
> 生产 Runtime、可执行 Builder Pack、Workspace、已激活 Project 或 APES 业务
> 数据，也不应被用于无人值守的生产任务。<br>
> 另有一个本地运行的隔离实验原型 [`.codex-mvp-phase1/`](./.codex-mvp-phase1/README.md)，
> 仅用于验证产品闭环，不是 Foundation 规范实现。

公开 Pre-release：[`v1.0.0-rc.1 — docs-first RC`](https://github.com/longyuanai/Research-OS/releases/tag/v1.0.0-rc.1)
（2026-08-05）。

## 项目要解决什么

普通 Agent 框架通常重点解决“怎样调用模型和工具”。Research-OS 进一步约束：

- 谁可以批准状态转换和外部动作；
- 一条结论由哪些来源和证据支持；
- 任务中断后如何恢复且不重复副作用；
- Pack、Run、Deliverable、Audit、Review 和 Report 如何形成可复核工件；
- 文件、网络、凭据、Git、发布和删除权限如何默认拒绝、逐项授权。

首个计划中的可运行作品是：验证一个 Builder Pack，在受控 Workspace 中执行
研究 Mission，保存来源、状态转换、工具调用与人工批准证据，最终输出带引用的
Deliverable 和审计记录。

## 当前已有与尚未实现

| 范围 | 当前状态 |
|---|---|
| Foundation Constitution、Governance、Standards | 已形成 `1.0.0-rc.1` 基线；治理周期已暂停（见 [`GOVERNANCE-PAUSE.md`](./GOVERNANCE-PAUSE.md)） |
| Audit、Report、Review、FD/FRFC 证据链 | 已存在并可人工复核 |
| Validation Cycle | 01–03 已完成记录；04/05 已随治理暂停归档，未进入 Review |
| 技术选型与分阶段实施路线 | Proposed / Non-normative |
| MVP 隔离实验原型（[`.codex-mvp-phase1/`](./.codex-mvp-phase1/README.md)） | 可在本机运行；**非 Foundation 规范实现**，不改变任何治理状态 |
| └ CLI、中文向导与实验性 JSON Pack | 已实现：一句话目标生成恰好 3 个 Task 的 Pack，严格校验并封存 |
| └ 本地 Run Runtime | 已实现：逐 Task 人工门禁（Approved / Changes Requested / Rejected）、append-only 事件与审查哈希链、`HASHES.*` 完整性校验、跨进程文件锁、SQLite 检查点、不可变修订 Evidence |
| └ 证据与 Claim 门禁 | 已实现：资料导入（PDF/网页/文本/代码目录/Git 快照）、Claim 确认与引用硬门禁、AI 草稿候选 Claim 逐条人工确认、确定性有效输出 Manifest |
| └ Reviewer 签名与信任策略 | 已实现（可选）：OpenSSH Ed25519 签名链、Run 级不可变信任注册表快照 |
| └ 本地 AI（Ollama） | 已实现：仅本机回环端点；NDJSON 流式生成、块间空闲超时与总时长预算；AI 审计角色、本地模型基准 |
| └ 导出与交接 | 已实现：Obsidian Markdown 快照导出、面向外部 AI 的研究交接指令 |
| └ 自动化测试与 CI | 已实现：标准库 `unittest` 套件（Ollama 全部 mock），GitHub Actions 在 Python 3.12 / 3.14 上运行 |
| 符合 Foundation 的 Python Domain Kernel、Pack Compiler | 尚未实现，须先通过实现 RFC 门禁（MVP 不替代它们） |
| Runtime 编排（LangGraph Adapter）、PostgreSQL、Docker Sandbox | 尚未实现 |
| 远程/云端模型 Provider、实时联网检索 | 尚未实现（MVP 仅支持本机 Ollama） |
| Web Console、Plugin、APES Project | 尚未激活 |

## 从这里开始

| 文档 | 用途 |
|---|---|
| [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md) | 同类开源项目对比、目标架构、技术栈、阶段路线与验收门禁 |
| [`FOUNDATION/README.md`](./FOUNDATION/README.md) | Foundation 版本、布局、任务终态与治理入口 |
| [`FOUNDATION/01-Constitution/constitution.md`](./FOUNDATION/01-Constitution/constitution.md) | 最高层原则与权限边界 |
| [`FOUNDATION/02-Governance/`](./FOUNDATION/02-Governance/) | 角色、审批、变更和升级机制 |
| [`FOUNDATION/03-Standards/`](./FOUNDATION/03-Standards/) | Directory、Schema、Pack、Runtime、Quality Gate 等规范 |
| [`FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md`](./FOUNDATION/16-Releases/RELEASE-1.0.0-rc.1-MANIFEST.md) | RC 内容、完整性与生命周期记录 |
| [`VALIDATION/`](./VALIDATION/) | Validation Plan、Checklist、Report、Audit 与 Review |

## 实施原则

1. Markdown + YAML Front Matter 作为人类可审阅的治理工件源。
2. 以 Python 3.12 的独立 Domain Kernel 解释 Foundation Schema 和状态机。
3. Pack Compiler 先完成纯验证、引用解析和 SHA-256 Manifest，不调用模型。
4. Runtime 通过适配器使用编排引擎；首选 LangGraph，但不把框架类型写入
   Foundation 工件。
5. 外部副作用必须经过 Permission Gate 和 Human Approval Gate。
6. APES 只在源项目盘点、PRFC/PD 和人工 Review 完成后作为首个试点。

完整架构与验收条件见[技术实现方案](./IMPLEMENTATION-PLAN.md)。该方案是
非规范性提案；与 Foundation 规范冲突时，以已批准的 Foundation 工件为准。

## Release 语义

- `v1.0.0-rc.1` 标签封存 Foundation 内部 Applied 内容，并在其上只增加标准
  `LICENSE` 与跨平台行尾策略 `.gitattributes` 作为公开分发封装；25 项
  Foundation Manifest 内容不变。
- 标签之后的 `main` 可以包含其余公开仓库材料和下一阶段提案；这些材料不会
  追溯性进入该 RC Manifest。
- GitHub Release 应标记为 **Pre-release**，并明确“docs-first / no runtime”。
- `v1.0.0-rc.1` 已按上述语义发布为 GitHub Pre-release；发布后状态记录位于
  `main`，不追溯修改 tag。
- Stable `1.0.0`、Package Registry 发布或生产可用性均未声明。

## 参与贡献

提交前请阅读 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。Foundation 规范性变更
必须遵循 FRFC → Audit/Report → Human Review → FD → Apply 的治理路径；一般
文档修正仍需保持证据、引用和状态一致。

安全问题请不要提交公开 Issue，按 [`SECURITY.md`](./SECURITY.md) 使用 GitHub
私有漏洞报告渠道。

## License

除文件中另有明确声明外，本项目的代码和文档均按
[Apache License 2.0](./LICENSE) 许可。

---

**English summary:** Research-OS is currently a documentation-first Foundation RC for
an auditable, evidence-first AI research runtime. Apart from an isolated,
non-normative local MVP prototype in `.codex-mvp-phase1/`, it does not yet ship a
Foundation-conformant runtime or an activated project. Start with the
[implementation plan](./IMPLEMENTATION-PLAN.md) and the
[Foundation index](./FOUNDATION/README.md).
