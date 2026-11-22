import json
import unittest
from decimal import Decimal
from pathlib import Path

from main import (
    file_dir,
    filter_by_part_number,
    find_cheapest_eligible_quote,
    load_quotes,
    validate_request,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTRACT_PATH = DATA_DIR / "expected_results.json"


class TestLoadQuotes(unittest.TestCase):
    """Unit tests: the CSV loader converts types correctly."""

    def setUp(self):
        self.quotes = load_quotes(file_dir)

    def test_loads_every_row(self):
        self.assertEqual(len(self.quotes), 5)

    def test_quantity_is_int(self):
        for q in self.quotes:
            self.assertIsInstance(q["quantity"], int)

    def test_unit_price_is_decimal_not_float(self):
        for q in self.quotes:
            self.assertIsInstance(q["unit_price"], Decimal)
        self.assertEqual(self.quotes[0]["unit_price"], Decimal("1250.00"))

    def test_keeps_csv_row_order(self):
        ids = [q["quote_id"] for q in self.quotes]
        self.assertEqual(ids, ["Q001", "Q002", "Q003", "Q004", "Q005"])


class TestContract(unittest.TestCase):
    """Acceptance tests: every case T01-T10 in data/expected_results.json."""

    @classmethod
    def setUpClass(cls):
        with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
            contract = json.load(f)
        cls.cases = contract["test_cases"]
        cls.quotes = load_quotes(DATA_DIR / contract["dataset_file"])

    def run_case(self, case_id):
        case = [i for i in self.cases if i["id"] == case_id].pop(0)
        if case["action"] == "filter_by_part_number":
            actual = {
                "matching_quote_ids": filter_by_part_number(
                    self.quotes, case["input"]["part_number"]
                )
            }
        elif case["action"] == "find_cheapest_eligible_quote":
            actual = find_cheapest_eligible_quote(self.quotes, case["input"])
        else:
            self.fail(f"unknown action {case['action']!r}")
        self.assertEqual(actual, case["expected"])

    def test_T01(self):
        self.run_case('T01')

    def test_T02(self):
        self.run_case('T02')

    def test_T03(self):
        self.run_case('T03')

    def test_T04(self):
        self.run_case('T04')

    def test_T05(self):
        self.run_case('T05')

    def test_T06(self):
        self.run_case('T06')

    def test_T07(self):
        self.run_case('T07')

    def test_T08(self):
        self.run_case('T08')

    def test_T09(self):
        self.run_case('T09')

    def test_T10(self):
        self.run_case('T10')

class TestValidateRequest(unittest.TestCase):
    """Unit tests: invalid requests raise instead of returning False."""

    def base_request(self, qty):
        return {
            "part_number": "TRAIN-PN-001",
            "requested_quantity": qty,
            "condition": "OH",
            "currency": "USD",
            "sale_basis": "OUTRIGHT",
        }

    def test_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            validate_request(self.base_request(0))

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            validate_request(self.base_request(-1))

    def test_non_integer_quantity_raises(self):
        for bad in ("2", 1.5):
            with self.subTest(qty=bad), self.assertRaises(ValueError):
                validate_request(self.base_request(bad))


if __name__ == "__main__":
    unittest.main()
