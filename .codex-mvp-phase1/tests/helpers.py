from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PACK = ROOT / "examples" / "builder-pack.json"


def valid_pack_data() -> dict:
    return copy.deepcopy(json.loads(EXAMPLE_PACK.read_text(encoding="utf-8")))


def write_pack(path: Path, data: dict | None = None) -> Path:
    path.write_text(
        json.dumps(data or valid_pack_data(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path
