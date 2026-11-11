"""Проверить запуск приложения и вывод статуса в JSON."""

import json
import subprocess
import sys
from pathlib import Path

from config import APP_NAME, APP_VERSION
from database import get_status


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "main.py", "--status-json"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    expected = {
        "name": APP_NAME,
        "version": APP_VERSION,
        "database_status": get_status(),
    }
    if json.loads(result.stdout) != expected:
        raise SystemExit("Unexpected application status in JSON output")
    print("Application startup check passed")
