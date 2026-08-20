from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from threading import Event
from unittest.mock import patch

import research_os_mvp.runtime as runtime_module
from research_os_mvp.errors import IntegrityError
from research_os_mvp.integrity import canonical_json_text, sha256_text
from research_os_mvp.runtime import (
    approve_run,
    build_effective_output_manifest,
    create_run,
    read_effective_run_snapshot,
    record_supplemental_evidence,
    resolve_effective_task_outputs,
    resume_run,
    review_run,
    revise_task_output,
    verify_effective_output_manifest,
)
from research_os_mvp.wizard import render_run_artifacts
from tests.helpers import EXAMPLE_PACK


class EffectiveOutputTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_self_identifying(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-manifest-stable")
            run_dir = root / "runs" / status["run_id"]

            first = build_effective_output_manifest(run_dir)
            second = build_effective_output_manifest(run_dir)
            unsigned = {
                key: value for key, value in first.items() if key != "manifest_sha256"
            }
            self.assertEqual(first, second)
            self.assertEqual(
                first["manifest_sha256"],
                sha256_text(canonical_json_text(unsigned)),
            )
            self.assertEqual(first["output_count"], 1)
            self.assertEqual(first["approved_revision_count"], 0)
            self.assertEqual(first["outputs"][0]["source"], "original")
            verified = verify_effective_output_manifest(first)
            self.assertEqual(verified["integrity"], "verified")

            tampered = {**first, "run_status": "tampered"}
            with self.assertRaisesRegex(IntegrityError, "hash does not match"):
                verify_effective_output_manifest(tampered)

    def test_snapshot_holds_one_lock_against_concurrent_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-snapshot-lock")
            run_dir = root / "runs" / status["run_id"]
            entered = Event()
            release = Event()
            original_reader = runtime_module._read_snapshot_text

            def blocking_reader(path: Path) -> str:
                if path.name == "TASK-REPORT-01.json" and not entered.is_set():
                    entered.set()
                    if not release.wait(timeout=5):
                        raise AssertionError("snapshot test release timed out")
                return original_reader(path)

            with patch.object(
                runtime_module,
                "_read_snapshot_text",
                side_effect=blocking_reader,
            ), ThreadPoolExecutor(max_workers=2) as executor:
                reader = executor.submit(read_effective_run_snapshot, run_dir)
                self.assertTrue(entered.wait(timeout=3))
                writer = executor.submit(
                    review_run,
                    run_dir,
                    reviewer="Concurrent Reviewer",
                    decision="Changes Requested",
                    note="must wait for snapshot",
                )
                try:
                    with self.assertRaises(TimeoutError):
                        writer.result(timeout=0.2)
                finally:
                    release.set()
                snapshot = reader.result(timeout=3)
                changed = writer.result(timeout=3)

            self.assertEqual(snapshot["reviews"], [])
            self.assertEqual(
                snapshot["effective_output_manifest"]["outputs"][0]["source"],
                "original",
            )
            self.assertEqual(changed["review_count"], 1)

    def test_pending_revision_is_not_effective_until_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-effective-pending")
            run_dir = root / "runs" / status["run_id"]
            original = resolve_effective_task_outputs(run_dir)[0]
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="revise goal",
            )
            revised = revise_task_output(
                run_dir,
                content="approved goal revision",
                revised_by="Editor",
                note="goal revised",
                review_decision_hash=reviewed["latest_review_hash"],
            )

            pending = resolve_effective_task_outputs(run_dir)[0]
            self.assertEqual(pending["source"], "original")
            self.assertEqual(pending["effective_id"], original["effective_id"])
            self.assertNotEqual(pending["effective_id"], revised["id"])

            approved = approve_run(
                run_dir,
                approver="Reviewer",
                note="revision accepted",
            )
            effective = resolve_effective_task_outputs(run_dir)[0]
            self.assertEqual(effective["source"], "approved_revision")
            self.assertEqual(effective["effective_id"], revised["id"])
            self.assertEqual(effective["content"], "approved goal revision")
            self.assertEqual(effective["approved_review_hash"], approved["latest_review_hash"])

    def test_show_marks_pending_revision_as_audit_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-effective-show")
            run_dir = root / "runs" / status["run_id"]
            original_content = resolve_effective_task_outputs(run_dir)[0]["content"]
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="revise visible output",
            )
            revise_task_output(
                run_dir,
                content="new visible approved output",
                revised_by="Editor",
                note="visible revision",
                review_decision_hash=reviewed["latest_review_hash"],
            )

            pending_view = render_run_artifacts(run_dir)
            effective_section = pending_view.split(
                "=== Evidence（原始审计记录） ===", maxsplit=1
            )[0]
            self.assertIn(str(original_content), effective_section)
            self.assertNotIn("new visible approved output", effective_section)
            self.assertIn("new visible approved output", pending_view)

            approve_run(run_dir, approver="Reviewer", note="visible approved")
            approved_view = render_run_artifacts(run_dir)
            approved_section = approved_view.split(
                "=== Evidence（原始审计记录） ===", maxsplit=1
            )[0]
            self.assertIn("new visible approved output", approved_section)
            self.assertIn("已批准修订", approved_section)

    def test_latest_revision_in_approved_bundle_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-effective-latest")
            run_dir = root / "runs" / status["run_id"]
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="iterate",
            )
            first = revise_task_output(
                run_dir,
                content="revision one",
                revised_by="Editor",
                note="first",
                review_decision_hash=reviewed["latest_review_hash"],
            )
            second = revise_task_output(
                run_dir,
                content="revision two",
                revised_by="Editor",
                note="second",
                review_decision_hash=reviewed["latest_review_hash"],
            )
            approve_run(run_dir, approver="Reviewer", note="latest accepted")

            effective = resolve_effective_task_outputs(run_dir)[0]
            self.assertNotEqual(effective["effective_id"], first["id"])
            self.assertEqual(effective["effective_id"], second["id"])
            self.assertEqual(effective["revision_of"], first["id"])

    def test_approved_ai_draft_is_effective_for_task_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-effective-ai")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Reviewer", note="task one")
            resume_run(run_dir)
            draft = record_supplemental_evidence(
                run_dir,
                content="reviewed AI research draft",
                source="ollama://qwen2.5:7b",
                method="local draft",
                limitations="facts require verification",
                collected_by="Ollama",
                evidence_role="ai_draft",
            )
            approve_run(run_dir, approver="Reviewer", note="AI draft checked")

            outputs = resolve_effective_task_outputs(run_dir)
            task_two = next(item for item in outputs if item["task_id"].startswith("TASK-MVP-02"))
            self.assertEqual(task_two["source"], "approved_revision")
            self.assertEqual(task_two["effective_role"], "ai_draft")
            self.assertEqual(task_two["effective_id"], draft["id"])

    def test_resolver_rejects_tampered_effective_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-effective-tamper")
            run_dir = root / "runs" / status["run_id"]
            reviewed = review_run(
                run_dir,
                reviewer="Reviewer",
                decision="Changes Requested",
                note="revise then verify",
            )
            revised = revise_task_output(
                run_dir,
                content="approved before tampering",
                revised_by="Editor",
                note="revision",
                review_decision_hash=reviewed["latest_review_hash"],
            )
            approve_run(run_dir, approver="Reviewer", note="accepted")
            (run_dir / revised["path"]).write_text("{}\n", encoding="utf-8")

            with self.assertRaises(IntegrityError):
                resolve_effective_task_outputs(run_dir)


if __name__ == "__main__":
    unittest.main()
