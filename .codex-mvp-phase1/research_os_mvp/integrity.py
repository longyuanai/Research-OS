from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_os_mvp.errors import IntegrityError

ZERO_HASH = "0" * 64
HASH_MANIFEST = "HASHES.json"
HASH_SIDECAR = "HASHES.sha256"
RUNTIME_DIR = ".runtime"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def canonical_json_text(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_text(value).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def write_json_atomic(path: Path, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    write_text_atomic(path, text)


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Cannot read valid JSON from {path}: {exc}") from exc


def verify_chained_log(path: Path) -> tuple[int, str]:
    if not path.exists():
        return 0, ZERO_HASH
    if path.is_symlink():
        raise IntegrityError(f"Chained log must not be a symlink: {path}")

    previous_hash = ZERO_HASH
    count = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.endswith("\n"):
                    raise IntegrityError(
                        f"Log line {line_number} is missing its newline: {path}"
                    )
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise IntegrityError(
                        f"Invalid JSON at {path}:{line_number}: {exc}"
                    ) from exc
                if not isinstance(record, dict):
                    raise IntegrityError(f"Log record is not an object: {path}:{line_number}")
                expected_sequence = count + 1
                if record.get("sequence") != expected_sequence:
                    raise IntegrityError(
                        f"Invalid sequence at {path}:{line_number}; "
                        f"expected {expected_sequence}"
                    )
                if record.get("previous_hash") != previous_hash:
                    raise IntegrityError(
                        f"Broken previous_hash at {path}:{line_number}"
                    )
                stored_hash = record.get("hash")
                if not isinstance(stored_hash, str) or len(stored_hash) != 64:
                    raise IntegrityError(f"Invalid hash at {path}:{line_number}")
                unsigned = dict(record)
                del unsigned["hash"]
                computed_hash = sha256_bytes(canonical_json_bytes(unsigned))
                if stored_hash != computed_hash:
                    raise IntegrityError(f"Hash mismatch at {path}:{line_number}")
                previous_hash = stored_hash
                count += 1
    except OSError as exc:
        raise IntegrityError(f"Cannot read chained log {path}: {exc}") from exc
    return count, previous_hash


def append_chained_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    reserved = {"sequence", "previous_hash", "hash"}
    collision = reserved.intersection(payload)
    if collision:
        raise IntegrityError(f"Reserved chained-log fields supplied: {sorted(collision)}")

    count, previous_hash = verify_chained_log(path)
    unsigned = dict(payload)
    unsigned["sequence"] = count + 1
    unsigned["previous_hash"] = previous_hash
    record = dict(unsigned)
    record["hash"] = sha256_bytes(canonical_json_bytes(unsigned))

    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (canonical_json_text(record) + "\n").encode("utf-8")
    try:
        with path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise IntegrityError(f"Cannot append chained record to {path}: {exc}") from exc
    return record


def _hashable_files(run_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(run_dir.rglob("*")):
        relative = path.relative_to(run_dir)
        if relative.parts and relative.parts[0] == RUNTIME_DIR:
            if path.is_symlink():
                raise IntegrityError(f"Operational runtime paths must not be symlinks: {path}")
            continue
        if path.name in {HASH_MANIFEST, HASH_SIDECAR}:
            continue
        if path.is_symlink():
            raise IntegrityError(f"Run artifacts must not contain symlinks: {path}")
        if path.is_file():
            if path.name.endswith(".tmp"):
                raise IntegrityError(f"Temporary file remains in Run: {path}")
            files.append(path)
    return files


def write_hash_manifest(run_dir: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in _hashable_files(run_dir):
        entries.append(
            {
                "path": path.relative_to(run_dir).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": "research-os-mvp-hashes/0.1",
        "algorithm": "SHA-256",
        "generated_at": utc_now(),
        "files": entries,
    }
    manifest_path = run_dir / HASH_MANIFEST
    write_json_atomic(manifest_path, manifest)
    manifest_hash = sha256_file(manifest_path)
    write_text_atomic(run_dir / HASH_SIDECAR, f"{manifest_hash}  {HASH_MANIFEST}\n")
    return manifest


def verify_hash_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / HASH_MANIFEST
    sidecar_path = run_dir / HASH_SIDECAR
    if not manifest_path.is_file() or not sidecar_path.is_file():
        raise IntegrityError("Run is missing HASHES.json or HASHES.sha256")
    try:
        sidecar_parts = sidecar_path.read_text(encoding="utf-8").strip().split()
    except OSError as exc:
        raise IntegrityError(f"Cannot read {sidecar_path}: {exc}") from exc
    if len(sidecar_parts) != 2 or sidecar_parts[1] != HASH_MANIFEST:
        raise IntegrityError("HASHES.sha256 has an invalid format")
    if sidecar_parts[0] != sha256_file(manifest_path):
        raise IntegrityError("HASHES.json does not match HASHES.sha256")

    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get("algorithm") != "SHA-256":
        raise IntegrityError("HASHES.json has an unsupported format")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise IntegrityError("HASHES.json files must be a list")

    recorded_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise IntegrityError("HASHES.json contains a non-object entry")
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        expected_size = entry.get("size")
        if not isinstance(relative, str) or not relative:
            raise IntegrityError("HASHES.json contains an invalid path")
        artifact = run_dir / Path(relative)
        try:
            artifact.resolve().relative_to(run_dir.resolve())
        except ValueError as exc:
            raise IntegrityError(f"Hash entry escapes the Run directory: {relative}") from exc
        if artifact.is_symlink() or not artifact.is_file():
            raise IntegrityError(f"Hash entry is missing or not a regular file: {relative}")
        if artifact.stat().st_size != expected_size:
            raise IntegrityError(f"Size mismatch for {relative}")
        if sha256_file(artifact) != expected_hash:
            raise IntegrityError(f"SHA-256 mismatch for {relative}")
        recorded_paths.append(relative)

    actual_paths = [path.relative_to(run_dir).as_posix() for path in _hashable_files(run_dir)]
    if recorded_paths != actual_paths:
        raise IntegrityError("HASHES.json does not exactly match the Run artifact set")
    return manifest
