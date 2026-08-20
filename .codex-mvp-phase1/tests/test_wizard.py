from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_os_mvp.ai import (
    AIProviderError,
    AIResponse,
    AISettings,
    save_ollama_settings,
)
from research_os_mvp.errors import RunStateError
from research_os_mvp.runtime import verify_run
from research_os_mvp.wizard import (
    _choose_category,
    render_easy_review,
    run_easy_wizard,
    run_wizard,
)


class WizardTests(unittest.TestCase):
    @staticmethod
    def _fake_ai_generate(settings: AISettings, _prompt: str) -> AIResponse:
        model = settings.model
        return AIResponse(
            content="针对当前任务生成的本地 AI 草稿。",
            provider="ollama",
            model=model,
            endpoint="http://127.0.0.1:11434",
            elapsed_seconds=0.1,
        )

    def test_category_choice_rejects_non_positive_numbers(self) -> None:
        for selected in ("-1", "-0"):
            with self.subTest(selected=selected), self.assertRaises(RunStateError):
                _choose_category(lambda _prompt, value=selected: value, lambda _line: None)

    def test_wizard_can_exit_immediately(self) -> None:
        answers = iter(["0"])
        output: list[str] = []
        result = run_wizard(
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )
        self.assertEqual(result, 0)
        self.assertTrue(any("已退出" in line for line in output))

    def test_wizard_quickstart_creates_pack_and_paused_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：核对 CLI 需求和测试证据",
                    "0",
                    "单人本地原型",
                    "0",
                ]
            )
            output: list[str] = []
            result = run_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            self.assertEqual(result, 0)
            packs = list((Path(temporary) / "packs").glob("*.json"))
            runs = list((Path(temporary) / "runs").glob("run-*"))
            self.assertEqual(len(packs), 1)
            self.assertEqual(len(runs), 1)
            self.assertTrue((runs[0] / "HASHES.json").is_file())
            self.assertTrue(any("状态=paused" in line for line in output))

    def test_wizard_can_cancel_run_after_exact_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：核对 CLI 需求和测试证据",
                    "0",
                    "单人本地原型",
                    "13",
                    "",
                    "CANCEL",
                    "",
                    "范围已经变化",
                    "0",
                ]
            )
            output: list[str] = []
            result = run_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )

            self.assertEqual(result, 0)
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "cancelled")
            self.assertEqual(status["cancellation_reason"], "范围已经变化")
            self.assertTrue(any("状态=cancelled" in line for line in output))

    def test_easy_wizard_completes_with_three_yes_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "技术选型：比较 Python、TypeScript 和 Rust",
                    "1000 元，一个月",
                    "本地 Windows",
                    "离线运行",
                    "开发效率",
                    "y",
                    "y",
                    "y",
                    "y",
                    "0",
                ]
            )
            output: list[str] = []
            result = run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            self.assertEqual(result, 0)
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "completed")
            self.assertEqual(status["approval_count"], 3)
            self.assertEqual(status["review_count"], 3)
            self.assertTrue(any("研究准备流程已经完成" in line for line in output))
            handoffs = list((Path(temporary) / "handoffs").glob("*.md"))
            self.assertEqual(len(handoffs), 1)
            handoff_text = handoffs[0].read_text(encoding="utf-8")
            self.assertIn("真正收集和比较证据", handoff_text)

    def test_easy_wizard_can_save_and_continue_latest_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first_answers = iter(
                [
                    "1",
                    "项目验收：核对需求和测试证据",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "",
                    "0",
                ]
            )
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(first_answers),
                output_fn=lambda _line: None,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            self.assertEqual(verify_run(run_dir)["status"], "paused")

            second_answers = iter(["2", "y", "y", "y", "0"])
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(second_answers),
                output_fn=lambda _line: None,
            )
            self.assertEqual(verify_run(run_dir)["status"], "completed")

    def test_easy_wizard_collects_pasted_hardware_constraints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "硬件选型：比较 ESP32、STM32 和树莓派",
                    "1000 元",
                    "1 台室内原型",
                    "USB 供电",
                    "Wi-Fi",
                    "每分钟采样，后续手机查看",
                    "y",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            evidence = next((run_dir / "evidence").glob("*.json"))
            content = evidence.read_text(encoding="utf-8")
            self.assertIn("预算：1000 元", content)
            self.assertIn("数量：1 台室内原型", content)
            self.assertIn("供电：USB 供电", content)
            self.assertIn("联网：Wi-Fi", content)
            self.assertIn("环境与扩展：每分钟采样，后续手机查看", content)

    def test_easy_wizard_asks_for_missing_budget_unit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "硬件选型：比较两个主控",
                    "1000",
                    "元",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "",
                    "0",
                ]
            )
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=lambda _line: None,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            evidence = next((run_dir / "evidence").glob("*.json"))
            self.assertIn("预算：1000 元", evidence.read_text(encoding="utf-8"))

    def test_easy_wizard_imports_a_dropped_file_at_task_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "datasheet.txt"
            source.write_text("传感器精度：待以正式数据手册核验", encoding="utf-8")
            answers = iter(
                [
                    "1",
                    "学习研究：整理一份数据手册",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "f",
                    f'"{source}"',
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "paused")
            self.assertEqual(status["evidence_count"], 3)
            self.assertTrue(any("资料已写入 Evidence" in line for line in output))
            imported = list((run_dir / "evidence").glob("EVID-SUPPLEMENTAL-*.json"))
            self.assertEqual(len(imported), 1)
            self.assertIn("imported_source", imported[0].read_text(encoding="utf-8"))

    def test_easy_wizard_rejects_text_in_approval_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "硬件选型：比较两个主控",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "执行 Research-OS 刚生成的 AI 研究指令",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            self.assertTrue(any("这里仅接收" in line for line in output))
            self.assertTrue(any("发送到 Codex" in line for line in output))

    def test_easy_wizard_lists_supported_question_types(self) -> None:
        answers = iter(["6", "0"])
        output: list[str] = []
        run_easy_wizard(
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )
        catalog = "\n".join(output)
        self.assertIn("可以提问的 8 类任务", catalog)
        self.assertIn("硬件选型", catalog)

    def test_easy_wizard_auto_imports_ai_and_supports_rework(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：检查本地 AI Evidence",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "r",
                    "请明确标出未知项",
                    "y",
                    "y",
                    "0",
                ]
            )
            calls: list[str] = []

            def fake_generate(settings: object, prompt: str) -> AIResponse:
                calls.append(prompt)
                version = len(calls)
                return AIResponse(
                    content=f"本地 AI 第 {version} 版：未知参数待查证。",
                    provider="ollama",
                    model="qwen2.5:7b",
                    endpoint="http://127.0.0.1:11434",
                    elapsed_seconds=0.1,
                )

            output: list[str] = []
            result = run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=fake_generate,
            )
            self.assertEqual(result, 0)
            self.assertEqual(len(calls), 2)
            self.assertIn("人工返工要求", calls[1])
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "completed")
            self.assertEqual(status["evidence_count"], 4)
            self.assertEqual(status["supplemental_evidence_count"], 2)
            self.assertEqual(status["review_count"], 4)
            revisions = sorted((run_dir / "evidence").glob("EVID-SUPPLEMENTAL-*.json"))
            revised = json.loads(revisions[-1].read_text(encoding="utf-8"))
            self.assertIsNotNone(revised["review_decision_hash"])
            joined = "\n".join(output)
            self.assertIn("本地 AI 初稿已写入 Evidence", joined)
            self.assertIn("AI 返工稿已写入 Evidence", joined)

    def test_easy_wizard_records_rejected_as_reviewer_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：审查输出是否满足目标",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "x",
                    "需求理解方向错误",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "rejected")
            self.assertEqual(status["latest_review_decision"], "Rejected")
            self.assertEqual(status["approval_count"], 0)
            self.assertTrue(any("正式 Rejected" in line for line in output))

    def test_advanced_wizard_records_formal_changes_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：核对 CLI 需求",
                    "0",
                    "单人本地原型",
                    "14",
                    "",
                    "c",
                    "Reviewer A",
                    "请补充失败路径",
                    "15",
                    "",
                    "",
                    "已补充失败路径",
                    "修订版：先验证失败路径，再执行正常验收。",
                    "0",
                ]
            )
            run_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=lambda _line: None,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "paused")
            self.assertEqual(status["latest_review_decision"], "Changes Requested")
            self.assertEqual(status["latest_reviewer"], "Reviewer A")
            self.assertEqual(status["task_output_revision_count"], 1)

    def test_easy_wizard_records_task_one_revision_after_changes_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：核对完成标准",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "r",
                    "请补充明确验收边界",
                    "修订版：CLI 功能、错误路径和双版本测试均通过。",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["status"], "paused")
            self.assertEqual(status["review_count"], 1)
            self.assertEqual(status["task_output_revision_count"], 1)
            self.assertTrue(any("Task 产物修订版已写入" in line for line in output))

    def test_easy_wizard_runs_ai_audit_and_shows_version_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                reviewer_model="qwen-auditor:latest",
            )
            answers = iter(
                [
                    "1",
                    "项目验收：复核 AI 研究草稿",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "v",
                    "y",
                    "y",
                    "10",
                    "0",
                ]
            )
            calls: list[tuple[str, str]] = []

            def fake_generate(settings: object, prompt: str) -> AIResponse:
                model = settings.model
                calls.append((model, prompt))
                content = "审计结论：NEEDS-REVISION" if len(calls) == 2 else "研究初稿"
                return AIResponse(
                    content=content,
                    provider="ollama",
                    model=model,
                    endpoint="http://127.0.0.1:11434",
                    elapsed_seconds=0.1,
                )

            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=fake_generate,
            )
            self.assertEqual(calls[0][0], "qwen2.5:7b")
            self.assertEqual(calls[1][0], "qwen-auditor:latest")
            self.assertIn("第二审计角色", calls[1][1])
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            status = verify_run(run_dir)
            self.assertEqual(status["evidence_count"], 4)
            joined = "\n".join(output)
            self.assertIn("AI 审计意见已写入 Evidence", joined)
            self.assertIn("版本历史", joined)

    def test_easy_wizard_starts_from_named_project_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "11",
                    "5",
                    "检查本地项目的输入校验",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            pack = next((Path(temporary) / "packs").glob("*.json"))
            self.assertIn("security-audit", pack.read_text(encoding="utf-8"))
            self.assertTrue(any("已使用项目模板：安全审计" in line for line in output))

    def test_warns_when_local_ai_unconfigured_before_task_two_decision(self) -> None:
        for automatic_disabled in (False, True):
            with (
                self.subTest(automatic_disabled=automatic_disabled),
                tempfile.TemporaryDirectory() as temporary,
            ):
                    if automatic_disabled:
                        save_ollama_settings(
                            temporary,
                            model="qwen2.5:7b",
                            automatic_research=False,
                        )
                    answers = iter(
                        [
                            "1",
                            "项目验收：确认第 2 步模板告知",
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
                    transcript: list[str] = []

                    def input_with_transcript(
                        prompt: str,
                        responses: object = answers,
                        captured: list[str] = transcript,
                    ) -> str:
                        captured.append(prompt)
                        return next(responses)

                    run_easy_wizard(
                        workspace=temporary,
                        input_fn=input_with_transcript,
                        output_fn=transcript.append,
                    )
                    warning_index = next(
                        index
                        for index, line in enumerate(transcript)
                        if "⚠ 第 2 步提示" in line
                    )
                    decision_index = next(
                        index
                        for index, line in enumerate(transcript[warning_index + 1 :], start=warning_index + 1)
                        if "Reviewer 决定" in line
                    )
                    self.assertLess(warning_index, decision_index)
                    self.assertIn("通用评估框架（模板）", transcript[warning_index])
                    self.assertIn("不是针对本任务的 AI 分析", transcript[warning_index])

    def test_warning_names_the_configure_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：确认本地 AI 配置提示",
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
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            warning = next(line for line in output if "⚠ 第 2 步提示" in line)
            self.assertIn("research-os-mvp configure-ollama", warning)
            self.assertIn("配置后重新开始一个任务", warning)
            self.assertIn("也可以知情后继续当前流程", warning)

    def test_no_warning_when_local_ai_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：确认已配置 AI 不显示降级警告",
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
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=self._fake_ai_generate,
            )
            self.assertNotIn("⚠ 第 2 步提示", "\n".join(output))

    def test_evidence_sources_are_labelled_in_review_render(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            source = Path(temporary) / "external-source.txt"
            source.write_text("来自外部资料的待核验事实。", encoding="utf-8")
            answers = iter(
                [
                    "1",
                    "项目验收：确认 Evidence 来源展示",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "f",
                    str(source),
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=self._fake_ai_generate,
            )
            rendered = "\n".join(output)
            self.assertIn("来源类型：你的输入", rendered)
            self.assertIn("来源类型：通用评估框架（模板）", rendered)
            self.assertIn("来源类型：本地 AI 针对本任务生成的草稿", rendered)
            self.assertIn("导入的外部资料 |", rendered)

    def test_template_evidence_is_marked_as_generic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：确认通用模板标签",
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
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=lambda _line: None,
            )
            run_dir = next((Path(temporary) / "runs").glob("run-*"))
            rendered = render_easy_review(run_dir)
            self.assertIn("来源类型：通用评估框架（模板）", rendered)

    def test_completion_message_names_the_handoff_purpose(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：确认完成后的研究交接动作",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "y",
                    "y",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=self._fake_ai_generate,
            )
            handoff = next((Path(temporary) / "handoffs").glob("*.md")).resolve()
            completion = "\n".join(output)
            self.assertIn(f"Handoff 完整路径：{handoff}", completion)
            self.assertIn("Codex / ChatGPT / Claude 等能联网的 AI", completion)
            self.assertIn("菜单 8 导入", completion)
            self.assertIn("菜单 9 打开高级菜单，再选择 15", completion)
            self.assertIn("记录闭环完成不等于候选方案已经完成真实比较", completion)

    def test_completion_message_survives_when_ai_unconfigured(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            answers = iter(
                [
                    "1",
                    "项目验收：确认未配置 AI 时的完成提示",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "y",
                    "y",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            completion = "\n".join(output)
            self.assertIn("Handoff 完整路径：", completion)
            self.assertIn("菜单 8 导入", completion)
            self.assertIn("research-os-mvp configure-ollama", completion)
            self.assertIn("第 2 步获得本地 AI 草稿", completion)

    def test_retry_key_appears_only_when_ai_configured_and_no_draft(self) -> None:
        with tempfile.TemporaryDirectory() as configured_temporary:
            save_ollama_settings(
                configured_temporary,
                model="qwen2.5:7b",
                automatic_research=False,
            )
            configured_answers = iter(
                [
                    "1",
                    "项目验收：确认重试键显示条件",
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
            configured_prompts: list[str] = []

            def configured_input(prompt: str) -> str:
                configured_prompts.append(prompt)
                return next(configured_answers)

            run_easy_wizard(
                workspace=configured_temporary,
                input_fn=configured_input,
                output_fn=lambda _line: None,
            )
            configured_review = next(
                prompt for prompt in configured_prompts if "F 导入资料" in prompt
            )
            self.assertIn("A 重试 AI", configured_review)

        with tempfile.TemporaryDirectory() as unconfigured_temporary:
            unconfigured_answers = iter(
                [
                    "1",
                    "项目验收：确认未配置时不显示重试键",
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
            unconfigured_prompts: list[str] = []

            def unconfigured_input(prompt: str) -> str:
                unconfigured_prompts.append(prompt)
                return next(unconfigured_answers)

            run_easy_wizard(
                workspace=unconfigured_temporary,
                input_fn=unconfigured_input,
                output_fn=lambda _line: None,
            )
            unconfigured_review = next(
                prompt for prompt in unconfigured_prompts if "F 导入资料" in prompt
            )
            self.assertNotIn("A 重试 AI", unconfigured_review)

        with tempfile.TemporaryDirectory() as draft_temporary:
            save_ollama_settings(draft_temporary, model="qwen2.5:7b")
            draft_answers = iter(
                [
                    "1",
                    "项目验收：确认已有草稿时不显示重试键",
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
            draft_prompts: list[str] = []

            def draft_input(prompt: str) -> str:
                draft_prompts.append(prompt)
                return next(draft_answers)

            run_easy_wizard(
                workspace=draft_temporary,
                input_fn=draft_input,
                output_fn=lambda _line: None,
                ai_generate_fn=self._fake_ai_generate,
            )
            draft_review = next(
                prompt for prompt in draft_prompts if "F 导入资料" in prompt
            )
            self.assertNotIn("A 重试 AI", draft_review)

    def test_retry_key_triggers_a_new_ai_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：确认显式 AI 重试",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "a",
                    "",
                    "0",
                ]
            )
            attempts: list[str] = []

            def fail_then_succeed(settings: AISettings, prompt: str) -> AIResponse:
                attempts.append(prompt)
                if len(attempts) == 1:
                    raise AIProviderError("模拟首次调用失败")
                return self._fake_ai_generate(settings, prompt)

            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=fail_then_succeed,
            )
            self.assertEqual(len(attempts), 2)
            rendered = "\n".join(output)
            self.assertIn("正在重试本地 AI", rendered)
            self.assertIn("本地 AI 初稿已写入 Evidence", rendered)

    def test_automatic_retry_loop_is_still_prevented(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：确认自动失败不会循环重试",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "v",
                    "",
                    "0",
                ]
            )
            attempts: list[str] = []

            def always_fail(_settings: AISettings, prompt: str) -> AIResponse:
                attempts.append(prompt)
                raise AIProviderError("模拟持续失败")

            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=lambda _line: None,
                ai_generate_fn=always_fail,
            )
            self.assertEqual(len(attempts), 1)

    def test_audit_key_explains_why_no_draft_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(
                temporary,
                model="qwen2.5:7b",
                automatic_research=False,
            )
            answers = iter(
                [
                    "1",
                    "项目验收：确认无草稿审计引导",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "v",
                    "",
                    "0",
                ]
            )
            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
            )
            rendered = "\n".join(output)
            self.assertIn("尚未调用或尚未生成草稿", rendered)
            self.assertIn("按 A 重试生成", rendered)
            self.assertIn("按 F 导入资料", rendered)
            self.assertIn("按 Y 直接批准通用模板", rendered)

    def test_audit_key_message_mentions_prior_ai_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            save_ollama_settings(temporary, model="qwen2.5:7b")
            answers = iter(
                [
                    "1",
                    "项目验收：确认审计提示识别调用失败",
                    "",
                    "",
                    "",
                    "",
                    "y",
                    "y",
                    "v",
                    "",
                    "0",
                ]
            )

            def fail_ai(_settings: AISettings, _prompt: str) -> AIResponse:
                raise AIProviderError("模拟 AI 调用失败")

            output: list[str] = []
            run_easy_wizard(
                workspace=temporary,
                input_fn=lambda _prompt: next(answers),
                output_fn=output.append,
                ai_generate_fn=fail_ai,
            )
            rendered = "\n".join(output)
            self.assertIn("此前本地 AI 调用已失败", rendered)
            self.assertIn("按 A 重试生成", rendered)

    def test_existing_run_verify_unchanged_after_ux02(self) -> None:
        runs_root = Path(__file__).resolve().parents[1] / "workspace" / "runs"
        expected = {
            "run-20260820t062550z-969cbc95": (
                "6447a0f78ef68a7775b624c4189d6306b958a3abcf906191a199be35fe497a3a",
                {
                    "evidence/EVID-01-task-local-01-capture-goal.json": "047a70c456410ae1187b4c3dada3cf1a91288cc4a14585ceba089b300b292712",
                    "evidence/EVID-02-task-local-02-record-evaluation-frame.json": "092d397326fcfcabf93751a09d5732fdd4cf4940ff4897ca33a7957d44aaf1aa",
                },
            ),
            "run-20260820t071348z-65b76017": (
                "c1fa6b16207df8e3c0997740ba15b5d942d90a07a64e48735ccc231153f126da",
                {
                    "evidence/EVID-01-task-local-01-capture-goal.json": "ac8ce03f2d912b10bbb93fa1eb4991e4798ae7963eb6c57efa6612f67d4c5712",
                    "evidence/EVID-02-task-local-02-record-evaluation-frame.json": "de215c408d6e642f72d0fa72c1873c178dd35f9aca7423a0f7cd08fdf372f7aa",
                },
            ),
        }
        for run_id, (review_hash, evidence_hashes) in expected.items():
            with self.subTest(run_id=run_id):
                run_dir = runs_root / run_id
                status = verify_run(run_dir)
                self.assertEqual(status["integrity"], "verified")
                self.assertEqual(status["status"], "completed")
                self.assertEqual(status["checkpoint"], "current")
                self.assertEqual(status["event_count"], 23)
                self.assertEqual(status["evidence_count"], 2)
                self.assertEqual(status["report_count"], 4)
                self.assertEqual(status["hashed_file_count"], 11)
                self.assertEqual(status["latest_review_hash"], review_hash)
                manifest = json.loads(
                    (run_dir / "HASHES.json").read_text(encoding="utf-8")
                )
                actual_evidence_hashes = {
                    item["path"]: item["sha256"]
                    for item in manifest["files"]
                    if item["path"].startswith("evidence/")
                }
                self.assertEqual(actual_evidence_hashes, evidence_hashes)

    def test_existing_run_verify_unchanged_after_ux01(self) -> None:
        run_dir = (
            Path(__file__).resolve().parents[1]
            / "workspace"
            / "runs"
            / "run-20260820t062550z-969cbc95"
        )
        status = verify_run(run_dir)
        selected = {
            key: status[key]
            for key in (
                "integrity",
                "status",
                "checkpoint",
                "event_count",
                "evidence_count",
                "report_count",
                "hashed_file_count",
                "pack_sha256",
                "latest_review_hash",
            )
        }
        self.assertEqual(
            selected,
            {
                "integrity": "verified",
                "status": "completed",
                "checkpoint": "current",
                "event_count": 23,
                "evidence_count": 2,
                "report_count": 4,
                "hashed_file_count": 11,
                "pack_sha256": "4064fce8de159c9be178dd646c3b85c0a5031692479e5549a2d41a243351f514",
                "latest_review_hash": "6447a0f78ef68a7775b624c4189d6306b958a3abcf906191a199be35fe497a3a",
            },
        )
        manifest = json.loads((run_dir / "HASHES.json").read_text(encoding="utf-8"))
        protected_hashes = {
            item["path"]: item["sha256"]
            for item in manifest["files"]
            if item["path"] == "pack.snapshot.json"
            or item["path"].startswith(("evidence/", "reports/"))
        }
        self.assertEqual(
            protected_hashes,
            {
                "evidence/EVID-01-task-local-01-capture-goal.json": "047a70c456410ae1187b4c3dada3cf1a91288cc4a14585ceba089b300b292712",
                "evidence/EVID-02-task-local-02-record-evaluation-frame.json": "092d397326fcfcabf93751a09d5732fdd4cf4940ff4897ca33a7957d44aaf1aa",
                "pack.snapshot.json": "0f56f9de810fd8378abd23f7fca45473fa53f62d8302b6c0d6ac5e3424b9fa26",
                "reports/REPORT-MISSION-mission-local-goal-9a5618dc52.md": "2b431e3e40aeb63fa0366f4c147a3cbea67c016471ab76b107bb05a6fe3fc61b",
                "reports/TASK-REPORT-01.json": "d0f3519dfa6d0e358e0c1ed93a63f954828e71e975a2831d698805169d490f27",
                "reports/TASK-REPORT-02.json": "9ee25832298ba62a40f6c5c7a902328c32f371e338efeaea6fab9c546c67289a",
                "reports/TASK-REPORT-03.json": "1741a2342f26709b830345af26fce3205e949fac9f0db6c0c684c3ddf0a23eec",
            },
        )

    def test_evidence_content_hashes_unchanged(self) -> None:
        evidence_dir = (
            Path(__file__).resolve().parents[1]
            / "workspace"
            / "runs"
            / "run-20260820t062550z-969cbc95"
            / "evidence"
        )
        expected = {
            "EVID-01-task-local-01-capture-goal.json": (
                "8c226f1d8f9c2053f7914136986f7548b532781de9823e2a38b455d44a262bc4",
                "047a70c456410ae1187b4c3dada3cf1a91288cc4a14585ceba089b300b292712",
            ),
            "EVID-02-task-local-02-record-evaluation-frame.json": (
                "a98094876e29354f94d25ac6180c620d05f9c823df6ea73e69fcd22d2c73fcde",
                "092d397326fcfcabf93751a09d5732fdd4cf4940ff4897ca33a7957d44aaf1aa",
            ),
        }
        self.assertEqual(
            {path.name for path in evidence_dir.glob("*.json")},
            set(expected),
        )
        for name, (content_hash, file_hash) in expected.items():
            with self.subTest(name=name):
                path = evidence_dir / name
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["content_sha256"], content_hash)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), file_hash)

    def test_double_click_launcher_opens_easy_mode(self) -> None:
        launcher = Path(__file__).resolve().parents[1] / "双击这里开始.cmd"
        content = launcher.read_text(encoding="utf-8")
        self.assertTrue(content.isascii())
        self.assertIn("-m research_os_mvp easy", content)
        self.assertIn("--workspace", content)


if __name__ == "__main__":
    unittest.main()
