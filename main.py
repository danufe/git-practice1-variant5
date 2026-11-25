# Application for generating a random word based on user input
"""Консольный генератор русских слов из онлайн-словаря."""

import json
import random
import sys
from hashlib import sha256
from http.client import HTTPException
from math import factorial
from urllib.parse import urlencode
from urllib.request import urlopen

__version__ = "1.0.1"

DICTIONARY_URL = "https://datasets-server.huggingface.co/rows"
DICTIONARY = "KvaytG/en-ru-statistical-dict-20m-corpus"
ROW_COUNT = 56_624
PROMPT = "Введите целое число от 0 до 100."


def word_index(number: int) -> int:
    """Вычисляет номер строки онлайн-словаря."""
    if not 0 <= number <= 100:
        raise ValueError(PROMPT)

    product = number * random.randint(1, 5)
    result = factorial(product) + random.randint(0, 100)
    digest = sha256(str(result).encode("utf-8")).digest()
    return int.from_bytes(digest, "big") % ROW_COUNT


def fetch_word(index: int) -> str:
    """Запрашивает одну строку словаря и возвращает русское слово."""
    query = urlencode(
        {
            "dataset": DICTIONARY,
            "config": "default",
            "split": "train",
            "offset": index,
            "length": 1,
        }
    )
    with urlopen(f"{DICTIONARY_URL}?{query}", timeout=20) as response:
        data = json.load(response)

    try:
        word = data["rows"][0]["row"]["russian_word"]
    except (IndexError, KeyError, TypeError) as error:
        raise ValueError("В ответе словаря отсутствует слово.") from error

    if not isinstance(word, str) or len(word.split()) != 1:
        raise ValueError("В ответе словаря ожидалось одно слово.")
    return word.strip()

def format_word(word: str, uppercase: bool = False) -> str:
    """Форматирует слово в зависимости от выбранного режима."""
    if uppercase:
        return word.upper()
    return word
    
def main() -> int:
    if "--version" in sys.argv:
        print(__version__)
        return 0
    """Читает число и выводит слово, выбранное по результату расчёта."""
    print(PROMPT, file=sys.stderr)
    try:
        index = word_index(int(input()))
    except (ValueError, EOFError):
        print(f"Ошибка. {PROMPT}", file=sys.stderr)
        return 1

    try:
        word = fetch_word(index)
    except (OSError, HTTPException, ValueError):
        print("Ошибка. Не удалось получить слово из онлайн-словаря.", file=sys.stderr)
        return 1

    print(format_word(word, "--uppercase" in sys.argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
