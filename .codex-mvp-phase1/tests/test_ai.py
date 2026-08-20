from __future__ import annotations

import json
import tempfile
import unittest
from typing import Self

from research_os_mvp.ai import (
    AIProviderError,
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
