from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_os_mvp.errors import PackValidationError
from research_os_mvp.natural_language import (
    build_pack_from_goal,
    context_questions_for,
    create_pack_from_goal,
    infer_category,
    list_scenarios,
    resolve_category,
)
from research_os_mvp.pack import load_pack


class NaturalLanguagePackTests(unittest.TestCase):
    def test_all_eight_scenarios_are_listed(self) -> None:
        scenarios = list_scenarios()
        self.assertEqual(len(scenarios), 8)
        self.assertEqual(len({item["key"] for item in scenarios}), 8)

    def test_eight_representative_goals_are_classified(self) -> None:
        cases = {
            "技术选型：比较 Python、TypeScript 和 Rust 框架": "technology-selection",
            "项目决策：记录采用或放弃方案的原因": "project-decision",
            "学习 Transformer 论文并记录理解": "learning-research",
            "项目验收：核对需求清单和交付证据": "project-acceptance",
            "安全审计：检查漏洞、权限和威胁": "security-audit",
            "硬件选型：比较 ESP32 和 STM32 主控": "hardware-selection",
            "内容核查：核查新闻真假和原始来源": "content-verification",
            "AI 工作监督：Agent 每次暂停等待批准": "ai-supervision",
        }
        for goal, expected in cases.items():
            with self.subTest(goal=goal):
                self.assertEqual(infer_category(goal), expected)

    def test_unknown_goal_defaults_to_learning_research(self) -> None:
        self.assertEqual(infer_category("请帮我系统化理清这件事"), "learning-research")

    def test_generated_pack_is_valid_and_honest_about_template_limits(self) -> None:
        pack, profile = build_pack_from_goal(
            "比较 Python、TypeScript 和 Rust 的技术栈",
            category="auto",
            context="用于单人本地 AI 工具",
        )
        self.assertEqual(profile.key, "technology-selection")
        self.assertEqual(len(pack["mission"]["tasks"]), 3)
        self.assertTrue(all(task["requires_approval"] for task in pack["mission"]["tasks"]))
        framework = pack["mission"]["tasks"][1]["input"]
        self.assertIn("不是候选项结论", framework["content"])
        self.assertIn("不包含", framework["limitations"])

    def test_generation_is_deterministic(self) -> None:
        first, _ = build_pack_from_goal("验收一个 CLI 项目", category="project-acceptance")
        second, _ = build_pack_from_goal("验收一个 CLI 项目", category="project-acceptance")
        self.assertEqual(first, second)
        self.assertEqual(first["pack_id"], second["pack_id"])

    def test_create_is_idempotent_for_identical_goal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = create_pack_from_goal("研究 Attention", workspace=temporary)
            second = create_pack_from_goal("研究 Attention", workspace=temporary)
            self.assertFalse(first.reused)
            self.assertTrue(second.reused)
            self.assertEqual(first.canonical_sha256, second.canonical_sha256)
            self.assertEqual(load_pack(first.path).canonical_sha256, first.canonical_sha256)

    def test_existing_different_output_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixed.json"
            create_pack_from_goal("研究 A", output=output)
            before = output.read_bytes()
            with self.assertRaisesRegex(PackValidationError, "different content"):
                create_pack_from_goal("研究 B", output=output)
            self.assertEqual(output.read_bytes(), before)

    def test_custom_criteria_replace_profile_defaults(self) -> None:
        pack, _ = build_pack_from_goal(
            "比较两个框架",
            category="technology-selection",
            criteria=["冷启动时间", "离线开发体验"],
        )
        content = pack["mission"]["tasks"][1]["input"]["content"]
        self.assertIn("冷启动时间", content)
        self.assertNotIn("迁移、学习与运维成本", content)

    def test_mission_title_does_not_repeat_category_prefix(self) -> None:
        pack, _ = build_pack_from_goal(
            "硬件选型：比较 ESP32、STM32 和树莓派",
            category="auto",
        )
        self.assertEqual(
            pack["mission"]["title"],
            "硬件选型：比较 ESP32、STM32 和树莓派",
        )
        self.assertNotIn("硬件选型：硬件选型", pack["mission"]["title"])

    def test_third_task_is_labeled_as_research_preparation(self) -> None:
        pack, _ = build_pack_from_goal("比较两个主控", category="hardware-selection")
        third = pack["mission"]["tasks"][2]
        self.assertIn("研究准备报告", third["name"])
        self.assertIn("Research Preparation", third["input"]["title"])

    def test_hardware_context_questions_are_structured(self) -> None:
        profile = resolve_category("hardware-selection", "比较两个主控")
        labels = [label for label, _prompt in context_questions_for(profile)]
        self.assertEqual(labels, ["预算", "数量", "供电", "联网", "环境与扩展"])


if __name__ == "__main__":
    unittest.main()
