from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from research_os_mvp.errors import MVPError
from research_os_mvp.integrity import sha256_file

MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
MAX_PDF_FILE_BYTES = 25 * 1024 * 1024
MAX_DIRECTORY_BYTES = 10 * 1024 * 1024
MAX_DIRECTORY_FILES = 200
MAX_EXTRACTED_CHARS = 500_000
MAX_PDF_PAGES = 100

TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".css", ".csv", ".go", ".h", ".hpp",
    ".htm", ".html", ".ini", ".java", ".js", ".json", ".jsx", ".log",
    ".md", ".ps1", ".py", ".rs", ".sh", ".sql", ".toml", ".ts", ".tsx",
    ".txt", ".xml", ".yaml", ".yml",
}
SKIP_DIRECTORIES = {
    ".git", ".hg", ".svn", ".venv", "__pycache__", "dist", "build",
    "node_modules", "target", "workspace",
}


class SourceImportError(MVPError):
    """Raised when a local source cannot be safely imported."""


@dataclass(frozen=True)
class ImportedSource:
    content: str
    source: str
    method: str
    limitations: str
    file_count: int


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style", "noscript", "svg"}:
            self._ignored_depth = max(0, self._ignored_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._ignored_depth == 0:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self._parts.append(cleaned)

    def text(self) -> str:
        return "\n".join(self._parts)


def normalize_dropped_path(value: str) -> Path:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    if not cleaned:
        raise SourceImportError("资料路径为空")
    path = Path(cleaned).expanduser()
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise SourceImportError(f"资料路径不存在：{path}") from exc
    if path.is_symlink() or resolved.is_symlink():
        raise SourceImportError("资料入口不得是符号链接")
    return resolved


def _decode_text(raw: bytes, path: Path) -> str:
    if b"\x00" in raw[:8192]:
        raise SourceImportError(f"检测到二进制内容：{path}")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SourceImportError(f"文本编码不是 UTF-8 或 GB18030：{path}")


def _extract_text_file(path: Path) -> str:
    size = path.stat().st_size
    if size > MAX_TEXT_FILE_BYTES:
        raise SourceImportError(f"文本文件超过 2 MiB 上限：{path}")
    text = _decode_text(path.read_bytes(), path)
    if path.suffix.casefold() in {".html", ".htm"}:
        parser = _HTMLTextExtractor()
        parser.feed(text)
        text = parser.text()
    return text


def _extract_pdf(path: Path) -> tuple[str, int]:
    if path.stat().st_size > MAX_PDF_FILE_BYTES:
        raise SourceImportError(f"PDF 超过 25 MiB 上限：{path}")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SourceImportError("当前 Python 缺少 pypdf，PDF 读取组件尚未就绪") from exc
    try:
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise SourceImportError("暂不读取加密 PDF")
        page_count = len(reader.pages)
        if page_count > MAX_PDF_PAGES:
            raise SourceImportError(f"PDF 超过 {MAX_PDF_PAGES} 页上限")
        parts: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            extracted = page.extract_text() or ""
            parts.append(f"\n--- PDF 第 {index} 页 ---\n{extracted.strip()}")
    except SourceImportError:
        raise
    except Exception as exc:
        raise SourceImportError(f"PDF 解析失败：{exc}") from exc
    return "\n".join(parts).strip(), page_count


def _file_header(path: Path) -> str:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    return (
        f"文件名：{path.name}\n"
        f"文件大小：{path.stat().st_size} bytes\n"
        f"文件修改时间（UTC）：{modified}\n"
        f"原始文件 SHA-256：{sha256_file(path)}"
    )


def _import_file(path: Path) -> ImportedSource:
    suffix = path.suffix.casefold()
    if suffix == ".pdf":
        extracted, page_count = _extract_pdf(path)
        method = f"只读解析本地 PDF 的 {page_count} 页文本，并记录原文件 Hash"
        limitation = "PDF 文本提取不等于版面或图像识别；表格、公式、扫描页可能缺失。"
    elif suffix in TEXT_EXTENSIONS:
        extracted = _extract_text_file(path)
        method = "只读提取本地文本/网页/代码文件，并记录原文件 Hash"
        limitation = "仅保存文本内容；渲染效果、外部资源、可执行行为和版本历史未采集。"
    else:
        raise SourceImportError(f"暂不支持该文件类型：{suffix or '无扩展名'}")
    if not extracted.strip():
        raise SourceImportError("资料没有提取到可用文本")
    truncated = len(extracted) > MAX_EXTRACTED_CHARS
    content = f"{_file_header(path)}\n\n提取内容：\n{extracted[:MAX_EXTRACTED_CHARS]}"
    if truncated:
        limitation += f" 提取文本已截断到 {MAX_EXTRACTED_CHARS} 字符。"
    return ImportedSource(
        content=content,
        source=f"file://{path}",
        method=method,
        limitations=limitation,
        file_count=1,
    )


def _directory_candidates(root: Path) -> tuple[list[Path], int]:
    candidates: list[Path] = []
    skipped = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        if path.is_symlink():
            skipped += 1
            continue
        if path.is_file():
            if path.suffix.casefold() in TEXT_EXTENSIONS:
                candidates.append(path)
            else:
                skipped += 1
    return candidates, skipped


def _import_directory(root: Path) -> ImportedSource:
    candidates, skipped = _directory_candidates(root)
    sections: list[str] = []
    total_bytes = 0
    included = 0
    truncated = False
    for path in candidates:
        size = path.stat().st_size
        if size > MAX_TEXT_FILE_BYTES:
            skipped += 1
            continue
        if included >= MAX_DIRECTORY_FILES or total_bytes + size > MAX_DIRECTORY_BYTES:
            truncated = True
            break
        try:
            text = _extract_text_file(path)
        except SourceImportError:
            skipped += 1
            continue
        relative = path.relative_to(root).as_posix()
        sections.append(
            f"\n## {relative}\nSHA-256：{sha256_file(path)}\n\n{text[:100_000]}"
        )
        total_bytes += size
        included += 1
        if sum(len(section) for section in sections) > MAX_EXTRACTED_CHARS:
            truncated = True
            break
    if not sections:
        raise SourceImportError("目录中没有可导入的文本、网页或代码文件")
    joined = "".join(sections)[:MAX_EXTRACTED_CHARS]
    limitations = (
        f"只读导入 {included} 个文本文件；跳过 {skipped} 个不支持、过大或符号链接文件。"
        "未执行任何代码，也未采集 Git 历史。"
    )
    if truncated:
        limitations += " 已达到目录文件、字节或文本上限，剩余内容未导入。"
    content = (
        f"代码/资料目录：{root}\n"
        f"已导入文件：{included}\n"
        f"原始字节合计：{total_bytes}\n"
        f"\n提取内容：{joined}"
    )
    return ImportedSource(
        content=content,
        source=f"directory://{root}",
        method="只读遍历允许的文本/网页/代码文件，逐文件记录 SHA-256",
        limitations=limitations,
        file_count=included,
    )


def import_local_source(value: str | Path) -> ImportedSource:
    path = normalize_dropped_path(str(value))
    if path.is_file():
        return _import_file(path)
    if path.is_dir():
        return _import_directory(path)
    raise SourceImportError("资料路径既不是普通文件也不是目录")
