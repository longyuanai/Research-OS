from __future__ import annotations

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research_os_mvp.errors import IntegrityError, RunStateError
from research_os_mvp.integrity import (
    append_chained_record,
    read_json,
    sha256_file,
    verify_chained_log,
    write_hash_manifest,
    write_json_atomic,
)
from research_os_mvp.runtime import (
    approve_run,
    cancel_run,
    create_run,
    record_supplemental_evidence,
    resume_run,
    review_run,
    revise_task_output,
    verify_run,
)
from tests.helpers import write_pack


class RuntimeFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pack = write_pack(self.root / "pack.json")
        self.runs = self.root / "runs"
        self.run_id = "run-test-flow"
        self.run_dir = self.runs / self.run_id

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _approve_and_resume(self, number: int) -> dict:
        approved = approve_run(
            self.run_dir,
            approver="Human Tester",
            note=f"Task {number} verified",
        )
        self.assertEqual(approved["status"], "approved_pending_resume")
        return resume_run(self.run_dir)

    def test_three_task_mission_pauses_approves_resumes_and_completes(self) -> None:
        first = create_run(self.pack, self.runs, self.run_id)
        self.assertEqual(first["status"], "paused")
        self.assertEqual(first["pending_task_id"], "TASK-MVP-01-capture-requirement")
        self.assertEqual(first["evidence_count"], 1)

        second = self._approve_and_resume(1)
        self.assertEqual(second["status"], "paused")
        self.assertEqual(second["pending_task_id"], "TASK-MVP-02-capture-human-gate")
        self.assertEqual(second["evidence_count"], 2)

        third = self._approve_and_resume(2)
        self.assertEqual(third["status"], "paused")
        self.assertEqual(third["pending_task_id"], "TASK-MVP-03-compose-report")
        self.assertEqual(third["report_count"], 4)

        completed = self._approve_and_resume(3)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["approved_tasks"], completed["executed_tasks"])
        self.assertEqual(completed["approval_count"], 3)
        self.assertEqual(completed["review_count"], 3)
        self.assertEqual(completed["evidence_count"], 2)
        self.assertEqual(completed["integrity"], "verified")

        event_count, _ = verify_chained_log(self.run_dir / "events.jsonl")
        self.assertEqual(event_count, completed["event_count"])
        reports = list((self.run_dir / "reports").glob("REPORT-MISSION-*.md"))
        self.assertEqual(len(reports), 1)
        report_text = reports[0].read_text(encoding="utf-8")
        self.assertIn("## Research Readiness", report_text)
        self.assertIn("不是候选方案比较结论", report_text)

    def test_supplemental_evidence_is_hashed_and_revision_is_linked(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        approve_run(self.run_dir, approver="Human Tester")
        resume_run(self.run_dir)
        first = record_supplemental_evidence(
            self.run_dir,
            content="AI 初稿：参数未知，等待核验。",
            source="ollama://qwen2.5:7b",
            method="本地 AI 初稿",
            limitations="没有实时联网，全部事实待核验。",
            collected_by="Ollama (qwen2.5:7b)",
            evidence_role="ai_draft",
        )
        second = record_supplemental_evidence(
            self.run_dir,
            content="AI 修订稿：明确标出未知参数。",
            source="ollama://qwen2.5:7b",
            method="根据人工意见返工",
            limitations="没有实时联网，全部事实待核验。",
            collected_by="Ollama (qwen2.5:7b)",
            evidence_role="ai_draft",
            revision_of=first["id"],
        )
        status = verify_run(self.run_dir)
        self.assertEqual(status["supplemental_evidence_count"], 2)
        self.assertEqual(status["evidence_count"], 4)
        evidence = json.loads(
            (self.run_dir / second["path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["revision_of"], first["id"])

    def test_changes_requested_is_idempotent_and_rework_links_to_decision(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        approve_run(self.run_dir, approver="Human Tester")
        resume_run(self.run_dir)
        first = record_supplemental_evidence(
            self.run_dir,
            content="AI 初稿：参数待核验。",
            source="ollama://qwen2.5:7b",
            method="本地 AI 初稿",
            limitations="全部事实待核验。",
            collected_by="Ollama",
            evidence_role="ai_draft",
        )

        reviewed = review_run(
            self.run_dir,
            reviewer="Human Reviewer",
            decision="Changes Requested",
            note="请标出所有未知参数",
        )
        review_hash_before = sha256_file(self.run_dir / "reviews.jsonl")
        event_hash_before = sha256_file(self.run_dir / "events.jsonl")
        repeated = review_run(
            self.run_dir,
            reviewer="Human Reviewer",
            decision="changes-requested",
            note="请标出所有未知参数",
        )
        self.assertEqual(repeated["review_count"], reviewed["review_count"])
        self.assertEqual(sha256_file(self.run_dir / "reviews.jsonl"), review_hash_before)
        self.assertEqual(sha256_file(self.run_dir / "events.jsonl"), event_hash_before)

        revision = record_supplemental_evidence(
            self.run_dir,
            content="AI 修订稿：未知参数已标注。",
            source="ollama://qwen2.5:7b",
            method="根据 Reviewer 意见返工",
            limitations="全部事实待核验。",
            collected_by="Ollama",
            evidence_role="ai_draft",
            revision_of=first["id"],
            review_decision_hash=reviewed["latest_review_hash"],
        )
        evidence = read_json(self.run_dir / revision["path"])
        self.assertEqual(
            evidence["review_decision_hash"],
            reviewed["latest_review_hash"],
        )

        approved = approve_run(
            self.run_dir,
            approver="Human Reviewer",
            note="修订稿已复核",
        )
        self.assertEqual(approved["status"], "approved_pending_resume")
        self.assertEqual(approved["review_count"], 3)
        self.assertEqual(approved["latest_review_decision"], "Approved")

    def test_rejected_is_distinct_terminal_and_idempotent(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        rejected = review_run(
            self.run_dir,
            reviewer="Human Reviewer",
            decision="Rejected",
            note="输出不符合任务目标",
        )
        self.assertEqual(rejected["status"], "rejected")
        self.assertEqual(rejected["review_count"], 1)
        self.assertEqual(rejected["approval_count"], 0)
        self.assertEqual(rejected["rejected_task_id"], rejected["executed_tasks"][-1])
        hashes_before = sha256_file(self.run_dir / "HASHES.json")

        repeated = review_run(
            self.run_dir,
            reviewer="Human Reviewer",
            decision="rejected",
            note="输出不符合任务目标",
        )
        self.assertEqual(repeated, rejected)
        self.assertEqual(sha256_file(self.run_dir / "HASHES.json"), hashes_before)
        with self.assertRaisesRegex(RunStateError, "cannot resume"):
            resume_run(self.run_dir)
        with self.assertRaisesRegex(RunStateError, "cannot be cancelled"):
            cancel_run(
                self.run_dir,
                cancelled_by="Human Tester",
                reason="不应覆盖 Reviewer 驳回",
            )

    def test_task_one_output_revision_is_audited_and_idempotent(self) -> None:
        created = create_run(self.pack, self.runs, self.run_id)
        state = read_json(self.run_dir / "state.json")
        reviewed = review_run(
            self.run_dir,
            reviewer="Human Reviewer",
            decision="Changes Requested",
            note="请补充明确的验收边界",
        )
        revised = revise_task_output(
            self.run_dir,
            content="修订后目标：完成 CLI 功能并通过双版本测试。",
            revised_by="Human Editor",
            note="补充验收边界",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        self.assertEqual(revised["role"], "task_output_revision")
        self.assertEqual(revised["revision_of"], state["pending_output"]["id"])
        self.assertEqual(revised["task_output_revision_count"], 1)
        revision = read_json(self.run_dir / revised["path"])
        self.assertEqual(
            revision["review_decision_hash"],
            reviewed["latest_review_hash"],
        )
        event_hash_before = sha256_file(self.run_dir / "events.jsonl")
        repeated = revise_task_output(
            self.run_dir,
            content="修订后目标：完成 CLI 功能并通过双版本测试。",
            revised_by="Human Editor",
            note="补充验收边界",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        self.assertEqual(repeated["id"], revised["id"])
        self.assertEqual(sha256_file(self.run_dir / "events.jsonl"), event_hash_before)

        approved = approve_run(
            self.run_dir,
            approver="Human Reviewer",
            note="修订版已复核",
        )
        self.assertEqual(approved["review_count"], created["review_count"] + 2)
        decisions = (self.run_dir / "reviews.jsonl").read_text(encoding="utf-8")
        self.assertIn(revised["id"], decisions)

    def test_task_three_report_revision_can_complete_after_re_review(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        self._approve_and_resume(1)
        self._approve_and_resume(2)
        state = read_json(self.run_dir / "state.json")
        self.assertEqual(state["pending_output"]["class"], "Report")
        reviewed = review_run(
            self.run_dir,
            reviewer="Report Reviewer",
            decision="Changes Requested",
            note="请补充风险与验证顺序",
        )
        revised = revise_task_output(
            self.run_dir,
            content="# 修订报告\n\n先验证失败路径，再执行功能验收。",
            revised_by="Report Editor",
            note="补充风险顺序",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        self.assertEqual(revised["revision_of"], state["pending_output"]["id"])
        approve_run(
            self.run_dir,
            approver="Report Reviewer",
            note="修订报告已复核",
        )
        completed = resume_run(self.run_dir)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["task_output_revision_count"], 1)
        self.assertEqual(completed["evidence_count"], 3)

    def test_task_output_revision_requires_current_changes_requested(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        with self.assertRaisesRegex(RunStateError, "latest Changes Requested"):
            revise_task_output(
                self.run_dir,
                content="revision",
                revised_by="Editor",
                note="change",
                review_decision_hash="0" * 64,
            )
        reviewed = review_run(
            self.run_dir,
            reviewer="Reviewer",
            decision="Changes Requested",
            note="change",
        )
        with self.assertRaisesRegex(RunStateError, "latest Changes Requested"):
            revise_task_output(
                self.run_dir,
                content="revision",
                revised_by="Editor",
                note="change",
                review_decision_hash="1" * 64,
            )
        with self.assertRaisesRegex(RunStateError, "revision content"):
            revise_task_output(
                self.run_dir,
                content=" ",
                revised_by="Editor",
                note="change",
                review_decision_hash=reviewed["latest_review_hash"],
            )

    def test_concurrent_identical_task_revisions_create_one_evidence(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        reviewed = review_run(
            self.run_dir,
            reviewer="Reviewer",
            decision="Changes Requested",
            note="same change",
        )

        def revise() -> dict:
            return revise_task_output(
                self.run_dir,
                content="same revised output",
                revised_by="Concurrent Editor",
                note="same change",
                review_decision_hash=reviewed["latest_review_hash"],
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _index: revise(), range(2)))
        self.assertEqual(results[0]["id"], results[1]["id"])
        self.assertEqual(verify_run(self.run_dir)["task_output_revision_count"], 1)

    def test_tampered_task_output_revision_chain_is_detected(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        reviewed = review_run(
            self.run_dir,
            reviewer="Reviewer",
            decision="Changes Requested",
            note="two revisions",
        )
        first = revise_task_output(
            self.run_dir,
            content="revision one",
            revised_by="Editor",
            note="first",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        second = revise_task_output(
            self.run_dir,
            content="revision two",
            revised_by="Editor",
            note="second",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        evidence = read_json(self.run_dir / second["path"])
        evidence["revision_of"] = first["revision_of"]
        write_json_atomic(self.run_dir / second["path"], evidence)
        write_hash_manifest(self.run_dir)
        with self.assertRaisesRegex(IntegrityError, "revision chain is broken"):
            verify_run(self.run_dir)

    def test_review_notes_and_transitions_are_validated(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        for decision in ("Changes Requested", "Rejected"):
            with self.subTest(decision=decision), self.assertRaisesRegex(
                RunStateError,
                "require a non-empty note",
            ):
                review_run(
                    self.run_dir,
                    reviewer="Human Reviewer",
                    decision=decision,
                )
        with self.assertRaisesRegex(RunStateError, "must be Approved"):
            review_run(
                self.run_dir,
                reviewer="Human Reviewer",
                decision="Maybe",
                note="unclear",
            )

    def test_concurrent_identical_changes_requested_creates_one_decision(self) -> None:
        create_run(self.pack, self.runs, self.run_id)

        def record() -> dict:
            return review_run(
                self.run_dir,
                reviewer="Concurrent Reviewer",
                decision="Changes Requested",
                note="统一返工意见",
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _index: record(), range(2)))
        self.assertEqual([result["review_count"] for result in results], [1, 1])
        self.assertEqual(verify_run(self.run_dir)["review_count"], 1)

    def test_legacy_state_without_review_tail_remains_verifiable(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        state = read_json(self.run_dir / "state.json")
        state.pop("review_tail_hash")
        write_json_atomic(self.run_dir / "state.json", state)
        write_hash_manifest(self.run_dir)

        verified = verify_run(self.run_dir)
        self.assertEqual(verified["review_count"], 0)
        self.assertEqual(verified["status"], "paused")

    def test_semantically_invalid_review_is_detected_after_manifest_rebuilt(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        state = read_json(self.run_dir / "state.json")
        forged = append_chained_record(
            self.run_dir / "reviews.jsonl",
            {
                "at": "2026-08-09T00:00:00Z",
                "review_id": f"REVIEW-{self.run_id}-001",
                "reviewer": "Forged Reviewer",
                "decision": "Approved",
                "task_id": state["pending_task_id"],
                "note": "",
                "subject": {"schema_version": "forged"},
            },
        )
        state["review_tail_hash"] = forged["hash"]
        write_json_atomic(self.run_dir / "state.json", state)
        write_hash_manifest(self.run_dir)

        with self.assertRaisesRegex(IntegrityError, "subject schema"):
            verify_run(self.run_dir)

    def test_supplemental_evidence_is_rejected_at_task_one(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        with self.assertRaisesRegex(RunStateError, "第 2 步"):
            record_supplemental_evidence(
                self.run_dir,
                content="draft",
                source="ollama://qwen2.5:7b",
                method="local",
                limitations="unverified",
                collected_by="Ollama",
                evidence_role="ai_draft",
            )
    def test_resume_requires_approval(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        with self.assertRaisesRegex(RunStateError, "requires explicit human approval"):
            resume_run(self.run_dir)

    def test_approval_cannot_be_recorded_twice_for_same_gate(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        approve_run(self.run_dir, approver="Human Tester")
        with self.assertRaisesRegex(RunStateError, "must be paused"):
            approve_run(self.run_dir, approver="Human Tester")

    def test_completed_resume_is_idempotent(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        self._approve_and_resume(1)
        self._approve_and_resume(2)
        completed = self._approve_and_resume(3)
        event_hash_before = sha256_file(self.run_dir / "events.jsonl")
        hashes_hash_before = sha256_file(self.run_dir / "HASHES.json")

        repeated = resume_run(self.run_dir)
        self.assertEqual(repeated, completed)
        self.assertEqual(sha256_file(self.run_dir / "events.jsonl"), event_hash_before)
        self.assertEqual(sha256_file(self.run_dir / "HASHES.json"), hashes_hash_before)

    def test_paused_run_can_be_cancelled_and_cancel_is_idempotent(self) -> None:
        before = create_run(self.pack, self.runs, self.run_id)
        cancelled = cancel_run(
            self.run_dir,
            cancelled_by="Human Tester",
            reason="Requirements changed",
        )
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(cancelled["pending_task_id"], None)
        self.assertEqual(
            cancelled["cancelled_task_id"],
            "TASK-MVP-01-capture-requirement",
        )
        self.assertEqual(cancelled["cancelled_by"], "Human Tester")
        self.assertEqual(cancelled["cancellation_reason"], "Requirements changed")
        self.assertEqual(cancelled["event_count"], before["event_count"] + 1)

        event_hash_before = sha256_file(self.run_dir / "events.jsonl")
        hashes_hash_before = sha256_file(self.run_dir / "HASHES.json")
        repeated = cancel_run(
            self.run_dir,
            cancelled_by="Different Caller",
            reason="This input is ignored after terminal cancellation",
        )
        self.assertEqual(repeated, cancelled)
        self.assertEqual(sha256_file(self.run_dir / "events.jsonl"), event_hash_before)
        self.assertEqual(sha256_file(self.run_dir / "HASHES.json"), hashes_hash_before)

    def test_approved_pending_resume_run_can_be_cancelled(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        approve_run(self.run_dir, approver="Human Tester")
        cancelled = cancel_run(
            self.run_dir,
            cancelled_by="Human Tester",
            reason="Approval withdrawn before resume",
        )
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(cancelled["approval_count"], 1)
        self.assertEqual(cancelled["approved_tasks"], [])
        self.assertEqual(
            cancelled["executed_tasks"],
            ["TASK-MVP-01-capture-requirement"],
        )
        with self.assertRaisesRegex(RunStateError, "cannot resume"):
            resume_run(self.run_dir)

    def test_completed_run_cannot_be_cancelled(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        self._approve_and_resume(1)
        self._approve_and_resume(2)
        self._approve_and_resume(3)
        with self.assertRaisesRegex(RunStateError, "cannot be cancelled"):
            cancel_run(
                self.run_dir,
                cancelled_by="Human Tester",
                reason="Too late",
            )

    def test_tampered_evidence_is_detected(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        evidence_path = next((self.run_dir / "evidence").glob("*.json"))
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["content"] = "tampered"
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        with self.assertRaisesRegex(IntegrityError, "mismatch"):
            verify_run(self.run_dir)

    def test_pack_snapshot_tampering_is_detected(self) -> None:
        create_run(self.pack, self.runs, self.run_id)
        snapshot = self.run_dir / "pack.snapshot.json"
        snapshot.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(IntegrityError):
            verify_run(self.run_dir)


if __name__ == "__main__":
    unittest.main()
