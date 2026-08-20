from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research_os_mvp.errors import IntegrityError, RunStateError
from research_os_mvp.exporters import export_run_to_obsidian
from research_os_mvp.handoff import render_research_handoff
from research_os_mvp.integrity import (
    canonical_json_bytes,
    canonical_json_text,
    read_json,
    sha256_bytes,
    write_hash_manifest,
    write_json_atomic,
    write_text_atomic,
)
from research_os_mvp.run_store import read_checkpoint
from research_os_mvp.runtime import (
    approve_run,
    attach_review_signature,
    build_effective_output_manifest,
    build_review_signature_request,
    create_run,
    sign_effective_output_manifest,
    sign_review_decision,
    verify_effective_output_manifest_signature,
    verify_run,
)
from research_os_mvp.signing import load_ed25519_public_key, sign_ssh_payload
from research_os_mvp.wizard import render_run_artifacts
from tests.helpers import EXAMPLE_PACK

SSH_KEYGEN = shutil.which("ssh-keygen")


@unittest.skipUnless(SSH_KEYGEN, "OpenSSH ssh-keygen is not installed")
class ReviewerSignatureTests(unittest.TestCase):
    def _generate_key(self, root: Path, name: str) -> tuple[Path, Path]:
        private_key = root / name
        result = subprocess.run(
            [
                str(SSH_KEYGEN),
                "-q",
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                name,
                "-f",
                str(private_key),
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return private_key, Path(f"{private_key}.pub")

    def test_signed_approved_review_is_exposed_in_effective_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "reviewer")
            status = create_run(EXAMPLE_PACK, root / "runs", "run-review-signature")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Human Reviewer", note="accepted")

            signed = sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
                review_hash=approved["latest_review_hash"],
            )
            repeated = sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
                review_hash=approved["latest_review_hash"],
            )
            manifest = build_effective_output_manifest(run_dir)

            self.assertEqual(signed["review_signature_count"], 1)
            self.assertEqual(repeated["review_signature_count"], 1)
            self.assertEqual(manifest["review_signature_count"], 1)
            self.assertEqual(
                manifest["outputs"][0]["approved_review_hash"],
                approved["latest_review_hash"],
            )
            signatures = manifest["outputs"][0]["approved_review_signatures"]
            self.assertEqual(len(signatures), 1)
            self.assertEqual(signatures[0]["signer_identity"], "reviewer@example")
            self.assertTrue(
                signatures[0]["public_key_fingerprint"].startswith("SHA256:")
            )
            fingerprint = signatures[0]["public_key_fingerprint"]
            self.assertIn(fingerprint, render_run_artifacts(run_dir))
            self.assertIn(fingerprint, render_research_handoff(run_dir))
            checkpoint = read_checkpoint(run_dir)
            self.assertEqual(checkpoint["review_signature_count"], 1)
            self.assertEqual(
                checkpoint["review_signature_tail_hash"],
                manifest["review_signature_chain_tail_sha256"],
            )
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)
            exported = export_run_to_obsidian(run_dir, vault)
            export_dir = Path(exported["export_dir"])
            self.assertEqual(exported["review_signatures"], 1)
            self.assertTrue((export_dir / "Reviewer Signatures.md").is_file())
            self.assertTrue((export_dir / "Reviewer Signatures.json").is_file())
            self.assertIn(
                fingerprint,
                (export_dir / "Reviewer Signatures.md").read_text(encoding="utf-8"),
            )
            attestation = sign_effective_output_manifest(
                manifest,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
            )
            verified_attestation = verify_effective_output_manifest_signature(
                manifest,
                attestation,
            )
            self.assertEqual(verified_attestation["integrity"], "verified")
            tampered_attestation = {**attestation, "signer_identity": "other-reviewer"}
            with self.assertRaisesRegex(IntegrityError, "attestation Hash is invalid"):
                verify_effective_output_manifest_signature(
                    manifest,
                    tampered_attestation,
                )

    def test_wrong_public_key_cannot_be_attached(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, _public_key = self._generate_key(root, "reviewer-one")
            _other_private, other_public = self._generate_key(root, "reviewer-two")
            status = create_run(EXAMPLE_PACK, root / "runs", "run-wrong-signature-key")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Human Reviewer", note="accepted")

            with self.assertRaises(RunStateError):
                sign_review_decision(
                    run_dir,
                    signer_identity="reviewer@example",
                    private_key_path=private_key,
                    public_key_path=other_public,
                    review_hash=approved["latest_review_hash"],
                )
            self.assertEqual(verify_run(run_dir)["review_signature_count"], 0)

    def test_concurrent_identical_signature_attachment_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key_path = self._generate_key(root, "concurrent-reviewer")
            public_key = load_ed25519_public_key(public_key_path)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-signature-concurrent")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Human Reviewer", note="accepted")
            request = build_review_signature_request(
                run_dir,
                signer_identity="reviewer@example",
                public_key=public_key,
                review_hash=approved["latest_review_hash"],
            )
            signature = sign_ssh_payload(
                request["payload"],
                private_key_path=private_key,
                namespace=request["namespace"],
            )

            def attach() -> dict:
                return attach_review_signature(
                    run_dir,
                    signer_identity="reviewer@example",
                    public_key=public_key,
                    signature=signature,
                    review_hash=approved["latest_review_hash"],
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(lambda _index: attach(), range(2)))
            self.assertEqual([item["review_signature_count"] for item in results], [1, 1])
            self.assertEqual(verify_run(run_dir)["review_signature_count"], 1)

    def test_cryptographically_tampered_signature_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "tamper-reviewer")
            status = create_run(EXAMPLE_PACK, root / "runs", "run-signature-tamper")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Human Reviewer", note="accepted")
            sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
                review_hash=approved["latest_review_hash"],
            )

            signature_path = run_dir / "review-signatures.jsonl"
            record = json.loads(signature_path.read_text(encoding="utf-8"))
            signature_lines = record["signature"].splitlines()
            body = signature_lines[1]
            signature_lines[1] = ("A" if body[0] != "A" else "B") + body[1:]
            record["signature"] = "\n".join(signature_lines) + "\n"
            unsigned = {key: value for key, value in record.items() if key != "hash"}
            record["hash"] = sha256_bytes(canonical_json_bytes(unsigned))
            write_text_atomic(signature_path, canonical_json_text(record) + "\n")
            state = read_json(run_dir / "state.json")
            state["review_signature_tail_hash"] = record["hash"]
            write_json_atomic(run_dir / "state.json", state)
            write_hash_manifest(run_dir)

            with self.assertRaisesRegex(IntegrityError, "Ed25519 signature is invalid"):
                verify_run(run_dir)

    def test_legacy_unsigned_run_without_signature_tail_still_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            status = create_run(EXAMPLE_PACK, root / "runs", "run-signature-legacy")
            run_dir = root / "runs" / status["run_id"]
            state = read_json(run_dir / "state.json")
            state.pop("review_signature_tail_hash")
            write_json_atomic(run_dir / "state.json", state)
            write_hash_manifest(run_dir)

            verified = verify_run(run_dir)
            self.assertEqual(verified["review_signature_count"], 0)


if __name__ == "__main__":
    unittest.main()
