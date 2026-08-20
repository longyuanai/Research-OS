from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_os_mvp.handoff import (
    render_effective_mission_report,
    render_research_handoff,
    save_research_handoff,
)
from research_os_mvp.runtime import (
    approve_run,
    create_run,
    resume_run,
    review_run,
    revise_task_output,
)
from tests.helpers import EXAMPLE_PACK


class EffectiveHandoffTests(unittest.TestCase):
    def test_handoff_switches_only_after_revision_is_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-handoff-effective")
            run_dir = root / "runs" / status["run_id"]
            original = render_research_handoff(run_dir)
            original_path = save_research_handoff(run_dir, root)
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="clarify the goal",
            )
            revised = revise_task_output(
                run_dir,
                content="reviewed and accepted research goal",
                revised_by="Editor",
                note="goal clarified",
                review_decision_hash=reviewed["latest_review_hash"],
            )

            pending = render_research_handoff(run_dir)
            self.assertNotEqual(pending, original)
            self.assertNotIn("reviewed and accepted research goal", pending)

            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            effective = render_research_handoff(run_dir)
            effective_path = save_research_handoff(run_dir, root)
            self.assertIn("reviewed and accepted research goal", effective)
            self.assertIn(revised["id"], effective)
            self.assertIn(approved["latest_review_hash"], effective)
            self.assertNotEqual(original_path, effective_path)
            self.assertTrue(original_path.is_file())
            self.assertTrue(effective_path.is_file())

    def test_mission_report_view_uses_approved_task_three_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-report-effective")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Reviewer", note="task one")
            resume_run(run_dir)
            approve_run(run_dir, approver="Reviewer", note="task two")
            resume_run(run_dir)
            original = render_effective_mission_report(run_dir)
            reviewed = review_run(
                run_dir,
                reviewer="Report Reviewer",
                decision="Changes Requested",
                note="rewrite conclusion",
            )
            revised = revise_task_output(
                run_dir,
                content="# Reviewed Mission Report\n\nFinal reviewed conclusion.",
                revised_by="Editor",
                note="report revised",
                review_decision_hash=reviewed["latest_review_hash"],
            )

            pending = render_effective_mission_report(run_dir)
            self.assertNotEqual(pending, original)
            self.assertNotIn("Final reviewed conclusion", pending)

            approved = approve_run(
                run_dir,
                approver="Report Reviewer",
                note="final report accepted",
            )
            effective = render_effective_mission_report(run_dir)
            self.assertIn("Final reviewed conclusion", effective)
            self.assertIn(revised["id"], effective)
            self.assertIn(approved["latest_review_hash"], effective)


if __name__ == "__main__":
    unittest.main()
