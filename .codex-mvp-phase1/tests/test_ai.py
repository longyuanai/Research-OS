from __future__ import annotations

import io
import json
import tempfile
import threading
import time
import unittest
import urllib.error
from collections.abc import Callable
from dataclasses import fields
from pathlib import Path
from typing import Self

from research_os_mvp.ai import (
    DEFAULT_GENERATION_BUDGET_SECONDS,
    DEFAULT_HEALTH_TIMEOUT_SECONDS,
    DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
    AIProviderError,
    AIResponse,
    AISettings,
    check_ollama,
    generate_research,
    load_ai_settings,
    save_ollama_settings,
)
from research_os_mvp.runtime import approve_run, create_run, resume_run
from research_os_mvp.wizard import _record_ai_response
from tests.helpers import EXAMPLE_PACK


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


class FakeNDJSONResponse(FakeHTTPResponse):
    def __init__(
        self,
        values: list[object] | None = None,
        *,
        raw_lines: list[bytes] | None = None,
        on_read: Callable[[int], None] | None = None,
        terminal_error: OSError | None = None,
    ) -> None:
        lines = raw_lines or [
            json.dumps(value, ensure_ascii=False).encode("utf-8") + b"\n"
            for value in (values or [])
        ]
        self._lines = list(lines)
        self._raw = b"".join(lines)
        self._on_read = on_read
        self._terminal_error = terminal_error
        self._read_count = 0
        self.headers = {}

    def readline(self, maximum: int = -1) -> bytes:
        read_index = self._read_count
        self._read_count += 1
        if self._on_read is not None:
            self._on_read(read_index)
        if self._lines:
            line = self._lines.pop(0)
            return line if maximum < 0 else line[:maximum]
        if self._terminal_error is not None:
            error = self._terminal_error
            self._terminal_error = None
            raise error
        return b""


class BlockingNDJSONResponse:
    def __init__(self) -> None:
        self.closed = threading.Event()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def readline(self, _maximum: int = -1) -> bytes:
        self.closed.wait(5)
        return b""

    def close(self) -> None:
        self.closed.set()
class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def stream_values(*contents: str) -> list[dict[str, object]]:
    values: list[dict[str, object]] = [
        {
            "model": "qwen2.5:7b",
            "message": {"content": content},
            "done": False,
        }
        for content in contents
    ]
    values.append(
        {
            "model": "qwen2.5:7b",
            "message": {"content": ""},
            "done": True,
            "done_reason": "stop",
            "eval_count": 42,
        }
    )
    return values


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
                self.assertTrue(body["stream"])
                self.assertFalse(body["think"])
                self.assertEqual(body["options"]["num_ctx"], 8192)
                self.assertEqual(body["options"]["num_predict"], 1536)
                self.assertIn("没有实时联网能力", body["messages"][0]["content"])
                self.assertIn("不得自行补充精确数值", body["messages"][0]["content"])
                return FakeNDJSONResponse(
                    [
                        {
                            "model": "qwen2.5:7b",
                            "message": {"content": "事实：资料不足。\n"},
                            "done": False,
                        },
                        {
                        "model": "qwen2.5:7b",
                            "message": {"content": "建议：先补充数据手册。"},
                            "done": True,
                        "done_reason": "stop",
                        "eval_count": 42,
                        },
                    ]
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

    def test_legacy_settings_without_budget_use_default(self) -> None:
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
                settings.stream_idle_timeout_seconds,
                DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
            )
            self.assertEqual(
                settings.generation_budget_seconds,
                DEFAULT_GENERATION_BUDGET_SECONDS,
            )

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

    def test_streaming_response_is_assembled_into_one_content(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

        response = generate_research(
            settings,
            "测试流式拼接",
            open_fn=lambda *_args, **_kwargs: FakeNDJSONResponse(
                stream_values("第一段", "与第二段")
            ),
        )

        self.assertEqual(response.content, "第一段与第二段")
        self.assertEqual(response.done_reason, "stop")
        self.assertEqual(response.eval_count, 42)

    def test_stream_chunks_reset_the_idle_timeout(self) -> None:
        clock = FakeClock()
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            stream_idle_timeout_seconds=60,
            generation_budget_seconds=900,
        )
        observed_timeouts: list[int] = []

        def advance_between_chunks(_index: int) -> None:
            clock.advance(50)

        def fake_open(
            _request: object,
            *,
            timeout: int,
        ) -> FakeNDJSONResponse:
            observed_timeouts.append(timeout)
            return FakeNDJSONResponse(
                stream_values("甲", "乙"),
                on_read=advance_between_chunks,
            )

        response = generate_research(
            settings,
            "每个块都在空闲上限内",
            open_fn=fake_open,
            monotonic_fn=clock,
        )

        self.assertEqual(observed_timeouts, [60])
        self.assertEqual(response.content, "甲乙")
        self.assertGreater(response.elapsed_seconds, 60)

    def test_idle_timeout_fires_when_no_chunk_arrives(self) -> None:
        clock = FakeClock()
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            stream_idle_timeout_seconds=60,
        )

        def advance_for_read(index: int) -> None:
            clock.advance(61 if index == 1 else 0)

        response = FakeNDJSONResponse(
            stream_values("已接收")[:-1],
            on_read=advance_for_read,
            terminal_error=TimeoutError("timed out"),
        )
        with self.assertRaises(AIProviderError) as raised:
            generate_research(
                settings,
                "测试块间超时",
                open_fn=lambda *_args, **_kwargs: response,
                monotonic_fn=clock,
            )
        message = str(raised.exception)
        self.assertIn("空闲超时", message)
        self.assertIn("stream_idle_timeout_seconds=60", message)
        self.assertIn("已生成 3 字符", message)

    def test_hard_budget_and_progress_continue_while_readline_blocks(self) -> None:
        response = BlockingNDJSONResponse()
        progress: list[str] = []
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            stream_idle_timeout_seconds=5,
            generation_budget_seconds=1,
        )

        started = time.monotonic()
        with self.assertRaisesRegex(AIProviderError, "超出总时长预算"):
            generate_research(
                settings,
                "测试阻塞读取硬截止",
                open_fn=lambda *_args, **_kwargs: response,
                progress_fn=progress.append,
                progress_interval_seconds=0.2,
            )

        self.assertLess(time.monotonic() - started, 1.5)
        self.assertGreaterEqual(len(progress), 3)
        self.assertTrue(response.closed.is_set())

    def test_generation_budget_aborts_a_runaway_stream(self) -> None:
        clock = FakeClock()
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            generation_budget_seconds=10,
        )
        response = FakeNDJSONResponse(
            stream_values("甲", "乙", "丙", "丁"),
            on_read=lambda _index: clock.advance(4),
        )

        with self.assertRaisesRegex(AIProviderError, "超出总时长预算"):
            generate_research(
                settings,
                "测试总预算",
                open_fn=lambda *_args, **_kwargs: response,
                monotonic_fn=clock,
            )

    def test_budget_error_reports_elapsed_and_partial_length(self) -> None:
        clock = FakeClock()
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
            generation_budget_seconds=10,
        )
        delays = [0, 5, 6]
        response = FakeNDJSONResponse(
            stream_values("甲", "乙", "丙"),
            on_read=lambda index: clock.advance(delays[index]),
        )

        with self.assertRaises(AIProviderError) as raised:
            generate_research(
                settings,
                "测试预算错误明细",
                open_fn=lambda *_args, **_kwargs: response,
                monotonic_fn=clock,
            )
        message = str(raised.exception)
        self.assertIn("已用 11.000 秒", message)
        self.assertIn("已生成 2 字符", message)

    def test_malformed_ndjson_line_raises_a_clear_error(self) -> None:
        response = FakeNDJSONResponse(
            raw_lines=[
                b'{"message":{"content":"ok"},"done":false}\n',
                b"not-json\n",
            ]
        )
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

        with self.assertRaises(AIProviderError) as raised:
            generate_research(
                settings,
                "测试损坏的 NDJSON",
                open_fn=lambda *_args, **_kwargs: response,
            )
        self.assertIn("第 2 行", str(raised.exception))
        self.assertIn("NDJSON", str(raised.exception))

    def test_empty_stream_raises_a_clear_error(self) -> None:
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

        with self.assertRaisesRegex(AIProviderError, "空的 NDJSON 流"):
            generate_research(
                settings,
                "测试空流",
                open_fn=lambda *_args, **_kwargs: FakeNDJSONResponse(),
            )

    def test_progress_is_emitted_during_a_long_stream(self) -> None:
        clock = FakeClock()
        progress: list[str] = []
        delays = [0, 11, 11]
        response = FakeNDJSONResponse(
            stream_values("甲", "乙"),
            on_read=lambda index: clock.advance(delays[index]),
        )
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )

        generate_research(
            settings,
            "测试长时流式进度",
            open_fn=lambda *_args, **_kwargs: response,
            progress_fn=progress.append,
            monotonic_fn=clock,
            progress_interval_seconds=10,
        )

        self.assertGreaterEqual(len(progress), 2)
        self.assertIn("已用 11.0 秒", progress[0])
        self.assertIn("已接收 2 字符", progress[0])

    def test_progress_does_not_enter_evidence_or_report(self) -> None:
        clock = FakeClock()
        progress: list[str] = []
        response = FakeNDJSONResponse(
            stream_values("只记录草稿正文"),
            on_read=lambda _index: clock.advance(16),
        )
        settings = AISettings(
            provider="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5:7b",
            reviewer_model="qwen2.5:7b",
        )
        generated = generate_research(
            settings,
            "测试进度与工件隔离",
            open_fn=lambda *_args, **_kwargs: response,
            progress_fn=progress.append,
            monotonic_fn=clock,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-progress-isolation")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Human Tester", note="Task 1 verified")
            resume_run(run_dir)
            _record_ai_response(run_dir, generated)
            artifact_text = "\n".join(
                path.read_text(encoding="utf-8")
                for directory in (run_dir / "evidence", run_dir / "reports")
                for path in directory.iterdir()
                if path.is_file()
            )

        self.assertTrue(progress)
        self.assertIn("本地 AI 生成进度", progress[0])
        self.assertNotIn("本地 AI 生成进度", artifact_text)
        self.assertIn("只记录草稿正文", artifact_text)

    def test_ai_response_shape_is_unchanged_for_consumers(self) -> None:
        self.assertEqual(
            [field.name for field in fields(AIResponse)],
            [
                "content",
                "provider",
                "model",
                "endpoint",
                "elapsed_seconds",
                "done_reason",
                "eval_count",
                "thinking_character_count",
                "truncated",
            ],
        )

    def test_remote_endpoint_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            AIProviderError, "本机 HTTP"
        ):
            save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                endpoint="https://example.com:11434",
            )


def _stream_settings(**overrides: object) -> AISettings:
    values: dict[str, object] = {
        "provider": "ollama",
        "endpoint": "http://127.0.0.1:11434",
        "model": "qwen2.5:7b",
        "reviewer_model": "qwen2.5:7b",
    }
    values.update(overrides)
    return AISettings(**values)  # type: ignore[arg-type]


def _write_settings(root: str, **ai_overrides: object) -> None:
    ai: dict[str, object] = {
        "enabled": True,
        "provider": "ollama",
        "endpoint": "http://127.0.0.1:11434",
        "model": "qwen2.5:7b",
        "reviewer_model": "qwen2.5:7b",
        "timeout_seconds": 300,
        "max_response_chars": 200_000,
        "max_output_tokens": 1536,
        "automatic_research": True,
    }
    ai.update(ai_overrides)
    (Path(root) / "settings.json").write_text(
        json.dumps(
            {"schema_version": "research-os-mvp-settings/0.1", "ai": ai},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


class AIStreamSettingsTests(unittest.TestCase):
    def test_custom_stream_limits_round_trip_through_settings_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                stream_idle_timeout_seconds=17,
                generation_budget_seconds=1234,
            )
            stored = json.loads(path.read_text(encoding="utf-8"))["ai"]
            self.assertEqual(stored["stream_idle_timeout_seconds"], 17)
            self.assertEqual(stored["generation_budget_seconds"], 1234)
            settings = load_ai_settings(temporary)
            assert settings is not None
            self.assertEqual(settings.stream_idle_timeout_seconds, 17)
            self.assertEqual(settings.generation_budget_seconds, 1234)

    def test_stream_limits_accept_inclusive_boundaries(self) -> None:
        for idle, budget in ((1, 10), (300, 7200)):
            with self.subTest(idle=idle, budget=budget):
                with tempfile.TemporaryDirectory() as temporary:
                    _write_settings(
                        temporary,
                        stream_idle_timeout_seconds=idle,
                        generation_budget_seconds=budget,
                    )
                    settings = load_ai_settings(temporary)
                    assert settings is not None
                    self.assertEqual(settings.stream_idle_timeout_seconds, idle)
                    self.assertEqual(settings.generation_budget_seconds, budget)

    def test_out_of_range_stream_idle_timeout_is_rejected(self) -> None:
        for value in (0, 301, "60", 1.5):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as temporary:
                    _write_settings(temporary, stream_idle_timeout_seconds=value)
                    with self.assertRaisesRegex(AIProviderError, "空闲超时"):
                        load_ai_settings(temporary)

    def test_out_of_range_generation_budget_is_rejected(self) -> None:
        for value in (9, 7201, "900", 10.5):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as temporary:
                    _write_settings(temporary, generation_budget_seconds=value)
                    with self.assertRaisesRegex(AIProviderError, "总时长预算"):
                        load_ai_settings(temporary)

    def test_save_rejects_invalid_stream_limits_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(AIProviderError, "总时长预算"):
                save_ollama_settings(
                    temporary,
                    model="qwen2.5:7b",
                    generation_budget_seconds=5,
                )
            self.assertFalse((Path(temporary) / "settings.json").exists())

    def test_health_check_reports_stream_limits(self) -> None:
        settings = _stream_settings(
            stream_idle_timeout_seconds=33,
            generation_budget_seconds=444,
        )
        status = check_ollama(
            settings,
            open_fn=lambda *_args, **_kwargs: FakeHTTPResponse(
                {"models": [{"name": "qwen2.5:7b"}]}
            ),
        )
        self.assertEqual(status["stream_idle_timeout_seconds"], 33)
        self.assertEqual(status["generation_budget_seconds"], 444)


class AIStreamFailureModeTests(unittest.TestCase):
    def test_open_timeout_is_capped_by_the_smaller_stream_limit(self) -> None:
        observed: list[int] = []

        def fake_open(_request: object, *, timeout: int) -> FakeNDJSONResponse:
            observed.append(timeout)
            return FakeNDJSONResponse(stream_values("ok"))

        generate_research(
            _stream_settings(
                stream_idle_timeout_seconds=120,
                generation_budget_seconds=30,
            ),
            "测试连接超时取较小值",
            open_fn=fake_open,
        )
        self.assertEqual(observed, [30])

    def test_request_payload_enables_streaming(self) -> None:
        bodies: list[dict[str, object]] = []

        def fake_open(request: object, **_kwargs: object) -> FakeNDJSONResponse:
            bodies.append(json.loads(request.data.decode("utf-8")))  # type: ignore[attr-defined]
            return FakeNDJSONResponse(stream_values("ok"))

        generate_research(_stream_settings(), "测试请求体", open_fn=fake_open)
        self.assertEqual(len(bodies), 1)
        self.assertIs(bodies[0]["stream"], True)
        self.assertIs(bodies[0]["think"], False)

    def test_error_record_in_stream_is_reported(self) -> None:
        response = FakeNDJSONResponse(
            [
                {"message": {"content": "部分"}, "done": False},
                {"error": "model runner crashed"},
            ]
        )
        with self.assertRaisesRegex(
            AIProviderError, "流式生成返回错误：model runner crashed"
        ):
            generate_research(
                _stream_settings(),
                "测试流内错误",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_stream_without_done_marker_is_rejected(self) -> None:
        response = FakeNDJSONResponse(stream_values("甲", "乙")[:-1])
        with self.assertRaisesRegex(AIProviderError, "完成标记前意外结束"):
            generate_research(
                _stream_settings(),
                "测试缺少 done",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_whitespace_only_content_is_rejected(self) -> None:
        response = FakeNDJSONResponse(stream_values("  ", "\n"))
        with self.assertRaisesRegex(AIProviderError, "没有返回有效正文"):
            generate_research(
                _stream_settings(),
                "测试空白正文",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_non_object_json_line_is_rejected(self) -> None:
        response = FakeNDJSONResponse(raw_lines=[b"[1, 2, 3]\n"])
        with self.assertRaisesRegex(AIProviderError, "第 1 行必须是 JSON 对象"):
            generate_research(
                _stream_settings(),
                "测试非对象行",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_invalid_utf8_line_is_rejected(self) -> None:
        response = FakeNDJSONResponse(raw_lines=[b"\xff\xfe\n"])
        with self.assertRaisesRegex(AIProviderError, "不是有效 NDJSON"):
            generate_research(
                _stream_settings(),
                "测试非法编码",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_blank_keepalive_lines_are_skipped(self) -> None:
        lines = [b"\n"]
        for value in stream_values("甲", "乙"):
            lines.append(json.dumps(value, ensure_ascii=False).encode("utf-8") + b"\n")
            lines.append(b"\r\n")
        response = FakeNDJSONResponse(raw_lines=lines)
        result = generate_research(
            _stream_settings(),
            "测试空行",
            open_fn=lambda *_args, **_kwargs: response,
        )
        self.assertEqual(result.content, "甲乙")

    def test_blank_lines_do_not_reset_the_idle_timeout(self) -> None:
        clock = FakeClock()
        lines = [
            json.dumps({"message": {"content": "甲"}, "done": False}).encode("utf-8")
            + b"\n",
            b"\n",
            b"\n",
        ]
        response = FakeNDJSONResponse(
            raw_lines=lines,
            on_read=lambda index: clock.advance(0 if index == 0 else 40),
            terminal_error=TimeoutError("timed out"),
        )
        with self.assertRaisesRegex(AIProviderError, "空闲超时"):
            generate_research(
                _stream_settings(stream_idle_timeout_seconds=60),
                "测试空行不算数据块",
                open_fn=lambda *_args, **_kwargs: response,
                monotonic_fn=clock,
            )

    def test_content_over_character_limit_is_rejected(self) -> None:
        response = FakeNDJSONResponse(stream_values("甲" * 600, "乙" * 600))
        with self.assertRaisesRegex(AIProviderError, "字符上限"):
            generate_research(
                _stream_settings(max_response_chars=1_000),
                "测试字符上限",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_raw_stream_over_byte_limit_is_rejected(self) -> None:
        big_line = b" " * (2 * 1024 * 1024 + 10) + b"\n"
        response = FakeNDJSONResponse(raw_lines=[big_line])
        with self.assertRaisesRegex(AIProviderError, "安全上限"):
            generate_research(
                _stream_settings(),
                "测试字节上限",
                open_fn=lambda *_args, **_kwargs: response,
            )

    def test_http_error_is_reported_with_status_and_detail(self) -> None:
        def fake_open(_request: object, **_kwargs: object) -> FakeNDJSONResponse:
            raise urllib.error.HTTPError(
                "http://127.0.0.1:11434/api/chat",
                404,
                "Not Found",
                None,  # type: ignore[arg-type]
                io.BytesIO(b'{"error":"model not found"}'),
            )

        with self.assertRaises(AIProviderError) as raised:
            generate_research(_stream_settings(), "测试 HTTP 错误", open_fn=fake_open)
        message = str(raised.exception)
        self.assertIn("HTTP 404", message)
        self.assertIn("model not found", message)

    def test_connection_error_names_stream_idle_limit(self) -> None:
        def fake_open(_request: object, **_kwargs: object) -> FakeNDJSONResponse:
            raise urllib.error.URLError(ConnectionRefusedError("refused"))

        with self.assertRaises(AIProviderError) as raised:
            generate_research(
                _stream_settings(stream_idle_timeout_seconds=45),
                "测试连接失败",
                open_fn=fake_open,
            )
        message = str(raised.exception)
        self.assertIn("生成调用失败", message)
        self.assertIn("45 秒", message)
        self.assertIn("refused", message)

    def test_unexpected_worker_exception_is_propagated(self) -> None:
        def fake_open(_request: object, **_kwargs: object) -> FakeNDJSONResponse:
            raise ValueError("boom")

        with self.assertRaisesRegex(ValueError, "boom"):
            generate_research(_stream_settings(), "测试异常传播", open_fn=fake_open)

    def test_metadata_is_aggregated_across_stream_records(self) -> None:
        values = [
            {
                "model": "qwen2.5:7b",
                "message": {"content": "甲", "thinking": "想"},
                "done": False,
            },
            {
                "model": "qwen2.5:7b-q4",
                "message": {"content": "乙", "thinking": "再想"},
                "done": False,
            },
            {
                "model": "qwen2.5:7b-q4",
                "message": {"content": ""},
                "done": True,
                "done_reason": "length",
                "eval_count": 7,
            },
        ]
        result = generate_research(
            _stream_settings(),
            "测试元数据",
            open_fn=lambda *_args, **_kwargs: FakeNDJSONResponse(values),
        )
        self.assertEqual(result.content, "甲乙")
        self.assertEqual(result.model, "qwen2.5:7b-q4")
        self.assertEqual(result.thinking_character_count, 3)
        self.assertEqual(result.done_reason, "length")
        self.assertEqual(result.eval_count, 7)
        self.assertTrue(result.truncated)

    def test_reader_thread_is_released_after_early_failure(self) -> None:
        response = FakeNDJSONResponse(
            raw_lines=[b"not-json\n"]
            + [b'{"message":{"content":"x"},"done":false}\n'] * 50
        )
        with self.assertRaises(AIProviderError):
            generate_research(
                _stream_settings(),
                "测试读取线程释放",
                open_fn=lambda *_args, **_kwargs: response,
            )
        deadline = time.monotonic() + 2
        alive: list[threading.Thread] = []
        while time.monotonic() < deadline:
            alive = [
                thread
                for thread in threading.enumerate()
                if thread.name == "research-os-ollama-stream-reader"
            ]
            if not alive:
                break
            time.sleep(0.02)
        self.assertEqual(alive, [])
        # The reader stopped before draining the remaining 50 lines.
        self.assertGreater(len(response._lines), 0)


if __name__ == "__main__":
    unittest.main()
