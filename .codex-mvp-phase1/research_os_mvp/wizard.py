from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from difflib import unified_diff
from pathlib import Path
from typing import Any

from research_os_mvp.ai import (
    AIResponse,
    AISettings,
    check_ollama,
    generate_research,
    load_ai_settings,
)
from research_os_mvp.claim_candidates import (
    classify_claim_candidates,
    extract_claim_candidates,
    find_ai_draft_policy_violations,
)
from research_os_mvp.errors import IntegrityError, MVPError, RunStateError
from research_os_mvp.exporters import export_run_to_obsidian
from research_os_mvp.git_integration import (
    collect_git_snapshot,
    record_git_snapshot_evidence,
)
from research_os_mvp.handoff import render_research_handoff, save_research_handoff
from research_os_mvp.natural_language import (
    SCENARIO_PROFILES,
    ScenarioProfile,
    context_questions_for,
    create_pack_from_goal,
    list_scenarios,
    resolve_category,
)
from research_os_mvp.pack import load_pack
from research_os_mvp.runtime import (
    approve_run,
    cancel_run,
    claims_coverage_status,
    create_run,
    read_claim_source_snapshot,
    read_effective_run_snapshot,
    record_confirmed_claims,
    record_supplemental_evidence,
    resume_run,
    review_run,
    revise_task_output,
    status_run,
    verify_run,
)
from research_os_mvp.sources import import_local_source

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
AIGenerateFn = Callable[[AISettings, str], AIResponse]


def category_catalog_text() -> str:
    lines = ["可用场景："]
    for index, profile in enumerate(SCENARIO_PROFILES, start=1):
        lines.append(f"{index}. {profile.name_zh} ({profile.key}) - {profile.description}")
        lines.append(f"   例如：{profile.example}")
    return "\n".join(lines)


def easy_question_examples_text() -> str:
    lines = ["可以提问的 8 类任务："]
    for index, profile in enumerate(SCENARIO_PROFILES, start=1):
        lines.append(f"{index}. {profile.name_zh}：{profile.example}")
    lines.extend(
        [
            "",
            "其他问题会按“学习研究”建立任务。",
            "本地模式负责整理目标、限制和证据结构；",
            "需要真实资料和结论时，使用菜单 5 生成 AI 研究指令。",
        ]
    )
    return "\n".join(lines)


def _read_text_limited(path: Path, maximum: int = 1024 * 1024) -> str:
    if path.stat().st_size > maximum:
        raise IntegrityError(f"Artifact exceeds {maximum} bytes: {path}")
    return path.read_text(encoding="utf-8")


def _read_json_object_limited(path: Path, maximum: int = 4 * 1024 * 1024) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RunStateError("Reviewer 信任策略必须是普通 JSON 文件")
    value = json.loads(_read_text_limited(path, maximum))
    if not isinstance(value, dict):
        raise RunStateError("Reviewer 信任策略必须是 JSON 对象")
    return value


def _revision_content_from_input(value: str) -> str:
    entered = value.strip()
    if not entered.startswith("@"):
        return entered
    path_value = entered[1:].strip()
    if (
        len(path_value) >= 2
        and path_value[0] == path_value[-1]
        and path_value[0] in {'"', "'"}
    ):
        path_value = path_value[1:-1].strip()
    revision_path = Path(path_value)
    if revision_path.is_symlink() or not revision_path.is_file():
        raise RunStateError("修订内容路径必须是普通 UTF-8 文件")
    return _read_text_limited(revision_path, maximum=2 * 1024 * 1024).strip()


def inspect_run_artifacts(run_dir: Path | str) -> dict[str, Any]:
    path = Path(run_dir)
    snapshot = read_effective_run_snapshot(path)
    status = snapshot["status"]
    evidence: list[dict[str, Any]] = []
    for item in snapshot["evidence"]:
        value = item["data"]
        evidence.append(
            {
                "path": item["path"],
                "evidence_id": value["evidence_id"],
                "source": value["source"],
                "method": value["method"],
                "content": value["content"],
                "content_sha256": value["content_sha256"],
                "limitations": value["limitations"],
                "evidence_role": value.get("evidence_role"),
                "revision_of": value.get("revision_of"),
                "review_decision_hash": value.get("review_decision_hash"),
            }
        )
    reports = snapshot["reports"]
    reviews = snapshot["reviews"]
    effective_manifest = snapshot["effective_output_manifest"]
    return {
        "status": status,
        "effective_manifest": effective_manifest,
        "effective_outputs": effective_manifest["outputs"],
        "evidence": evidence,
        "reports": reports,
        "reviews": reviews,
        "review_signatures": snapshot["review_signatures"],
        "reviewer_trust_registry": snapshot["reviewer_trust_registry"],
    }


def render_run_artifacts(run_dir: Path | str) -> str:
    inspected = inspect_run_artifacts(run_dir)
    status = inspected["status"]
    lines = [
        f"运行：{status['run_id']}",
        f"状态：{status['status']}",
        f"待批准 Task：{status['pending_task_id'] or '无'}",
        (
            "Reviewer 信任策略："
            + (
                f"{status['reviewer_trust_registry_id']} v"
                f"{status['reviewer_trust_registry_version']}；"
                f"门槛{'已满足' if status['reviewer_trust_satisfied'] else '未满足'}"
                if status["reviewer_trust_policy_bound"]
                else "未绑定（仅校验签名真实性，不限制推进）"
            )
        ),
        f"有效输出 Manifest：{inspected['effective_manifest']['manifest_sha256']}",
        (
            "权威快照 Hash："
            f"{inspected['effective_manifest']['canonical_snapshot_sha256']}"
        ),
        "",
        "=== Effective Task Outputs（默认采用最新 Approved 修订） ===",
    ]
    if not inspected["effective_outputs"]:
        lines.append("尚未生成 Task 输出。")
    for item in inspected["effective_outputs"]:
        source = (
            f"已批准修订；Reviewer 决定 {item['approved_review_id']}"
            if item["source"] == "approved_revision"
            else "原始 Task 输出"
        )
        lines.extend(
            [
                f"\n[{item['task_id']}] {item['task_name']}",
                f"有效产物：{item['effective_id']}",
                f"版本来源：{source}",
                f"内容：\n{item['content'].rstrip()}",
            ]
        )
        if item.get("approved_review_hash"):
            lines.append(f"Approved Reviewer Hash：{item['approved_review_hash']}")
        for signature in item.get("approved_review_signatures", []):
            lines.append(
                "Ed25519 签名："
                f"{signature['signer_identity']} "
                f"({signature['public_key_fingerprint']})"
                + (
                    f"；策略角色 {signature['reviewer_role']}，可信"
                    if signature.get("policy_trusted")
                    else (
                        "；未计入策略门槛"
                        if signature.get("policy_trusted") is False
                        else ""
                    )
                )
            )
    if status.get("latest_review_trust_outstanding"):
        lines.append("\n=== Reviewer Trust Outstanding ===")
        for item in status["latest_review_trust_outstanding"]:
            lines.append(
                f"- 角色 {item['role']}：已有 {item['observed_signatures']}，"
                f"要求 {item['required_signatures']}，还缺 {item['missing_signatures']}"
            )
    lines.append("\n=== Evidence（原始审计记录） ===")
    if not inspected["evidence"]:
        lines.append("尚未生成 Evidence。")
    for item in inspected["evidence"]:
        lines.extend(
            [
                f"\n[{item['evidence_id']}] {item['path']}",
                f"来源：{item['source']}",
                f"方法：{item['method']}",
                f"内容：\n{item['content']}",
                f"限制：{item['limitations']}",
                f"SHA-256：{item['content_sha256']}",
            ]
        )
        if item.get("evidence_role"):
            lines.append(f"角色：{item['evidence_role']}")
        if item.get("revision_of"):
            lines.append(f"修订自：{item['revision_of']}")
        if item.get("review_decision_hash"):
            lines.append(f"Reviewer 决定 Hash：{item['review_decision_hash']}")
    lines.append("\n=== Reviewer Decisions ===")
    if not inspected["reviews"]:
        lines.append("尚未记录正式 Reviewer 决定。")
    for item in inspected["reviews"]:
        lines.extend(
            [
                f"\n[{item['review_id']}] {item['decision']} | {item['task_id']}",
                f"Reviewer：{item['reviewer']}",
                f"意见：{item['note'] or '（无）'}",
                f"审查包 SHA-256：{item['subject']['bundle_sha256']}",
                f"决定记录 Hash：{item['hash']}",
            ]
        )
    lines.append("\n=== Reviewer Ed25519 Signatures ===")
    if not inspected["review_signatures"]:
        lines.append("尚未附加 Reviewer 身份签名（纯 Hash Run 仍有效）。")
    for item in inspected["review_signatures"]:
        lines.extend(
            [
                f"\n[{item['signature_id']}] Review {item['review_id']}",
                f"签名身份：{item['signer_identity']}",
                f"公钥指纹：{item['public_key_fingerprint']}",
                f"载荷 SHA-256：{item['payload_sha256']}",
                f"签名记录 Hash：{item['hash']}",
            ]
        )
    lines.append("\n=== Reports ===")
    if not inspected["reports"]:
        lines.append("尚未生成 Report。")
    for item in inspected["reports"]:
        lines.extend([f"\n--- {item['path']} ---", item["content"].rstrip()])
    return "\n".join(lines)


def _latest_run(workspace: Path) -> Path:
    runs_root = workspace / "runs"
    if not runs_root.is_dir() or runs_root.is_symlink():
        raise RunStateError("还没有任务记录，请先选择“开始一个新任务”")
    candidates = [
        path
        for path in runs_root.glob("run-*")
        if path.is_dir()
        and not path.is_symlink()
        and (path / "state.json").is_file()
    ]
    if not candidates:
        raise RunStateError("还没有任务记录，请先选择“开始一个新任务”")
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def _evidence_for_task(run_dir: Path, task_id: str) -> dict[str, Any]:
    for artifact in sorted((run_dir / "evidence").glob("*.json")):
        value = json.loads(_read_text_limited(artifact))
        if value.get("task_id") == task_id:
            return value
    raise IntegrityError(f"没有找到当前步骤的证据：{task_id}")


def _ai_evidence_for_task(run_dir: Path, task_id: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for artifact in sorted((run_dir / "evidence").glob("*.json")):
        value = json.loads(_read_text_limited(artifact))
        if value.get("task_id") == task_id and value.get("evidence_role") == "ai_draft":
            evidence.append(value)
    return evidence


def _confirm_ai_draft_claims(
    run_dir: Path,
    task_id: str,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> dict[str, Any] | None:
    drafts = _ai_evidence_for_task(run_dir, task_id)
    if not drafts:
        output_fn("当前 Task 没有可抽取 Claim 的本地 AI 草稿。")
        return None
    source_path, source_hash, content = read_claim_source_snapshot(run_dir, task_id)
    source_label = source_path.relative_to(run_dir).as_posix()
    candidates = extract_claim_candidates(content)
    output_fn(
        f"当前 Claim 源：{source_label}；SHA-256：{source_hash}。"
    )
    output_fn(
        f"已用确定性规则抽取 {len(candidates)} 条候选 Claim；未再次调用 AI。\n"
        "草稿正文中的“来源：...”不被信任，也不会转换成 Evidence 引用。\n"
        "所有候选固定从 support=unsupported、evidence_ids=[] 开始。"
    )
    claims = classify_claim_candidates(
        candidates,
        input_fn=input_fn,
        output_fn=output_fn,
    )
    if claims is None:
        return None
    confirmed_by = (
        input_fn("确认人 [Human Owner (Easy Mode)]：").strip()
        or "Human Owner (Easy Mode)"
    )
    recorded = record_confirmed_claims(
        run_dir,
        task_id=task_id,
        expected_source_artifact_sha256=source_hash,
        confirmed_by=confirmed_by,
        confirmed_at=datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        claims=claims,
    )
    coverage = claims_coverage_status(run_dir)
    output_fn(
        f"已通过 record_confirmed_claims 记录 {len(claims)} 条 Claim；"
        f"hard_gate_pass={coverage['hard_gate_pass']}；"
        f"fact_coverage={coverage['fact_coverage']}。"
    )
    return recorded


def _source_evidence_for_task(run_dir: Path, task_id: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for artifact in sorted((run_dir / "evidence").glob("*.json")):
        value = json.loads(_read_text_limited(artifact))
        if (
            value.get("task_id") == task_id
            and value.get("evidence_role") == "imported_source"
        ):
            evidence.append(value)
    return evidence


def _ai_audits_for_task(run_dir: Path, task_id: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for artifact in sorted((run_dir / "evidence").glob("*.json")):
        value = json.loads(_read_text_limited(artifact))
        if value.get("task_id") == task_id and value.get("evidence_role") == "ai_audit":
            evidence.append(value)
    return evidence


def _task_output_revisions_for_task(
    run_dir: Path,
    task_id: str,
) -> list[dict[str, Any]]:
    revisions: list[dict[str, Any]] = []
    for artifact in sorted((run_dir / "evidence").glob("*.json")):
        value = json.loads(_read_text_limited(artifact))
        if (
            value.get("task_id") == task_id
            and value.get("evidence_role") == "task_output_revision"
        ):
            revisions.append(value)
    return revisions


def _display_ai_content(content: str, maximum: int = 12_000) -> str:
    if len(content) <= maximum:
        return content
    return content[:maximum] + "\n\n[屏幕显示已截断；完整内容保存在 Evidence 文件中。]"


def _evidence_source_label(evidence: dict[str, Any]) -> str:
    source = str(evidence.get("source", ""))
    if evidence.get("evidence_role") == "imported_source":
        return "导入的外部资料"
    if source.startswith("template://"):
        return "通用评估框架（模板）"
    if source.startswith("ollama://"):
        return "本地 AI 针对本任务生成的草稿"
    if source.startswith("human://"):
        return "你的输入"
    return "其他 Evidence"


def _local_ai_template_warning(settings: AISettings | None) -> str:
    reason = (
        "本地 AI 尚未配置。"
        if settings is None
        else "本地 AI 已配置，但自动生成研究草稿的功能当前关闭。"
    )
    return (
        "⚠ 第 2 步提示：当前内容是通用评估框架（模板），"
        "不是针对本任务的 AI 分析。\n"
        f"{reason} 如果你希望先获得针对本任务的本地 AI 草稿，"
        "可现在暂停并运行 research-os-mvp configure-ollama。\n"
        "配置后重新开始一个任务即可获得 AI 草稿；也可以知情后继续当前流程。"
    )


def _missing_ai_draft_guidance(*, prior_failure: bool) -> str:
    reason = (
        "此前本地 AI 调用已失败，所以没有生成草稿"
        if prior_failure
        else "本地 AI 尚未调用或尚未生成草稿"
    )
    return (
        f"当前没有可审计的本地 AI 草稿：{reason}。"
        "现在可按 A 重试生成、按 F 导入资料，或按 Y 直接批准通用模板。"
    )


def render_easy_review(run_dir: Path | str) -> str:
    path = Path(run_dir)
    status = verify_run(path)
    pack = load_pack(path / "pack.snapshot.json").data
    tasks = pack["mission"]["tasks"]
    if status["status"] == "completed":
        return (
            "本轮研究准备流程已经完成。\n"
            f"记录：{status['event_count']} 个事件，"
            f"{status['evidence_count']} 份证据，"
            f"{status['report_count']} 份报告。\n"
            "完整性检查：通过。\n"
            "注意：记录闭环完成不等于候选方案已经完成真实比较。"
        )
    if status["status"] == "cancelled":
        return (
            "本轮任务已取消，所有审计记和产物已保留。\n"
            f"取消原因：{status['cancellation_reason']}"
        )
    if status["status"] == "rejected":
        return (
            "当前 Task 已由 Reviewer 正式 Rejected，Run 已终止。\n"
            f"Reviewer：{status['rejected_by']}\n"
            f"驳回原因：{status['rejection_reason']}\n"
            f"决定记录：{status['latest_review_id']}"
        )

    pending_id = status["pending_task_id"]
    task = next(item for item in tasks if item["task_id"] == pending_id)
    task_number = tasks.index(task) + 1
    lines = [
        "",
        "=" * 56,
        f"当前是第 {task_number}/3 步：{task['name']}",
        "请检查下面的内容，再决定是否批准。",
        "-" * 56,
    ]
    if status.get("latest_review_task_id") == pending_id:
        lines.extend(
            [
                f"最新 Reviewer 决定：{status['latest_review_decision']}",
                f"审查意见：{status['latest_review_note'] or '（无）'}",
                "-" * 56,
            ]
        )

    task_output_revisions = _task_output_revisions_for_task(path, pending_id)
    if task_output_revisions:
        latest_task_revision = task_output_revisions[-1]
        lines.extend(
            [
                f"=== Task 产物修订版（第 {len(task_output_revisions)} 版） ===",
                _display_ai_content(latest_task_revision["content"]),
                "",
                f"Evidence：{latest_task_revision['evidence_id']}",
                f"来源类型：{_evidence_source_label(latest_task_revision)}",
                f"修订自：{latest_task_revision['revision_of']}",
                (
                    "Reviewer 决定 Hash："
                    f"{latest_task_revision['review_decision_hash']}"
                ),
                "-" * 56,
                "以下继续保留原始 Task 产物，供对照复核。",
                "",
            ]
        )

    if task["operation"] == "record_evidence":
        evidence = _evidence_for_task(path, pending_id)
        lines.extend(
            [
                evidence["content"],
                "",
                f"来源类型：{_evidence_source_label(evidence)}",
                f"来源：{evidence['source']}",
                f"注意事项：{evidence['limitations']}",
            ]
        )
        imported_sources = _source_evidence_for_task(path, pending_id)
        if imported_sources:
            lines.extend(["", f"=== 已导入原始资料：{len(imported_sources)} 份 ==="])
            for imported in imported_sources:
                lines.append(
                    f"- {_evidence_source_label(imported)} | "
                    f"{imported['source']}（{imported['evidence_id']}，"
                    f"SHA-256 {imported['content_sha256'][:12]}…）"
                )
        ai_drafts = _ai_evidence_for_task(path, pending_id)
        if ai_drafts:
            latest = ai_drafts[-1]
            revision_label = "返工稿" if latest.get("revision_of") else "初稿"
            lines.extend(
                [
                    "",
                    f"=== 本地 AI {revision_label}（第 {len(ai_drafts)} 版，待人工复核） ===",
                    _display_ai_content(latest["content"]),
                    "",
                    f"来源类型：{_evidence_source_label(latest)}",
                    f"来源：{latest['source']}",
                    f"Evidence：{latest['evidence_id']}",
                    f"注意事项：{latest['limitations']}",
                ]
            )
        audits = _ai_audits_for_task(path, pending_id)
        if audits:
            latest_audit = audits[-1]
            lines.extend(
                [
                    "",
                    f"=== AI 审计意见（第 {len(audits)} 版，待人工裁决） ===",
                    _display_ai_content(latest_audit["content"]),
                    "",
                    f"来源类型：{_evidence_source_label(latest_audit)}",
                    f"来源：{latest_audit['source']}",
                    f"Evidence：{latest_audit['evidence_id']}",
                    f"审计对象：{latest_audit.get('revision_of') or '未记录'}",
                    f"注意事项：{latest_audit['limitations']}",
                ]
            )
    else:
        reports = sorted((path / "reports").glob("REPORT-MISSION-*.md"))
        if not reports:
            raise IntegrityError("研究准备报告文件缺失")
        mission = pack["mission"]
        lines.extend(
            [
                "研究准备报告已生成（目前不是选型结论）。",
                f"任务：{mission['title']}",
                f"报告已引用 {status['evidence_count']} 份证据。",
                "当前状态：目标和研究框架已记录，真实资料或测试数据仍待补充。",
                "",
                "完成标准：",
            ]
        )
        lines.extend(f"- {criterion}" for criterion in mission["success_criteria"])
        lines.extend(
            [
                "",
                "完整报告保存在：",
                str(reports[0]),
                "需要全部技术记录时，请在主菜单输入 3。",
                "需要让其他 AI 真正研究时，请在主菜单输入 5。",
            ]
        )

    lines.extend(["-" * 56, "系统记录和哈希检查：通过。"])
    return "\n".join(lines)


def _record_ai_response(
    run_dir: Path,
    response: AIResponse,
    *,
    revision_of: str | None = None,
    review_decision_hash: str | None = None,
) -> dict[str, Any]:
    mode = "根据人工反馈重新生成本地 AI 草稿" if revision_of else "执行研究指令并生成本地 AI 初稿"
    completion = f"；结束原因 {response.done_reason or '未报告'}"
    if response.eval_count is not None:
        completion += f"；输出 Token {response.eval_count}"
    return record_supplemental_evidence(
        run_dir,
        content=response.content,
        source=f"ollama://{response.model}",
        method=f"{mode}；耗时 {response.elapsed_seconds:.3f} 秒{completion}",
        limitations=(
            "本地模型没有实时联网能力；输出是待复核草稿，所含事实、参数、"
            "引用和建议需以导入的原始资料、官方来源或实测结果核验。"
            + (
                "本次输出达到 Token 上限并被截断，必须返工后再批准。"
                if response.truncated
                else ""
            )
        ),
        collected_by=f"Ollama ({response.model})",
        evidence_role="ai_draft",
        revision_of=revision_of,
        review_decision_hash=review_decision_hash,
    )


def _generate_with_progress(
    settings: AISettings,
    prompt: str,
    ai_generate_fn: AIGenerateFn,
    output_fn: OutputFn,
) -> AIResponse:
    if ai_generate_fn is generate_research:
        return generate_research(settings, prompt, progress_fn=output_fn)
    return ai_generate_fn(settings, prompt)


def _automatic_ai_research(
    run_dir: Path,
    settings: AISettings,
    ai_generate_fn: AIGenerateFn,
    output_fn: OutputFn,
) -> dict[str, Any]:
    prompt = render_research_handoff(run_dir)
    response = _generate_with_progress(settings, prompt, ai_generate_fn, output_fn)
    return _record_ai_response(run_dir, response)


def _import_source_to_run(run_dir: Path, dropped_path: str) -> dict[str, Any]:
    imported = import_local_source(dropped_path)
    return record_supplemental_evidence(
        run_dir,
        content=imported.content,
        source=imported.source,
        method=imported.method,
        limitations=imported.limitations,
        collected_by="Human Owner (Local Source Import)",
        evidence_role="imported_source",
    )


def _record_ai_audit_response(
    run_dir: Path,
    response: AIResponse,
    *,
    audited_evidence_id: str,
    researcher_model: str,
) -> dict[str, Any]:
    same_model = response.model == researcher_model
    independence = "同一模型分角色复核" if same_model else "不同模型交叉复核"
    completion = f"；结束原因 {response.done_reason or '未报告'}"
    if response.eval_count is not None:
        completion += f"；输出 Token {response.eval_count}"
    return record_supplemental_evidence(
        run_dir,
        content=response.content,
        source=f"ollama://{response.model}",
        method=(
            f"{independence}；研究模型 {researcher_model}；审计模型 {response.model}；"
            f"耗时 {response.elapsed_seconds:.3f} 秒{completion}"
        ),
        limitations=(
            "AI 审计只提供第二视角，不构成人工批准。"
            + (
                "研究者与审计者使用同一模型，角色隔离不等于模型独立性。"
                if same_model
                else "两个本地模型仍可能共享训练偏差，关键主张需原始资料核验。"
            )
            + (
                "本次审计达到 Token 上限并被截断，不应作为完整审计意见。"
                if response.truncated
                else ""
            )
        ),
        collected_by=f"Ollama Audit ({response.model})",
        evidence_role="ai_audit",
        revision_of=audited_evidence_id,
    )


def _audit_ai_research(
    run_dir: Path,
    settings: AISettings,
    ai_generate_fn: AIGenerateFn,
    output_fn: OutputFn,
) -> dict[str, Any]:
    drafts = _ai_evidence_for_task(
        run_dir,
        "TASK-LOCAL-02-record-evaluation-frame",
    )
    if not drafts:
        raise RunStateError(
            "当前没有可审计的本地 AI 草稿；本地 AI 可能尚未调用或调用失败。"
            "请先重试生成，也可导入资料后继续，或直接批准通用模板。"
        )
    latest = drafts[-1]
    sources = _source_evidence_for_task(
        run_dir,
        "TASK-LOCAL-02-record-evaluation-frame",
    )
    source_text = "\n\n".join(
        f"来源：{item['source']}\n{item['content']}" for item in sources
    )[:2_500]
    prompt = (
        "你现在是 Research-OS 的第二审计角色。请复核下列研究草稿。\n\n"
        "逐项检查：主张是否有当前 Evidence 支持；是否混淆事实、推断和建议；"
        "是否遗漏反证、风险和未知项；推荐是否超出证据。\n"
        "输出 PASS / NEEDS-REVISION 结论、逐条问题、建议修订和仍需人工判断项。\n\n"
        f"## 待审计草稿\n\n{latest['content'][:3_500]}\n\n"
        f"## 已导入资料摘录\n\n{source_text or '没有导入原始资料。'}"
    )
    reviewer_settings = replace(settings, model=settings.reviewer_model)
    response = _generate_with_progress(
        reviewer_settings,
        prompt,
        ai_generate_fn,
        output_fn,
    )
    return _record_ai_audit_response(
        run_dir,
        response,
        audited_evidence_id=latest["evidence_id"],
        researcher_model=settings.model,
    )


def render_ai_comparison(run_dir: Path | str) -> str:
    path = Path(run_dir)
    status = verify_run(path)
    task_id = "TASK-LOCAL-02-record-evaluation-frame"
    drafts = _ai_evidence_for_task(path, task_id)
    audits = _ai_audits_for_task(path, task_id)
    lines = [
        f"运行：{status['run_id']}",
        f"AI 草稿：{len(drafts)} 版；AI 审计：{len(audits)} 版。",
        "",
        "版本历史：",
    ]
    for index, item in enumerate(drafts, start=1):
        lines.append(
            f"- 草稿 {index}: {item['evidence_id']} | {item['source']} | "
            f"Hash {item['content_sha256'][:12]}… | 上一版 {item.get('revision_of') or '无'}"
        )
    for index, item in enumerate(audits, start=1):
        lines.append(
            f"- 审计 {index}: {item['evidence_id']} | {item['source']} | "
            f"审计对象 {item.get('revision_of') or '未记录'}"
        )
    if len(drafts) >= 2:
        before = drafts[-2]["content"].splitlines()
        after = drafts[-1]["content"].splitlines()
        diff = list(
            unified_diff(before, after, fromfile="上一版", tofile="最新一版", lineterm="")
        )
        lines.extend(["", "最近两版差异：", *diff[:500]])
        if len(diff) > 500:
            lines.append("[差异显示已截断到 500 行]")
    elif drafts:
        lines.extend(["", "目前只有一版草稿，返工后这里会显示差异。"])
    else:
        lines.extend(["", "当前没有 AI 草稿。"])
    return "\n".join(lines)


def _revise_ai_research(
    run_dir: Path,
    settings: AISettings,
    feedback: str,
    ai_generate_fn: AIGenerateFn,
    output_fn: OutputFn,
    review_decision_hash: str,
) -> dict[str, Any]:
    drafts = _ai_evidence_for_task(
        run_dir,
        "TASK-LOCAL-02-record-evaluation-frame",
    )
    if not drafts:
        raise RunStateError("当前还没有可返工的本地 AI 草稿")
    cleaned = feedback.strip()
    if not cleaned:
        raise RunStateError("返工要求不得为空")
    if len(cleaned) > 1500:
        raise RunStateError("返工要求超过 1500 字符")
    previous = drafts[-1]
    sources = _source_evidence_for_task(
        run_dir,
        "TASK-LOCAL-02-record-evaluation-frame",
    )
    source_text = "\n\n".join(
        f"来源：{item['source']}\n{item['content']}" for item in sources
    )[:2_500]
    prompt = (
        f"{render_research_handoff(run_dir)}\n\n"
        "## 上一版草稿\n\n"
        f"{previous['content'][:2_500]}\n\n"
        "## 新导入的原始资料摘录\n\n"
        f"{source_text or '本轮没有新导入资料。'}\n\n"
        "## 人工返工要求\n\n"
        f"{cleaned}\n\n"
        "请输出完整修订稿，并明确列出本次修改点。"
    )
    response = _generate_with_progress(settings, prompt, ai_generate_fn, output_fn)
    return _record_ai_response(
        run_dir,
        response,
        revision_of=previous["evidence_id"],
        review_decision_hash=review_decision_hash,
    )


def _easy_approval_loop(
    run_dir: Path,
    workspace: Path,
    input_fn: InputFn,
    output_fn: OutputFn,
    ai_generate_fn: AIGenerateFn,
) -> None:
    approvals = {"y", "yes", "是", "批准", "继续"}
    pauses = {"n", "no", "否", "稍后"}
    reworks = {"r", "rework", "返工", "修改"}
    rejects = {"x", "reject", "rejected", "驳回", "拒绝"}
    imports = {"f", "file", "文件", "导入"}
    audits = {"v", "verify", "audit", "复核", "审计"}
    ai_retries = {"a", "ai", "重试"}
    claim_confirmations = {"c", "claim", "claims", "断言", "确认断言"}
    automatic_attempted = False
    ai_attempt_failed = False
    template_warning_shown = False
    while True:
        status = verify_run(run_dir)
        if status["status"] == "cancelled":
            output_fn(_easy_status_text(run_dir))
            output_fn(f"取消原因：{status['cancellation_reason']}")
            return
        if status["status"] == "rejected":
            output_fn(render_easy_review(run_dir))
            return
        if status["status"] == "completed":
            output_fn(render_easy_review(run_dir))
            handoff = save_research_handoff(
                run_dir,
                run_dir.parent.parent,
            )
            output_fn(
                "下一步：把下面的 handoff 研究指令文件发送给 "
                "Codex / ChatGPT / Claude 等能联网的 AI，让它收集真实资料、"
                "附上来源并完成候选方案比较。\n"
                f"Handoff 完整路径：{handoff.resolve()}\n"
                "拿到研究结果后：在简易模式选择菜单 8 导入；"
                "如需录入完整修订稿，选择菜单 9 打开高级菜单，再选择 15。"
            )
            completion_settings = load_ai_settings(workspace)
            if completion_settings is None:
                output_fn(
                    "本地 AI 尚未配置；运行 research-os-mvp configure-ollama 后"
                    "重新开始一个任务，可在第 2 步获得本地 AI 草稿。"
                )
            return
        if status["status"] == "approved_pending_resume":
            resume_run(run_dir)
            continue
        settings = load_ai_settings(workspace)
        if (
            not automatic_attempted
            and settings is not None
            and settings.automatic_research
            and status["pending_task_id"] == "TASK-LOCAL-02-record-evaluation-frame"
            and not _ai_evidence_for_task(run_dir, status["pending_task_id"])
        ):
            automatic_attempted = True
            output_fn(f"正在调用本地 AI（{settings.model}），请稍候……")
            try:
                imported = _automatic_ai_research(
                    run_dir,
                    settings,
                    ai_generate_fn,
                    output_fn,
                )
                ai_attempt_failed = False
                output_fn(f"本地 AI 初稿已写入 Evidence：{imported['id']}")
            except MVPError as exc:
                ai_attempt_failed = True
                output_fn(f"本地 AI 调用未完成：{exc}")
                output_fn(_missing_ai_draft_guidance(prior_failure=True))
        if (
            not template_warning_shown
            and status["pending_task_id"] == "TASK-LOCAL-02-record-evaluation-frame"
            and (settings is None or not settings.automatic_research)
        ):
            output_fn(_local_ai_template_warning(settings))
            template_warning_shown = True
        output_fn(render_easy_review(run_dir))
        task_two_pending = (
            status["pending_task_id"] == "TASK-LOCAL-02-record-evaluation-frame"
        )
        retry_available = (
            task_two_pending
            and settings is not None
            and not _ai_evidence_for_task(run_dir, status["pending_task_id"])
        )
        claim_drafts = (
            _ai_evidence_for_task(run_dir, status["pending_task_id"])
            if task_two_pending
            else []
        )
        claim_action_available = task_two_pending and bool(claim_drafts)
        policy_violations: list[str] = []
        claims_recorded = False
        if claim_action_available:
            _, _, claim_source_content = read_claim_source_snapshot(
                run_dir,
                status["pending_task_id"],
            )
            policy_violations = find_ai_draft_policy_violations(claim_source_content)
            claim_coverage = claims_coverage_status(run_dir)
            claims_recorded = (
                status["pending_task_id"] in claim_coverage["tasks_confirmed"]
            )
        policy_confirmation_required = bool(policy_violations) and not claims_recorded
        if policy_confirmation_required:
            output_fn(
                f"守约门槛：当前草稿含 {len(policy_violations)} 条表面来源声明；"
                "批准前必须按 C 逐条分类并确认 Claims。"
            )
        if task_two_pending:
            retry_option = "A 重试 AI；" if retry_available else ""
            claim_option = (
                ("C 重新确认 Claims；" if claims_recorded else "C 逐条确认 Claims；")
                if claim_action_available
                else ""
            )
            prompt = (
                "Reviewer 决定：Y Approved；R Changes Requested；"
                "X Rejected；F 导入资料；V AI 审计；"
                f"{claim_option}{retry_option}回车暂停："
            )
        else:
            prompt = (
                "Reviewer 决定：Y Approved；R Changes Requested；"
                "X Rejected；直接回车稍后处理："
            )
        entered = input_fn(prompt).strip()
        answer = entered.lower()
        if not answer or answer in pauses:
            output_fn("任务已保存。下次双击“双击这里开始.cmd”可继续。")
            return
        if answer in ai_retries:
            if not retry_available or settings is None:
                output_fn("A 重试仅在第 2 步已配置本地 AI 且尚无 AI 草稿时使用。")
                continue
            output_fn(f"正在重试本地 AI（{settings.model}），请稍候……")
            try:
                imported = _automatic_ai_research(
                    run_dir,
                    settings,
                    ai_generate_fn,
                    output_fn,
                )
                ai_attempt_failed = False
                output_fn(f"本地 AI 初稿已写入 Evidence：{imported['id']}")
            except MVPError as exc:
                ai_attempt_failed = True
                output_fn(f"本地 AI 重试未完成：{exc}")
                output_fn(_missing_ai_draft_guidance(prior_failure=True))
            continue
        if answer in claim_confirmations:
            if not claim_action_available:
                output_fn("C Claim 确认仅在第 2 步已有本地 AI 草稿时使用。")
                continue
            try:
                _confirm_ai_draft_claims(
                    run_dir,
                    status["pending_task_id"],
                    input_fn,
                    output_fn,
                )
            except MVPError as exc:
                output_fn(f"Claim 确认未完成：{exc}")
            continue
        if answer in reworks:
            feedback = input_fn("请记录 Changes Requested 的具体修改要求：")
            if not feedback.strip():
                output_fn("修改要求不得为空，本次未记录 Reviewer 决定。")
                continue
            reviewed = review_run(
                run_dir,
                reviewer="Human Owner (Easy Mode)",
                decision="Changes Requested",
                note=feedback,
            )
            output_fn(f"已记录正式 Reviewer 决定：{reviewed['latest_review_id']}")
            if status["pending_task_id"] != "TASK-LOCAL-02-record-evaluation-frame":
                entered_revision = input_fn(
                    "请粘贴修订后的完整内容；也可输入 @UTF-8文件路径；"
                    "直接回车只保存 Reviewer 决定："
                )
                revision_content = _revision_content_from_input(entered_revision)
                if not revision_content:
                    output_fn("Task 保持暂停，可稍后录入修订版。")
                    return
                revised = revise_task_output(
                    run_dir,
                    content=revision_content,
                    revised_by="Human Owner (Easy Mode)",
                    note=feedback,
                    review_decision_hash=reviewed["latest_review_hash"],
                )
                output_fn(f"Task 产物修订版已写入 Evidence：{revised['id']}")
                continue
            if settings is None:
                output_fn("决定已保存；本地 AI 未配置，Task 保持暂停。")
                return
            output_fn(f"正在让本地 AI（{settings.model}）返工，请稍候……")
            try:
                imported = _revise_ai_research(
                    run_dir,
                    settings,
                    feedback,
                    ai_generate_fn,
                    output_fn,
                    reviewed["latest_review_hash"],
                )
                output_fn(f"AI 返工稿已写入 Evidence：{imported['id']}")
            except MVPError as exc:
                output_fn(f"AI 返工未完成：{exc}")
            continue
        if answer in rejects:
            reason = input_fn("请记录 Rejected 原因（必填）：")
            if not reason.strip():
                output_fn("驳回原因不得为空，本次未记录 Reviewer 决定。")
                continue
            reviewed = review_run(
                run_dir,
                reviewer="Human Owner (Easy Mode)",
                decision="Rejected",
                note=reason,
            )
            output_fn(
                f"已记录正式 Rejected：{reviewed['latest_review_id']}；"
                "Run 已终止，全部产物保留。"
            )
            return
        if answer in imports:
            if status["pending_task_id"] != "TASK-LOCAL-02-record-evaluation-frame":
                output_fn("F 导入在第 2 步使用。")
                continue
            dropped = input_fn("请把 PDF、网页文件、数据手册或代码目录拖到这里：")
            try:
                imported = _import_source_to_run(run_dir, dropped)
                output_fn(f"资料已写入 Evidence：{imported['id']}")
                output_fn("如需 AI 根据新资料重做，请输入 R。")
            except MVPError as exc:
                output_fn(f"资料导入未完成：{exc}")
            continue
        if answer in audits:
            if status["pending_task_id"] != "TASK-LOCAL-02-record-evaluation-frame":
                output_fn("V 审计在第 2 步使用。")
                continue
            if settings is None:
                output_fn(
                    "本地 AI 尚未配置，因此没有可审计草稿；"
                    "可按 F 导入资料、按 Y 批准通用模板，或使用菜单 5 导出研究指令。"
                )
                continue
            if not _ai_evidence_for_task(run_dir, status["pending_task_id"]):
                output_fn(
                    _missing_ai_draft_guidance(prior_failure=ai_attempt_failed)
                )
                continue
            output_fn(f"正在调用审计模型（{settings.reviewer_model}），请稍候……")
            try:
                imported = _audit_ai_research(
                    run_dir,
                    settings,
                    ai_generate_fn,
                    output_fn,
                )
                output_fn(f"AI 审计意见已写入 Evidence：{imported['id']}")
            except MVPError as exc:
                output_fn(f"AI 审计未完成：{exc}")
            continue
        if answer in approvals and policy_confirmation_required:
            output_fn(
                "本次未批准：表面来源声明尚未完成人工 Claim 确认。"
                "请先按 C 逐条分类，或按 R 修订草稿。"
            )
            continue
        if answer not in approvals:
            accepted = "Y、R、X、F、V、N"
            if retry_available:
                accepted += "、A"
            if claim_action_available:
                accepted += "、C"
            output_fn(
                f"这里仅接收 {accepted} 或直接回车；"
                "刚才的文字没有写入任务。"
            )
            if _looks_like_external_ai_instruction(entered):
                output_fn(
                    "这段内容应发送到 Codex/其他 AI 对话，不是在本窗口执行。"
                )
            continue
        approve_run(
            run_dir,
            approver="Human Owner (Easy Mode)",
            note="Approved in the guided easy workflow",
        )
        resume_run(run_dir)


def _easy_status_text(run_dir: Path) -> str:
    status = verify_run(run_dir)
    state_names = {
        "paused": "等待您批准",
        "approved_pending_resume": "已批准，等待继续",
        "completed": "已完成",
        "cancelled": "已取消（证据已保留）",
        "rejected": "Reviewer 已驳回（记录已保留）",
    }
    state = state_names.get(status["status"], status["status"])
    return (
        f"最近任务：{status['run_id']}\n"
        f"状态：{state}\n"
        f"证据：{status['evidence_count']} 份\n"
        f"报告：{status['report_count']} 份\n"
        f"人工批准：{status['approval_count']} 次\n"
        f"Reviewer 决定：{status['review_count']} 次\n"
        "完整性检查：通过。\n"
        "研究结论：仍需真实来源、参数或测试数据。"
    )


def _collect_scenario_context(
    profile: ScenarioProfile,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> str:
    output_fn("请逐项补充要求；不适用的项目直接回车跳过。")
    answers: list[str] = []
    for label, prompt in context_questions_for(profile):
        answer = input_fn(prompt).strip()
        if (
            profile.key == "hardware-selection"
            and label == "预算"
            and answer
            and any(character.isdigit() for character in answer)
            and not re.search(r"元|人民币|rmb|cny|美元|usd|欧元|eur|万|千", answer, re.IGNORECASE)
        ):
            unit = input_fn("预算数字的单位是什么（例如：元、美元）：").strip()
            if unit:
                answer = f"{answer} {unit}"
            else:
                output_fn("预算单位仍是未知项，系统会在 Evidence 中保留原输入。")
        if answer:
            answers.append(f"{label}：{answer}")
    return "\n".join(answers)


def _confirm_new_task(
    goal: str,
    profile: ScenarioProfile,
    context: str,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> str:
    output_fn("\n请确认即将创建的任务：")
    output_fn(f"类型：{profile.name_zh}")
    output_fn(f"目标：{goal}")
    output_fn(f"要求：\n{context or '（未补充）'}")
    answer = input_fn(
        "输入 Y 确认创建；输入 R 重新填写；直接回车取消："
    ).strip().lower()
    if answer in {"y", "yes", "是", "确认", "创建"}:
        return "confirm"
    if answer in {"r", "redo", "重填", "重新填写"}:
        return "retry"
    return "cancel"


def _looks_like_external_ai_instruction(value: str) -> bool:
    normalized = value.casefold()
    return (
        "执行 research-os" in normalized
        or "ai-research-run-" in normalized
        or normalized.endswith(".md")
    )


def _choose_category(input_fn: InputFn, output_fn: OutputFn) -> str:
    output_fn("0. 自动识别")
    for index, profile in enumerate(SCENARIO_PROFILES, start=1):
        output_fn(f"{index}. {profile.name_zh}")
    selected = input_fn("选择场景 [0]：").strip() or "0"
    if selected == "0":
        return "auto"
    try:
        position = int(selected)
    except ValueError as exc:
        raise RunStateError("场景选项无效") from exc
    if not 1 <= position <= len(SCENARIO_PROFILES):
        raise RunStateError("场景选项无效")
    return SCENARIO_PROFILES[position - 1].key


def _resolve_run_path(
    current_run: Path | None,
    input_fn: InputFn,
) -> Path:
    default = str(current_run) if current_run else ""
    prompt = f"Run 目录 [{default}]：" if default else "Run 目录："
    entered = input_fn(prompt).strip()
    if entered:
        return Path(entered)
    if current_run is None:
        raise RunStateError("尚未选择 Run 目录")
    return current_run


def _status_line(status: dict[str, Any]) -> str:
    return (
        f"Run={status['run_id']} | 状态={status['status']} | "
        f"待批准={status['pending_task_id'] or '无'} | "
        f"Evidence={status['evidence_count']} | Report={status['report_count']}"
    )


def _record_git_project_from_prompt(
    run_dir: Path,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> dict[str, Any]:
    repo_value = input_fn("请把 Git 项目文件夹拖到这里：").strip()
    preview = collect_git_snapshot(repo_value, run_tests=False)
    if preview.test_command:
        command = " ".join(preview.test_command)
        output_fn(f"检测到测试命令：{command}")
        confirmation = input_fn(
            "运行测试会执行该项目代码；输入 RUN 明确确认，直接回车只记录 Git 快照："
        ).strip()
        run_tests = confirmation == "RUN"
        if confirmation and not run_tests:
            output_fn("未收到 RUN 确认，本次只记录 Git 快照，不执行测试。")
    else:
        output_fn("没有检测到受支持的测试命令，本次只记录 Git 快照。")
        run_tests = False
    return record_git_snapshot_evidence(run_dir, repo_value, run_tests=run_tests)


def run_wizard(
    workspace: Path | str = Path("workspace"),
    *,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> int:
    root = Path(workspace)
    current_run: Path | None = None
    output_fn("Research-OS MVP 中文交互向导")
    output_fn("自然语言入口使用本地规则和模板，不会调用外部模型。")

    while True:
        output_fn(
            "\n1. 一句话创建 Pack 并立即启动\n"
            "2. 一句话只创建 Pack\n"
            "3. 验证已有 Pack\n"
            "4. 启动已有 Pack\n"
            "5. 查看 Run 状态\n"
            "6. 批准当前 Task\n"
            "7. 恢复运行\n"
            "8. 查看 Evidence 和 Report\n"
            "9. 验证完整性\n"
            "10. 查看场景目录\n"
            "11. 导出到 Obsidian\n"
            "12. 导入 Git 项目快照\n"
            "13. 取消 Run（保留全部记录）\n"
            "14. 记录正式 Reviewer 决定\n"
            "15. 录入 Task 产物修订版\n"
            "16. 使用 Reviewer Registry 启动已有 Pack\n"
            "0. 退出"
        )
        try:
            choice = input_fn("请选择：").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\n已退出。")
            return 0
        try:
            if choice == "0":
                output_fn("已退出。")
                return 0
            if choice in {"1", "2"}:
                goal = input_fn("请用一句话说明目标：")
                category = _choose_category(input_fn, output_fn)
                context = input_fn("补充背景（可留空）：")
                generated = create_pack_from_goal(
                    goal,
                    category=category,
                    context=context,
                    workspace=root,
                )
                output_fn(
                    f"Pack 已{'\u590d\u7528' if generated.reused else '\u521b\u5efa'}："
                    f"{generated.path} [{generated.category_name}]"
                )
                if choice == "1":
                    status = create_run(generated.path, root / "runs")
                    current_run = root / "runs" / status["run_id"]
                    output_fn(_status_line(status))
            elif choice == "3":
                pack_path = Path(input_fn("Pack 路径：").strip())
                loaded = load_pack(pack_path)
                output_fn(f"VALID: {loaded.data['pack_id']} {loaded.canonical_sha256}")
            elif choice == "4":
                pack_path = Path(input_fn("Pack 路径：").strip())
                status = create_run(pack_path, root / "runs")
                current_run = root / "runs" / status["run_id"]
                output_fn(_status_line(status))
            elif choice == "5":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(_status_line(status_run(current_run)))
            elif choice == "6":
                current_run = _resolve_run_path(current_run, input_fn)
                approver = input_fn("批准人 [Human Owner]：").strip() or "Human Owner"
                note = input_fn("备注（可留空）：")
                output_fn(_status_line(approve_run(current_run, approver=approver, note=note)))
            elif choice == "7":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(_status_line(resume_run(current_run)))
            elif choice == "8":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(render_run_artifacts(current_run))
            elif choice == "9":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(_status_line(verify_run(current_run)))
                output_fn("完整性验证通过。")
            elif choice == "10":
                output_fn(category_catalog_text())
            elif choice == "11":
                current_run = _resolve_run_path(current_run, input_fn)
                vault = input_fn("Obsidian 库根目录：").strip()
                exported = export_run_to_obsidian(current_run, vault)
                output_fn(f"已导出不可变快照：{exported['export_dir']}")
            elif choice == "12":
                current_run = _resolve_run_path(current_run, input_fn)
                recorded = _record_git_project_from_prompt(
                    current_run,
                    input_fn,
                    output_fn,
                )
                output_fn(
                    f"Git 快照已写入 Evidence：{recorded['id']}；"
                    f"测试结果：{recorded['test_status']}"
                )
            elif choice == "13":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(_status_line(status_run(current_run)))
                confirmation = input_fn(
                    "取消后不可恢复执行，但全部 Evidence 会保留；输入 CANCEL 确认："
                ).strip()
                if confirmation != "CANCEL":
                    output_fn("未收到 CANCEL，Run 保持原状态。")
                    continue
                cancelled_by = input_fn("操作人 [Human Owner]：").strip() or "Human Owner"
                reason = input_fn("取消原因（必填）：")
                output_fn(
                    _status_line(
                        cancel_run(
                            current_run,
                            cancelled_by=cancelled_by,
                            reason=reason,
                        )
                    )
                )
            elif choice == "14":
                current_run = _resolve_run_path(current_run, input_fn)
                output_fn(_status_line(status_run(current_run)))
                entered = input_fn(
                    "决定：A Approved；C Changes Requested；X Rejected："
                ).strip().lower()
                decision_map = {
                    "a": "Approved",
                    "approved": "Approved",
                    "c": "Changes Requested",
                    "changes requested": "Changes Requested",
                    "x": "Rejected",
                    "rejected": "Rejected",
                }
                if entered not in decision_map:
                    output_fn("决定选项无效，Run 保持原状态。")
                    continue
                reviewer = input_fn("Reviewer [Human Owner]：").strip() or "Human Owner"
                note = input_fn("审查意见（Changes Requested / Rejected 必填）：")
                output_fn(
                    _status_line(
                        review_run(
                            current_run,
                            reviewer=reviewer,
                            decision=decision_map[entered],
                            note=note,
                        )
                    )
                )
            elif choice == "15":
                current_run = _resolve_run_path(current_run, input_fn)
                current_status = status_run(current_run)
                if current_status.get("latest_review_decision") != "Changes Requested":
                    raise RunStateError(
                        "录入修订版前，必须先对当前 Task 记录 Changes Requested"
                    )
                revised_by = input_fn("修订人 [Human Owner]：").strip() or "Human Owner"
                note = input_fn("本版修订说明（必填）：")
                entered_revision = input_fn(
                    "粘贴完整修订内容，或输入 @UTF-8文件路径："
                )
                content = _revision_content_from_input(entered_revision)
                revised = revise_task_output(
                    current_run,
                    content=content,
                    revised_by=revised_by,
                    note=note,
                    review_decision_hash=current_status["latest_review_hash"],
                )
                output_fn(f"Task 产物修订版已写入 Evidence：{revised['id']}")
                output_fn(_status_line(status_run(current_run)))
            elif choice == "16":
                pack_path = Path(input_fn("Pack 路径：").strip())
                registry_path = Path(
                    input_fn("已封存 Reviewer Registry 路径：").strip()
                )
                actor = (
                    input_fn("策略绑定操作人 [Human Owner]：").strip()
                    or "Human Owner"
                )
                status = create_run(
                    pack_path,
                    root / "runs",
                    reviewer_trust_registry=_read_json_object_limited(registry_path),
                    reviewer_trust_actor=actor,
                )
                current_run = root / "runs" / status["run_id"]
                output_fn(_status_line(status))
                output_fn("Reviewer Registry 已在 Run 创建时绑定。")
            else:
                output_fn("选项无效，请重新选择。")
        except (MVPError, OSError, json.JSONDecodeError) as exc:
            output_fn(f"操作失败：{exc}")


def run_easy_wizard(
    workspace: Path | str = Path("workspace"),
    *,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    ai_generate_fn: AIGenerateFn = generate_research,
) -> int:
    root = Path(workspace)
    output_fn("Research-OS 简易模式")
    output_fn("输入任务和必要限制；每一步检查后，认可就输入 Y。")
    settings = load_ai_settings(root)
    if settings is None:
        output_fn("本地模式先建立研究记录；菜单 5 用于生成真实研究指令。")
    else:
        output_fn(f"本地 AI 已启用：{settings.model}；第 2 步会自动生成研究草稿。")

    while True:
        output_fn(
            "\n1. 开始一个新任务（推荐）\n"
            "2. 继续上次任务\n"
            "3. 查看上次任务的全部记录\n"
            "4. 检查上次任务是否完整\n"
            "5. 生成给 AI 的真实研究指令（用于得到答案）\n"
            "6. 查看我可以问什么\n"
            "7. 检查本地 AI\n"
            "8. 给上次任务导入资料\n"
            "9. 打开高级菜单\n"
            "10. 对比上次任务的 AI 版本\n"
            "11. 从项目模板开始\n"
            "12. 导出上次任务到 Obsidian\n"
            "13. 给上次任务导入 Git 项目快照\n"
            "0. 退出"
        )
        try:
            choice = input_fn("请输入数字：").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\n已安全退出，任务记录会保留。")
            return 0

        try:
            if choice == "0":
                output_fn("已安全退出，任务记录会保留。")
                return 0
            if choice == "1":
                while True:
                    goal = input_fn("您想完成什么？请用一句话说明：").strip()
                    if not goal:
                        output_fn("已取消创建任务。")
                        break
                    profile = resolve_category("auto", goal)
                    context = _collect_scenario_context(
                        profile,
                        input_fn,
                        output_fn,
                    )
                    decision = _confirm_new_task(
                        goal,
                        profile,
                        context,
                        input_fn,
                        output_fn,
                    )
                    if decision == "retry":
                        output_fn("请重新填写任务。")
                        continue
                    if decision == "cancel":
                        output_fn("已取消创建任务，没有生成新记录。")
                        break
                    generated = create_pack_from_goal(
                        goal,
                        category=profile.key,
                        context=context,
                        workspace=root,
                    )
                    status = create_run(generated.path, root / "runs")
                    run_dir = root / "runs" / status["run_id"]
                    output_fn(f"已识别任务类型：{generated.category_name}")
                    output_fn("任务已经保存，现在开始第 1 步。")
                    _easy_approval_loop(run_dir, root, input_fn, output_fn, ai_generate_fn)
                    break
            elif choice == "2":
                run_dir = _latest_run(root)
                _easy_approval_loop(run_dir, root, input_fn, output_fn, ai_generate_fn)
            elif choice == "3":
                output_fn(render_run_artifacts(_latest_run(root)))
            elif choice == "4":
                output_fn(_easy_status_text(_latest_run(root)))
            elif choice == "5":
                run_dir = _latest_run(root)
                handoff = save_research_handoff(run_dir, root)
                output_fn(f"研究指令已保存：{handoff}")
                output_fn(render_research_handoff(run_dir))
            elif choice == "6":
                output_fn(easy_question_examples_text())
            elif choice == "7":
                settings = load_ai_settings(root)
                if settings is None:
                    output_fn("本地 AI 尚未配置。")
                else:
                    state = check_ollama(settings)
                    availability = "已安装" if state["model_available"] else "模型待下载"
                    output_fn(
                        f"Ollama 服务正常。模型：{state['model']}（{availability}）。"
                    )
            elif choice == "8":
                run_dir = _latest_run(root)
                dropped = input_fn(
                    "请把 PDF、网页文件、数据手册或代码目录拖到这里："
                )
                imported = _import_source_to_run(run_dir, dropped)
                output_fn(f"资料已写入 Evidence：{imported['id']}")
                output_fn("继续任务时输入 2；在第 2 步输入 R 可让 AI 根据资料返工。")
            elif choice == "9":
                output_fn("正在打开高级菜单；退出高级菜单后会回到这里。")
                run_wizard(root, input_fn=input_fn, output_fn=output_fn)
            elif choice == "10":
                output_fn(render_ai_comparison(_latest_run(root)))
            elif choice == "11":
                output_fn("项目模板：")
                for index, profile in enumerate(SCENARIO_PROFILES, start=1):
                    output_fn(f"{index}. {profile.name_zh} - {profile.description}")
                selected = input_fn("请选择模板数字：").strip()
                if not selected.isdigit() or not 1 <= int(selected) <= len(SCENARIO_PROFILES):
                    output_fn("模板数字无效，本次没有创建任务。")
                    continue
                profile = SCENARIO_PROFILES[int(selected) - 1]
                goal = input_fn(f"请说明这次{profile.name_zh}要完成什么：").strip()
                if not goal:
                    output_fn("已取消创建任务。")
                    continue
                context = _collect_scenario_context(profile, input_fn, output_fn)
                decision = _confirm_new_task(
                    goal,
                    profile,
                    context,
                    input_fn,
                    output_fn,
                )
                if decision != "confirm":
                    output_fn("本次没有创建任务。")
                    continue
                generated = create_pack_from_goal(
                    goal,
                    category=profile.key,
                    context=context,
                    workspace=root,
                )
                status = create_run(generated.path, root / "runs")
                run_dir = root / "runs" / status["run_id"]
                output_fn(f"已使用项目模板：{generated.category_name}")
                _easy_approval_loop(run_dir, root, input_fn, output_fn, ai_generate_fn)
            elif choice == "12":
                run_dir = _latest_run(root)
                vault = input_fn("请把 Obsidian 库根目录拖到这里：").strip()
                exported = export_run_to_obsidian(run_dir, vault)
                output_fn(f"已导出不可变快照：{exported['export_dir']}")
            elif choice == "13":
                run_dir = _latest_run(root)
                recorded = _record_git_project_from_prompt(
                    run_dir,
                    input_fn,
                    output_fn,
                )
                output_fn(
                    f"Git 快照已写入 Evidence：{recorded['id']}；"
                    f"测试结果：{recorded['test_status']}"
                )
            else:
                if _looks_like_external_ai_instruction(choice):
                    output_fn(
                        "这段内容应发送到 Codex/其他 AI 对话；本窗口请输入菜单数字。"
                    )
                else:
                    output_fn("请输入 0 到 13 之间的菜单数字。")
        except (MVPError, OSError, json.JSONDecodeError) as exc:
            output_fn(f"操作没有完成：{exc}")


def category_catalog_json() -> dict[str, Any]:
    return {"categories": list_scenarios()}
