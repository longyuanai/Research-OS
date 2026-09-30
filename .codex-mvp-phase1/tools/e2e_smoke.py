"""Run the guided product path against a real local Ollama model.

Exit codes:
    0: the real product path completed and an Ollama Evidence verified
    1: the product path or its evidence verification failed
    2: Ollama settings, service, or the configured model are unavailable
"""

# ruff: noqa: I001 -- direct script execution needs PROJECT_ROOT on sys.path first.

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_os_mvp.ai import (
    check_ollama,
    generate_research,
    load_ai_settings,
    save_ollama_settings,
)
from research_os_mvp.errors import MVPError
from research_os_mvp.runtime import claims_coverage_status, claims_status, verify_run
from research_os_mvp.wizard import _confirm_ai_draft_claims, run_easy_wizard


EXIT_OK = 0
EXIT_FAILED = 1
EXIT_SKIPPED = 2
MIN_AI_CONTENT_CHARS = 100

# Kept in the same order as
# tests/test_wizard.py::test_easy_wizard_completes_with_three_yes_answers.
SCRIPTED_ANSWERS = (
    "1",
    "技术选型：比较 Python、TypeScript 和 Rust",
    "1000 元，一个月",
    "本地 Windows",
    "离线运行",
    "开发效率",
    "y",
    "y",
    "y",
    "y",
    "0",
)


class SmokeFailure(RuntimeError):
    """Raised when the E2E product path or its persisted evidence is invalid."""


def _configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Research-OS Easy Mode with the real configured Ollama model.",
    )
    parser.add_argument(
        "--settings-workspace",
        type=Path,
        default=PROJECT_ROOT / "workspace",
        help="read-only workspace containing the Ollama settings.json",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "e2e-runs",
        help="root for isolated E2E workspaces (never use the product workspace)",
    )
    parser.add_argument(
        "--claims-from-run",
        type=Path,
        help=(
            "copy an existing verified Run and exercise human Claim classification "
            "without calling Ollama"
        ),
    )
    return parser.parse_args()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _new_e2e_workspace(output_root: Path, settings_workspace: Path) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dt%H%M%Sz")
    workspace = (
        output_root / f"smoke-{timestamp}-{uuid.uuid4().hex[:8]}"
    ).resolve()
    product_workspace = (PROJECT_ROOT / "workspace").resolve()
    source_workspace = settings_workspace.resolve()
    if _is_within(workspace, product_workspace) or _is_within(
        workspace,
        source_workspace,
    ):
        raise SmokeFailure(
            "E2E 输出目录落入真实/配置 workspace；请使用独立的 --output-root"
        )
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def _copy_settings_to_e2e_workspace(workspace: Path, settings: Any) -> None:
    save_ollama_settings(
        workspace,
        model=settings.model,
        reviewer_model=settings.reviewer_model,
        endpoint=settings.endpoint,
        health_timeout_seconds=settings.health_timeout_seconds,
        stream_idle_timeout_seconds=settings.stream_idle_timeout_seconds,
        generation_budget_seconds=settings.generation_budget_seconds,
        max_output_tokens=settings.max_output_tokens,
        automatic_research=True,
    )


def _copy_run_for_claim_smoke(source_run: Path, output_root: Path) -> Path:
    source = source_run.resolve()
    timestamp = datetime.now(UTC).strftime("%Y%m%dt%H%M%Sz")
    workspace = (
        output_root / f"claim-smoke-{timestamp}-{uuid.uuid4().hex[:8]}"
    ).resolve()
    product_workspace = (PROJECT_ROOT / "workspace").resolve()
    if _is_within(workspace, product_workspace) or _is_within(workspace, source):
        raise SmokeFailure("Claim E2E 输出目录必须独立于产品 workspace 和源 Run")
    target = workspace / "runs" / source.name
    target.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".runtime"),
    )
    verify_run(target)
    return target


def _scripted_input(answers: Iterator[str]):
    claim_confirmation_complete = False

    def read(prompt: str) -> str:
        nonlocal claim_confirmation_complete
        if (
            "Reviewer 决定" in prompt
            and "C " in prompt
            and not claim_confirmation_complete
        ):
            answer = "c"
        elif prompt.startswith("请选择 1/2/3/4"):
            answer = "1"
        elif "全部确认后输入 CONFIRM" in prompt:
            answer = "CONFIRM"
        elif prompt.startswith("确认人"):
            answer = "E2E Human"
            claim_confirmation_complete = True
        else:
            try:
                answer = next(answers)
            except StopIteration as exc:
                raise SmokeFailure(
                    f"脚本化输入提前耗尽，最后提示为：{prompt}"
                ) from exc
        print(f"{prompt}{answer}", flush=True)
        return answer

    return read


def _load_evidence(run_dir: Path) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for path in sorted((run_dir / "evidence").glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SmokeFailure(f"Evidence 无法读取：{path}：{exc}") from exc
        if not isinstance(value, dict):
            raise SmokeFailure(f"Evidence 不是 JSON 对象：{path}")
        evidence.append(value)
    return evidence


def _ai_elapsed_seconds(evidence: dict[str, Any]) -> float:
    method = evidence.get("method")
    if not isinstance(method, str):
        raise SmokeFailure("ollama:// Evidence 缺少 method，无法读取 AI 生成耗时")
    match = re.search(r"耗时 ([0-9]+(?:\.[0-9]+)?) 秒", method)
    if match is None:
        raise SmokeFailure("ollama:// Evidence 的 method 未记录 AI 生成耗时")
    return float(match.group(1))


def _verify_e2e_run(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        status = verify_run(run_dir)
    except (MVPError, OSError, json.JSONDecodeError) as exc:
        raise SmokeFailure(f"verify 未通过：{exc}") from exc
    if status.get("integrity") != "verified":
        raise SmokeFailure(
            f"verify 未返回 integrity=verified：{status.get('integrity')!r}"
        )

    evidence = _load_evidence(run_dir)
    ollama_evidence = [
        item
        for item in evidence
        if isinstance(item.get("source"), str)
        and item["source"].startswith("ollama://")
    ]
    if not ollama_evidence:
        raise SmokeFailure("缺少 source 以 ollama:// 开头的 Evidence")
    usable = [
        item
        for item in ollama_evidence
        if isinstance(item.get("content"), str)
        and len(item["content"].strip()) > MIN_AI_CONTENT_CHARS
    ]
    if not usable:
        lengths = [
            len(item.get("content", ""))
            if isinstance(item.get("content"), str)
            else 0
            for item in ollama_evidence
        ]
        raise SmokeFailure(
            "ollama:// Evidence 正文为空或过短；"
            f"要求 > {MIN_AI_CONTENT_CHARS} 字符，实际长度={lengths}"
        )
    return evidence, usable[0]


def _print_summary(
    *,
    total_elapsed: float,
    run_dir: Path,
    evidence: list[dict[str, Any]],
    ai_evidence: dict[str, Any],
) -> None:
    content = str(ai_evidence["content"]).strip()
    print("\n=== E2E 证据摘要 ===")
    print(f"总耗时：{total_elapsed:.3f} 秒")
    print(f"AI 生成耗时：{_ai_elapsed_seconds(ai_evidence):.3f} 秒")
    print(f"Evidence 条数：{len(evidence)}")
    for item in evidence:
        evidence_id = item.get("evidence_id", item.get("id", "<缺少 ID>"))
        print(f"- {evidence_id} | {item.get('source', '<缺少 source>')}")
    print(f"ollama:// Evidence：{ai_evidence['source']}")
    print("ollama:// 正文前 200 字：")
    print(content[:200])
    print(f"Run 目录：{run_dir.resolve()}")
    print("E2E PASS：真实 Ollama Evidence 存在、正文长度合理且 verify 通过。")
    print("退出码：0")


def _run_claim_smoke(source_run: Path, output_root: Path) -> int:
    copied_run = _copy_run_for_claim_smoke(source_run, output_root)
    evidence, ai_evidence = _verify_e2e_run(copied_run)
    task_id = ai_evidence.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise SmokeFailure("ollama:// Evidence 缺少 task_id")
    print("C4 Claim 模式：复用既有真实草稿，不调用 Ollama。")
    print(f"源 Run（只读）：{source_run.resolve()}")
    print(f"隔离副本：{copied_run}")
    print(f"Evidence 条数：{len(evidence)}；AI Evidence：{ai_evidence['source']}")
    recorded = _confirm_ai_draft_claims(
        copied_run,
        task_id,
        input,
        lambda line: print(line, flush=True),
    )
    if recorded is None:
        raise SmokeFailure("人工分类未完整确认；隔离副本没有记录 Claim")

    view = claims_status(copied_run)
    coverage = claims_coverage_status(copied_run)
    records = view.get("records", [])
    if len(records) != 1:
        raise SmokeFailure(f"应有 1 个 Claims 记录，实际为 {len(records)}")
    claims = records[0].get("claims", [])
    fabricated = [item for item in claims if "来源：" in item.get("text", "")]
    print("\n=== C4 真实草稿结果 ===")
    print(f"候选/已确认 Claim：{len(claims)} 条")
    print(f"含草稿内“来源：...”的 Claim：{len(fabricated)} 条")
    for index, claim in enumerate(fabricated, start=1):
        print(f"{index}. {claim['text']}")
        print(
            f"   kind={claim['kind']}；support={claim['support']}；"
            f"evidence_ids={claim['evidence_ids']}"
        )
    print(f"hard_gate_pass={coverage['hard_gate_pass']}")
    print(f"fact_coverage={coverage['fact_coverage']}")
    print(f"unsupported_fact_count={coverage['unsupported_fact_count']}")
    print(f"claims_confirmed={view['claims_confirmed']}")
    print(f"verify={verify_run(copied_run)['integrity']}")
    print(f"结果 Run：{copied_run}")
    print("源 Run 保持只读；本模式未调用 Ollama。")
    print("退出码：0")
    return EXIT_OK


def main() -> int:
    _configure_utf8_stdio()
    started = time.monotonic()
    args = _parse_args()
    settings_workspace = args.settings_workspace.resolve()

    if args.claims_from_run is not None:
        try:
            return _run_claim_smoke(args.claims_from_run, args.output_root)
        except (SmokeFailure, MVPError, OSError, json.JSONDecodeError) as exc:
            print(f"C4 E2E FAILED：{exc}", file=sys.stderr)
            return EXIT_FAILED

    try:
        settings = load_ai_settings(settings_workspace)
    except (MVPError, OSError, json.JSONDecodeError) as exc:
        print(f"E2E SKIPPED：Ollama 配置不可用：{exc}", file=sys.stderr)
        return EXIT_SKIPPED
    if settings is None:
        print(
            f"E2E SKIPPED：未找到 Ollama 配置：{settings_workspace / 'settings.json'}",
            file=sys.stderr,
        )
        return EXIT_SKIPPED

    print(f"Ollama 预检：{settings.endpoint}，模型 {settings.model}", flush=True)
    try:
        availability = check_ollama(settings)
    except (MVPError, OSError, json.JSONDecodeError) as exc:
        print(f"E2E SKIPPED：Ollama 服务不可用：{exc}", file=sys.stderr)
        return EXIT_SKIPPED
    if not availability.get("model_available"):
        available = ", ".join(availability.get("available_models", [])) or "（无）"
        print(
            f"E2E SKIPPED：模型 {settings.model} 不可用；本机模型：{available}",
            file=sys.stderr,
        )
        return EXIT_SKIPPED
    print(
        "Ollama 预检通过："
        f"服务耗时 {availability['health_check_elapsed_seconds']:.3f} 秒，"
        f"模型 {settings.model} 已安装。",
        flush=True,
    )

    try:
        workspace = _new_e2e_workspace(args.output_root, settings_workspace)
        _copy_settings_to_e2e_workspace(workspace, settings)
        print(f"E2E 专用 workspace：{workspace}", flush=True)
        answers = iter(SCRIPTED_ANSWERS)
        wizard_result = run_easy_wizard(
            workspace=workspace,
            input_fn=_scripted_input(answers),
            output_fn=lambda line: print(line, flush=True),
            ai_generate_fn=generate_research,
        )
        if wizard_result != 0:
            raise SmokeFailure(f"run_easy_wizard 返回非零值：{wizard_result}")
        try:
            unexpected = next(answers)
        except StopIteration:
            pass
        else:
            raise SmokeFailure(f"脚本化输入未全部消费，下一项为：{unexpected!r}")

        run_dirs = sorted((workspace / "runs").glob("run-*"))
        if len(run_dirs) != 1:
            raise SmokeFailure(f"应生成 1 个 Run，实际生成 {len(run_dirs)} 个")
        run_dir = run_dirs[0]
        evidence, ai_evidence = _verify_e2e_run(run_dir)
        _print_summary(
            total_elapsed=time.monotonic() - started,
            run_dir=run_dir,
            evidence=evidence,
            ai_evidence=ai_evidence,
        )
        return EXIT_OK
    except (SmokeFailure, MVPError, OSError, json.JSONDecodeError) as exc:
        print(f"E2E FAILED：{exc}", file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
