from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_os_mvp.errors import IntegrityError
from research_os_mvp.integrity import (
    HASH_MANIFEST,
    HASH_SIDECAR,
    ZERO_HASH,
    append_chained_record,
    canonical_json_bytes,
    canonical_json_text,
    read_json,
    sha256_bytes,
    sha256_file,
    verify_chained_log,
    verify_hash_manifest,
    write_hash_manifest,
    write_json_atomic,
    write_text_atomic,
)


class IntegrityTests(unittest.TestCase):
    def _write_resigned_manifest(self, run_dir: Path, manifest: object) -> None:
        manifest_path = run_dir / HASH_MANIFEST
        write_json_atomic(manifest_path, manifest)
        write_text_atomic(
            run_dir / HASH_SIDECAR,
            f"{sha256_file(manifest_path)}  {HASH_MANIFEST}\n",
        )

    def _manifest_fixture(self, run_dir: Path) -> dict:
        (run_dir / "artifact.txt").write_text("trusted", encoding="utf-8")
        return write_hash_manifest(run_dir)

    def test_atomic_write_removes_temporary_file_after_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "artifact.txt"

            with patch(
                "research_os_mvp.integrity.os.replace",
                side_effect=OSError("replace failed"),
            ), self.assertRaisesRegex(OSError, "replace failed"):
                write_text_atomic(target, "content")

            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".artifact.txt.*.tmp")), [])

    def test_read_json_wraps_invalid_json_as_integrity_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(IntegrityError, "Cannot read valid JSON"):
                read_json(path)

    def test_chained_log_round_trip_and_reserved_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "events.jsonl"
            first = append_chained_record(path, {"event": "created"})
            second = append_chained_record(path, {"event": "paused"})

            self.assertEqual(first["sequence"], 1)
            self.assertEqual(second["sequence"], 2)
            self.assertEqual(second["previous_hash"], first["hash"])
            self.assertEqual(verify_chained_log(path), (2, second["hash"]))

            with self.assertRaisesRegex(IntegrityError, "Reserved chained-log fields"):
                append_chained_record(path, {"sequence": 3})

    def test_chained_log_rejects_each_structural_corruption(self) -> None:
        unsigned = {
            "event": "created",
            "sequence": 1,
            "previous_hash": ZERO_HASH,
        }
        valid = dict(unsigned)
        valid["hash"] = sha256_bytes(canonical_json_bytes(unsigned))

        wrong_sequence = copy.deepcopy(valid)
        wrong_sequence["sequence"] = 2
        wrong_previous = copy.deepcopy(valid)
        wrong_previous["previous_hash"] = "1" * 64
        invalid_hash = copy.deepcopy(valid)
        invalid_hash["hash"] = "short"
        mismatched_hash = copy.deepcopy(valid)
        mismatched_hash["hash"] = "f" * 64
        cases = (
            ("missing-newline", canonical_json_text(valid), "missing its newline"),
            ("invalid-json", "not-json\n", "Invalid JSON"),
            ("non-object", "[]\n", "not an object"),
            ("sequence", canonical_json_text(wrong_sequence) + "\n", "Invalid sequence"),
            (
                "previous-hash",
                canonical_json_text(wrong_previous) + "\n",
                "Broken previous_hash",
            ),
            ("invalid-hash", canonical_json_text(invalid_hash) + "\n", "Invalid hash"),
            ("hash-mismatch", canonical_json_text(mismatched_hash) + "\n", "Hash mismatch"),
        )

        for name, content, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "events.jsonl"
                path.write_text(content, encoding="utf-8", newline="")
                with self.assertRaisesRegex(IntegrityError, message):
                    verify_chained_log(path)

    def test_hash_manifest_rejects_missing_or_invalid_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            with self.assertRaisesRegex(IntegrityError, "missing HASHES"):
                verify_hash_manifest(run_dir)

        for name, sidecar, message in (
            ("invalid-format", "invalid\n", "invalid format"),
            ("wrong-digest", f"{'0' * 64}  {HASH_MANIFEST}\n", "does not match"),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = Path(temporary)
                self._manifest_fixture(run_dir)
                write_text_atomic(run_dir / HASH_SIDECAR, sidecar)
                with self.assertRaisesRegex(IntegrityError, message):
                    verify_hash_manifest(run_dir)

    def test_hash_manifest_rejects_invalid_entries_after_valid_signature(self) -> None:
        cases = (
            ("algorithm", "unsupported format"),
            ("files-type", "files must be a list"),
            ("entry-type", "non-object entry"),
            ("empty-path", "invalid path"),
            ("escape", "escapes the Run directory"),
            ("missing-file", "missing or not a regular file"),
            ("size", "Size mismatch"),
            ("digest", "SHA-256 mismatch"),
        )

        for name, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = Path(temporary)
                manifest = self._manifest_fixture(run_dir)
                if name == "algorithm":
                    manifest["algorithm"] = "MD5"
                elif name == "files-type":
                    manifest["files"] = {}
                elif name == "entry-type":
                    manifest["files"] = [None]
                elif name == "empty-path":
                    manifest["files"][0]["path"] = ""
                elif name == "escape":
                    manifest["files"][0]["path"] = "../outside.txt"
                elif name == "missing-file":
                    manifest["files"][0]["path"] = "missing.txt"
                elif name == "size":
                    manifest["files"][0]["size"] += 1
                elif name == "digest":
                    manifest["files"][0]["sha256"] = "0" * 64
                self._write_resigned_manifest(run_dir, manifest)

                with self.assertRaisesRegex(IntegrityError, message):
                    verify_hash_manifest(run_dir)

    def test_hash_manifest_rejects_unrecorded_and_temporary_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            self._manifest_fixture(run_dir)
            (run_dir / "unrecorded.txt").write_text("new", encoding="utf-8")
            with self.assertRaisesRegex(IntegrityError, "does not exactly match"):
                verify_hash_manifest(run_dir)

        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            (run_dir / "unfinished.tmp").write_text("partial", encoding="utf-8")
            with self.assertRaisesRegex(IntegrityError, "Temporary file remains"):
                write_hash_manifest(run_dir)


if __name__ == "__main__":
    unittest.main()
