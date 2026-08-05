# Contributing to Research-OS

感谢你帮助 Research-OS 从可审阅的 Foundation 走向可验证的运行系统。当前仓库
仍是 docs-first RC，因此“状态和证据一致”与文本或代码本身同样重要。

## 贡献前先确认范围

- 修正拼写、失效链接或非规范性说明：可以直接提交小型 Pull Request。
- 修改 Foundation Constitution、Governance、Standard、Schema、生命周期、权限
  或保留目录：必须走 Foundation RFC 流程。
- 激活 `FOUNDATION/11-*` 至 `15-*`、新增生产依赖或实现 Runtime：必须已有明确
  的批准决定和 Review 证据。
- 创建或迁移 Project（包括 APES）：必须先完成源项目盘点，并走 PRFC/PD 与人工
  Review；不要把私有项目数据复制到本仓库。

不确定时，先创建一个不含敏感信息的 Issue，说明问题、预期结果和建议范围。

## 治理路径

规范性 Foundation 变更采用以下顺序：

```text
Validation evidence
  → Draft FRFC
  → Audit + Report
  → Human Review
  → Ratified FD
  → Minimal implementation
  → Verification + closeout record
```

任何 Builder、Agent 或自动化都不能替自己完成 Human Review，不能把 `Pending`
自行改成 `Approved`，也不能在 FD Ratified 前激活保留实现目录。Project 级变更
使用相同原则下的 PRFC/PD 路径。

请先阅读：

- [`FOUNDATION/02-Governance/change-control-policy.md`](./FOUNDATION/02-Governance/change-control-policy.md)
- [`FOUNDATION/02-Governance/approval-workflow.md`](./FOUNDATION/02-Governance/approval-workflow.md)
- [`FOUNDATION/08-RFCs/rfc-policy.md`](./FOUNDATION/08-RFCs/rfc-policy.md)
- [`FOUNDATION/09-Decisions/foundation-decision-policy.md`](./FOUNDATION/09-Decisions/foundation-decision-policy.md)

## 提交要求

1. 保持改动最小，不无理由重构或更换技术栈。
2. 在修改前阅读相关规范、Decision、Review 与当前状态索引。
3. 不新增无必要的生产依赖；新增依赖时说明许可证、安全面和替代方案。
4. 不提交 Secret、凭据、客户数据、APES 私有资料或真实个人敏感信息。
5. 更新受影响的 README、索引、Manifest/Report/Review 和 `CHANGELOG.md`，但不要
   改写已经封存的历史事实。
6. 运行与改动相称的测试、类型检查、Lint、链接检查和安全检查，并在 PR 中列出
   实际结果。
7. 明确剩余风险、回滚方法和未验证部分；不得把“准备好”写成“已完成”。

## Pull Request 内容

PR 描述至少应包含：

- 问题与范围；
- 修改文件和关键决定；
- 对 Foundation / Release / Project 状态的影响；
- 验证命令及结果；
- 安全、兼容性、迁移和回滚影响；
- 相关 Issue、FRFC、FD、PRFC、PD、Audit、Review 或 Report。

请避免在一个 PR 中混合无关重构、格式化和治理变更。

## AI 辅助贡献

可以使用 AI 辅助，但提交者仍对正确性、来源、许可证、安全性和测试负责。PR 中
应说明 AI 是否生成了实质性代码/文本，以及人工做过哪些核对。不得把模型输出
当成人工批准或独立审计。

## License 与贡献协议

仓库当前不要求单独 CLA 或 DCO。除提交中另有明确且兼容的声明外，贡献者提交的
内容将按本项目的 [Apache License 2.0](./LICENSE) 提供。请只提交你有权许可的
内容，不复制许可证不兼容的第三方代码或文档。

安全问题请遵循 [`SECURITY.md`](./SECURITY.md)，不要提交公开漏洞 Issue。
