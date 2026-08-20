from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_os_mvp.errors import MVPError
from research_os_mvp.runtime import record_supplemental_evidence

MAX_COMMAND_OUTPUT_CHARS = 200_000


class GitIntegrationError(MVPError):
    """Raised when a Git snapshot or detected test cannot be collected."""


@dataclass(frozen=True)
class GitSnapshot:
    content: str
    source: str
    method: str
    limitations: str
    test_command: tuple[str, ...] | None
    test_status: str


def normalize_repo_path(value: str | Path) -> Path:
    cleaned = str(value).strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    if not cleaned:
        raise GitIntegrationError("Git 项目路径为空")
    candidate = Path(cleaned).expanduser()
    if candidate.is_symlink():
        raise GitIntegrationError("Git 项目路径不得是符号链接")
    try:
        repo = candidate.resolve(strict=True)
    except OSError as exc:
        raise GitIntegrationError(f"Git 项目路径不存在：{cleaned}") from exc
    if not repo.is_dir():
        raise GitIntegrationError("Git 项目路径必须是普通目录")
    return repo


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitIntegrationError(f"命令不存在：{command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitIntegrationError(f"命令超过 {timeout} 秒：{' '.join(command)}") from exc


def _git(repo: Path, *args: str, allow_failure: bool = False) -> str:
    result = _run(("git", "-C", str(repo), *args), cwd=repo, timeout=30)
    output = result.stdout[:MAX_COMMAND_OUTPUT_CHARS].strip()
    if result.returncode != 0 and not allow_failure:
        raise GitIntegrationError(f"Git 命令失败：git {' '.join(args)}\n{output}")
    return output


def detect_test_command(repo: Path | str) -> tuple[str, ...] | None:
    path = Path(repo)
    tests_dir = path / "tests"
    python_tests = tests_dir.is_dir() and any(tests_dir.rglob("test*.py"))
    pyproject = path / "pyproject.toml"
    pytest_configured = (path / "pytest.ini").is_file() or (path / "conftest.py").is_file()
    if pyproject.is_file():
        try:
            pytest_configured = pytest_configured or "pytest" in pyproject.read_text(
                encoding="utf-8",
                errors="replace",
            ).lower()
        except OSError as exc:
            raise GitIntegrationError(f"pyproject.toml 读取失败：{exc}") from exc
    if python_tests or pytest_configured:
        if pytest_configured:
            return (sys.executable, "-m", "pytest", "-q")
        return (sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    package = path / "package.json"
    if package.is_file():
        try:
            value = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GitIntegrationError(f"package.json 读取失败：{exc}") from exc
        scripts = value.get("scripts") if isinstance(value, dict) else None
        if isinstance(scripts, dict) and isinstance(scripts.get("test"), str):
            return ("npm", "test")
    if (path / "Cargo.toml").is_file():
        return ("cargo", "test")
    if (path / "go.mod").is_file():
        return ("go", "test", "./...")
    return None


def collect_git_snapshot(
    repo_value: str | Path,
    *,
    run_tests: bool,
) -> GitSnapshot:
    repo = normalize_repo_path(repo_value)
    inside = _git(repo, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        raise GitIntegrationError("所选目录不在 Git 工作树中")
    root_text = _git(repo, "rev-parse", "--show-toplevel")
    root_input = Path(root_text)
    if root_input.is_symlink():
        raise GitIntegrationError("Git 根目录不得是符号链接")
    root = root_input.resolve(strict=True)
    head_result = _run(
        ("git", "-C", str(root), "rev-parse", "--verify", "HEAD"),
        cwd=root,
        timeout=30,
    )
    head = head_result.stdout.strip() if head_result.returncode == 0 else "UNBORN"
    branch = _git(root, "branch", "--show-current", allow_failure=True) or "DETACHED"
    status = _git(root, "status", "--short", allow_failure=True) or "(clean)"
    diff_stat = _git(root, "diff", "--stat", allow_failure=True) or "(no unstaged diff)"
    diff_check = _git(root, "diff", "--check", allow_failure=True)
    test_command = detect_test_command(root)
    test_status = "NOT_RUN"
    test_output = "自动测试未运行。"
    if run_tests:
        if test_command is None:
            test_status = "NO_DETECTED_COMMAND"
            test_output = "没有检测到受支持的自动测试入口。"
        else:
            result = _run(test_command, cwd=root, timeout=300)
            test_status = "PASS" if result.returncode == 0 else "FAIL"
            test_output = result.stdout[:MAX_COMMAND_OUTPUT_CHARS]
    command_display = " ".join(test_command) if test_command else "未检测到"
    content = (
        f"Git 根目录：{root}\n"
        f"分支：{branch}\n"
        f"HEAD：{head}\n"
        f"\n## git status --short\n{status}\n"
        f"\n## git diff --stat\n{diff_stat}\n"
        f"\n## git diff --check\n{diff_check or '(pass)'}\n"
        f"\n## 自动测试\n命令：{command_display}\n结果：{test_status}\n\n{test_output}"
    )
    return GitSnapshot(
        content=content,
        source=f"git://{root}@{head}",
        method="只读采集 Git HEAD/分支/状态/diff；可选执行检测到的项目测试命令",
        limitations=(
            "Git 快照只代表采集时刻；未读取未跟踪文件内容。"
            "自动测试会执行所选项目代码，结果仅覆盖检测到的测试入口。"
        ),
        test_command=test_command,
        test_status=test_status,
    )


def record_git_snapshot_evidence(
    run_dir: Path | str,
    repo_value: Path | str,
    *,
    run_tests: bool,
) -> dict[str, Any]:
    """Collect one Git snapshot and append it to the paused Task-2 Evidence set."""
    snapshot = collect_git_snapshot(repo_value, run_tests=run_tests)
    recorded = record_supplemental_evidence(
        run_dir,
        content=snapshot.content,
        source=snapshot.source,
        method=snapshot.method,
        limitations=snapshot.limitations,
        collected_by="Research-OS Git Integration",
        evidence_role="git_project_snapshot",
    )
    return {
        **recorded,
        "test_command": list(snapshot.test_command) if snapshot.test_command else None,
        "test_status": snapshot.test_status,
    }
