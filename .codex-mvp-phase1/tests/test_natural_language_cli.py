from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.cli import main


class NaturalLanguageCLITests(unittest.TestCase):
    def _run_json(self, arguments: list[str]) -> tuple[int, dict]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(arguments)
        return exit_code, json.loads(output.getvalue())

    def test_categories_command_lists_eight_profiles(self) -> None:
        exit_code, result = self._run_json(["categories"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(result["categories"]), 8)

    def test_create_command_writes_a_valid_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            exit_code, result = self._run_json(
                [
                    "create",
                    "硬件选型：比较 ESP32 和 STM32 主控",
                    "--workspace",
                    temporary,
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(result["result"], "CREATED")
            self.assertEqual(result["category"], "hardware-selection")
            self.assertTrue(Path(result["path"]).is_file())

    def test_quickstart_creates_pack_and_pauses_at_task_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            exit_code, result = self._run_json(
                [
                    "quickstart",
                    "技术选型：比较 Python、TypeScript 和 Rust",
                    "--workspace",
                    temporary,
                    "--run-id",
                    "run-natural-cli",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(result["result"], "PAUSED_AT_HUMAN_GATE")
            self.assertEqual(result["status"], "paused")
            self.assertEqual(result["category"], "technology-selection")
            self.assertEqual(result["evidence_count"], 1)
            run_dir = Path(temporary) / "runs" / "run-natural-cli"
            self.assertTrue((run_dir / "HASHES.json").is_file())


if __name__ == "__main__":
    unittest.main()
