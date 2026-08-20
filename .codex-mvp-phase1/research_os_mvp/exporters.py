from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_os_mvp.errors import MVPError
from research_os_mvp.handoff import (
    render_effective_mission_report_from_manifest,
)
from research_os_mvp.integrity import write_text_atomic
from research_os_mvp.runtime import read_effective_run_snapshot


class ExportError(MVPError):
    """Raised when an immutable knowledge export cannot be created."""


def _write_immutable(path: Path, content: str) -> None:
    if path.is_symlink():
        raise ExportError(f"导出目标不得是符号链接：{path}")
    if path.exists():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ExportError(f"导出目标已有不同内容：{path}")
        return
    write_text_atomic(path, content)


def _yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def export_run_to_obsidian(
    run_dir: Path | str,
    vault_dir: Path | str,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    snapshot = read_effective_run_snapshot(run_path)
    status = snapshot["status"]
    manifest = snapshot["effective_output_manifest"]
    vault_value = str(vault_dir).strip()
    if (
        len(vault_value) >= 2
        and vault_value[0] == vault_value[-1]
        and vault_value[0] in {'"', "'"}
    ):
        vault_value = vault_value[1:-1].strip()
    if not vault_value:
        raise ExportError("Obsidian 库路径为空")
    vault_input = Path(vault_value).expanduser()
    if vault_input.is_symlink():
        raise ExportError("Obsidian 库路径不得是符号链接")
    vault = vault_input.resolve(strict=True)
    if not vault.is_dir():
        raise ExportError("Obsidian 库路径必须是普通目录")
    if not (vault / ".obsidian").is_dir():
        raise ExportError("所选目录没有 .obsidian，请选择 Obsidian 库根目录")

    snapshot_hash = manifest["canonical_snapshot_sha256"]
    namespace = vault / "Research-OS"
    if namespace.exists() and (namespace.is_symlink() or not namespace.is_dir()):
        raise ExportError("Obsidian 的 Research-OS 导出位置必须是普通目录")
    namespace.mkdir(exist_ok=True)
    export_dir = namespace / f"{status['run_id']}-{snapshot_hash[:8]}"
    if export_dir.exists() and export_dir.is_symlink():
        raise ExportError("导出目录不得是符号链接")
    export_dir.mkdir(exist_ok=True)

    pack = snapshot["pack"]
    evidence_rows = [item["data"] for item in snapshot["evidence"]]
    reviews = snapshot["reviews"]
    review_signatures = snapshot["review_signatures"]
    trust_registry = snapshot["reviewer_trust_registry"]
    effective_outputs = manifest["outputs"]

    _write_immutable(
        export_dir / "Effective Output Manifest.json",
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    )

    effective_lines = [
        "# Effective Task Outputs",
        "",
        f"Run：`{status['run_id']}`",
        "",
        (
            "默认输出只提升已进入 `Approved` Reviewer 审查包、且满足已绑定"
            " Reviewer 信任策略的修订；待审或签名门槛不足的版本仅保留在审计记录。"
        ),
    ]
    for item in effective_outputs:
        source = (
            f"已批准修订；Reviewer 决定 `{item['approved_review_id']}` "
            f"(`{item['approved_review_hash']}`)"
            if item["source"] == "approved_revision"
            else "原始 Task 输出"
        )
        if item["source"] == "original" and item.get("approved_review_hash"):
            source += (
                f"；Reviewer 决定 `{item['approved_review_id']}` "
                f"(`{item['approved_review_hash']}`)"
            )
        effective_lines.extend(
            [
                "",
                f"## {item['task_id']} — {item['task_name']}",
                "",
                f"- 有效产物：`{item['effective_id']}`",
                f"- 版本来源：{source}",
                "",
                str(item["content"]).rstrip(),
            ]
        )
        for signature in item.get("approved_review_signatures", []):
            effective_lines.append(
                "- Ed25519 签名："
                f"{signature['signer_identity']} "
                f"(`{signature['public_key_fingerprint']}`)"
                + (
                    f"；策略角色 `{signature['reviewer_role']}`，可信"
                    if signature.get("policy_trusted")
                    else (
                        "；未计入策略门槛"
                        if signature.get("policy_trusted") is False
                        else ""
                    )
                )
            )
    _write_immutable(
        export_dir / "Effective Task Outputs.md",
        "\n".join(effective_lines) + "\n",
    )

    evidence_links: list[str] = []
    for evidence in evidence_rows:
        evidence_id = evidence["evidence_id"]
        note_name = f"{evidence_id}.md"
        evidence_links.append(f"- [[{evidence_id}]] — {evidence['source']}")
        revision_metadata = ""
        if evidence.get("revision_of"):
            revision_metadata += (
                f"revision_of: {_yaml_scalar(str(evidence['revision_of']))}\n"
            )
        if evidence.get("review_decision_hash"):
            revision_metadata += (
                "review_decision_hash: "
                f"{_yaml_scalar(str(evidence['review_decision_hash']))}\n"
            )
        note = (
            "---\n"
            "type: research-os-evidence\n"
            f"run_id: {_yaml_scalar(status['run_id'])}\n"
            f"evidence_id: {_yaml_scalar(evidence_id)}\n"
            f"source: {_yaml_scalar(str(evidence['source']))}\n"
            f"content_sha256: {_yaml_scalar(evidence['content_sha256'])}\n"
            f"role: {_yaml_scalar(str(evidence.get('evidence_role') or 'task_evidence'))}\n"
            f"{revision_metadata}"
            "---\n\n"
            f"# {evidence_id}\n\n"
            f"来源：`{evidence['source']}`\n\n"
            f"采集方法：{evidence['method']}\n\n"
            f"限制：{evidence['limitations']}\n\n"
            "## 内容\n\n"
            f"{evidence['content']}\n\n"
            f"原始内容 Hash：`{evidence['content_sha256']}`\n"
        )
        _write_immutable(export_dir / note_name, note)

    mission_reports = [
        item
        for item in snapshot["reports"]
        if Path(item["path"]).name.startswith("REPORT-MISSION-")
        and Path(item["path"]).suffix.casefold() == ".md"
    ]
    report_link = ""
    if mission_reports:
        report_content = mission_reports[0]["content"]
        _write_immutable(export_dir / "Original Mission Report.md", report_content)
        _write_immutable(
            export_dir / "Mission Report.md",
            render_effective_mission_report_from_manifest(manifest),
        )
        report_link = "\n- [[Mission Report]]（默认有效版本）\n- [[Original Mission Report]]（原始审计版本）\n"

    review_link = "\n- 尚未记录 Reviewer 决定\n"
    if reviews:
        review_lines = [
            "# Reviewer Decisions",
            "",
            f"Run：`{status['run_id']}`",
            "",
            "以下记录按审计链顺序列出：",
        ]
        for review in reviews:
            review_lines.extend(
                [
                    "",
                    f"## {review['review_id']} — {review['decision']}",
                    "",
                    f"- Task：`{review['task_id']}`",
                    f"- Reviewer：{review['reviewer']}",
                    f"- 时间：`{review['at']}`",
                    f"- 意见：{review['note'] or '（无）'}",
                    f"- 审查包 Hash：`{review['subject']['bundle_sha256']}`",
                    f"- 决定记录 Hash：`{review['hash']}`",
                ]
            )
            for signature in review_signatures:
                if signature["review_hash"] == review["hash"]:
                    review_lines.extend(
                        [
                            f"- Ed25519 签名身份：{signature['signer_identity']}",
                            f"- 公钥指纹：`{signature['public_key_fingerprint']}`",
                            f"- 签名记录 Hash：`{signature['hash']}`",
                        ]
                    )
        _write_immutable(
            export_dir / "Reviewer Decisions.md",
            "\n".join(review_lines) + "\n",
        )
        review_link = "\n- [[Reviewer Decisions]]\n"

    signature_link = "\n- 尚未附加 Reviewer Ed25519 签名\n"
    if review_signatures:
        signature_lines = [
            "# Reviewer Ed25519 Signatures",
            "",
            f"Run：`{status['run_id']}`",
            "",
            "签名使用 OpenSSH Ed25519，私钥不进入 Research-OS Run。",
        ]
        for signature in review_signatures:
            signature_lines.extend(
                [
                    "",
                    f"## {signature['signature_id']}",
                    "",
                    f"- Review：`{signature['review_id']}`",
                    f"- Review Hash：`{signature['review_hash']}`",
                    f"- 签名身份：{signature['signer_identity']}",
                    f"- 公钥指纹：`{signature['public_key_fingerprint']}`",
                    f"- Payload Hash：`{signature['payload_sha256']}`",
                    f"- 签名记录 Hash：`{signature['hash']}`",
                ]
            )
        _write_immutable(
            export_dir / "Reviewer Signatures.md",
            "\n".join(signature_lines) + "\n",
        )
        _write_immutable(
            export_dir / "Reviewer Signatures.json",
            json.dumps(
                review_signatures,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
        )
        signature_link = (
            "\n- [[Reviewer Signatures]]\n"
            "- `Reviewer Signatures.json`（完整签名记录）\n"
        )

    trust_link = "\n- 未绑定 Reviewer 信任策略\n"
    if trust_registry is not None:
        _write_immutable(
            export_dir / "Reviewer Trust Registry.json",
            json.dumps(
                trust_registry,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
        )
        trust_lines = [
            "# Reviewer Trust Registry",
            "",
            f"Run：`{status['run_id']}`",
            "",
            f"- 注册表：`{trust_registry['registry_id']}` v{trust_registry['version']}",
            f"- Registry Hash：`{trust_registry['registry_sha256']}`",
            f"- 当前门槛：{'已满足' if status['reviewer_trust_satisfied'] else '未满足'}",
            "",
            "## Trusted Keys",
        ]
        for key in trust_registry["keys"]:
            validity = f"自 `{key['valid_from']}`"
            if key.get("valid_until"):
                validity += f" 至 `{key['valid_until']}`"
            if key.get("revoked_at"):
                validity += f"；`{key['revoked_at']}` 起吊销"
            trust_lines.extend(
                [
                    "",
                    f"- `{key['identity']}` / `{key['role']}`",
                    f"  - 指纹：`{key['public_key_fingerprint']}`",
                    f"  - 有效期：{validity}",
                ]
            )
        trust_lines.extend(["", "## Requirements"])
        for requirement in trust_registry["requirements"]:
            trust_lines.append(
                f"- Task `{requirement['task_id']}` / {requirement['decision']} / "
                f"角色 `{requirement['role']}`：至少 "
                f"{requirement['minimum_signatures']} 个不同公钥签名"
            )
        if status["reviewer_trust_reviews"]:
            trust_lines.extend(["", "## Review Evaluation"])
            for evaluation in status["reviewer_trust_reviews"]:
                trust_lines.append(
                    f"- `{evaluation['review_id']}`："
                    f"{'已满足' if evaluation['satisfied'] else '未满足'}"
                )
                for outstanding in evaluation["outstanding_requirements"]:
                    trust_lines.append(
                        f"  - `{outstanding['role']}`："
                        f"{outstanding['observed_signatures']}/"
                        f"{outstanding['required_signatures']}，"
                        f"缺 {outstanding['missing_signatures']}"
                    )
        _write_immutable(
            export_dir / "Reviewer Trust Registry.md",
            "\n".join(trust_lines) + "\n",
        )
        trust_link = (
            "\n- [[Reviewer Trust Registry]]\n"
            "- `Reviewer Trust Registry.json`（Run 绑定的不可变策略快照）\n"
        )

    trust_status_line = (
        f"Reviewer 信任策略：`{status['reviewer_trust_registry_id']}` v"
        f"{status['reviewer_trust_registry_version']}；"
        f"门槛{'已满足' if status['reviewer_trust_satisfied'] else '未满足'}  \n"
        if status["reviewer_trust_policy_bound"]
        else "Reviewer 信任策略：未绑定  \n"
    )
    index = (
        "---\n"
        "type: research-os-run\n"
        f"run_id: {_yaml_scalar(status['run_id'])}\n"
        f"status: {_yaml_scalar(status['status'])}\n"
        f"snapshot_sha256: {_yaml_scalar(snapshot_hash)}\n"
        "---\n\n"
        f"# {pack['mission']['title']}\n\n"
        f"Run：`{status['run_id']}`  \n"
        f"状态：`{status['status']}`  \n"
        f"人工批准：{status['approval_count']} 次  \n"
        f"Reviewer 决定：{status['review_count']} 次  \n"
        f"Reviewer Ed25519 签名：{status['review_signature_count']} 个  \n"
        + trust_status_line
        + f"Task 产物修订：{status['task_output_revision_count']} 版  \n"
        f"Evidence：{status['evidence_count']} 份  \n"
        f"Snapshot Hash：`{snapshot_hash}`\n\n"
        "## Effective Task Outputs\n\n"
        "- [[Effective Task Outputs]]\n\n"
        f"- Manifest：`Effective Output Manifest.json` (`{manifest['manifest_sha256']}`)\n\n"
        "## Evidence\n\n"
        + ("\n".join(evidence_links) if evidence_links else "- 无")
        + "\n\n## Report\n"
        + (report_link or "\n- 尚未生成 Mission Report\n")
        + "\n## Reviewer Decisions\n"
        + review_link
        + "\n## Reviewer Signatures\n"
        + signature_link
        + "\n## Reviewer Trust Policy\n"
        + trust_link
        + "\n## 可复核说明\n\n"
        "此目录是一次不可变快照；同一 Run 在状态变化后会导出到新的 Hash 后缀目录。\n"
    )
    _write_immutable(export_dir / "INDEX.md", index)
    return {
        "run_id": status["run_id"],
        "export_dir": str(export_dir),
        "evidence_notes": len(evidence_rows),
        "review_decisions": len(reviews),
        "review_signatures": len(review_signatures),
        "reviewer_trust_policy_bound": status["reviewer_trust_policy_bound"],
        "reviewer_trust_satisfied": status["reviewer_trust_satisfied"],
        "effective_outputs": len(effective_outputs),
        "approved_revision_outputs": sum(
            item["source"] == "approved_revision" for item in effective_outputs
        ),
        "effective_manifest_sha256": manifest["manifest_sha256"],
        "report_exported": bool(mission_reports),
        "snapshot_sha256": snapshot_hash,
    }
