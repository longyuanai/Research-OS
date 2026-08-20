# Research-OS MVP 与其他 AI 协作指南

## 1. 先分清两类 AI

### 内置本地 AI（最省事）

双击 `双击这里开始.cmd` 后正常创建任务。第 1 步批准后，系统会自动调用
Ollama 的 `qwen2.5:7b` 生成草稿，并将完整结果、模型名、结束原因、输出 Token、
限制和 Hash 写入 Evidence。当前生成固定关闭思考输出，默认最多输出 1536 Token；
如果模型因长度上限截断，Evidence 会明确标记。审核时会记录正式 Reviewer 决定：

- 输入 `Y`：记录 `Approved`，生成关联 Approval，然后继续。
- 输入 `R`：记录 `Changes Requested` 及具体意见，让 AI 生成新版本；
  新 Evidence 会链回该 Reviewer 决定，旧版本继续保留。
- 输入 `X`：记录 `Rejected` 和原因，Run 进入独立终态，产物保留。
- 直接回车：保存现场，下次从当前门禁继续。

在 Task 1 或 Task 3 选择 `R` 后，可直接粘贴完整修订内容，或输入
`@UTF-8文件路径`。系统会把新版保存为 `task_output_revision` Evidence，
保留原产物，并将修订版同时链回上一版和对应 Reviewer 决定。

修订稿写入后仍处于待审状态。只有新的 `Approved` 决定把该稿封存为
`latest_revision_id` 后，它才会成为查看、AI 交接、最终报告视图和导出的默认内容；
`Changes Requested` 阶段的稿件会继续显示在审计 Evidence 中，但不会提前下发。
如果 Run 已绑定 Reviewer 信任策略，`Approved` 后还必须补齐指定角色和数量的可信
Ed25519 签名；门槛不足时 Run 保持 `approved_pending_resume`，有效内容仍使用上一个
策略合格版本。

主菜单输入 `7` 可检查 Ollama 服务和模型。这个本地模型不访问实时网页；遇到
价格、版本、供货、法规或精确参数时，应把官方文档、数据手册或实测结果再导入
Evidence。

命令行可用固定提示词复测已安装模型：

```powershell
python -m research_os_mvp benchmark-ollama --workspace workspace `
  --model qwen3:1.7b `
  --model qwen2.5:3b-instruct-q4_K_M `
  --model qwen2.5:7b
```

报告保存完整草稿与检查结果，控制台只显示摘要。2026-08-09 当前机器实测中，
`qwen2.5:7b` 用时 32.578 秒并通过全部门槛；两个更小模型虽为 13.438 秒和
16.078 秒，但都生成了缺少来源的精确参数或价格，因此不切换默认模型。该门槛
不证明事实正确，所有实际选型参数仍需证据核验。

主菜单还支持：`8` 导入本地资料、`10` 比较 AI 版本、`12` 导出 Obsidian、
`13` 导入 Git 快照。Git 测试只有在用户输入精确的 `RUN` 后才执行；其余情况
只记录只读状态。

需要终止未完成任务时，主菜单输入 `9` 进入高级菜单，再输入 `13`。只有精确输入
`CANCEL` 并填写取消原因才会生效；系统会保留全部 Evidence、Report、
Reviewer、Approval、事件和 Hash。这是操作性取消，与 Reviewer 的 `Rejected`
分开记录。审查界面输入 `N` 或回车只是保存并暂停。

### 具有终端和文件权限的 AI

例如 Codex、Claude Code 或可操作本地工作区的 Agent。它们可以直接运行 Research-OS CLI。

可复制这段话给它们：

```text
你作为 Builder，使用本地 Research-OS MVP 处理以下目标。
项目路径：<Research-OS 仓库目录>\.codex-mvp-phase1
目标：<填写你的一句话目标>
场景：<auto 或指定 category>

执行要求：
1. 先运行 quickstart 生成 Pack 并执行 Task 1。
2. 到达人工门禁后停止，展示 Evidence、来源、方法、限制和 Hash。
3. 不代替我做 Reviewer 决定，等待我明确选择 Approved、Changes Requested 或 Rejected。
4. 用 review 记录决定；只有 Approved 后才 resume，返工 Evidence 必须引用对应决定 Hash。
5. 完成后运行 verify，报告 Event、Reviewer、Approval、Evidence、Report 和哈希统计。
6. 保持零网络、零外部命令、零自动批准的 MVP 边界。
```

### 只能聊天的 AI

例如没有本地终端权限的网页版 ChatGPT、Claude 或 Gemini。它们适合准备证据草案，
然后由你将结果交给本地 Codex/Research-OS 入库。

可复制这段话：

```text
请作为 Research-OS Evidence Preparer 处理以下目标：
<填写目标>

请输出：
1. 目标和范围重述。
2. 候选项或需核查主张。
3. 每条证据的 Source、Collected-At、Method、Content、Limitations。
4. 事实、推断、建议和未知项分开记录。
5. 反证或可能改变结论的条件。
6. 不作出人工批准决定，最后明确列出“待人工确认”。
```

## 2. 八类任务的一句话调用

### 技术选型

```text
用 Research-OS 比较 Python、TypeScript 和 Rust，针对本地 AI 工具的开发效率、生态、性能、安全和维护成本给出可追溯建议。
```

### 项目决策

```text
用 Research-OS 记录我们是否在当前阶段引入数据库，分别列出采用、延后和放弃的证据、成本、风险和触发条件。
```

### 学习研究

```text
用 Research-OS 研究 Transformer Attention，保存来源、理解、疑问、反例和结论，生成可复习的证据报告。
```

### 项目验收

```text
用 Research-OS 验收这个 CLI 项目，逐项核对需求、自动测试、手工演示、文档、安全检查和剩余限制。
```

### 安全审计

```text
用 Research-OS 审计本地 Web 项目的认证、输入校验、文件访问和 Secret 管理，保存证据、限制和剩余风险。
```

### 硬件选型

```text
用 Research-OS 比较 ESP32 和 STM32，为低功耗环境监测设备评估接口、算力、功耗、成本、供货和开发风险。
```

### 内容核查

```text
用 Research-OS 核查这篇文章的五个关键主张，追溯原始来源、日期和上下文，寻找交叉证据与反证。
```

### AI 工作监督

```text
用 Research-OS 监督 AI 完成一次代码修改：先声明可写文件和禁止项，每个 Task 后展示产物并等待我批准，最后验证测试与 Hash。
```

## 3. 真正提升效率的使用规则

1. **只对重要任务使用。** 预计超过 30 分钟、需多来源、有返工风险或需批准的任务适合进入 Research-OS。
2. **一句话先启动。** 先用 `quickstart` 得到目标和评估框架，再补真实证据，减少先搭大系统的时间。
3. **把 AI 输出当作草案 Evidence。** 保留来源、方法和限制，由你决定是否批准。
4. **每个门禁只检查一件事。** Task 1 检查目标，Task 2 检查证据与评估框架，Task 3 检查报告。
5. **将修改条件记录下来。** 不只写“选 A”，还写“什么新证据会让我们改选 B”。
6. **每次结束运行 `verify`。** 用于发现意外修改、缺失产物或日志断链。

## 4. 已实现的协作扩展

- PDF、网页文件、数据手册、文本和代码目录可作为只读原始 Evidence 导入。
- 初稿、返工稿、第二 AI 审计意见可保留版本链并进行对比；返工稿
  还会引用导致它的 `Changes Requested` Hash。
- 非 AI Task 的通用修订版也使用 Evidence 版本链，支持文本粘贴或 UTF-8
  文件导入，不覆盖原 Evidence / Report。
- `Approved / Changes Requested / Rejected` 是独立 append-only Reviewer 哈希链；
  Obsidian 快照会额外导出 `Reviewer Decisions.md`。
- 已验证 Run 可导出为 Obsidian Markdown 不可变快照；`Effective Task Outputs.md`
  和 `Mission Report.md` 使用最新 Approved 版本，原始报告另存供复核；同时导出
  `Effective Output Manifest.json`，绑定权威快照、Reviewer 链尾和逐 Task 产物 Hash。
- `effective-outputs <run-dir>` 可直接返回确定性 JSON；查看、交接和导出从同一次
  加锁快照生成，避免审核与读取并发时混用两个版本；导出的 JSON 可用
  `verify-effective-manifest <manifest.json>` 独立校验。
- Reviewer 决定可选使用 `sign-review` 附加 OpenSSH Ed25519 身份签名；私钥不进入
  Run。高隔离场景可用 `review-signing-request` 导出载荷、离线签名，再通过
  `attach-review-signature` 入链。Manifest 也支持独立签名和离线验签。
- 公钥指纹证明“该密钥签过此载荷”；`seal-reviewer-trust` 可把团队核验过的公钥、
  identity、role、有效期/吊销时间和签名门槛封成自校验注册表。首次审查前使用
  `bind-reviewer-trust` 固定到 Run 后，`resume`、有效输出、交接、报告和导出都会采用
  同一策略判断。可用 `reviewer-trust-status` 查看还缺哪些角色签名。
- `reviewer-trust-template` 或 `examples/reviewer-trust.draft.json` 可生成项目级草稿；
  编辑并 seal/validate 后，`quickstart` / `start` 同时传入 `--reviewer-trust` 和
  `--trust-by`，即可在 Task 1 前自动绑定。高级向导菜单 `16` 提供同一显式入口；
  未选择 Registry 的 Run 保持兼容模式。
- Git 项目的 HEAD、分支、工作区状态与可选测试结果可进入 Evidence。
- 同一 Run 的操作由本机跨进程文件锁串行化，并在每次验证后同步可重建的
  SQLite Checkpoint。
- 未完成 Run 支持带操作人和原因的显式取消；取消事件进入哈希链，重复取消幂等，
  已有研究记录继续可验证。
- 固定提示词的 Ollama 基准已覆盖三个本地模型；基于本轮完整性和谨慎性结果，
  继续使用 `qwen2.5:7b`。主模型与审核模型相同时会明确披露。

仍待后续验证的扩展：

- 为真正跨模型审核补充并基准验证新的合格候选模型。
- 接入远程模型 Provider、Web UI 和跨主体复核。
