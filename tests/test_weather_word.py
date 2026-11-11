import io
import json
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit

import main


class CityInputTests(unittest.TestCase):
    def test_one_selects_moscow(self):
        self.assertEqual(main.CITIES[main.parse_city("1")][0], "Москва")

    def test_two_selects_saint_petersburg(self):
        self.assertEqual(main.CITIES[main.parse_city("2")][0], "Санкт-Петербург")

    def test_three_with_whitespace_selects_kazan(self):
        self.assertEqual(main.CITIES[main.parse_city(" 3 \t")][0], "Казань")

    def test_non_integer_input_is_rejected(self):
        for value in ("", "abc", "2.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                main.parse_city(value)

    def test_out_of_range_input_is_rejected(self):
        for value in ("0", "4", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                main.parse_city(value)


class WordSelectionTests(unittest.TestCase):
    def assert_weather_group(self, codes, expected_words):
        for code in codes:
            with self.subTest(code=code):
                with patch.object(main.random, "choice", return_value=expected_words[1]) as choice:
                    self.assertEqual(main.word_for_weather(code), expected_words[1])
                choice.assert_called_once_with(expected_words)

    def test_clear_sky_uses_sun_words(self):
        self.assert_weather_group((0, 1), ("солнце", "луч", "свет"))

    def test_clouds_use_cloud_words(self):
        self.assert_weather_group((2, 3), ("облако", "небо", "тень"))

    def test_fog_uses_fog_words(self):
        self.assert_weather_group((45, 48), ("туман", "дымка", "мгла"))

    def test_rain_and_drizzle_use_rain_words(self):
        self.assert_weather_group((51, 57, 61, 67, 80, 82), ("дождь", "капля", "ливень"))

    def test_snow_uses_snow_words(self):
        self.assert_weather_group((71, 77, 85, 86), ("снег", "иней", "снежинка"))

    def test_thunderstorms_use_thunder_words(self):
        self.assert_weather_group((95, 96, 99), ("гроза", "гром", "молния"))

    def test_unknown_weather_code_is_rejected(self):
        with self.assertRaises(ValueError):
            main.word_for_weather(100)


class WeatherApiTests(unittest.TestCase):
    def test_request_uses_city_coordinates_and_timeout(self):
        coordinates = {
            1: ("55.75", "37.62"),
            2: ("59.94", "30.31"),
            3: ("55.79", "49.12"),
        }
        for city, (latitude, longitude) in coordinates.items():
            with self.subTest(city=city):
                response = io.BytesIO(b'{"current":{"weather_code":61}}')
                with patch.object(main, "urlopen", return_value=response) as open_url:
                    self.assertEqual(main.fetch_weather_code(city), 61)
                url = urlsplit(open_url.call_args.args[0])
                self.assertEqual(url.scheme, "https")
                self.assertEqual(url.netloc, "api.open-meteo.com")
                self.assertEqual(url.path, "/v1/forecast")
                self.assertEqual(
                    parse_qs(url.query),
                    {"latitude": [latitude], "longitude": [longitude], "current": ["weather_code"]},
                )
                self.assertEqual(open_url.call_args.kwargs["timeout"], 5)

    def test_malformed_json_is_rejected(self):
        with patch.object(main, "urlopen", return_value=io.BytesIO(b"invalid JSON")):
            with self.assertRaises(json.JSONDecodeError):
                main.fetch_weather_code(1)

    def test_response_without_weather_code_is_rejected(self):
        with patch.object(main, "urlopen", return_value=io.BytesIO(b'{"current":{}}')):
            with self.assertRaises(KeyError):
                main.fetch_weather_code(1)

    def test_non_integer_weather_code_is_rejected(self):
        for code in (True, "61", 61.0, None):
            payload = json.dumps({"current": {"weather_code": code}}).encode()
            with self.subTest(code=code):
                with patch.object(main, "urlopen", return_value=io.BytesIO(payload)):
                    with self.assertRaises(ValueError):
                        main.fetch_weather_code(1)

    def test_connection_error_reaches_the_caller(self):
        with patch.object(main, "urlopen", side_effect=URLError("offline")):
            with self.assertRaises(URLError):
                main.fetch_weather_code(1)


class ConsoleTests(unittest.TestCase):
    def run_console(self, entered):
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            patch("builtins.input", return_value=entered, side_effect=EOFError if entered is None else None),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            code = main.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_valid_input_prints_one_word_after_real_http_request(self):
        requests = []

        class WeatherHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                body = b'{"current":{"weather_code":61}}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), WeatherHandler) as server:
            worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
            worker.start()
            try:
                with (
                    patch.object(main, "API_URL", f"http://127.0.0.1:{server.server_port}/v1/forecast"),
                    patch.object(main.random, "choice", side_effect=lambda words: words[1]),
                ):
                    code, output, _ = self.run_console("2")
            finally:
                server.shutdown()
                worker.join()

        self.assertEqual((code, output), (0, "капля\n"))
        self.assertEqual(len(requests), 1)
        self.assertEqual(parse_qs(urlsplit(requests[0]).query)["latitude"], ["59.94"])

    def test_invalid_or_missing_input_does_not_call_api(self):
        for entered in ("abc", "4", None):
            with self.subTest(entered=entered):
                with patch.object(main, "fetch_weather_code") as fetch:
                    code, output, error = self.run_console(entered)
                self.assertEqual((code, output), (2, ""))
                self.assertIn("Введите целое число от 1 до 3.", error)
                fetch.assert_not_called()

    def test_service_failure_prints_error_and_no_word(self):
        for failure in (URLError("offline"), TimeoutError(), KeyError("current")):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(main, "fetch_weather_code", side_effect=failure):
                    code, output, error = self.run_console("1")
                self.assertEqual((code, output), (1, ""))
                self.assertIn("Не удалось получить погоду.", error)
