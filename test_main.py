import unittest
import json
import io

from unittest.mock import patch
from hashlib import sha256
from math import factorial

import main


class TestWordIndex(unittest.TestCase):

    def test_minimum(self):
        self.assertTrue(0 <= main.word_index(0) < main.ROW_COUNT)

    def test_maximum(self):
        self.assertTrue(0 <= main.word_index(100) < main.ROW_COUNT)

    def test_negative(self):
        with self.assertRaises(ValueError):
            main.word_index(-1)

    def test_above_maximum(self):
        with self.assertRaises(ValueError):
            main.word_index(101)

    @patch("main.random.randint", side_effect=[3, 72])
    def test_calculation(self, mock_random):
        result = factorial(45 * 3) + 72
        digest = sha256(str(result).encode("utf-8")).digest()
        expected = int.from_bytes(digest, "big") % main.ROW_COUNT
        self.assertEqual(main.word_index(45), expected)

    @patch("main.random.randint", side_effect=[2, 10])
    def test_random_calls(self, mock_random):
        main.word_index(5)
        self.assertEqual(
            mock_random.call_args_list,
            [unittest.mock.call(1, 5), unittest.mock.call(0, 100)]
        )


class TestFetchWord(unittest.TestCase):

    def fetch(self, data):
        response = io.BytesIO(json.dumps(data).encode("utf-8"))
        with patch("main.urlopen", return_value=response):
            return main.fetch_word(10)

    def test_valid_word(self):
        data = {"rows": [{"row": {"russian_word": "кот"}}]}
        self.assertEqual(self.fetch(data), "кот")

    def test_whitespace(self):
        data = {"rows": [{"row": {"russian_word": " кот "}}]}
        self.assertEqual(self.fetch(data), "кот")

    def test_empty_rows(self):
        with self.assertRaises(ValueError):
            self.fetch({"rows": []})

    def test_missing_word(self):
        with self.assertRaises(ValueError):
            self.fetch({"rows": [{"row": {}}]})

    def test_invalid_type(self):
        data = {"rows": [{"row": {"russian_word": 123}}]}
        with self.assertRaises(ValueError):
            self.fetch(data)

    def test_multiple_words(self):
        data = {"rows": [{"row": {"russian_word": "белый кот"}}]}
        with self.assertRaises(ValueError):
            self.fetch(data)

    def test_empty_word(self):
        data = {"rows": [{"row": {"russian_word": ""}}]}
        with self.assertRaises(ValueError):
            self.fetch(data)


class TestMain(unittest.TestCase):

    def run_app(self, value, error=None):
        with patch("builtins.input", return_value=value), \
             patch("main.fetch_word", return_value="кот",
                   side_effect=error), \
             patch("sys.stdout", new_callable=io.StringIO) as output, \
             patch("sys.stderr", new_callable=io.StringIO):

            result = main.main()
            return result, output.getvalue()

    def test_success(self):
        result, output = self.run_app("10")
        self.assertEqual(result, 0)
        self.assertEqual(output.strip(), "кот")

    def test_invalid_input(self):
        self.assertEqual(self.run_app("abc")[0], 1)

    def test_negative_input(self):
        self.assertEqual(self.run_app("-1")[0], 1)

    def test_large_input(self):
        self.assertEqual(self.run_app("101")[0], 1)

    def test_empty_input_stream(self):
        with patch("builtins.input", side_effect=EOFError), \
             patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main.main(), 1)

    def test_network_error(self):
        self.assertEqual(self.run_app("10", OSError())[0], 1)

    def test_dictionary_error(self):
        self.assertEqual(self.run_app("10", ValueError())[0], 1)
        
class TestFormatWord(unittest.TestCase):

    def test_default_format(self):
        self.assertEqual(main.format_word("кот"), "кот")

    def test_uppercase_format(self):
        self.assertEqual(main.format_word("кот", True), "КОТ")

    def test_disabled_uppercase(self):
        self.assertEqual(main.format_word("кот", False), "кот")

    def test_already_uppercase(self):
        self.assertEqual(main.format_word("КОТ", True), "КОТ")

    def test_mixed_case(self):
        self.assertEqual(main.format_word("КоТ", True), "КОТ")

if __name__ == "__main__":
    unittest.main()
