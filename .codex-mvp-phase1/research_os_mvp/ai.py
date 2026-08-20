from __future__ import annotations

import json
import re
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
    maximum = ai.get("max_response_chars", 200_000)
    max_output_tokens = ai.get("max_output_tokens", 1536)
    automatic = ai.get("automatic_research", True)
    if not isinstance(health_timeout, int) or not 1 <= health_timeout <= 300:
        raise AIProviderError("Ollama 健康检查超时必须在 1-300 秒之间")
    if not isinstance(timeout, int) or not 10 <= timeout <= 900:
        raise AIProviderError("AI 超时必须在 10-900 秒之间")
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
) -> AIResponse:
    cleaned = prompt.strip()
    if not cleaned:
        raise AIProviderError("AI 研究指令为空")
    if len(cleaned) > 120_000:
        raise AIProviderError("AI 研究指令超过 120000 字符")
    payload = {
        "model": settings.model,
        "stream": False,
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
    started = time.monotonic()
    try:
        with open_fn(request, timeout=settings.timeout_seconds) as response:
            value = _read_json_response(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise AIProviderError(f"Ollama 请求失败（HTTP {exc.code}）：{detail}") from exc
    except (OSError, urllib.error.URLError) as exc:
        elapsed = time.monotonic() - started
        raise AIProviderError(
            "Ollama AI 生成调用失败"
            f"（实际等待 {elapsed:.3f} 秒；timeout_seconds={settings.timeout_seconds} 秒）；"
            f"可调高 timeout_seconds 或改用更小模型。原始错误：{exc}"
        ) from exc
    message = value.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        error = value.get("error")
        raise AIProviderError(f"Ollama 没有返回有效正文：{error or '未知原因'}")
    content = content.strip()
    if len(content) > settings.max_response_chars:
        raise AIProviderError("Ollama 正文超过配置的字符上限")
    returned_model = value.get("model")
    done_reason = value.get("done_reason")
    eval_count = value.get("eval_count")
    thinking = message.get("thinking") if isinstance(message, dict) else None
    return AIResponse(
        content=content,
        provider=settings.provider,
        model=returned_model if isinstance(returned_model, str) else settings.model,
        endpoint=settings.endpoint,
        elapsed_seconds=round(time.monotonic() - started, 3),
        done_reason=done_reason if isinstance(done_reason, str) else None,
        eval_count=eval_count if isinstance(eval_count, int) else None,
        thinking_character_count=len(thinking) if isinstance(thinking, str) else 0,
        truncated=done_reason == "length",
    )
