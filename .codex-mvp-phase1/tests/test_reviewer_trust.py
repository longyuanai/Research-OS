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
from research_os_mvp.errors import RunStateError, TrustPolicyError
from research_os_mvp.exporters import export_run_to_obsidian
from research_os_mvp.handoff import render_research_handoff
from research_os_mvp.integrity import (
    ZERO_HASH,
    canonical_json_text,
    read_json,
    sha256_text,
    write_hash_manifest,
    write_json_atomic,
    write_text_atomic,
)
from research_os_mvp.runtime import (
    approve_run,
    bind_reviewer_trust_registry,
    build_effective_output_manifest,
    create_run,
    resume_run,
    reviewer_trust_status,
    sign_review_decision,
    verify_run,
)
from research_os_mvp.signing import load_ed25519_public_key
from research_os_mvp.trust import (
    REVIEWER_TRUST_SCHEMA,
    reviewer_trust_registry_template,
    seal_reviewer_trust_registry,
    validate_reviewer_trust_registry,
)
from research_os_mvp.wizard import render_run_artifacts, run_wizard
from tests.helpers import EXAMPLE_PACK, ROOT

SSH_KEYGEN = shutil.which("ssh-keygen")


def trust_draft(keys: list[dict], *, role: str = "reviewer") -> dict:
    return {
        "schema_version": REVIEWER_TRUST_SCHEMA,
        "registry_id": "primary-reviewers",
        "version": 1,
        "keys": keys,
        "requirements": [
            {
                "task_id": "*",
                "decision": "Approved",
                "role": role,
                "minimum_signatures": 1,
            }
        ],
    }


class ReviewerTrustRegistryTests(unittest.TestCase):
    def _sealed_registry(self) -> dict:
        public_key = (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBV5SA/o2VXDYc2QUbTlUs5x7x1E"
            "5aiCpzZiPmf8zJt5"
        )
        return seal_reviewer_trust_registry(
            trust_draft(
                [
                    {
                        "identity": "reviewer@example",
                        "role": "reviewer",
                        "public_key": public_key,
                        "valid_from": "2020-01-01T00:00:00Z",
                    }
                ]
            )
        )

    def test_sealed_registry_is_deterministic_and_self_validating(self) -> None:
        public_key = (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBV5SA/o2VXDYc2QUbTlUs5x7x1E"
            "5aiCpzZiPmf8zJt5"
        )
        draft = trust_draft(
            [
                {
                    "identity": "reviewer@example",
                    "role": "reviewer",
                    "public_key": public_key,
                    "valid_from": "2020-01-01T00:00:00Z",
                }
            ]
        )
        first = seal_reviewer_trust_registry(draft)
        second = seal_reviewer_trust_registry(draft)

        self.assertEqual(first, second)
        self.assertEqual(validate_reviewer_trust_registry(first), first)
        tampered = {**first, "version": 2}
        with self.assertRaisesRegex(TrustPolicyError, "hash does not match"):
            validate_reviewer_trust_registry(tampered)

    def test_cli_seals_and_validates_registry(self) -> None:
        public_key = (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBV5SA/o2VXDYc2QUbTlUs5x7x1E"
            "5aiCpzZiPmf8zJt5"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            draft_path = root / "draft.json"
            sealed_path = root / "sealed.json"
            draft_path.write_text(
                json.dumps(
                    trust_draft(
                        [
                            {
                                "identity": "reviewer@example",
                                "role": "reviewer",
                                "public_key": public_key,
                                "valid_from": "2020-01-01T00:00:00Z",
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "seal-reviewer-trust",
                            str(draft_path),
                            "--output",
                            str(sealed_path),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    main(["validate-reviewer-trust", str(sealed_path)]),
                    0,
                )

    def test_project_template_command_matches_versioned_example(self) -> None:
        expected = reviewer_trust_registry_template()
        example = json.loads(
            (ROOT / "examples" / "reviewer-trust.draft.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(example, expected)
        with tempfile.TemporaryDirectory() as temporary:
            output_path = Path(temporary) / "project-reviewers.draft.json"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "reviewer-trust-template",
                            "--output",
                            str(output_path),
                        ]
                    ),
                    0,
                )
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), expected)
            self.assertIn("seal-reviewer-trust", output.getvalue())

    def test_create_run_can_atomically_bind_selected_project_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = self._sealed_registry()
            status = create_run(
                EXAMPLE_PACK,
                root / "runs",
                "run-create-with-trust",
                reviewer_trust_registry=registry,
                reviewer_trust_actor="Project Owner",
            )
            run_dir = root / "runs" / status["run_id"]
            self.assertTrue(status["reviewer_trust_policy_bound"])
            self.assertEqual(status["reviewer_trust_registry_id"], "primary-reviewers")
            self.assertTrue((run_dir / "reviewer-trust.snapshot.json").is_file())
            events = (run_dir / "events.jsonl").read_text(encoding="utf-8")
            self.assertIn("reviewer_trust_policy_bound", events)
            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            self.assertEqual(approved["status"], "approved_pending_resume")
            with self.assertRaisesRegex(RunStateError, "reviewer 0/1"):
                resume_run(run_dir)

    def test_quickstart_requires_explicit_pair_and_auto_binds_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_path = root / "reviewer-trust.json"
            registry_path.write_text(
                json.dumps(self._sealed_registry(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            missing_actor_error = io.StringIO()
            with contextlib.redirect_stderr(missing_actor_error):
                self.assertEqual(
                    main(
                        [
                            "quickstart",
                            "验证项目级 Reviewer Registry",
                            "--workspace",
                            str(root / "missing-actor"),
                            "--reviewer-trust",
                            str(registry_path),
                        ]
                    ),
                    2,
                )
            self.assertIn("必须同时提供", missing_actor_error.getvalue())
            self.assertFalse((root / "missing-actor").exists())

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "quickstart",
                            "验证项目级 Reviewer Registry",
                            "--workspace",
                            str(root / "selected"),
                            "--run-id",
                            "run-cli-auto-bind",
                            "--reviewer-trust",
                            str(registry_path),
                            "--trust-by",
                            "Project Owner",
                        ]
                    ),
                    0,
                )
            result = json.loads(output.getvalue())
            self.assertTrue(result["reviewer_trust_policy_bound"])
            self.assertEqual(result["reviewer_trust_registry_id"], "primary-reviewers")

    def test_advanced_wizard_explicit_registry_start(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_path = root / "reviewer-trust.json"
            registry_path.write_text(
                json.dumps(self._sealed_registry(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            answers = iter(
                [
                    "16",
                    str(EXAMPLE_PACK),
                    str(registry_path),
                    "Project Owner",
                    "0",
                ]
            )
            output: list[str] = []
            self.assertEqual(
                run_wizard(
                    workspace=root,
                    input_fn=lambda _prompt: next(answers),
                    output_fn=output.append,
                ),
                0,
            )
            run_dir = next((root / "runs").glob("run-*"))
            self.assertTrue(verify_run(run_dir)["reviewer_trust_policy_bound"])
            self.assertTrue(any("创建时绑定" in line for line in output))


@unittest.skipUnless(SSH_KEYGEN, "OpenSSH ssh-keygen is not installed")
class ReviewerTrustRuntimeTests(unittest.TestCase):
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

    def _key_entry(
        self,
        public_key_path: Path,
        *,
        identity: str = "reviewer@example",
        role: str = "reviewer",
        valid_from: str = "2020-01-01T00:00:00Z",
        valid_until: str | None = None,
        revoked_at: str | None = None,
    ) -> dict:
        entry = {
            "identity": identity,
            "role": role,
            "public_key": load_ed25519_public_key(public_key_path),
            "valid_from": valid_from,
        }
        if valid_until is not None:
            entry["valid_until"] = valid_until
        if revoked_at is not None:
            entry["revoked_at"] = revoked_at
        return entry

    def test_required_signature_blocks_resume_and_effective_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft([self._key_entry(public_key)])
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-gate")
            run_dir = root / "runs" / status["run_id"]
            bound = bind_reviewer_trust_registry(
                run_dir,
                registry,
                actor="Policy Administrator",
            )
            self.assertTrue(bound["reviewer_trust_policy_bound"])

            approved = approve_run(run_dir, approver="Human Reviewer", note="accepted")
            pending = reviewer_trust_status(run_dir)
            manifest = build_effective_output_manifest(run_dir)
            self.assertFalse(pending["satisfied"])
            self.assertEqual(
                pending["reviews"][-1]["outstanding_requirements"][0][
                    "missing_signatures"
                ],
                1,
            )
            self.assertIsNone(manifest["outputs"][0]["approved_review_hash"])
            with self.assertRaisesRegex(RunStateError, "reviewer 0/1"):
                resume_run(run_dir)

            signed = sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
                review_hash=approved["latest_review_hash"],
            )
            self.assertTrue(signed["reviewer_trust_satisfied"])
            trusted_manifest = build_effective_output_manifest(run_dir)
            self.assertEqual(
                trusted_manifest["outputs"][0]["approved_review_hash"],
                approved["latest_review_hash"],
            )
            self.assertTrue(
                trusted_manifest["outputs"][0]["approved_review_signatures"][0][
                    "policy_trusted"
                ]
            )
            self.assertEqual(
                trusted_manifest["outputs"][0]["approved_review_signatures"][0][
                    "reviewer_role"
                ],
                "reviewer",
            )
            self.assertIn("primary-reviewers", render_run_artifacts(run_dir))
            self.assertIn("Reviewer 信任状态", render_research_handoff(run_dir))
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)
            exported = export_run_to_obsidian(run_dir, vault)
            export_dir = Path(exported["export_dir"])
            self.assertTrue(exported["reviewer_trust_policy_bound"])
            self.assertTrue((export_dir / "Reviewer Trust Registry.md").is_file())
            self.assertTrue((export_dir / "Reviewer Trust Registry.json").is_file())
            resumed = resume_run(run_dir)
            self.assertEqual(resumed["status"], "paused")
            self.assertEqual(resumed["next_task_index"], 1)

    def test_cli_binds_registry_and_reports_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _private_key, public_key = self._generate_key(root, "cli-reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft([self._key_entry(public_key)])
            )
            registry_path = root / "reviewer-trust.json"
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-cli-bind")
            run_dir = root / "runs" / status["run_id"]
            bind_output = io.StringIO()
            with contextlib.redirect_stdout(bind_output):
                self.assertEqual(
                    main(
                        [
                            "bind-reviewer-trust",
                            str(run_dir),
                            str(registry_path),
                            "--by",
                            "Policy Admin",
                        ]
                    ),
                    0,
                )
            self.assertTrue(
                json.loads(bind_output.getvalue())["reviewer_trust_policy_bound"]
            )
            status_output = io.StringIO()
            with contextlib.redirect_stdout(status_output):
                self.assertEqual(
                    main(["reviewer-trust-status", str(run_dir)]),
                    0,
                )
            trust = json.loads(status_output.getvalue())
            self.assertTrue(trust["policy_bound"])
            self.assertEqual(trust["registry_id"], "primary-reviewers")

    def test_wrong_role_and_expired_keys_do_not_satisfy_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            observer_private, observer_public = self._generate_key(root, "observer")
            reviewer_private, reviewer_public = self._generate_key(root, "reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft(
                    [
                        self._key_entry(
                            observer_public,
                            identity="observer@example",
                            role="observer",
                        ),
                        self._key_entry(
                            reviewer_public,
                            valid_until="2021-01-01T00:00:00Z",
                        ),
                    ]
                )
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-wrong-role")
            run_dir = root / "runs" / status["run_id"]
            bind_reviewer_trust_registry(run_dir, registry, actor="Admin")
            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            sign_review_decision(
                run_dir,
                signer_identity="observer@example",
                private_key_path=observer_private,
                public_key_path=observer_public,
                review_hash=approved["latest_review_hash"],
            )
            trust = reviewer_trust_status(run_dir)
            self.assertFalse(trust["satisfied"])
            self.assertEqual(
                trust["reviews"][-1]["trusted_signatures"][0]["role"],
                "observer",
            )

            sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=reviewer_private,
                public_key_path=reviewer_public,
                review_hash=approved["latest_review_hash"],
            )
            trust = reviewer_trust_status(run_dir)
            self.assertFalse(trust["satisfied"])
            reasons = {
                item["reason"] for item in trust["reviews"][-1]["untrusted_signatures"]
            }
            self.assertIn("expired", reasons)

    def test_revoked_key_is_audited_but_does_not_satisfy_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private_key, public_key = self._generate_key(root, "revoked-reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft(
                    [
                        self._key_entry(
                            public_key,
                            revoked_at="2021-01-01T00:00:00Z",
                        )
                    ]
                )
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-revoked")
            run_dir = root / "runs" / status["run_id"]
            bind_reviewer_trust_registry(run_dir, registry, actor="Admin")
            approved = approve_run(run_dir, approver="Reviewer", note="accepted")
            sign_review_decision(
                run_dir,
                signer_identity="reviewer@example",
                private_key_path=private_key,
                public_key_path=public_key,
                review_hash=approved["latest_review_hash"],
            )

            trust = reviewer_trust_status(run_dir)
            self.assertFalse(trust["satisfied"])
            self.assertEqual(
                trust["reviews"][-1]["untrusted_signatures"][0]["reason"],
                "revoked",
            )
            with self.assertRaises(RunStateError):
                resume_run(run_dir)

    def test_policy_cannot_be_bound_after_a_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _private_key, public_key = self._generate_key(root, "reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft([self._key_entry(public_key)])
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-too-late")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Reviewer", note="accepted")

            with self.assertRaisesRegex(RunStateError, "before the first decision"):
                bind_reviewer_trust_registry(run_dir, registry, actor="Admin")
            self.assertFalse(verify_run(run_dir)["reviewer_trust_policy_bound"])

    def test_policy_cannot_be_bound_at_a_later_legacy_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _private_key, public_key = self._generate_key(root, "legacy-reviewer")
            registry = seal_reviewer_trust_registry(
                trust_draft([self._key_entry(public_key)])
            )
            status = create_run(EXAMPLE_PACK, root / "runs", "run-trust-late-gate")
            run_dir = root / "runs" / status["run_id"]
            approve_run(run_dir, approver="Legacy Reviewer", note="task one")
            resume_run(run_dir)
            approval_path = run_dir / "approvals.jsonl"
            approval = json.loads(approval_path.read_text(encoding="utf-8"))
            approval.pop("review_hash")
            unsigned = {key: value for key, value in approval.items() if key != "hash"}
            approval["hash"] = sha256_text(canonical_json_text(unsigned))
            write_text_atomic(approval_path, canonical_json_text(approval) + "\n")
            (run_dir / "reviews.jsonl").unlink()
            state = read_json(run_dir / "state.json")
            state["approval_tail_hash"] = approval["hash"]
            state["review_tail_hash"] = ZERO_HASH
            write_json_atomic(run_dir / "state.json", state)
            write_hash_manifest(run_dir)
            self.assertEqual(verify_run(run_dir)["review_count"], 0)

            with self.assertRaisesRegex(RunStateError, "first human gate"):
                bind_reviewer_trust_registry(run_dir, registry, actor="Admin")
            self.assertFalse(verify_run(run_dir)["reviewer_trust_policy_bound"])


if __name__ == "__main__":
    unittest.main()
