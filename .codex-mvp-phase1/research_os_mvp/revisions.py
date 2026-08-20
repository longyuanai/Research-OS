"""Order-independent Task output revision chain resolution.

Historically three call sites derived "the latest Task output revision" by taking
the last match while iterating ``sorted(evidence_dir.glob("*.json"))``. Supplemental
Evidence artifacts are named ``EVID-SUPPLEMENTAL-<n>.json`` with a minimum-width
format, so lexicographic order stops matching creation order once the sequence
reaches three digits::

    sorted([...01..102]) -> 1, 2, ... 10, 100, 101, 102, 11, 12, ...

That produced a silent wrong-revision binding in two call sites and a false
"chain is broken" integrity failure in a third. This module resolves the chain by
following ``revision_of`` links instead, so the result does not depend on
filename order, directory order, or sequence width.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from research_os_mvp.errors import IntegrityError

TASK_OUTPUT_REVISION_ROLE = "task_output_revision"


class RevisionChainError(IntegrityError):
    """The recorded revisions do not form one linear chain from the base output."""


def _evidence_id(evidence: dict[str, Any]) -> str:
    value = evidence.get("evidence_id")
    if not isinstance(value, str) or not value:
        raise RevisionChainError("Task output revision has no Evidence ID")
    return value


def resolve_revision_chain(
    revisions: Iterable[dict[str, Any]],
    *,
    task_id: str,
    base_output_id: str,
) -> list[dict[str, Any]]:
    """Return the task's revisions ordered from oldest to newest.

    ``revisions`` may arrive in any order. Each entry must carry ``evidence_id`` and
    ``revision_of``. The chain must start at ``base_output_id``, must be linear, and
    must reach every supplied revision.

    Raises ``RevisionChainError`` on a fork, a cycle, a dangling parent, or an
    unreachable revision.
    """
    by_parent: dict[str, dict[str, Any]] = {}
    for revision in revisions:
        evidence_id = _evidence_id(revision)
        parent = revision.get("revision_of")
        if not isinstance(parent, str) or not parent:
            raise RevisionChainError(
                f"Task output revision has no parent reference: {evidence_id}"
            )
        if parent in by_parent:
            raise RevisionChainError(
                f"Task output revision chain forks at {parent}: "
                f"{by_parent[parent]['evidence_id']} and {evidence_id} ({task_id})"
            )
        by_parent[parent] = revision

    chain: list[dict[str, Any]] = []
    current = base_output_id
    seen = {current}
    while current in by_parent:
        nxt = by_parent.pop(current)
        evidence_id = _evidence_id(nxt)
        if evidence_id in seen:
            raise RevisionChainError(
                f"Task output revision chain contains a cycle at {evidence_id} ({task_id})"
            )
        seen.add(evidence_id)
        chain.append(nxt)
        current = evidence_id

    if by_parent:
        orphans = sorted(_evidence_id(item) for item in by_parent.values())
        raise RevisionChainError(
            f"Task output revision chain is broken for {task_id}: "
            f"unreachable revisions {orphans}"
        )
    return chain


def latest_revision(
    revisions: Iterable[dict[str, Any]],
    *,
    task_id: str,
    base_output_id: str,
) -> dict[str, Any] | None:
    """Return the newest revision in the chain, or ``None`` when there is none."""
    chain = resolve_revision_chain(
        revisions,
        task_id=task_id,
        base_output_id=base_output_id,
    )
    return chain[-1] if chain else None


def select_task_revisions(
    evidence_records: Iterable[tuple[Any, dict[str, Any]]],
    *,
    task_id: str,
) -> list[tuple[Any, dict[str, Any]]]:
    """Filter ``(path, evidence)`` pairs down to one Task's output revisions."""
    selected: list[tuple[Any, dict[str, Any]]] = []
    for path, evidence in evidence_records:
        if not isinstance(evidence, dict):
            continue
        if evidence.get("task_id") != task_id:
            continue
        if evidence.get("evidence_role") != TASK_OUTPUT_REVISION_ROLE:
            continue
        selected.append((path, evidence))
    return selected
