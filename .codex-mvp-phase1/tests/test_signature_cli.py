from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.cli import main
from research_os_mvp.runtime import (
    approve_run,
    build_effective_output_manifest,
    create_run,
)
from tests.helpers import EXAMPLE_PACK

SSH_KEYGEN = shutil.which("ssh-keygen")


@unittest.skipUnless(SSH_KEYGEN, "OpenSSH ssh-keygen is not installed")
class SignatureCLITests(unittest.TestCase):
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
                "-f",
                str(private_key),
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return private_key, Path(f"{private_key}.pub")

    def test_sign_review_and_effective_manifest_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "cli-reviewer")
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-signature")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            signed_output = io.StringIO()
            with contextlib.redirect_stdout(signed_output):
                signed_exit = main(
                    [
                        "sign-review",
                        str(run_dir),
                        "--identity",
                        "reviewer@example",
                        "--key",
                        str(private_key),
                        "--public-key",
                        str(public_key),
                        "--review-hash",
                        approved["latest_review_hash"],
                    ]
                )
            self.assertEqual(signed_exit, 0)
            self.assertEqual(json.loads(signed_output.getvalue())["review_signature_count"], 1)

            manifest_path = root / "effective-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    build_effective_output_manifest(run_dir),
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            attestation_path = root / "effective-manifest.signature.json"
            sign_output = io.StringIO()
            with contextlib.redirect_stdout(sign_output):
                sign_exit = main(
                    [
                        "sign-effective-manifest",
                        str(manifest_path),
                        "--identity",
                        "reviewer@example",
                        "--key",
                        str(private_key),
                        "--public-key",
                        str(public_key),
                        "--output",
                        str(attestation_path),
                    ]
                )
            self.assertEqual(sign_exit, 0)
            self.assertTrue(attestation_path.is_file())

            verify_output = io.StringIO()
            with contextlib.redirect_stdout(verify_output):
                verify_exit = main(
                    [
                        "verify-effective-manifest-signature",
                        str(manifest_path),
                        str(attestation_path),
                    ]
                )
            self.assertEqual(verify_exit, 0)
            self.assertEqual(json.loads(verify_output.getvalue())["integrity"], "verified")

    def test_offline_review_signature_request_can_be_attached(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "offline-reviewer")
            status = create_run(EXAMPLE_PACK, root / "runs", "run-cli-offline-signature")
            run_dir = root / "runs" / status["run_id"]
            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            payload_path = root / "review.payload"
            request_output = io.StringIO()
            with contextlib.redirect_stdout(request_output):
                request_exit = main(
                    [
                        "review-signing-request",
                        str(run_dir),
                        "--identity",
                        "reviewer@example",
                        "--public-key",
                        str(public_key),
                        "--review-hash",
                        approved["latest_review_hash"],
                        "--output",
                        str(payload_path),
                    ]
                )
            self.assertEqual(request_exit, 0)
            signed = subprocess.run(
                [
                    str(SSH_KEYGEN),
                    "-Y",
                    "sign",
                    "-f",
                    str(private_key),
                    "-n",
                    "research-os-review",
                    str(payload_path),
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(signed.returncode, 0, signed.stderr)
            signature_path = Path(f"{payload_path}.sig")

            attach_output = io.StringIO()
            with contextlib.redirect_stdout(attach_output):
                attach_exit = main(
                    [
                        "attach-review-signature",
                        str(run_dir),
                        "--identity",
                        "reviewer@example",
                        "--public-key",
                        str(public_key),
                        "--signature",
                        str(signature_path),
                        "--review-hash",
                        approved["latest_review_hash"],
                    ]
                )
            self.assertEqual(attach_exit, 0)
            self.assertEqual(json.loads(attach_output.getvalue())["review_signature_count"], 1)


if __name__ == "__main__":
    unittest.main()
