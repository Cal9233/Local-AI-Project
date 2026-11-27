"""Integration tests: the HTTP API returns the same results as the rule functions."""

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api import app

CONTRACT = Path(__file__).resolve().parent.parent / "data" / "expected_results.json"
CASES = {c["id"]: c for c in json.loads(CONTRACT.read_text())["test_cases"]}


class TestAPI(unittest.TestCase):
    """Run contract cases and error cases through the HTTP layer."""

    client = TestClient(app)

    def cheapest(self, **overrides):
        return self.client.get("/cheapest", params={**CASES["T02"]["input"], **overrides})

    def test_cheapest_matches_contract(self):
        for case_id in ("T02", "T07"):
            with self.subTest(case_id):
                res = self.client.get("/cheapest", params=CASES[case_id]["input"])
                self.assertEqual(res.status_code, 200)
                self.assertEqual(res.json(), CASES[case_id]["expected"])

    def test_quotes_found_and_no_match(self):
        for case_id, status in (("T01", "found"), ("T10", "no_match")):
            with self.subTest(case_id):
                res = self.client.get("/quotes", params=CASES[case_id]["input"])
                self.assertEqual(res.status_code, 200)
                self.assertEqual(res.json()["status"], status)
                self.assertEqual(
                    res.json()["matching_quote_ids"],
                    CASES[case_id]["expected"]["matching_quote_ids"],
                )

    def test_no_eligible_quote_is_200(self):
        res = self.cheapest(requested_quantity=5)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "no_eligible_quote")

    def test_rejected_quantity_is_400_with_rule_message(self):
        for qty in (0, -1):
            with self.subTest(qty):
                res = self.cheapest(requested_quantity=qty)
                self.assertEqual(res.status_code, 400)
                self.assertIn(f"got {qty}", res.json()["detail"])

    def test_non_integer_quantity_is_422(self):
        self.assertEqual(self.cheapest(requested_quantity="abc").status_code, 422)

    def test_missing_or_empty_part_number_is_422(self):
        self.assertEqual(self.client.get("/quotes").status_code, 422)
        self.assertEqual(self.client.get("/quotes", params={"part_number": ""}).status_code, 422)
        self.assertEqual(self.client.get("/cheapest").status_code, 422)


if __name__ == "__main__":
    unittest.main()
