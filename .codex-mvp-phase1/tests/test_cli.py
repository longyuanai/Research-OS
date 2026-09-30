from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from research_os_mvp.ai import AISettings, load_ai_settings
from research_os_mvp.cli import main
from research_os_mvp.runtime import (
    EFFECTIVE_OUTPUT_MANIFEST_SCHEMA,
    approve_run,
    create_run,
    resume_run,
)
from tests.helpers import EXAMPLE_PACK, write_pack


class CLITests(unittest.TestCase):
    @patch("research_os_mvp.cli.check_ollama")
    def test_configure_ollama_accepts_and_reports_health_timeout(
        self,
        check_mock: Mock,
    ) -> None:
        def fake_check(settings: AISettings) -> dict[str, object]:
            return {
                "provider": settings.provider,
                "health_timeout_seconds": settings.health_timeout_seconds,
                "health_check_elapsed_seconds": 0.25,
                "timeout_seconds": settings.timeout_seconds,
            }

        check_mock.side_effect = fake_check
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "configure-ollama",
                        "--workspace",
                        temporary,
                        "--model",
                        "qwen2.5:7b",
                        "--health-timeout-seconds",
                        "88",
                    ]
                )
            self.assertEqual(exit_code, 0)
            settings = load_ai_settings(temporary)
            assert settings is not None
            self.assertEqual(settings.health_timeout_seconds, 88)
            result = json.loads(output.getvalue())
            self.assertEqual(result["health_timeout_seconds"], 88)
            self.assertEqual(result["timeout_seconds"], 300)

    @patch("research_os_mvp.cli.check_ollama")
    def test_configure_ollama_reports_stream_limits_and_model_guidance(
        self,
        check_mock: Mock,
    ) -> None:
        def fake_check(settings: AISettings) -> dict[str, object]:
            return {
                "provider": settings.provider,
                "stream_idle_timeout_seconds": settings.stream_idle_timeout_seconds,
                "generation_budget_seconds": settings.generation_budget_seconds,
            }

        check_mock.side_effect = fake_check
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "configure-ollama",
                        "--workspace",
                        temporary,
                        "--model",
                        "qwen2.5:7b",
                        "--stream-idle-timeout-seconds",
                        "44",
                        "--generation-budget-seconds",
                        "1200",
                    ]
                )
            self.assertEqual(exit_code, 0)
            settings = load_ai_settings(temporary)
            assert settings is not None
            self.assertEqual(settings.stream_idle_timeout_seconds, 44)
            self.assertEqual(settings.generation_budget_seconds, 1200)
            result = json.loads(output.getvalue())
            self.assertEqual(result["stream_idle_timeout_seconds"], 44)
            self.assertEqual(result["generation_budget_seconds"], 1200)
            self.assertIn("数分钟", result["model_guidance"])
            self.assertIn("更小模型", result["model_guidance"])

    def test_effective_outputs_command_returns_stable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-effective")
            run_dir = root / "runs" / status["run_id"]
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main(["effective-outputs", str(run_dir)])

            self.assertEqual(exit_code, 0)
            manifest = json.loads(output.getvalue())
            self.assertEqual(manifest["schema_version"], EFFECTIVE_OUTPUT_MANIFEST_SCHEMA)
            self.assertEqual(manifest["run_id"], "run-cli-effective")
            self.assertEqual(manifest["outputs"][0]["source"], "original")
            manifest_path = root / "effective-output-manifest.json"
            manifest_path.write_text(output.getvalue(), encoding="utf-8")
            verified_output = io.StringIO()
            with contextlib.redirect_stdout(verified_output):
                verify_exit = main(
                    ["verify-effective-manifest", str(manifest_path)]
                )
            self.assertEqual(verify_exit, 0)
            verified = json.loads(verified_output.getvalue())
            self.assertEqual(verified["integrity"], "verified")
            self.assertEqual(verified["manifest_sha256"], manifest["manifest_sha256"])

    def test_review_command_records_changes_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-review")
            run_dir = root / "runs" / status["run_id"]
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "review",
                        str(run_dir),
                        "--by",
                        "CLI Reviewer",
                        "--decision",
                        "changes-requested",
                        "--note",
                        "请补充可验收标准",
                    ]
                )

            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["status"], "paused")
            self.assertEqual(result["review_count"], 1)
            self.assertEqual(result["latest_review_decision"], "Changes Requested")

    def test_revise_command_records_task_output_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-revise")
            run_dir = root / "runs" / status["run_id"]
            review_output = io.StringIO()
            with contextlib.redirect_stdout(review_output):
                self.assertEqual(
                    main(
                        [
                            "review",
                            str(run_dir),
                            "--by",
                            "CLI Reviewer",
                            "--decision",
                            "changes-requested",
                            "--note",
                            "补充验收边界",
                        ]
                    ),
                    0,
                )
            review = json.loads(review_output.getvalue())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "revise",
                        str(run_dir),
                        "--by",
                        "CLI Editor",
                        "--review-hash",
                        review["latest_review_hash"],
                        "--note",
                        "已补充验收边界",
                        "--content",
                        "修订后的完整 Task 产物",
                    ]
                )

            self.assertEqual(exit_code, 0)
            revised = json.loads(output.getvalue())
            self.assertEqual(revised["role"], "task_output_revision")
            self.assertEqual(revised["task_output_revision_count"], 1)

    def test_cancel_command_records_audited_terminal_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-cancel")
            run_dir = root / "runs" / status["run_id"]
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main(
                    [
                        "cancel",
                        str(run_dir),
                        "--by",
                        "Human Owner",
                        "--reason",
                        "Scope changed",
                    ]
                )

            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["status"], "cancelled")
            self.assertEqual(result["cancelled_by"], "Human Owner")
            self.assertEqual(result["cancellation_reason"], "Scope changed")

    def test_checkpoint_status_command_returns_verified_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-checkpoint")
            run_dir = root / "runs" / status["run_id"]
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main(["checkpoint-status", str(run_dir)])

            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["run_id"], "run-cli-checkpoint")
            self.assertEqual(result["status"], "paused")
            self.assertEqual(result["canonical_alignment"], "matches")

            (run_dir / "state.json").write_text("{}\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["checkpoint-status", str(run_dir)])
            self.assertEqual(exit_code, 0)
            stale = json.loads(output.getvalue())
            self.assertEqual(stale["status"], "paused")
            self.assertEqual(stale["canonical_alignment"], "differs")

    def test_validate_command_returns_machine_readable_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = write_pack(Path(temporary) / "pack.json")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["validate", str(pack)])
            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["result"], "VALID")
            self.assertEqual(result["task_count"], 3)

    def test_validate_command_returns_error_code_for_invalid_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack.json"
            pack.write_text("{}\n", encoding="utf-8")
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                exit_code = main(["validate", str(pack)])
            self.assertEqual(exit_code, 2)
            self.assertIn("ERROR:", error.getvalue())

    def test_export_obsidian_command_returns_snapshot_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-export")
            run_dir = root / "runs" / status["run_id"]
            for index in range(3):
                approve_run(run_dir, approver="Human Owner", note=f"gate {index + 1}")
                resume_run(run_dir)
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["export-obsidian", str(run_dir), str(vault)])

            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["run_id"], "run-cli-export")
            self.assertTrue(Path(result["export_dir"]).is_dir())

    def test_git_snapshot_command_records_task_two_evidence_without_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            (repo / "README.md").write_text("sample\n", encoding="utf-8")
            subprocess.run(
                ["git", "init", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-git")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Human Owner", note="Task 1 checked")
            resume_run(run_dir)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["git-snapshot", str(run_dir), str(repo)])

            self.assertEqual(exit_code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["role"], "git_project_snapshot")
            self.assertEqual(result["test_status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
