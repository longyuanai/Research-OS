from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.claims import current_task_source
from research_os_mvp.errors import IntegrityError, RunStateError
from research_os_mvp.integrity import (
    read_json,
    write_hash_manifest,
    write_json_atomic,
)
from research_os_mvp.runtime import (
    approve_run,
    bind_claims_gate,
    create_run,
    record_confirmed_claims,
    resume_run,
    verify_run,
)
from tests.helpers import EXAMPLE_PACK

CONFIRMED_AT = "2026-08-17T10:00:00Z"
TASK_ONE = "TASK-MVP-01-capture-requirement"
TASK_TWO = "TASK-MVP-02-capture-human-gate"
TASK_THREE = "TASK-MVP-03-compose-report"


class ClaimsGateTests(unittest.TestCase):
    def _create(self, root: Path, run_id: str, *, enabled: bool) -> Path:
        status = create_run(
            EXAMPLE_PACK,
            root / "runs",
            run_id,
            claims_gate_enabled=enabled,
            claims_gate_actor="Claims Policy Admin" if enabled else None,
        )
        return root / "runs" / status["run_id"]

    def _record_claims(
        self,
        run_dir: Path,
        *,
        task_id: str,
        classifications: list[tuple[str, str]],
    ) -> None:
        _, _, source_text = current_task_source(run_dir, task_id)
        evidence_id = read_json(next((run_dir / "evidence").glob("*.json")))[
            "evidence_id"
        ]
        claims = [
            {
                "text": source_text,
                "kind": kind,
                "evidence_ids": (
                    [] if support == "unsupported" else [evidence_id]
                ),
                "support": support,
            }
            for kind, support in classifications
        ]
        record_confirmed_claims(
            run_dir,
            task_id=task_id,
            confirmed_by="Human Reviewer",
            confirmed_at=CONFIRMED_AT,
            claims=claims,
        )

    def test_gate_blocks_resume_when_pending_task_has_unsupported_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-unsupported-fact",
                enabled=True,
            )
            self._record_claims(
                run_dir,
                task_id=TASK_ONE,
                classifications=[("verifiable_fact", "unsupported")],
            )
            approve_run(run_dir, approver="Human Reviewer")

            with self.assertRaisesRegex(
                RunStateError,
                "1 unsupported verifiable_fact",
            ):
                resume_run(run_dir)

    def test_gate_blocks_resume_when_pending_task_has_no_claims(self) -> None:
        for variant, record_empty in (("missing", False), ("empty", True)):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as temporary:
                run_dir = self._create(
                    Path(temporary),
                    f"run-gate-{variant}-claims",
                    enabled=True,
                )
                if record_empty:
                    self._record_claims(
                        run_dir,
                        task_id=TASK_ONE,
                        classifications=[],
                    )
                approve_run(run_dir, approver="Human Reviewer")

                with self.assertRaisesRegex(
                    RunStateError,
                    rf"{variant} Claim confirmation.*0 Claim",
                ):
                    resume_run(run_dir)

    def test_gate_blocks_resume_when_pending_task_has_only_interpretations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-only-interpretations",
                enabled=True,
            )
            self._record_claims(
                run_dir,
                task_id=TASK_ONE,
                classifications=[("interpretation", "direct")],
            )
            approve_run(run_dir, approver="Human Reviewer")

            with self.assertRaisesRegex(
                RunStateError,
                r"no verifiable_fact \(0 present\)",
            ):
                resume_run(run_dir)

    def test_gate_allows_resume_when_pending_task_fully_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-supported",
                enabled=True,
            )
            self._record_claims(
                run_dir,
                task_id=TASK_ONE,
                classifications=[("verifiable_fact", "direct")],
            )
            approve_run(run_dir, approver="Human Reviewer")

            resumed = resume_run(run_dir)
            self.assertEqual(resumed["status"], "paused")
            self.assertEqual(resumed["pending_task_id"], TASK_TWO)

    def test_gate_error_message_names_task_and_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-message",
                enabled=True,
            )
            self._record_claims(
                run_dir,
                task_id=TASK_ONE,
                classifications=[
                    ("verifiable_fact", "unsupported"),
                    ("verifiable_fact", "unsupported"),
                ],
            )
            approve_run(run_dir, approver="Human Reviewer")

            with self.assertRaises(RunStateError) as raised:
                resume_run(run_dir)
            message = str(raised.exception)
            self.assertIn(TASK_ONE, message)
            self.assertIn("2 unsupported verifiable_fact", message)

    def test_legacy_run_without_gate_resumes_with_unsupported_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-legacy-unsupported-fact",
                enabled=False,
            )
            self._record_claims(
                run_dir,
                task_id=TASK_ONE,
                classifications=[("verifiable_fact", "unsupported")],
            )
            approve_run(run_dir, approver="Human Reviewer")

            resumed = resume_run(run_dir)
            self.assertEqual(resumed["pending_task_id"], TASK_TWO)

    def test_legacy_run_without_claims_dir_resumes_normally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-legacy-no-claims-dir",
                enabled=False,
            )
            self.assertFalse((run_dir / "claims").exists())
            approve_run(run_dir, approver="Human Reviewer")

            resumed = resume_run(run_dir)
            self.assertEqual(resumed["pending_task_id"], TASK_TWO)

    def test_enabling_gate_does_not_retroactively_block_already_approved_tasks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-nonretroactive",
                enabled=False,
            )
            approve_run(run_dir, approver="Human Reviewer", note="task one")
            resume_run(run_dir)
            approve_run(run_dir, approver="Human Reviewer", note="task two")

            bound = bind_claims_gate(run_dir, actor="Claims Policy Admin")
            self.assertEqual(bound["claims_gate_from_task_index"], 2)
            self.assertFalse(bound["claims_gate_applies_to_pending_task"])
            resumed = resume_run(run_dir)
            self.assertEqual(resumed["pending_task_id"], TASK_THREE)
            self.assertTrue(resumed["claims_gate_applies_to_pending_task"])

    def test_gate_flag_is_persisted_in_state_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-persisted",
                enabled=True,
            )
            state = read_json(run_dir / "state.json")
            events = [
                json.loads(line)
                for line in (run_dir / "events.jsonl").read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            verified = verify_run(run_dir)

            self.assertIs(state["claims_gate_enabled"], True)
            self.assertEqual(state["claims_gate_from_task_index"], 0)
            self.assertEqual(
                [event["type"] for event in events].count("claims_gate_bound"),
                1,
            )
            self.assertTrue(verified["claims_gate_enabled"])
            self.assertEqual(verified["claims_gate_from_task_index"], 0)

    def test_gate_flag_tampering_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._create(
                Path(temporary),
                "run-gate-flag-tamper",
                enabled=False,
            )
            state = read_json(run_dir / "state.json")
            state["claims_gate_enabled"] = True
            state["claims_gate_from_task_index"] = 0
            write_json_atomic(run_dir / "state.json", state)
            write_hash_manifest(run_dir)

            with self.assertRaisesRegex(
                IntegrityError,
                "exactly one binding event",
            ):
                verify_run(run_dir)


if __name__ == "__main__":
    unittest.main()
