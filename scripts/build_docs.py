"""Собрать HTML-документацию из исходного кода приложения."""

import os
from html import escape
from inspect import getdoc, signature
from pathlib import Path

import main
from config import APP_NAME, APP_VERSION


if __name__ == "__main__":
    revision = os.environ.get("GITHUB_SHA", "local")
    functions = (main.parse_city, main.fetch_weather_code, main.word_for_weather, main.main)
    cities = "".join(
        f"<li>{number} — {escape(city[0])}</li>" for number, city in main.CITIES.items()
    )
    descriptions = "".join(
        f"<dt><code>{escape(function.__name__ + str(signature(function)))}</code></dt>"
        f"<dd>{escape(getdoc(function) or '')}</dd>"
        for function in functions
    )
    html = f"""<!doctype html>
<html lang="ru">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(APP_NAME)}</title>
<main>
  <h1>{escape(APP_NAME)}</h1>
  <p>Версия <strong>{escape(APP_VERSION)}</strong></p>
  <p>Ревизия <code>{escape(revision)}</code></p>
  <p>{escape(getdoc(main) or '')}</p>
  <h2>Города</h2>
  <ul>{cities}</ul>
  <h2>Функции</h2>
  <dl>{descriptions}</dl>
  <p>Данные о погоде предоставляет <a href="https://open-meteo.com/">Open-Meteo</a>.</p>
</main>
</html>
"""
    output = Path("build/docs/index.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Built {output.as_posix()} for version {APP_VERSION} at revision {revision}")
