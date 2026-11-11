"""Вывести случайное слово о текущей погоде выбранного города."""

import json
import random
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

API_URL = "https://api.open-meteo.com/v1/forecast"
CITIES = {
    1: ("Москва", 55.75, 37.62),
    2: ("Санкт-Петербург", 59.94, 30.31),
    3: ("Казань", 55.79, 49.12),
}
WORDS_BY_WEATHER = (
    ({0, 1}, ("солнце", "луч", "свет")),
    ({2, 3}, ("облако", "небо", "тень")),
    ({45, 48}, ("туман", "дымка", "мгла")),
    ({51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}, ("дождь", "капля", "ливень")),
    ({71, 73, 75, 77, 85, 86}, ("снег", "иней", "снежинка")),
    ({95, 96, 99}, ("гроза", "гром", "молния")),
)


def parse_city(value: str) -> int:
    """Вернуть номер города по введённому числу."""
    number = int(value)
    if number not in CITIES:
        raise ValueError("Номер города вне диапазона")
    return number


def fetch_weather_code(city: int) -> int:
    """Получить текущий код погоды города из API Open-Meteo."""
    _, latitude, longitude = CITIES[city]
    params = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "weather_code",
    })
    with urlopen(f"{API_URL}?{params}", timeout=5) as response:
        payload = json.load(response)
    code = payload["current"]["weather_code"]
    if type(code) is not int:
        raise ValueError("Код погоды должен быть целым числом")
    return code


def word_for_weather(code: int) -> str:
    """Выбрать случайное слово из группы с подходящим кодом погоды."""
    for codes, words in WORDS_BY_WEATHER:
        if code in codes:
            return random.choice(words)
    raise ValueError("Неизвестный код погоды")


def main() -> int:
    """Прочитать номер города и напечатать слово о текущей погоде."""
    print("Введите 1 для Москвы, 2 для Санкт-Петербурга или 3 для Казани.", file=sys.stderr)
    try:
        city = parse_city(input())
    except (ValueError, EOFError):
        print("Введите целое число от 1 до 3.", file=sys.stderr)
        return 2

    try:
        print(word_for_weather(fetch_weather_code(city)))
    except (OSError, ValueError, KeyError, TypeError):
        print("Не удалось получить погоду.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
