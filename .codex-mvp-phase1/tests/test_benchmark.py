from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_os_mvp.ai import AIResponse, AISettings
from research_os_mvp.benchmark import (
    benchmark_console_summary,
    evaluate_benchmark_response,
    run_ollama_benchmark,
    save_benchmark_report,
)

STRONG_CONTENT = (
    "## 候选项\nESP32、STM32、树莓派。\n"
    "## 比较维度\n比较接口、实时性、算力、功耗、开发和成本。\n"
    "## 事实与推断\n事实需由数据手册核验；推断只用于形成实验。\n"
    "## 未知/待查证\n未知具体负载、功耗和供货。\n"
    "## 验证实验\n实验一测量功耗；实验二测试实时性；实验三测试接口。\n"
    "## 条件式建议\n如果低功耗优先则先验证 ESP32；若实时控制优先则验证 STM32；"
    "如果需要 Linux 软件栈则验证树莓派。\n"
) * 4


class OllamaBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

    def test_structural_evaluation_distinguishes_complete_and_weak_outputs(self) -> None:
        strong = evaluate_benchmark_response(STRONG_CONTENT)
        weak = evaluate_benchmark_response("建议选择 ESP32。")
        truncated = evaluate_benchmark_response(STRONG_CONTENT, truncated=True)
        fabricated = evaluate_benchmark_response(STRONG_CONTENT + "内存为 512MB。")
        self.assertTrue(strong["qualified"])
        self.assertFalse(weak["qualified"])
        self.assertFalse(truncated["qualified"])
        self.assertFalse(fabricated["qualified"])
        self.assertIn("no_unsupported_precision", fabricated["failed_checks"])
        self.assertGreater(strong["score"], weak["score"])

    @patch("research_os_mvp.benchmark.check_ollama")
    def test_benchmark_selects_fastest_qualified_model_and_saves_full_report(
        self,
        check_mock: object,
    ) -> None:
        check_mock.return_value = {
            "available_models": ["qwen3:1.7b", "qwen2.5:7b"],
        }

        def fake_generate(settings: AISettings, _prompt: str) -> AIResponse:
            elapsed = 0.5 if settings.model == "qwen3:1.7b" else 2.0
            return AIResponse(
                content=STRONG_CONTENT,
                provider="ollama",
                model=settings.model,
                endpoint=settings.endpoint,
                elapsed_seconds=elapsed,
            )

        report = run_ollama_benchmark(
            self.settings,
            ["qwen3:1.7b", "qwen2.5:7b"],
            generate_fn=fake_generate,
        )
        self.assertEqual(report["fastest_structurally_qualified_model"], "qwen3:1.7b")

        with tempfile.TemporaryDirectory() as temporary:
            output = save_benchmark_report(report, Path(temporary) / "benchmark.json")
            saved = json.loads(output.read_text(encoding="utf-8"))
            summary = benchmark_console_summary(report, output)
            self.assertIn("content", saved["results"][0])
            self.assertNotIn("content", summary["results"][0])


if __name__ == "__main__":
    unittest.main()
