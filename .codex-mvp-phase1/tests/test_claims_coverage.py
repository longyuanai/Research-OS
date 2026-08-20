from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_os_mvp.claims import build_claims_record, claims_coverage
from research_os_mvp.errors import IntegrityError
from research_os_mvp.integrity import read_json, write_hash_manifest, write_json_atomic
from research_os_mvp.runtime import (
    claims_coverage_status,
    create_run,
    record_confirmed_claims,
    verify_run,
)
from tests.helpers import EXAMPLE_PACK

CONFIRMED_AT = "2026-08-13T10:00:00Z"
TASK_ID = "TASK-MVP-01-capture-requirement"
EVIDENCE_ID = "EVID-MVP-{run_id}-01"


def _summary(task_id: str, claim_count: int) -> dict:
    return {"task_id": task_id, "claim_count": claim_count}


def _view(summaries: list[dict], stale: list[str] | None = None) -> dict:
    return {"summaries": summaries, "stale_task_ids": stale or []}


class CoverageArithmeticTests(unittest.TestCase):
    """Pure-function coverage combinatorics; no Run fixture required."""

    def test_all_executed_confirmed_returns_true(self) -> None:
        view = _view([_summary("t1", 2), _summary("t2", 1)])
        result = claims_coverage(view, ["t1", "t2"])
        self.assertTrue(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["confirmed_task_count"], 2)
        self.assertEqual(result["tasks_missing_claims"], [])

    def test_partial_confirmation_returns_false(self) -> None:
        """D-03 lock: an aggregate 'has some claims' must not read as full coverage."""
        view = _view([_summary("t1", 3)])
        result = claims_coverage(view, ["t1", "t2", "t3"])
        self.assertFalse(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["confirmed_task_count"], 1)
        self.assertEqual(result["executed_task_count"], 3)
        self.assertEqual(result["tasks_missing_claims"], ["t2", "t3"])

    def test_unexecuted_task_is_not_counted_in_denominator(self) -> None:
        view = _view([_summary("t1", 1)])
        result = claims_coverage(view, ["t1"])
        self.assertTrue(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["executed_task_count"], 1)

    def test_empty_claims_file_does_not_confirm_a_task(self) -> None:
        view = _view([_summary("t1", 0)])
        result = claims_coverage(view, ["t1"])
        self.assertFalse(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["tasks_with_empty_claims"], ["t1"])
        self.assertEqual(result["tasks_missing_claims"], [])

    def test_stale_task_is_its_own_bucket(self) -> None:
        view = _view([_summary("t1", 2)], stale=["t2"])
        result = claims_coverage(view, ["t1", "t2"])
        self.assertFalse(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["tasks_with_stale_claims"], ["t2"])
        self.assertEqual(result["tasks_missing_claims"], [])

    def test_buckets_are_disjoint_and_cover_every_executed_task(self) -> None:
        view = _view(
            [_summary("t1", 2), _summary("t2", 0)],
            stale=["t3"],
        )
        executed = ["t1", "t2", "t3", "t4"]
        result = claims_coverage(view, executed)
        buckets = (
            result["tasks_confirmed"]
            + result["tasks_with_empty_claims"]
            + result["tasks_with_stale_claims"]
            + result["tasks_missing_claims"]
        )
        self.assertEqual(sorted(buckets), sorted(executed))
        self.assertEqual(len(buckets), len(set(buckets)))

    def test_no_executed_task_does_not_auto_pass(self) -> None:
        result = claims_coverage(_view([]), [])
        self.assertFalse(result["all_executed_tasks_confirmed"])
        self.assertEqual(result["executed_task_count"], 0)


class ClaimReferenceCoverageTests(unittest.TestCase):
    def _coverage(
        self,
        run_id: str,
        classifications: list[tuple[str, str]],
    ) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", run_id)
            run_dir = root / "runs" / status["run_id"]
            report = read_json(run_dir / "reports" / "TASK-REPORT-01.json")
            source_text = read_json(run_dir / report["output"]["path"])["content"]
            evidence_id = EVIDENCE_ID.format(run_id=status["run_id"])
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
                task_id=TASK_ID,
                confirmed_by="Human Reviewer",
                confirmed_at=CONFIRMED_AT,
                claims=claims,
            )
            return claims_coverage_status(run_dir)

    def test_no_verifiable_facts_returns_none_not_one(self) -> None:
        result = self._coverage(
            "run-reference-no-facts",
            [("interpretation", "direct")],
        )
        self.assertIsNone(result["fact_coverage"])
        self.assertTrue(result["hard_gate_pass"])
        self.assertEqual(result["all_coverage"], 1.0)

    def test_all_facts_cited_returns_hard_gate_pass(self) -> None:
        result = self._coverage(
            "run-reference-all-facts-cited",
            [
                ("verifiable_fact", "direct"),
                ("verifiable_fact", "derived"),
            ],
        )
        self.assertTrue(result["hard_gate_pass"])
        self.assertEqual(result["fact_coverage"], 1.0)
        self.assertEqual(result["unsupported_fact_count"], 0)

    def test_single_unsupported_fact_fails_hard_gate(self) -> None:
        result = self._coverage(
            "run-reference-one-unsupported-fact",
            [
                ("verifiable_fact", "direct"),
                ("verifiable_fact", "unsupported"),
            ],
        )
        self.assertFalse(result["hard_gate_pass"])
        self.assertEqual(result["fact_coverage"], 0.5)
        self.assertEqual(result["unsupported_fact_count"], 1)

    def test_unsupported_interpretation_does_not_fail_hard_gate(self) -> None:
        result = self._coverage(
            "run-reference-unsupported-interpretation",
            [
                ("verifiable_fact", "direct"),
                ("interpretation", "unsupported"),
            ],
        )
        self.assertTrue(result["hard_gate_pass"])
        self.assertEqual(result["fact_coverage"], 1.0)
        self.assertEqual(result["all_coverage"], 0.5)
        self.assertEqual(result["unsupported_fact_count"], 0)
        self.assertEqual(result["unsupported_claim_count"], 1)

    def test_fact_coverage_arithmetic_matches_manual_count(self) -> None:
        result = self._coverage(
            "run-reference-arithmetic",
            [
                ("verifiable_fact", "direct"),
                ("verifiable_fact", "derived"),
                ("verifiable_fact", "direct"),
                ("verifiable_fact", "unsupported"),
                ("interpretation", "unsupported"),
            ],
        )
        self.assertEqual(result["fact_coverage"], 3 / 4)
        self.assertEqual(result["all_coverage"], 3 / 5)
        self.assertEqual(result["unsupported_fact_count"], 1)
        self.assertEqual(result["unsupported_claim_count"], 2)

    def test_kind_counts_are_exposed_in_output(self) -> None:
        result = self._coverage(
            "run-reference-kind-counts",
            [
                ("verifiable_fact", "direct"),
                ("interpretation", "unsupported"),
                ("recommendation", "derived"),
                ("assumption", "unsupported"),
            ],
        )
        self.assertEqual(
            result["kind_counts"],
            {
                "assumption": 1,
                "interpretation": 1,
                "recommendation": 1,
                "verifiable_fact": 1,
            },
        )

    def test_legacy_run_without_claims_returns_null_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(
                EXAMPLE_PACK,
                root / "runs",
                "run-reference-legacy-null",
            )
            result = claims_coverage_status(root / "runs" / status["run_id"])

        self.assertIsNone(result["fact_coverage"])
        self.assertIsNone(result["all_coverage"])
        self.assertTrue(result["hard_gate_pass"])
        self.assertEqual(result["unsupported_claim_count"], 0)
        self.assertEqual(result["unsupported_fact_count"], 0)
        self.assertEqual(result["kind_counts"], {kind: 0 for kind in (
            "assumption",
            "interpretation",
            "recommendation",
            "verifiable_fact",
        )})


class CoverageIntegrationTests(unittest.TestCase):
    def _run(self, root: Path, run_id: str) -> Path:
        status = create_run(EXAMPLE_PACK, root / "runs", run_id)
        return root / "runs" / status["run_id"]

    def _source_content(self, run_dir: Path) -> str:
        report = read_json(run_dir / "reports" / "TASK-REPORT-01.json")
        return read_json(run_dir / report["output"]["path"])["content"]

    def _confirm(self, run_dir: Path) -> None:
        run_id = read_json(run_dir / "state.json")["run_id"]
        record_confirmed_claims(
            run_dir,
            task_id=TASK_ID,
            confirmed_by="Human Reviewer",
            confirmed_at=CONFIRMED_AT,
            claims=[
                {
                    "text": self._source_content(run_dir),
                    "kind": "verifiable_fact",
                    "evidence_ids": [EVIDENCE_ID.format(run_id=run_id)],
                    "support": "direct",
                }
            ],
        )

    def test_legacy_run_without_claims_dir_returns_zero_not_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-coverage-legacy")
            self.assertFalse((run_dir / "claims").exists())
            result = claims_coverage_status(run_dir)
            self.assertEqual(result["confirmed_task_count"], 0)
            self.assertEqual(result["tasks_missing_claims"], [TASK_ID])
            self.assertFalse(result["all_executed_tasks_confirmed"])
            self.assertEqual(result["integrity"], "verified")

    def test_confirmed_executed_task_reports_full_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-coverage-confirmed")
            self._confirm(run_dir)
            result = claims_coverage_status(run_dir)
            self.assertTrue(result["all_executed_tasks_confirmed"])
            self.assertEqual(result["tasks_confirmed"], [TASK_ID])
            self.assertEqual(result["executed_task_count"], 1)

    def test_pack_tasks_beyond_execution_are_excluded(self) -> None:
        """The Pack declares three Tasks; only the executed prefix is the denominator."""
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-coverage-prefix")
            pack_tasks = read_json(run_dir / "pack.snapshot.json")["mission"]["tasks"]
            self.assertGreater(len(pack_tasks), 1)
            self._confirm(run_dir)
            result = claims_coverage_status(run_dir)
            self.assertEqual(result["executed_task_count"], 1)
            self.assertTrue(result["all_executed_tasks_confirmed"])

    def test_stale_claims_are_reported_not_crashed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-coverage-stale")
            self._confirm(run_dir)
            claims_path = run_dir / "claims" / f"CLAIMS-{TASK_ID}.json"
            record = read_json(claims_path)
            record["source_artifact_sha256"] = "0" * 64
            write_json_atomic(claims_path, record)
            write_hash_manifest(run_dir)

            result = claims_coverage_status(run_dir)
            self.assertEqual(result["tasks_with_stale_claims"], [TASK_ID])
            self.assertFalse(result["all_executed_tasks_confirmed"])
            # Coverage degrades rather than hiding which Task needs re-confirmation.
            self.assertEqual(result["integrity"], "stale-claims")

            # verify_run keeps its strict C1 behaviour; only coverage degrades.
            with self.assertRaisesRegex(IntegrityError, "stale Task output"):
                verify_run(run_dir)

    def test_coverage_matches_verify_claims_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), "run-coverage-consistent")
            self._confirm(run_dir)
            from research_os_mvp.runtime import claims_status

            view = claims_status(run_dir)
            coverage = claims_coverage_status(run_dir)
            confirmed = [
                summary["task_id"]
                for summary in view["summaries"]
                if summary["claim_count"] > 0
            ]
            self.assertEqual(coverage["tasks_confirmed"], confirmed)


class BuildValidationTests(unittest.TestCase):
    """D-02: the builder must reject what the validator would reject."""

    def _build(self, **overrides: object) -> dict:
        claim = {
            "text": "an assertion",
            "kind": "verifiable_fact",
            "evidence_ids": [],
            "support": "unsupported",
        }
        claim.update(overrides)
        return build_claims_record(
            run_id="run-1",
            task_id="task-1",
            source_artifact_sha256="a" * 64,
            confirmed_by="Human Reviewer",
            confirmed_at=CONFIRMED_AT,
            claims=[claim],
        )

    def test_valid_claim_builds(self) -> None:
        record = self._build()
        self.assertEqual(record["claims"][0]["kind"], "verifiable_fact")

    def test_build_rejects_unknown_kind(self) -> None:
        with self.assertRaisesRegex(IntegrityError, "kind must be one of"):
            self._build(kind="opinion")

    def test_build_rejects_missing_kind(self) -> None:
        with self.assertRaisesRegex(IntegrityError, "kind must be one of"):
            self._build(kind=None)

    def test_build_rejects_unknown_support(self) -> None:
        with self.assertRaisesRegex(IntegrityError, "support must be one of"):
            self._build(support="maybe")


if __name__ == "__main__":
    unittest.main()
