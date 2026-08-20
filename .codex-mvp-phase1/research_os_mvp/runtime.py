from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_os_mvp.claims import (
    StaleClaimsError,
    build_claims_record,
    claims_artifact_path,
    claims_coverage,
    current_task_source,
    task_claims_coverage,
    validate_claims_record,
    verify_claims,
)
from research_os_mvp.errors import (
    IntegrityError,
    RunStateError,
    SignatureError,
    TrustPolicyError,
)
from research_os_mvp.integrity import (
    ZERO_HASH,
    append_chained_record,
    canonical_json_text,
    read_json,
    sha256_file,
    sha256_text,
    utc_now,
    verify_chained_log,
    verify_hash_manifest,
    write_hash_manifest,
    write_json_atomic,
    write_text_atomic,
)
from research_os_mvp.pack import load_pack, validate_run_id
from research_os_mvp.revisions import (
    RevisionChainError,
    latest_revision,
    resolve_revision_chain,
)
from research_os_mvp.run_store import (
    CHECKPOINT_SCHEMA_VERSION,
    run_lock,
    sync_checkpoint,
)
from research_os_mvp.signing import (
    ed25519_public_key_fingerprint,
    load_ed25519_public_key,
    normalize_ed25519_public_key,
    normalize_signer_identity,
    normalize_ssh_signature,
    sign_ssh_payload,
    verify_ssh_signature,
)
from research_os_mvp.trust import (
    evaluate_reviewer_trust,
    review_trust_result,
    validate_registry_task_scope,
    validate_reviewer_trust_registry,
)

STATE_FILE = "state.json"
EVENTS_FILE = "events.jsonl"
APPROVALS_FILE = "approvals.jsonl"
REVIEWS_FILE = "reviews.jsonl"
REVIEW_SIGNATURES_FILE = "review-signatures.jsonl"
PACK_SNAPSHOT = "pack.snapshot.json"
REVIEWER_TRUST_SNAPSHOT = "reviewer-trust.snapshot.json"
REVIEW_DECISIONS = {"Approved", "Changes Requested", "Rejected"}
ALLOWED_RUN_STATUSES = {
    "running",
    "paused",
    "approved_pending_resume",
    "completed",
    "cancelled",
    "rejected",
}
MAX_SUPPLEMENTAL_EVIDENCE = 20
MAX_SUPPLEMENTAL_CONTENT_CHARS = 600_000
MAX_REVIEW_DECISIONS = 100
MAX_REVIEW_SIGNATURES = 100
TASK_OUTPUT_REVISION_ROLE = "task_output_revision"
MAX_TASK_OUTPUT_REVISION_NOTE_CHARS = 800
EFFECTIVE_OUTPUT_MANIFEST_SCHEMA = "research-os-mvp-effective-outputs/0.2"
LEGACY_EFFECTIVE_OUTPUT_MANIFEST_SCHEMA = "research-os-mvp-effective-outputs/0.1"
EFFECTIVE_OUTPUT_RESOLUTION_RULE = (
    "latest-policy-satisfied-approved-review-subject-revision/2"
)
MAX_SNAPSHOT_ARTIFACT_BYTES = 4 * 1024 * 1024
REVIEW_SIGNATURE_SCHEMA = "research-os-mvp-review-signature/0.1"
REVIEW_SIGNATURE_PAYLOAD_SCHEMA = "research-os-mvp-review-signature-payload/0.1"
REVIEW_SIGNATURE_NAMESPACE = "research-os-review"
EFFECTIVE_MANIFEST_SIGNATURE_SCHEMA = (
    "research-os-mvp-effective-manifest-signature/0.1"
)
EFFECTIVE_MANIFEST_SIGNATURE_PAYLOAD_SCHEMA = (
    "research-os-mvp-effective-manifest-signature-payload/0.1"
)
EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE = "research-os-effective-manifest"


def _verified_checkpointed_status(run_dir: Path) -> dict[str, Any]:
    status = _verify_run_unlocked(run_dir)
    sync_checkpoint(run_dir, status)
    return {
        **status,
        "checkpoint": "current",
        "checkpoint_schema_version": CHECKPOINT_SCHEMA_VERSION,
    }


def _finalize_run_update(run_dir: Path) -> dict[str, Any]:
    write_hash_manifest(run_dir)
    return _verified_checkpointed_status(run_dir)


def _new_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dt%H%M%Sz").lower()
    return f"run-{timestamp}-{uuid.uuid4().hex[:8]}"


def _load_state(run_dir: Path) -> dict[str, Any]:
    state = read_json(run_dir / STATE_FILE)
    if not isinstance(state, dict):
        raise IntegrityError("state.json must contain an object")
    return state


def _write_state(run_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    write_json_atomic(run_dir / STATE_FILE, state)


def _append_event(
    run_dir: Path,
    event_type: str,
    *,
    actor: str,
    task_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "at": utc_now(),
        "actor": actor,
        "type": event_type,
        "task_id": task_id,
        "details": details or {},
    }
    return append_chained_record(run_dir / EVENTS_FILE, payload)


def _set_event_tail(state: dict[str, Any], record: dict[str, Any]) -> None:
    state["event_tail_hash"] = record["hash"]


def _safe_component(value: str) -> str:
    component = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not component:
        raise RunStateError(f"Identifier cannot produce a safe artifact name: {value}")
    return component


def _artifact_relative(run_dir: Path, artifact: Path) -> str:
    return artifact.relative_to(run_dir).as_posix()


def _read_review_records(run_dir: Path) -> tuple[int, str, list[dict[str, Any]]]:
    review_path = run_dir / REVIEWS_FILE
    count, tail = verify_chained_log(review_path)
    if count > MAX_REVIEW_DECISIONS:
        raise IntegrityError("Reviewer decision count exceeds the Run limit")
    if count == 0:
        return count, tail, []
    records: list[dict[str, Any]] = []
    try:
        with review_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise IntegrityError("Reviewer decision record must be an object")
                records.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Cannot read Reviewer decision chain: {exc}") from exc
    return count, tail, records


def _read_review_signature_records(
    run_dir: Path,
) -> tuple[int, str, list[dict[str, Any]]]:
    signature_path = run_dir / REVIEW_SIGNATURES_FILE
    count, tail = verify_chained_log(signature_path)
    if count > MAX_REVIEW_SIGNATURES:
        raise IntegrityError("Reviewer signature count exceeds the Run limit")
    if count == 0:
        return count, tail, []
    records: list[dict[str, Any]] = []
    try:
        with signature_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise IntegrityError("Reviewer signature record must be an object")
                records.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Cannot read Reviewer signature chain: {exc}") from exc
    return count, tail, records


def _load_bound_reviewer_trust_registry(
    run_dir: Path,
    state: dict[str, Any],
    task_ids: list[str],
) -> dict[str, Any] | None:
    snapshot_path = run_dir / REVIEWER_TRUST_SNAPSHOT
    state_snapshot_hash = state.get("reviewer_trust_snapshot_sha256")
    state_registry_hash = state.get("reviewer_trust_registry_sha256")
    if not snapshot_path.exists():
        if state_snapshot_hash is not None or state_registry_hash is not None:
            raise IntegrityError(
                "Reviewer trust state exists without its immutable policy snapshot"
            )
        return None
    if snapshot_path.is_symlink() or not snapshot_path.is_file():
        raise IntegrityError("Reviewer trust policy snapshot must be a regular file")
    if state_snapshot_hash != sha256_file(snapshot_path):
        raise IntegrityError("Reviewer trust policy snapshot Hash does not match state.json")
    try:
        registry = validate_reviewer_trust_registry(read_json(snapshot_path))
        validate_registry_task_scope(registry, task_ids)
    except TrustPolicyError as exc:
        raise IntegrityError(f"Reviewer trust policy snapshot is invalid: {exc}") from exc
    if state_registry_hash != registry["registry_sha256"]:
        raise IntegrityError("Reviewer trust registry Hash does not match state.json")
    return registry


def _reviewer_trust_evaluation(
    run_dir: Path,
    state: dict[str, Any],
    task_ids: list[str],
    reviews: list[dict[str, Any]],
    signatures: list[dict[str, Any]],
) -> dict[str, Any]:
    registry = _load_bound_reviewer_trust_registry(run_dir, state, task_ids)
    if registry is None:
        return {
            "policy_bound": False,
            "satisfied": True,
            "reviews": [],
        }
    try:
        return evaluate_reviewer_trust(registry, reviews, signatures)
    except TrustPolicyError as exc:
        raise IntegrityError(f"Reviewer trust evaluation failed: {exc}") from exc


def _review_subject(run_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    task_id = state.get("pending_task_id")
    pending_output = state.get("pending_output")
    if not isinstance(task_id, str) or not isinstance(pending_output, dict):
        raise RunStateError("Run is not paused with a reviewable Task output")

    # NOTE: the order of `supplemental` feeds `bundle_sha256`. It must stay in
    # filename order so existing Review subjects keep their recorded hash. Only the
    # *selection* of the latest revision/draft below is order-independent.
    supplemental: list[dict[str, Any]] = []
    latest_fallback_id: str | None = None
    revisions: list[dict[str, Any]] = []
    drafts: list[tuple[str, str]] = []
    for evidence_path in sorted((run_dir / "evidence").glob("*.json")):
        evidence = read_json(evidence_path)
        if (
            not isinstance(evidence, dict)
            or evidence.get("task_id") != task_id
            or evidence.get("evidence_role") is None
        ):
            continue
        reference = {
            "evidence_id": evidence["evidence_id"],
            "path": _artifact_relative(run_dir, evidence_path),
            "sha256": sha256_file(evidence_path),
            "content_sha256": evidence["content_sha256"],
            "role": evidence["evidence_role"],
            "revision_of": evidence.get("revision_of"),
            "review_decision_hash": evidence.get("review_decision_hash"),
        }
        supplemental.append(reference)
        latest_fallback_id = evidence["evidence_id"]
        if evidence.get("evidence_role") == "ai_draft":
            drafts.append(
                (str(evidence.get("collected_at") or ""), str(evidence["evidence_id"]))
            )
        if evidence.get("evidence_role") == TASK_OUTPUT_REVISION_ROLE:
            revisions.append(evidence)

    base_output_id = pending_output.get("id")
    latest_task_output_revision_id: str | None = None
    if revisions and isinstance(base_output_id, str) and base_output_id:
        newest = latest_revision(
            revisions,
            task_id=task_id,
            base_output_id=base_output_id,
        )
        latest_task_output_revision_id = newest["evidence_id"] if newest else None
    elif revisions:
        latest_task_output_revision_id = revisions[-1]["evidence_id"]
    latest_revision_id = max(drafts)[1] if drafts else None

    subject: dict[str, Any] = {
        "schema_version": "research-os-mvp-review-subject/0.1",
        "task_id": task_id,
        "task_output": dict(pending_output),
        "supplemental_evidence": supplemental,
        "latest_revision_id": (
            latest_task_output_revision_id or latest_revision_id or latest_fallback_id
        ),
    }
    subject["bundle_sha256"] = sha256_text(canonical_json_text(subject))
    return subject


def _record_evidence(
    run_dir: Path,
    state: dict[str, Any],
    task: dict[str, Any],
    task_index: int,
) -> dict[str, Any]:
    task_input = task["input"]
    content = task_input["content"]
    evidence_id = f"EVID-MVP-{state['run_id']}-{task_index + 1:02d}"
    evidence = {
        "schema_version": "research-os-mvp-evidence/0.1",
        "evidence_id": evidence_id,
        "run_id": state["run_id"],
        "pack_id": state["pack_id"],
        "mission_id": state["mission_id"],
        "task_id": task["task_id"],
        "collected_at": utc_now(),
        "collected_by": "MVP Runtime",
        "source": task_input["source"],
        "method": task_input["method"],
        "content": content,
        "content_sha256": sha256_text(content),
        "limitations": task_input["limitations"],
    }
    artifact = run_dir / "evidence" / (
        f"EVID-{task_index + 1:02d}-{_safe_component(task['task_id'])}.json"
    )
    if artifact.exists():
        raise RunStateError(f"Evidence artifact already exists: {artifact}")
    write_json_atomic(artifact, evidence)
    return {
        "class": "Evidence",
        "path": _artifact_relative(run_dir, artifact),
        "sha256": sha256_file(artifact),
        "id": evidence_id,
    }


def _compose_report(
    run_dir: Path,
    state: dict[str, Any],
    pack: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    evidence_files = sorted((run_dir / "evidence").glob("*.json"))
    if not evidence_files:
        raise RunStateError("compose_report requires at least one Evidence artifact")
    evidence_rows: list[dict[str, Any]] = []
    for evidence_file in evidence_files:
        evidence = read_json(evidence_file)
        if not isinstance(evidence, dict):
            raise IntegrityError(f"Evidence must be an object: {evidence_file}")
        evidence_rows.append(evidence)

    ai_sources = [
        str(evidence["source"])
        for evidence in evidence_rows
        if str(evidence["source"]).startswith("ollama://")
    ]
    ai_draft_count = sum(
        1 for evidence in evidence_rows if evidence.get("evidence_role") == "ai_draft"
    )
    ai_audit_count = sum(
        1 for evidence in evidence_rows if evidence.get("evidence_role") == "ai_audit"
    )
    research_sources = [
        str(evidence["source"])
        for evidence in evidence_rows
        if not str(evidence["source"]).startswith(
            ("human://natural-language-request", "template://", "ollama://")
        )
    ]
    if research_sources:
        readiness = "已有外部或实测证据，仍需人工复核后形成结论"
    elif ai_sources:
        readiness = "已有本地 AI 分析草稿，引用事实仍待原始来源复核"
    else:
        readiness = "尚未就绪：当前只有用户目标和本地研究模板"

    title = task["input"]["title"]
    lines = [
        f"# {title}",
        "",
        "**Status:** Research Preparation",
        f"**Run-ID:** `{state['run_id']}`",
        f"**Pack-ID:** `{state['pack_id']}`",
        f"**Pack SHA-256:** `{state['pack_sha256']}`",
        f"**Mission-ID:** `{state['mission_id']}`",
        f"**Generated-At:** {utc_now()}",
        "",
        "## Mission",
        "",
        pack["mission"]["title"],
        "",
        "## Research Readiness",
        "",
        f"**决策就绪度：** {readiness}",
        "",
        (
            "本报告用于建立范围、评估框架和证据缺口；在补充真实来源、"
            "测量数据或可复现实验前，它不是候选方案比较结论。"
        ),
        "",
        "## Evidence",
        "",
        "| Evidence ID | Source | Content SHA-256 | Observation |",
        "|---|---|---|---|",
    ]
    for evidence in evidence_rows:
        observation = str(evidence["content"]).replace("|", "\\|").replace("\n", " ")
        if len(observation) > 2_000:
            observation = observation[:2_000] + "… [报告中截断，完整内容见 Evidence]"
        source = str(evidence["source"]).replace("|", "\\|")
        lines.append(
            f"| `{evidence['evidence_id']}` | {source} | "
            f"`{evidence['content_sha256']}` | {observation} |"
        )
    lines.extend(
        [
            "",
            "## Success Criteria",
            "",
            *[f"- {item}" for item in pack["mission"]["success_criteria"]],
            "",
            "## Limitations",
            "",
            *[f"- {item['limitations']}" for item in evidence_rows],
            (
                "- This report is generated by an isolated prototype and has no "
                "Foundation approval status."
            ),
            "",
        ]
    )
    report_text = "\n".join(lines)
    report = run_dir / "reports" / (
        f"REPORT-MISSION-{_safe_component(state['mission_id'])}.md"
    )
    if report.exists():
        raise RunStateError(f"Mission Report already exists: {report}")
    write_text_atomic(report, report_text)
    return {
        "class": "Report",
        "path": _artifact_relative(run_dir, report),
        "sha256": sha256_file(report),
        "id": f"REPORT-MVP-{state['mission_id']}",
        "research_source_count": len(research_sources),
        "ai_draft_count": ai_draft_count,
        "ai_audit_count": ai_audit_count,
        "decision_ready": False,
    }


def _write_task_report(
    run_dir: Path,
    state: dict[str, Any],
    task: dict[str, Any],
    task_index: int,
    output: dict[str, Any],
) -> dict[str, Any]:
    report = {
        "schema_version": "research-os-mvp-task-report/0.1",
        "report_id": f"REPORT-MVP-{state['run_id']}-{task_index + 1:02d}",
        "run_id": state["run_id"],
        "pack_id": state["pack_id"],
        "mission_id": state["mission_id"],
        "task_id": task["task_id"],
        "task_name": task["name"],
        "operation": task["operation"],
        "gate_status_at_generation": "Pending Human Approval",
        "generated_at": utc_now(),
        "output": output,
    }
    artifact = run_dir / "reports" / f"TASK-REPORT-{task_index + 1:02d}.json"
    if artifact.exists():
        raise RunStateError(f"Task Report already exists: {artifact}")
    write_json_atomic(artifact, report)
    return {
        "class": "Task Report",
        "path": _artifact_relative(run_dir, artifact),
        "sha256": sha256_file(artifact),
        "id": report["report_id"],
    }


def _execute_current_task(
    run_dir: Path, state: dict[str, Any], pack: dict[str, Any]
) -> dict[str, Any]:
    if state["status"] != "running":
        raise RunStateError("Runtime must be running before executing a Task")
    task_index = state["next_task_index"]
    tasks = pack["mission"]["tasks"]
    if task_index >= len(tasks):
        raise RunStateError("No Task remains to execute")
    task = tasks[task_index]

    started = _append_event(
        run_dir,
        "task_started",
        actor="MVP Runtime",
        task_id=task["task_id"],
        details={"task_index": task_index, "operation": task["operation"]},
    )
    _set_event_tail(state, started)

    if task["operation"] == "record_evidence":
        output = _record_evidence(run_dir, state, task, task_index)
        artifact_event = _append_event(
            run_dir,
            "evidence_recorded",
            actor="MVP Runtime",
            task_id=task["task_id"],
            details=output,
        )
    elif task["operation"] == "compose_report":
        output = _compose_report(run_dir, state, pack, task)
        artifact_event = _append_event(
            run_dir,
            "report_generated",
            actor="MVP Runtime",
            task_id=task["task_id"],
            details=output,
        )
    else:
        raise RunStateError(f"Unsupported operation: {task['operation']}")
    _set_event_tail(state, artifact_event)

    task_report = _write_task_report(run_dir, state, task, task_index, output)
    completed = _append_event(
        run_dir,
        "task_completed",
        actor="MVP Runtime",
        task_id=task["task_id"],
        details={"output": output, "task_report": task_report},
    )
    _set_event_tail(state, completed)

    approval_required = _append_event(
        run_dir,
        "approval_required",
        actor="MVP Runtime",
        task_id=task["task_id"],
        details={"gate": f"human-gate-{task_index + 1:02d}"},
    )
    _set_event_tail(state, approval_required)
    state["status"] = "paused"
    state["pending_task_id"] = task["task_id"]
    state["pending_output"] = output
    state["executed_tasks"].append(task["task_id"])
    _write_state(run_dir, state)
    return _finalize_run_update(run_dir)


def create_run(
    pack_path: Path | str,
    runs_dir: Path | str,
    run_id: str | None = None,
    *,
    reviewer_trust_registry: Any | None = None,
    reviewer_trust_actor: str | None = None,
    claims_gate_enabled: bool = False,
    claims_gate_actor: str | None = None,
) -> dict[str, Any]:
    loaded = load_pack(pack_path)
    task_ids = [task["task_id"] for task in loaded.data["mission"]["tasks"]]
    normalized_registry: dict[str, Any] | None = None
    normalized_actor: str | None = None
    if reviewer_trust_registry is None:
        if reviewer_trust_actor is not None:
            raise RunStateError(
                "reviewer_trust_actor requires a Reviewer trust registry"
            )
    else:
        if reviewer_trust_actor is None:
            raise RunStateError(
                "Reviewer trust registry requires an explicit binding actor"
            )
        try:
            normalized_registry = validate_reviewer_trust_registry(
                reviewer_trust_registry
            )
            validate_registry_task_scope(normalized_registry, task_ids)
        except TrustPolicyError as exc:
            raise RunStateError(str(exc)) from exc
        normalized_actor = reviewer_trust_actor.strip()
        if not normalized_actor or len(normalized_actor) > 100:
            raise RunStateError(
                "Trust-policy actor must be 1-100 non-whitespace characters"
            )
    if not isinstance(claims_gate_enabled, bool):
        raise RunStateError("claims_gate_enabled must be a boolean")
    normalized_claims_gate_actor: str | None = None
    if claims_gate_enabled:
        if claims_gate_actor is None:
            raise RunStateError("Claims gate requires an explicit binding actor")
        normalized_claims_gate_actor = claims_gate_actor.strip()
        if (
            not normalized_claims_gate_actor
            or len(normalized_claims_gate_actor) > 100
        ):
            raise RunStateError(
                "Claims-gate actor must be 1-100 non-whitespace characters"
            )
    elif claims_gate_actor is not None:
        raise RunStateError("claims_gate_actor requires claims_gate_enabled=True")
    selected_run_id = run_id or _new_run_id()
    validate_run_id(selected_run_id)
    runs_root = Path(runs_dir)
    if runs_root.exists() and runs_root.is_symlink():
        raise RunStateError("runs_dir must not be a symlink")
    runs_root.mkdir(parents=True, exist_ok=True)
    run_dir = runs_root / selected_run_id
    try:
        run_dir.mkdir()
    except FileExistsError:
        raise RunStateError(f"Run directory already exists: {run_dir}")
    with run_lock(run_dir):
        (run_dir / "evidence").mkdir()
        (run_dir / "reports").mkdir()
        write_json_atomic(run_dir / PACK_SNAPSHOT, loaded.data)

        started_at = utc_now()
        state: dict[str, Any] = {
            "schema_version": "research-os-mvp-run-state/0.1",
            "run_id": selected_run_id,
            "pack_id": loaded.data["pack_id"],
            "pack_sha256": loaded.canonical_sha256,
            "mission_id": loaded.data["mission"]["mission_id"],
            "status": "running",
            "next_task_index": 0,
            "pending_task_id": None,
            "pending_output": None,
            "executed_tasks": [],
            "approved_tasks": [],
            "supplemental_evidence_count": 0,
            "event_tail_hash": ZERO_HASH,
            "approval_tail_hash": ZERO_HASH,
            "review_tail_hash": ZERO_HASH,
            "review_signature_tail_hash": ZERO_HASH,
            "claims_gate_enabled": False,
            "claims_gate_from_task_index": None,
            "started_at": started_at,
            "updated_at": started_at,
        }
        created = _append_event(
            run_dir,
            "run_created",
            actor="MVP Runtime",
            details={
                "pack_id": state["pack_id"],
                "pack_sha256": state["pack_sha256"],
                "mission_id": state["mission_id"],
                "task_count": 3,
            },
        )
        _set_event_tail(state, created)
        if normalized_registry is not None and normalized_actor is not None:
            _write_reviewer_trust_snapshot_unlocked(
                run_dir,
                state,
                normalized_registry,
                actor=normalized_actor,
                task_id=task_ids[0],
            )
        if normalized_claims_gate_actor is not None:
            _enable_claims_gate_unlocked(
                run_dir,
                state,
                actor=normalized_claims_gate_actor,
                effective_from_task_index=0,
                task_ids=task_ids,
            )
        _write_state(run_dir, state)
        _finalize_run_update(run_dir)
        return _execute_current_task(run_dir, state, loaded.data)


def _write_reviewer_trust_snapshot_unlocked(
    run_dir: Path,
    state: dict[str, Any],
    registry: dict[str, Any],
    *,
    actor: str,
    task_id: str,
) -> None:
    snapshot_path = run_dir / REVIEWER_TRUST_SNAPSHOT
    if snapshot_path.exists():
        raise RunStateError("Run already has a Reviewer trust policy")
    write_json_atomic(snapshot_path, registry)
    snapshot_hash = sha256_file(snapshot_path)
    state["reviewer_trust_registry_sha256"] = registry["registry_sha256"]
    state["reviewer_trust_snapshot_sha256"] = snapshot_hash
    event = _append_event(
        run_dir,
        "reviewer_trust_policy_bound",
        actor=actor,
        task_id=task_id,
        details={
            "registry_id": registry["registry_id"],
            "registry_version": registry["version"],
            "registry_sha256": registry["registry_sha256"],
            "snapshot_sha256": snapshot_hash,
        },
    )
    _set_event_tail(state, event)


def bind_reviewer_trust_registry(
    run_dir: Path | str,
    registry: Any,
    *,
    actor: str,
) -> dict[str, Any]:
    """Bind one sealed Reviewer trust registry before the first decision."""
    try:
        normalized = validate_reviewer_trust_registry(registry)
    except TrustPolicyError as exc:
        raise RunStateError(str(exc)) from exc
    cleaned_actor = actor.strip()
    if not cleaned_actor or len(cleaned_actor) > 100:
        raise RunStateError("Trust-policy actor must be 1-100 non-whitespace characters")

    path = Path(run_dir)
    with run_lock(path):
        _verify_run_unlocked(path)
        state = _load_state(path)
        loaded = load_pack(path / PACK_SNAPSHOT)
        task_ids = [task["task_id"] for task in loaded.data["mission"]["tasks"]]
        try:
            validate_registry_task_scope(normalized, task_ids)
        except TrustPolicyError as exc:
            raise RunStateError(str(exc)) from exc

        snapshot_path = path / REVIEWER_TRUST_SNAPSHOT
        if snapshot_path.exists():
            if state.get("reviewer_trust_registry_sha256") == normalized[
                "registry_sha256"
            ]:
                return _verified_checkpointed_status(path)
            raise RunStateError("Run already has a different Reviewer trust policy")
        review_count, _, _ = _read_review_records(path)
        signature_count, _, _ = _read_review_signature_records(path)
        if review_count or signature_count:
            raise RunStateError(
                "Reviewer trust policy must be bound before the first decision or signature"
            )
        if (
            state["status"] != "paused"
            or state["next_task_index"] != 0
            or state["approved_tasks"]
        ):
            raise RunStateError("Run must be paused at its first human gate before binding")

        _write_reviewer_trust_snapshot_unlocked(
            path,
            state,
            normalized,
            actor=cleaned_actor,
            task_id=state["pending_task_id"],
        )
        _write_state(path, state)
        return _finalize_run_update(path)


def _enable_claims_gate_unlocked(
    run_dir: Path,
    state: dict[str, Any],
    *,
    actor: str,
    effective_from_task_index: int,
    task_ids: list[str],
) -> None:
    if state.get("claims_gate_enabled", False):
        raise RunStateError("Run already has the Claims gate enabled")
    if not 0 <= effective_from_task_index < len(task_ids):
        raise RunStateError("Claims gate has no future Task on which it can take effect")
    effective_task_id = task_ids[effective_from_task_index]
    state["claims_gate_enabled"] = True
    state["claims_gate_from_task_index"] = effective_from_task_index
    event = _append_event(
        run_dir,
        "claims_gate_bound",
        actor=actor,
        task_id=effective_task_id,
        details={
            "effective_from_task_index": effective_from_task_index,
            "effective_from_task_id": effective_task_id,
        },
    )
    _set_event_tail(state, event)


def bind_claims_gate(
    run_dir: Path | str,
    *,
    actor: str,
) -> dict[str, Any]:
    """Enable the Claims gate for future Tasks in an existing Run.

    The currently pending Task was executed before this binding event, so a late
    binding starts with the next Task. Creation-time binding uses index zero and is
    therefore the way to gate Task 1.
    """
    cleaned_actor = actor.strip()
    if not cleaned_actor or len(cleaned_actor) > 100:
        raise RunStateError("Claims-gate actor must be 1-100 non-whitespace characters")

    path = Path(run_dir)
    with run_lock(path):
        verified = _verify_run_unlocked(path)
        if verified["claims_gate_enabled"]:
            return _verified_checkpointed_status(path)
        state = _load_state(path)
        if state["status"] not in {"paused", "approved_pending_resume"}:
            raise RunStateError(
                "Claims gate can only be bound while a Run is at a human gate"
            )
        loaded = load_pack(path / PACK_SNAPSHOT)
        task_ids = [
            task["task_id"] for task in loaded.data["mission"]["tasks"]
        ]
        _enable_claims_gate_unlocked(
            path,
            state,
            actor=cleaned_actor,
            effective_from_task_index=state["next_task_index"] + 1,
            task_ids=task_ids,
        )
        _write_state(path, state)
        return _finalize_run_update(path)


def reviewer_trust_status(run_dir: Path | str) -> dict[str, Any]:
    """Return the verified trust-policy evaluation for one Run."""
    status = verify_run(run_dir)
    return {
        "run_id": status["run_id"],
        "run_status": status["status"],
        "policy_bound": status["reviewer_trust_policy_bound"],
        "satisfied": status["reviewer_trust_satisfied"],
        "registry_id": status.get("reviewer_trust_registry_id"),
        "registry_version": status.get("reviewer_trust_registry_version"),
        "registry_sha256": status.get("reviewer_trust_registry_sha256"),
        "snapshot_sha256": status.get("reviewer_trust_snapshot_sha256"),
        "reviews": status["reviewer_trust_reviews"],
        "integrity": status["integrity"],
    }


def record_supplemental_evidence(
    run_dir: Path | str,
    *,
    content: str,
    source: str,
    method: str,
    limitations: str,
    collected_by: str,
    evidence_role: str,
    revision_of: str | None = None,
    review_decision_hash: str | None = None,
) -> dict[str, Any]:
    """Append human-reviewable Evidence while Task 2 is paused."""
    path = Path(run_dir)
    with run_lock(path):
        return _record_supplemental_evidence_unlocked(
            path,
            content=content,
            source=source,
            method=method,
            limitations=limitations,
            collected_by=collected_by,
            evidence_role=evidence_role,
            revision_of=revision_of,
            review_decision_hash=review_decision_hash,
            allow_any_paused_task=False,
        )


def record_confirmed_claims(
    run_dir: Path | str,
    *,
    task_id: str,
    confirmed_by: str,
    confirmed_at: str,
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    """Persist an audited human-confirmed Claim set for one executed Task."""
    path = Path(run_dir)
    with run_lock(path):
        stale_task_id: str | None = None
        try:
            _verify_run_unlocked(path)
        except StaleClaimsError as exc:
            if exc.task_id != task_id:
                raise
            stale_task_id = exc.task_id
        state = _load_state(path)
        pack = load_pack(path / PACK_SNAPSHOT).data
        task_ids = [task["task_id"] for task in pack["mission"]["tasks"]]
        if task_id not in state["executed_tasks"]:
            raise RunStateError("Claims can only be recorded for an executed Task")
        _, source_hash, _ = current_task_source(path, task_id)
        record = build_claims_record(
            run_id=state["run_id"],
            task_id=task_id,
            source_artifact_sha256=source_hash,
            confirmed_by=confirmed_by,
            confirmed_at=confirmed_at,
            claims=claims,
        )
        summary = validate_claims_record(
            path,
            record,
            run_id=state["run_id"],
            task_ids=task_ids,
        )
        artifact = claims_artifact_path(path, task_id)
        previous_record: dict[str, Any] | None = None
        previous_artifact_sha256: str | None = None
        if artifact.exists() or artifact.is_symlink():
            if artifact.is_symlink() or not artifact.is_file():
                raise RunStateError(f"Claims artifact path is not a regular file: {artifact}")
            loaded_record = read_json(artifact)
            if not isinstance(loaded_record, dict):
                raise IntegrityError("Existing Claims artifact must be an object")
            if loaded_record == record:
                status = _verified_checkpointed_status(path)
                return {
                    **status,
                    "claims_artifact": _artifact_relative(path, artifact),
                    "recorded_claims": summary,
                    "idempotent": True,
                    "reconfirmed": False,
                }
            previous_record = loaded_record
            previous_artifact_sha256 = sha256_file(artifact)

        write_json_atomic(artifact, record)
        event_type = "claims_reconfirmed" if previous_record is not None else "claims_recorded"
        event_details: dict[str, Any] = {
            "claims_artifact": _artifact_relative(path, artifact),
            "claims_artifact_sha256": sha256_file(artifact),
            "claims_sha256": record["claims_sha256"],
            "claim_count": summary["claim_count"],
            "source_artifact_sha256": record["source_artifact_sha256"],
        }
        if previous_record is not None:
            event_details.update(
                {
                    "previous_claims_artifact_sha256": previous_artifact_sha256,
                    "previous_claims_sha256": previous_record.get("claims_sha256"),
                    "previous_source_artifact_sha256": previous_record.get(
                        "source_artifact_sha256"
                    ),
                    "repaired_stale_binding": stale_task_id == task_id,
                }
            )
        event = _append_event(
            path,
            event_type,
            actor=record["confirmed_by"],
            task_id=task_id,
            details=event_details,
        )
        _set_event_tail(state, event)
        _write_state(path, state)
        status = _finalize_run_update(path)
        return {
            **status,
            "claims_artifact": _artifact_relative(path, artifact),
            "recorded_claims": summary,
            "idempotent": False,
            "reconfirmed": previous_record is not None,
        }


def _record_supplemental_evidence_unlocked(
    path: Path,
    *,
    content: str,
    source: str,
    method: str,
    limitations: str,
    collected_by: str,
    evidence_role: str,
    revision_of: str | None,
    review_decision_hash: str | None,
    allow_any_paused_task: bool,
) -> dict[str, Any]:
    _verify_run_unlocked(path)
    state = _load_state(path)
    pack = load_pack(path / PACK_SNAPSHOT).data
    tasks = pack["mission"]["tasks"]
    current_index = state.get("next_task_index")
    current_task = (
        tasks[current_index]
        if isinstance(current_index, int) and 0 <= current_index < len(tasks)
        else None
    )
    if (
        state["status"] != "paused"
        or current_task is None
        or state["pending_task_id"] != current_task["task_id"]
    ):
        raise RunStateError("Run 必须暂停在可审查的 Task 门禁")
    if not allow_any_paused_task and (
        current_index != 1 or current_task["operation"] != "record_evidence"
    ):
        raise RunStateError("补充 Evidence 只能在第 2 步等待批准时导入")

    fields = {
        "content": (content, MAX_SUPPLEMENTAL_CONTENT_CHARS),
        "source": (source, 500),
        "method": (method, 1000),
        "limitations": (limitations, 2000),
        "collected_by": (collected_by, 200),
        "evidence_role": (evidence_role, 100),
    }
    cleaned: dict[str, str] = {}
    for name, (value, maximum) in fields.items():
        if not isinstance(value, str) or not value.strip():
            raise RunStateError(f"{name} 必须是非空文本")
        normalized = value.strip()
        if len(normalized) > maximum:
            raise RunStateError(f"{name} 超过 {maximum} 字符")
        cleaned[name] = normalized

    sequence = state.get("supplemental_evidence_count", 0)
    if not isinstance(sequence, int) or not 0 <= sequence < MAX_SUPPLEMENTAL_EVIDENCE:
        raise RunStateError("补充 Evidence 数量已达到本阶段上限")
    sequence += 1

    artifact_ids: set[str] = set()
    for existing_path in sorted((path / "evidence").glob("*.json")):
        existing = read_json(existing_path)
        if isinstance(existing, dict) and isinstance(existing.get("evidence_id"), str):
            artifact_ids.add(existing["evidence_id"])
    for report_path in sorted((path / "reports").glob("TASK-REPORT-*.json")):
        report = read_json(report_path)
        output = report.get("output") if isinstance(report, dict) else None
        if isinstance(output, dict) and isinstance(output.get("id"), str):
            artifact_ids.add(output["id"])
    if revision_of is not None and revision_of not in artifact_ids:
        raise RunStateError("revision_of 没有对应的既有 Task 产物")
    if review_decision_hash is not None:
        _, _, review_records = _read_review_records(path)
        latest_review = review_records[-1] if review_records else None
        if (
            latest_review is None
            or latest_review.get("hash") != review_decision_hash
            or latest_review.get("decision") != "Changes Requested"
            or latest_review.get("task_id") != state["pending_task_id"]
        ):
            raise RunStateError("review_decision_hash 不是当前 Task 的最新返工决定")

    evidence_id = f"EVID-MVP-{state['run_id']}-SUP-{sequence:02d}"
    evidence: dict[str, Any] = {
        "schema_version": "research-os-mvp-evidence/0.1",
        "evidence_id": evidence_id,
        "run_id": state["run_id"],
        "pack_id": state["pack_id"],
        "mission_id": state["mission_id"],
        "task_id": state["pending_task_id"],
        "collected_at": utc_now(),
        "collected_by": cleaned["collected_by"],
        "source": cleaned["source"],
        "method": cleaned["method"],
        "content": cleaned["content"],
        "content_sha256": sha256_text(cleaned["content"]),
        "limitations": cleaned["limitations"],
        "evidence_role": cleaned["evidence_role"],
        "revision_of": revision_of,
        "review_decision_hash": review_decision_hash,
    }
    artifact = path / "evidence" / f"EVID-SUPPLEMENTAL-{sequence:02d}.json"
    if artifact.exists() or artifact.is_symlink():
        raise RunStateError(f"补充 Evidence 文件已存在：{artifact}")
    write_json_atomic(artifact, evidence)
    output = {
        "class": "Evidence",
        "path": _artifact_relative(path, artifact),
        "sha256": sha256_file(artifact),
        "id": evidence_id,
        "role": cleaned["evidence_role"],
        "revision_of": revision_of,
        "review_decision_hash": review_decision_hash,
    }
    event = _append_event(
        path,
        "supplemental_evidence_recorded",
        actor=cleaned["collected_by"],
        task_id=state["pending_task_id"],
        details=output,
    )
    _set_event_tail(state, event)
    state["supplemental_evidence_count"] = sequence
    _write_state(path, state)
    verified = _finalize_run_update(path)
    return {
        **output,
        "run_status": verified["status"],
        "task_output_revision_count": verified["task_output_revision_count"],
    }


def revise_task_output(
    run_dir: Path | str,
    *,
    content: str,
    revised_by: str,
    note: str,
    review_decision_hash: str,
) -> dict[str, Any]:
    """Append an immutable Task-output revision linked to Changes Requested."""
    path = Path(run_dir)
    with run_lock(path):
        return _revise_task_output_unlocked(
            path,
            content=content,
            revised_by=revised_by,
            note=note,
            review_decision_hash=review_decision_hash,
        )


def _revise_task_output_unlocked(
    path: Path,
    *,
    content: str,
    revised_by: str,
    note: str,
    review_decision_hash: str,
) -> dict[str, Any]:
    _verify_run_unlocked(path)
    state = _load_state(path)
    if (
        state["status"] != "paused"
        or not isinstance(state.get("pending_task_id"), str)
        or not isinstance(state.get("pending_output"), dict)
    ):
        raise RunStateError("Task output revision requires a paused review gate")

    actor = revised_by.strip()
    cleaned_note = note.strip()
    cleaned_content = content.strip()
    if not actor or len(actor) > 200:
        raise RunStateError("revised_by must be 1-200 non-whitespace characters")
    if not cleaned_note or len(cleaned_note) > MAX_TASK_OUTPUT_REVISION_NOTE_CHARS:
        raise RunStateError(
            "revision note must be 1-800 non-whitespace characters"
        )
    if not cleaned_content or len(cleaned_content) > MAX_SUPPLEMENTAL_CONTENT_CHARS:
        raise RunStateError(
            f"revision content must be 1-{MAX_SUPPLEMENTAL_CONTENT_CHARS} characters"
        )
    if not isinstance(review_decision_hash, str) or len(review_decision_hash) != 64:
        raise RunStateError("review_decision_hash must be a 64-character hash")

    _, _, review_records = _read_review_records(path)
    latest_review = review_records[-1] if review_records else None
    if (
        latest_review is None
        or latest_review.get("hash") != review_decision_hash
        or latest_review.get("decision") != "Changes Requested"
        or latest_review.get("task_id") != state["pending_task_id"]
    ):
        raise RunStateError(
            "Task output revision must link the current latest Changes Requested"
        )

    revision_rows: list[tuple[Path, dict[str, Any]]] = []
    for evidence_path in sorted((path / "evidence").glob("*.json")):
        evidence = read_json(evidence_path)
        if (
            isinstance(evidence, dict)
            and evidence.get("task_id") == state["pending_task_id"]
            and evidence.get("evidence_role") == TASK_OUTPUT_REVISION_ROLE
        ):
            revision_rows.append((evidence_path, evidence))
    method = f"根据 Reviewer Changes Requested 修订 Task 产物：{cleaned_note}"
    if revision_rows:
        latest_path, latest_revision = revision_rows[-1]
        if (
            latest_revision.get("content") == cleaned_content
            and latest_revision.get("collected_by") == actor
            and latest_revision.get("method") == method
            and latest_revision.get("review_decision_hash") == review_decision_hash
        ):
            verified = _verified_checkpointed_status(path)
            return {
                "class": "Evidence",
                "path": _artifact_relative(path, latest_path),
                "sha256": sha256_file(latest_path),
                "id": latest_revision["evidence_id"],
                "role": TASK_OUTPUT_REVISION_ROLE,
                "revision_of": latest_revision["revision_of"],
                "review_decision_hash": review_decision_hash,
                "run_status": verified["status"],
                "task_output_revision_count": verified[
                    "task_output_revision_count"
                ],
            }
        revision_of = latest_revision["evidence_id"]
    else:
        revision_of = state["pending_output"].get("id")
        if not isinstance(revision_of, str) or not revision_of:
            raise RunStateError("Pending Task output has no revision target ID")

    return _record_supplemental_evidence_unlocked(
        path,
        content=cleaned_content,
        source="human://task-output-revision",
        method=method,
        limitations=(
            "该 Evidence 是对原 Task 产物的不可变修订覆盖层；"
            "原产物保留，后续 Reviewer 应以最新修订版为主并对照原版。"
        ),
        collected_by=actor,
        evidence_role=TASK_OUTPUT_REVISION_ROLE,
        revision_of=revision_of,
        review_decision_hash=review_decision_hash,
        allow_any_paused_task=True,
    )


def approve_run(
    run_dir: Path | str,
    *,
    approver: str,
    note: str = "",
) -> dict[str, Any]:
    """Compatibility shorthand for a formal Reviewer `Approved` decision."""
    return review_run(
        run_dir,
        reviewer=approver,
        decision="Approved",
        note=note,
    )


def _normalize_review_decision(value: str) -> str:
    normalized = " ".join(
        value.strip().casefold().replace("-", " ").replace("_", " ").split()
    )
    aliases = {
        "approved": "Approved",
        "approve": "Approved",
        "批准": "Approved",
        "changes requested": "Changes Requested",
        "request changes": "Changes Requested",
        "返工": "Changes Requested",
        "修改": "Changes Requested",
        "rejected": "Rejected",
        "reject": "Rejected",
        "驳回": "Rejected",
        "拒绝": "Rejected",
    }
    decision = aliases.get(normalized)
    if decision is None:
        raise RunStateError(
            "Reviewer decision must be Approved, Changes Requested, or Rejected"
        )
    return decision


def review_run(
    run_dir: Path | str,
    *,
    reviewer: str,
    decision: str,
    note: str = "",
) -> dict[str, Any]:
    """Append one formal human Reviewer decision for the current Task bundle."""
    path = Path(run_dir)
    with run_lock(path):
        return _review_run_unlocked(
            path,
            reviewer=reviewer,
            decision=decision,
            note=note,
        )


def read_review_decisions(run_dir: Path | str) -> list[dict[str, Any]]:
    """Return verified formal Reviewer decisions in append order."""
    path = Path(run_dir)
    with run_lock(path):
        _verify_run_unlocked(path)
        _, _, records = _read_review_records(path)
        return [dict(record) for record in records]


def _select_review_record(
    reviews: list[dict[str, Any]],
    review_hash: str | None,
) -> dict[str, Any]:
    if not reviews:
        raise RunStateError("Run has no Reviewer decision to sign")
    if review_hash is None:
        return reviews[-1]
    selected = next((item for item in reviews if item.get("hash") == review_hash), None)
    if selected is None:
        raise RunStateError("Reviewer decision Hash does not exist in this Run")
    return selected


def _review_signature_payload(
    run_id: str,
    review: dict[str, Any],
    *,
    signer_identity: str,
    public_key_fingerprint: str,
) -> str:
    payload = {
        "schema_version": REVIEW_SIGNATURE_PAYLOAD_SCHEMA,
        "namespace": REVIEW_SIGNATURE_NAMESPACE,
        "run_id": run_id,
        "review_id": review["review_id"],
        "review_hash": review["hash"],
        "reviewer": review["reviewer"],
        "decision": review["decision"],
        "task_id": review["task_id"],
        "subject_sha256": review["subject"]["bundle_sha256"],
        "signer_identity": signer_identity,
        "public_key_fingerprint": public_key_fingerprint,
    }
    return canonical_json_text(payload) + "\n"


def build_review_signature_request(
    run_dir: Path | str,
    *,
    signer_identity: str,
    public_key: str,
    review_hash: str | None = None,
) -> dict[str, Any]:
    path = Path(run_dir)
    try:
        identity = normalize_signer_identity(signer_identity)
        normalized_key = normalize_ed25519_public_key(public_key)
        fingerprint = ed25519_public_key_fingerprint(normalized_key)
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    with run_lock(path):
        status = _verified_checkpointed_status(path)
        _, _, reviews = _read_review_records(path)
        review = _select_review_record(reviews, review_hash)
        payload = _review_signature_payload(
            status["run_id"],
            review,
            signer_identity=identity,
            public_key_fingerprint=fingerprint,
        )
        return {
            "schema_version": REVIEW_SIGNATURE_PAYLOAD_SCHEMA,
            "namespace": REVIEW_SIGNATURE_NAMESPACE,
            "run_id": status["run_id"],
            "review_id": review["review_id"],
            "review_hash": review["hash"],
            "signer_identity": identity,
            "public_key": normalized_key,
            "public_key_fingerprint": fingerprint,
            "payload": payload,
            "payload_sha256": sha256_text(payload),
        }


def attach_review_signature(
    run_dir: Path | str,
    *,
    signer_identity: str,
    public_key: str,
    signature: str,
    review_hash: str | None = None,
) -> dict[str, Any]:
    path = Path(run_dir)
    with run_lock(path):
        _verify_run_unlocked(path)
        state = _load_state(path)
        _, _, reviews = _read_review_records(path)
        review = _select_review_record(reviews, review_hash)
        try:
            identity = normalize_signer_identity(signer_identity)
            normalized_key = normalize_ed25519_public_key(public_key)
            fingerprint = ed25519_public_key_fingerprint(normalized_key)
            normalized_signature = normalize_ssh_signature(signature)
            payload = _review_signature_payload(
                state["run_id"],
                review,
                signer_identity=identity,
                public_key_fingerprint=fingerprint,
            )
            verify_ssh_signature(
                payload,
                normalized_signature,
                public_key=normalized_key,
                signer_identity=identity,
                namespace=REVIEW_SIGNATURE_NAMESPACE,
            )
        except SignatureError as exc:
            raise RunStateError(str(exc)) from exc

        signature_count, _, signature_records = _read_review_signature_records(path)
        matching = [
            item
            for item in signature_records
            if item.get("review_hash") == review["hash"]
            and item.get("public_key_fingerprint") == fingerprint
        ]
        if matching:
            existing = matching[-1]
            if (
                existing.get("signer_identity") == identity
                and existing.get("signature") == normalized_signature
            ):
                return _verified_checkpointed_status(path)
            raise RunStateError(
                "This Ed25519 key already has a different signature for the Reviewer decision"
            )
        if signature_count >= MAX_REVIEW_SIGNATURES:
            raise RunStateError("Reviewer signature count has reached the Run limit")

        signature_record = append_chained_record(
            path / REVIEW_SIGNATURES_FILE,
            {
                "schema_version": REVIEW_SIGNATURE_SCHEMA,
                "at": utc_now(),
                "signature_id": (
                    f"REVIEW-SIGNATURE-{state['run_id']}-{signature_count + 1:03d}"
                ),
                "review_id": review["review_id"],
                "review_hash": review["hash"],
                "signer_identity": identity,
                "public_key": normalized_key,
                "public_key_fingerprint": fingerprint,
                "namespace": REVIEW_SIGNATURE_NAMESPACE,
                "payload_sha256": sha256_text(payload),
                "signature": normalized_signature,
            },
        )
        event = _append_event(
            path,
            "review_signature_attached",
            actor=identity,
            task_id=review["task_id"],
            details={
                "signature_id": signature_record["signature_id"],
                "review_id": review["review_id"],
                "review_hash": review["hash"],
                "public_key_fingerprint": fingerprint,
            },
        )
        state["review_signature_tail_hash"] = signature_record["hash"]
        _set_event_tail(state, event)
        _write_state(path, state)
        return _finalize_run_update(path)


def sign_review_decision(
    run_dir: Path | str,
    *,
    signer_identity: str,
    private_key_path: Path | str,
    public_key_path: Path | str,
    review_hash: str | None = None,
) -> dict[str, Any]:
    try:
        public_key = load_ed25519_public_key(public_key_path)
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    request = build_review_signature_request(
        run_dir,
        signer_identity=signer_identity,
        public_key=public_key,
        review_hash=review_hash,
    )
    try:
        signature = sign_ssh_payload(
            request["payload"],
            private_key_path=private_key_path,
            namespace=REVIEW_SIGNATURE_NAMESPACE,
        )
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    return attach_review_signature(
        run_dir,
        signer_identity=signer_identity,
        public_key=public_key,
        signature=signature,
        review_hash=request["review_hash"],
    )


def _review_run_unlocked(
    path: Path,
    *,
    reviewer: str,
    decision: str,
    note: str,
) -> dict[str, Any]:
    _verify_run_unlocked(path)
    state = _load_state(path)
    normalized_decision = _normalize_review_decision(decision)
    actor = reviewer.strip()
    cleaned_note = note.strip()
    if not actor or len(actor) > 100:
        raise RunStateError("reviewer must be 1-100 non-whitespace characters")
    if len(cleaned_note) > 1000:
        raise RunStateError("Reviewer decision note exceeds 1000 characters")
    if normalized_decision != "Approved" and not cleaned_note:
        raise RunStateError("Changes Requested and Rejected require a non-empty note")

    review_count, _, review_records = _read_review_records(path)
    latest_review = review_records[-1] if review_records else None
    if state["status"] == "rejected":
        if (
            normalized_decision == "Rejected"
            and latest_review is not None
            and latest_review.get("hash") == state.get("rejection_review_hash")
            and latest_review.get("reviewer") == actor
            and latest_review.get("note") == cleaned_note
        ):
            return _verified_checkpointed_status(path)
        raise RunStateError("Rejected Run cannot accept another Reviewer decision")
    if state["status"] != "paused":
        raise RunStateError("Run must be paused at a human gate before review")
    if review_count >= MAX_REVIEW_DECISIONS:
        raise RunStateError("Reviewer decision count has reached the Run limit")

    task_id = state["pending_task_id"]
    subject = _review_subject(path, state)
    if (
        normalized_decision == "Changes Requested"
        and latest_review is not None
        and latest_review.get("decision") == normalized_decision
        and latest_review.get("reviewer") == actor
        and latest_review.get("note") == cleaned_note
        and isinstance(latest_review.get("subject"), dict)
        and latest_review["subject"].get("bundle_sha256") == subject["bundle_sha256"]
    ):
        return _verified_checkpointed_status(path)

    review = append_chained_record(
        path / REVIEWS_FILE,
        {
            "at": utc_now(),
            "review_id": f"REVIEW-{state['run_id']}-{review_count + 1:03d}",
            "reviewer": actor,
            "decision": normalized_decision,
            "task_id": task_id,
            "note": cleaned_note,
            "subject": subject,
        },
    )
    review_event = _append_event(
        path,
        "review_decision_recorded",
        actor=actor,
        task_id=task_id,
        details={
            "review_id": review["review_id"],
            "review_hash": review["hash"],
            "decision": normalized_decision,
            "subject_sha256": subject["bundle_sha256"],
            "note": cleaned_note,
        },
    )
    state["review_tail_hash"] = review["hash"]
    _set_event_tail(state, review_event)

    if normalized_decision == "Approved":
        approval = append_chained_record(
            path / APPROVALS_FILE,
            {
                "at": utc_now(),
                "approver": actor,
                "decision": "Approved",
                "task_id": task_id,
                "note": cleaned_note,
                "review_hash": review["hash"],
            },
        )
        approval_event = _append_event(
            path,
            "approval_granted",
            actor=actor,
            task_id=task_id,
            details={
                "decision": "Approved",
                "approval_hash": approval["hash"],
                "review_hash": review["hash"],
                "note": cleaned_note,
            },
        )
        state["status"] = "approved_pending_resume"
        state["approval_tail_hash"] = approval["hash"]
        _set_event_tail(state, approval_event)
    elif normalized_decision == "Rejected":
        state["status"] = "rejected"
        state["pending_task_id"] = None
        state["pending_output"] = None
        state["rejected_task_id"] = task_id
        state["rejected_at"] = review["at"]
        state["rejected_by"] = actor
        state["rejection_reason"] = cleaned_note
        state["rejection_review_hash"] = review["hash"]

    _write_state(path, state)
    return _finalize_run_update(path)


def cancel_run(
    run_dir: Path | str,
    *,
    cancelled_by: str,
    reason: str,
) -> dict[str, Any]:
    """Move an unfinished Run into an audited, idempotent terminal state."""
    path = Path(run_dir)
    with run_lock(path):
        return _cancel_run_unlocked(
            path,
            cancelled_by=cancelled_by,
            reason=reason,
        )


def _cancel_run_unlocked(
    path: Path,
    *,
    cancelled_by: str,
    reason: str,
) -> dict[str, Any]:
    _verify_run_unlocked(path)
    state = _load_state(path)
    if state["status"] == "cancelled":
        return _verified_checkpointed_status(path)
    if state["status"] == "completed":
        raise RunStateError("Completed Run cannot be cancelled")
    if state["status"] == "rejected":
        raise RunStateError("Rejected Run cannot be cancelled")

    actor = cancelled_by.strip()
    cleaned_reason = reason.strip()
    if not actor or len(actor) > 100:
        raise RunStateError("cancelled_by must be 1-100 non-whitespace characters")
    if not cleaned_reason or len(cleaned_reason) > 1000:
        raise RunStateError("cancellation reason must be 1-1000 characters")

    previous_status = state["status"]
    cancelled_task_id = state["pending_task_id"]
    event = _append_event(
        path,
        "run_cancelled",
        actor=actor,
        task_id=cancelled_task_id,
        details={
            "reason": cleaned_reason,
            "previous_status": previous_status,
            "executed_task_count": len(state["executed_tasks"]),
            "approved_task_count": len(state["approved_tasks"]),
        },
    )
    _set_event_tail(state, event)
    state["status"] = "cancelled"
    state["pending_task_id"] = None
    state["pending_output"] = None
    state["cancelled_task_id"] = cancelled_task_id
    state["cancelled_at"] = event["at"]
    state["cancelled_by"] = actor
    state["cancellation_reason"] = cleaned_reason
    _write_state(path, state)
    return _finalize_run_update(path)


def resume_run(run_dir: Path | str) -> dict[str, Any]:
    path = Path(run_dir)
    with run_lock(path):
        return _resume_run_unlocked(path)


def _claims_gate_reasons(coverage: dict[str, Any], task_id: str) -> list[str]:
    reasons: list[str] = []
    if task_id in coverage["tasks_missing_claims"]:
        reasons.append("missing Claim confirmation (0 Claim records)")
    elif task_id in coverage["tasks_with_empty_claims"]:
        reasons.append("empty Claim confirmation (0 Claims)")
    if not coverage["hard_gate_pass"]:
        count = coverage["unsupported_fact_count"]
        reasons.append(f"{count} unsupported verifiable_fact")
    if coverage["fact_coverage"] is None:
        reasons.append(
            f"no verifiable_fact ({coverage['verifiable_fact_count']} present)"
        )
    return reasons


def _pending_task_claims_gate(path: Path, state: dict[str, Any]) -> None:
    task_id = state["pending_task_id"]
    loaded = load_pack(path / PACK_SNAPSHOT)
    view = verify_claims(
        path,
        run_id=state["run_id"],
        task_ids=[task["task_id"] for task in loaded.data["mission"]["tasks"]],
    )
    coverage = task_claims_coverage(view, task_id)
    reasons = _claims_gate_reasons(coverage, task_id)
    if reasons:
        raise RunStateError(
            f"Claims gate is not satisfied for pending Task {task_id}: "
            + "; ".join(reasons)
        )


def _resume_run_unlocked(path: Path) -> dict[str, Any]:
    verified = _verify_run_unlocked(path)
    state = _load_state(path)
    if state["status"] == "completed":
        return _verified_checkpointed_status(path)
    if state["status"] == "paused":
        raise RunStateError("Run is paused and requires explicit human approval")
    if state["status"] == "approved_pending_resume":
        if (
            verified["reviewer_trust_policy_bound"]
            and not verified.get("latest_review_trust_satisfied", False)
        ):
            missing = ", ".join(
                f"{item['role']} {item['observed_signatures']}/"
                f"{item['required_signatures']}"
                for item in verified.get("latest_review_trust_outstanding", [])
            )
            raise RunStateError(
                "Reviewer trust policy is not satisfied for the Approved decision"
                + (f": {missing}" if missing else "")
            )
        task_id = state["pending_task_id"]
        if (
            verified["claims_gate_enabled"]
            and state["next_task_index"]
            >= verified["claims_gate_from_task_index"]
        ):
            _pending_task_claims_gate(path, state)
        event = _append_event(
            path,
            "task_approved",
            actor="MVP Runtime",
            task_id=task_id,
            details={"next_task_index": state["next_task_index"] + 1},
        )
        _set_event_tail(state, event)
        state["approved_tasks"].append(task_id)
        state["next_task_index"] += 1
        state["pending_task_id"] = None
        state["pending_output"] = None
        state["status"] = "running"
        _write_state(path, state)
        _finalize_run_update(path)
    elif state["status"] != "running":
        raise RunStateError(f"Run status cannot resume: {state['status']}")

    loaded = load_pack(path / PACK_SNAPSHOT)
    state = _load_state(path)
    tasks = loaded.data["mission"]["tasks"]
    if state["next_task_index"] == len(tasks):
        event = _append_event(
            path,
            "mission_completed",
            actor="MVP Runtime",
            details={
                "mission_id": state["mission_id"],
                "approved_tasks": state["approved_tasks"],
            },
        )
        _set_event_tail(state, event)
        state["status"] = "completed"
        _write_state(path, state)
        return _finalize_run_update(path)
    return _execute_current_task(path, state, loaded.data)


def _verify_evidence(
    run_dir: Path,
    task_ids: list[str],
    review_records: list[dict[str, Any]],
) -> tuple[int, int, int]:
    count = 0
    supplemental_count = 0
    task_output_revision_count = 0
    evidence_ids: set[str] = set()
    task_output_ids: dict[str, str] = {}
    for report_path in sorted((run_dir / "reports").glob("TASK-REPORT-*.json")):
        report = read_json(report_path)
        output = report.get("output") if isinstance(report, dict) else None
        if (
            isinstance(report, dict)
            and isinstance(report.get("task_id"), str)
            and isinstance(output, dict)
            and isinstance(output.get("id"), str)
        ):
            task_output_ids[report["task_id"]] = output["id"]
    revisions_by_task: dict[str, list[dict[str, Any]]] = {}
    for evidence_path in sorted((run_dir / "evidence").glob("*.json")):
        evidence = read_json(evidence_path)
        if not isinstance(evidence, dict):
            raise IntegrityError(f"Evidence must be an object: {evidence_path}")
        content = evidence.get("content")
        if not isinstance(content, str):
            raise IntegrityError(f"Evidence content must be a string: {evidence_path}")
        if evidence.get("content_sha256") != sha256_text(content):
            raise IntegrityError(f"Evidence content hash mismatch: {evidence_path}")
        if evidence.get("task_id") not in task_ids:
            raise IntegrityError(f"Evidence references an unknown Task: {evidence_path}")
        evidence_id = evidence.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            raise IntegrityError(f"Evidence ID is invalid: {evidence_path}")
        if evidence_id in evidence_ids:
            raise IntegrityError(f"Evidence ID is duplicated: {evidence_id}")
        evidence_ids.add(evidence_id)
        role = evidence.get("evidence_role")
        if role is not None:
            if not isinstance(role, str) or not role.strip():
                raise IntegrityError(f"Evidence role is invalid: {evidence_path}")
            review_hash = evidence.get("review_decision_hash")
            if review_hash is not None:
                linked_review = next(
                    (
                        review
                        for review in review_records
                        if review.get("hash") == review_hash
                    ),
                    None,
                )
                if (
                    linked_review is None
                    or linked_review.get("decision") != "Changes Requested"
                    or linked_review.get("task_id") != evidence.get("task_id")
                ):
                    raise IntegrityError(
                        f"Evidence links an invalid Reviewer decision: {evidence_path}"
                    )
            if role == TASK_OUTPUT_REVISION_ROLE:
                task_id = evidence["task_id"]
                if review_hash is None:
                    raise IntegrityError(
                        f"Task output revision has no Reviewer decision: {evidence_path}"
                    )
                if task_output_ids.get(task_id) is None:
                    raise IntegrityError(
                        f"Task output revision has no original Task output: {evidence_path}"
                    )
                if evidence.get("source") != "human://task-output-revision":
                    raise IntegrityError(
                        f"Task output revision source is invalid: {evidence_path}"
                    )
                revisions_by_task.setdefault(task_id, []).append(evidence)
                task_output_revision_count += 1
            supplemental_count += 1
        count += 1

    # Chain linkage is validated after the scan so the result does not depend on the
    # order in which Evidence files happen to sort. See revisions.py for why.
    for task_id, revisions in sorted(revisions_by_task.items()):
        try:
            resolve_revision_chain(
                revisions,
                task_id=task_id,
                base_output_id=task_output_ids[task_id],
            )
        except RevisionChainError as exc:
            raise IntegrityError(f"Task output revision chain is broken: {exc}") from exc

    return count, supplemental_count, task_output_revision_count


def _verify_task_reports(
    run_dir: Path,
    pack: dict[str, Any],
    executed_tasks: list[str],
) -> int:
    task_report_files = sorted((run_dir / "reports").glob("TASK-REPORT-*.json"))
    if len(task_report_files) != len(executed_tasks):
        raise IntegrityError("Task Report count does not match executed_tasks")

    tasks = pack["mission"]["tasks"]
    for index, task_id in enumerate(executed_tasks):
        report_path = run_dir / "reports" / f"TASK-REPORT-{index + 1:02d}.json"
        report = read_json(report_path)
        if not isinstance(report, dict) or report.get("task_id") != task_id:
            raise IntegrityError(f"Task Report identity mismatch: {report_path}")
        output = report.get("output")
        if not isinstance(output, dict):
            raise IntegrityError(f"Task Report output is invalid: {report_path}")
        relative = output.get("path")
        expected_hash = output.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            raise IntegrityError(f"Task Report output reference is invalid: {report_path}")
        artifact = run_dir / relative
        try:
            artifact.resolve().relative_to(run_dir.resolve())
        except ValueError as exc:
            raise IntegrityError(
                f"Task Report output escapes the Run directory: {report_path}"
            ) from exc
        if artifact.is_symlink() or not artifact.is_file():
            raise IntegrityError(f"Task Report output is missing: {artifact}")
        if sha256_file(artifact) != expected_hash:
            raise IntegrityError(f"Task Report output hash mismatch: {artifact}")
        if task_id != tasks[index]["task_id"]:
            raise IntegrityError(f"Task Report order mismatch: {report_path}")

    mission_reports = list((run_dir / "reports").glob("REPORT-MISSION-*.md"))
    expected_mission_reports = 1 if len(executed_tasks) == len(tasks) else 0
    if len(mission_reports) != expected_mission_reports:
        raise IntegrityError("Mission Report count does not match executed_tasks")
    return len(task_report_files) + len(mission_reports)


def _verified_review_artifact(run_dir: Path, relative: Any, expected_hash: Any) -> Path:
    if not isinstance(relative, str) or not isinstance(expected_hash, str):
        raise IntegrityError("Reviewer subject artifact reference is invalid")
    artifact = run_dir / relative
    try:
        artifact.resolve().relative_to(run_dir.resolve())
    except ValueError as exc:
        raise IntegrityError("Reviewer subject artifact escapes the Run directory") from exc
    if artifact.is_symlink() or not artifact.is_file():
        raise IntegrityError(f"Reviewer subject artifact is missing: {artifact}")
    if sha256_file(artifact) != expected_hash:
        raise IntegrityError(f"Reviewer subject artifact hash mismatch: {artifact}")
    return artifact


def _verify_review_subject(run_dir: Path, subject: Any, task_id: str) -> str:
    if not isinstance(subject, dict):
        raise IntegrityError("Reviewer decision subject must be an object")
    if subject.get("schema_version") != "research-os-mvp-review-subject/0.1":
        raise IntegrityError("Reviewer decision subject schema is unsupported")
    if subject.get("task_id") != task_id:
        raise IntegrityError("Reviewer decision subject Task does not match the decision")

    stored_bundle_hash = subject.get("bundle_sha256")
    unsigned_subject = dict(subject)
    unsigned_subject.pop("bundle_sha256", None)
    expected_bundle_hash = sha256_text(canonical_json_text(unsigned_subject))
    if stored_bundle_hash != expected_bundle_hash:
        raise IntegrityError("Reviewer decision subject bundle hash mismatch")

    task_output = subject.get("task_output")
    if not isinstance(task_output, dict):
        raise IntegrityError("Reviewer decision subject has no Task output")
    output_artifact = _verified_review_artifact(
        run_dir,
        task_output.get("path"),
        task_output.get("sha256"),
    )
    if output_artifact.parent == run_dir:
        raise IntegrityError("Reviewer Task output must be a Run artifact")
    matching_reports: list[dict[str, Any]] = []
    for report_path in sorted((run_dir / "reports").glob("TASK-REPORT-*.json")):
        report = read_json(report_path)
        if isinstance(report, dict) and report.get("task_id") == task_id:
            matching_reports.append(report)
    if len(matching_reports) != 1 or matching_reports[0].get("output") != task_output:
        raise IntegrityError("Reviewer Task output does not match its Task Report")

    supplemental = subject.get("supplemental_evidence")
    if not isinstance(supplemental, list):
        raise IntegrityError("Reviewer supplemental Evidence references must be an array")
    evidence_ids: set[str] = set()
    for reference in supplemental:
        if not isinstance(reference, dict):
            raise IntegrityError("Reviewer supplemental Evidence reference is invalid")
        evidence_path = _verified_review_artifact(
            run_dir,
            reference.get("path"),
            reference.get("sha256"),
        )
        evidence = read_json(evidence_path)
        if not isinstance(evidence, dict):
            raise IntegrityError("Reviewer supplemental Evidence must be an object")
        evidence_id = reference.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id or evidence_id in evidence_ids:
            raise IntegrityError("Reviewer supplemental Evidence ID is invalid or duplicated")
        evidence_ids.add(evidence_id)
        expected_values = {
            "evidence_id": evidence_id,
            "task_id": task_id,
            "content_sha256": reference.get("content_sha256"),
            "evidence_role": reference.get("role"),
            "revision_of": reference.get("revision_of"),
            "review_decision_hash": reference.get("review_decision_hash"),
        }
        for field, expected in expected_values.items():
            if evidence.get(field) != expected:
                raise IntegrityError(
                    f"Reviewer supplemental Evidence {field} does not match its artifact"
                )

    latest_revision_id = subject.get("latest_revision_id")
    if latest_revision_id is not None and latest_revision_id not in evidence_ids:
        raise IntegrityError("Reviewer latest revision is not in the subject bundle")
    return expected_bundle_hash


def _verify_reviews(
    run_dir: Path,
    state: dict[str, Any],
    task_ids: list[str],
) -> tuple[int, str, list[dict[str, Any]]]:
    count, tail, records = _read_review_records(run_dir)
    previous_task_index = -1
    for index, record in enumerate(records, start=1):
        task_id = record.get("task_id")
        if task_id not in state["executed_tasks"]:
            raise IntegrityError("Reviewer decision references an unexecuted Task")
        task_index = task_ids.index(task_id)
        if task_index < previous_task_index:
            raise IntegrityError("Reviewer decisions are not in Task order")
        previous_task_index = task_index
        if record.get("review_id") != f"REVIEW-{state['run_id']}-{index:03d}":
            raise IntegrityError("Reviewer decision ID does not match its sequence")
        reviewer = record.get("reviewer")
        note = record.get("note")
        decision = record.get("decision")
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 100:
            raise IntegrityError("Reviewer decision has an invalid reviewer")
        if not isinstance(note, str) or len(note) > 1000:
            raise IntegrityError("Reviewer decision has an invalid note")
        if decision not in REVIEW_DECISIONS:
            raise IntegrityError("Reviewer decision value is invalid")
        if decision != "Approved" and not note.strip():
            raise IntegrityError("Changes Requested and Rejected require a note")
        if not isinstance(record.get("at"), str) or not record["at"].strip():
            raise IntegrityError("Reviewer decision timestamp is invalid")
        _verify_review_subject(run_dir, record.get("subject"), task_id)
        if decision == "Rejected" and index != count:
            raise IntegrityError("Rejected must be the final Reviewer decision")
    return count, tail, records


def _verify_review_signatures(
    run_dir: Path,
    state: dict[str, Any],
    reviews: list[dict[str, Any]],
) -> tuple[int, str, list[dict[str, Any]]]:
    count, tail, records = _read_review_signature_records(run_dir)
    reviews_by_hash = {review["hash"]: review for review in reviews}
    signed_keys: set[tuple[str, str]] = set()
    for index, record in enumerate(records, start=1):
        if record.get("schema_version") != REVIEW_SIGNATURE_SCHEMA:
            raise IntegrityError("Reviewer signature schema is unsupported")
        if record.get("signature_id") != (
            f"REVIEW-SIGNATURE-{state['run_id']}-{index:03d}"
        ):
            raise IntegrityError("Reviewer signature ID does not match its sequence")
        review_hash = record.get("review_hash")
        review = reviews_by_hash.get(review_hash)
        if review is None or record.get("review_id") != review.get("review_id"):
            raise IntegrityError("Reviewer signature references an unknown decision")
        if not isinstance(record.get("at"), str) or not record["at"].strip():
            raise IntegrityError("Reviewer signature timestamp is invalid")
        try:
            identity = normalize_signer_identity(record.get("signer_identity", ""))
            public_key = normalize_ed25519_public_key(record.get("public_key", ""))
            fingerprint = ed25519_public_key_fingerprint(public_key)
            signature = normalize_ssh_signature(record.get("signature", ""))
        except SignatureError as exc:
            raise IntegrityError(f"Reviewer signature metadata is invalid: {exc}") from exc
        if record.get("public_key_fingerprint") != fingerprint:
            raise IntegrityError("Reviewer signature public key fingerprint mismatch")
        if record.get("namespace") != REVIEW_SIGNATURE_NAMESPACE:
            raise IntegrityError("Reviewer signature namespace is invalid")
        signed_key = (review["hash"], fingerprint)
        if signed_key in signed_keys:
            raise IntegrityError("Reviewer decision has a duplicated public-key signature")
        signed_keys.add(signed_key)
        payload = _review_signature_payload(
            state["run_id"],
            review,
            signer_identity=identity,
            public_key_fingerprint=fingerprint,
        )
        if record.get("payload_sha256") != sha256_text(payload):
            raise IntegrityError("Reviewer signature payload Hash mismatch")
        try:
            verify_ssh_signature(
                payload,
                signature,
                public_key=public_key,
                signer_identity=identity,
                namespace=REVIEW_SIGNATURE_NAMESPACE,
            )
        except SignatureError as exc:
            raise IntegrityError(f"Reviewer Ed25519 signature is invalid: {exc}") from exc
    return count, tail, records


def _read_approval_records(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / APPROVALS_FILE
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise IntegrityError("Approval record must be an object")
                records.append(record)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Cannot read approval chain: {exc}") from exc
    return records


def _read_event_records(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / EVENTS_FILE
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise IntegrityError("Event record must be an object")
                records.append(record)
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Cannot read event chain: {exc}") from exc
    return records


def _verify_claims_gate_binding(
    state: dict[str, Any],
    task_ids: list[str],
    event_records: list[dict[str, Any]],
) -> dict[str, Any]:
    enabled = state.get("claims_gate_enabled", False)
    effective_index = state.get("claims_gate_from_task_index")
    if not isinstance(enabled, bool):
        raise IntegrityError("claims_gate_enabled must be a boolean")
    binding_events = [
        record for record in event_records if record.get("type") == "claims_gate_bound"
    ]
    if not enabled:
        if effective_index is not None or binding_events:
            raise IntegrityError(
                "Claims gate state does not match its binding event history"
            )
        return {"enabled": False, "effective_from_task_index": None}
    if type(effective_index) is not int or not 0 <= effective_index < len(task_ids):
        raise IntegrityError("claims_gate_from_task_index is invalid")
    if len(binding_events) != 1:
        raise IntegrityError("Enabled Claims gate must have exactly one binding event")
    event = binding_events[0]
    expected_task_id = task_ids[effective_index]
    details = event.get("details")
    if (
        event.get("task_id") != expected_task_id
        or not isinstance(event.get("actor"), str)
        or not event["actor"].strip()
        or not isinstance(details, dict)
        or details.get("effective_from_task_index") != effective_index
        or details.get("effective_from_task_id") != expected_task_id
    ):
        raise IntegrityError("Claims gate binding event does not match state.json")
    return {
        "enabled": True,
        "effective_from_task_index": effective_index,
    }


def _verify_approval_review_links(
    approval_records: list[dict[str, Any]],
    review_records: list[dict[str, Any]],
) -> None:
    reviews_by_hash = {record["hash"]: record for record in review_records}
    linked_reviews: set[str] = set()
    for approval in approval_records:
        review_hash = approval.get("review_hash")
        if review_hash is None:
            continue
        review = reviews_by_hash.get(review_hash)
        if (
            review is None
            or review.get("decision") != "Approved"
            or review.get("task_id") != approval.get("task_id")
            or review.get("reviewer") != approval.get("approver")
            or review.get("note") != approval.get("note")
        ):
            raise IntegrityError("Approval does not match its formal Reviewer decision")
        if review_hash in linked_reviews:
            raise IntegrityError("Reviewer decision is linked to multiple approvals")
        linked_reviews.add(review_hash)
    expected_links = {
        record["hash"] for record in review_records if record["decision"] == "Approved"
    }
    if linked_reviews != expected_links:
        raise IntegrityError("Approved Reviewer decision is missing its approval record")


def _verify_state_invariants(state: dict[str, Any], task_ids: list[str]) -> None:
    status = state.get("status")
    if status not in ALLOWED_RUN_STATUSES:
        raise IntegrityError(f"Unknown Run status: {status}")
    executed = state.get("executed_tasks")
    approved = state.get("approved_tasks")
    next_index = state.get("next_task_index")
    if not isinstance(executed, list) or not isinstance(approved, list):
        raise IntegrityError("Run task lists must be arrays")
    if not isinstance(next_index, int) or not 0 <= next_index <= len(task_ids):
        raise IntegrityError("next_task_index is invalid")
    if executed != task_ids[: len(executed)]:
        raise IntegrityError("executed_tasks is not an ordered Task prefix")
    if approved != task_ids[: len(approved)]:
        raise IntegrityError("approved_tasks is not an ordered Task prefix")
    if len(approved) > len(executed) or len(executed) > len(approved) + 1:
        raise IntegrityError("Run has an impossible executed/approved Task relationship")
    if next_index != len(approved):
        raise IntegrityError("next_task_index does not match approved_tasks")
    supplemental_count = state.get("supplemental_evidence_count", 0)
    if (
        not isinstance(supplemental_count, int)
        or not 0 <= supplemental_count <= MAX_SUPPLEMENTAL_EVIDENCE
    ):
        raise IntegrityError("supplemental_evidence_count is invalid")

    pending = state.get("pending_task_id")
    if status in {"paused", "approved_pending_resume"}:
        if next_index >= len(task_ids) or pending != task_ids[next_index]:
            raise IntegrityError("Paused Run does not identify its current Task")
        if executed != approved + [pending]:
            raise IntegrityError("Paused Run Task lists are inconsistent")
    elif status == "running":
        if pending is not None or executed != approved:
            raise IntegrityError("Running Run has stale pending Task state")
    elif status == "completed":
        if pending is not None:
            raise IntegrityError("Completed Run still has a pending Task")
        if next_index != len(task_ids) or executed != task_ids or approved != task_ids:
            raise IntegrityError("Completed Run is missing executed or approved Tasks")
    elif status == "cancelled":
        if pending is not None or state.get("pending_output") is not None:
            raise IntegrityError("Cancelled Run still has pending Task state")
        cancelled_task_id = state.get("cancelled_task_id")
        if cancelled_task_id is None:
            if executed != approved:
                raise IntegrityError("Cancelled running Run has inconsistent Task lists")
        else:
            if next_index >= len(task_ids) or cancelled_task_id != task_ids[next_index]:
                raise IntegrityError("Cancelled Run references an invalid current Task")
            if executed != approved + [cancelled_task_id]:
                raise IntegrityError("Cancelled paused Run has inconsistent Task lists")
        for field in ("cancelled_at", "cancelled_by", "cancellation_reason"):
            value = state.get(field)
            if not isinstance(value, str) or not value.strip():
                raise IntegrityError(f"Cancelled Run is missing {field}")
    elif status == "rejected":
        if pending is not None or state.get("pending_output") is not None:
            raise IntegrityError("Rejected Run still has pending Task state")
        rejected_task_id = state.get("rejected_task_id")
        if next_index >= len(task_ids) or rejected_task_id != task_ids[next_index]:
            raise IntegrityError("Rejected Run references an invalid current Task")
        if executed != approved + [rejected_task_id]:
            raise IntegrityError("Rejected Run has inconsistent Task lists")
        for field in (
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "rejection_review_hash",
        ):
            value = state.get(field)
            if not isinstance(value, str) or not value.strip():
                raise IntegrityError(f"Rejected Run is missing {field}")


def _verify_run_unlocked(run_dir: Path | str) -> dict[str, Any]:
    path = Path(run_dir)
    if path.is_symlink() or not path.is_dir():
        raise IntegrityError(f"Run directory is missing or is a symlink: {path}")
    manifest = verify_hash_manifest(path)
    state = _load_state(path)
    loaded = load_pack(path / PACK_SNAPSHOT)
    if loaded.canonical_sha256 != state.get("pack_sha256"):
        raise IntegrityError("Pack snapshot hash does not match state.json")
    if loaded.data["pack_id"] != state.get("pack_id"):
        raise IntegrityError("Pack snapshot ID does not match state.json")
    if loaded.data["mission"]["mission_id"] != state.get("mission_id"):
        raise IntegrityError("Mission ID does not match state.json")

    event_count, event_tail = verify_chained_log(path / EVENTS_FILE)
    if event_tail != state.get("event_tail_hash"):
        raise IntegrityError("Event log tail does not match state.json")
    event_records = _read_event_records(path)
    if len(event_records) != event_count:
        raise IntegrityError("Event record count does not match its chained log")
    approval_count, approval_tail = verify_chained_log(path / APPROVALS_FILE)
    if approval_tail != state.get("approval_tail_hash"):
        raise IntegrityError("Approval log tail does not match state.json")

    task_ids = [task["task_id"] for task in loaded.data["mission"]["tasks"]]
    _verify_state_invariants(state, task_ids)
    claims_gate = _verify_claims_gate_binding(state, task_ids, event_records)
    review_count, review_tail, review_records = _verify_reviews(path, state, task_ids)
    if review_tail != state.get("review_tail_hash", ZERO_HASH):
        raise IntegrityError("Reviewer decision log tail does not match state.json")
    signature_count, signature_tail, signature_records = _verify_review_signatures(
        path,
        state,
        review_records,
    )
    if signature_tail != state.get("review_signature_tail_hash", ZERO_HASH):
        raise IntegrityError("Reviewer signature log tail does not match state.json")
    trust_evaluation = _reviewer_trust_evaluation(
        path,
        state,
        task_ids,
        review_records,
        signature_records,
    )
    approval_records = _read_approval_records(path)
    if len(approval_records) != approval_count:
        raise IntegrityError("Approval record count does not match its chained log")
    _verify_approval_review_links(approval_records, review_records)
    if state["status"] == "rejected" and (
        not review_records
        or review_records[-1].get("decision") != "Rejected"
        or review_records[-1].get("hash") != state.get("rejection_review_hash")
        or review_records[-1].get("task_id") != state.get("rejected_task_id")
    ):
        raise IntegrityError("Rejected Run does not match its final Reviewer decision")
    evidence_count, supplemental_count, task_output_revision_count = _verify_evidence(
        path,
        task_ids,
        review_records,
    )
    expected_evidence_count = sum(
        1
        for task in loaded.data["mission"]["tasks"][: len(state["executed_tasks"])]
        if task["operation"] == "record_evidence"
    )
    recorded_supplemental = state.get("supplemental_evidence_count", 0)
    if supplemental_count != recorded_supplemental:
        raise IntegrityError("Supplemental Evidence count does not match state.json")
    expected_evidence_count += recorded_supplemental
    if evidence_count != expected_evidence_count:
        raise IntegrityError("Evidence count does not match executed_tasks")
    report_count = _verify_task_reports(path, loaded.data, state["executed_tasks"])
    claim_status = verify_claims(
        path,
        run_id=state["run_id"],
        task_ids=task_ids,
    )
    result = {
        "run_id": state["run_id"],
        "status": state["status"],
        "pack_id": state["pack_id"],
        "pack_sha256": state["pack_sha256"],
        "mission_id": state["mission_id"],
        "next_task_index": state["next_task_index"],
        "pending_task_id": state["pending_task_id"],
        "executed_tasks": state["executed_tasks"],
        "approved_tasks": state["approved_tasks"],
        "event_count": event_count,
        "approval_count": approval_count,
        "review_count": review_count,
        "review_signature_count": signature_count,
        "reviewer_trust_policy_bound": trust_evaluation["policy_bound"],
        "reviewer_trust_satisfied": trust_evaluation["satisfied"],
        "reviewer_trust_reviews": trust_evaluation["reviews"],
        "claims_gate_enabled": claims_gate["enabled"],
        "claims_gate_from_task_index": claims_gate["effective_from_task_index"],
        "claims_gate_applies_to_pending_task": (
            claims_gate["enabled"]
            and state["pending_task_id"] is not None
            and state["next_task_index"]
            >= claims_gate["effective_from_task_index"]
        ),
        "evidence_count": evidence_count,
        "supplemental_evidence_count": supplemental_count,
        "task_output_revision_count": task_output_revision_count,
        "report_count": report_count,
        "claims_confirmed": claim_status["claims_confirmed"],
        "claims_file_count": claim_status["claims_file_count"],
        "claim_count": claim_status["claim_count"],
        "unsupported_claim_count": claim_status["unsupported_claim_count"],
        "claim_kind_counts": claim_status["kind_counts"],
        "hashed_file_count": len(manifest["files"]),
        "integrity": "verified",
    }
    if trust_evaluation["policy_bound"]:
        result.update(
            {
                "reviewer_trust_registry_id": trust_evaluation["registry_id"],
                "reviewer_trust_registry_version": trust_evaluation[
                    "registry_version"
                ],
                "reviewer_trust_registry_sha256": trust_evaluation[
                    "registry_sha256"
                ],
                "reviewer_trust_snapshot_sha256": state[
                    "reviewer_trust_snapshot_sha256"
                ],
            }
        )
    if review_records:
        latest_review = review_records[-1]
        latest_trust = (
            review_trust_result(trust_evaluation, latest_review["hash"])
            if trust_evaluation["policy_bound"]
            else None
        )
        result.update(
            {
                "latest_review_id": latest_review["review_id"],
                "latest_review_hash": latest_review["hash"],
                "latest_review_task_id": latest_review["task_id"],
                "latest_review_decision": latest_review["decision"],
                "latest_reviewer": latest_review["reviewer"],
                "latest_review_note": latest_review["note"],
                "latest_review_subject_sha256": latest_review["subject"][
                    "bundle_sha256"
                ],
                "latest_review_trust_required": (
                    latest_trust["required"] if latest_trust is not None else False
                ),
                "latest_review_trust_satisfied": (
                    latest_trust["satisfied"] if latest_trust is not None else True
                ),
                "latest_review_trust_outstanding": (
                    latest_trust["outstanding_requirements"]
                    if latest_trust is not None
                    else []
                ),
            }
        )
    if signature_records:
        latest_signature = signature_records[-1]
        result.update(
            {
                "latest_review_signature_id": latest_signature["signature_id"],
                "latest_signed_review_hash": latest_signature["review_hash"],
                "latest_signer_identity": latest_signature["signer_identity"],
                "latest_signer_fingerprint": latest_signature[
                    "public_key_fingerprint"
                ],
            }
        )
    if state["status"] == "cancelled":
        result.update(
            {
                "cancelled_task_id": state["cancelled_task_id"],
                "cancelled_at": state["cancelled_at"],
                "cancelled_by": state["cancelled_by"],
                "cancellation_reason": state["cancellation_reason"],
            }
        )
    if state["status"] == "rejected":
        result.update(
            {
                "rejected_task_id": state["rejected_task_id"],
                "rejected_at": state["rejected_at"],
                "rejected_by": state["rejected_by"],
                "rejection_reason": state["rejection_reason"],
                "rejection_review_hash": state["rejection_review_hash"],
            }
        )
    return result


def verify_run(run_dir: Path | str) -> dict[str, Any]:
    path = Path(run_dir)
    if path.is_symlink() or not path.is_dir():
        raise IntegrityError(f"Run directory is missing or is a symlink: {path}")
    with run_lock(path):
        return _verified_checkpointed_status(path)


def status_run(run_dir: Path | str) -> dict[str, Any]:
    return verify_run(Path(run_dir))


def claims_status(run_dir: Path | str) -> dict[str, Any]:
    """Return a verified, read-only view of Claim records and summary counts."""
    path = Path(run_dir)
    if path.is_symlink() or not path.is_dir():
        raise IntegrityError(f"Run directory is missing or is a symlink: {path}")
    with run_lock(path):
        status = _verified_checkpointed_status(path)
        state = _load_state(path)
        pack = load_pack(path / PACK_SNAPSHOT).data
        view = verify_claims(
            path,
            run_id=state["run_id"],
            task_ids=[task["task_id"] for task in pack["mission"]["tasks"]],
            include_records=True,
        )
        return {**view, "run_status": status["status"], "integrity": "verified"}


def claims_coverage_status(run_dir: Path | str) -> dict[str, Any]:
    """Read-only per-Task Claim coverage for the Tasks this Run actually executed.

    C2-S4 gates only the pending Task through ``task_claims_coverage``; this Run-level
    report remains read-only and ``all_executed_tasks_confirmed`` is not a resume gate.

    ``verify_run`` deliberately treats a Claims record bound to a superseded Task output
    as an integrity failure, and this function does not change that. But refusing to
    report anything in that state would hide the one fact the operator needs — *which*
    Task requires re-confirmation. So a ``StaleClaimsError`` degrades the reported
    ``integrity`` to ``"stale-claims"`` and still returns coverage. Every other
    integrity failure still propagates.
    """
    path = Path(run_dir)
    if path.is_symlink() or not path.is_dir():
        raise IntegrityError(f"Run directory is missing or is a symlink: {path}")
    with run_lock(path):
        state = _load_state(path)
        pack = load_pack(path / PACK_SNAPSHOT).data
        try:
            verified = _verified_checkpointed_status(path)
            integrity = "verified"
            run_status = verified["status"]
        except StaleClaimsError:
            integrity = "stale-claims"
            run_status = state.get("status")
        view = verify_claims(
            path,
            run_id=state["run_id"],
            task_ids=[task["task_id"] for task in pack["mission"]["tasks"]],
            tolerate_stale=True,
        )
        coverage = claims_coverage(view, state["executed_tasks"])
        return {
            **coverage,
            "run_id": state["run_id"],
            "run_status": run_status,
            "integrity": integrity,
        }


def _output_content(run_dir: Path, output: dict[str, Any]) -> str:
    artifact = _verified_review_artifact(
        run_dir,
        output.get("path"),
        output.get("sha256"),
    )
    if artifact.suffix.casefold() == ".json":
        value = read_json(artifact)
        content = value.get("content") if isinstance(value, dict) else None
        if not isinstance(content, str):
            raise IntegrityError(f"Effective JSON output has no content: {artifact}")
        return content
    try:
        return artifact.read_text(encoding="utf-8")
    except OSError as exc:
        raise IntegrityError(f"Cannot read effective output {artifact}: {exc}") from exc


def _resolve_effective_task_outputs_unlocked(run_dir: Path) -> list[dict[str, Any]]:
    pack = load_pack(run_dir / PACK_SNAPSHOT).data
    state = _load_state(run_dir)
    _, _, review_records = _read_review_records(run_dir)
    _, _, signature_records = _read_review_signature_records(run_dir)
    task_ids = [task["task_id"] for task in pack["mission"]["tasks"]]
    claims_gate_enabled = state.get("claims_gate_enabled", False)
    claims_gate_from_task_index = state.get("claims_gate_from_task_index")
    claims_view: dict[str, Any] | None = None
    if claims_gate_enabled:
        claims_view = verify_claims(
            run_dir,
            run_id=state["run_id"],
            task_ids=task_ids,
        )
    trust_evaluation = _reviewer_trust_evaluation(
        run_dir,
        state,
        task_ids,
        review_records,
        signature_records,
    )
    trusted_review_hashes = {
        item["review_hash"]
        for item in trust_evaluation["reviews"]
        if item["satisfied"]
    }
    approved_reviews = [
        review
        for review in review_records
        if review.get("decision") == "Approved"
        and (
            not trust_evaluation["policy_bound"]
            or review.get("hash") in trusted_review_hashes
        )
    ]
    results: list[dict[str, Any]] = []
    for task_index, task in enumerate(pack["mission"]["tasks"], start=1):
        report_path = run_dir / "reports" / f"TASK-REPORT-{task_index:02d}.json"
        if not report_path.is_file():
            continue
        report = read_json(report_path)
        original_output = report.get("output") if isinstance(report, dict) else None
        if not isinstance(original_output, dict):
            raise IntegrityError(f"Task Report output is invalid: {report_path}")

        effective_output = dict(original_output)
        effective_source = "original"
        effective_role: str | None = None
        approved_review_id: str | None = None
        approved_review_hash: str | None = None
        revision_of: str | None = None
        claims_gate_allows_promotion = True
        if (
            claims_view is not None
            and type(claims_gate_from_task_index) is int
            and task_index - 1 >= claims_gate_from_task_index
        ):
            coverage = task_claims_coverage(claims_view, task["task_id"])
            claims_gate_allows_promotion = not _claims_gate_reasons(
                coverage,
                task["task_id"],
            )
        for review in approved_reviews:
            if review.get("task_id") != task["task_id"]:
                continue
            if not claims_gate_allows_promotion:
                continue
            approved_review_id = review["review_id"]
            approved_review_hash = review["hash"]
            subject = review.get("subject")
            if not isinstance(subject, dict):
                continue
            latest_revision_id = subject.get("latest_revision_id")
            references = subject.get("supplemental_evidence")
            if not isinstance(latest_revision_id, str) or not isinstance(references, list):
                continue
            reference = next(
                (
                    item
                    for item in references
                    if isinstance(item, dict)
                    and item.get("evidence_id") == latest_revision_id
                ),
                None,
            )
            if reference is None or reference.get("role") not in {
                TASK_OUTPUT_REVISION_ROLE,
                "ai_draft",
            }:
                continue
            effective_output = {
                "class": "Evidence",
                "path": reference["path"],
                "sha256": reference["sha256"],
                "id": reference["evidence_id"],
            }
            effective_source = "approved_revision"
            effective_role = reference["role"]
            revision_of = reference.get("revision_of")

        results.append(
            {
                "task_id": task["task_id"],
                "task_name": task["name"],
                "operation": task["operation"],
                "source": effective_source,
                "effective_id": effective_output["id"],
                "effective_class": effective_output["class"],
                "effective_path": effective_output["path"],
                "effective_sha256": effective_output["sha256"],
                "effective_role": effective_role,
                "content": _output_content(run_dir, effective_output),
                "original_output": dict(original_output),
                "revision_of": revision_of,
                "approved_review_id": approved_review_id,
                "approved_review_hash": approved_review_hash,
                "approved_review_trust_satisfied": (
                    True if approved_review_hash is not None else None
                ),
            }
        )
    return results


def _build_effective_output_manifest_unlocked(
    run_dir: Path,
    status: dict[str, Any],
) -> dict[str, Any]:
    outputs = _resolve_effective_task_outputs_unlocked(run_dir)
    state = _load_state(run_dir)
    _, signature_tail, signature_records = _read_review_signature_records(run_dir)
    trust_by_review = {
        item["review_hash"]: item for item in status["reviewer_trust_reviews"]
    }
    for output in outputs:
        trust = trust_by_review.get(output.get("approved_review_hash"))
        trusted_by_id = {
            item["signature_id"]: item
            for item in trust.get("trusted_signatures", [])
        } if trust is not None else {}
        output["approved_review_signatures"] = [
            {
                "signature_id": record["signature_id"],
                "signer_identity": record["signer_identity"],
                "public_key_fingerprint": record["public_key_fingerprint"],
                "signature_record_hash": record["hash"],
                "policy_trusted": (
                    record["signature_id"] in trusted_by_id
                    if status["reviewer_trust_policy_bound"]
                    else None
                ),
                "reviewer_role": (
                    trusted_by_id[record["signature_id"]]["role"]
                    if record["signature_id"] in trusted_by_id
                    else None
                ),
            }
            for record in signature_records
            if record["review_hash"] == output.get("approved_review_hash")
        ]
    unsigned = {
        "schema_version": EFFECTIVE_OUTPUT_MANIFEST_SCHEMA,
        "resolution_rule": EFFECTIVE_OUTPUT_RESOLUTION_RULE,
        "run_id": status["run_id"],
        "run_status": status["status"],
        "canonical_snapshot_sha256": sha256_file(run_dir / "HASHES.json"),
        "review_chain_tail_sha256": state.get("review_tail_hash", ZERO_HASH),
        "review_signature_chain_tail_sha256": signature_tail,
        "review_signature_count": len(signature_records),
        "reviewer_trust_policy_bound": status["reviewer_trust_policy_bound"],
        "reviewer_trust_satisfied": status["reviewer_trust_satisfied"],
        "reviewer_trust_registry_id": status.get("reviewer_trust_registry_id"),
        "reviewer_trust_registry_version": status.get(
            "reviewer_trust_registry_version"
        ),
        "reviewer_trust_registry_sha256": status.get(
            "reviewer_trust_registry_sha256"
        ),
        "reviewer_trust_snapshot_sha256": status.get(
            "reviewer_trust_snapshot_sha256"
        ),
        "output_count": len(outputs),
        "approved_revision_count": sum(
            item["source"] == "approved_revision" for item in outputs
        ),
        "outputs": outputs,
    }
    return {
        **unsigned,
        "manifest_sha256": sha256_text(canonical_json_text(unsigned)),
    }


def verify_effective_output_manifest(manifest: Any) -> dict[str, Any]:
    """Verify one detached Effective Output Manifest and return a compact result."""
    if not isinstance(manifest, dict):
        raise IntegrityError("Effective Output Manifest must be an object")
    schema_version = manifest.get("schema_version")
    if schema_version not in {
        LEGACY_EFFECTIVE_OUTPUT_MANIFEST_SCHEMA,
        EFFECTIVE_OUTPUT_MANIFEST_SCHEMA,
    }:
        raise IntegrityError("Effective Output Manifest schema is unsupported")
    claimed_hash = manifest.get("manifest_sha256")
    if not isinstance(claimed_hash, str) or re.fullmatch(r"[0-9a-f]{64}", claimed_hash) is None:
        raise IntegrityError("Effective Output Manifest hash is invalid")
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if sha256_text(canonical_json_text(unsigned)) != claimed_hash:
        raise IntegrityError("Effective Output Manifest hash does not match its content")
    for field in (
        "canonical_snapshot_sha256",
        "review_chain_tail_sha256",
        "review_signature_chain_tail_sha256",
    ):
        value = manifest.get(field)
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise IntegrityError(f"Effective Output Manifest {field} is invalid")
    signature_count = manifest.get("review_signature_count")
    if not isinstance(signature_count, int) or signature_count < 0:
        raise IntegrityError("Effective Output Manifest Reviewer signature count is invalid")
    policy_bound = manifest.get("reviewer_trust_policy_bound")
    policy_satisfied = manifest.get("reviewer_trust_satisfied")
    if schema_version == EFFECTIVE_OUTPUT_MANIFEST_SCHEMA and (
        not isinstance(policy_bound, bool) or not isinstance(policy_satisfied, bool)
    ):
        raise IntegrityError("Effective Output Manifest trust-policy status is invalid")
    if schema_version == EFFECTIVE_OUTPUT_MANIFEST_SCHEMA and policy_bound:
        registry_id = manifest.get("reviewer_trust_registry_id")
        registry_version = manifest.get("reviewer_trust_registry_version")
        if not isinstance(registry_id, str) or not registry_id:
            raise IntegrityError("Effective Output Manifest trust registry ID is invalid")
        if (
            not isinstance(registry_version, int)
            or isinstance(registry_version, bool)
            or registry_version < 1
        ):
            raise IntegrityError(
                "Effective Output Manifest trust registry version is invalid"
            )
        for field in (
            "reviewer_trust_registry_sha256",
            "reviewer_trust_snapshot_sha256",
        ):
            value = manifest.get(field)
            if (
                not isinstance(value, str)
                or re.fullmatch(r"[0-9a-f]{64}", value) is None
            ):
                raise IntegrityError(f"Effective Output Manifest {field} is invalid")
    elif schema_version == EFFECTIVE_OUTPUT_MANIFEST_SCHEMA and any(
        manifest.get(field) is not None
        for field in (
            "reviewer_trust_registry_id",
            "reviewer_trust_registry_version",
            "reviewer_trust_registry_sha256",
            "reviewer_trust_snapshot_sha256",
        )
    ):
        raise IntegrityError("Unbound Effective Output Manifest has trust registry fields")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or manifest.get("output_count") != len(outputs):
        raise IntegrityError("Effective Output Manifest output count is invalid")
    task_ids: set[str] = set()
    for output in outputs:
        if not isinstance(output, dict):
            raise IntegrityError("Effective Output Manifest output must be an object")
        task_id = output.get("task_id")
        source = output.get("source")
        effective_hash = output.get("effective_sha256")
        if not isinstance(task_id, str) or not task_id or task_id in task_ids:
            raise IntegrityError("Effective Output Manifest Task identity is invalid")
        if source not in {"original", "approved_revision"}:
            raise IntegrityError("Effective Output Manifest source is invalid")
        if (
            not isinstance(effective_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", effective_hash) is None
        ):
            raise IntegrityError("Effective Output Manifest artifact hash is invalid")
        task_ids.add(task_id)
    approved_count = sum(
        output.get("source") == "approved_revision" for output in outputs
    )
    if manifest.get("approved_revision_count") != approved_count:
        raise IntegrityError("Effective Output Manifest approved count is invalid")
    return {
        "schema_version": manifest["schema_version"],
        "run_id": manifest.get("run_id"),
        "manifest_sha256": claimed_hash,
        "output_count": len(outputs),
        "approved_revision_count": approved_count,
        "integrity": "verified",
    }


def _effective_manifest_signature_payload(
    manifest: dict[str, Any],
    *,
    signer_identity: str,
    public_key_fingerprint: str,
) -> str:
    payload = {
        "schema_version": EFFECTIVE_MANIFEST_SIGNATURE_PAYLOAD_SCHEMA,
        "namespace": EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE,
        "manifest_schema_version": manifest["schema_version"],
        "manifest_sha256": manifest["manifest_sha256"],
        "canonical_snapshot_sha256": manifest["canonical_snapshot_sha256"],
        "run_id": manifest["run_id"],
        "signer_identity": signer_identity,
        "public_key_fingerprint": public_key_fingerprint,
    }
    return canonical_json_text(payload) + "\n"


def build_effective_manifest_signature_request(
    manifest: Any,
    *,
    signer_identity: str,
    public_key: str,
) -> dict[str, Any]:
    verified = verify_effective_output_manifest(manifest)
    assert isinstance(manifest, dict)
    try:
        identity = normalize_signer_identity(signer_identity)
        normalized_key = normalize_ed25519_public_key(public_key)
        fingerprint = ed25519_public_key_fingerprint(normalized_key)
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    payload = _effective_manifest_signature_payload(
        manifest,
        signer_identity=identity,
        public_key_fingerprint=fingerprint,
    )
    return {
        "schema_version": EFFECTIVE_MANIFEST_SIGNATURE_PAYLOAD_SCHEMA,
        "namespace": EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE,
        "run_id": verified["run_id"],
        "manifest_sha256": verified["manifest_sha256"],
        "signer_identity": identity,
        "public_key": normalized_key,
        "public_key_fingerprint": fingerprint,
        "payload": payload,
        "payload_sha256": sha256_text(payload),
    }


def sign_effective_output_manifest(
    manifest: Any,
    *,
    signer_identity: str,
    private_key_path: Path | str,
    public_key_path: Path | str,
) -> dict[str, Any]:
    try:
        public_key = load_ed25519_public_key(public_key_path)
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    request = build_effective_manifest_signature_request(
        manifest,
        signer_identity=signer_identity,
        public_key=public_key,
    )
    try:
        signature = sign_ssh_payload(
            request["payload"],
            private_key_path=private_key_path,
            namespace=EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE,
        )
    except SignatureError as exc:
        raise RunStateError(str(exc)) from exc
    unsigned = {
        "schema_version": EFFECTIVE_MANIFEST_SIGNATURE_SCHEMA,
        "namespace": EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE,
        "run_id": request["run_id"],
        "manifest_sha256": request["manifest_sha256"],
        "signer_identity": request["signer_identity"],
        "public_key": request["public_key"],
        "public_key_fingerprint": request["public_key_fingerprint"],
        "payload_sha256": request["payload_sha256"],
        "signature": signature,
    }
    return {
        **unsigned,
        "attestation_sha256": sha256_text(canonical_json_text(unsigned)),
    }


def verify_effective_output_manifest_signature(
    manifest: Any,
    attestation: Any,
) -> dict[str, Any]:
    verified = verify_effective_output_manifest(manifest)
    if not isinstance(manifest, dict) or not isinstance(attestation, dict):
        raise IntegrityError("Effective Manifest signature attestation must be an object")
    if attestation.get("schema_version") != EFFECTIVE_MANIFEST_SIGNATURE_SCHEMA:
        raise IntegrityError("Effective Manifest signature schema is unsupported")
    claimed_hash = attestation.get("attestation_sha256")
    unsigned = {
        key: value for key, value in attestation.items() if key != "attestation_sha256"
    }
    if (
        not isinstance(claimed_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", claimed_hash) is None
        or sha256_text(canonical_json_text(unsigned)) != claimed_hash
    ):
        raise IntegrityError("Effective Manifest signature attestation Hash is invalid")
    if (
        attestation.get("namespace") != EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE
        or attestation.get("run_id") != verified["run_id"]
        or attestation.get("manifest_sha256") != verified["manifest_sha256"]
    ):
        raise IntegrityError("Effective Manifest signature target does not match")
    try:
        identity = normalize_signer_identity(attestation.get("signer_identity", ""))
        public_key = normalize_ed25519_public_key(attestation.get("public_key", ""))
        fingerprint = ed25519_public_key_fingerprint(public_key)
        signature = normalize_ssh_signature(attestation.get("signature", ""))
    except SignatureError as exc:
        raise IntegrityError(f"Effective Manifest signature metadata is invalid: {exc}") from exc
    if attestation.get("public_key_fingerprint") != fingerprint:
        raise IntegrityError("Effective Manifest signer fingerprint mismatch")
    payload = _effective_manifest_signature_payload(
        manifest,
        signer_identity=identity,
        public_key_fingerprint=fingerprint,
    )
    if attestation.get("payload_sha256") != sha256_text(payload):
        raise IntegrityError("Effective Manifest signature payload Hash mismatch")
    try:
        verify_ssh_signature(
            payload,
            signature,
            public_key=public_key,
            signer_identity=identity,
            namespace=EFFECTIVE_MANIFEST_SIGNATURE_NAMESPACE,
        )
    except SignatureError as exc:
        raise IntegrityError(f"Effective Manifest Ed25519 signature is invalid: {exc}") from exc
    return {
        "schema_version": attestation["schema_version"],
        "run_id": verified["run_id"],
        "manifest_sha256": verified["manifest_sha256"],
        "attestation_sha256": claimed_hash,
        "signer_identity": identity,
        "public_key_fingerprint": fingerprint,
        "integrity": "verified",
    }


def build_effective_output_manifest(run_dir: Path | str) -> dict[str, Any]:
    """Build a deterministic, verified manifest without modifying Run artifacts."""
    path = Path(run_dir)
    with run_lock(path):
        status = _verified_checkpointed_status(path)
        return _build_effective_output_manifest_unlocked(path, status)


def resolve_effective_task_outputs(run_dir: Path | str) -> list[dict[str, Any]]:
    """Resolve each executed Task to its latest Reviewer-Approved output."""
    return build_effective_output_manifest(run_dir)["outputs"]


def _read_snapshot_text(path: Path) -> str:
    if path.stat().st_size > MAX_SNAPSHOT_ARTIFACT_BYTES:
        raise IntegrityError(
            f"Snapshot artifact exceeds {MAX_SNAPSHOT_ARTIFACT_BYTES} bytes: {path}"
        )
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise IntegrityError(f"Cannot read UTF-8 snapshot artifact {path}: {exc}") from exc


def read_effective_run_snapshot(run_dir: Path | str) -> dict[str, Any]:
    """Read one verified Run view while holding one cross-process lock."""
    path = Path(run_dir)
    with run_lock(path):
        status = _verified_checkpointed_status(path)
        pack = load_pack(path / PACK_SNAPSHOT).data
        manifest = _build_effective_output_manifest_unlocked(path, status)
        _, _, reviews = _read_review_records(path)
        evidence: list[dict[str, Any]] = []
        for artifact in sorted((path / "evidence").glob("*.json")):
            value = read_json(artifact)
            if not isinstance(value, dict):
                raise IntegrityError(f"Evidence format is invalid: {artifact}")
            evidence.append(
                {
                    "path": artifact.relative_to(path).as_posix(),
                    "data": value,
                }
            )
        reports: list[dict[str, Any]] = []
        for artifact in sorted((path / "reports").glob("*")):
            if artifact.is_symlink() or not artifact.is_file():
                continue
            reports.append(
                {
                    "path": artifact.relative_to(path).as_posix(),
                    "content": _read_snapshot_text(artifact),
                }
            )
        return {
            "status": status,
            "pack": pack,
            "effective_output_manifest": manifest,
            "evidence": evidence,
            "reports": reports,
            "reviews": reviews,
            "review_signatures": _read_review_signature_records(path)[2],
            "reviewer_trust_registry": (
                read_json(path / REVIEWER_TRUST_SNAPSHOT)
                if (path / REVIEWER_TRUST_SNAPSHOT).is_file()
                else None
            ),
        }
