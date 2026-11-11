"""Консольный запуск учебного приложения."""

import argparse
import json
import sys
from collections.abc import Sequence

from config import APP_NAME, APP_VERSION
from database import get_status


def get_application_status() -> dict[str, str]:
    """Собрать название, версию и статус настройки PostgreSQL."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "database_status": get_status(),
    }


def main(argv: Sequence[str] = ()) -> None:
    """Запустить консольное приложение.

    --status-json выводит название, версию и статус настройки PostgreSQL в JSON.
    --version выводит текущую версию. Без аргументов выводится обычный текст.
    """
    parser = argparse.ArgumentParser(description=APP_NAME, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--status-json", action="store_true", help="print application status as JSON")
    modes.add_argument("--version", action="store_true", help="print the application version")
    args = parser.parse_args(argv)

    if args.version:
        print(APP_VERSION)
        return

    if args.status_json:
        print(json.dumps(get_application_status(), ensure_ascii=False))
        return

    print("Application:", APP_NAME)
    print(get_status())
    print("Program updated by person3")
    print("Changes from person3")


if __name__ == "__main__":
    main(sys.argv[1:])
