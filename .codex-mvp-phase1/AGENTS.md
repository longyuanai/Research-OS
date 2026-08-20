# Research-OS MVP 项目约定

本仓库是隔离的本地实验原型，不是 `Research-OS/FOUNDATION` 的规范实现。修改本仓库
不代表 Foundation、Release、Pack Profile 或治理状态发生变化。

## 边界

- 不在本任务中修改兄弟目录 `Research-OS/FOUNDATION`、`VALIDATION` 或其治理记录。
- 保持恰好 3 个 Task、逐 Task 人工门禁和显式 Reviewer 决定；
  Agent 不代替人类做 `Approved / Changes Requested / Rejected`。
- `workspace/` 含用户 Run 与本地设置。测试使用临时目录，不删除或覆盖真实 Run。
- JSON、Event、Reviewer、Approval、Evidence、Report 与 `HASHES.*` 是权威记录；`.runtime/`
  的锁和 SQLite Checkpoint 只是可重建运行状态。
- Task 返工使用不可变修订 Evidence 覆盖层，不改写原 Evidence、Report 或 Task Report。
- 下游默认内容统一经过有效 Task 输出解析器；只有 Reviewer `Approved` 审查包中的
  最新修订可覆盖原输出，待审修订不得进入查看摘要、交接、最终报告或默认导出。
- 跨多个权威文件的派生视图必须在一次 Run 锁内读取；Effective Output Manifest
  保持确定性、带 Schema 与自身 Hash，不得为生成派生视图而改写 Run 权威产物。
- Reviewer Ed25519 签名是可选附加证明链；不得生成、复制、提交或托管用户私钥，
  只接受显式私钥路径或离线签名，并把签名公钥指纹纳入 Run 完整性与有效输出 Manifest。
- Reviewer 信任策略只能在首次审查/签名前绑定为 Run 级不可变快照；门槛不足的
  `Approved` 不得 `resume` 或进入有效输出。公钥轮换和吊销使用新版注册表与新 Run，
  不回写旧 Run；未绑定策略的旧 Run 必须保持兼容。
- 新 Run 自动绑定必须由调用方显式同时提供已封存 Registry 与绑定操作人；不得从目录中
  猜测或静默启用默认策略。创建期绑定应在同一 Run 锁内、Task 1 执行前进入事件链。
- 所有 Run 读写都经跨进程锁；新增状态必须补完整性不变量和幂等测试。
- Ollama 端点只允许本机回环地址；不得把 Token、密码、私钥或客户数据写入仓库。
- 保持 Python 3.12+ 和标准库优先；未经明确必要性评估不新增生产依赖或更换技术栈。

## 修改与验证

1. 修改前阅读相关实现、测试与 README，保持变更范围最小。
2. 运行 `python -m unittest discover -s tests -v`；状态机改动需覆盖正常、非法、
   幂等、篡改和跨进程场景。
3. 运行适用的 Ruff 错误级检查，并在可用时用 Python 3.12 与 3.14 双版本验证。
4. 完成后报告修改文件、实际测试结果、剩余风险和下一步；不自动提交或发布。

使用入口见 `README.md`，本地 AI 与外部 AI 协作边界见 `AI-USAGE-GUIDE.md`。
