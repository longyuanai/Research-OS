from __future__ import annotations

from pathlib import Path
from typing import Any

from research_os_mvp.errors import RunStateError
from research_os_mvp.integrity import sha256_text, write_text_atomic
from research_os_mvp.runtime import (
    read_effective_run_snapshot,
    verify_effective_output_manifest,
)


def _effective_output_map(
    manifest: dict[str, Any],
) -> dict[str, dict[str, object]]:
    return {
        str(item["task_id"]): item for item in manifest["outputs"]
    }


def _provenance_line(item: dict[str, object]) -> str:
    signatures = item.get("approved_review_signatures")
    signature_text = ""
    if isinstance(signatures, list) and signatures:
        signature_text = "; 签名 " + ", ".join(
            f"{entry['signer_identity']} ({entry['public_key_fingerprint']})"
            + (
                f" [{entry['reviewer_role']}:可信]"
                if entry.get("policy_trusted")
                else (" [未计入策略]" if entry.get("policy_trusted") is False else "")
            )
            for entry in signatures
        )
    if item["source"] == "approved_revision":
        return (
            f"- `{item['task_id']}`：已批准修订 `{item['effective_id']}`，"
            f"Reviewer 决定 `{item['approved_review_id']}` "
            f"(`{item['approved_review_hash']}`){signature_text}"
        )
    approved_text = ""
    if item.get("approved_review_hash"):
        approved_text = (
            f"，Approved 决定 `{item['approved_review_id']}` "
            f"(`{item['approved_review_hash']}`){signature_text}"
        )
    return (
        f"- `{item['task_id']}`：原始 Task 输出 `{item['effective_id']}`"
        f"{approved_text}"
    )


def _trust_summary(manifest: dict[str, Any]) -> str:
    if not manifest.get("reviewer_trust_policy_bound"):
        return "未绑定 Reviewer 信任策略；签名仅做密码学真实性校验。"
    state = "已满足" if manifest.get("reviewer_trust_satisfied") else "未满足"
    return (
        f"注册表 `{manifest['reviewer_trust_registry_id']}` v"
        f"{manifest['reviewer_trust_registry_version']}；签名门槛{state}；"
        f"策略 Hash `{manifest['reviewer_trust_registry_sha256']}`。"
    )


def render_research_handoff(run_dir: Path | str) -> str:
    path = Path(run_dir)
    snapshot = read_effective_run_snapshot(path)
    status = snapshot["status"]
    pack = snapshot["pack"]
    manifest = snapshot["effective_output_manifest"]
    mission = pack["mission"]
    effective = _effective_output_map(manifest)
    task_one = mission["tasks"][0]
    task_two = mission["tasks"][1]
    goal_output = effective.get(task_one["task_id"])
    framework_output = effective.get(task_two["task_id"])
    goal_record = (
        str(goal_output["content"])
        if goal_output is not None
        else task_one["input"]["content"]
    )
    framework = (
        str(framework_output["content"])
        if framework_output is not None
        else task_two["input"]["content"]
    )
    provenance = "\n".join(
        _provenance_line(item)
        for item in (goal_output, framework_output)
        if item is not None
    )
    criteria = "\n".join(f"- {item}" for item in mission["success_criteria"])
    return (
        "# 给 AI 的真实研究执行指令\n\n"
        "你是本任务的研究执行者。请真正收集和比较证据，不要只复述评估框架。\n\n"
        f"## 任务\n\n{mission['title']}\n\n"
        f"## 用户输入\n\n{goal_record}\n\n"
        f"## 评估框架\n\n{framework}\n\n"
        "## 输入版本来源\n\n"
        f"{provenance or '- 尚无已执行 Task，使用 Pack 输入'}\n\n"
        "## Reviewer 信任状态\n\n"
        f"{_trust_summary(manifest)}\n\n"
        "## 执行要求\n\n"
        "1. 先列出缺失条件；缺失条件会改变结论时，明确向用户提问。\n"
        "2. 对每个候选项使用同一组维度比较，保留型号和版本差异。\n"
        "3. 优先使用官方文档、数据手册、实测结果和原始来源。\n"
        "4. 每个可变事实附来源、日期和链接；查不到时标为“未知”。\n"
        "5. 将事实、推断、经验判断和建议分开，不编造参数或引用。\n"
        "6. 给出比较表、主要风险、验证实验和带条件的推荐。\n"
        "7. 结尾列出结论会在什么条件下改变。\n\n"
        "## Research-OS 接受标准\n\n"
        f"{criteria}\n\n"
        "## 返回格式\n\n"
        "- 缺失条件与澄清问题\n"
        "- 候选项比较表\n"
        "- 逐条证据清单（主张、来源、日期、链接、可信度）\n"
        "- 风险和未知项\n"
        "- 推荐方案及适用条件\n"
        "- 最小验证实验\n"
        "- 结论变更条件\n\n"
        f"Run-ID：{status['run_id']}\n"
        f"Effective-Output-Manifest-SHA256：{manifest['manifest_sha256']}\n"
    )


def render_effective_mission_report_from_manifest(manifest: dict[str, Any]) -> str:
    verify_effective_output_manifest(manifest)
    effective = manifest.get("outputs")
    if not isinstance(effective, list):
        raise RunStateError("有效输出 Manifest 缺少 outputs")
    report = next(
        (item for item in effective if item["operation"] == "compose_report"),
        None,
    )
    if report is None:
        raise RunStateError("Run 尚未生成 Mission Report")
    if report["source"] == "approved_revision":
        provenance = (
            f"已批准修订 `{report['effective_id']}`；Reviewer 决定 "
            f"`{report['approved_review_id']}` (`{report['approved_review_hash']}`)"
        )
    else:
        provenance = f"原始 Task 输出 `{report['effective_id']}`"
        if report.get("approved_review_hash"):
            provenance += (
                f"；Approved 决定 `{report['approved_review_id']}` "
                f"(`{report['approved_review_hash']}`)"
            )
    signatures = report.get("approved_review_signatures")
    if isinstance(signatures, list) and signatures:
        provenance += "；Ed25519 签名 " + ", ".join(
            f"{entry['signer_identity']} ({entry['public_key_fingerprint']})"
            + (
                f" [{entry['reviewer_role']}:可信]"
                if entry.get("policy_trusted")
                else (" [未计入策略]" if entry.get("policy_trusted") is False else "")
            )
            for entry in signatures
        )
    return (
        "<!-- Research-OS 有效 Mission Report 派生视图；权威原始产物保持不变。 -->\n\n"
        f"> 有效版本来源：{provenance}\n\n"
        f"> Effective Output Manifest：`{manifest['manifest_sha256']}`\n\n"
        f"> Reviewer 信任：{_trust_summary(manifest)}\n\n"
        f"{str(report['content']).rstrip()}\n"
    )


def render_effective_mission_report(run_dir: Path | str) -> str:
    snapshot = read_effective_run_snapshot(Path(run_dir))
    return render_effective_mission_report_from_manifest(
        snapshot["effective_output_manifest"]
    )


def save_research_handoff(
    run_dir: Path | str,
    workspace: Path | str,
) -> Path:
    path = Path(run_dir)
    prompt = render_research_handoff(path)
    output_dir = Path(workspace) / "handoffs"
    if output_dir.exists() and output_dir.is_symlink():
        raise RunStateError("handoffs 目录不得是符号链接")
    prompt_hash = sha256_text(prompt)[:8]
    output = output_dir / f"AI-RESEARCH-{path.name}-{prompt_hash}.md"
    if output.is_symlink():
        raise RunStateError("AI 研究指令文件不得是符号链接")
    if output.exists():
        current = output.read_text(encoding="utf-8")
        if current != prompt:
            raise RunStateError(f"AI 研究指令 Hash 命名与内容不一致：{output}")
        return output.resolve()
    write_text_atomic(output, prompt)
    return output.resolve()
