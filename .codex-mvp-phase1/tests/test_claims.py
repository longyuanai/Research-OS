from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.claims import claims_digest
from research_os_mvp.cli import main
from research_os_mvp.errors import IntegrityError
from research_os_mvp.integrity import (
    read_json,
    sha256_file,
    sha256_text,
    write_hash_manifest,
    write_json_atomic,
)
from research_os_mvp.runtime import (
    approve_run,
    claims_status,
    create_run,
    record_confirmed_claims,
    resume_run,
    verify_run,
)
from tests.helpers import EXAMPLE_PACK

CONFIRMED_AT = "2026-08-13T10:00:00Z"
TASK_ID = "TASK-MVP-01-capture-requirement"
EVIDENCE_ID = "EVID-MVP-{run_id}-01"


class ClaimIntegrityTests(unittest.TestCase):
    def _run(self, root: Path, run_id: str) -> Path:
        status = create_run(EXAMPLE_PACK, root / "runs", run_id)
        return root / "runs" / status["run_id"]

    def _source_content(self, run_dir: Path) -> str:
        evidence = read_json(self._source_evidence_path(run_dir))
        return evidence["content"]

    def _source_evidence_path(self, run_dir: Path) -> Path:
        report = read_json(run_dir / "reports" / "TASK-REPORT-01.json")
        return run_dir / report["output"]["path"]

    def _record(
        self,
        run_dir: Path,
        *,
        claims: list[dict] | None = None,
    ) -> dict:
        run_id = read_json(run_dir / "state.json")["run_id"]
        if claims is None:
            claims = [
                {
                    "text": self._source_content(run_dir),
                    "kind": "verifiable_fact",
                    "evidence_ids": [EVIDENCE_ID.format(run_id=run_id)],
                    "support": "direct",
                }
            ]
        return record_confirmed_claims(
            run_dir,
            task_id=TASK_ID,
            confirmed_by="Human Reviewer",
            confirmed_at=CONFIRMED_AT,
            claims=claims,
        )

    def _claims_path(self, run_dir: Path) -> Path:
        return run_dir / "claims" / f"CLAIMS-{TASK_ID}.json"

    def _rewrite_claims(self, run_dir: Path, record: dict) -> None:
        write_json_atomic(self._claims_path(run_dir), record)
        write_hash_manifest(run_dir)

    def test_claim_text_mutated_after_confirm_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-text-tamper")
            self._record(run_dir)
            record = read_json(self._claims_path(run_dir))
            record["claims"][0]["text"] += " changed"
            record["claims_sha256"] = claims_digest(record["claims"])
            self._rewrite_claims(run_dir, record)

            with self.assertRaisesRegex(IntegrityError, "text hash mismatch"):
                verify_run(run_dir)

    def test_claim_references_unknown_evidence_id_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-dangling")
            self._record(run_dir)
            record = read_json(self._claims_path(run_dir))
            record["claims"][0]["evidence_ids"] = ["EVID-MVP-UNKNOWN-01"]
            record["claims_sha256"] = claims_digest(record["claims"])
            self._rewrite_claims(run_dir, record)

            with self.assertRaisesRegex(IntegrityError, "unknown Evidence IDs"):
                verify_run(run_dir)

    def test_duplicate_claim_id_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-duplicate")
            run_id = read_json(run_dir / "state.json")["run_id"]
            source = self._source_content(run_dir)
            self._record(
                run_dir,
                claims=[
                    {
                        "text": source,
                        "kind": "verifiable_fact",
                        "evidence_ids": [EVIDENCE_ID.format(run_id=run_id)],
                        "support": "direct",
                    },
                    {
                        "text": "The MVP must validate one declarative Builder Pack",
                        "kind": "interpretation",
                        "evidence_ids": [EVIDENCE_ID.format(run_id=run_id)],
                        "support": "derived",
                    },
                ],
            )
            record = read_json(self._claims_path(run_dir))
            record["claims"][1]["claim_id"] = record["claims"][0]["claim_id"]
            record["claims_sha256"] = claims_digest(record["claims"])
            self._rewrite_claims(run_dir, record)

            with self.assertRaisesRegex(IntegrityError, "invalid or duplicated"):
                verify_run(run_dir)

    def test_claims_file_bound_to_stale_artifact_hash_requires_reconfirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-stale-source")
            self._record(run_dir)
            evidence_path = self._source_evidence_path(run_dir)
            evidence = read_json(evidence_path)
            evidence["content"] += " Revised source."
            evidence["content_sha256"] = sha256_text(evidence["content"])
            write_json_atomic(evidence_path, evidence)
            report_path = run_dir / "reports" / "TASK-REPORT-01.json"
            report = read_json(report_path)
            report["output"]["sha256"] = sha256_file(evidence_path)
            write_json_atomic(report_path, report)
            write_hash_manifest(run_dir)

            with self.assertRaisesRegex(IntegrityError, "stale Task output"):
                verify_run(run_dir)

            reconfirmed = self._record(run_dir)
            self.assertTrue(reconfirmed["reconfirmed"])
            self.assertEqual(reconfirmed["integrity"], "verified")

    def test_canonical_claims_hash_is_deterministic(self) -> None:
        left = [
            {
                "claim_id": "CLM-001",
                "text": "alpha\nbeta",
                "evidence_ids": ["EVID-01"],
            }
        ]
        right = [
            {
                "evidence_ids": ["EVID-01"],
                "text": "alpha\nbeta",
                "claim_id": "CLM-001",
            }
        ]
        self.assertEqual(claims_digest(left), claims_digest(right))

    def test_existing_run_without_claims_remains_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-legacy")

            status = verify_run(run_dir)
            view = claims_status(run_dir)

            self.assertEqual(status["integrity"], "verified")
            self.assertFalse(status["claims_confirmed"])
            self.assertEqual(status["claim_count"], 0)
            self.assertEqual(view["records"], [])

    def test_record_is_verified_idempotent_and_visible_from_read_only_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-cli")
            first = self._record(run_dir)
            second = self._record(run_dir)
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main(["claims", str(run_dir)])
            view = json.loads(output.getvalue())

            self.assertFalse(first["idempotent"])
            self.assertTrue(second["idempotent"])
            self.assertEqual(second["event_count"], first["event_count"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(view["claims_confirmed"])
            self.assertEqual(view["claim_count"], 1)
            self.assertEqual(view["unsupported_claim_count"], 0)
            self.assertEqual(len(view["records"]), 1)
            self.assertEqual(view["integrity"], "verified")

    def test_zero_claim_record_is_not_reported_as_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-zero")
            recorded = self._record(run_dir, claims=[])

            self.assertFalse(recorded["claims_confirmed"])
            self.assertEqual(recorded["claim_count"], 0)
            self.assertEqual(recorded["claims_file_count"], 1)

    def test_unsupported_claim_is_observable_but_not_a_c1_runtime_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-no-c2-gate")
            recorded = self._record(
                run_dir,
                claims=[
                    {
                        "text": self._source_content(run_dir),
                        "kind": "verifiable_fact",
                        "evidence_ids": [],
                        "support": "unsupported",
                    }
                ],
            )

            self.assertEqual(recorded["unsupported_claim_count"], 1)
            approve_run(run_dir, approver="Human Reviewer", note="C1 only")
            resumed = resume_run(run_dir)
            self.assertEqual(resumed["status"], "paused")
            self.assertEqual(resumed["pending_task_id"], "TASK-MVP-02-capture-human-gate")

    def test_changed_claim_record_is_reconfirmed_with_an_audited_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-claims-immutable")
            first = self._record(run_dir)
            second = record_confirmed_claims(
                run_dir,
                task_id=TASK_ID,
                confirmed_by="Different Human",
                confirmed_at="2026-08-13T11:00:00Z",
                claims=[],
            )

            self.assertTrue(second["reconfirmed"])
            self.assertEqual(second["event_count"], first["event_count"] + 1)
            self.assertFalse(second["claims_confirmed"])
            self.assertEqual(verify_run(run_dir)["integrity"], "verified")


if __name__ == "__main__":
    unittest.main()
