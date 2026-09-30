from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from research_os_mvp.ai import (
    DEFAULT_GENERATION_BUDGET_SECONDS,
    DEFAULT_HEALTH_TIMEOUT_SECONDS,
    DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
    check_ollama,
    load_ai_settings,
    save_ollama_settings,
)
from research_os_mvp.benchmark import (
    benchmark_console_summary,
    default_benchmark_path,
    run_ollama_benchmark,
    save_benchmark_report,
)
from research_os_mvp.errors import IntegrityError, MVPError
from research_os_mvp.exporters import export_run_to_obsidian
from research_os_mvp.git_integration import record_git_snapshot_evidence
from research_os_mvp.integrity import read_json, write_text_atomic
from research_os_mvp.natural_language import create_pack_from_goal
from research_os_mvp.pack import load_pack
from research_os_mvp.run_store import CHECKPOINT_FILE, RUNTIME_DIR, read_checkpoint
from research_os_mvp.runtime import (
    approve_run,
    attach_review_signature,
    bind_reviewer_trust_registry,
    build_effective_output_manifest,
    build_review_signature_request,
    cancel_run,
    claims_status,
    create_run,
    resume_run,
    review_run,
    reviewer_trust_status,
    revise_task_output,
    sign_effective_output_manifest,
    sign_review_decision,
    status_run,
    verify_effective_output_manifest,
    verify_effective_output_manifest_signature,
    verify_run,
)
from research_os_mvp.signing import load_ed25519_public_key
from research_os_mvp.trust import (
    reviewer_trust_registry_template,
    seal_reviewer_trust_registry,
    validate_reviewer_trust_registry,
)
from research_os_mvp.wizard import (
    category_catalog_json,
    render_run_artifacts,
    run_easy_wizard,
    run_wizard,
)


def _print_result(result: dict[str, object]) -> None:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


def _configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def _write_immutable_cli_artifact(path: Path, content: str) -> Path:
    if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
        raise MVPError("输出目标必须位于已存在的普通目录中")
    if path.exists():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise MVPError(f"输出目标已有不同内容：{path}")
        return path.resolve()
    write_text_atomic(path, content)
    return path.resolve()


def _read_bounded_json_artifact(path: Path, label: str) -> object:
    if path.is_symlink() or not path.is_file():
        raise MVPError(f"{label}必须是普通 JSON 文件")
    if path.stat().st_size > 4 * 1024 * 1024:
        raise MVPError(f"{label}超过 4 MiB")
    return read_json(path)


def _creation_trust_options(args: argparse.Namespace) -> dict[str, object]:
    registry_path = getattr(args, "reviewer_trust", None)
    actor = getattr(args, "trust_actor", None)
    if registry_path is None and actor is None:
        return {}
    if registry_path is None or actor is None:
        raise MVPError("--reviewer-trust 与 --trust-by 必须同时提供")
    return {
        "reviewer_trust_registry": _read_bounded_json_artifact(
            registry_path,
            "Reviewer 信任策略",
        ),
        "reviewer_trust_actor": actor,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-os-mvp",
        description="Isolated, non-canonical Research-OS MVP prototype",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate one JSON Builder Pack")
    validate_parser.add_argument("pack", type=Path)

    create_parser = subparsers.add_parser(
        "create",
        aliases=["创建"],
        help="create a three-Task Pack from a natural-language goal",
    )
    create_parser.add_argument("goal")
    create_parser.add_argument("--category", default="auto")
    create_parser.add_argument("--context", default="")
    create_parser.add_argument("--criterion", action="append", default=[])
    create_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    create_parser.add_argument("--output", type=Path)

    quickstart_parser = subparsers.add_parser(
        "quickstart",
        aliases=["快速开始"],
        help="create a Pack from a goal and run Task 1 immediately",
    )
    quickstart_parser.add_argument("goal")
    quickstart_parser.add_argument("--category", default="auto")
    quickstart_parser.add_argument("--context", default="")
    quickstart_parser.add_argument("--criterion", action="append", default=[])
    quickstart_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    quickstart_parser.add_argument("--run-id")
    quickstart_parser.add_argument("--reviewer-trust", type=Path)
    quickstart_parser.add_argument("--trust-by", dest="trust_actor")

    subparsers.add_parser(
        "categories",
        aliases=["场景"],
        help="list the eight natural-language scenario profiles",
    )

    start_parser = subparsers.add_parser("start", help="create a Run and execute its next Task")
    start_parser.add_argument("pack", type=Path)
    start_parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    start_parser.add_argument("--run-id")
    start_parser.add_argument("--reviewer-trust", type=Path)
    start_parser.add_argument("--trust-by", dest="trust_actor")

    trust_template_parser = subparsers.add_parser(
        "reviewer-trust-template",
        help="write an editable project-level Reviewer trust registry draft",
    )
    trust_template_parser.add_argument("--output", required=True, type=Path)

    seal_trust_parser = subparsers.add_parser(
        "seal-reviewer-trust",
        help="normalize a Reviewer trust draft and add its canonical self-hash",
    )
    seal_trust_parser.add_argument("draft", type=Path)
    seal_trust_parser.add_argument("--output", required=True, type=Path)

    validate_trust_parser = subparsers.add_parser(
        "validate-reviewer-trust",
        help="validate one sealed Reviewer trust registry",
    )
    validate_trust_parser.add_argument("registry", type=Path)

    bind_trust_parser = subparsers.add_parser(
        "bind-reviewer-trust",
        help="bind an immutable trust registry before the first Reviewer decision",
    )
    bind_trust_parser.add_argument("run_dir", type=Path)
    bind_trust_parser.add_argument("registry", type=Path)
    bind_trust_parser.add_argument("--by", required=True, dest="actor")

    trust_status_parser = subparsers.add_parser(
        "reviewer-trust-status",
        help="show Reviewer trust requirements and their signature status",
    )
    trust_status_parser.add_argument("run_dir", type=Path)

    approve_parser = subparsers.add_parser(
        "approve",
        help="compatibility shorthand for a formal Approved Reviewer decision",
    )
    approve_parser.add_argument("run_dir", type=Path)
    approve_parser.add_argument("--by", required=True, dest="approver")
    approve_parser.add_argument("--note", default="")

    review_parser = subparsers.add_parser(
        "review",
        help="record an Approved, Changes Requested, or Rejected Reviewer decision",
    )
    review_parser.add_argument("run_dir", type=Path)
    review_parser.add_argument("--by", required=True, dest="reviewer")
    review_parser.add_argument(
        "--decision",
        required=True,
        choices=("approved", "changes-requested", "rejected"),
    )
    review_parser.add_argument("--note", default="")

    sign_review_parser = subparsers.add_parser(
        "sign-review",
        help="attach an OpenSSH Ed25519 signature to one Reviewer decision",
    )
    sign_review_parser.add_argument("run_dir", type=Path)
    sign_review_parser.add_argument("--identity", required=True)
    sign_review_parser.add_argument("--key", required=True, type=Path)
    sign_review_parser.add_argument("--public-key", required=True, type=Path)
    sign_review_parser.add_argument("--review-hash")

    review_request_parser = subparsers.add_parser(
        "review-signing-request",
        help="write the exact Reviewer signature payload for an offline signer",
    )
    review_request_parser.add_argument("run_dir", type=Path)
    review_request_parser.add_argument("--identity", required=True)
    review_request_parser.add_argument("--public-key", required=True, type=Path)
    review_request_parser.add_argument("--review-hash")
    review_request_parser.add_argument("--output", required=True, type=Path)

    attach_signature_parser = subparsers.add_parser(
        "attach-review-signature",
        help="verify and append an externally produced Reviewer signature",
    )
    attach_signature_parser.add_argument("run_dir", type=Path)
    attach_signature_parser.add_argument("--identity", required=True)
    attach_signature_parser.add_argument("--public-key", required=True, type=Path)
    attach_signature_parser.add_argument("--signature", required=True, type=Path)
    attach_signature_parser.add_argument("--review-hash")

    revise_parser = subparsers.add_parser(
        "revise",
        help="append an immutable Task-output revision after Changes Requested",
    )
    revise_parser.add_argument("run_dir", type=Path)
    revise_parser.add_argument("--by", required=True, dest="revised_by")
    revise_parser.add_argument("--review-hash", required=True)
    revise_parser.add_argument("--note", required=True)
    revision_content = revise_parser.add_mutually_exclusive_group(required=True)
    revision_content.add_argument("--content")
    revision_content.add_argument("--content-file", type=Path)

    resume_parser = subparsers.add_parser("resume", help="resume after explicit approval")
    resume_parser.add_argument("run_dir", type=Path)

    cancel_parser = subparsers.add_parser(
        "cancel",
        help="cancel an unfinished Run while preserving its audit trail",
    )
    cancel_parser.add_argument("run_dir", type=Path)
    cancel_parser.add_argument("--by", required=True, dest="cancelled_by")
    cancel_parser.add_argument("--reason", required=True)

    status_parser = subparsers.add_parser("status", help="show verified Run status")
    status_parser.add_argument("run_dir", type=Path)

    verify_parser = subparsers.add_parser("verify", help="verify hashes and state invariants")
    verify_parser.add_argument("run_dir", type=Path)

    claims_parser = subparsers.add_parser(
        "claims",
        help="show verified Claim records and counts without changing governance state",
    )
    claims_parser.add_argument("run_dir", type=Path)

    effective_parser = subparsers.add_parser(
        "effective-outputs",
        help="print the deterministic Reviewer-Approved output manifest",
    )
    effective_parser.add_argument("run_dir", type=Path)

    verify_effective_parser = subparsers.add_parser(
        "verify-effective-manifest",
        help="verify one detached Effective Output Manifest JSON file",
    )
    verify_effective_parser.add_argument("manifest", type=Path)

    sign_effective_parser = subparsers.add_parser(
        "sign-effective-manifest",
        help="create a detached OpenSSH Ed25519 attestation for one manifest",
    )
    sign_effective_parser.add_argument("manifest", type=Path)
    sign_effective_parser.add_argument("--identity", required=True)
    sign_effective_parser.add_argument("--key", required=True, type=Path)
    sign_effective_parser.add_argument("--public-key", required=True, type=Path)
    sign_effective_parser.add_argument("--output", required=True, type=Path)

    verify_effective_signature_parser = subparsers.add_parser(
        "verify-effective-manifest-signature",
        help="verify a detached Ed25519 attestation for one effective manifest",
    )
    verify_effective_signature_parser.add_argument("manifest", type=Path)
    verify_effective_signature_parser.add_argument("attestation", type=Path)

    show_parser = subparsers.add_parser(
        "show",
        aliases=["查看"],
        help="show verified Evidence and Reports for one Run",
    )
    show_parser.add_argument("run_dir", type=Path)

    easy_parser = subparsers.add_parser(
        "easy",
        aliases=["简易模式"],
        help="open the beginner-friendly Chinese workflow",
    )
    easy_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    wizard_parser = subparsers.add_parser(
        "wizard",
        aliases=["向导"],
        help="open the Chinese interactive menu",
    )
    wizard_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    configure_ai_parser = subparsers.add_parser(
        "configure-ollama",
        help="enable the local Ollama provider for easy mode",
    )
    configure_ai_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    configure_ai_parser.add_argument("--model", default="qwen2.5:7b")
    configure_ai_parser.add_argument("--review-model")
    configure_ai_parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    configure_ai_parser.add_argument(
        "--health-timeout-seconds",
        type=int,
        default=DEFAULT_HEALTH_TIMEOUT_SECONDS,
        help="Ollama health-check timeout only",
    )
    configure_ai_parser.add_argument(
        "--stream-idle-timeout-seconds",
        type=int,
        default=DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
        help="maximum silence between streamed Ollama chunks",
    )
    configure_ai_parser.add_argument(
        "--generation-budget-seconds",
        type=int,
        default=DEFAULT_GENERATION_BUDGET_SECONDS,
        help="independent total wall-clock budget for one generation",
    )
    configure_ai_parser.add_argument("--max-output-tokens", type=int, default=1536)
    configure_ai_parser.add_argument(
        "--manual",
        action="store_true",
        help="do not automatically call AI at Task 2",
    )

    ai_status_parser = subparsers.add_parser(
        "ollama-status",
        help="check the configured local Ollama provider",
    )
    ai_status_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    benchmark_parser = subparsers.add_parser(
        "benchmark-ollama",
        help="benchmark installed local Ollama models with one fixed research prompt",
    )
    benchmark_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    benchmark_parser.add_argument("--model", action="append", dest="models", required=True)
    benchmark_parser.add_argument("--output", type=Path)

    obsidian_parser = subparsers.add_parser(
        "export-obsidian",
        help="export one verified Run as an immutable Obsidian snapshot",
    )
    obsidian_parser.add_argument("run_dir", type=Path)
    obsidian_parser.add_argument("vault_dir", type=Path)

    git_parser = subparsers.add_parser(
        "git-snapshot",
        help="record a Git snapshot as Task-2 Evidence",
    )
    git_parser.add_argument("run_dir", type=Path)
    git_parser.add_argument("repo", type=Path)
    git_parser.add_argument(
        "--run-tests",
        action="store_true",
        help="explicitly authorize execution of the detected project test command",
    )

    checkpoint_parser = subparsers.add_parser(
        "checkpoint-status",
        help="show the latest verified SQLite checkpoint for one Run",
    )
    checkpoint_parser.add_argument("run_dir", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            loaded = load_pack(args.pack)
            _print_result(
                {
                    "result": "VALID",
                    "pack_id": loaded.data["pack_id"],
                    "mission_id": loaded.data["mission"]["mission_id"],
                    "task_count": len(loaded.data["mission"]["tasks"]),
                    "canonical_sha256": loaded.canonical_sha256,
                }
            )
        elif args.command in {"create", "创建"}:
            generated = create_pack_from_goal(
                args.goal,
                category=args.category,
                context=args.context,
                criteria=args.criterion,
                workspace=args.workspace,
                output=args.output,
            )
            _print_result(
                {
                    "result": "CREATED" if not generated.reused else "REUSED",
                    "path": str(generated.path),
                    "category": generated.category,
                    "category_name": generated.category_name,
                    "pack_id": generated.data["pack_id"],
                    "mission_id": generated.data["mission"]["mission_id"],
                    "task_count": 3,
                    "canonical_sha256": generated.canonical_sha256,
                }
            )
        elif args.command in {"quickstart", "快速开始"}:
            trust_options = _creation_trust_options(args)
            generated = create_pack_from_goal(
                args.goal,
                category=args.category,
                context=args.context,
                criteria=args.criterion,
                workspace=args.workspace,
            )
            status = create_run(
                generated.path,
                args.workspace / "runs",
                args.run_id,
                **trust_options,
            )
            status.update(
                {
                    "result": "PAUSED_AT_HUMAN_GATE",
                    "generated_pack": str(generated.path),
                    "category": generated.category,
                    "category_name": generated.category_name,
                    "pack_reused": generated.reused,
                }
            )
            _print_result(status)
        elif args.command in {"categories", "场景"}:
            _print_result(category_catalog_json())
        elif args.command == "start":
            _print_result(
                create_run(
                    args.pack,
                    args.runs_dir,
                    args.run_id,
                    **_creation_trust_options(args),
                )
            )
        elif args.command == "reviewer-trust-template":
            template = reviewer_trust_registry_template()
            output = _write_immutable_cli_artifact(
                args.output,
                json.dumps(
                    template,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
            )
            _print_result(
                {
                    "schema_version": template["schema_version"],
                    "registry_id": template["registry_id"],
                    "output": str(output),
                    "next_step": "replace placeholders, then run seal-reviewer-trust",
                }
            )
        elif args.command == "seal-reviewer-trust":
            registry = seal_reviewer_trust_registry(
                _read_bounded_json_artifact(args.draft, "Reviewer 信任策略草稿")
            )
            output = _write_immutable_cli_artifact(
                args.output,
                json.dumps(
                    registry,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
            )
            _print_result(
                {
                    "registry_id": registry["registry_id"],
                    "registry_version": registry["version"],
                    "registry_sha256": registry["registry_sha256"],
                    "key_count": len(registry["keys"]),
                    "requirement_count": len(registry["requirements"]),
                    "output": str(output),
                }
            )
        elif args.command == "validate-reviewer-trust":
            registry = validate_reviewer_trust_registry(
                _read_bounded_json_artifact(args.registry, "Reviewer 信任策略")
            )
            _print_result(
                {
                    "registry_id": registry["registry_id"],
                    "registry_version": registry["version"],
                    "registry_sha256": registry["registry_sha256"],
                    "key_count": len(registry["keys"]),
                    "requirement_count": len(registry["requirements"]),
                    "integrity": "verified",
                }
            )
        elif args.command == "bind-reviewer-trust":
            _print_result(
                bind_reviewer_trust_registry(
                    args.run_dir,
                    _read_bounded_json_artifact(
                        args.registry, "Reviewer 信任策略"
                    ),
                    actor=args.actor,
                )
            )
        elif args.command == "reviewer-trust-status":
            _print_result(reviewer_trust_status(args.run_dir))
        elif args.command == "approve":
            _print_result(
                approve_run(args.run_dir, approver=args.approver, note=args.note)
            )
        elif args.command == "review":
            decisions = {
                "approved": "Approved",
                "changes-requested": "Changes Requested",
                "rejected": "Rejected",
            }
            _print_result(
                review_run(
                    args.run_dir,
                    reviewer=args.reviewer,
                    decision=decisions[args.decision],
                    note=args.note,
                )
            )
        elif args.command == "sign-review":
            _print_result(
                sign_review_decision(
                    args.run_dir,
                    signer_identity=args.identity,
                    private_key_path=args.key,
                    public_key_path=args.public_key,
                    review_hash=args.review_hash,
                )
            )
        elif args.command == "review-signing-request":
            public_key = load_ed25519_public_key(args.public_key)
            request = build_review_signature_request(
                args.run_dir,
                signer_identity=args.identity,
                public_key=public_key,
                review_hash=args.review_hash,
            )
            output = _write_immutable_cli_artifact(args.output, request["payload"])
            _print_result(
                {
                    key: value
                    for key, value in request.items()
                    if key != "payload"
                }
                | {"output": str(output)}
            )
        elif args.command == "attach-review-signature":
            if args.signature.is_symlink() or not args.signature.is_file():
                raise MVPError("Reviewer 签名必须是普通文件")
            if args.signature.stat().st_size > 16_000:
                raise MVPError("Reviewer 签名文件过大")
            public_key = load_ed25519_public_key(args.public_key)
            signature = args.signature.read_text(encoding="utf-8")
            _print_result(
                attach_review_signature(
                    args.run_dir,
                    signer_identity=args.identity,
                    public_key=public_key,
                    signature=signature,
                    review_hash=args.review_hash,
                )
            )
        elif args.command == "revise":
            if args.content_file is not None:
                if args.content_file.is_symlink() or not args.content_file.is_file():
                    raise MVPError("修订内容文件必须是普通文件")
                if args.content_file.stat().st_size > 2 * 1024 * 1024:
                    raise MVPError("修订内容文件超过 2 MiB")
                content = args.content_file.read_text(encoding="utf-8")
            else:
                content = args.content
            _print_result(
                revise_task_output(
                    args.run_dir,
                    content=content,
                    revised_by=args.revised_by,
                    note=args.note,
                    review_decision_hash=args.review_hash,
                )
            )
        elif args.command == "resume":
            _print_result(resume_run(args.run_dir))
        elif args.command == "cancel":
            _print_result(
                cancel_run(
                    args.run_dir,
                    cancelled_by=args.cancelled_by,
                    reason=args.reason,
                )
            )
        elif args.command == "status":
            _print_result(status_run(args.run_dir))
        elif args.command == "verify":
            _print_result(verify_run(args.run_dir))
        elif args.command == "claims":
            _print_result(claims_status(args.run_dir))
        elif args.command == "effective-outputs":
            _print_result(build_effective_output_manifest(args.run_dir))
        elif args.command == "verify-effective-manifest":
            if args.manifest.is_symlink() or not args.manifest.is_file():
                raise MVPError("有效输出 Manifest 必须是普通 JSON 文件")
            if args.manifest.stat().st_size > 4 * 1024 * 1024:
                raise MVPError("有效输出 Manifest 超过 4 MiB")
            _print_result(verify_effective_output_manifest(read_json(args.manifest)))
        elif args.command == "sign-effective-manifest":
            if args.manifest.is_symlink() or not args.manifest.is_file():
                raise MVPError("有效输出 Manifest 必须是普通 JSON 文件")
            if args.manifest.stat().st_size > 4 * 1024 * 1024:
                raise MVPError("有效输出 Manifest 超过 4 MiB")
            attestation = sign_effective_output_manifest(
                read_json(args.manifest),
                signer_identity=args.identity,
                private_key_path=args.key,
                public_key_path=args.public_key,
            )
            output = _write_immutable_cli_artifact(
                args.output,
                json.dumps(
                    attestation,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
            )
            _print_result(
                {
                    "run_id": attestation["run_id"],
                    "manifest_sha256": attestation["manifest_sha256"],
                    "attestation_sha256": attestation["attestation_sha256"],
                    "signer_identity": attestation["signer_identity"],
                    "public_key_fingerprint": attestation[
                        "public_key_fingerprint"
                    ],
                    "output": str(output),
                }
            )
        elif args.command == "verify-effective-manifest-signature":
            for artifact in (args.manifest, args.attestation):
                if artifact.is_symlink() or not artifact.is_file():
                    raise MVPError("Manifest 与签名证明都必须是普通 JSON 文件")
                if artifact.stat().st_size > 4 * 1024 * 1024:
                    raise MVPError("Manifest 或签名证明超过 4 MiB")
            _print_result(
                verify_effective_output_manifest_signature(
                    read_json(args.manifest),
                    read_json(args.attestation),
                )
            )
        elif args.command in {"show", "查看"}:
            print(render_run_artifacts(args.run_dir))
        elif args.command in {"easy", "简易模式"}:
            return run_easy_wizard(args.workspace)
        elif args.command in {"wizard", "向导"}:
            return run_wizard(args.workspace)
        elif args.command == "configure-ollama":
            path = save_ollama_settings(
                args.workspace,
                model=args.model,
                reviewer_model=args.review_model,
                endpoint=args.endpoint,
                health_timeout_seconds=args.health_timeout_seconds,
                stream_idle_timeout_seconds=args.stream_idle_timeout_seconds,
                generation_budget_seconds=args.generation_budget_seconds,
                max_output_tokens=args.max_output_tokens,
                automatic_research=not args.manual,
            )
            settings = load_ai_settings(args.workspace)
            assert settings is not None
            result = check_ollama(settings)
            result.update(
                {
                    "result": "CONFIGURED",
                    "settings": str(path),
                    "model_guidance": (
                        f"已选择 {settings.model}。较大的模型通常质量更好，"
                        "但一次完整生成可能需要数分钟；若过慢，"
                        "可重新运行 configure-ollama 并用 --model 选择更小模型。"
                    ),
                }
            )
            _print_result(result)
        elif args.command == "ollama-status":
            settings = load_ai_settings(args.workspace)
            if settings is None:
                raise MVPError("本地 AI 尚未配置")
            _print_result(check_ollama(settings))
        elif args.command == "benchmark-ollama":
            settings = load_ai_settings(args.workspace)
            if settings is None:
                raise MVPError("本地 AI 尚未配置")
            report = run_ollama_benchmark(settings, args.models)
            output = args.output or default_benchmark_path(args.workspace)
            saved = save_benchmark_report(report, output)
            _print_result(benchmark_console_summary(report, saved))
        elif args.command == "export-obsidian":
            _print_result(export_run_to_obsidian(args.run_dir, args.vault_dir))
        elif args.command == "git-snapshot":
            _print_result(
                record_git_snapshot_evidence(
                    args.run_dir,
                    args.repo,
                    run_tests=args.run_tests,
                )
            )
        elif args.command == "checkpoint-status":
            checkpoint_path = args.run_dir / RUNTIME_DIR / CHECKPOINT_FILE
            if not checkpoint_path.is_file():
                verify_run(args.run_dir)
            _print_result(read_checkpoint(args.run_dir))
        else:
            parser.error(f"unsupported command: {args.command}")
    except IntegrityError as exc:
        print(f"INTEGRITY ERROR: {exc}", file=sys.stderr)
        return 3
    except MVPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0
