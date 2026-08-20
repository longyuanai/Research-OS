from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from research_os_mvp.errors import SignatureError, TrustPolicyError
from research_os_mvp.integrity import canonical_json_text, sha256_text
from research_os_mvp.signing import (
    ed25519_public_key_fingerprint,
    normalize_ed25519_public_key,
    normalize_signer_identity,
)

REVIEWER_TRUST_SCHEMA = "research-os-mvp-reviewer-trust/0.1"
REVIEW_DECISIONS = {"Approved", "Changes Requested", "Rejected"}
MAX_TRUST_KEYS = 100
MAX_TRUST_REQUIREMENTS = 100
MAX_ROLE_CHARS = 50
MAX_REGISTRY_ID_CHARS = 100
MAX_TASK_ID_CHARS = 100
UTC_TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"
)
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ROLE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")


def reviewer_trust_registry_template() -> dict[str, Any]:
    """Return an editable project-level Reviewer trust registry draft."""
    return {
        "schema_version": REVIEWER_TRUST_SCHEMA,
        "registry_id": "project-reviewers",
        "version": 1,
        "keys": [
            {
                "identity": "reviewer@example",
                "role": "reviewer",
                "public_key": "ssh-ed25519 REPLACE_WITH_BASE64_PUBLIC_KEY",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2027-01-01T00:00:00Z",
            }
        ],
        "requirements": [
            {
                "task_id": "*",
                "decision": "Approved",
                "role": "reviewer",
                "minimum_signatures": 1,
            }
        ],
    }


def _utc_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or UTC_TIMESTAMP_PATTERN.fullmatch(value) is None:
        raise TrustPolicyError(f"{field} must be an ISO 8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise TrustPolicyError(f"{field} is not a valid UTC timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise TrustPolicyError(f"{field} must use UTC")
    return parsed


def _identifier(value: Any, field: str, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > maximum
        or IDENTIFIER_PATTERN.fullmatch(value) is None
    ):
        raise TrustPolicyError(
            f"{field} must use 1-{maximum} ASCII letters, digits, or ._-"
        )
    return value


def _role(value: Any, field: str = "role") -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_ROLE_CHARS
        or ROLE_PATTERN.fullmatch(value) is None
    ):
        raise TrustPolicyError(
            f"{field} must use 1-{MAX_ROLE_CHARS} ASCII letters, digits, or ._-"
        )
    return value


def _normalized_unsigned_registry(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrustPolicyError("Reviewer trust registry must be an object")
    allowed = {
        "schema_version",
        "registry_id",
        "version",
        "keys",
        "requirements",
        "registry_sha256",
    }
    unknown = set(value) - allowed
    if unknown:
        raise TrustPolicyError(
            f"Reviewer trust registry has unsupported fields: {sorted(unknown)}"
        )
    if value.get("schema_version") != REVIEWER_TRUST_SCHEMA:
        raise TrustPolicyError("Reviewer trust registry schema is unsupported")
    registry_id = _identifier(
        value.get("registry_id"),
        "registry_id",
        MAX_REGISTRY_ID_CHARS,
    )
    version = value.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise TrustPolicyError("Reviewer trust registry version must be a positive integer")

    raw_keys = value.get("keys")
    if not isinstance(raw_keys, list) or not 1 <= len(raw_keys) <= MAX_TRUST_KEYS:
        raise TrustPolicyError("Reviewer trust registry must contain 1-100 keys")
    keys: list[dict[str, Any]] = []
    fingerprints: set[str] = set()
    roles: dict[str, int] = {}
    for index, raw_key in enumerate(raw_keys, start=1):
        if not isinstance(raw_key, dict):
            raise TrustPolicyError(f"keys[{index}] must be an object")
        key_allowed = {
            "identity",
            "role",
            "public_key",
            "public_key_fingerprint",
            "valid_from",
            "valid_until",
            "revoked_at",
        }
        key_unknown = set(raw_key) - key_allowed
        if key_unknown:
            raise TrustPolicyError(
                f"keys[{index}] has unsupported fields: {sorted(key_unknown)}"
            )
        try:
            identity = normalize_signer_identity(raw_key.get("identity", ""))
            public_key = normalize_ed25519_public_key(raw_key.get("public_key", ""))
            fingerprint = ed25519_public_key_fingerprint(public_key)
        except SignatureError as exc:
            raise TrustPolicyError(f"keys[{index}] is invalid: {exc}") from exc
        claimed_fingerprint = raw_key.get("public_key_fingerprint")
        if claimed_fingerprint is not None and claimed_fingerprint != fingerprint:
            raise TrustPolicyError(f"keys[{index}] public-key fingerprint does not match")
        if fingerprint in fingerprints:
            raise TrustPolicyError("Reviewer trust registry contains a duplicated public key")
        fingerprints.add(fingerprint)
        role = _role(raw_key.get("role"), f"keys[{index}].role")
        valid_from = raw_key.get("valid_from")
        valid_from_time = _utc_datetime(valid_from, f"keys[{index}].valid_from")
        valid_until = raw_key.get("valid_until")
        revoked_at = raw_key.get("revoked_at")
        if valid_until is not None:
            valid_until_time = _utc_datetime(
                valid_until, f"keys[{index}].valid_until"
            )
            if valid_until_time < valid_from_time:
                raise TrustPolicyError(
                    f"keys[{index}].valid_until is earlier than valid_from"
                )
        if revoked_at is not None:
            revoked_time = _utc_datetime(revoked_at, f"keys[{index}].revoked_at")
            if revoked_time < valid_from_time:
                raise TrustPolicyError(
                    f"keys[{index}].revoked_at is earlier than valid_from"
                )
        normalized_key: dict[str, Any] = {
            "identity": identity,
            "role": role,
            "public_key": public_key,
            "public_key_fingerprint": fingerprint,
            "valid_from": valid_from,
        }
        if valid_until is not None:
            normalized_key["valid_until"] = valid_until
        if revoked_at is not None:
            normalized_key["revoked_at"] = revoked_at
        keys.append(normalized_key)
        roles[role] = roles.get(role, 0) + 1

    raw_requirements = value.get("requirements")
    if (
        not isinstance(raw_requirements, list)
        or not 1 <= len(raw_requirements) <= MAX_TRUST_REQUIREMENTS
    ):
        raise TrustPolicyError("Reviewer trust registry must contain 1-100 requirements")
    requirements: list[dict[str, Any]] = []
    selectors: set[tuple[str, str, str]] = set()
    for index, raw_requirement in enumerate(raw_requirements, start=1):
        if not isinstance(raw_requirement, dict):
            raise TrustPolicyError(f"requirements[{index}] must be an object")
        requirement_allowed = {"task_id", "decision", "role", "minimum_signatures"}
        requirement_unknown = set(raw_requirement) - requirement_allowed
        if requirement_unknown:
            raise TrustPolicyError(
                f"requirements[{index}] has unsupported fields: "
                f"{sorted(requirement_unknown)}"
            )
        raw_task_id = raw_requirement.get("task_id")
        task_id = (
            "*"
            if raw_task_id == "*"
            else _identifier(
                raw_task_id,
                f"requirements[{index}].task_id",
                MAX_TASK_ID_CHARS,
            )
        )
        decision = raw_requirement.get("decision")
        if decision not in REVIEW_DECISIONS:
            raise TrustPolicyError(f"requirements[{index}].decision is unsupported")
        role = _role(raw_requirement.get("role"), f"requirements[{index}].role")
        minimum = raw_requirement.get("minimum_signatures")
        if (
            not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or minimum < 1
            or minimum > roles.get(role, 0)
        ):
            raise TrustPolicyError(
                f"requirements[{index}].minimum_signatures exceeds registered {role} keys"
            )
        selector = (task_id, decision, role)
        if selector in selectors:
            raise TrustPolicyError("Reviewer trust registry has a duplicated requirement")
        selectors.add(selector)
        requirements.append(
            {
                "task_id": task_id,
                "decision": decision,
                "role": role,
                "minimum_signatures": minimum,
            }
        )

    return {
        "schema_version": REVIEWER_TRUST_SCHEMA,
        "registry_id": registry_id,
        "version": version,
        "keys": keys,
        "requirements": requirements,
    }


def seal_reviewer_trust_registry(value: Any) -> dict[str, Any]:
    """Normalize a draft registry and add its canonical self-hash."""
    unsigned = _normalized_unsigned_registry(value)
    return {
        **unsigned,
        "registry_sha256": sha256_text(canonical_json_text(unsigned)),
    }


def validate_reviewer_trust_registry(value: Any) -> dict[str, Any]:
    """Validate and normalize a sealed, self-identifying trust registry."""
    sealed = seal_reviewer_trust_registry(value)
    claimed = value.get("registry_sha256") if isinstance(value, dict) else None
    if claimed != sealed["registry_sha256"]:
        raise TrustPolicyError(
            "Reviewer trust registry hash does not match its canonical content"
        )
    return sealed


def validate_registry_task_scope(
    registry: dict[str, Any],
    task_ids: list[str],
) -> None:
    known = set(task_ids)
    unknown = sorted(
        {
            requirement["task_id"]
            for requirement in registry["requirements"]
            if requirement["task_id"] != "*"
            and requirement["task_id"] not in known
        }
    )
    if unknown:
        raise TrustPolicyError(
            f"Reviewer trust registry references unknown Run Tasks: {unknown}"
        )


def _signature_key_status(
    signature: dict[str, Any],
    key: dict[str, Any],
) -> tuple[bool, str | None]:
    if signature.get("signer_identity") != key["identity"]:
        return False, "identity_mismatch"
    if signature.get("public_key") != key["public_key"]:
        return False, "public_key_mismatch"
    try:
        signed_at = _utc_datetime(signature.get("at"), "signature.at")
    except TrustPolicyError:
        return False, "invalid_signature_time"
    if signed_at < _utc_datetime(key["valid_from"], "key.valid_from"):
        return False, "not_yet_valid"
    valid_until = key.get("valid_until")
    if valid_until is not None and signed_at > _utc_datetime(
        valid_until, "key.valid_until"
    ):
        return False, "expired"
    revoked_at = key.get("revoked_at")
    if revoked_at is not None and signed_at >= _utc_datetime(
        revoked_at, "key.revoked_at"
    ):
        return False, "revoked"
    return True, None


def evaluate_reviewer_trust(
    registry: dict[str, Any],
    reviews: list[dict[str, Any]],
    signatures: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate cryptographically verified signatures against one trust registry."""
    normalized = validate_reviewer_trust_registry(registry)
    keys_by_fingerprint = {
        key["public_key_fingerprint"]: key for key in normalized["keys"]
    }
    review_results: list[dict[str, Any]] = []
    for review in reviews:
        review_hash = review.get("hash")
        matching_requirements = [
            requirement
            for requirement in normalized["requirements"]
            if requirement["decision"] == review.get("decision")
            and requirement["task_id"] in {"*", review.get("task_id")}
        ]
        trusted: list[dict[str, Any]] = []
        untrusted: list[dict[str, Any]] = []
        for signature in signatures:
            if signature.get("review_hash") != review_hash:
                continue
            fingerprint = signature.get("public_key_fingerprint")
            key = keys_by_fingerprint.get(fingerprint)
            if key is None:
                untrusted.append(
                    {
                        "signature_id": signature.get("signature_id"),
                        "public_key_fingerprint": fingerprint,
                        "reason": "unregistered_key",
                    }
                )
                continue
            accepted, reason = _signature_key_status(signature, key)
            detail = {
                "signature_id": signature.get("signature_id"),
                "signer_identity": signature.get("signer_identity"),
                "public_key_fingerprint": fingerprint,
                "role": key["role"],
                "signature_record_hash": signature.get("hash"),
            }
            if accepted:
                trusted.append(detail)
            else:
                untrusted.append({**detail, "reason": reason})

        requirement_results: list[dict[str, Any]] = []
        outstanding: list[dict[str, Any]] = []
        for requirement in matching_requirements:
            observed = len(
                {
                    item["public_key_fingerprint"]
                    for item in trusted
                    if item["role"] == requirement["role"]
                }
            )
            required = requirement["minimum_signatures"]
            result = {
                **requirement,
                "observed_signatures": observed,
                "satisfied": observed >= required,
            }
            requirement_results.append(result)
            if observed < required:
                outstanding.append(
                    {
                        "role": requirement["role"],
                        "required_signatures": required,
                        "observed_signatures": observed,
                        "missing_signatures": required - observed,
                    }
                )
        review_results.append(
            {
                "review_id": review.get("review_id"),
                "review_hash": review_hash,
                "task_id": review.get("task_id"),
                "decision": review.get("decision"),
                "required": bool(matching_requirements),
                "satisfied": not outstanding,
                "requirements": requirement_results,
                "outstanding_requirements": outstanding,
                "trusted_signatures": trusted,
                "untrusted_signatures": untrusted,
            }
        )
    return {
        "policy_bound": True,
        "registry_id": normalized["registry_id"],
        "registry_version": normalized["version"],
        "registry_sha256": normalized["registry_sha256"],
        "satisfied": all(item["satisfied"] for item in review_results),
        "reviews": review_results,
    }


def review_trust_result(
    evaluation: dict[str, Any],
    review_hash: str,
) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in evaluation.get("reviews", [])
            if item.get("review_hash") == review_hash
        ),
        None,
    )
