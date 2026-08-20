from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_os_mvp.errors import PackValidationError
from research_os_mvp.integrity import (
    canonical_json_bytes,
    sha256_bytes,
    sha256_text,
    write_json_atomic,
)
from research_os_mvp.pack import load_pack, validate_pack_data


@dataclass(frozen=True)
class ScenarioProfile:
    key: str
    name_zh: str
    description: str
    keywords: tuple[str, ...]
    criteria: tuple[str, ...]
    example: str


@dataclass(frozen=True)
class GeneratedPack:
    path: Path
    data: dict[str, Any]
    category: str
    category_name: str
    canonical_sha256: str
    reused: bool


SCENARIO_PROFILES: tuple[ScenarioProfile, ...] = (
    ScenarioProfile(
        key="technology-selection",
        name_zh="技术选型",
        description="比较语言、框架、数据库或工具并记录取舍。",
        keywords=(
            "技术选型",
            "框架",
            "python",
            "typescript",
            "rust",
            "java",
            "数据库",
            "选什么",
            "对比技术",
        ),
        criteria=(
            "目标与场景适配度",
            "开发与调试效率",
            "生态、人才与长期维护性",
            "性能、安全与可靠性",
            "迁移、学习与运维成本",
        ),
        example="比较 Python、TypeScript 和 Rust，选择适合本地 AI 工具的技术栈。",
    ),
    ScenarioProfile(
        key="project-decision",
        name_zh="项目决策",
        description="记录方案被采用、延后或放弃的原因。",
        keywords=(
            "项目决策",
            "采用",
            "放弃",
            "延后",
            "方案决策",
            "取舍",
            "是否要做",
        ),
        criteria=(
            "与当前目标和优先级的一致性",
            "预期收益与可验证性",
            "成本、时间、依赖和机会成本",
            "主要风险与回滚方式",
            "采用、延后和放弃各自的触发条件",
        ),
        example="决定项目是否现在引入数据库，并记录采用或延后的原因。",
    ),
    ScenarioProfile(
        key="learning-research",
        name_zh="学习研究",
        description="将资料、理解、疑问和结论组织成证据链。",
        keywords=(
            "学习",
            "研究",
            "理解",
            "论文",
            "课程",
            "资料",
            "知识",
            "复习",
        ),
        criteria=(
            "研究问题和边界是否清楚",
            "资料来源、时间和作者是否可追溯",
            "事实、解释、推断和未知项是否分开",
            "关键理解是否能用自己的话复述",
            "结论是否由当前证据支持",
        ),
        example="研究 Transformer 的 Attention 机制，形成可复习的证据与理解报告。",
    ),
    ScenarioProfile(
        key="project-acceptance",
        name_zh="项目验收",
        description="逐项核对需求、测试证据、缺口和批准。",
        keywords=(
            "项目验收",
            "验收",
            "交付",
            "需求清单",
            "接受标准",
            "完成标准",
            "检查清单",
        ),
        criteria=(
            "需求与接受标准是否逐项映射",
            "每个通过项是否有可复现的测试证据",
            "失败、未测和排除项是否明确",
            "剩余风险、限制和后续任务是否记录",
            "人工批准是否在产物核对后发生",
        ),
        example="验收一个 CLI 工具，核对功能、测试、文档和剩余限制。",
    ),
    ScenarioProfile(
        key="security-audit",
        name_zh="安全审计",
        description="记录资产、边界、检查证据、风险和限制。",
        keywords=(
            "安全审计",
            "安全评估",
            "漏洞",
            "威胁",
            "攻击面",
            "权限",
            "安全风险",
            "安全检查",
        ),
        criteria=(
            "资产、信任边界与数据流是否明确",
            "威胁、前置条件与可利用路径是否有证据",
            "风险严重度与发生可能性是否分开",
            "修复建议是否可验证且保留回滚方式",
            "未覆盖范围和剩余风险是否明确",
        ),
        example="审计本地 Web 项目的认证、输入校验和 Secret 管理边界。",
    ),
    ScenarioProfile(
        key="hardware-selection",
        name_zh="硬件选型",
        description="比较主控、传感器、通信和供电方案。",
        keywords=(
            "硬件选型",
            "主控",
            "传感器",
            "单片机",
            "esp32",
            "stm32",
            "通信方案",
            "电源方案",
            "物联网硬件",
        ),
        criteria=(
            "功能、接口和实时性要求",
            "算力、内存、功耗与散热",
            "单价、供货、寿命周期与替代料",
            "开发工具、驱动、社区和调试成本",
            "环境、安全、认证与量产风险",
        ),
        example="比较 ESP32 和 STM32，为低功耗环境监测设备选择主控。",
    ),
    ScenarioProfile(
        key="content-verification",
        name_zh="内容核查",
        description="核对事实主张、原始来源、时效性和反证。",
        keywords=(
            "内容核查",
            "事实核查",
            "核查内容",
            "真假",
            "谣言",
            "新闻核查",
            "来源可靠",
            "引用核查",
        ),
        criteria=(
            "可验证的事实主张是否与观点分开",
            "是否追溯到原始或最接近原始的来源",
            "来源日期、版本、作者和上下文是否完整",
            "是否有独立交叉证据与反证",
            "结论的确定性是否与证据强度匹配",
        ),
        example="核查一段技术文章的五个关键主张，保存原始来源与限制。",
    ),
    ScenarioProfile(
        key="ai-supervision",
        name_zh="AI 工作监督",
        description="声明 AI 的边界、产物、停止条件和人工门禁。",
        keywords=(
            "ai 工作监督",
            "ai工作监督",
            "ai 监督",
            "agent 监督",
            "agent监督",
            "智能体监督",
            "人工门禁",
            "暂停批准",
            "ai 审批",
        ),
        criteria=(
            "AI 的允许动作、禁止动作和可写范围",
            "每个 Task 的可检查产物与成功标准",
            "高风险操作前的显式人工批准点",
            "错误、超范围和缺失信息时的停止条件",
            "Event、Evidence、Report 与 Hash 是否可复核",
        ),
        example="监督 AI 完成一次代码修改，每个阶段提供产物后等待人工批准。",
    ),
)


PROFILE_BY_KEY = {profile.key: profile for profile in SCENARIO_PROFILES}
CATEGORY_ALIASES = {
    **{profile.key: profile.key for profile in SCENARIO_PROFILES},
    **{profile.name_zh: profile.key for profile in SCENARIO_PROFILES},
    "auto": "auto",
    "自动": "auto",
}

CONTEXT_QUESTIONS = {
    "technology-selection": (
        ("预算与期限", "预算和完成期限（可直接回车）："),
        ("部署环境", "本地、服务器、浏览器还是嵌入式环境（可直接回车）："),
        ("必须能力", "必须具备的性能、生态或功能（可直接回车）："),
        ("优先级", "最看重开发速度、性能、成本还是维护性（可直接回车）："),
    ),
    "project-decision": (
        ("期限", "何时必须作出决定（可直接回车）："),
        ("资源", "可用人员、预算和时间（可直接回车）："),
        ("预期收益", "希望获得什么可验证结果（可直接回车）："),
        ("风险边界", "必须回避的风险或失败条件（可直接回车）："),
    ),
    "learning-research": (
        ("已有基础", "您已经了解什么（可直接回车）："),
        ("学习期限", "希望何时完成（可直接回车）："),
        ("目标深度", "入门、能实践还是深入研究（可直接回车）："),
        ("期望产物", "希望得到笔记、练习、代码还是报告（可直接回车）："),
    ),
    "project-acceptance": (
        ("验收对象", "要验收哪个项目或版本（可直接回车）："),
        ("需求来源", "需求清单或接受标准在哪里（可直接回车）："),
        ("交付期限", "何时需要完成验收（可直接回车）："),
        ("重点风险", "最担心哪些缺陷或遗漏（可直接回车）："),
    ),
    "security-audit": (
        ("检查范围", "要检查哪些资产、目录或服务（可直接回车）："),
        ("信任边界", "哪些用户、系统或数据跨越边界（可直接回车）："),
        ("重点风险", "最关注哪些威胁或漏洞类型（可直接回车）："),
        ("排除范围", "哪些内容本轮不检查（可直接回车）："),
    ),
    "hardware-selection": (
        ("预算", "预算是多少（例如 1000 元；可直接回车）："),
        ("数量", "原型或量产数量（例如 1 台；可直接回车）："),
        ("供电", "供电和功耗要求（例如 USB 供电；可直接回车）："),
        ("联网", "联网方式（例如 Wi-Fi、蓝牙、4G；可直接回车）："),
        ("环境与扩展", "环境、采样频率和后续扩展（可直接回车）："),
    ),
    "content-verification": (
        ("待核查主张", "最需要核查的事实主张（可直接回车）："),
        ("时间范围", "内容涉及什么时间范围（可直接回车）："),
        ("优先来源", "优先检查哪些原始来源（可直接回车）："),
        ("使用目的", "核查结果将用于什么场景（可直接回车）："),
    ),
    "ai-supervision": (
        ("允许范围", "AI 可以读取和修改什么（可直接回车）："),
        ("停止条件", "遇到什么情况必须暂停（可直接回车）："),
        ("人工门禁", "哪些动作前必须获得批准（可直接回车）："),
        ("验收要求", "最终需要哪些测试和产物（可直接回车）："),
    ),
}


def list_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "key": profile.key,
            "name_zh": profile.name_zh,
            "description": profile.description,
            "example": profile.example,
            "criteria": list(profile.criteria),
        }
        for profile in SCENARIO_PROFILES
    ]


def infer_category(goal: str) -> str:
    normalized = goal.casefold()
    scored: list[tuple[int, int, str]] = []
    for index, profile in enumerate(SCENARIO_PROFILES):
        score = sum(1 for keyword in profile.keywords if keyword.casefold() in normalized)
        scored.append((score, -index, profile.key))
    best_score, _, best_key = max(scored)
    if best_score == 0:
        return "learning-research"
    return best_key


def resolve_category(category: str, goal: str) -> ScenarioProfile:
    normalized = category.strip()
    key = CATEGORY_ALIASES.get(normalized, CATEGORY_ALIASES.get(normalized.casefold()))
    if key is None:
        allowed = ", ".join(["auto", *PROFILE_BY_KEY])
        raise PackValidationError(f"Unknown category {category!r}; allowed: {allowed}")
    if key == "auto":
        key = infer_category(goal)
    return PROFILE_BY_KEY[key]


def context_prompt_for(profile: ScenarioProfile) -> str:
    return "请按场景提示补充关键限制；不适用的项目可直接回车。"


def context_questions_for(
    profile: ScenarioProfile,
) -> tuple[tuple[str, str], ...]:
    return CONTEXT_QUESTIONS[profile.key]


def goal_without_category_prefix(goal: str, profile: ScenarioProfile) -> str:
    display = goal.strip()
    prefix = profile.name_zh
    separators = "：:-—–"
    while display.casefold().startswith(prefix.casefold()):
        remainder = display[len(prefix) :].lstrip()
        if remainder and remainder[0] in separators:
            remainder = remainder[1:].lstrip()
        if not remainder or remainder == display:
            break
        display = remainder
    return display


def _clean_text(value: str, field: str, maximum: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise PackValidationError(f"{field} must be non-empty")
    if len(cleaned) > maximum:
        raise PackValidationError(f"{field} exceeds {maximum} characters")
    return cleaned


def _clean_criteria(criteria: Iterable[str] | None) -> list[str]:
    if criteria is None:
        return []
    cleaned: list[str] = []
    for index, item in enumerate(criteria):
        cleaned.append(_clean_text(item, f"criteria[{index}]", 300))
    if len(cleaned) > 12:
        raise PackValidationError("criteria may contain at most 12 items")
    return cleaned


def build_pack_from_goal(
    goal: str,
    *,
    category: str = "auto",
    context: str = "",
    criteria: Iterable[str] | None = None,
) -> tuple[dict[str, Any], ScenarioProfile]:
    cleaned_goal = _clean_text(goal, "goal", 4000)
    cleaned_context = context.strip()
    if len(cleaned_context) > 4000:
        raise PackValidationError("context exceeds 4000 characters")
    profile = resolve_category(category, cleaned_goal)
    display_goal = goal_without_category_prefix(cleaned_goal, profile)
    user_criteria = _clean_criteria(criteria)
    selected_criteria = user_criteria or list(profile.criteria)
    digest = sha256_text(f"{profile.key}\n{cleaned_goal}\n{cleaned_context}")[:10]
    slug = f"goal-{digest}"
    pack_id = f"PACK-LOCAL-{slug}"
    mission_id = f"MISSION-LOCAL-{slug}"

    goal_lines = [
        f"场景：{profile.name_zh}",
        f"用户目标：{cleaned_goal}",
    ]
    if cleaned_context:
        goal_lines.append(f"补充背景：{cleaned_context}")
    criteria_lines = [
        "研究框架（这是待用真实来源填充的框架，不是候选项结论）：",
        *[f"- {item}" for item in selected_criteria],
    ]

    pack = {
        "schema_version": "research-os-mvp-pack/0.1",
        "pack_id": pack_id,
        "version": "0.1.0",
        "status": "Draft",
        "pack_type": "Tool",
        "scope": mission_id,
        "foundation_version": "1.0.0-rc.1",
        "constitution_version": "0.1.0-draft",
        "supersedes": "none",
        "permissions": {
            "network": False,
            "subprocess": False,
            "external_writes": False,
        },
        "mission": {
            "mission_id": mission_id,
            "title": f"{profile.name_zh}：{display_goal[:120]}",
            "success_criteria": [
                "目标、背景和关键约束已形成可追溯 Evidence",
                "评估维度已明确且未被误当作事实结论",
                "研究准备报告引用当前 Evidence 及其内容 Hash",
                "真实资料、测试数据和未知项的缺口已明确",
                "三个 Task 都经过显式人工批准",
            ],
            "exit_conditions": [
                "任一完整性检查失败",
                "缺失人工批准",
                "发现目标或范围需要重新定义",
            ],
            "tasks": [
                {
                    "task_id": "TASK-LOCAL-01-capture-goal",
                    "name": "记录目标、背景与约束",
                    "operation": "record_evidence",
                    "requires_approval": True,
                    "input": {
                        "content": "\n".join(goal_lines),
                        "source": "human://natural-language-request",
                        "method": "保留用户自然语言输入并应用本地场景分类",
                        "limitations": (
                            "用户输入可能省略候选项、预算、时间或成功标准；"
                            "需在批准前人工核对。"
                        ),
                    },
                },
                {
                    "task_id": "TASK-LOCAL-02-record-evaluation-frame",
                    "name": "记录评估框架与证据缺口",
                    "operation": "record_evidence",
                    "requires_approval": True,
                    "input": {
                        "content": "\n".join(criteria_lines),
                        "source": f"template://research-os-mvp/{profile.key}",
                        "method": "使用本地确定性场景模板生成评估维度",
                        "limitations": (
                            "该框架不包含对任何候选项的真实测量或外部来源；"
                            "实际决策前需补充可核验证据。"
                        ),
                    },
                },
                {
                    "task_id": "TASK-LOCAL-03-compose-report",
                    "name": "生成研究准备报告（非选型结论）",
                    "operation": "compose_report",
                    "requires_approval": True,
                    "input": {
                        "title": f"{profile.name_zh} Research Preparation Report"
                    },
                },
            ],
        },
    }
    validate_pack_data(pack)
    return pack, profile


def default_pack_path(workspace: Path | str, pack: dict[str, Any]) -> Path:
    return Path(workspace) / "packs" / f"{pack['pack_id']}.json"


def create_pack_from_goal(
    goal: str,
    *,
    category: str = "auto",
    context: str = "",
    criteria: Iterable[str] | None = None,
    workspace: Path | str = Path("workspace"),
    output: Path | str | None = None,
) -> GeneratedPack:
    pack, profile = build_pack_from_goal(
        goal,
        category=category,
        context=context,
        criteria=criteria,
    )
    path = Path(output) if output is not None else default_pack_path(workspace, pack)
    if path.is_symlink():
        raise PackValidationError("Generated Pack path must not be a symlink")
    expected_hash = sha256_bytes(canonical_json_bytes(pack))
    if path.exists():
        existing = load_pack(path)
        if existing.canonical_sha256 != expected_hash:
            raise PackValidationError(
                f"Generated Pack path already contains different content: {path}"
            )
        return GeneratedPack(
            path=path.resolve(),
            data=existing.data,
            category=profile.key,
            category_name=profile.name_zh,
            canonical_sha256=existing.canonical_sha256,
            reused=True,
        )

    write_json_atomic(path, pack)
    loaded = load_pack(path)
    return GeneratedPack(
        path=path.resolve(),
        data=loaded.data,
        category=profile.key,
        category_name=profile.name_zh,
        canonical_sha256=loaded.canonical_sha256,
        reused=False,
    )
