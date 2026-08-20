from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_os_mvp.errors import IntegrityError
from research_os_mvp.integrity import (
    read_json,
    write_hash_manifest,
    write_json_atomic,
)
from research_os_mvp.runtime import create_run, verify_run
from tests.helpers import write_pack

TASK_1 = "TASK-MVP-01-capture-requirement"
TASK_2 = "TASK-MVP-02-capture-human-gate"


class RuntimeIntegrityTests(unittest.TestCase):
    def _create_run(self, root: Path) -> Path:
        pack = write_pack(root / "pack.json")
        run_id = "run-integrity-test"
        create_run(pack, root / "runs", run_id)
        return root / "runs" / run_id

    def _rewrite_state(self, run_dir: Path, updates: dict[str, object]) -> None:
        state = read_json(run_dir / "state.json")
        state.update(updates)
        write_json_atomic(run_dir / "state.json", state)
        write_hash_manifest(run_dir)

    def test_semantically_invalid_state_is_rejected_after_manifest_is_rebuilt(self) -> None:
        terminal_fields = {
            "cancelled_at": "2026-08-17T00:00:00Z",
            "cancelled_by": "Tester",
            "cancellation_reason": "test",
        }
        rejection_fields = {
            "rejected_at": "2026-08-17T00:00:00Z",
            "rejected_by": "Reviewer",
            "rejection_reason": "test",
            "rejection_review_hash": "1" * 64,
        }
        cases = (
            ("unknown-status", {"status": "unknown"}, "Unknown Run status"),
            ("task-list-type", {"executed_tasks": "bad"}, "task lists must be arrays"),
            ("next-index", {"next_task_index": 4}, "next_task_index is invalid"),
            ("executed-order", {"executed_tasks": [TASK_2]}, "executed_tasks is not"),
            ("approved-order", {"approved_tasks": [TASK_2]}, "approved_tasks is not"),
            (
                "impossible-relationship",
                {"approved_tasks": [TASK_1, TASK_2], "next_task_index": 2},
                "impossible executed/approved",
            ),
            ("next-mismatch", {"next_task_index": 1}, "does not match approved_tasks"),
            (
                "supplemental-count",
                {"supplemental_evidence_count": -1},
                "supplemental_evidence_count is invalid",
            ),
            ("paused-task", {"pending_task_id": TASK_2}, "does not identify"),
            ("paused-lists", {"executed_tasks": []}, "Paused Run Task lists"),
            ("running-pending", {"status": "running"}, "stale pending Task"),
            ("completed-pending", {"status": "completed"}, "still has a pending Task"),
            (
                "completed-incomplete",
                {"status": "completed", "pending_task_id": None, "pending_output": None},
                "missing executed or approved",
            ),
            ("cancelled-pending", {"status": "cancelled"}, "still has pending Task"),
            (
                "cancelled-running-lists",
                {
                    "status": "cancelled",
                    "pending_task_id": None,
                    "pending_output": None,
                    "cancelled_task_id": None,
                    **terminal_fields,
                },
                "Cancelled running Run has inconsistent",
            ),
            (
                "cancelled-task",
                {
                    "status": "cancelled",
                    "pending_task_id": None,
                    "pending_output": None,
                    "cancelled_task_id": TASK_2,
                    **terminal_fields,
                },
                "invalid current Task",
            ),
            (
                "cancelled-paused-lists",
                {
                    "status": "cancelled",
                    "pending_task_id": None,
                    "pending_output": None,
                    "executed_tasks": [],
                    "cancelled_task_id": TASK_1,
                    **terminal_fields,
                },
                "Cancelled paused Run has inconsistent",
            ),
            (
                "cancelled-metadata",
                {
                    "status": "cancelled",
                    "pending_task_id": None,
                    "pending_output": None,
                    "cancelled_task_id": TASK_1,
                    **terminal_fields,
                    "cancelled_by": "",
                },
                "missing cancelled_by",
            ),
            ("rejected-pending", {"status": "rejected"}, "still has pending Task"),
            (
                "rejected-task",
                {
                    "status": "rejected",
                    "pending_task_id": None,
                    "pending_output": None,
                    "rejected_task_id": TASK_2,
                    **rejection_fields,
                },
                "Rejected Run references an invalid",
            ),
            (
                "rejected-lists",
                {
                    "status": "rejected",
                    "pending_task_id": None,
                    "pending_output": None,
                    "executed_tasks": [],
                    "rejected_task_id": TASK_1,
                    **rejection_fields,
                },
                "Rejected Run has inconsistent",
            ),
            (
                "rejected-metadata",
                {
                    "status": "rejected",
                    "pending_task_id": None,
                    "pending_output": None,
                    "rejected_task_id": TASK_1,
                    **rejection_fields,
                    "rejection_reason": "",
                },
                "missing rejection_reason",
            ),
        )

        for name, updates, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = self._create_run(Path(temporary))
                self._rewrite_state(run_dir, updates)
                with self.assertRaisesRegex(IntegrityError, message):
                    verify_run(run_dir)

    def test_pack_identity_and_log_tail_mismatches_are_rejected(self) -> None:
        cases = (
            ("pack-hash", {"pack_sha256": "0" * 64}, "Pack snapshot hash"),
            ("pack-id", {"pack_id": "wrong-pack"}, "Pack snapshot ID"),
            ("mission-id", {"mission_id": "wrong-mission"}, "Mission ID"),
            ("event-tail", {"event_tail_hash": "0" * 64}, "Event log tail"),
            ("approval-tail", {"approval_tail_hash": "1" * 64}, "Approval log tail"),
            ("review-tail", {"review_tail_hash": "1" * 64}, "Reviewer decision log tail"),
            (
                "signature-tail",
                {"review_signature_tail_hash": "1" * 64},
                "Reviewer signature log tail",
            ),
        )

        for name, updates, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = self._create_run(Path(temporary))
                self._rewrite_state(run_dir, updates)
                with self.assertRaisesRegex(IntegrityError, message):
                    verify_run(run_dir)

    def test_evidence_metadata_corruption_is_rejected(self) -> None:
        cases = (
            ("non-object", "Evidence must be an object"),
            ("content-type", "content must be a string"),
            ("unknown-task", "unknown Task"),
            ("empty-id", "Evidence ID is invalid"),
            ("invalid-role", "Evidence role is invalid"),
            ("duplicate-id", "Evidence ID is duplicated"),
        )

        for name, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = self._create_run(Path(temporary))
                evidence_path = next((run_dir / "evidence").glob("*.json"))
                evidence = read_json(evidence_path)
                if name == "non-object":
                    write_json_atomic(evidence_path, [])
                elif name == "content-type":
                    evidence["content"] = 1
                    write_json_atomic(evidence_path, evidence)
                elif name == "unknown-task":
                    evidence["task_id"] = "TASK-UNKNOWN"
                    write_json_atomic(evidence_path, evidence)
                elif name == "empty-id":
                    evidence["evidence_id"] = ""
                    write_json_atomic(evidence_path, evidence)
                elif name == "invalid-role":
                    evidence["evidence_role"] = " "
                    write_json_atomic(evidence_path, evidence)
                elif name == "duplicate-id":
                    write_json_atomic(run_dir / "evidence" / "duplicate.json", evidence)
                write_hash_manifest(run_dir)

                with self.assertRaisesRegex(IntegrityError, message):
                    verify_run(run_dir)

    def test_task_report_corruption_and_unexpected_mission_report_are_rejected(self) -> None:
        cases = (
            ("non-object", "Task Report identity mismatch"),
            ("task-id", "Task Report identity mismatch"),
            ("output-type", "Task Report output is invalid"),
            ("reference-type", "Task Report output reference is invalid"),
            ("escape", "escapes the Run directory"),
            ("missing", "Task Report output is missing"),
            ("digest", "Task Report output hash mismatch"),
            ("mission-report", "Mission Report count"),
        )

        for name, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                run_dir = self._create_run(Path(temporary))
                report_path = run_dir / "reports" / "TASK-REPORT-01.json"
                report = read_json(report_path)
                if name == "non-object":
                    write_json_atomic(report_path, [])
                elif name == "task-id":
                    report["task_id"] = TASK_2
                    write_json_atomic(report_path, report)
                elif name == "output-type":
                    report["output"] = []
                    write_json_atomic(report_path, report)
                elif name == "reference-type":
                    report["output"]["path"] = 1
                    write_json_atomic(report_path, report)
                elif name == "escape":
                    report["output"]["path"] = "../outside.json"
                    write_json_atomic(report_path, report)
                elif name == "missing":
                    report["output"]["path"] = "evidence/missing.json"
                    write_json_atomic(report_path, report)
                elif name == "digest":
                    report["output"]["sha256"] = "0" * 64
                    write_json_atomic(report_path, report)
                elif name == "mission-report":
                    (run_dir / "reports" / "REPORT-MISSION-unexpected.md").write_text(
                        "unexpected",
                        encoding="utf-8",
                    )
                write_hash_manifest(run_dir)

                with self.assertRaisesRegex(IntegrityError, message):
                    verify_run(run_dir)

    def test_missing_run_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing-run"
            with self.assertRaisesRegex(IntegrityError, "Run directory is missing"):
                verify_run(missing)


if __name__ == "__main__":
    unittest.main()
