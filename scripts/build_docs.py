"""Собрать HTML-документацию из текущего кода приложения."""

import os
from html import escape
from inspect import getdoc, signature
from pathlib import Path

import main
from config import APP_NAME, APP_VERSION


if __name__ == "__main__":
    revision = os.environ.get("GITHUB_SHA", "local")
    groups = "".join(
        f"<tr><td>{index}</td><td>{escape(word)}</td></tr>"
        for index, word in enumerate(main.WORDS)
    )
    functions = "".join(
        f"<dt><code>{escape(function.__name__ + str(signature(function)))}</code></dt>"
        f"<dd>{escape(getdoc(function) or '')}</dd>"
        for function in (main.choose_word, main.main)
    )
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(APP_NAME)}</title>
  <style>
    body {{ max-width: 850px; margin: 40px auto; padding: 0 24px; font: 17px/1.6 sans-serif; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ padding: 8px 12px; border: 1px solid #ccc; text-align: left; }}
    code {{ background: #f2f2f2; padding: 2px 5px; }}
  </style>
</head>
<body>
  <h1>{escape(APP_NAME)}</h1>
  <p>Версия <strong>{escape(APP_VERSION)}</strong></p>
  <p>Ревизия <code>{escape(revision)}</code></p>
  <p>{escape(getdoc(main) or '')}</p>
  <h2>Запуск</h2>
  <p><code>python main.py</code></p>
  <p>Введите целое число от 0 до 100.</p>
  <table><tr><th>Индекс</th><th>Слово</th></tr>{groups}</table>
  <h2>Функции</h2>
  <dl>{functions}</dl>
</body>
</html>
"""
    output = Path("build/docs/index.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Built {output.as_posix()} for version {APP_VERSION} at revision {revision}")
