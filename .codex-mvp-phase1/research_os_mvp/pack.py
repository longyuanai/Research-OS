from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_os_mvp.errors import PackValidationError
from research_os_mvp.integrity import canonical_json_bytes, sha256_bytes

MAX_PACK_BYTES = 1024 * 1024
PACK_SCHEMA_VERSION = "research-os-mvp-pack/0.1"
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
PACK_ID_PATTERN = re.compile(r"^PACK-[A-Z0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*$")
MISSION_ID_PATTERN = re.compile(
    r"^MISSION-[A-Z0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
TASK_ID_PATTERN = re.compile(
    r"^TASK-[A-Z0-9]+-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
RUN_ID_PATTERN = re.compile(r"^run-[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class LoadedPack:
    path: Path
    data: dict[str, Any]
    canonical_sha256: str


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackValidationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _exact_fields(value: dict[str, Any], expected: set[str], location: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append(f"missing={missing}")
        if extra:
            parts.append(f"unexpected={extra}")
        raise PackValidationError(f"{location} fields are invalid: {'; '.join(parts)}")


def _required_string(value: Any, location: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PackValidationError(f"{location} must be a non-empty string")
    if len(value) > maximum:
        raise PackValidationError(f"{location} exceeds {maximum} characters")
    return value


def _string_list(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PackValidationError(f"{location} must be a non-empty list")
    for index, item in enumerate(value):
        _required_string(item, f"{location}[{index}]")
    return value


def validate_pack_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise PackValidationError("Pack root must be a JSON object")
    _exact_fields(
        data,
        {
            "schema_version",
            "pack_id",
            "version",
            "status",
            "pack_type",
            "scope",
            "foundation_version",
            "constitution_version",
            "supersedes",
            "permissions",
            "mission",
        },
        "pack",
    )
    if data["schema_version"] != PACK_SCHEMA_VERSION:
        raise PackValidationError(
            f"schema_version must be {PACK_SCHEMA_VERSION!r}"
        )
    pack_id = _required_string(data["pack_id"], "pack.pack_id")
    if not PACK_ID_PATTERN.fullmatch(pack_id):
        raise PackValidationError("pack.pack_id has an invalid identifier form")
    version = _required_string(data["version"], "pack.version")
    if not SEMVER_PATTERN.fullmatch(version):
        raise PackValidationError("pack.version must be SemVer")
    if data["status"] != "Draft":
        raise PackValidationError("prototype Pack status must be Draft")
    if data["pack_type"] != "Tool":
        raise PackValidationError("prototype Pack pack_type must be Tool")
    foundation_version = _required_string(
        data["foundation_version"], "pack.foundation_version"
    )
    constitution_version = _required_string(
        data["constitution_version"], "pack.constitution_version"
    )
    if not SEMVER_PATTERN.fullmatch(foundation_version):
        raise PackValidationError("pack.foundation_version must be SemVer")
    if not SEMVER_PATTERN.fullmatch(constitution_version):
        raise PackValidationError("pack.constitution_version must be SemVer")
    if data["supersedes"] != "none":
        raise PackValidationError("first prototype Pack must declare supersedes=none")

    permissions = data["permissions"]
    if not isinstance(permissions, dict):
        raise PackValidationError("pack.permissions must be an object")
    _exact_fields(
        permissions,
        {"network", "subprocess", "external_writes"},
        "pack.permissions",
    )
    for permission in ("network", "subprocess", "external_writes"):
        if permissions[permission] is not False:
            raise PackValidationError(
                f"pack.permissions.{permission} must be false in this prototype"
            )

    mission = data["mission"]
    if not isinstance(mission, dict):
        raise PackValidationError("pack.mission must be an object")
    _exact_fields(
        mission,
        {
            "mission_id",
            "title",
            "success_criteria",
            "exit_conditions",
            "tasks",
        },
        "pack.mission",
    )
    mission_id = _required_string(mission["mission_id"], "pack.mission.mission_id")
    if not MISSION_ID_PATTERN.fullmatch(mission_id):
        raise PackValidationError("pack.mission.mission_id has an invalid identifier form")
    if data["scope"] != mission_id:
        raise PackValidationError("pack.scope must equal pack.mission.mission_id")
    _required_string(mission["title"], "pack.mission.title")
    _string_list(mission["success_criteria"], "pack.mission.success_criteria")
    _string_list(mission["exit_conditions"], "pack.mission.exit_conditions")

    tasks = mission["tasks"]
    if not isinstance(tasks, list) or len(tasks) != 3:
        raise PackValidationError("prototype Mission must contain exactly 3 Tasks")
    seen_task_ids: set[str] = set()
    expected_operations = ["record_evidence", "record_evidence", "compose_report"]
    for index, task in enumerate(tasks):
        location = f"pack.mission.tasks[{index}]"
        if not isinstance(task, dict):
            raise PackValidationError(f"{location} must be an object")
        _exact_fields(
            task,
            {"task_id", "name", "operation", "requires_approval", "input"},
            location,
        )
        task_id = _required_string(task["task_id"], f"{location}.task_id")
        if not TASK_ID_PATTERN.fullmatch(task_id):
            raise PackValidationError(f"{location}.task_id has an invalid identifier form")
        if task_id in seen_task_ids:
            raise PackValidationError(f"duplicate task_id: {task_id}")
        seen_task_ids.add(task_id)
        _required_string(task["name"], f"{location}.name")
        if task["operation"] != expected_operations[index]:
            raise PackValidationError(
                f"{location}.operation must be {expected_operations[index]!r}"
            )
        if task["requires_approval"] is not True:
            raise PackValidationError(f"{location}.requires_approval must be true")
        task_input = task["input"]
        if not isinstance(task_input, dict):
            raise PackValidationError(f"{location}.input must be an object")
        if task["operation"] == "record_evidence":
            _exact_fields(
                task_input,
                {"content", "source", "method", "limitations"},
                f"{location}.input",
            )
            _required_string(
                task_input["content"], f"{location}.input.content", maximum=65536
            )
            _required_string(task_input["source"], f"{location}.input.source")
            _required_string(task_input["method"], f"{location}.input.method")
            _required_string(
                task_input["limitations"], f"{location}.input.limitations", maximum=2000
            )
        else:
            _exact_fields(task_input, {"title"}, f"{location}.input")
            _required_string(task_input["title"], f"{location}.input.title")
    return data


def load_pack(path: Path | str) -> LoadedPack:
    pack_path = Path(path)
    if pack_path.is_symlink():
        raise PackValidationError("Pack path must not be a symlink")
    if not pack_path.is_file():
        raise PackValidationError(f"Pack file does not exist: {pack_path}")
    size = pack_path.stat().st_size
    if size > MAX_PACK_BYTES:
        raise PackValidationError(f"Pack exceeds {MAX_PACK_BYTES} bytes")
    try:
        text = pack_path.read_text(encoding="utf-8")
        data = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except UnicodeDecodeError as exc:
        raise PackValidationError("Pack must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise PackValidationError(f"Pack is not valid JSON: {exc}") from exc
    validated = validate_pack_data(data)
    return LoadedPack(
        path=pack_path.resolve(),
        data=validated,
        canonical_sha256=sha256_bytes(canonical_json_bytes(validated)),
    )


def validate_run_id(run_id: str) -> None:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PackValidationError(
            "run_id must match run-<lowercase letters, digits, and hyphen groups>"
        )
