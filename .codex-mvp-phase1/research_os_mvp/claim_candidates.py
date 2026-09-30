from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Sequence
from typing import Any

from research_os_mvp.errors import RunStateError

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]

MAX_CANDIDATES = 1_000
CLAIM_SECTION_MODES = {
    "逐条证据清单": "list",
    "推荐方案及适用条件": "sentences",
}
KIND_CHOICES = {
    "1": ("verifiable_fact", "可核验事实"),
    "2": ("interpretation", "解释/判断"),
    "3": ("recommendation", "建议"),
    "4": ("assumption", "假设"),
}

_HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
_LIST_PATTERN = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+(.+?)\s*$")
_SENTENCE_PATTERN = re.compile(r"[^。！？!?\n]+(?:[。！？!?]+|$)")
_BOLD_LABEL_PATTERN = re.compile(r"^\*\*[^*]+\*\*$")
_FENCE_PATTERN = re.compile(r"^\s{0,3}(?P<marker>\x60{3,}|~{3,})(?P<tail>.*)$")
_SOURCE_ASSERTION_PATTERN = re.compile(
    r"(?:来源|参考(?:资料|文献)?|source)\s*[:：]\s*"
    r"(?!未知(?:\s*/\s*待查证)?(?:\W|$)|待查证(?:\W|$)|未提供(?:\W|$)|用户提供(?:\W|$)|evidence\b)\S+",
    re.IGNORECASE,
)


def _iter_unfenced_lines(draft: str) -> Iterator[str]:
    fence_character: str | None = None
    fence_length = 0
    for raw_line in draft.splitlines():
        fence_match = _FENCE_PATTERN.match(raw_line)
        if fence_match:
            marker = fence_match.group("marker")
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif (
                marker[0] == fence_character
                and len(marker) >= fence_length
                and not fence_match.group("tail").strip()
            ):
                fence_character = None
                fence_length = 0
            continue
        if fence_character is None:
            yield raw_line


def _candidate(section: str, text: str) -> dict[str, Any]:
    return {
        "section": section,
        "text": text,
        "locator": {"kind": "quote", "value": text},
        "kind": None,
        "evidence_ids": [],
        "support": "unsupported",
    }


def extract_claim_candidates(draft: str) -> list[dict[str, Any]]:
    """Split structured AI draft text without inferring kind or trusting citations.

    Comparison tables are omitted because the structured evidence list repeats their
    assertions in reviewable prose. Workflow-only sections (questions, risks,
    experiments, and change conditions) are also not Claim-bearing inputs. Inline
    strings such as ``来源：...`` remain verbatim text and are never parsed as Evidence.
    """

    if not isinstance(draft, str):
        raise TypeError("draft must be a string")
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    section = ""
    mode: str | None = None

    def append(text: str) -> None:
        cleaned = text.strip()
        if not cleaned or cleaned in seen:
            return
        seen.add(cleaned)
        candidates.append(_candidate(section, cleaned))
        if len(candidates) > MAX_CANDIDATES:
            raise RunStateError(f"AI 草稿候选 Claim 超过 {MAX_CANDIDATES} 条")

    for raw_line in _iter_unfenced_lines(draft):
        heading = _HEADING_PATTERN.fullmatch(raw_line)
        if heading is not None:
            section = heading.group(1).strip().strip("#").strip()
            mode = CLAIM_SECTION_MODES.get(section)
            continue
        if mode is None:
            continue
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("|"):
            continue
        listed = _LIST_PATTERN.fullmatch(raw_line)
        if listed is not None:
            text = listed.group(1).strip()
            if not _BOLD_LABEL_PATTERN.fullmatch(text):
                append(text)
            continue
        if mode == "sentences":
            for sentence in _SENTENCE_PATTERN.findall(stripped):
                append(sentence)

    return candidates


def find_ai_draft_policy_violations(draft: str, *, max_violations: int = 100) -> list[str]:
    """Return apparent source assertions that need human classification before approval."""
    if not isinstance(draft, str):
        raise TypeError("draft must be a string")
    if max_violations < 1:
        raise ValueError("max_violations must be at least 1")

    violations: list[str] = []
    seen: set[str] = set()
    for raw_line in _iter_unfenced_lines(draft):
        line = raw_line.strip()
        if line and line not in seen and _SOURCE_ASSERTION_PATTERN.search(line):
            seen.add(line)
            violations.append(line)
            if len(violations) >= max_violations:
                break
    return violations


def _read_kind(
    candidate: dict[str, Any],
    *,
    index: int,
    total: int,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> str | None:
    output_fn(
        f"\n候选 {index}/{total}｜{candidate['section']}\n"
        f"{candidate['text']}\n"
        "默认支持状态：unsupported；Evidence 引用：[]\n"
        "1 可核验事实｜2 解释/判断｜3 建议｜4 假设"
    )
    while True:
        selected = input_fn("请选择 1/2/3/4；直接回车取消整个 Claim 确认：").strip()
        if not selected:
            return None
        choice = KIND_CHOICES.get(selected)
        if choice is not None:
            return choice[0]
        output_fn("分类无效；必须逐条选择 1、2、3 或 4。")


def classify_claim_candidates(
    candidates: Sequence[dict[str, Any]],
    *,
    input_fn: InputFn,
    output_fn: OutputFn,
) -> list[dict[str, Any]] | None:
    """Collect one human kind per candidate and fail closed on any interruption."""

    if not candidates:
        output_fn("草稿中没有抽取到可确认的候选 Claim。")
        return None
    selected_kinds: list[str] = []
    for index, candidate in enumerate(candidates, start=1):
        kind = _read_kind(
            candidate,
            index=index,
            total=len(candidates),
            input_fn=input_fn,
            output_fn=output_fn,
        )
        if kind is None:
            output_fn("Claim 分类未完成；本次不记录任何 Claim。")
            return None
        selected_kinds.append(kind)

    while True:
        output_fn("\nClaim 分类复核（每条仍为 unsupported，Evidence 引用均为空）：")
        for index, (candidate, kind) in enumerate(
            zip(candidates, selected_kinds, strict=True),
            start=1,
        ):
            label = next(label for value, label in KIND_CHOICES.values() if value == kind)
            output_fn(f"{index}. [{label}] {candidate['text']}")
        action = input_fn(
            "输入候选编号可修改；全部确认后输入 CONFIRM；直接回车取消："
        ).strip()
        if not action:
            output_fn("Claim 分类未最终确认；本次不记录任何 Claim。")
            return None
        if action == "CONFIRM":
            return [
                {
                    "text": candidate["text"],
                    "locator": {
                        "kind": "quote",
                        "value": candidate["text"],
                    },
                    "kind": kind,
                    "evidence_ids": [],
                    "support": "unsupported",
                }
                for candidate, kind in zip(candidates, selected_kinds, strict=True)
            ]
        if action.isdigit() and 1 <= int(action) <= len(candidates):
            edit_index = int(action) - 1
            replacement = _read_kind(
                candidates[edit_index],
                index=edit_index + 1,
                total=len(candidates),
                input_fn=input_fn,
                output_fn=output_fn,
            )
            if replacement is None:
                output_fn("Claim 分类修改未完成；本次不记录任何 Claim。")
                return None
            selected_kinds[edit_index] = replacement
            continue
        output_fn("请输入有效候选编号、精确的 CONFIRM，或直接回车取消。")
