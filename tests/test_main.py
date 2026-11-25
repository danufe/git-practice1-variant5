"""Модульные и интеграционные проверки генератора слов."""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

import main

ROOT = Path(__file__).resolve().parents[1]


class WordTests(unittest.TestCase):
    def test_zero_is_supported(self):
        self.assertIn(main.choose_word(0), main.WORDS)

    def test_one_hundred_is_supported(self):
        self.assertIn(main.choose_word(100), main.WORDS)

    def test_out_of_range_is_rejected(self):
        for number in (-1, 101):
            with self.subTest(number=number), self.assertRaises(ValueError):
                main.choose_word(number)

    def test_factorial_receives_multiplied_number(self):
        with patch("main.random.randint", return_value=3):
            with patch("main.factorial", return_value=120) as calculate:
                self.assertIn(main.choose_word(45), main.WORDS)
        calculate.assert_called_once_with(135)

    def test_known_calculation_selects_expected_word(self):
        with patch("main.random.randint", side_effect=[3, 72]) as random_value:
            self.assertEqual(main.choose_word(45), "облако")
        self.assertEqual(random_value.call_args_list, [call(1, 5), call(0, 100)])


class ConsoleTests(unittest.TestCase):
    def run_app(self, value):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py")],
            input=value,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=5,
            cwd=ROOT,
        )

    def test_valid_input_prints_one_word(self):
        result = self.run_app(" 45 \n")
        self.assertEqual(result.returncode, 0)
        self.assertIn(result.stdout.strip(), main.WORDS)
        self.assertEqual(len(result.stdout.splitlines()), 1)

    def test_invalid_input_is_rejected(self):
        for value in ("abc\n", "3.5\n", "\n", "-1\n", "101\n"):
            with self.subTest(value=value):
                result = self.run_app(value)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn("Введите целое число", result.stderr)

    def test_end_of_input_is_handled(self):
        result = self.run_app("")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Введите целое число", result.stderr)


if __name__ == "__main__":
    unittest.main()
