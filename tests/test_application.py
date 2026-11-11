import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from config import APP_NAME, APP_VERSION
from database import get_status
from notifications import send_notification
from reports import create_report

ROOT = Path(__file__).resolve().parents[1]


class ApplicationTests(unittest.TestCase):
    def test_configuration_provides_application_name(self):
        self.assertEqual(APP_NAME, "PostgreSQL Git Practice")

    def test_version_uses_major_minor_patch(self):
        self.assertRegex(APP_VERSION, r"^\d+\.\d+\.\d+$")

    def test_database_status_reports_missing_configuration(self):
        self.assertEqual(get_status(), "PostgreSQL connection is not configured")

    def test_notification_returns_success_message(self):
        self.assertEqual(send_notification(), "Notification sent successfully")

    def test_report_returns_creation_message(self):
        self.assertEqual(create_report(), "Report created")

    def test_main_uses_name_from_configuration(self):
        output = io.StringIO()
        with patch.object(main, "APP_NAME", "Example"), redirect_stdout(output):
            main.main()
        self.assertEqual(output.getvalue().splitlines()[0], "Application: Example")

    def test_main_prints_status_from_database_provider(self):
        output = io.StringIO()
        with patch.object(main, "get_status", return_value="test status") as provider:
            with redirect_stdout(output):
                main.main()
        provider.assert_called_once_with()
        self.assertEqual(output.getvalue().splitlines()[1], "test status")


class StartupTests(unittest.TestCase):
    def test_entry_point_prints_legacy_output(self):
        result = subprocess.run(
            [sys.executable, "main.py"], cwd=ROOT, capture_output=True, text=True,
            check=True,
        )
        self.assertEqual(
            result.stdout.splitlines(),
            [
                f"Application: {APP_NAME}",
                "PostgreSQL connection is not configured",
                "Program updated by person3",
                "Changes from person3",
            ],
        )

    def test_entry_point_writes_no_stderr_on_success(self):
        result = subprocess.run(
            [sys.executable, "main.py"], cwd=ROOT, capture_output=True, text=True,
            check=True,
        )
        self.assertEqual(result.stderr, "")

    def test_import_main_has_no_console_side_effect(self):
        result = subprocess.run(
            [sys.executable, "-c", "import main"], cwd=ROOT, capture_output=True,
            text=True, check=True,
        )
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
