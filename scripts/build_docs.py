"""Собрать HTML-документацию из публичных функций приложения."""

import argparse
import inspect
import os
from html import escape
from pathlib import Path

import database
import main
import notifications
import reports
from config import APP_NAME, APP_VERSION

MODULES = (main, database, notifications, reports)


def render_documentation(revision: str) -> str:
    """Вернуть HTML со сведениями о версии и описаниями функций."""
    sections = []
    for module in MODULES:
        entries = []
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_") or function.__module__ != module.__name__:
                continue
            signature = escape(f"{name}{inspect.signature(function)}")
            description = escape(inspect.getdoc(function) or "")
            entries.append(f"<dt><code>{signature}</code></dt><dd>{description}</dd>")
        sections.append(
            f"<section><h2>{module.__name__}.py</h2><dl>{''.join(entries)}</dl></section>"
        )

    return f"""<!doctype html>
<html lang="ru">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Документация {escape(APP_NAME)}</title>
<style>
  body {{ font: 1rem/1.6 system-ui, sans-serif; color: #17212b; margin: 2rem auto;
          max-width: 52rem; padding: 0 1rem; }}
  section {{ border-top: 1px solid #d6dce2; }}
  dt {{ font-weight: 600; }}
  dd {{ margin: 0 0 1rem; white-space: pre-line; }}
  code {{ overflow-wrap: anywhere; }}
</style>
<main>
  <h1>{escape(APP_NAME)}</h1>
  <p>Версия <strong>{escape(APP_VERSION)}</strong></p>
  <p>Ревизия <code>{escape(revision)}</code></p>
  {''.join(sections)}
</main>
</html>
"""


def build(output_dir: Path, revision: str) -> Path:
    """Записать документацию в index.html и вернуть путь к файлу."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"
    output_file.write_text(render_documentation(revision), encoding="utf-8")
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/docs"))
    args = parser.parse_args()
    revision = os.environ.get("GITHUB_SHA", "local")
    path = build(args.output, revision)
    print(f"Built {path} for version {APP_VERSION} at revision {revision}")
