import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from config import APP_NAME, APP_VERSION
from scripts.build_docs import build, render_documentation

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.html = render_documentation("test-revision")

    def test_documentation_has_project_heading(self):
        self.assertIn(f"<h1>{APP_NAME}</h1>", self.html)

    def test_documentation_has_configured_version(self):
        self.assertIn(f"<strong>{APP_VERSION}</strong>", self.html)

    def test_documentation_identifies_source_revision(self):
        self.assertIn("<code>test-revision</code>", self.html)

    def test_documentation_identifies_utf8(self):
        self.assertIn('<meta charset="utf-8">', self.html)

    def test_documentation_includes_public_entry_point(self):
        self.assertIn("<h2>main.py</h2>", self.html)
        self.assertIn("<code>main(", self.html)

    def test_documentation_includes_database_signature(self):
        self.assertIn("<code>get_status() -&gt; str</code>", self.html)

    def test_documentation_includes_notification_signature(self):
        self.assertIn("<code>send_notification() -&gt; str</code>", self.html)

    def test_documentation_includes_report_signature(self):
        self.assertIn("<code>create_report() -&gt; str</code>", self.html)

    def test_documentation_excludes_imported_functions_from_main(self):
        main_section = self.html.split("<h2>main.py</h2>", 1)[1].split("</section>", 1)[0]
        self.assertNotIn("get_status(", main_section)

    def test_documentation_escapes_revision(self):
        html = render_documentation("r&d <draft>")
        self.assertIn("<code>r&amp;d &lt;draft&gt;</code>", html)

    def test_build_creates_nested_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "docs"
            self.assertEqual(build(output, "new"), output / "index.html")
            self.assertTrue((output / "index.html").is_file())

    def test_build_overwrites_documentation_for_new_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build(output, "old-revision")
            html = build(output, "new-revision").read_text(encoding="utf-8")
        self.assertIn("<code>new-revision</code>", html)
        self.assertNotIn("old-revision", html)

    def test_build_is_repeatable_for_same_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = build(output, "same-revision").read_bytes()
            second = build(output, "same-revision").read_bytes()
        self.assertEqual(first, second)

    def test_builder_cli_reads_github_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            subprocess.run(
                [sys.executable, "-m", "scripts.build_docs", "--output", str(output)],
                cwd=ROOT, env={**os.environ, "GITHUB_SHA": "ci-sha"},
                capture_output=True, text=True, check=True,
            )
            html = (output / "index.html").read_text(encoding="utf-8")
        self.assertIn("<code>ci-sha</code>", html)
