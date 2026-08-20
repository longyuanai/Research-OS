from __future__ import annotations

import random
import unittest

from research_os_mvp.revisions import (
    RevisionChainError,
    latest_revision,
    resolve_revision_chain,
    select_task_revisions,
)

BASE = "OUT-TASK-1"
TASK = "task-1"


def _revision(index: int, parent: str) -> dict:
    return {
        "evidence_id": f"EVID-MVP-run-SUP-{index:02d}",
        "revision_of": parent,
        "task_id": TASK,
        "evidence_role": "task_output_revision",
    }


def _linear_chain(count: int) -> list[dict]:
    chain: list[dict] = []
    parent = BASE
    for index in range(1, count + 1):
        revision = _revision(index, parent)
        chain.append(revision)
        parent = revision["evidence_id"]
    return chain


def _filename(revision: dict) -> str:
    sequence = revision["evidence_id"].rsplit("-", 1)[-1]
    return f"EVID-SUPPLEMENTAL-{sequence}.json"


class RevisionChainTests(unittest.TestCase):
    def test_empty_input_yields_no_chain(self) -> None:
        self.assertEqual(
            resolve_revision_chain([], task_id=TASK, base_output_id=BASE), []
        )
        self.assertIsNone(latest_revision([], task_id=TASK, base_output_id=BASE))

    def test_chain_follows_links_not_input_order(self) -> None:
        chain = _linear_chain(6)
        shuffled = list(chain)
        random.Random(7).shuffle(shuffled)
        resolved = resolve_revision_chain(shuffled, task_id=TASK, base_output_id=BASE)
        self.assertEqual(
            [item["evidence_id"] for item in resolved],
            [item["evidence_id"] for item in chain],
        )

    def test_latest_revision_is_the_chain_tail(self) -> None:
        chain = _linear_chain(4)
        newest = latest_revision(
            list(reversed(chain)), task_id=TASK, base_output_id=BASE
        )
        assert newest is not None
        self.assertEqual(newest["evidence_id"], chain[-1]["evidence_id"])

    def test_three_digit_sequence_survives_filename_sort(self) -> None:
        """Regression witness for the filename-ordering defect.

        ``sorted()`` over ``EVID-SUPPLEMENTAL-<n>.json`` yields 1..10, 100, 101, ...
        once the sequence reaches three digits. The old implementations took the last
        match in that order and therefore bound to revision 99. The chain resolver
        must be immune to it.
        """
        chain = _linear_chain(120)
        by_filename = sorted(chain, key=_filename)

        # Confirm the hazard is real for this fixture before asserting the fix.
        self.assertNotEqual(
            by_filename[-1]["evidence_id"],
            chain[-1]["evidence_id"],
            "fixture no longer reproduces the filename-ordering hazard",
        )
        self.assertEqual(by_filename[-1]["evidence_id"], "EVID-MVP-run-SUP-99")

        newest = latest_revision(by_filename, task_id=TASK, base_output_id=BASE)
        assert newest is not None
        self.assertEqual(newest["evidence_id"], "EVID-MVP-run-SUP-120")

    def test_fork_is_rejected(self) -> None:
        chain = _linear_chain(2)
        fork = _revision(99, BASE)
        with self.assertRaises(RevisionChainError) as ctx:
            resolve_revision_chain(chain + [fork], task_id=TASK, base_output_id=BASE)
        self.assertIn("forks", str(ctx.exception))

    def test_cycle_is_rejected(self) -> None:
        first = _revision(1, BASE)
        second = _revision(2, first["evidence_id"])
        first["revision_of"] = second["evidence_id"]
        with self.assertRaises(RevisionChainError):
            resolve_revision_chain(
                [first, second], task_id=TASK, base_output_id=BASE
            )

    def test_unreachable_revision_is_rejected(self) -> None:
        detached = _revision(5, "EVID-MVP-run-SUP-04")
        with self.assertRaises(RevisionChainError) as ctx:
            resolve_revision_chain([detached], task_id=TASK, base_output_id=BASE)
        self.assertIn("unreachable", str(ctx.exception))

    def test_missing_parent_reference_is_rejected(self) -> None:
        broken = {"evidence_id": "EVID-MVP-run-SUP-01", "task_id": TASK}
        with self.assertRaises(RevisionChainError) as ctx:
            resolve_revision_chain([broken], task_id=TASK, base_output_id=BASE)
        self.assertIn("parent reference", str(ctx.exception))

    def test_missing_evidence_id_is_rejected(self) -> None:
        broken = {"revision_of": BASE, "task_id": TASK}
        with self.assertRaises(RevisionChainError) as ctx:
            resolve_revision_chain([broken], task_id=TASK, base_output_id=BASE)
        self.assertIn("Evidence ID", str(ctx.exception))


class SelectTaskRevisionsTests(unittest.TestCase):
    def test_filters_by_task_and_role(self) -> None:
        records = [
            ("a", {"task_id": TASK, "evidence_role": "task_output_revision"}),
            ("b", {"task_id": TASK, "evidence_role": "ai_draft"}),
            ("c", {"task_id": "other", "evidence_role": "task_output_revision"}),
            ("d", {"task_id": TASK}),
            ("e", "not-a-dict"),
        ]
        selected = select_task_revisions(records, task_id=TASK)
        self.assertEqual([path for path, _ in selected], ["a"])


if __name__ == "__main__":
    unittest.main()
