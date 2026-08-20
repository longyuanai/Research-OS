from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from research_os_mvp.errors import IntegrityError, RunStateError
from research_os_mvp.integrity import (
    canonical_json_text,
    read_json,
    sha256_file,
    sha256_text,
)
from research_os_mvp.revisions import latest_revision, select_task_revisions

CLAIMS_SCHEMA_VERSION = "research-os-mvp-claims/0.1"
CLAIMS_VIEW_SCHEMA_VERSION = "research-os-mvp-claims-view/0.1"
CLAIMS_COVERAGE_SCHEMA_VERSION = "research-os-mvp-claims-coverage/0.2"
CLAIM_KINDS = {
    "verifiable_fact",
    "interpretation",
    "recommendation",
    "assumption",
}
CLAIM_SUPPORT = {"direct", "derived", "unsupported"}
MAX_CLAIMS_PER_TASK = 1_000
MAX_CLAIM_TEXT_CHARS = 50_000
MAX_CLAIM_NOTE_CHARS = 2_000
MAX_ACTOR_CHARS = 100
MAX_CLAIMS_FILE_BYTES = 4 * 1024 * 1024


class StaleClaimsError(IntegrityError):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(
            f"Claims are bound to a stale Task output and require re-confirmation: {task_id}"
        )


def _required_text(value: Any, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IntegrityError(f"{label} must be a non-empty string")
    if len(value) > maximum:
        raise IntegrityError(f"{label} exceeds {maximum} characters")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise IntegrityError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _confirmed_at(value: Any) -> str:
    text = _required_text(value, "confirmed_at", 64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntegrityError("confirmed_at must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise IntegrityError("confirmed_at must include a timezone")
    if parsed.utcoffset() != timedelta(0):
        raise IntegrityError("confirmed_at must be in UTC")
    return text


def claims_artifact_path(run_dir: Path, task_id: str) -> Path:
    return run_dir / "claims" / f"CLAIMS-{task_id}.json"


def claims_digest(claims: list[dict[str, Any]]) -> str:
    return sha256_text(canonical_json_text(claims))


def _claim_id(run_id: str, task_id: str, sequence: int) -> str:
    return f"CLM-MVP-{run_id}-{task_id}-{sequence:03d}"


def build_claims_record(
    *,
    run_id: str,
    task_id: str,
    source_artifact_sha256: str,
    confirmed_by: str,
    confirmed_at: str,
    claims: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Build one canonical, human-confirmed Claim record for a Task output."""
    normalized_run_id = _required_text(run_id, "run_id", 200)
    normalized_task_id = _required_text(task_id, "task_id", 200)
    source_hash = _sha256(source_artifact_sha256, "source_artifact_sha256")
    actor = _required_text(confirmed_by, "confirmed_by", MAX_ACTOR_CHARS)
    timestamp = _confirmed_at(confirmed_at)
    normalized: list[dict[str, Any]] = []
    for sequence, candidate in enumerate(claims, start=1):
        if not isinstance(candidate, dict):
            raise IntegrityError(f"claims[{sequence - 1}] must be an object")
        allowed = {"text", "locator", "kind", "evidence_ids", "support", "note"}
        unexpected = sorted(set(candidate) - allowed)
        if unexpected:
            raise IntegrityError(
                f"claims[{sequence - 1}] has unexpected fields: {unexpected}"
            )
        text = _required_text(
            candidate.get("text"),
            f"claims[{sequence - 1}].text",
            MAX_CLAIM_TEXT_CHARS,
        )
        locator = candidate.get("locator", {"kind": "quote", "value": text})
        evidence_ids = candidate.get("evidence_ids")
        if not isinstance(evidence_ids, list):
            raise IntegrityError(f"claims[{sequence - 1}].evidence_ids must be a list")
        # Fail fast here rather than only in validate_claims_record: a builder that can
        # emit a structurally invalid record is a trap for any future caller that does
        # not immediately validate.
        kind = candidate.get("kind")
        if kind not in CLAIM_KINDS:
            raise IntegrityError(
                f"claims[{sequence - 1}].kind must be one of {sorted(CLAIM_KINDS)}"
            )
        support = candidate.get("support")
        if support not in CLAIM_SUPPORT:
            raise IntegrityError(
                f"claims[{sequence - 1}].support must be one of {sorted(CLAIM_SUPPORT)}"
            )
        claim: dict[str, Any] = {
            "claim_id": _claim_id(normalized_run_id, normalized_task_id, sequence),
            "text": text,
            "text_sha256": sha256_text(text),
            "locator": locator,
            "kind": kind,
            "evidence_ids": list(evidence_ids),
            "support": support,
        }
        if "note" in candidate:
            claim["note"] = candidate["note"]
        normalized.append(claim)
    if len(normalized) > MAX_CLAIMS_PER_TASK:
        raise IntegrityError(f"Claim count exceeds {MAX_CLAIMS_PER_TASK}")
    record = {
        "schema_version": CLAIMS_SCHEMA_VERSION,
        "run_id": normalized_run_id,
        "task_id": normalized_task_id,
        "source_artifact_sha256": source_hash,
        "confirmed_by": actor,
        "confirmed_at": timestamp,
        "claims": normalized,
    }
    record["claims_sha256"] = claims_digest(normalized)
    return record


def _source_text(path: Path) -> str:
    if path.suffix.casefold() != ".json":
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise IntegrityError(f"Cannot read Claim source artifact {path}: {exc}") from exc
    value = read_json(path)
    content = value.get("content") if isinstance(value, dict) else None
    if not isinstance(content, str):
        raise IntegrityError(f"Claim source JSON has no string content: {path}")
    return content


def current_task_source(run_dir: Path, task_id: str) -> tuple[Path, str, str]:
    """Resolve the latest human revision, AI draft, or original Task output.

    Revision selection follows the ``revision_of`` chain (see ``revisions.py``) rather
    than filename order, so it stays correct once the supplemental sequence reaches
    three digits.
    """
    original: Path | None = None
    base_output_id: str | None = None
    for report_path in sorted((run_dir / "reports").glob("TASK-REPORT-*.json")):
        report = read_json(report_path)
        output = report.get("output") if isinstance(report, dict) else None
        if not isinstance(report, dict) or report.get("task_id") != task_id:
            continue
        relative = output.get("path") if isinstance(output, dict) else None
        output_id = output.get("id") if isinstance(output, dict) else None
        if not isinstance(relative, str) or not isinstance(output_id, str) or not output_id:
            raise IntegrityError(f"Task Report output reference is invalid: {report_path}")
        original = run_dir / relative
        base_output_id = output_id
        break
    if original is None or base_output_id is None:
        raise RunStateError(f"Task has no executed output to confirm Claims against: {task_id}")

    records: list[tuple[Path, dict[str, Any]]] = []
    for evidence_path in sorted((run_dir / "evidence").glob("*.json")):
        evidence = read_json(evidence_path)
        if isinstance(evidence, dict):
            records.append((evidence_path, evidence))

    path_by_id: dict[str, Path] = {}
    for evidence_path, evidence in records:
        evidence_id = evidence.get("evidence_id")
        if isinstance(evidence_id, str) and evidence_id:
            path_by_id[evidence_id] = evidence_path

    revision_pairs = select_task_revisions(records, task_id=task_id)
    newest = latest_revision(
        [evidence for _, evidence in revision_pairs],
        task_id=task_id,
        base_output_id=base_output_id,
    )
    task_revision = path_by_id.get(newest["evidence_id"]) if newest is not None else None

    # AI drafts carry no revision_of chain; order them by their recorded collection
    # time (then Evidence ID) so the choice does not depend on filename order either.
    drafts = [
        (evidence.get("collected_at") or "", evidence.get("evidence_id") or "", path)
        for path, evidence in records
        if evidence.get("task_id") == task_id and evidence.get("evidence_role") == "ai_draft"
    ]
    ai_draft = max(drafts)[2] if drafts else None

    selected = task_revision or ai_draft or original
    try:
        selected.resolve().relative_to(run_dir.resolve())
    except ValueError as exc:
        raise IntegrityError("Claim source artifact escapes the Run directory") from exc
    if selected.is_symlink() or not selected.is_file():
        raise IntegrityError(f"Claim source artifact is missing: {selected}")
    return selected, sha256_file(selected), _source_text(selected)


def _evidence_ids(run_dir: Path) -> set[str]:
    result: set[str] = set()
    for evidence_path in sorted((run_dir / "evidence").glob("*.json")):
        evidence = read_json(evidence_path)
        evidence_id = evidence.get("evidence_id") if isinstance(evidence, dict) else None
        if isinstance(evidence_id, str) and evidence_id:
            result.add(evidence_id)
    return result


def _validate_claim(
    claim: Any,
    *,
    index: int,
    expected_id: str,
    source_text: str,
    evidence_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(claim, dict):
        raise IntegrityError(f"claims[{index}] must be an object")
    required = {
        "claim_id",
        "text",
        "text_sha256",
        "locator",
        "kind",
        "evidence_ids",
        "support",
    }
    allowed = required | {"note"}
    missing = sorted(required - set(claim))
    unexpected = sorted(set(claim) - allowed)
    if missing or unexpected:
        raise IntegrityError(
            f"claims[{index}] fields are invalid: missing={missing}; unexpected={unexpected}"
        )
    if claim.get("claim_id") != expected_id:
        raise IntegrityError(f"Claim ID is invalid or duplicated: {claim.get('claim_id')}")
    text = _required_text(claim.get("text"), f"claims[{index}].text", MAX_CLAIM_TEXT_CHARS)
    if claim.get("text_sha256") != sha256_text(text):
        raise IntegrityError(f"Claim text hash mismatch: {expected_id}")
    locator = claim.get("locator")
    if not isinstance(locator, dict) or set(locator) != {"kind", "value"}:
        raise IntegrityError(f"Claim locator is invalid: {expected_id}")
    if locator.get("kind") != "quote" or locator.get("value") != text:
        raise IntegrityError(f"Claim quote locator must equal its verbatim text: {expected_id}")
    if text not in source_text:
        raise IntegrityError(f"Claim quote does not resolve in its source artifact: {expected_id}")
    if claim.get("kind") not in CLAIM_KINDS:
        raise IntegrityError(f"Claim kind is invalid: {expected_id}")
    support = claim.get("support")
    if support not in CLAIM_SUPPORT:
        raise IntegrityError(f"Claim support is invalid: {expected_id}")
    references = claim.get("evidence_ids")
    if (
        not isinstance(references, list)
        or any(not isinstance(item, str) or not item for item in references)
        or len(references) != len(set(references))
    ):
        raise IntegrityError(f"Claim evidence references are invalid: {expected_id}")
    unknown = sorted(set(references) - evidence_ids)
    if unknown:
        raise IntegrityError(f"Claim references unknown Evidence IDs: {expected_id}: {unknown}")
    if support == "unsupported" and references:
        raise IntegrityError(f"Unsupported Claim must not cite Evidence: {expected_id}")
    if support in {"direct", "derived"} and not references:
        raise IntegrityError(f"Supported Claim must cite Evidence: {expected_id}")
    if "note" in claim:
        note = claim["note"]
        if not isinstance(note, str) or len(note) > MAX_CLAIM_NOTE_CHARS:
            raise IntegrityError(f"Claim note is invalid: {expected_id}")
    return claim


def validate_claims_record(
    run_dir: Path,
    record: Any,
    *,
    run_id: str,
    task_ids: list[str],
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise IntegrityError("Claims artifact must be an object")
    expected_fields = {
        "schema_version",
        "run_id",
        "task_id",
        "source_artifact_sha256",
        "confirmed_by",
        "confirmed_at",
        "claims",
        "claims_sha256",
    }
    if set(record) != expected_fields:
        raise IntegrityError(
            "Claims artifact fields are invalid: "
            f"missing={sorted(expected_fields - set(record))}; "
            f"unexpected={sorted(set(record) - expected_fields)}"
        )
    if record.get("schema_version") != CLAIMS_SCHEMA_VERSION:
        raise IntegrityError("Claims artifact has an unsupported schema_version")
    if record.get("run_id") != run_id:
        raise IntegrityError("Claims artifact run_id does not match its Run")
    task_id = record.get("task_id")
    if task_id not in task_ids:
        raise IntegrityError("Claims artifact references an unknown Task")
    _sha256(record.get("source_artifact_sha256"), "source_artifact_sha256")
    _required_text(record.get("confirmed_by"), "confirmed_by", MAX_ACTOR_CHARS)
    _confirmed_at(record.get("confirmed_at"))
    source_path, source_hash, source_text = current_task_source(run_dir, task_id)
    if record.get("source_artifact_sha256") != source_hash:
        raise StaleClaimsError(task_id)
    claims = record.get("claims")
    if not isinstance(claims, list) or len(claims) > MAX_CLAIMS_PER_TASK:
        raise IntegrityError("Claims list is invalid or exceeds its limit")
    evidence_ids = _evidence_ids(run_dir)
    seen: set[str] = set()
    kind_counts = {kind: 0 for kind in sorted(CLAIM_KINDS)}
    unsupported = 0
    unsupported_facts = 0
    for index, claim in enumerate(claims):
        expected_id = _claim_id(run_id, task_id, index + 1)
        validated = _validate_claim(
            claim,
            index=index,
            expected_id=expected_id,
            source_text=source_text,
            evidence_ids=evidence_ids,
        )
        claim_id = validated["claim_id"]
        if claim_id in seen:
            raise IntegrityError(f"Claim ID is duplicated: {claim_id}")
        seen.add(claim_id)
        kind_counts[validated["kind"]] += 1
        if validated["support"] == "unsupported":
            unsupported += 1
            if validated["kind"] == "verifiable_fact":
                unsupported_facts += 1
    if record.get("claims_sha256") != claims_digest(claims):
        raise IntegrityError(f"Claims collection hash mismatch: {task_id}")
    return {
        "task_id": task_id,
        "source_artifact": source_path.relative_to(run_dir).as_posix(),
        "source_artifact_sha256": source_hash,
        "confirmed_by": record["confirmed_by"],
        "confirmed_at": record["confirmed_at"],
        "claims_sha256": record["claims_sha256"],
        "claim_count": len(claims),
        "unsupported_claim_count": unsupported,
        "unsupported_fact_count": unsupported_facts,
        "kind_counts": kind_counts,
        "claims_confirmed": len(claims) > 0,
    }


def verify_claims(
    run_dir: Path,
    *,
    run_id: str,
    task_ids: list[str],
    include_records: bool = False,
    tolerate_stale: bool = False,
) -> dict[str, Any]:
    """Verify every Claims artifact in the Run.

    ``tolerate_stale`` is opt-in. When it stays ``False`` the behaviour is unchanged:
    a Claims record bound to a superseded Task output raises ``StaleClaimsError``.
    When set, such records are collected into ``stale_task_ids`` instead, so a caller
    computing coverage can report "needs re-confirmation" without treating an ordinary
    revision workflow as a corrupt Run.
    """
    claims_dir = run_dir / "claims"
    empty: dict[str, Any] = {
        "schema_version": CLAIMS_VIEW_SCHEMA_VERSION,
        "run_id": run_id,
        "claims_confirmed": False,
        "claims_file_count": 0,
        "claim_count": 0,
        "unsupported_claim_count": 0,
        "unsupported_fact_count": 0,
        "kind_counts": {kind: 0 for kind in sorted(CLAIM_KINDS)},
        "stale_task_ids": [],
        "summaries": [],
    }
    if include_records:
        empty["records"] = []
    if not claims_dir.exists():
        return empty
    if claims_dir.is_symlink() or not claims_dir.is_dir():
        raise IntegrityError("Run claims path must be a regular directory")
    entries = sorted(claims_dir.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in entries):
        raise IntegrityError("Run claims directory contains a non-regular file")
    if any(path.suffix.casefold() != ".json" for path in entries):
        raise IntegrityError("Run claims directory contains a non-JSON artifact")
    if len(entries) > len(task_ids):
        raise IntegrityError("Run contains more Claims artifacts than Tasks")

    summaries: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    seen_tasks: set[str] = set()
    stale_task_ids: list[str] = []
    for path in entries:
        if path.stat().st_size > MAX_CLAIMS_FILE_BYTES:
            raise IntegrityError(f"Claims artifact exceeds 4 MiB: {path}")
        record = read_json(path)
        task_id = record.get("task_id") if isinstance(record, dict) else None
        if not isinstance(task_id, str):
            raise IntegrityError(f"Claims artifact has no Task identity: {path}")
        if path != claims_artifact_path(run_dir, task_id):
            raise IntegrityError(f"Claims artifact filename does not match task_id: {path}")
        if task_id in seen_tasks:
            raise IntegrityError(f"Multiple Claims artifacts exist for Task: {task_id}")
        seen_tasks.add(task_id)
        try:
            summary = validate_claims_record(
                run_dir,
                record,
                run_id=run_id,
                task_ids=task_ids,
            )
        except StaleClaimsError:
            if not tolerate_stale:
                raise
            stale_task_ids.append(task_id)
            continue
        summaries.append(summary)
        if include_records:
            records.append(record)

    aggregate_kinds = {kind: 0 for kind in sorted(CLAIM_KINDS)}
    for summary in summaries:
        for kind, count in summary["kind_counts"].items():
            aggregate_kinds[kind] += count
    claim_count = sum(item["claim_count"] for item in summaries)
    result = {
        **empty,
        "claims_confirmed": bool(summaries) and claim_count > 0,
        "claims_file_count": len(summaries),
        "claim_count": claim_count,
        "unsupported_claim_count": sum(
            item["unsupported_claim_count"] for item in summaries
        ),
        "unsupported_fact_count": sum(
            item["unsupported_fact_count"] for item in summaries
        ),
        "kind_counts": aggregate_kinds,
        "stale_task_ids": sorted(stale_task_ids),
        "summaries": summaries,
    }
    if include_records:
        result["records"] = records
    return result


def claims_coverage(
    view: dict[str, Any],
    executed_tasks: list[str],
) -> dict[str, Any]:
    """Per-Task confirmation coverage over the Tasks that actually executed.

    The denominator is ``executed_tasks`` — the Run state's authoritative, ordered-prefix
    list — not every Task declared by the Pack. Using the Pack's list would leave a Run
    permanently uncovered simply because later Tasks have not run yet.

    The four task buckets are disjoint:

    ``tasks_confirmed``          artifact present, at least one Claim, bound to the current output
    ``tasks_with_empty_claims``  artifact present but it confirms zero Claims
    ``tasks_with_stale_claims``  artifact present but bound to a superseded Task output
    ``tasks_missing_claims``     executed Task with no Claims artifact at all

    Only ``tasks_confirmed`` satisfies Task confirmation coverage. Claim reference
    coverage uses two separate denominators: ``fact_coverage`` covers only
    ``verifiable_fact`` Claims, while ``all_coverage`` covers every Claim. Both derive
    support from the validated ``support`` field, never directly from ``evidence_ids``.
    This function is read-only and gates nothing.
    """
    confirmed: set[str] = set()
    empty_claims: set[str] = set()
    for summary in view.get("summaries", []):
        task_id = summary["task_id"]
        if summary["claim_count"] > 0:
            confirmed.add(task_id)
        else:
            empty_claims.add(task_id)
    stale = set(view.get("stale_task_ids", []))
    accounted = confirmed | empty_claims | stale

    executed = list(executed_tasks)
    missing = [task_id for task_id in executed if task_id not in accounted]
    kind_counts = {
        kind: int(view.get("kind_counts", {}).get(kind, 0))
        for kind in sorted(CLAIM_KINDS)
    }
    claim_count = int(view.get("claim_count", 0))
    unsupported_claim_count = int(view.get("unsupported_claim_count", 0))
    unsupported_fact_count = int(view.get("unsupported_fact_count", 0))
    verifiable_fact_count = kind_counts["verifiable_fact"]
    supported_fact_count = verifiable_fact_count - unsupported_fact_count
    supported_claim_count = claim_count - unsupported_claim_count
    return {
        "schema_version": CLAIMS_COVERAGE_SCHEMA_VERSION,
        "executed_task_count": len(executed),
        "confirmed_task_count": sum(1 for task_id in executed if task_id in confirmed),
        "tasks_confirmed": [t for t in executed if t in confirmed],
        "tasks_with_empty_claims": [t for t in executed if t in empty_claims],
        "tasks_with_stale_claims": [t for t in executed if t in stale],
        "tasks_missing_claims": missing,
        "all_executed_tasks_confirmed": bool(executed)
        and all(task_id in confirmed for task_id in executed),
        "claim_count": claim_count,
        "supported_claim_count": supported_claim_count,
        "unsupported_claim_count": unsupported_claim_count,
        "verifiable_fact_count": verifiable_fact_count,
        "supported_fact_count": supported_fact_count,
        "unsupported_fact_count": unsupported_fact_count,
        "hard_gate_pass": unsupported_fact_count == 0,
        "fact_coverage": (
            supported_fact_count / verifiable_fact_count
            if verifiable_fact_count
            else None
        ),
        "all_coverage": (
            supported_claim_count / claim_count if claim_count else None
        ),
        "kind_counts": kind_counts,
    }


def task_claims_coverage(view: dict[str, Any], task_id: str) -> dict[str, Any]:
    """Return the S2/S3 coverage metrics for exactly one Task.

    The Run-level view aggregates Claim counts across Tasks. A resume gate must not
    consume those aggregates because older Tasks are outside the pending gate. This
    adapter isolates one verified summary and then delegates all arithmetic to
    ``claims_coverage`` so the S3 definitions cannot drift between reporting and gates.
    """
    summary = next(
        (
            item
            for item in view.get("summaries", [])
            if item.get("task_id") == task_id
        ),
        None,
    )
    task_view: dict[str, Any] = {
        "summaries": [summary] if summary is not None else [],
        "stale_task_ids": (
            [task_id] if task_id in view.get("stale_task_ids", []) else []
        ),
        "claim_count": 0,
        "unsupported_claim_count": 0,
        "unsupported_fact_count": 0,
        "kind_counts": {kind: 0 for kind in sorted(CLAIM_KINDS)},
    }
    if summary is not None:
        task_view.update(
            {
                "claim_count": summary["claim_count"],
                "unsupported_claim_count": summary["unsupported_claim_count"],
                "unsupported_fact_count": summary["unsupported_fact_count"],
                "kind_counts": summary["kind_counts"],
            }
        )
    return claims_coverage(task_view, [task_id])
