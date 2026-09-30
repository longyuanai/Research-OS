# Research-OS MVP 隔离实验原型

> 这是一个非正式、非 Foundation 实现的本地实验原型。它只用于快速验证产品闭环，
> 不承载 Research-OS Foundation 的正式治理结论。

## 已实现范围

- CLI 读取、严格验证并封存一个 JSON Builder Pack。
- 使用一句中文或英文目标自动识别 8 类场景，收集关键限制并生成 3-Task Pack。
- 提供中文交互向导，覆盖创建、启动、查看、Reviewer 决定、恢复、取消和验证。
- 执行一个恰好包含 3 个 Task 的 Mission。
- 每个 Task 结束后强制暂停，等待正式 Reviewer 做出 `Approved`、
  `Changes Requested` 或 `Rejected`；只有 `Approved` 才允许 `resume`。
- 生成 append-only Event/Reviewer/Approval 哈希链、Evidence、Task Report、研究准备报告、
  `HASHES.json` 与 `HASHES.sha256`。
- 为每个任务生成可直接交给其他 AI 的真实研究指令，要求来源、比较表、
  未知项、验证实验和带条件的推荐。
- 可连接本机 Ollama；第 2 步自动生成中文研究草稿并写入 Evidence 与哈希清单。
- 提供固定提示词的本地模型基准命令，记录耗时、结束原因、输出 Token、完整性检查
  和完整原文；控制台摘要不回显草稿正文。
- 人工审核 AI 草稿时可输入 `R` 记录 `Changes Requested`；初稿、
  修订稿和导致返工的 Reviewer 决定通过 Hash 相互引用。
- Task 1 / Task 3 同样可在 `Changes Requested` 后录入完整修订内容；
  原产物不覆盖，新版以 `task_output_revision` Evidence 不可变保留。
- 提供统一的“有效 Task 输出”解析器；查看、AI 交接、Mission Report 默认视图和
  Obsidian 导出只提升已进入 `Approved` 审查包、且满足已绑定 Reviewer 信任策略的
  最新修订，待审稿或门槛不足版本仍作为审计 Evidence 保留。
- 有效输出可生成确定性的版本化 JSON Manifest，绑定 Run 的 `HASHES.json`、Reviewer
  链尾和每个 original/effective 产物 Hash；所有消费入口在同一把 Run 锁内读取一致快照。
- Reviewer 决定可选附加 OpenSSH Ed25519 身份签名；签名形成独立 append-only 链，
  有效输出、交接、查看和导出显示签名身份及公钥指纹，旧的纯 Hash Run 保持兼容。
- 可把自校验的 Reviewer 信任注册表绑定到首次审查前的 Run；注册表声明
  `fingerprint → identity / role`、有效期、吊销时间和按 Task/决策/角色计算的最少
  不同公钥签名数。门槛不足的 `Approved` 保持待签名状态，不能 `resume`，也不会进入
  有效输出、AI 交接、最终报告或默认导出。
- 提供版本化的项目级 Registry 草稿模板；`quickstart`、`start` 和高级向导可在创建
  新 Run 时显式选择已封存 Registry，并在 Task 1 执行前自动写入不可变策略快照。
- 支持导入 PDF、保存的网页、数据手册、文本与代码目录；只读提取内容并记录
  原文件 Hash，不执行导入的代码。
- 支持第二 AI 审计角色和版本对比；使用同一模型时会明确披露，不冒充独立主体。
- 可把已验证 Run 导出为 Obsidian 不可变快照，或在第 2 步把 Git 状态与可选测试
  结果写入 Evidence。
- 支持不同 CLI 进程从已持久化的人工门禁状态继续；已完成的 Mission 重复
  `resume` 不产生新事件。
- 未完成的 Run 可由明确的人工作用者填写原因后取消；取消是可验证的终态，保留
  已有 Evidence、Report、Reviewer、Approval 和事件链，重复 `cancel` 不产生新事件。
- 对同一个 Run 的读取和状态变更使用本机跨进程独占锁，避免并发批准、恢复或
  Evidence 写入互相覆盖。
- 每次完整性验证成功后同步 SQLite Checkpoint；JSON/Event/Evidence/Report 仍是
  权威记录，检查点可删除并从老 Run 自动重建。
- `verify` 可独立复算 Pack、Run、Evidence、Report 与日志完整性。
- 可按 Task 保存经人工确认的 Claim-Evidence 映射；Claim 原文、当前 Task 输出
  版本、Evidence 引用与集合 Hash 纳入 `verify`，`claims` 命令只读显示统计与记录。

## 范围外

- Web UI、API 服务、多租户、计费和组织权限。
- 插件市场、MCP、浏览器联网研究、远程模型 API 和复杂模型编排。
- Pack 中的任意代码、命令、路径或网络地址执行。
- Foundation 正式 Schema 的 Markdown + YAML Front Matter 完整实现。
- 内建 CA、自动私钥托管、联网证书吊销服务或组织级密钥目录同步。

## 环境

- Python 3.12
- 核心流程零第三方运行依赖；PDF 导入可选使用 `pypdf`
- Git 快照需要本机 `git`；Obsidian 导出需要一个已有 `.obsidian` 的 Vault
- 可选 Reviewer/Manifest Ed25519 签名需要本机 OpenSSH `ssh-keygen`；未启用签名时不需要

Codex 桌面环境中可使用：

```powershell
$MvpPython = '$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

## 傻瓜式操作：直接双击

打开项目文件夹，双击 [双击这里开始.cmd](双击这里开始.cmd)，然后：

1. 输入数字 `1`，开始一个新任务。
2. 用一句话说明想完成的事情。
3. 按提示逐项补充预算、数量、供电、联网和环境；不适用时直接回车。
4. 检查汇总内容，输入 `Y` 确认创建，或输入 `R` 重新填写。
5. 查看第 1 步结果；输入 `Y` 记录 `Approved`，`R` 记录
   `Changes Requested`，`X` 记录 `Rejected`。
6. 系统进入第 2 步后自动调用本地 AI；调用失败且尚无草稿时可按 `A` 显式重试，
   系统不会自动循环重试。`R` 会先封存 Reviewer 意见，再让 AI 返工并将新 Evidence
   链回该决定。
7. 第 3 次批准后，系统自动完成、检查记录并生成 AI 研究指令。

中途直接回车或关闭窗口，任务仍保存在 `workspace`。下次双击后输入 `2`，
即可自动继续最近一次任务。启动文件会依次寻找项目虚拟环境、Codex 自带 Python、
Windows `py` 和系统 `python`，无需手动填写 Python 路径。

主菜单输入 `5` 可再次查看给 AI 的研究指令。文件保存在
`workspace/handoffs/`，文件名含指令内容 Hash，修订前后版本可并存。当前三步流程完成代表“研究范围和证据结构已经建立”，
不代表候选方案已经完成真实比较；报告会明确显示决策就绪度。

Reviewer 提示接收 `Y`、`R`、`X`、`N` 或空行；第 2 步还支持 `F` 导入、`V` 审计，
以及在本地 AI 已配置且尚无草稿时显示的 `A` 重试。无草稿时按 `V` 会说明是尚未调用
还是本次调用已经失败，并提示重试、导入或直接批准。对第 2 步选 `R`
会自动触发 AI 返工；其他步骤会继续询问完整修订内容，也可输入
`@UTF-8文件路径` 导入。直接回车则只保存 Reviewer 决定并继续暂停。
误输入要求、文件路径或“执行 Research-OS”
时，程序会保留当前页面并说明正确位置。主菜单输入 `6` 可查看支持的问题类型。
“执行 Research-OS……”和 AI 研究指令文件路径应发送到 Codex 或其他 AI 对话，
而不是粘贴在这个本地菜单里。

常用扩展入口：

- 输入 `8`：导入 PDF、网页文件、数据手册、文本或代码目录。
- 输入 `10`：比较 AI 初稿、返工稿和审计意见的版本历史。
- 输入 `12`：把上次任务导出到 Obsidian；同一 Run 的不同状态使用不同 Hash 目录。
- 输入 `13`：在第 2 步导入 Git 项目快照。检测到测试命令后，只有输入精确的
  `RUN` 才会执行项目代码；直接回车只采集 Git 状态。

## 命令行用法（可选）

### 简易中文模式

```powershell
cd "<Research-OS 仓库目录>\.codex-mvp-phase1"
& $MvpPython -m research_os_mvp easy --workspace .\workspace
```

### 一句话生成并启动

```powershell
& $MvpPython -m research_os_mvp quickstart `
  "比较 Python、TypeScript 和 Rust，选择适合本地 AI 工具的技术栈" `
  --workspace .\workspace
```

该命令会：

1. 自动识别为“技术选型”。
2. 在 `workspace/packs/` 生成一个经过验证的 Pack。
3. 在 `workspace/runs/` 创建 Run。
4. 执行 Task 1 后停在人工批准点。

自然语言分类使用本地确定性规则和模板；配置 Ollama 后，第 2 步会调用本地模型
生成待复核草稿。它会明确标记“评估框架不是事实结论”，便于后续加入真实来源。
原来的 `wizard` 命令保留为
高级菜单，可处理 Pack 路径、单独批准、单独恢复和完整记录查看。高级菜单输入
`14` 可显式选择三种 Reviewer 决定，`15` 可在 Changes Requested 后
录入通用 Task 产物修订版。输入 `13` 并精确键入 `CANCEL`，
再填写操作人和原因，可操作性取消未完成 Run；它不等于 Reviewer 驳回。

## 8 类自然语言场景

```powershell
& $MvpPython -m research_os_mvp categories
```

| 场景 | `--category` | 典型用途 |
|---|---|---|
| 技术选型 | `technology-selection` | 比较 Python、TypeScript、Rust 或框架 |
| 项目决策 | `project-decision` | 记录采用、延后或放弃原因 |
| 学习研究 | `learning-research` | 将资料、理解和结论组织成证据链 |
| 项目验收 | `project-acceptance` | 逐项核对需求、测试和剩余风险 |
| 安全审计 | `security-audit` | 记录资产、边界、检查证据和风险 |
| 硬件选型 | `hardware-selection` | 比较主控、传感器、通信和供电 |
| 内容核查 | `content-verification` | 保存原始来源、交叉证据和反证 |
| AI 工作监督 | `ai-supervision` | 让 AI 每个 Task 后暂停并等待人工批准 |

给 Codex、Claude Code、ChatGPT、Gemini 等工具的可复制提示词见
[AI-USAGE-GUIDE.md](AI-USAGE-GUIDE.md)。

## 快速演示

### 1. 验证 Pack

```powershell
& $MvpPython -m research_os_mvp validate .\examples\builder-pack.json
```

### 2. 创建 Run，执行 Task 1 并暂停

```powershell
& $MvpPython -m research_os_mvp start .\examples\builder-pack.json `
  --runs-dir .\demo-runs --run-id run-local-demo
```

### 3. 人工批准 Task 1，恢复后执行 Task 2

```powershell
& $MvpPython -m research_os_mvp approve .\demo-runs\run-local-demo `
  --by "Independent Human Operator" --note "Task 1 checked"
& $MvpPython -m research_os_mvp resume .\demo-runs\run-local-demo
```

### 4. 对 Task 2 和 Task 3 重复批准/恢复

```powershell
& $MvpPython -m research_os_mvp approve .\demo-runs\run-local-demo `
  --by "Independent Human Operator" --note "Task 2 checked"
& $MvpPython -m research_os_mvp resume .\demo-runs\run-local-demo

& $MvpPython -m research_os_mvp approve .\demo-runs\run-local-demo `
  --by "Independent Human Operator" --note "Task 3 checked"
& $MvpPython -m research_os_mvp resume .\demo-runs\run-local-demo
```

### 5. 查看状态并独立验证哈希

```powershell
& $MvpPython -m research_os_mvp status .\demo-runs\run-local-demo
& $MvpPython -m research_os_mvp verify .\demo-runs\run-local-demo
```

## CLI

```text
python -m research_os_mvp create "<一句话目标>" [--category auto]
python -m research_os_mvp quickstart "<一句话目标>" --workspace <dir> [--reviewer-trust <registry.json> --trust-by <actor>]
python -m research_os_mvp categories
python -m research_os_mvp easy --workspace <dir>
python -m research_os_mvp wizard --workspace <dir>
python -m research_os_mvp validate <pack.json>
python -m research_os_mvp start <pack.json> --runs-dir <dir> [--run-id <id>] [--reviewer-trust <registry.json> --trust-by <actor>]
python -m research_os_mvp reviewer-trust-template --output <draft.json>
python -m research_os_mvp seal-reviewer-trust <draft.json> --output <registry.json>
python -m research_os_mvp validate-reviewer-trust <registry.json>
python -m research_os_mvp bind-reviewer-trust <run-dir> <registry.json> --by <actor>
python -m research_os_mvp reviewer-trust-status <run-dir>
python -m research_os_mvp approve <run-dir> --by <human> [--note <text>]
python -m research_os_mvp review <run-dir> --by <human> --decision <approved|changes-requested|rejected> [--note <text>]
python -m research_os_mvp sign-review <run-dir> --identity <id> --key <private-key> --public-key <public-key> [--review-hash <hash>]
python -m research_os_mvp review-signing-request <run-dir> --identity <id> --public-key <public-key> --output <payload> [--review-hash <hash>]
python -m research_os_mvp attach-review-signature <run-dir> --identity <id> --public-key <public-key> --signature <signature> [--review-hash <hash>]
python -m research_os_mvp revise <run-dir> --by <human> --review-hash <hash> --note <text> (--content <text> | --content-file <path>)
python -m research_os_mvp resume <run-dir>
python -m research_os_mvp cancel <run-dir> --by <human> --reason <text>
python -m research_os_mvp status <run-dir>
python -m research_os_mvp show <run-dir>
python -m research_os_mvp verify <run-dir>
python -m research_os_mvp claims <run-dir>
python -m research_os_mvp effective-outputs <run-dir>
python -m research_os_mvp verify-effective-manifest <manifest.json>
python -m research_os_mvp sign-effective-manifest <manifest.json> --identity <id> --key <private-key> --public-key <public-key> --output <attestation.json>
python -m research_os_mvp verify-effective-manifest-signature <manifest.json> <attestation.json>
python -m research_os_mvp configure-ollama --workspace <dir> --model qwen2.5:7b [--review-model qwen2.5:7b] [--health-timeout-seconds 60] [--stream-idle-timeout-seconds 60] [--generation-budget-seconds 900] [--max-output-tokens 1536]
python -m research_os_mvp ollama-status --workspace <dir>
python -m research_os_mvp benchmark-ollama --workspace <dir> --model qwen3:1.7b --model qwen2.5:3b-instruct-q4_K_M --model qwen2.5:7b [--output <report.json>]
python -m research_os_mvp export-obsidian <run-dir> <vault-dir>
python -m research_os_mvp git-snapshot <run-dir> <repo-dir> [--run-tests]
python -m research_os_mvp checkpoint-status <run-dir>
```

`git-snapshot --run-tests` 是显式执行授权：它会运行自动检测到的 Python、npm、
Cargo 或 Go 测试入口，并把命令、输出和结果一并写入 Evidence。不加该参数时只读取
HEAD、分支、`git status`、`git diff --stat` 和 `git diff --check`。

`checkpoint-status` 读取最近一次已验证的 SQLite 快照；
`canonical_alignment` 为 `matches` 表示当前 `state.json` 和 `HASHES.json` 仍与快照
一致，为 `differs` 则表示当前权威文件已经变化或损坏，需要再运行 `verify` 定位。
旧的 `research-os-mvp-checkpoint/0.1` / `0.2` 会在下次成功验证时就地升级到 `0.3`，
并补入 Reviewer 与 Reviewer Signature 链的末尾 Hash 和记录数；权威 JSON 产物不会因此改写。

`effective-outputs` 输出 `research-os-mvp-effective-outputs/0.2` JSON Manifest，并继续接受
旧的 `0.1` Manifest 做离线验证。
它是由已验证 Run 确定性计算的只读接口，不写回 Run；同一权威快照重复调用得到相同
`manifest_sha256`。Obsidian 快照会保存 `Effective Output Manifest.json`，供未来 UI、
API 或签名工具直接消费；`verify-effective-manifest` 可脱离原 Run 复算其自身 Hash、
输出数量、Approved 数量和逐 Task 产物 Hash 结构。

Reviewer 身份签名是可选增强层。`sign-review` 只把私钥路径交给 OpenSSH，不读取、复制
或写入私钥；Run 只保存规范化公钥、公钥指纹、签名和被签 Review Hash。更严格的离线
流程可先用 `review-signing-request` 输出确定性载荷，在隔离设备签名后用
`attach-review-signature` 验证并追加。Effective Output Manifest 可生成独立 attestation，
使用 `verify-effective-manifest-signature` 脱离 Run 验证。

需要把“签名有效”提升为“指定角色可信”时，先准备不含私钥的草稿 JSON，运行
`seal-reviewer-trust` 规范化公钥、计算指纹并加入 `registry_sha256`，再用
`validate-reviewer-trust` 检查。`bind-reviewer-trust` 只能在首次 Reviewer 决定或签名前、
且 Run 停在第一个人工门禁时执行；绑定后策略快照进入 `HASHES.json`，不能静默替换。
`reviewer-trust-status` 会列出每个 Review 已满足和仍缺少的角色签名。示例草稿：

```json
{
  "schema_version": "research-os-mvp-reviewer-trust/0.1",
  "registry_id": "project-reviewers",
  "version": 1,
  "keys": [
    {
      "identity": "alice@example",
      "role": "reviewer",
      "public_key": "ssh-ed25519 AAAA...",
      "valid_from": "2026-01-01T00:00:00Z",
      "valid_until": "2027-01-01T00:00:00Z"
    }
  ],
  "requirements": [
    {
      "task_id": "*",
      "decision": "Approved",
      "role": "reviewer",
      "minimum_signatures": 1
    }
  ]
}
```

仓库内置 [项目级草稿模板](examples/reviewer-trust.draft.json)，也可生成一份独立副本：

```powershell
python -m research_os_mvp reviewer-trust-template `
  --output .\reviewer-trust.draft.json
# 编辑 identity / role / public_key / 有效期 / requirements 后：
python -m research_os_mvp seal-reviewer-trust `
  .\reviewer-trust.draft.json `
  --output .\reviewer-trust.registry.json
python -m research_os_mvp validate-reviewer-trust `
  .\reviewer-trust.registry.json
```

同一份已封存的项目级 Registry 可复用于多个新 Run。自动绑定必须显式同时提供策略文件
和绑定操作人；缺少任一参数都会停止创建：

```powershell
python -m research_os_mvp quickstart "核对项目验收证据" `
  --workspace .\workspace `
  --reviewer-trust .\reviewer-trust.registry.json `
  --trust-by "Project Owner"

python -m research_os_mvp start .\examples\builder-pack.json `
  --runs-dir .\workspace\runs `
  --reviewer-trust .\reviewer-trust.registry.json `
  --trust-by "Project Owner"
```

创建期绑定发生在同一把 Run 锁内：`run_created` 后立即写入策略快照和绑定事件，再执行
Task 1。高级向导菜单 `16` 提供对应的显式 Registry 启动入口。未传这两个参数时，
新 Run 保持未绑定的兼容行为。

`task_id` 可使用精确 Task ID 或 `*`。同一 Review 上同一公钥只计一次；门槛按角色和
不同 fingerprint 计算。`revoked_at` 起（含该时刻）附加的签名不再计入门槛；
`valid_from` 前或 `valid_until` 后的签名同样只保留审计、不产生推进权限。未绑定注册表的
旧 Run 保持原行为：密码学签名可验证，但不强制门槛。

Reviewer 决定语义：

| 决定 | Run 结果 | 后续动作 |
|---|---|---|
| `Approved` | `approved_pending_resume` | 生成关联 Approval；若绑定信任策略，签名门槛满足后才允许 `resume` |
| `Changes Requested` | 保持 `paused` | 保留意见；AI 返工或通用修订 Evidence 链回该决定后重新审查 |
| `Rejected` | `rejected` | 独立终态，保留产物，不允许 `resume` 或用 `cancel` 覆盖 |

`approve` 保留为兼容入口，内部会创建正式 `Approved` Reviewer 决定。
`Changes Requested` 和 `Rejected` 必须有审查意见；对相同审查包重复提交完全相同的
返工或驳回决定是幂等操作，不追加新记录。

有效输出规则：原始 Task Report 输出是默认基线；`task_output_revision` 或 `ai_draft`
只有被 `Approved` Reviewer 决定的 `latest_revision_id` 引用、该决定满足已绑定的
Reviewer 信任策略，且适用的 Claim 门禁通过后，才成为下游默认版本。
仅录入修订、导入来源或收到 `Changes Requested` 都不会提前切换。`show` 会先展示
有效输出，再展示完整原始 Evidence / Report；最终报告和导出也保留原版供对照。

`cancel` 不删除任何产物。它追加 `run_cancelled` 事件，保存取消人、原因、时间和
取消前状态，然后将 Run 置为 `cancelled`。该终态不可 `resume`；再次执行
`cancel` 只返回已验证状态，不改写 Event 或 Hash。

Ollama 生成固定关闭思考输出，默认最多生成 1536 Token，并保存 `done_reason`、
`eval_count` 和截断状态。生成响应使用 NDJSON 流式传输，不再等待整段内容
完成后才返回。`benchmark-ollama` 只将完整报告写入指定文件；其自动门槛
检查结构、未知项、验证计划、结束状态和无来源精确数值，不等于事实正确性评测。

## 本地模型基准与默认策略

2026-08-09 在当前本机 Ollama/Vulkan 环境使用同一硬件选型提示词实测：

| 模型 | 耗时 | 自动分数 | 门槛结果 | 主要原因 |
|---|---:|---:|---|---|
| `qwen3:1.7b` | 13.438 秒 | 90 | 未通过 | 输出无来源的精确内存等数值 |
| `qwen2.5:3b-instruct-q4_K_M` | 16.078 秒 | 90 | 未通过 | 输出无来源的精确价格等数值 |
| `qwen2.5:7b` | 32.578 秒 | 100 | 通过 | 完整结束且未触发精确数值门槛 |

因此当前继续使用 `qwen2.5:7b` 作为主模型和审核模型；审核 Evidence 会明确披露
它与主模型相同，暂不声称独立交叉验证。完整基准报告保存在
`workspace/benchmarks/OLLAMA-BENCHMARK-20260809-three-models-v3.json`。这是一组单提示词、
单次运行结果，只用于当前本机的默认策略，不代表通用模型排名。

## Run 产物

```text
<run-id>/
├── pack.snapshot.json
├── state.json
├── events.jsonl
├── approvals.jsonl           # 首次批准后出现
├── reviews.jsonl             # 首次正式 Reviewer 决定后出现
├── review-signatures.jsonl   # 首次附加 Reviewer Ed25519 签名后出现
├── reviewer-trust.snapshot.json # 可选；首次审查前绑定的自校验信任策略
├── evidence/
│   └── EVID-*.json
├── claims/                    # 可选；经人工确认后出现
│   └── CLAIMS-<task-id>.json
├── reports/
│   ├── TASK-REPORT-*.json
│   └── REPORT-MISSION-*.md
├── .runtime/                 # 可重建的本地运行状态，不属于权威 Evidence
│   ├── run.lock
│   └── checkpoint.sqlite3
├── HASHES.json
└── HASHES.sha256
```

给 AI 的交接指令位于 Run 目录外：

```text
workspace/handoffs/AI-RESEARCH-<run-id>-<content-hash-8>.md
```

`events.jsonl`、`reviews.jsonl` 和 `approvals.jsonl` 中每条记录都包含上一条记录的 Hash。
Reviewer 记录还封存当时 Task 输出、补充 Evidence 引用与整体审查包 Hash。
Reviewer Signature 记录逐条绑定 Review Hash、签名身份、公钥指纹、载荷 Hash 和
OpenSSH 签名；签名链尾由 `state.json` 锚定并进入 `HASHES.json`。
Task 产物修订版作为 `EVID-SUPPLEMENTAL-*.json` 保存，`revision_of` 从原产物
逐版指向上一版，`review_decision_hash` 指向导致修订的 Reviewer 决定。
有效输出解析器逐个 Task 复核这些引用、Run 完整性和 Reviewer 签名门槛，并返回原始
输出或最新策略合格的 Reviewer-Approved 修订；它是派生视图，不改写任何权威产物。
查看、AI 交接和导出会一次性在 Run 锁内读取 Pack、Reviewer、Evidence、Report 和
有效输出 Manifest，随后使用内存快照渲染，避免并发审核造成跨版本混合。
`HASHES.json` 则封存当前 Run 的所有权威文件；`.runtime/` 是可重建的运行辅助目录，
不进入 Hash 清单。首次对旧 Run 执行 `status` 或 `verify` 会自动创建检查点。
Claim 工件是 Run 的可选权威 JSON，每个 Task 最多一份；缺少 `claims/` 的旧 Run
仍可验证，但 `claims_confirmed` 为 `false`。当前进度为 C1 + C2-S5：模型、存储、
完整性验证、只读查看、按 Task 统计的确认覆盖、Claim 引用覆盖率，以及
按 Run 显式启用的 pending-Task `resume` 与 effective output 门禁。`approve` 本身
仍只记录 Reviewer 决定，不执行 Claim 门禁。
对同一 Task 重新确认会更新当前 Claim 工件，并在 Event 链中保留前后工件 Hash、
Claim 集合 Hash 和源输出 Hash；因输出修订而失效的绑定可由该存储 API 重新确认。

### Claim 覆盖判据（C2-S2）

`claims_coverage_status` 报告**已执行 Task** 的确认覆盖情况。分母取
`state.executed_tasks`（Run 状态中经"有序前缀"不变式校验的权威列表），
不是 Pack 声明的全部 Task —— 否则只跑完 Task 1 的 Run 会因为 Task 2/3 尚未执行
而永远判为未覆盖。

四个 Task 分类互不重叠，只有第一类满足覆盖：

| 分类 | 含义 |
|---|---|
| `tasks_confirmed` | 有 Claim 工件、至少一条 Claim、且绑定当前输出 |
| `tasks_with_empty_claims` | 有工件但确认了零条 Claim |
| `tasks_with_stale_claims` | 有工件但绑定到已被取代的 Task 输出 |
| `tasks_missing_claims` | 已执行但完全没有 Claim 工件 |

`claims_confirmed` 是**聚合**布尔值，三个 Task 只确认一个也会为 `true`；
判断"是否全部已执行 Task 都已确认"必须使用 `all_executed_tasks_confirmed`。

**陈旧绑定的归类。** 输出修订后 Claim 自然失效，这是正常工作流，不是 Run 损坏。
但 `verify` 保持 C1 的严格行为，仍将陈旧绑定报为完整性错误；
真正的产物篡改由 `HASHES.json` 独立检测，不依赖这一项。
`claims_coverage_status` 在遇到陈旧绑定时不会崩溃，而是降级为
`integrity: "stale-claims"` 并列出需要重新确认的 Task —— 因为此时操作者最需要
知道的恰恰是“哪个 Task 要重做”。其他任何完整性错误仍会正常抛出。

### Claim 引用覆盖率（C2-S3）

`claims_coverage_status` 的 Schema 现为
`research-os-mvp-claims-coverage/0.2`，在 S2 的 Task 确认四分类之外增加两个不同分母的
纯计算指标：

| 字段 | 分母 | 含义 |
|---|---|---|
| `fact_coverage` | `kind == verifiable_fact` | 其中 `support != unsupported` 的比例 |
| `all_coverage` | 全部 Claim | 其中 `support != unsupported` 的比例 |

计算以经验证的 `support` 字段为准，不重新根据 `evidence_ids` 是否为空推测。
没有 `verifiable_fact` 时 `fact_coverage` 为 `null`；完全没有 Claim 时两个覆盖率均为
`null`，不把“没有可评估对象”写成 100%。

`hard_gate_pass` 是“`verifiable_fact` 中没有 `unsupported`”的派生谓词；
`interpretation` / `recommendation` / `assumption` 中的 `unsupported` 不会使它变为
`false`。它在 S3 **不是运行时门禁**，也不改变 `approve`、`resume`、effective output、
handoff 或导出。无 Claim 时该谓词为 `true`，但 Task 仍由
`all_executed_tasks_confirmed: false` 表示尚未确认；后续门禁必须组合两者，不得只看该谓词。

`unsupported_claim_count` 仍统计所有 kind 的 unsupported Claim，语义未改；
`unsupported_fact_count` 是 S3 新增的事实子集计数。输出同时显示完整 `kind_counts`，
用于暴露将事实改标为其他 kind 的规避空间。

### Claim 引用硬门禁（C2-S4）

门禁是 Run 级显式绑定，默认关闭。两个入口都需要明确 actor，并把
`claims_gate_enabled`、`claims_gate_from_task_index` 写入 `state.json`，同时追加
`claims_gate_bound` Event：

```python
create_run(
    pack_path,
    runs_dir,
    claims_gate_enabled=True,
    claims_gate_actor="Claims Policy Admin",
)
bind_claims_gate(run_dir, actor="Claims Policy Admin")
```

创建期绑定从 Task 1 生效。已有 Run 在人工门禁处首次绑定时，当前 pending
Task 已在绑定前执行，因此从下一个 Task 生效；已执行或已批准的 Task
不会被倒查。绑定只能从关闭变为开启，Event 与生效 Task 索引会在
`verify` 中交叉校验；缺少 S4 字段的旧 Run 按未启用处理。

仅当 Run 门禁已启用且已到生效 Task 时，`resume` 才检查
`state.pending_task_id`。该 Task 必须同时满足：

1. 有非空 Claim 确认记录；
2. `hard_gate_pass` 为 `true`，即没有 unsupported `verifiable_fact`；
3. `fact_coverage` 不为 `null`，即至少标注一条 `verifiable_fact`。

计算复用 S3 的 `support` 判定，不使用全部已执行 Task 的
`all_executed_tasks_confirmed`。S4 的推进检查只位于 `resume`；`approve` 不变。
未启用门禁的 Run 不读取这三个条件，因而继续保持 S4 前的 `resume` 行为。

### Claim 门禁与有效输出（C2-S5）

effective output 解析器沿用同一个 Run 级开关和零基
`claims_gate_from_task_index`。只有 Task 索引达到生效点时，Reviewer-Approved 修订
才额外要求该 Task 同时满足非空 Claim、至少一个 `verifiable_fact`，且没有
unsupported `verifiable_fact`。创建期绑定从 Task 1 生效；晚绑定只影响其声明的未来
Task，不倒查更早 Task。CLI、handoff、Obsidian export 和 wizard 均消费同一个
Effective Output Manifest，因此门禁结果一致。

S5 采用“回退 original”语义：Claim 门禁不合格只阻止修订版提升，Task 仍保留在结果
列表中，`source` 保持 `"original"`；其形状与 Reviewer 信任不足时一致。代价是 original
本身可能没有经过 Claim 确认；需要“未确认即不展示”的消费者应同时读取独立的
`claims_coverage_status`，而不能把 Task 从共享 manifest 中删除。

为保持既有签名兼容，S5 不把 Claim 状态加入 manifest 的 `outputs`，不升级
`research-os-mvp-effective-outputs/0.2`，也不改签名载荷。未启用门禁的 Run 不进入
Claim 评估分支，其 effective outputs、`manifest_sha256` 与既有 detached attestation
保持逐位兼容；Claim 状态继续由独立只读接口报告。

## UX-01：首次真实使用提示层改进（2026-08-20）

本轮只调整简易向导的控制台提示与 `render_easy_review()` 展示：第 2 步在本地 AI
未配置或自动草稿关闭时明确说明当前内容是通用模板；Evidence 在审查视图中标注模板、
本地 AI、用户输入和导入资料来源；完成后说明 handoff 文件用于交给能联网的 AI 做真实
研究，以及研究结果的导入入口。没有修改 Evidence、Report、Pack 的持久化内容或哈希，
也没有改变 Task 状态机、Reviewer 决定、Claims gate、Reviewer trust 或 effective output
行为。

## UX-02：本地 AI 调用链修复（2026-08-20）

Ollama 健康检查使用独立的 `health_timeout_seconds`，默认 60 秒；这比 UX-02 时
默认 300 秒的整次生成等待短，避免服务不可用时让界面等待五分钟，同时给本机
服务和模型冷启动留出余量。
旧 `settings.json` 缺少该字段时自动使用默认值。`configure-ollama` 可通过
`--health-timeout-seconds` 设置。UX-03 之后，生成超时由块间空闲上限和总预算
取代；`timeout_seconds` 只为旧配置兼容保留，不再作为整次生成的读超时。

第 2 步的自动调用仍只尝试一次，防止失败循环；只有本地 AI 已配置且当前尚无草稿时，
Reviewer 提示才显示 `A 重试 AI`。这是用户显式重试，不改变 `Y/R/X/回车` 的 Reviewer
决定语义，也不修改 Evidence、Report、Pack 或 Run 状态机。

## UX-03：本地 AI 流式生成（2026-08-20）

Ollama 生成由后台守护读取线程逐行接收 NDJSON 数据块，主控制循环拼接
`message.content`。`stream_idle_timeout_seconds` 默认 60 秒，表示两个完整、
非空数据块之间允许的最长静默时间；只要数据持续到达，整次生成可以超过 60 秒。
`generation_budget_seconds` 是独立的硬总时长预算，默认 900 秒。即使底层
`readline()` 一直不返回，主控制循环仍会按时触发进度回调，并在达到总预算时
关闭响应、中止生成，报告已用时间和已接收字符数。旧 `settings.json` 没有
这两个字段时自动使用上述默认值。

交互向导默认每 15 秒显示已用时间和已接收字符数；没有完整数据块到达时也会继续
显示。这些进度文字只通过
`output_fn` 输出到控制台，不进入 Evidence、Report 或 Pack；`AIResponse` 对外字段保持
不变。`configure-ollama` 会说明较大模型可能需要数分钟，若过慢可由用户
重新选择更小模型；它不会自动更换模型或运行基准测试。

## 测试

```powershell
& $MvpPython -m unittest discover -s tests -v
```

旧 Run 回归样本以 `tests/fixtures/legacy-runs.bundle.json` 随测试版本化；测试运行时
在临时目录按 Base64 原字节还原，不依赖被忽略的 `workspace/runs`。因此干净克隆
与开发机本地状态使用同一夹具。

## 已知限制

- 当前 Pack Profile 为实验性 JSON，只支持两个内建操作：
  `record_evidence` 和 `compose_report`。
- 自然语言分类基于关键词和确定性模板；它负责建立工作结构和研究指令。
- 本地 Ollama 没有实时联网能力，自动产物属于分析草稿；可变事实、参数、链接和
  引用仍需导入官方资料或实测结果后核验。
- 三个已安装模型已完成单提示词基准；较小模型更快，但本轮均因无来源精确数值
  未通过自动门槛。`qwen2.5:7b` 仍可能因任务复杂度出现更长等待。
- 当前自动基准主要检查输出完整性与谨慎性，无法替代基于权威资料的事实评测；
  真正跨模型审核仍待新增候选模型后验证。
- Obsidian 导出是本地 Markdown 快照，不会同步远端，也不会改写既有不同内容。
- Git 自动测试只覆盖检测到的一个入口，不等于完整 CI；运行前仍需人工确认。
- 每次进程只处理一个 Task，并在人工门禁处停止。
- `cancelled` Run 当前没有重新打开功能；若目标恢复，应创建新 Run，并把旧 Run
  作为可追溯背景而不是改写旧状态。
- `rejected` Run 同样是不可恢复的 Reviewer 终态；新方向应创建新 Run，
  并引用原驳回决定，而不是把它改成操作性取消。
- Reviewer 信任注册表是 Run 级不可变策略快照，不是联网 CA 或实时吊销服务；绑定后的
  密钥轮换/新增吊销需要创建使用新版注册表的新 Run，并保留旧 Run 作为审计背景。
- 有效期和吊销判断使用进入签名链的 UTC 附加时间；它受 Run 哈希链保护，但不是外部
  可信时间戳机构证明。需要法律级时间证明时仍需额外的 TSA/HSM/组织 PKI。
- 文件锁只协调同一台机器上的进程，不是网络文件系统或分布式锁。
- SQLite 只保存最近一次已验证检查点，不替代 JSON 权威记录，也不提供整组产物的
  自动回滚事务。
- 在 Task 产物生成过程中异常中断仍可能留下完整性失败的 Run；检查点可用于确认
  最近一次已验证状态，但当前不会自动覆盖或回滚权威文件。
