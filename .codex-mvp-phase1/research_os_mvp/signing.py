from __future__ import annotations

import base64
import binascii
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from research_os_mvp.errors import SignatureError
from research_os_mvp.integrity import write_text_atomic

SSH_ED25519 = "ssh-ed25519"
MAX_PUBLIC_KEY_CHARS = 1_000
MAX_SIGNATURE_CHARS = 16_000
MAX_SIGNER_IDENTITY_CHARS = 100
SSH_OPERATION_TIMEOUT_SECONDS = 30


def normalize_signer_identity(value: str) -> str:
    identity = value.strip()
    if (
        not identity
        or len(identity) > MAX_SIGNER_IDENTITY_CHARS
        or re.fullmatch(r"[A-Za-z0-9._@+-]+", identity) is None
    ):
        raise SignatureError(
            "Signer identity must use 1-100 ASCII letters, digits, or ._@+-"
        )
    return identity


def normalize_ed25519_public_key(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_PUBLIC_KEY_CHARS:
        raise SignatureError("Ed25519 public key is empty or too large")
    parts = value.strip().split()
    if len(parts) < 2 or parts[0] != SSH_ED25519:
        raise SignatureError("Reviewer public key must be OpenSSH ssh-ed25519")
    try:
        decoded = base64.b64decode(parts[1], validate=True)
    except (ValueError, binascii.Error) as exc:
        raise SignatureError("Reviewer public key base64 is invalid") from exc
    key_type_length = len(SSH_ED25519)
    expected_prefix = key_type_length.to_bytes(4, "big") + SSH_ED25519.encode("ascii")
    expected_size = len(expected_prefix) + 4 + 32
    if (
        len(decoded) != expected_size
        or not decoded.startswith(expected_prefix)
        or decoded[len(expected_prefix) : len(expected_prefix) + 4]
        != (32).to_bytes(4, "big")
    ):
        raise SignatureError("Reviewer public key is not a valid Ed25519 key blob")
    return f"{SSH_ED25519} {parts[1]}"


def ed25519_public_key_fingerprint(public_key: str) -> str:
    normalized = normalize_ed25519_public_key(public_key)
    decoded = base64.b64decode(normalized.split()[1], validate=True)
    digest = base64.b64encode(hashlib.sha256(decoded).digest()).decode("ascii")
    return f"SHA256:{digest.rstrip('=')}"


def load_ed25519_public_key(path: Path | str) -> str:
    public_path = Path(path)
    if public_path.is_symlink() or not public_path.is_file():
        raise SignatureError("Reviewer public key path must be a regular file")
    if public_path.stat().st_size > MAX_PUBLIC_KEY_CHARS:
        raise SignatureError("Reviewer public key file is too large")
    try:
        parts = public_path.read_bytes().split()
        if len(parts) < 2:
            raise SignatureError("Reviewer public key file is incomplete")
        key_material = b" ".join(parts[:2]).decode("ascii")
        return normalize_ed25519_public_key(key_material)
    except (OSError, UnicodeError) as exc:
        raise SignatureError(f"Cannot read Reviewer public key: {exc}") from exc


def _ssh_keygen() -> str:
    executable = shutil.which("ssh-keygen")
    if executable is None:
        raise SignatureError("OpenSSH ssh-keygen is required for Ed25519 signatures")
    return executable


def normalize_ssh_signature(value: str) -> str:
    signature = value.strip()
    if not signature or len(signature) > MAX_SIGNATURE_CHARS:
        raise SignatureError("OpenSSH signature is empty or too large")
    if not signature.startswith("-----BEGIN SSH SIGNATURE-----") or not signature.endswith(
        "-----END SSH SIGNATURE-----"
    ):
        raise SignatureError("OpenSSH signature armor is invalid")
    return signature + "\n"


def sign_ssh_payload(
    payload: str,
    *,
    private_key_path: Path | str,
    namespace: str,
) -> str:
    key_path = Path(private_key_path)
    if key_path.is_symlink() or not key_path.is_file():
        raise SignatureError("Reviewer private key path must be a regular file")
    executable = _ssh_keygen()
    with tempfile.TemporaryDirectory(prefix="research-os-sign-") as temporary:
        payload_path = Path(temporary) / "payload.txt"
        write_text_atomic(payload_path, payload)
        try:
            result = subprocess.run(
                [
                    executable,
                    "-Y",
                    "sign",
                    "-f",
                    str(key_path),
                    "-n",
                    namespace,
                    str(payload_path),
                ],
                capture_output=True,
                timeout=SSH_OPERATION_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SignatureError(f"OpenSSH signing failed to start: {exc}") from exc
        signature_path = Path(f"{payload_path}.sig")
        if result.returncode != 0 or not signature_path.is_file():
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise SignatureError(f"OpenSSH signing failed: {detail or result.returncode}")
        try:
            signature = signature_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise SignatureError(f"Cannot read OpenSSH signature: {exc}") from exc
    return normalize_ssh_signature(signature)


def verify_ssh_signature(
    payload: str,
    signature: str,
    *,
    public_key: str,
    signer_identity: str,
    namespace: str,
) -> None:
    normalized_key = normalize_ed25519_public_key(public_key)
    normalized_identity = normalize_signer_identity(signer_identity)
    normalized_signature = normalize_ssh_signature(signature)
    executable = _ssh_keygen()
    with tempfile.TemporaryDirectory(prefix="research-os-verify-") as temporary:
        temporary_path = Path(temporary)
        allowed_signers = temporary_path / "allowed_signers"
        signature_path = temporary_path / "payload.sig"
        write_text_atomic(
            allowed_signers,
            f"{normalized_identity} {normalized_key}\n",
        )
        write_text_atomic(signature_path, normalized_signature)
        try:
            result = subprocess.run(
                [
                    executable,
                    "-Y",
                    "verify",
                    "-f",
                    str(allowed_signers),
                    "-I",
                    normalized_identity,
                    "-n",
                    namespace,
                    "-s",
                    str(signature_path),
                ],
                input=payload.encode("utf-8"),
                capture_output=True,
                timeout=SSH_OPERATION_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SignatureError(f"OpenSSH verification failed to start: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SignatureError(
            f"OpenSSH signature verification failed: {detail or result.returncode}"
        )
