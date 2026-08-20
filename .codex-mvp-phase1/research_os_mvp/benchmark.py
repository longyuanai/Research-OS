from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from research_os_mvp.ai import (
    LOCAL_RESEARCH_SYSTEM_PROMPT,
    MODEL_PATTERN,
    AIProviderError,
    AIResponse,
    AISettings,
    check_ollama,
    generate_research,
)
from research_os_mvp.integrity import sha256_text, utc_now, write_json_atomic

BENCHMARK_SCHEMA_VERSION = "research-os-mvp-ollama-benchmark/0.1"
BENCHMARK_PROMPT = """
你没有实时联网能力。请为以下任务生成一份研究准备草稿：

目标：预算 1000 元，比较 ESP32、STM32 和树莓派，选择适合本地环境监测原型的主控。

必须使用中文，并覆盖以下内容：
1. 候选项及各自适用边界；
2. 功能接口、实时性、算力内存、功耗散热、开发调试、供货成本六个比较维度；
3. 将已知事实、推断和建议分开；
4. 明确列出未知/待查证项，不编造参数、来源或链接；
5. 给出至少三个可执行验证实验；
6. 只给条件式建议，说明什么新证据会改变选择。
""".strip()
BENCHMARK_CANDIDATES = ("ESP32", "STM32", "树莓派")
MIN_BENCHMARK_CHARS = 600
QUALIFIED_SCORE = 75
UNSUPPORTED_PRECISION_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:\.\d+)?\s*"
    r"(?:k?hz|mhz|ghz|kb|mb|gb|mw|w|v|ms|毫秒|元|美元|%)(?![A-Za-z0-9])",
    re.IGNORECASE,
)


BenchmarkGenerateFn = Callable[[AISettings, str], AIResponse]


def evaluate_benchmark_response(
    content: str,
    *,
    truncated: bool = False,
) -> dict[str, Any]:
    normalized = content.lower()
    precision_input = (
        content.replace("ESP32", "ESP")
        .replace("esp32", "esp")
        .replace("STM32", "STM")
        .replace("stm32", "stm")
        .replace("1000 元", "预算")
        .replace("1000元", "预算")
    )
    unsupported_precision = UNSUPPORTED_PRECISION_PATTERN.findall(precision_input)
    checks = {
        "minimum_length": len(content) >= MIN_BENCHMARK_CHARS,
        "all_candidates": all(candidate.lower() in normalized for candidate in BENCHMARK_CANDIDATES),
        "comparison_dimensions": "比较" in content and "维度" in content,
        "fact_inference_separation": "事实" in content and "推断" in content,
        "uncertainty_disclosure": "未知" in content or "待查证" in content,
        "validation_plan": "验证" in content
        and sum(content.count(marker) for marker in ("实验", "测试", "测量")) >= 3,
        "conditional_recommendation": any(
            marker in content for marker in ("如果", "若", "条件", "前提")
        )
        and any(marker in content for marker in ("建议", "推荐", "选择")),
        "no_fabricated_url": "http://" not in normalized and "https://" not in normalized,
        "no_unsupported_precision": not unsupported_precision,
        "complete_response": not truncated,
    }
    passed = [name for name, value in checks.items() if value]
    failed = [name for name, value in checks.items() if not value]
    score = round(len(passed) * 100 / len(checks))
    return {
        "score": score,
        "qualified": score >= QUALIFIED_SCORE
        and not truncated
        and not unsupported_precision,
        "passed_checks": passed,
        "failed_checks": failed,
        "unsupported_precision_examples": unsupported_precision[:10],
    }


def run_ollama_benchmark(
    settings: AISettings,
    models: Sequence[str],
    *,
    prompt: str = BENCHMARK_PROMPT,
    generate_fn: BenchmarkGenerateFn | None = None,
) -> dict[str, Any]:
    selected: list[str] = []
    for model in models:
        if not isinstance(model, str) or not MODEL_PATTERN.fullmatch(model):
            raise AIProviderError(f"Ollama 基准模型名称格式不正确：{model}")
        if model not in selected:
            selected.append(model)
    if not selected:
        raise AIProviderError("至少需要一个 Ollama 基准模型")

    availability = check_ollama(settings)
    available = set(availability["available_models"])
    missing = [model for model in selected if model not in available]
    if missing:
        raise AIProviderError(f"本机尚未安装这些基准模型：{', '.join(missing)}")

    generator = generate_fn or generate_research
    results: list[dict[str, Any]] = []
    for model in selected:
        model_settings = replace(settings, model=model)
        try:
            response = generator(model_settings, prompt)
        except AIProviderError as exc:
            results.append(
                {
                    "model": model,
                    "status": "ERROR",
                    "error": str(exc),
                }
            )
            continue
        evaluation = evaluate_benchmark_response(
            response.content,
            truncated=response.truncated,
        )
        results.append(
            {
                "model": response.model,
                "status": "COMPLETED",
                "elapsed_seconds": response.elapsed_seconds,
                "done_reason": response.done_reason,
                "eval_count": response.eval_count,
                "thinking_character_count": response.thinking_character_count,
                "character_count": len(response.content),
                "content_sha256": sha256_text(response.content),
                **evaluation,
                "content": response.content,
            }
        )

    qualified = [
        result
        for result in results
        if result.get("status") == "COMPLETED" and result.get("qualified") is True
    ]
    fastest = min(qualified, key=lambda item: item["elapsed_seconds"], default=None)
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "provider": settings.provider,
        "endpoint": settings.endpoint,
        "prompt_sha256": sha256_text(prompt),
        "system_prompt_sha256": sha256_text(LOCAL_RESEARCH_SYSTEM_PROMPT),
        "generation_profile": {
            "temperature": 0.2,
            "num_ctx": 8192,
            "max_output_tokens": settings.max_output_tokens,
            "think": False,
        },
        "models": selected,
        "quality_scope": (
            "检查结构、候选覆盖、未知项披露、验证计划和无来源精确数值；"
            "仍不证明事实正确性或推荐质量"
        ),
        "qualified_score": QUALIFIED_SCORE,
        "fastest_structurally_qualified_model": fastest["model"] if fastest else None,
        "results": results,
    }


def default_benchmark_path(workspace: Path | str) -> Path:
    timestamp = utc_now().replace("-", "").replace(":", "").replace(".", "-")
    return Path(workspace) / "benchmarks" / f"OLLAMA-BENCHMARK-{timestamp}.json"


def save_benchmark_report(report: dict[str, Any], output: Path | str) -> Path:
    path = Path(output)
    if path.exists() or path.is_symlink():
        raise AIProviderError(f"基准报告目标已存在，未覆盖：{path}")
    if path.parent.exists() and (path.parent.is_symlink() or not path.parent.is_dir()):
        raise AIProviderError(f"基准报告目录必须是普通目录：{path.parent}")
    write_json_atomic(path, report)
    return path.resolve()


def benchmark_console_summary(report: dict[str, Any], output: Path) -> dict[str, Any]:
    summarized: list[dict[str, Any]] = []
    for result in report["results"]:
        summarized.append({key: value for key, value in result.items() if key != "content"})
    return {
        **{key: value for key, value in report.items() if key != "results"},
        "output": str(output),
        "results": summarized,
    }
