from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from research_os_mvp.integrity import ZERO_HASH, sha256_file
from research_os_mvp.run_store import (
    CHECKPOINT_SCHEMA_VERSION,
    LEGACY_CHECKPOINT_SCHEMA_VERSION,
    RUNTIME_DIR,
    read_checkpoint,
    run_lock,
)
from research_os_mvp.runtime import create_run, verify_run
from tests.helpers import EXAMPLE_PACK, ROOT


class RunStoreTests(unittest.TestCase):
    def test_checkpoint_tracks_verified_state_and_is_not_canonical_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-checkpoint-test")
            run_dir = root / "runs" / status["run_id"]

            checkpoint = read_checkpoint(run_dir)
            manifest = json.loads((run_dir / "HASHES.json").read_text(encoding="utf-8"))

            self.assertEqual(status["checkpoint"], "current")
            self.assertEqual(checkpoint["status"], "paused")
            self.assertEqual(
                checkpoint["state_sha256"],
                sha256_file(run_dir / "state.json"),
            )
            self.assertTrue(
                all(not entry["path"].startswith(f"{RUNTIME_DIR}/") for entry in manifest["files"])
            )

    def test_legacy_run_recreates_missing_checkpoint_without_changing_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-legacy-test")
            run_dir = root / "runs" / status["run_id"]
            manifest_hash = sha256_file(run_dir / "HASHES.json")

            shutil.rmtree(run_dir / RUNTIME_DIR)
            verified = verify_run(run_dir)

            self.assertEqual(verified["checkpoint"], "current")
            self.assertTrue((run_dir / RUNTIME_DIR / "checkpoint.sqlite3").is_file())
            self.assertEqual(sha256_file(run_dir / "HASHES.json"), manifest_hash)

    def test_legacy_checkpoint_schema_is_read_and_migrated_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-checkpoint-migration")
            run_dir = root / "runs" / status["run_id"]
            database = run_dir / RUNTIME_DIR / "checkpoint.sqlite3"
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            database.unlink()
            with closing(sqlite3.connect(database)) as connection:
                connection.execute(
                    """
                    CREATE TABLE run_checkpoint (
                        singleton INTEGER PRIMARY KEY,
                        schema_version TEXT NOT NULL,
                        run_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        state_json TEXT NOT NULL,
                        state_sha256 TEXT NOT NULL,
                        manifest_sha256 TEXT NOT NULL,
                        event_tail_hash TEXT NOT NULL,
                        approval_tail_hash TEXT NOT NULL,
                        event_count INTEGER NOT NULL,
                        approval_count INTEGER NOT NULL,
                        evidence_count INTEGER NOT NULL,
                        report_count INTEGER NOT NULL,
                        updated_at TEXT NOT NULL,
                        checkpointed_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO run_checkpoint VALUES
                    (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        LEGACY_CHECKPOINT_SCHEMA_VERSION,
                        status["run_id"],
                        status["status"],
                        json.dumps(state),
                        sha256_file(run_dir / "state.json"),
                        sha256_file(run_dir / "HASHES.json"),
                        state["event_tail_hash"],
                        state["approval_tail_hash"],
                        status["event_count"],
                        status["approval_count"],
                        status["evidence_count"],
                        status["report_count"],
                        state["updated_at"],
                        "2026-08-09T00:00:00Z",
                    ),
                )
                connection.commit()

            legacy = read_checkpoint(run_dir)
            self.assertEqual(legacy["schema_version"], LEGACY_CHECKPOINT_SCHEMA_VERSION)
            self.assertEqual(legacy["review_tail_hash"], ZERO_HASH)
            self.assertEqual(legacy["review_count"], 0)

            verify_run(run_dir)
            migrated = read_checkpoint(run_dir)
            self.assertEqual(migrated["schema_version"], CHECKPOINT_SCHEMA_VERSION)
            self.assertEqual(migrated["review_count"], 0)
            with closing(sqlite3.connect(database)) as connection:
                columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(run_checkpoint)")
                }
            self.assertTrue({"review_tail_hash", "review_count"}.issubset(columns))

    def test_cross_process_lock_times_out_instead_of_writing_concurrently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary) / "run-lock-test"
            run_dir.mkdir()
            child_code = (
                "import sys\n"
                "from research_os_mvp.errors import RunStateError\n"
                "from research_os_mvp.run_store import run_lock\n"
                f"path = {str(run_dir)!r}\n"
                "try:\n"
                "    with run_lock(path, timeout_seconds=0.2):\n"
                "        pass\n"
                "except RunStateError:\n"
                "    raise SystemExit(7)\n"
            )

            with run_lock(run_dir):
                result = subprocess.run(
                    [sys.executable, "-c", child_code],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )

            self.assertEqual(result.returncode, 7, result.stderr)


if __name__ == "__main__":
    unittest.main()
