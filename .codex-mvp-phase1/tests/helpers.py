from __future__ import annotations

import base64
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PACK = ROOT / "examples" / "builder-pack.json"
LEGACY_RUNS_BUNDLE = ROOT / "tests" / "fixtures" / "legacy-runs.bundle.json"


def valid_pack_data() -> dict:
    return copy.deepcopy(json.loads(EXAMPLE_PACK.read_text(encoding="utf-8")))


def write_pack(path: Path, data: dict | None = None) -> Path:
    path.write_text(
        json.dumps(data or valid_pack_data(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def materialize_legacy_runs(root: Path) -> Path:
    """Restore byte-exact immutable Run fixtures into a disposable directory."""

    target = root / "legacy-runs"
    bundle = json.loads(LEGACY_RUNS_BUNDLE.read_text(encoding="utf-8"))
    if bundle.get("schema_version") != "research-os-mvp-legacy-run-fixtures/0.1":
        raise AssertionError("legacy Run fixture bundle schema is invalid")
    for relative, encoded in bundle["files"].items():
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise AssertionError(
                f"legacy Run fixture path escapes its target: {relative!r}"
            )
        path = (target / relative_path).resolve()
        if not path.is_relative_to(target.resolve()):
            raise AssertionError(f"legacy Run fixture path is unsafe: {relative!r}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(encoded, validate=True))
    return target
