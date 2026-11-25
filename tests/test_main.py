"""Модульные и интеграционные тесты генератора случайных слов."""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

import main

ROOT = Path(__file__).resolve().parents[1]
PROMPT = "Введите целое число от 0 до 100."


class WordTests(unittest.TestCase):
    def test_zero_is_supported(self):
        with patch("main.random.randint", side_effect=[5, 0]):
            self.assertEqual(main.choose_word(0), "луна")

    def test_one_hundred_is_supported(self):
        with patch("main.random.randint", side_effect=[5, 100]):
            self.assertEqual(main.choose_word(100), "море")

    def test_below_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "от 0 до 100"):
            main.choose_word(-1)

    def test_above_hundred_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "от 0 до 100"):
            main.choose_word(101)

    def test_factorial_receives_multiplied_number(self):
        with (
            patch("main.random.randint", side_effect=[3, 0]),
            patch("main.factorial", return_value=120) as calculate,
        ):
            main.choose_word(45)

        calculate.assert_called_once_with(135)

    def test_requests_multiplier_and_bonus_in_their_ranges(self):
        with patch("main.random.randint", side_effect=[1, 0]) as draw:
            main.choose_word(4)

        self.assertEqual(draw.call_args_list, [call(1, 5), call(0, 100)])

    def test_adds_bonus_before_hashing(self):
        with (
            patch("main.random.randint", side_effect=[2, 9]),
            patch("main.sha256", wraps=main.sha256) as hash_value,
        ):
            main.choose_word(4)

        hash_value.assert_called_once_with(b"40329")

    def test_converts_hash_to_word_index(self):
        with (
            patch("main.random.randint", side_effect=[1, 0]),
            patch("main.sha256") as hash_value,
        ):
            # Младший байт равен 33. Остаток при делении на 16 равен 1.
            hash_value.return_value.digest.return_value = bytes(31) + b"\x21"
            self.assertEqual(main.choose_word(1), "река")

    def test_known_calculation_selects_expected_word(self):
        with patch("main.random.randint", side_effect=[3, 72]):
            self.assertEqual(main.choose_word(45), "облако")

    def test_input_changes_word_with_fixed_random_values(self):
        with patch("main.random.randint", side_effect=[1, 0, 1, 0]):
            first_word = main.choose_word(2)
            second_word = main.choose_word(3)

        self.assertEqual((first_word, second_word), ("лес", "солнце"))


class ConsoleTests(unittest.TestCase):
    def run_app(self, value):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py")],
            input=value,
            encoding="utf-8",
            capture_output=True,
            timeout=5,
            cwd=ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def assert_successful_input(self, value):
        result = self.run_app(value)
        self.assertEqual(result.returncode, 0, result.stderr)
        words = result.stdout.splitlines()
        self.assertEqual(len(words), 1, result.stdout)
        self.assertIn(words[0], main.WORDS)
        self.assertEqual(result.stderr.splitlines(), [PROMPT])

    def assert_rejected_input(self, value):
        result = self.run_app(value)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.splitlines(), [PROMPT, f"Ошибка. {PROMPT}"])

    def test_valid_input_prints_one_word(self):
        self.assert_successful_input("45\n")

    def test_whitespace_around_number_is_accepted(self):
        self.assert_successful_input(" 45 \n")

    def test_zero_is_read_from_console(self):
        self.assert_successful_input("0\n")

    def test_one_hundred_is_read_from_console(self):
        self.assert_successful_input("100\n")

    def test_negative_number_is_rejected(self):
        self.assert_rejected_input("-1\n")

    def test_number_above_limit_is_rejected(self):
        self.assert_rejected_input("101\n")

    def test_text_input_is_rejected(self):
        self.assert_rejected_input("abc\n")

    def test_fractional_input_is_rejected(self):
        self.assert_rejected_input("3.5\n")

    def test_blank_line_is_rejected(self):
        self.assert_rejected_input("\n")

    def test_end_of_input_is_handled(self):
        self.assert_rejected_input("")


if __name__ == "__main__":
    unittest.main()
