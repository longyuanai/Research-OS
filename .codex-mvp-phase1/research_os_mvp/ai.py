from __future__ import annotations

import json
import queue
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_os_mvp.errors import MVPError
from research_os_mvp.integrity import read_json, write_json_atomic

SETTINGS_FILE = "settings.json"
SETTINGS_SCHEMA = "research-os-mvp-settings/0.1"
DEFAULT_ENDPOINT = "http://127.0.0.1:11434"
DEFAULT_HEALTH_TIMEOUT_SECONDS = 60
DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS = 60
DEFAULT_GENERATION_BUDGET_SECONDS = 900
DEFAULT_PROGRESS_INTERVAL_SECONDS = 15
MAX_HTTP_RESPONSE_BYTES = 2 * 1024 * 1024
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
LOCAL_RESEARCH_SYSTEM_PROMPT = (
    "你是 Research-OS 的本地研究执行者。你没有实时联网能力。"
    "只依据用户提供的信息和明确标注的通用知识工作；"
    "不得编造来源、链接、参数或测试。资料不足时写‘未知/待查证’。"
    "如果输入没有给出可追溯来源或测量，对具体架构、频率、内存、功耗、"
    "价格和型号差异都必须写‘未知/待查证’，不得自行补充精确数值或价格区间。"
    "将事实、推断、建议和待验证项分开，使用中文输出。"
)


class AIProviderError(MVPError):
    """Raised when a configured local AI provider cannot complete a request."""


@dataclass(frozen=True)
class AISettings:
    provider: str
    endpoint: str
    model: str
    reviewer_model: str
    health_timeout_seconds: int = DEFAULT_HEALTH_TIMEOUT_SECONDS
    timeout_seconds: int = 300
    stream_idle_timeout_seconds: int = DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS
    generation_budget_seconds: int = DEFAULT_GENERATION_BUDGET_SECONDS
    max_response_chars: int = 200_000
    max_output_tokens: int = 1536
    automatic_research: bool = True


@dataclass(frozen=True)
class AIResponse:
    content: str
    provider: str
    model: str
    endpoint: str
    elapsed_seconds: float
    done_reason: str | None = None
    eval_count: int | None = None
    thinking_character_count: int = 0
    truncated: bool = False


OpenFn = Callable[..., Any]
ProgressFn = Callable[[str], None]
MonotonicFn = Callable[[], float]


def _validate_local_endpoint(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.rstrip("/"))
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise AIProviderError("第一阶段 AI 地址必须是本机 HTTP 服务")
    try:
        port = parsed.port
    except ValueError as exc:
        raise AIProviderError("AI 服务端口格式不正确") from exc
    if port is None or not 1 <= port <= 65535:
        raise AIProviderError("AI 服务地址必须包含有效端口")
    host = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
    return f"http://{host}:{port}"


def _settings_from_data(value: Any) -> AISettings:
    if not isinstance(value, dict) or value.get("schema_version") != SETTINGS_SCHEMA:
        raise AIProviderError("AI 设置文件格式不受支持")
    ai = value.get("ai")
    if not isinstance(ai, dict):
        raise AIProviderError("AI 设置缺少 ai 对象")
    if ai.get("enabled") is not True:
        raise AIProviderError("本地 AI 尚未启用")
    if ai.get("provider") != "ollama":
        raise AIProviderError("第一阶段仅支持 Ollama Provider")
    model = ai.get("model")
    if not isinstance(model, str) or not MODEL_PATTERN.fullmatch(model):
        raise AIProviderError("Ollama 模型名称格式不正确")
    reviewer_model = ai.get("reviewer_model", model)
    if not isinstance(reviewer_model, str) or not MODEL_PATTERN.fullmatch(reviewer_model):
        raise AIProviderError("Ollama 审计模型名称格式不正确")
    health_timeout = ai.get(
        "health_timeout_seconds",
        DEFAULT_HEALTH_TIMEOUT_SECONDS,
    )
    timeout = ai.get("timeout_seconds", 300)
    stream_idle_timeout = ai.get(
        "stream_idle_timeout_seconds",
        DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
    )
    generation_budget = ai.get(
        "generation_budget_seconds",
        DEFAULT_GENERATION_BUDGET_SECONDS,
    )
    maximum = ai.get("max_response_chars", 200_000)
    max_output_tokens = ai.get("max_output_tokens", 1536)
    automatic = ai.get("automatic_research", True)
    if not isinstance(health_timeout, int) or not 1 <= health_timeout <= 300:
        raise AIProviderError("Ollama 健康检查超时必须在 1-300 秒之间")
    if not isinstance(timeout, int) or not 10 <= timeout <= 900:
        raise AIProviderError("AI 超时必须在 10-900 秒之间")
    if not isinstance(stream_idle_timeout, int) or not 1 <= stream_idle_timeout <= 300:
        raise AIProviderError("Ollama 流式块间空闲超时必须在 1-300 秒之间")
    if not isinstance(generation_budget, int) or not 10 <= generation_budget <= 7200:
        raise AIProviderError("Ollama 生成总时长预算必须在 10-7200 秒之间")
    if not isinstance(maximum, int) or not 1_000 <= maximum <= 500_000:
        raise AIProviderError("AI 输出上限必须在 1000-500000 字符之间")
    if not isinstance(max_output_tokens, int) or not 256 <= max_output_tokens <= 4096:
        raise AIProviderError("AI 输出 Token 上限必须在 256-4096 之间")
    if not isinstance(automatic, bool):
        raise AIProviderError("automatic_research 必须是布尔值")
    return AISettings(
        provider="ollama",
        endpoint=_validate_local_endpoint(str(ai.get("endpoint", DEFAULT_ENDPOINT))),
        model=model,
        reviewer_model=reviewer_model,
        health_timeout_seconds=health_timeout,
        timeout_seconds=timeout,
        stream_idle_timeout_seconds=stream_idle_timeout,
        generation_budget_seconds=generation_budget,
        max_response_chars=maximum,
        max_output_tokens=max_output_tokens,
        automatic_research=automatic,
    )


def load_ai_settings(workspace: Path | str) -> AISettings | None:
    path = Path(workspace) / SETTINGS_FILE
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise AIProviderError("AI 设置文件必须是普通文件")
    return _settings_from_data(read_json(path))


def save_ollama_settings(
    workspace: Path | str,
    *,
    model: str,
    reviewer_model: str | None = None,
    endpoint: str = DEFAULT_ENDPOINT,
    health_timeout_seconds: int = DEFAULT_HEALTH_TIMEOUT_SECONDS,
    stream_idle_timeout_seconds: int = DEFAULT_STREAM_IDLE_TIMEOUT_SECONDS,
    generation_budget_seconds: int = DEFAULT_GENERATION_BUDGET_SECONDS,
    max_output_tokens: int = 1536,
    automatic_research: bool = True,
) -> Path:
    root = Path(workspace)
    if root.exists() and root.is_symlink():
        raise AIProviderError("workspace 不得是符号链接")
    data = {
        "schema_version": SETTINGS_SCHEMA,
        "ai": {
            "enabled": True,
            "provider": "ollama",
            "endpoint": endpoint,
            "model": model,
            "reviewer_model": reviewer_model or model,
            "health_timeout_seconds": health_timeout_seconds,
            "timeout_seconds": 300,
            "stream_idle_timeout_seconds": stream_idle_timeout_seconds,
            "generation_budget_seconds": generation_budget_seconds,
            "max_response_chars": 200_000,
            "max_output_tokens": max_output_tokens,
            "automatic_research": automatic_research,
        },
    }
    _settings_from_data(data)
    path = root / SETTINGS_FILE
    if path.is_symlink():
        raise AIProviderError("AI 设置文件不得是符号链接")
    write_json_atomic(path, data)
    return path.resolve()


def _read_json_response(response: Any) -> dict[str, Any]:
    declared = response.headers.get("Content-Length")
    if declared is not None:
        try:
            if int(declared) > MAX_HTTP_RESPONSE_BYTES:
                raise AIProviderError("Ollama 返回内容超过安全上限")
        except ValueError as exc:
            raise AIProviderError("Ollama 返回了无效的 Content-Length") from exc
    raw = response.read(MAX_HTTP_RESPONSE_BYTES + 1)
    if len(raw) > MAX_HTTP_RESPONSE_BYTES:
        raise AIProviderError("Ollama 返回内容超过安全上限")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AIProviderError("Ollama 返回的 JSON 无效") from exc
    if not isinstance(value, dict):
        raise AIProviderError("Ollama 返回值必须是 JSON 对象")
    return value


def check_ollama(settings: AISettings, *, open_fn: OpenFn = urllib.request.urlopen) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{settings.endpoint}/api/tags",
        headers={"Accept": "application/json"},
        method="GET",
    )
    started = time.monotonic()
    try:
        with open_fn(request, timeout=settings.health_timeout_seconds) as response:
            value = _read_json_response(response)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        elapsed = time.monotonic() - started
        raise AIProviderError(
            "Ollama 健康检查失败：无法连接本地服务"
            f"（实际等待 {elapsed:.3f} 秒；"
            f"health_timeout_seconds={settings.health_timeout_seconds} 秒）；"
            f"请确认服务已启动，或调高 health_timeout_seconds。原始错误：{exc}"
        ) from exc
    models = value.get("models")
    if not isinstance(models, list):
        raise AIProviderError("Ollama 模型列表格式不正确")
    names = [item.get("name") for item in models if isinstance(item, dict)]
    return {
        "provider": settings.provider,
        "endpoint": settings.endpoint,
        "health_timeout_seconds": settings.health_timeout_seconds,
        "health_check_elapsed_seconds": round(time.monotonic() - started, 3),
        "timeout_seconds": settings.timeout_seconds,
        "stream_idle_timeout_seconds": settings.stream_idle_timeout_seconds,
        "generation_budget_seconds": settings.generation_budget_seconds,
        "model": settings.model,
        "model_available": settings.model in names,
        "reviewer_model": settings.reviewer_model,
        "reviewer_model_available": settings.reviewer_model in names,
        "available_models": [name for name in names if isinstance(name, str)],
    }


def generate_research(
    settings: AISettings,
    prompt: str,
    *,
    open_fn: OpenFn = urllib.request.urlopen,
    progress_fn: ProgressFn | None = None,
    monotonic_fn: MonotonicFn = time.monotonic,
    progress_interval_seconds: float = DEFAULT_PROGRESS_INTERVAL_SECONDS,
) -> AIResponse:
    cleaned = prompt.strip()
    if not cleaned:
        raise AIProviderError("AI 研究指令为空")
    if len(cleaned) > 120_000:
        raise AIProviderError("AI 研究指令超过 120000 字符")
    payload = {
        "model": settings.model,
        "stream": True,
        "think": False,
        "messages": [
            {
                "role": "system",
                "content": LOCAL_RESEARCH_SYSTEM_PROMPT,
            },
            {"role": "user", "content": cleaned},
        ],
        "options": {
            "temperature": 0.2,
            "num_ctx": 8192,
            "num_predict": settings.max_output_tokens,
        },
    }
    request = urllib.request.Request(
        f"{settings.endpoint}/api/chat",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    started = monotonic_fn()
    chunks: list[str] = []
    content_characters = 0
    thinking_character_count = 0
    returned_model = settings.model
    done_reason: str | None = None
    eval_count: int | None = None
    saw_record = False
    saw_done = False
    raw_bytes = 0
    line_number = 0
    next_progress = progress_interval_seconds

    def elapsed_seconds() -> float:
        return monotonic_fn() - started

    def check_budget() -> float:
        elapsed = elapsed_seconds()
        if elapsed >= settings.generation_budget_seconds:
            raise AIProviderError(
                "Ollama AI 生成超出总时长预算"
                f"（已用 {elapsed:.3f} 秒；"
                f"generation_budget_seconds={settings.generation_budget_seconds} 秒；"
                f"已生成 {content_characters} 字符）"
            )
        return elapsed

    stream_events: queue.Queue[tuple[str, Any, float]] = queue.Queue()
    stop_reader = threading.Event()
    event_processed = threading.Event()
    response_holder: list[Any] = []

    def publish_stream_event(kind: str, payload: Any) -> None:
        if stop_reader.is_set():
            return
        event_processed.clear()
        stream_events.put((kind, payload, monotonic_fn()))
        while not stop_reader.is_set() and not event_processed.wait(0.05):
            pass

    def read_stream() -> None:
        try:
            with open_fn(
                request,
                timeout=min(
                    settings.stream_idle_timeout_seconds,
                    settings.generation_budget_seconds,
                ),
            ) as response:
                response_holder.append(response)
                while not stop_reader.is_set():
                    try:
                        raw_line = response.readline(MAX_HTTP_RESPONSE_BYTES + 1)
                    except (OSError, urllib.error.URLError) as exc:
                        publish_stream_event("read_error", exc)
                        return
                    publish_stream_event("line", raw_line)
                    if not raw_line:
                        return
        except urllib.error.HTTPError as exc:
            publish_stream_event("http_error", exc)
        except (OSError, urllib.error.URLError) as exc:
            publish_stream_event("open_error", exc)
        except Exception as exc:  # noqa: BLE001 - transfer worker failures to caller
            publish_stream_event("unexpected_error", exc)

    def stop_stream() -> None:
        stop_reader.set()
        event_processed.set()
        if response_holder:
            close = getattr(response_holder[0], "close", None)
            if callable(close):
                try:
                    close()
                except OSError:
                    pass

    def idle_timeout_error(elapsed: float, cause: object | None = None) -> AIProviderError:
        detail = f"原始错误：{cause}" if cause is not None else ""
        return AIProviderError(
            "Ollama AI 生成流式读取空闲超时"
            f"（实际等待 {elapsed:.3f} 秒；"
            "两个完整数据块之间的最长间隔 "
            f"stream_idle_timeout_seconds="
            f"{settings.stream_idle_timeout_seconds} 秒；"
            f"旧配置 timeout_seconds={settings.timeout_seconds} 秒；"
            f"已生成 {content_characters} 字符）。"
            "可调高 stream_idle_timeout_seconds 或改用更小模型。"
            f"{detail}"
        )

    reader = threading.Thread(
        target=read_stream,
        name="research-os-ollama-stream-reader",
        daemon=True,
    )
    last_chunk_elapsed = 0.0
    try:
        reader.start()
        try:
            while True:
                elapsed = check_budget()
                if elapsed - last_chunk_elapsed >= settings.stream_idle_timeout_seconds:
                    raise idle_timeout_error(elapsed)
                if (
                    progress_fn is not None
                    and progress_interval_seconds > 0
                    and elapsed >= next_progress
                ):
                    progress_fn(
                        "本地 AI 生成进度："
                        f"已用 {elapsed:.1f} 秒，已接收 {content_characters} 字符。"
                    )
                    next_progress = elapsed + progress_interval_seconds

                deadlines = [
                    settings.generation_budget_seconds - elapsed,
                    settings.stream_idle_timeout_seconds
                    - (elapsed - last_chunk_elapsed),
                ]
                if progress_fn is not None and progress_interval_seconds > 0:
                    deadlines.append(next_progress - elapsed)
                wait_seconds = max(0.0, min(deadlines))
                try:
                    kind, payload, event_at = stream_events.get(timeout=wait_seconds)
                except queue.Empty:
                    continue

                try:
                    event_elapsed = event_at - started
                    if event_elapsed >= settings.generation_budget_seconds:
                        check_budget()
                    if kind == "http_error" or kind == "open_error":
                        raise payload
                    if kind == "unexpected_error":
                        raise payload
                    if kind == "read_error":
                        raise idle_timeout_error(event_elapsed, payload) from payload
                    if kind != "line" or not isinstance(payload, bytes):
                        raise AIProviderError("Ollama 流式读取器返回了无效事件")
                    raw_line = payload
                    if not raw_line:
                        break
                    if raw_line.strip():
                        last_chunk_elapsed = event_elapsed
                    line_number += 1
                    raw_bytes += len(raw_line)
                    if raw_bytes > MAX_HTTP_RESPONSE_BYTES:
                        raise AIProviderError("Ollama 流式返回内容超过安全上限")
                    if not raw_line.strip():
                        continue
                    try:
                        value = json.loads(raw_line.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise AIProviderError(
                            f"Ollama 流式响应第 {line_number} 行不是有效 NDJSON"
                        ) from exc
                    if not isinstance(value, dict):
                        raise AIProviderError(
                            f"Ollama 流式响应第 {line_number} 行必须是 JSON 对象"
                        )
                    saw_record = True
                    error = value.get("error")
                    if isinstance(error, str) and error:
                        raise AIProviderError(f"Ollama 流式生成返回错误：{error}")
                    model = value.get("model")
                    if isinstance(model, str):
                        returned_model = model
                    message = value.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str):
                            chunks.append(content)
                            content_characters += len(content)
                            if content_characters > settings.max_response_chars:
                                raise AIProviderError("Ollama 正文超过配置的字符上限")
                        thinking = message.get("thinking")
                        if isinstance(thinking, str):
                            thinking_character_count += len(thinking)
                    current_done_reason = value.get("done_reason")
                    if isinstance(current_done_reason, str):
                        done_reason = current_done_reason
                    current_eval_count = value.get("eval_count")
                    if isinstance(current_eval_count, int):
                        eval_count = current_eval_count
                    if value.get("done") is True:
                        saw_done = True
                    if (
                        progress_fn is not None
                        and progress_interval_seconds > 0
                        and event_elapsed >= next_progress
                    ):
                        progress_fn(
                            "本地 AI 生成进度："
                            f"已用 {event_elapsed:.1f} 秒，已接收 {content_characters} 字符。"
                        )
                        next_progress = event_elapsed + progress_interval_seconds
                    if saw_done:
                        break
                finally:
                    event_processed.set()
        finally:
            stop_stream()
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise AIProviderError(f"Ollama 请求失败（HTTP {exc.code}）：{detail}") from exc
    except AIProviderError:
        raise
    except (OSError, urllib.error.URLError) as exc:
        elapsed = elapsed_seconds()
        raise AIProviderError(
            "Ollama AI 生成调用失败"
            f"（实际等待 {elapsed:.3f} 秒；"
            f"旧配置 timeout_seconds={settings.timeout_seconds} 秒）；"
            f"流式连接空闲上限为 {settings.stream_idle_timeout_seconds} 秒；"
            "请确认 Ollama 服务和模型可用。"
            f"原始错误：{exc}"
        ) from exc
    if not saw_record:
        raise AIProviderError("Ollama 返回了空的 NDJSON 流")
    if not saw_done:
        raise AIProviderError("Ollama NDJSON 流在生成完成标记前意外结束")
    content = "".join(chunks).strip()
    if not content:
        raise AIProviderError("Ollama NDJSON 流没有返回有效正文")
    return AIResponse(
        content=content,
        provider=settings.provider,
        model=returned_model,
        endpoint=settings.endpoint,
        elapsed_seconds=round(elapsed_seconds(), 3),
        done_reason=done_reason,
        eval_count=eval_count,
        thinking_character_count=thinking_character_count,
        truncated=done_reason == "length",
    )
