# Research-OS · ARCHITECTURE

核实日期：2026-10-15。依据本地README、构建清单和实际入口；本文件不把文档计划当成运行时验收。

## 目标与范围

维护 docs-first/evidence-first 的研究执行治理基线；当前 Foundation RC 不等于生产 Runtime。

GitHub：[longyuanai/Research-OS](https://github.com/longyuanai/Research-OS)。知识笔记：Vault内 `03_Projects/Research-OS/Research-OS - Git关联.md`。

## 组件与代码入口

| 实际路径 | 责任边界 |
| --- | --- |
| [FOUNDATION](FOUNDATION) | 规范基线 |
| [VALIDATION](VALIDATION) | 验证证据 |

## 数据与控制流

以下链路对应README/规范描述；实现覆盖以代码入口和适用验证为准。

```mermaid
flowchart LR
    N0["FOUNDATION规范"]
    N1["治理决策和变更"]
    N2["VALIDATION证据"]
    N0 --> N1
    N1 --> N2
```

## 构建与依赖依据

按README和各子目录清单运行；文档/静态/脚本项目不额外引入构建框架。

## 验证边界

核对治理暂停条件、证据链和审批边界；不把尚未实现的 Runtime、Builder Pack 标为完成。

## 现行依据

- [README.md](README.md)
