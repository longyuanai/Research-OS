from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import research_os_mvp.integrity as integrity_module
import research_os_mvp.runtime as runtime_module
from research_os_mvp.claims import current_task_source
from research_os_mvp.cli import main
from research_os_mvp.exporters import export_run_to_obsidian
from research_os_mvp.handoff import render_research_handoff
from research_os_mvp.integrity import canonical_json_text, read_json, sha256_text
from research_os_mvp.runtime import (
    approve_run,
    bind_claims_gate,
    build_effective_output_manifest,
    create_run,
    record_confirmed_claims,
    resolve_effective_task_outputs,
    review_run,
    revise_task_output,
    verify_effective_output_manifest_signature,
)
from research_os_mvp.wizard import inspect_run_artifacts
from tests.helpers import EXAMPLE_PACK

FIXED_NOW = "2026-08-18T00:00:00Z"
TASK_ONE = "TASK-MVP-01-capture-requirement"
LEGACY_MANIFEST_SHA256 = (
    "019ea0b4dcdee8252827d878bd7225422cece2a18e118db494e3a96dcb515d8b"
)
LEGACY_OUTPUTS_SHA256 = (
    "b3e0e578e389c0b562d956e69a048c2f5ddbd798c3f35991eead851fb1f99e72"
)
LEGACY_ATTESTATION = {
    "attestation_sha256": (
        "5b1af0d8d1765c13b5f740e2aef5da83ca6a9c298385216ac049b71185d081ae"
    ),
    "manifest_sha256": LEGACY_MANIFEST_SHA256,
    "namespace": "research-os-effective-manifest",
    "payload_sha256": (
        "7428b32e523284b335301f6c7672ff74bb6a58ac988ac61045da0b820c3cd18b"
    ),
    "public_key": (
        "ssh-ed25519 "
        "AAAAC3NzaC1lZDI1NTE5AAAAILylxI6tKR3juO+7pJhi09FmudQKDAZoDv5ms2TBj29Q"
    ),
    "public_key_fingerprint": "SHA256:i6lEWM0s4amfnILmwHhf+kaRnJWoIVvbm7ApGyQjQAE",
    "run_id": "run-s5-legacy-hash",
    "schema_version": "research-os-mvp-effective-manifest-signature/0.1",
    "signature": (
        "-----BEGIN SSH SIGNATURE-----\n"
        "U1NIU0lHAAAAAQAAADMAAAALc3NoLWVkMjU1MTkAAAAgvKXEjq0pHeO477ukmGLT0Wa51A\n"
        "oMBmgO/mazZMGPb1AAAAAecmVzZWFyY2gtb3MtZWZmZWN0aXZlLW1hbmlmZXN0AAAAAAAA\n"
        "AAZzaGE1MTIAAABTAAAAC3NzaC1lZDI1NTE5AAAAQJu3V+RXTxV74LlSgz4JEi+C+kqE++\n"
        "JY2RycHlGajbPJWYZ89rXk1l3Ot53bO/jUNxYZQIkTc53cZOSdqyDMFQQ=\n"
        "-----END SSH SIGNATURE-----\n"
    ),
    "signer_identity": "legacy@example",
}


class EffectiveOutputClaimsGateTests(unittest.TestCase):
    @contextlib.contextmanager
    def _fixed_clock(self) -> Iterator[None]:
        with (
            patch.object(runtime_module, "utc_now", return_value=FIXED_NOW),
            patch.object(integrity_module, "utc_now", return_value=FIXED_NOW),
        ):
            yield

    def _prepare_revision(
        self,
        root: Path,
        run_id: str,
        *,
        gate_enabled: bool,
    ) -> tuple[Path, dict, dict]:
        status = create_run(
            EXAMPLE_PACK,
            root / "runs",
            run_id,
            claims_gate_enabled=gate_enabled,
            claims_gate_actor=("Claims Policy Admin" if gate_enabled else None),
        )
        run_dir = root / "runs" / status["run_id"]
        original = resolve_effective_task_outputs(run_dir)[0]
        reviewed = review_run(
            run_dir,
            reviewer="Reviewer",
            decision="Changes Requested",
            note="revise effective output",
        )
        revised = revise_task_output(
            run_dir,
            content="S5 approved revision candidate",
            revised_by="Editor",
            note="S5 revision",
            review_decision_hash=reviewed["latest_review_hash"],
        )
        return run_dir, original, revised

    def _record_fact(self, run_dir: Path, *, support: str) -> None:
        source_path, _, source_text = current_task_source(run_dir, TASK_ONE)
        source = read_json(source_path)
        record_confirmed_claims(
            run_dir,
            task_id=TASK_ONE,
            confirmed_by="Human Reviewer",
            confirmed_at=FIXED_NOW,
            claims=[
                {
                    "text": source_text,
                    "kind": "verifiable_fact",
                    "evidence_ids": (
                        [] if support == "unsupported" else [source["evidence_id"]]
                    ),
                    "support": support,
                }
            ],
        )

    def _approved_gated_revision(
        self,
        root: Path,
        run_id: str,
        *,
        support: str,
    ) -> tuple[Path, dict, dict]:
        run_dir, original, revised = self._prepare_revision(
            root,
            run_id,
            gate_enabled=True,
        )
        self._record_fact(run_dir, support=support)
        approve_run(run_dir, approver="Reviewer", note="revision accepted")
        return run_dir, original, revised

    def _legacy_manifest(self, root: Path) -> dict:
        with self._fixed_clock():
            status = create_run(
                EXAMPLE_PACK,
                root / "runs",
                "run-s5-legacy-hash",
            )
            return build_effective_output_manifest(
                root / "runs" / status["run_id"]
            )

    def test_gate_prevents_promotion_when_task_claims_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, original, revised = self._approved_gated_revision(
                Path(temporary),
                "run-s5-gate-blocks-promotion",
                support="unsupported",
            )

            effective = resolve_effective_task_outputs(run_dir)[0]
            self.assertEqual(effective["source"], "original")
            self.assertEqual(effective["effective_id"], original["effective_id"])
            self.assertNotEqual(effective["effective_id"], revised["id"])

    def test_gate_allows_promotion_when_task_claims_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, _, revised = self._approved_gated_revision(
                Path(temporary),
                "run-s5-gate-allows-promotion",
                support="direct",
            )

            effective = resolve_effective_task_outputs(run_dir)[0]
            self.assertEqual(effective["source"], "approved_revision")
            self.assertEqual(effective["effective_id"], revised["id"])
            self.assertEqual(effective["content"], "S5 approved revision candidate")

    def test_gate_effect_is_consistent_across_cli_handoff_export_wizard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_dir, original, _ = self._approved_gated_revision(
                root,
                "run-s5-four-entry-consistency",
                support="unsupported",
            )

            cli_output = io.StringIO()
            with contextlib.redirect_stdout(cli_output):
                cli_exit = main(["effective-outputs", str(run_dir)])
            cli_manifest = json.loads(cli_output.getvalue())

            handoff = render_research_handoff(run_dir)
            wizard = inspect_run_artifacts(run_dir)
            vault = root / "vault"
            (vault / ".obsidian").mkdir(parents=True)
            exported = export_run_to_obsidian(run_dir, vault)
            exported_effective = (
                Path(exported["export_dir"]) / "Effective Task Outputs.md"
            ).read_text(encoding="utf-8")

            self.assertEqual(cli_exit, 0)
            self.assertEqual(cli_manifest["outputs"][0]["source"], "original")
            self.assertIn(original["content"], handoff)
            self.assertNotIn("S5 approved revision candidate", handoff)
            self.assertEqual(wizard["effective_outputs"][0]["source"], "original")
            self.assertIn(original["content"], exported_effective)
            self.assertNotIn("S5 approved revision candidate", exported_effective)
            self.assertEqual(exported["approved_revision_outputs"], 0)

    def test_legacy_run_manifest_sha256_unchanged_after_s5(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._legacy_manifest(Path(temporary))

            self.assertEqual(manifest["manifest_sha256"], LEGACY_MANIFEST_SHA256)
            self.assertEqual(
                sha256_text(canonical_json_text(manifest["outputs"])),
                LEGACY_OUTPUTS_SHA256,
            )

    @unittest.skipUnless(shutil.which("ssh-keygen"), "OpenSSH ssh-keygen is not installed")
    def test_existing_signed_manifest_still_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._legacy_manifest(Path(temporary))

            verified = verify_effective_output_manifest_signature(
                manifest,
                LEGACY_ATTESTATION,
            )
            self.assertEqual(verified["integrity"], "verified")
            self.assertEqual(verified["manifest_sha256"], LEGACY_MANIFEST_SHA256)

    def test_run_without_gate_produces_identical_effective_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self._fixed_clock():
                baseline_dir, _, _ = self._prepare_revision(
                    root / "baseline",
                    "run-s5-no-gate-identical",
                    gate_enabled=False,
                )
                approve_run(
                    baseline_dir,
                    approver="Reviewer",
                    note="revision accepted",
                )
                claimed_dir, _, _ = self._prepare_revision(
                    root / "with-claims",
                    "run-s5-no-gate-identical",
                    gate_enabled=False,
                )
                self._record_fact(claimed_dir, support="unsupported")
                approve_run(
                    claimed_dir,
                    approver="Reviewer",
                    note="revision accepted",
                )

                self.assertEqual(
                    resolve_effective_task_outputs(claimed_dir),
                    resolve_effective_task_outputs(baseline_dir),
                )

    def test_gate_semantic_matches_chosen_option_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, original, _ = self._approved_gated_revision(
                Path(temporary),
                "run-s5-option-a",
                support="unsupported",
            )

            effective = resolve_effective_task_outputs(run_dir)[0]
            self.assertEqual(effective["effective_id"], original["effective_id"])
            self.assertEqual(effective["source"], "original")
            self.assertIsNone(effective["approved_review_id"])
            self.assertIsNone(effective["approved_review_hash"])
            self.assertIsNone(effective["approved_review_trust_satisfied"])

    def test_gate_does_not_remove_task_from_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, _, _ = self._approved_gated_revision(
                Path(temporary),
                "run-s5-task-retained",
                support="unsupported",
            )

            outputs = resolve_effective_task_outputs(run_dir)
            self.assertEqual(len(outputs), 1)
            self.assertEqual(outputs[0]["task_id"], TASK_ONE)

    def test_late_bound_gate_does_not_retroactively_change_effective_output(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir, _, revised = self._prepare_revision(
                Path(temporary),
                "run-s5-late-bound",
                gate_enabled=False,
            )
            self._record_fact(run_dir, support="unsupported")
            approve_run(run_dir, approver="Reviewer", note="revision accepted")

            bound = bind_claims_gate(run_dir, actor="Claims Policy Admin")
            effective = resolve_effective_task_outputs(run_dir)[0]

            self.assertEqual(bound["claims_gate_from_task_index"], 1)
            self.assertEqual(effective["source"], "approved_revision")
            self.assertEqual(effective["effective_id"], revised["id"])


if __name__ == "__main__":
    unittest.main()
