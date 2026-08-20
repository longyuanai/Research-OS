from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Self

from research_os_mvp.ai import (
    DEFAULT_HEALTH_TIMEOUT_SECONDS,
    AIProviderError,
    AISettings,
    check_ollama,
    generate_research,
    load_ai_settings,
    save_ollama_settings,
)


class FakeHTTPResponse:
    def __init__(self, value: object) -> None:
        self._raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.headers = {"Content-Length": str(len(self._raw))}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, maximum: int = -1) -> bytes:
        return self._raw if maximum < 0 else self._raw[:maximum]


class AITests(unittest.TestCase):
    def test_save_load_check_and_generate_with_local_ollama(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = save_ollama_settings(temporary, model="qwen2.5:7b")
            self.assertTrue(path.is_file())
            settings = load_ai_settings(temporary)
            self.assertIsNotNone(settings)
            assert settings is not None
            self.assertEqual(settings.reviewer_model, "qwen2.5:7b")
            self.assertEqual(settings.max_output_tokens, 1536)

            requests: list[object] = []

            def fake_open(request: object, **_kwargs: object) -> FakeHTTPResponse:
                requests.append(request)
                url = request.full_url
                if url.endswith("/api/tags"):
                    return FakeHTTPResponse({"models": [{"name": "qwen2.5:7b"}]})
                body = json.loads(request.data.decode("utf-8"))
                self.assertFalse(body["stream"])
                self.assertFalse(body["think"])
                self.assertEqual(body["options"]["num_ctx"], 8192)
                self.assertEqual(body["options"]["num_predict"], 1536)
                self.assertIn("没有实时联网能力", body["messages"][0]["content"])
                self.assertIn("不得自行补充精确数值", body["messages"][0]["content"])
                return FakeHTTPResponse(
                    {
                        "model": "qwen2.5:7b",
                        "message": {"content": "事实：资料不足。\n建议：先补充数据手册。"},
                        "done_reason": "stop",
                        "eval_count": 42,
                    }
                )

            status = check_ollama(settings, open_fn=fake_open)
            self.assertTrue(status["model_available"])
            self.assertTrue(status["reviewer_model_available"])
            response = generate_research(settings, "比较两个方案", open_fn=fake_open)
            self.assertEqual(response.model, "qwen2.5:7b")
            self.assertIn("资料不足", response.content)
            self.assertEqual(response.done_reason, "stop")
            self.assertEqual(response.eval_count, 42)
            self.assertFalse(response.truncated)
            self.assertEqual(len(requests), 2)

    def test_health_check_uses_its_own_timeout_not_the_generation_timeout(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            health_timeout_seconds=47,
            timeout_seconds=300,
        )
        observed_timeouts: list[int] = []

        def fake_open(
            _request: object,
            *,
            timeout: int,
        ) -> FakeHTTPResponse:
            observed_timeouts.append(timeout)
            return FakeHTTPResponse({"models": [{"name": "qwen2.5:7b"}]})

        check_ollama(settings, open_fn=fake_open)
        self.assertEqual(observed_timeouts, [47])
        self.assertNotEqual(observed_timeouts, [settings.timeout_seconds])

    def test_health_check_timeout_is_configurable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                health_timeout_seconds=91,
            )
            settings = load_ai_settings(temporary)
            assert settings is not None

            def fake_open(
                _request: object,
                *,
                timeout: int,
            ) -> FakeHTTPResponse:
                self.assertEqual(timeout, 91)
                return FakeHTTPResponse({"models": [{"name": "qwen2.5:7b"}]})

            status = check_ollama(settings, open_fn=fake_open)
            self.assertEqual(settings.health_timeout_seconds, 91)
            self.assertEqual(status["health_timeout_seconds"], 91)
            self.assertEqual(status["timeout_seconds"], 300)
            self.assertIn("health_check_elapsed_seconds", status)

    def test_legacy_settings_without_health_timeout_use_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "settings.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": "research-os-mvp-settings/0.1",
                        "ai": {
                            "enabled": True,
                            "provider": "ollama",
                            "endpoint": "http://127.0.0.1:11434",
                            "model": "qwen2.5:7b",
                            "reviewer_model": "qwen3:1.7b",
                            "timeout_seconds": 300,
                            "max_response_chars": 200_000,
                            "max_output_tokens": 1536,
                            "automatic_research": True,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            settings = load_ai_settings(temporary)
            assert settings is not None
            self.assertEqual(
                settings.health_timeout_seconds,
                DEFAULT_HEALTH_TIMEOUT_SECONDS,
            )
            self.assertEqual(settings.health_timeout_seconds, 60)

    def test_health_check_error_names_the_step_and_config_key(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            health_timeout_seconds=60,
        )

        def fail_open(_request: object, **_kwargs: object) -> FakeHTTPResponse:
            raise TimeoutError("timed out")

        with self.assertRaises(AIProviderError) as raised:
            check_ollama(settings, open_fn=fail_open)
        message = str(raised.exception)
        self.assertIn("健康检查", message)
        self.assertIn("实际等待", message)
        self.assertIn("health_timeout_seconds=60", message)

    def test_generation_error_names_the_step_and_config_key(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            timeout_seconds=300,
        )

        def fail_open(_request: object, **_kwargs: object) -> FakeHTTPResponse:
            raise TimeoutError("timed out")

        with self.assertRaises(AIProviderError) as raised:
            generate_research(settings, "测试生成错误", open_fn=fail_open)
        message = str(raised.exception)
        self.assertIn("生成调用", message)
        self.assertIn("实际等待", message)
        self.assertIn("timeout_seconds=300", message)

    def test_health_and_generation_errors_are_distinguishable(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

        def fail_open(_request: object, **_kwargs: object) -> FakeHTTPResponse:
            raise TimeoutError("timed out")

        with self.assertRaises(AIProviderError) as health_error:
            check_ollama(settings, open_fn=fail_open)
        with self.assertRaises(AIProviderError) as generation_error:
            generate_research(settings, "测试错误区分", open_fn=fail_open)
        health_message = str(health_error.exception)
        generation_message = str(generation_error.exception)
        self.assertNotEqual(health_message, generation_message)
        self.assertIn("健康检查", health_message)
        self.assertNotIn("生成调用", health_message)
        self.assertIn("生成调用", generation_message)
        self.assertNotIn("健康检查", generation_message)

    def test_remote_endpoint_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            AIProviderError, "本机 HTTP"
        ):
            save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                endpoint="https://example.com:11434",
            )


if __name__ == "__main__":
    unittest.main()
