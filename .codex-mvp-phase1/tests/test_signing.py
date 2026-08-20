from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.errors import SignatureError
from research_os_mvp.signing import (
    ed25519_public_key_fingerprint,
    load_ed25519_public_key,
    sign_ssh_payload,
    verify_ssh_signature,
)

SSH_KEYGEN = shutil.which("ssh-keygen")


@unittest.skipUnless(SSH_KEYGEN, "OpenSSH ssh-keygen is not installed")
class OpenSSHSigningTests(unittest.TestCase):
    def test_ed25519_payload_round_trip_and_wrong_identity_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key = root / "reviewer_ed25519"
            generated = subprocess.run(
                [
                    str(SSH_KEYGEN),
                    "-q",
                    "-t",
                    "ed25519",
                    "-N",
                    "",
                    "-C",
                    "test-reviewer",
                    "-f",
                    str(private_key),
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            public_key = load_ed25519_public_key(Path(f"{private_key}.pub"))
            payload = "research-os signed payload\n"
            signature = sign_ssh_payload(
                payload,
                private_key_path=private_key,
                namespace="research-os-test",
            )

            verify_ssh_signature(
                payload,
                signature,
                public_key=public_key,
                signer_identity="reviewer@example",
                namespace="research-os-test",
            )
            self.assertTrue(ed25519_public_key_fingerprint(public_key).startswith("SHA256:"))
            with self.assertRaises(SignatureError):
                verify_ssh_signature(
                    payload,
                    signature,
                    public_key=public_key,
                    signer_identity="other-reviewer",
                    namespace="research-os-other",
                )


if __name__ == "__main__":
    unittest.main()
