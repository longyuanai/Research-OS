from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.git_integration import (
    GitIntegrationError,
    collect_git_snapshot,
    detect_test_command,
    record_git_snapshot_evidence,
)
from research_os_mvp.runtime import approve_run, create_run, resume_run, verify_run
from tests.helpers import EXAMPLE_PACK


class GitIntegrationTests(unittest.TestCase):
    def _git_repo(self, root: Path) -> Path:
        repo = root / "sample-repo"
        (repo / "tests").mkdir(parents=True)
        (repo / "README.md").write_text("sample\n", encoding="utf-8")
        (repo / "tests" / "test_sample.py").write_text(
            "import unittest\n\n"
            "class SampleTest(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "init", str(repo)],
            check=True,
            capture_output=True,
            text=True,
        )
        return repo

    def _task_two_run(self, root: Path) -> Path:
        status = create_run(EXAMPLE_PACK, root / "runs", "run-git-test")
        run_dir = root / "runs" / status["run_id"]
        approve_run(run_dir, approver="Human Owner", note="Task 1 checked")
        resume_run(run_dir)
        return run_dir

    def test_snapshot_can_run_detected_tests_and_become_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = self._git_repo(root)
            snapshot = collect_git_snapshot(repo, run_tests=True)
            self.assertEqual(snapshot.test_status, "PASS")
            self.assertEqual(
                snapshot.test_command,
                (sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"),
            )
            self.assertIn("HEAD：UNBORN", snapshot.content)

            run_dir = self._task_two_run(root)
            recorded = record_git_snapshot_evidence(run_dir, repo, run_tests=False)
            self.assertEqual(recorded["test_status"], "NOT_RUN")
            self.assertEqual(recorded["role"], "git_project_snapshot")
            self.assertEqual(verify_run(run_dir)["evidence_count"], 3)

    def test_non_git_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(
            GitIntegrationError
        ):
            collect_git_snapshot(temporary, run_tests=False)

    def test_node_tests_directory_does_not_trigger_python_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "tests").mkdir()
            (repo / "tests" / "sample.test.js").write_text(
                "console.log('ok');\n",
                encoding="utf-8",
            )
            (repo / "package.json").write_text(
                '{"scripts":{"test":"node --test"}}\n',
                encoding="utf-8",
            )
            self.assertEqual(detect_test_command(repo), ("npm", "test"))


if __name__ == "__main__":
    unittest.main()
