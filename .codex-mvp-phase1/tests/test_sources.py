from __future__ import annotations

import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from research_os_mvp.sources import SourceImportError, import_local_source


class SourceImportTests(unittest.TestCase):
    def test_text_and_html_files_are_imported_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            text_path = root / "资料.txt"
            text_path.write_text("温度范围：0-50°C", encoding="utf-8")
            imported = import_local_source(f'"{text_path}"')
            self.assertIn("温度范围", imported.content)
            self.assertIn("原始文件 SHA-256", imported.content)
            self.assertTrue(imported.source.startswith("file://"))

            html_path = root / "page.html"
            html_path.write_text(
                "<html><style>hidden</style><body>可见正文<script>bad()</script></body></html>",
                encoding="utf-8",
            )
            html = import_local_source(html_path)
            self.assertIn("可见正文", html.content)
            self.assertNotIn("bad()", html.content)
            self.assertNotIn("hidden", html.content)

    def test_code_directory_skips_binary_and_dependency_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('ok')", encoding="utf-8")
            (root / "image.bin").write_bytes(b"\x00\x01")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "skip.js").write_text("skip", encoding="utf-8")
            imported = import_local_source(root)
            self.assertEqual(imported.file_count, 1)
            self.assertIn("src/app.py", imported.content)
            self.assertNotIn("skip.js", imported.content)
            self.assertIn("未执行任何代码", imported.limitations)

    def test_unknown_file_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.exe"
            path.write_bytes(b"MZ")
            with self.assertRaisesRegex(SourceImportError, "文件类型"):
                import_local_source(path)

    def test_empty_missing_binary_and_empty_sources_are_rejected(self) -> None:
        with self.assertRaisesRegex(SourceImportError, "路径为空"):
            import_local_source("   ")
        with self.assertRaisesRegex(SourceImportError, "路径不存在"):
            import_local_source("definitely-missing-source.txt")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "binary.txt"
            binary.write_bytes(b"prefix\x00payload")
            with self.assertRaisesRegex(SourceImportError, "二进制"):
                import_local_source(binary)

            empty = root / "empty.txt"
            empty.write_text("   ", encoding="utf-8")
            with self.assertRaisesRegex(SourceImportError, "没有提取到"):
                import_local_source(empty)

    def test_gb18030_text_and_extraction_limit_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            encoded = root / "legacy.txt"
            encoded.write_bytes("旧编码资料".encode("gb18030"))
            self.assertIn("旧编码资料", import_local_source(encoded).content)

            long_text = root / "long.txt"
            long_text.write_text("0123456789", encoding="utf-8")
            with patch("research_os_mvp.sources.MAX_EXTRACTED_CHARS", 5):
                imported = import_local_source(long_text)
            self.assertIn("01234", imported.content)
            self.assertIn("已截断到 5 字符", imported.limitations)

    def test_text_file_size_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.txt"
            path.write_text("1234", encoding="utf-8")
            with patch(
                "research_os_mvp.sources.MAX_TEXT_FILE_BYTES", 3
            ), self.assertRaisesRegex(SourceImportError, "2 MiB 上限"):
                import_local_source(path)

    def test_directory_skips_bad_files_and_reports_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.txt").write_text("ok", encoding="utf-8")
            (root / "b.txt").write_text("oversized", encoding="utf-8")
            with patch("research_os_mvp.sources.MAX_TEXT_FILE_BYTES", 4):
                imported = import_local_source(root)
            self.assertEqual(imported.file_count, 1)
            self.assertIn("跳过 1 个", imported.limitations)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.txt").write_text("first", encoding="utf-8")
            (root / "b.txt").write_text("second", encoding="utf-8")
            with patch("research_os_mvp.sources.MAX_DIRECTORY_FILES", 1):
                imported = import_local_source(root)
            self.assertEqual(imported.file_count, 1)
            self.assertIn("剩余内容未导入", imported.limitations)

    def test_directory_rejects_when_every_candidate_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "binary.txt").write_bytes(b"\x00\x01")
            (root / "unsupported.exe").write_bytes(b"MZ")
            with self.assertRaisesRegex(SourceImportError, "没有可导入"):
                import_local_source(root)

    def test_pdf_optional_dependency_and_size_limit_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.pdf"
            path.write_bytes(b"%PDF-fake")

            with patch(
                "research_os_mvp.sources.MAX_PDF_FILE_BYTES", 1
            ), self.assertRaisesRegex(SourceImportError, "25 MiB 上限"):
                import_local_source(path)

            with patch.dict(
                "sys.modules", {"pypdf": None}
            ), self.assertRaisesRegex(SourceImportError, "缺少 pypdf"):
                import_local_source(path)

    def test_pdf_success_encryption_page_limit_and_parse_failure(self) -> None:
        class Page:
            def __init__(self, text: str | None) -> None:
                self._text = text

            def extract_text(self) -> str | None:
                return self._text

        def module_for(reader: object) -> types.ModuleType:
            module = types.ModuleType("pypdf")
            module.PdfReader = lambda *_args, **_kwargs: reader
            return module

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.pdf"
            path.write_bytes(b"%PDF-fake")

            reader = types.SimpleNamespace(
                is_encrypted=False,
                pages=[Page("第一页"), Page(None)],
            )
            with patch.dict("sys.modules", {"pypdf": module_for(reader)}):
                imported = import_local_source(path)
            self.assertIn("PDF 第 1 页", imported.content)
            self.assertIn("第一页", imported.content)
            self.assertIn("2 页文本", imported.method)

            encrypted = types.SimpleNamespace(is_encrypted=True, pages=[])
            with patch.dict(
                "sys.modules", {"pypdf": module_for(encrypted)}
            ), self.assertRaisesRegex(SourceImportError, "加密 PDF"):
                import_local_source(path)

            too_many = types.SimpleNamespace(
                is_encrypted=False,
                pages=[Page("one"), Page("two")],
            )
            with patch("research_os_mvp.sources.MAX_PDF_PAGES", 1), patch.dict(
                "sys.modules", {"pypdf": module_for(too_many)}
            ), self.assertRaisesRegex(SourceImportError, "超过 1 页"):
                import_local_source(path)

            failing_module = types.ModuleType("pypdf")

            def fail_reader(*_args: object, **_kwargs: object) -> object:
                raise ValueError("broken pdf")

            failing_module.PdfReader = fail_reader
            with patch.dict(
                "sys.modules", {"pypdf": failing_module}
            ), self.assertRaisesRegex(SourceImportError, "PDF 解析失败"):
                import_local_source(path)


if __name__ == "__main__":
    unittest.main()
