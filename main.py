"""Случайное слово по числу пользователя и результату вычислений."""

import random
import sys
from hashlib import sha256
from math import factorial

WORDS = (
    "кот", "река", "ветер", "солнце", "книга", "лес", "облако", "море",
    "звезда", "камень", "дорога", "луна", "цветок", "дождь", "огонь", "снег",
)


def choose_word(number: int) -> str:
    """Умножить число на случайный множитель, взять факториал и выбрать слово по SHA-256."""
    if not 0 <= number <= 100:
        raise ValueError("Введите целое число от 0 до 100.")
    product = number * random.randint(1, 5)
    result = factorial(product)
    digest = sha256(str(result).encode("utf-8")).digest()
    index = int.from_bytes(digest, "big") % len(WORDS)
    return WORDS[index]


def main() -> int:
    """Прочитать целое число от 0 до 100 и вывести одно слово."""
    print("Введите целое число от 0 до 100.", file=sys.stderr)
    try:
        number = int(input())
        print(choose_word(number))
    except (ValueError, EOFError):
        print("Ошибка. Введите целое число от 0 до 100.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
