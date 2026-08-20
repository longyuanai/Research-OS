from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.errors import PackValidationError
from research_os_mvp.pack import load_pack
from tests.helpers import valid_pack_data, write_pack


class PackValidationTests(unittest.TestCase):
    def test_example_pack_is_valid_and_has_three_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack_path = write_pack(Path(temporary) / "pack.json")
            loaded = load_pack(pack_path)
            self.assertEqual(loaded.data["pack_id"], "PACK-MVP-three-task-demo")
            self.assertEqual(len(loaded.data["mission"]["tasks"]), 3)
            self.assertEqual(len(loaded.canonical_sha256), 64)

    def test_canonical_hash_ignores_json_whitespace_and_key_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = valid_pack_data()
            first = write_pack(root / "first.json", data)
            second = root / "second.json"
            second.write_text(
                json.dumps(dict(reversed(list(data.items()))), separators=(",", ":")),
                encoding="utf-8",
            )
            self.assertEqual(
                load_pack(first).canonical_sha256,
                load_pack(second).canonical_sha256,
            )

    def test_pack_rejects_wrong_task_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = valid_pack_data()
            data["mission"]["tasks"].pop()
            pack_path = write_pack(Path(temporary) / "pack.json", data)
            with self.assertRaisesRegex(PackValidationError, "exactly 3 Tasks"):
                load_pack(pack_path)

    def test_pack_rejects_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = valid_pack_data()
            data["unexpected"] = "value"
            pack_path = write_pack(Path(temporary) / "pack.json", data)
            with self.assertRaisesRegex(PackValidationError, "unexpected"):
                load_pack(pack_path)

    def test_pack_rejects_runtime_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = valid_pack_data()
            data["permissions"]["network"] = True
            pack_path = write_pack(Path(temporary) / "pack.json", data)
            with self.assertRaisesRegex(PackValidationError, "network.*false"):
                load_pack(pack_path)

    def test_pack_rejects_non_semver_foundation_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = valid_pack_data()
            data["foundation_version"] = "latest"
            pack_path = write_pack(Path(temporary) / "pack.json", data)
            with self.assertRaisesRegex(PackValidationError, "foundation_version.*SemVer"):
                load_pack(pack_path)

    def test_pack_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack_path = Path(temporary) / "pack.json"
            pack_path.write_text('{"pack_id":"one","pack_id":"two"}', encoding="utf-8")
            with self.assertRaisesRegex(PackValidationError, "Duplicate JSON key"):
                load_pack(pack_path)


if __name__ == "__main__":
    unittest.main()
