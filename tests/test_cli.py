import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from config import APP_NAME, APP_VERSION

ROOT = Path(__file__).resolve().parents[1]


class StatusTests(unittest.TestCase):
    def test_status_uses_configured_name(self):
        with patch.object(main, "APP_NAME", "Example"):
            self.assertEqual(main.get_application_status()["name"], "Example")

    def test_status_uses_configured_version(self):
        with patch.object(main, "APP_VERSION", "9.8.7"):
            self.assertEqual(main.get_application_status()["version"], "9.8.7")

    def test_status_uses_database_status_provider(self):
        with patch.object(main, "get_status", return_value="test status") as provider:
            self.assertEqual(main.get_application_status()["database_status"], "test status")
        provider.assert_called_once_with()

    def test_status_json_preserves_unicode(self):
        output = io.StringIO()
        with patch.object(main, "get_status", return_value="Подключение не настроено"):
            with redirect_stdout(output):
                main.main(["--status-json"])
        self.assertIn("Подключение не настроено", output.getvalue())

    def test_version_mode_does_not_call_database_provider(self):
        with patch.object(main, "get_status") as provider:
            with redirect_stdout(io.StringIO()):
                main.main(["--version"])
        provider.assert_not_called()


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "main.py", *args], cwd=ROOT, capture_output=True, text=True,
        )

    def test_status_json_prints_one_document(self):
        result = self.run_cli("--status-json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(result.stdout),
            {
                "name": APP_NAME,
                "version": APP_VERSION,
                "database_status": "PostgreSQL connection is not configured",
            },
        )

    def test_version_prints_only_the_current_version(self):
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, APP_VERSION + "\n")

    def test_help_lists_supported_modes(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("--status-json", result.stdout)
        self.assertIn("--version", result.stdout)

    def test_unknown_option_is_rejected(self):
        result = self.run_cli("--unknown")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--unknown", result.stderr)

    def test_unexpected_positional_argument_is_rejected(self):
        result = self.run_cli("extra")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("extra", result.stderr)

    def test_option_abbreviation_is_rejected(self):
        result = self.run_cli("--status")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_status_and_version_modes_are_mutually_exclusive(self):
        for args in (("--version", "--status-json"), ("--status-json", "--version")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
