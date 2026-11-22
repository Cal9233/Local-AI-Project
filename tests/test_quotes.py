import unittest
import json
from pathlib import Path
from main import load_quotes, filter_by_part_number, find_cheapest_eligible_quote, file_dir


class TestQuotes(unittest.TestCase):
    def setUp(self):
        self.path = Path(__file__).parent.parent / "data" / "expected_results.json"
        
        with open(self.path, "r", encoding="utf-8") as f:
            self.expected_data = json.load(f)

    def test_load_quotes(self):
        quotes = load_quotes(self.path)
        self.assertEqual(quotes, self.expected_data)


if __name__ == "__main__":
    unittest.main()
