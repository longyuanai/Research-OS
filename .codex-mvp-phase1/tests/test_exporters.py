from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_os_mvp.exporters import ExportError, export_run_to_obsidian
from research_os_mvp.runtime import (
    approve_run,
    create_run,
    resume_run,
    review_run,
    revise_task_output,
)
from tests.helpers import EXAMPLE_PACK


class ObsidianExportTests(unittest.TestCase):
    def _completed_run(self, root: Path) -> Path:
        status = create_run(EXAMPLE_PACK, root / "runs", "run-export-test")
        run_dir = root / "runs" / status["run_id"]
        for index in range(3):
            approve_run(run_dir, approver="Human Owner", note=f"gate {index + 1}")
            resume_run(run_dir)
        return run_dir

    def test_verified_run_exports_as_immutable_obsidian_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = self._completed_run(root)
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)

            first = export_run_to_obsidian(run_dir, vault)
            second = export_run_to_obsidian(run_dir, vault)
            quoted = export_run_to_obsidian(run_dir, f'"{vault}"')

            export_dir = Path(first["export_dir"])
            self.assertEqual(first, second)
            self.assertEqual(first, quoted)
            self.assertTrue((export_dir / "INDEX.md").is_file())
            self.assertTrue((export_dir / "Effective Task Outputs.md").is_file())
            self.assertTrue((export_dir / "Effective Output Manifest.json").is_file())
            self.assertTrue((export_dir / "Mission Report.md").is_file())
            self.assertTrue((export_dir / "Original Mission Report.md").is_file())
            self.assertTrue((export_dir / "Reviewer Decisions.md").is_file())
            self.assertEqual(first["review_decisions"], 3)
            self.assertEqual(first["effective_outputs"], 3)
            manifest = (export_dir / "Effective Output Manifest.json").read_text(
                encoding="utf-8"
            )
            self.assertIn(first["effective_manifest_sha256"], manifest)
            self.assertEqual(len(list(export_dir.glob("EVID-*.md"))), 2)
            self.assertIn("不可变快照", (export_dir / "INDEX.md").read_text(encoding="utf-8"))
            decisions = (export_dir / "Reviewer Decisions.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Approved", decisions)
            self.assertIn("审查包 Hash", decisions)

            (export_dir / "INDEX.md").write_text("tampered\n", encoding="utf-8")
            with self.assertRaises(ExportError):
                export_run_to_obsidian(run_dir, vault)

    def test_non_obsidian_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir = self._completed_run(root)
            with self.assertRaises(ExportError):
                export_run_to_obsidian(run_dir, root)

    def test_task_output_revision_exports_with_reviewer_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-export-revision")
            run_dir = root / "runs" / status["run_id"]
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="revise output",
            )
            revised = revise_task_output(
                run_dir,
                content="revised task output",
                revised_by="Editor",
                note="revision complete",
                review_decision_hash=reviewed["latest_review_hash"],
            )
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)

            pending_export = export_run_to_obsidian(run_dir, vault)
            pending_effective = (
                Path(pending_export["export_dir"]) / "Effective Task Outputs.md"
            ).read_text(encoding="utf-8")
            self.assertNotIn("revised task output", pending_effective)
            self.assertEqual(pending_export["approved_revision_outputs"], 0)

            approved = approve_run(
                run_dir,
                approver="Reviewer",
                note="revised output accepted",
            )
            exported = export_run_to_obsidian(run_dir, vault)
            export_dir = Path(exported["export_dir"])
            index = (export_dir / "INDEX.md").read_text(encoding="utf-8")
            evidence_note = (export_dir / f"{revised['id']}.md").read_text(
                encoding="utf-8"
            )
            effective_outputs = (export_dir / "Effective Task Outputs.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Task 产物修订：1 版", index)
            self.assertIn("role: \"task_output_revision\"", evidence_note)
            self.assertIn(reviewed["latest_review_hash"], evidence_note)
            self.assertIn("revised task output", effective_outputs)
            self.assertIn(approved["latest_review_hash"], effective_outputs)
            self.assertEqual(exported["approved_revision_outputs"], 1)

    def test_task_three_approved_revision_is_default_exported_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-export-report-revision")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Reviewer", note="task one")
            resume_run(run_dir)
            approve_run(run_dir, approver="Reviewer", note="task two")
            resume_run(run_dir)
            reviewed = review_run(
                run_dir,
                reviewer="Report Reviewer",
                decision="Changes Requested",
                note="replace final report",
            )
            revise_task_output(
                run_dir,
                content="# Approved Final Report\n\nReviewed export conclusion.",
                revised_by="Editor",
                note="final report revised",
                review_decision_hash=reviewed["latest_review_hash"],
            )
            approve_run(
                run_dir,
                approver="Report Reviewer",
                note="report accepted",
            )
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)

            exported = export_run_to_obsidian(run_dir, vault)
            export_dir = Path(exported["export_dir"])
            effective_report = (export_dir / "Mission Report.md").read_text(
                encoding="utf-8"
            )
            original_report = (export_dir / "Original Mission Report.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Reviewed export conclusion", effective_report)
            self.assertIn("Effective Output Manifest", effective_report)
            self.assertNotIn("Reviewed export conclusion", original_report)


if __name__ == "__main__":
    unittest.main()
