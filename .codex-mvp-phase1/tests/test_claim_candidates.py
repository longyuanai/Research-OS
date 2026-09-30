from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_os_mvp.ai import AIResponse, save_ollama_settings
from research_os_mvp.claim_candidates import (
    classify_claim_candidates,
    extract_claim_candidates,
    find_ai_draft_policy_violations,
)
from research_os_mvp.errors import RunStateError
from research_os_mvp.integrity import read_json
from research_os_mvp.natural_language import create_pack_from_goal
from research_os_mvp.runtime import (
    approve_run,
    claims_coverage_status,
    claims_status,
    create_run,
    read_claim_source_snapshot,
    record_confirmed_claims,
    record_supplemental_evidence,
    resume_run,
    verify_run,
)
from research_os_mvp.wizard import _confirm_ai_draft_claims, run_easy_wizard
from tests.helpers import materialize_legacy_runs

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "fabricated-citation-draft.md"
TASK_ID = "TASK-LOCAL-02-record-evaluation-frame"

SMALL_DRAFT = """### 逐条证据清单
- Python：开发速度快。来源：模型编造的文档，2023-01-01。

### 推荐方案及适用条件
建议先做最小验证。
"""

EXISTING_EVIDENCE_HASHES = {
    "run-20260820t062550z-969cbc95": {
        "evidence/EVID-01-task-local-01-capture-goal.json": (
            "047a70c456410ae1187b4c3dada3cf1a91288cc4a14585ceba089b300b292712"
        ),
        "evidence/EVID-02-task-local-02-record-evaluation-frame.json": (
            "092d397326fcfcabf93751a09d5732fdd4cf4940ff4897ca33a7957d44aaf1aa"
        ),
    },
    "run-20260820t071348z-65b76017": {
        "evidence/EVID-01-task-local-01-capture-goal.json": (
            "ac8ce03f2d912b10bbb93fa1eb4991e4798ae7963eb6c57efa6612f67d4c5712"
        ),
        "evidence/EVID-02-task-local-02-record-evaluation-frame.json": (
            "de215c408d6e642f72d0fa72c1873c178dd35f9aca7423a0f7cd08fdf372f7aa"
        ),
    },
}


def _fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def _answers(*values: str):
    answers = iter(values)
    return lambda _prompt: next(answers)


class ClaimCandidateExtractorTests(unittest.TestCase):
    def test_extractor_splits_structured_draft_into_candidates(self) -> None:
        candidates = extract_claim_candidates(_fixture_text())
        self.assertEqual(len(candidates), 18)
        self.assertEqual(
            [item["section"] for item in candidates].count("逐条证据清单"),
            15,
        )
        self.assertEqual(
            [item["section"] for item in candidates].count("推荐方案及适用条件"),
            3,
        )

    def test_extractor_never_emits_evidence_ids(self) -> None:
        candidates = extract_claim_candidates(_fixture_text())
        self.assertTrue(all(item["evidence_ids"] == [] for item in candidates))

    def test_extractor_defaults_every_candidate_to_unsupported(self) -> None:
        candidates = extract_claim_candidates(_fixture_text())
        self.assertTrue(all(item["support"] == "unsupported" for item in candidates))

    def test_inline_source_strings_are_not_treated_as_evidence(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        fabricated = next(item for item in candidates if "来源：" in item["text"])
        self.assertIn("模型编造的文档", fabricated["text"])
        self.assertEqual(fabricated["evidence_ids"], [])
        self.assertEqual(fabricated["support"], "unsupported")

    def test_fabricated_citation_fixture_yields_unsupported_facts(self) -> None:
        citations = [
            item
            for item in extract_claim_candidates(_fixture_text())
            if item["section"] == "逐条证据清单" and "来源：" in item["text"]
        ]
        self.assertEqual(len(citations), 15)
        self.assertTrue(all("2023-01-01" in item["text"] for item in citations))
        self.assertTrue(all(item["support"] == "unsupported" for item in citations))
        self.assertTrue(all(item["evidence_ids"] == [] for item in citations))

    def test_extractor_is_deterministic_for_the_same_input(self) -> None:
        draft = _fixture_text()
        self.assertEqual(extract_claim_candidates(draft), extract_claim_candidates(draft))


    def test_fenced_code_blocks_do_not_emit_claim_candidates(self) -> None:
        backtick_fence = chr(96) * 3
        draft = "\n".join(
            [
                "### 逐条证据清单",
                f"{backtick_fence}text",
                "- 示例命令不是 Claim。来源：虚构文档。",
                f"{backtick_fence}not-a-closing-fence",
                "- marker 后有文字时仍在代码围栏内。",
                backtick_fence,
                "~~~text",
                "- 波浪围栏里的示例也不是 Claim。",
                "~~~",
                "- 真实候选。",
            ]
        )
        self.assertEqual(
            [item["text"] for item in extract_claim_candidates(draft)],
            ["真实候选。"],
        )

    def test_policy_detector_ignores_placeholders_and_fenced_examples(self) -> None:
        draft = (
            "来源：真实文档，2026-08-24。\n"
            "来源：未知/待查证。\n"
            "~~~text\n"
            "来源：围栏中的示例文档。\n"
            "~~~"
        )
        self.assertEqual(
            find_ai_draft_policy_violations(draft),
            ["来源：真实文档，2026-08-24。"],
        )


class ClaimCandidateConfirmationTests(unittest.TestCase):
    def _run_with_draft(self, root: Path, draft: str = SMALL_DRAFT) -> Path:
        generated = create_pack_from_goal(
            "技术选型：比较 Python、TypeScript 和 Rust",
            workspace=root,
        )
        status = create_run(generated.path, root / "runs")
        run_dir = root / "runs" / status["run_id"]
        approve_run(run_dir, approver="Human Reviewer", note="Task 1 reviewed")
        resume_run(run_dir)
        record_supplemental_evidence(
            run_dir,
            content=draft,
            source="ollama://qwen2.5:7b",
            method="real draft fixture",
            limitations="requires human verification",
            collected_by="Ollama (qwen2.5:7b)",
            evidence_role="ai_draft",
        )
        return run_dir

    def test_no_claims_recorded_when_human_skips_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(Path(temporary))
            with patch("research_os_mvp.wizard.record_confirmed_claims") as recorder:
                result = _confirm_ai_draft_claims(
                    run_dir,
                    TASK_ID,
                    _answers(""),
                    lambda _line: None,
                )
            self.assertIsNone(result)
            recorder.assert_not_called()
            self.assertFalse(claims_status(run_dir)["claims_confirmed"])
            self.assertFalse((run_dir / "claims").exists())

    def test_claims_confirmed_stays_false_until_all_classified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(Path(temporary))
            result = _confirm_ai_draft_claims(
                run_dir,
                TASK_ID,
                _answers("1", ""),
                lambda _line: None,
            )
            self.assertIsNone(result)
            self.assertFalse(verify_run(run_dir)["claims_confirmed"])
            self.assertEqual(verify_run(run_dir)["claim_count"], 0)

    def test_human_can_set_each_candidate_kind_individually(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        output: list[str] = []
        answers = iter(["1", "2", "1", "4", "CONFIRM"])

        def input_with_transcript(prompt: str) -> str:
            output.append(prompt)
            return next(answers)

        claims = classify_claim_candidates(
            candidates,
            input_fn=input_with_transcript,
            output_fn=output.append,
        )
        assert claims is not None
        self.assertEqual([item["kind"] for item in claims], ["assumption", "interpretation"])
        self.assertTrue(all(item["support"] == "unsupported" for item in claims))
        self.assertTrue(all(item["evidence_ids"] == [] for item in claims))
        self.assertTrue(any("输入候选编号可修改" in line for line in output))

    def test_recorded_claims_go_through_record_confirmed_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(Path(temporary))
            with patch(
                "research_os_mvp.wizard.record_confirmed_claims",
                wraps=record_confirmed_claims,
            ) as recorder:
                _confirm_ai_draft_claims(
                    run_dir,
                    TASK_ID,
                    _answers("1", "3", "CONFIRM", "C4 Human"),
                    lambda _line: None,
                )
            recorder.assert_called_once()
            claims = recorder.call_args.kwargs["claims"]
            self.assertTrue(all(item["evidence_ids"] == [] for item in claims))
            self.assertTrue(all(item["support"] == "unsupported" for item in claims))

    def test_source_change_during_confirmation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(Path(temporary))
            answers = iter(["1", "3", "CONFIRM"])

            def input_with_source_change(prompt: str) -> str:
                if prompt.startswith("确认人"):
                    record_supplemental_evidence(
                        run_dir,
                        content=SMALL_DRAFT.replace("Python", "Rust", 1),
                        source="ollama://qwen2.5:7b",
                        method="concurrent replacement draft",
                        limitations="requires human verification",
                        collected_by="Ollama (qwen2.5:7b)",
                        evidence_role="ai_draft",
                    )
                    return "Race Human"
                return next(answers)

            with self.assertRaisesRegex(RunStateError, "source changed"):
                _confirm_ai_draft_claims(
                    run_dir,
                    TASK_ID,
                    input_with_source_change,
                    lambda _line: None,
                )

            self.assertFalse((run_dir / "claims").exists())

    def test_confirmed_claims_pass_c1_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(Path(temporary))
            _confirm_ai_draft_claims(
                run_dir,
                TASK_ID,
                _answers("1", "3", "CONFIRM", ""),
                lambda _line: None,
            )
            status = verify_run(run_dir)
            self.assertTrue(status["claims_confirmed"])
            self.assertEqual(status["claim_count"], 2)
            record = read_json(run_dir / "claims" / f"CLAIMS-{TASK_ID}.json")
            self.assertEqual(record["task_id"], TASK_ID)
            self.assertTrue(all(item["evidence_ids"] == [] for item in record["claims"]))

    def test_c2_hard_gate_still_blocks_unsupported_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run_with_draft(
                Path(temporary),
                "### 逐条证据清单\n- 编造的事实。来源：虚构文档，2023-01-01。\n",
            )
            _confirm_ai_draft_claims(
                run_dir,
                TASK_ID,
                _answers("1", "CONFIRM", "C4 Human"),
                lambda _line: None,
            )
            coverage = claims_coverage_status(run_dir)
            self.assertFalse(coverage["hard_gate_pass"])
            self.assertEqual(coverage["fact_coverage"], 0.0)
            self.assertEqual(coverage["unsupported_fact_count"], 1)

    def test_c_key_is_shown_only_when_task_two_has_ai_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "技术选型：比较 Python、TypeScript 和 Rust",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            transcript: list[str] = []

            def fake_generate(_settings: object, _prompt: str):
                raise AssertionError("AI must not be called without settings")

            def input_with_transcript(prompt: str) -> str:
                transcript.append(prompt)
                return next(answers)

            run_easy_wizard(
                workspace=temporary,
                input_fn=input_with_transcript,
                output_fn=output.append,
                ai_generate_fn=fake_generate,
            )
            decision_prompts = [line for line in transcript if "Reviewer 决定" in line]
            self.assertTrue(decision_prompts)
            self.assertTrue(all("C 逐条确认 Claims" not in line for line in decision_prompts))

        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "技术选型：比较 Python、TypeScript 和 Rust",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "",
                    "0",
                ]
            )
            transcript = []

            def input_with_transcript(prompt: str) -> str:
                transcript.append(prompt)
                return next(answers)

            def fake_generate(_settings: object, _prompt: str) -> AIResponse:
                return AIResponse(
                    content=SMALL_DRAFT,
                    provider="ollama",
                    model="qwen2.5:7b",
                    endpoint="http://127.0.0.1:11434",
                    elapsed_seconds=0.1,
                )

            run_easy_wizard(
                workspace=temporary,
                input_fn=input_with_transcript,
                output_fn=transcript.append,
                ai_generate_fn=fake_generate,
            )
            decision_prompts = [line for line in transcript if "Reviewer 决定" in line]
            self.assertTrue(any("C 逐条确认 Claims" in line for line in decision_prompts))


    def test_approval_waits_for_claim_confirmation_when_sources_are_asserted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "技术选型：比较 Python、TypeScript 和 Rust",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "y",
                    "",
                    "0",
                ]
            )
            output: list[str] = []

            def fake_generate(_settings: object, _prompt: str) -> AIResponse:
                return AIResponse(
                    content=SMALL_DRAFT,
                    provider="ollama",
                    model="qwen2.5:7b",
                    endpoint="http://127.0.0.1:11434",
                    elapsed_seconds=0.1,
                )

            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=fake_generate,
            )

            run_dir = next((Path(temporary) / "runs").iterdir())
            status = verify_run(run_dir)
            self.assertEqual(status["pending_task_id"], TASK_ID)
            self.assertEqual(status["approval_count"], 1)
            self.assertTrue(any("本次未批准" in line for line in output))


class ClaimCandidateRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._legacy_runs_temporary = tempfile.TemporaryDirectory()
        cls.legacy_runs_root = materialize_legacy_runs(
            Path(cls._legacy_runs_temporary.name)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._legacy_runs_temporary.cleanup()

    def test_fixture_bundle_rejects_parent_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "unsafe.bundle.json"
            bundle.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "research-os-mvp-legacy-run-fixtures/0.1"
                        ),
                        "files": {"../escape.txt": ""},
                    }
                ),
                encoding="utf-8",
            )
            with (
                patch("tests.helpers.LEGACY_RUNS_BUNDLE", bundle),
                self.assertRaisesRegex(AssertionError, "escapes"),
            ):
                materialize_legacy_runs(root / "restore")
            self.assertFalse((root / "escape.txt").exists())

    def test_existing_runs_verify_unchanged_after_c4(self) -> None:
        runs_root = self.legacy_runs_root
        expected_counts = {
            "run-20260820t062550z-969cbc95": (23, 2, 11),
            "run-20260820t071348z-65b76017": (23, 2, 11),
        }
        for run_id, (events, evidence, hashed) in expected_counts.items():
            with self.subTest(run_id=run_id):
                status = verify_run(runs_root / run_id)
                self.assertEqual(status["integrity"], "verified")
                self.assertEqual(status["status"], "completed")
                self.assertEqual(status["event_count"], events)
                self.assertEqual(status["evidence_count"], evidence)
                self.assertEqual(status["hashed_file_count"], hashed)
                self.assertEqual(status["claim_count"], 0)

    def test_existing_evidence_hashes_unchanged(self) -> None:
        runs_root = self.legacy_runs_root
        for run_id, expected in EXISTING_EVIDENCE_HASHES.items():
            with self.subTest(run_id=run_id):
                manifest = json.loads(
                    (runs_root / run_id / "HASHES.json").read_text(encoding="utf-8")
                )
                actual = {
                    item["path"]: item["sha256"]
                    for item in manifest["files"]
                    if item["path"].startswith("evidence/")
                }
                self.assertEqual(actual, expected)


class ClaimCandidateExtractorEdgeCaseTests(unittest.TestCase):
    def test_non_string_draft_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            extract_claim_candidates(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            find_ai_draft_policy_violations(b"bytes")  # type: ignore[arg-type]

    def test_only_claim_bearing_sections_are_extracted(self) -> None:
        draft = (
            "### 缺失条件与澄清问题\n"
            "1. 版本未明确。\n"
            "### 逐条证据清单\n"
            "1. **分组标题**\n"
            "   - 甲事实。\n"
            "   + 乙事实。\n"
            "2) 丙事实。\n"
            "| 表格 | 行 |\n"
            "游离段落在列表模式中被忽略。\n"
            "### 风险与反证\n"
            "- 风险条目。\n"
            "## 推荐方案及适用条件 ##\n"
            "先做验证！再扩大范围？最后复盘\n"
            "- 列表形式的建议。\n"
        )
        texts = [item["text"] for item in extract_claim_candidates(draft)]
        self.assertEqual(
            texts,
            [
                "甲事实。",
                "乙事实。",
                "丙事实。",
                "先做验证！",
                "再扩大范围？",
                "最后复盘",
                "列表形式的建议。",
            ],
        )

    def test_candidates_record_section_and_quote_locator(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        self.assertEqual(
            [item["section"] for item in candidates],
            ["逐条证据清单", "推荐方案及适用条件"],
        )
        for item in candidates:
            self.assertEqual(item["locator"], {"kind": "quote", "value": item["text"]})
            self.assertIsNone(item["kind"])

    def test_duplicate_candidates_are_collapsed(self) -> None:
        draft = "### 逐条证据清单\n- 同一事实。\n- 同一事实。\n-   同一事实。  \n"
        self.assertEqual(len(extract_claim_candidates(draft)), 1)

    def test_candidate_limit_fails_closed(self) -> None:
        from research_os_mvp.claim_candidates import MAX_CANDIDATES

        lines = "".join(f"- 事实 {index}。\n" for index in range(MAX_CANDIDATES + 1))
        with self.assertRaisesRegex(RunStateError, "超过"):
            extract_claim_candidates("### 逐条证据清单\n" + lines)

    def test_unterminated_or_mismatched_fences_hide_following_lines(self) -> None:
        draft = (
            "### 逐条证据清单\n"
            "````markdown\n"
            "- 围栏内条目。\n"
            "```\n"
            "- 仍在围栏内（短标记不闭合长围栏）。\n"
            "````\n"
            "- 围栏外条目。\n"
            "~~~\n"
            "- 未闭合围栏中的条目。\n"
        )
        texts = [item["text"] for item in extract_claim_candidates(draft)]
        self.assertEqual(texts, ["围栏外条目。"])


class PolicyViolationDetectorEdgeCaseTests(unittest.TestCase):
    def test_source_assertion_variants_are_detected(self) -> None:
        draft = (
            "- 甲。来源：某白皮书\n"
            "- 乙。参考资料: 某网站\n"
            "- 丙。参考文献：某论文\n"
            "- 丁。Source: https://example.invalid/doc\n"
        )
        self.assertEqual(len(find_ai_draft_policy_violations(draft)), 4)

    def test_placeholder_sources_are_not_violations(self) -> None:
        draft = (
            "- 甲。来源：未知\n"
            "- 乙。来源：未知 / 待查证\n"
            "- 丙。来源：待查证\n"
            "- 丁。来源：未提供\n"
            "- 戊。来源：用户提供\n"
            "- 己。source: evidence\n"
        )
        self.assertEqual(find_ai_draft_policy_violations(draft), [])

    def test_duplicate_lines_are_reported_once_and_capped(self) -> None:
        draft = "来源：同一文档\n来源：同一文档\n" + "".join(
            f"来源：文档{index}\n" for index in range(10)
        )
        self.assertEqual(len(find_ai_draft_policy_violations(draft)), 11)
        self.assertEqual(
            len(find_ai_draft_policy_violations(draft, max_violations=3)),
            3,
        )

    def test_non_positive_cap_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            find_ai_draft_policy_violations("来源：x", max_violations=0)


class ClaimClassificationEdgeCaseTests(unittest.TestCase):
    def test_empty_candidate_list_records_nothing(self) -> None:
        output: list[str] = []
        result = classify_claim_candidates(
            [],
            input_fn=lambda _prompt: self.fail("must not prompt"),
            output_fn=output.append,
        )
        self.assertIsNone(result)
        self.assertTrue(any("没有抽取到" in line for line in output))

    def test_invalid_kind_is_reprompted_until_valid(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        output: list[str] = []
        claims = classify_claim_candidates(
            candidates,
            input_fn=_answers("5", "fact", "1", "3", "CONFIRM"),
            output_fn=output.append,
        )
        assert claims is not None
        self.assertEqual(
            [item["kind"] for item in claims],
            ["verifiable_fact", "recommendation"],
        )
        self.assertEqual(sum("分类无效" in line for line in output), 2)

    def test_confirm_keyword_is_exact(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        output: list[str] = []
        claims = classify_claim_candidates(
            candidates,
            input_fn=_answers("1", "3", "confirm", "9", "CONFIRM"),
            output_fn=output.append,
        )
        assert claims is not None
        self.assertEqual(sum("有效候选编号" in line for line in output), 2)

    def test_cancel_during_edit_records_nothing(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        output: list[str] = []
        result = classify_claim_candidates(
            candidates,
            input_fn=_answers("1", "3", "2", ""),
            output_fn=output.append,
        )
        self.assertIsNone(result)
        self.assertTrue(any("修改未完成" in line for line in output))

    def test_review_lists_human_labels(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        output: list[str] = []
        classify_claim_candidates(
            candidates,
            input_fn=_answers("2", "4", "CONFIRM"),
            output_fn=output.append,
        )
        self.assertTrue(any(line.startswith("1. [解释/判断]") for line in output))
        self.assertTrue(any(line.startswith("2. [假设]") for line in output))

    def test_candidate_input_is_not_mutated(self) -> None:
        candidates = extract_claim_candidates(SMALL_DRAFT)
        snapshot = json.loads(json.dumps(candidates))
        classify_claim_candidates(
            candidates,
            input_fn=_answers("1", "3", "CONFIRM"),
            output_fn=lambda _line: None,
        )
        self.assertEqual(candidates, snapshot)


class ClaimSourceSnapshotTests(unittest.TestCase):
    def _run(self, root: Path, *, with_draft: bool) -> Path:
        generated = create_pack_from_goal(
            "技术选型：比较 Python、TypeScript 和 Rust",
            workspace=root,
        )
        status = create_run(generated.path, root / "runs")
        run_dir = root / "runs" / status["run_id"]
        approve_run(run_dir, approver="Human Reviewer", note="Task 1 reviewed")
        resume_run(run_dir)
        if with_draft:
            record_supplemental_evidence(
                run_dir,
                content=SMALL_DRAFT,
                source="ollama://qwen2.5:7b",
                method="unit test draft",
                limitations="requires human verification",
                collected_by="Ollama (qwen2.5:7b)",
                evidence_role="ai_draft",
            )
        return run_dir

    def test_snapshot_returns_current_source_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), with_draft=True)
            path, digest, content = read_claim_source_snapshot(run_dir, TASK_ID)
            self.assertTrue(path.is_file())
            self.assertTrue(path.is_relative_to(run_dir))
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertIn("Python：开发速度快", content)

    def test_snapshot_rejects_unexecuted_task(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), with_draft=False)
            with self.assertRaisesRegex(RunStateError, "executed Task"):
                read_claim_source_snapshot(run_dir, "TASK-LOCAL-03-not-executed")

    def test_record_rejects_mismatched_expected_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), with_draft=True)
            with self.assertRaisesRegex(RunStateError, "source changed"):
                record_confirmed_claims(
                    run_dir,
                    task_id=TASK_ID,
                    confirmed_by="Human",
                    confirmed_at="2026-01-01T00:00:00Z",
                    claims=[
                        {
                            "text": "建议先做最小验证。",
                            "locator": {"kind": "quote", "value": "建议先做最小验证。"},
                            "kind": "recommendation",
                            "evidence_ids": [],
                            "support": "unsupported",
                        }
                    ],
                    expected_source_artifact_sha256="0" * 64,
                )
            self.assertFalse((run_dir / "claims").exists())

    def test_confirmation_without_ai_draft_is_a_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), with_draft=False)
            output: list[str] = []
            result = _confirm_ai_draft_claims(
                run_dir,
                TASK_ID,
                lambda _prompt: self.fail("must not prompt"),
                output.append,
            )
            self.assertIsNone(result)
            self.assertTrue(any("没有可抽取 Claim" in line for line in output))
            self.assertFalse((run_dir / "claims").exists())

    def test_confirmation_output_states_source_hash_and_no_ai_call(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = self._run(Path(temporary), with_draft=True)
            _, digest, _ = read_claim_source_snapshot(run_dir, TASK_ID)
            output: list[str] = []
            with patch("research_os_mvp.wizard.generate_research") as generator:
                recorded = _confirm_ai_draft_claims(
                    run_dir,
                    TASK_ID,
                    _answers("1", "3", "CONFIRM", ""),
                    output.append,
                )
            generator.assert_not_called()
            self.assertIsNotNone(recorded)
            joined = "\n".join(output)
            self.assertIn(digest, joined)
            self.assertIn("未再次调用 AI", joined)
            self.assertIn("hard_gate_pass=False", joined)
            record = read_json(run_dir / "claims" / f"CLAIMS-{TASK_ID}.json")
            self.assertEqual(record["confirmed_by"], "Human Owner (Easy Mode)")


if __name__ == "__main__":
    unittest.main()
