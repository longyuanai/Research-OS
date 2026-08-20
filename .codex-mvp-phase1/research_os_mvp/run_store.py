from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, BinaryIO

from research_os_mvp.errors import IntegrityError, RunStateError
from research_os_mvp.integrity import (
    HASH_MANIFEST,
    RUNTIME_DIR,
    ZERO_HASH,
    read_json,
    sha256_file,
    utc_now,
)

CHECKPOINT_FILE = "checkpoint.sqlite3"
LOCK_FILE = "run.lock"
LEGACY_CHECKPOINT_SCHEMA_VERSION = "research-os-mvp-checkpoint/0.1"
REVIEW_CHECKPOINT_SCHEMA_VERSION = "research-os-mvp-checkpoint/0.2"
CHECKPOINT_SCHEMA_VERSION = "research-os-mvp-checkpoint/0.3"
SUPPORTED_CHECKPOINT_SCHEMA_VERSIONS = {
    LEGACY_CHECKPOINT_SCHEMA_VERSION,
    REVIEW_CHECKPOINT_SCHEMA_VERSION,
    CHECKPOINT_SCHEMA_VERSION,
}
DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0

_LOCKS_GUARD = threading.Lock()
_PROCESS_LOCKS: dict[str, threading.Lock] = {}


def _process_lock(path: Path) -> threading.Lock:
    key = os.path.normcase(str(path.resolve()))
    with _LOCKS_GUARD:
        return _PROCESS_LOCKS.setdefault(key, threading.Lock())


def _runtime_dir(run_dir: Path) -> Path:
    operational = run_dir / RUNTIME_DIR
    if operational.exists() and (operational.is_symlink() or not operational.is_dir()):
        raise RunStateError(f"Operational runtime path must be a directory: {operational}")
    operational.mkdir(exist_ok=True)
    return operational


def _acquire_os_lock(handle: BinaryIO, deadline: float) -> None:
    while True:
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except OSError as exc:
            if time.monotonic() >= deadline:
                raise RunStateError("Run 正被另一个进程使用，请稍后重试") from exc
            time.sleep(0.05)


def _release_os_lock(handle: BinaryIO) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def run_lock(
    run_dir: Path | str,
    *,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> Iterator[None]:
    """Hold one local, cross-process exclusive lock for a Run."""
    path = Path(run_dir)
    if path.is_symlink() or not path.is_dir():
        raise RunStateError(f"Run directory is missing or is a symlink: {path}")
    if timeout_seconds < 0:
        raise RunStateError("Run lock timeout must not be negative")

    deadline = time.monotonic() + timeout_seconds
    local_lock = _process_lock(path)
    remaining = max(0.0, deadline - time.monotonic())
    if not local_lock.acquire(timeout=remaining):
        raise RunStateError("Run 正被当前进程的另一个操作使用，请稍后重试")

    handle: BinaryIO | None = None
    acquired = False
    try:
        operational = _runtime_dir(path)
        lock_path = operational / LOCK_FILE
        if lock_path.exists() and (lock_path.is_symlink() or not lock_path.is_file()):
            raise RunStateError(f"Run lock path must be a regular file: {lock_path}")
        handle = lock_path.open("a+b")
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        _acquire_os_lock(handle, deadline)
        acquired = True
        yield
    finally:
        try:
            if handle is not None:
                try:
                    if acquired:
                        _release_os_lock(handle)
                finally:
                    handle.close()
        finally:
            local_lock.release()


def _checkpoint_path(run_dir: Path) -> Path:
    operational = _runtime_dir(run_dir)
    database = operational / CHECKPOINT_FILE
    if database.exists() and (database.is_symlink() or not database.is_file()):
        raise RunStateError(f"Checkpoint path must be a regular file: {database}")
    return database


def sync_checkpoint(run_dir: Path | str, status: dict[str, Any]) -> None:
    """Persist a derived checkpoint after canonical JSON artifacts verify."""
    path = Path(run_dir)
    state = read_json(path / "state.json")
    if not isinstance(state, dict):
        raise IntegrityError("state.json must contain an object")
    database = _checkpoint_path(path)
    state_sha256 = sha256_file(path / "state.json")
    manifest_sha256 = sha256_file(path / HASH_MANIFEST)
    state_json = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    checkpointed_at = utc_now()
    try:
        with closing(sqlite3.connect(database, timeout=5.0)) as connection:
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_checkpoint (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    schema_version TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    state_sha256 TEXT NOT NULL,
                    manifest_sha256 TEXT NOT NULL,
                    event_tail_hash TEXT NOT NULL,
                    approval_tail_hash TEXT NOT NULL,
                    review_tail_hash TEXT NOT NULL,
                    review_signature_tail_hash TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    approval_count INTEGER NOT NULL,
                    review_count INTEGER NOT NULL,
                    review_signature_count INTEGER NOT NULL,
                    evidence_count INTEGER NOT NULL,
                    report_count INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    checkpointed_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(run_checkpoint)")
            }
            if "review_tail_hash" not in columns:
                connection.execute(
                    "ALTER TABLE run_checkpoint ADD COLUMN review_tail_hash "
                    f"TEXT NOT NULL DEFAULT '{ZERO_HASH}'"
                )
            if "review_count" not in columns:
                connection.execute(
                    "ALTER TABLE run_checkpoint ADD COLUMN review_count "
                    "INTEGER NOT NULL DEFAULT 0"
                )
            if "review_signature_tail_hash" not in columns:
                connection.execute(
                    "ALTER TABLE run_checkpoint ADD COLUMN review_signature_tail_hash "
                    f"TEXT NOT NULL DEFAULT '{ZERO_HASH}'"
                )
            if "review_signature_count" not in columns:
                connection.execute(
                    "ALTER TABLE run_checkpoint ADD COLUMN review_signature_count "
                    "INTEGER NOT NULL DEFAULT 0"
                )
            connection.execute(
                """
                INSERT INTO run_checkpoint (
                    singleton, schema_version, run_id, status, state_json,
                    state_sha256, manifest_sha256, event_tail_hash,
                    approval_tail_hash, review_tail_hash,
                    review_signature_tail_hash, event_count,
                    approval_count, review_count, review_signature_count,
                    evidence_count, report_count, updated_at, checkpointed_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    schema_version=excluded.schema_version,
                    run_id=excluded.run_id,
                    status=excluded.status,
                    state_json=excluded.state_json,
                    state_sha256=excluded.state_sha256,
                    manifest_sha256=excluded.manifest_sha256,
                    event_tail_hash=excluded.event_tail_hash,
                    approval_tail_hash=excluded.approval_tail_hash,
                    review_tail_hash=excluded.review_tail_hash,
                    review_signature_tail_hash=excluded.review_signature_tail_hash,
                    event_count=excluded.event_count,
                    approval_count=excluded.approval_count,
                    review_count=excluded.review_count,
                    review_signature_count=excluded.review_signature_count,
                    evidence_count=excluded.evidence_count,
                    report_count=excluded.report_count,
                    updated_at=excluded.updated_at,
                    checkpointed_at=excluded.checkpointed_at
                """,
                (
                    CHECKPOINT_SCHEMA_VERSION,
                    state["run_id"],
                    state["status"],
                    state_json,
                    state_sha256,
                    manifest_sha256,
                    state["event_tail_hash"],
                    state["approval_tail_hash"],
                    state.get("review_tail_hash", ZERO_HASH),
                    state.get("review_signature_tail_hash", ZERO_HASH),
                    status["event_count"],
                    status["approval_count"],
                    status["review_count"],
                    status.get("review_signature_count", 0),
                    status["evidence_count"],
                    status["report_count"],
                    state["updated_at"],
                    checkpointed_at,
                ),
            )
            connection.commit()
    except (OSError, sqlite3.Error, KeyError) as exc:
        raise RunStateError(f"无法写入 Run SQLite Checkpoint：{exc}") from exc


def read_checkpoint(run_dir: Path | str) -> dict[str, Any]:
    """Read the latest verified checkpoint without treating it as canonical state."""
    path = Path(run_dir)
    database = path / RUNTIME_DIR / CHECKPOINT_FILE
    if database.is_symlink() or not database.is_file():
        raise IntegrityError(f"Run is missing a valid SQLite checkpoint: {database}")
    try:
        uri = f"{database.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=5.0)) as connection:
            columns = {
                item[1] for item in connection.execute("PRAGMA table_info(run_checkpoint)")
            }
            has_review_columns = {"review_tail_hash", "review_count"}.issubset(columns)
            has_signature_columns = {
                "review_signature_tail_hash",
                "review_signature_count",
            }.issubset(columns)
            if has_review_columns and has_signature_columns:
                row = connection.execute(
                    """
                    SELECT schema_version, run_id, status, state_sha256,
                           manifest_sha256, event_tail_hash, approval_tail_hash,
                           review_tail_hash, review_signature_tail_hash,
                           event_count, approval_count, review_count,
                           review_signature_count, evidence_count, report_count,
                           updated_at, checkpointed_at
                    FROM run_checkpoint WHERE singleton = 1
                    """
                ).fetchone()
            elif has_review_columns:
                review_row = connection.execute(
                    """
                    SELECT schema_version, run_id, status, state_sha256,
                           manifest_sha256, event_tail_hash, approval_tail_hash,
                           review_tail_hash, event_count, approval_count,
                           review_count, evidence_count, report_count,
                           updated_at, checkpointed_at
                    FROM run_checkpoint WHERE singleton = 1
                    """
                ).fetchone()
                row = (
                    None
                    if review_row is None
                    else (
                        *review_row[:8],
                        ZERO_HASH,
                        *review_row[8:11],
                        0,
                        *review_row[11:],
                    )
                )
            else:
                legacy_row = connection.execute(
                    """
                    SELECT schema_version, run_id, status, state_sha256,
                           manifest_sha256, event_tail_hash, approval_tail_hash,
                           event_count, approval_count, evidence_count, report_count,
                           updated_at, checkpointed_at
                    FROM run_checkpoint WHERE singleton = 1
                    """
                ).fetchone()
                row = (
                    None
                    if legacy_row is None
                    else (
                        *legacy_row[:7],
                        ZERO_HASH,
                        ZERO_HASH,
                        *legacy_row[7:9],
                        0,
                        0,
                        *legacy_row[9:],
                    )
                )
    except (OSError, sqlite3.Error) as exc:
        raise IntegrityError(f"Cannot read SQLite checkpoint {database}: {exc}") from exc
    if row is None or row[0] not in SUPPORTED_CHECKPOINT_SCHEMA_VERSIONS:
        raise IntegrityError(f"SQLite checkpoint has an unsupported format: {database}")
    keys = (
        "schema_version",
        "run_id",
        "status",
        "state_sha256",
        "manifest_sha256",
        "event_tail_hash",
        "approval_tail_hash",
        "review_tail_hash",
        "review_signature_tail_hash",
        "event_count",
        "approval_count",
        "review_count",
        "review_signature_count",
        "evidence_count",
        "report_count",
        "updated_at",
        "checkpointed_at",
    )
    checkpoint = dict(zip(keys, row, strict=True))
    try:
        state_matches = sha256_file(path / "state.json") == checkpoint["state_sha256"]
        manifest_matches = (
            sha256_file(path / HASH_MANIFEST) == checkpoint["manifest_sha256"]
        )
    except OSError:
        checkpoint["canonical_alignment"] = "unavailable"
    else:
        checkpoint["canonical_alignment"] = (
            "matches" if state_matches and manifest_matches else "differs"
        )
    return checkpoint
