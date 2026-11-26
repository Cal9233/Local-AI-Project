import json
import unittest
from decimal import Decimal
from pathlib import Path
import sqlite3
from model import Quote, Conditions, Sales, PriceBasis
from extraction import ingest_email, phrase_in_source, store_extracted, supplier_from_email

from main import (
    file_dir,
    filter_by_part_number,
    find_cheapest_eligible_quote,
    load_quotes,
    validate_request,
)

from database import (
    create_db, 
    import_quotes, 
    filter_by_part_number_sql,
    find_cheapest_sql
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONTRACT_PATH = DATA_DIR / "expected_results.json"
EMAILS_DIR = DATA_DIR.parent / "evals" / "emails"


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

    filter_by_part_number = staticmethod(filter_by_part_number)
    find_cheapest_eligible_quote = staticmethod(find_cheapest_eligible_quote)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
            contract = json.load(f)
        cls.cases = contract["test_cases"]
        cls.source = load_quotes(DATA_DIR / contract["dataset_file"])
    
    def run_case(self, case_id):
        case = [i for i in self.cases if i["id"] == case_id].pop(0)
        if case["action"] == "filter_by_part_number":
            actual = {
                "matching_quote_ids": self.filter_by_part_number(
                    self.source, case["input"]["part_number"]
                )
            }
        elif case["action"] == "find_cheapest_eligible_quote":
            actual = self.find_cheapest_eligible_quote(self.source, case["input"])
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

class TestContractSQL(TestContract):
    """Acceptance tests T01-T10 again, with SQLite as the backend.

    Inherits run_case and test_T01..T10; only the functions and the source differ.
    """

    filter_by_part_number = staticmethod(filter_by_part_number_sql)
    find_cheapest_eligible_quote = staticmethod(find_cheapest_sql)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # loads cls.cases (and a list source we replace)
        cls.csv_path = DATA_DIR / "sample_quotes.csv"
        cls.conn = sqlite3.connect(":memory:")  # never touch the real quotes.db
        create_db(cls.conn)
        import_quotes(cls.conn, cls.csv_path)
        cls.source = cls.conn

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        super().tearDownClass()

    def test_import_twice_stores_each_quote_once(self):
        import_quotes(self.conn, self.csv_path)
        (count,) = self.conn.execute("SELECT COUNT(*) FROM quotes").fetchone()
        self.assertEqual(count, len(load_quotes(self.csv_path)))

class TestStoreExtracted(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        create_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def store(self, quote, email="E05.txt"):
        """Store `quote` as record 1 of a real eval email."""
        return store_extracted(
            self.conn, quote, source_file=email, source_text=(EMAILS_DIR / email).read_text(),
            supplier="example-supplier", record_no=1,
        )

    def test_missing_currency_is_stored_for_review_not_ranked(self):
        # E05: price present, currency never stated.
        phrase = "Price 2,750.00 each, outright."
        quote = Quote(part_number="TRAIN-PN-014", quantity=3, condition='OH', currency=None, price=Decimal("2750.00"), price_basis="PER_UNIT", sale_basis="OUTRIGHT", core_charge=None, price_phrase=phrase)

        outcome = self.store(quote)

        self.assertEqual(outcome, "review")
        rows = self.conn.execute("SELECT part_number, price, currency, reason, source_file, source_phrase FROM review_quotes").fetchall()
        self.assertEqual(len(rows), 1)
        part_number, price, currency, reason, source_file, source_phrase = rows[0]
        self.assertEqual(part_number, "TRAIN-PN-014")
        self.assertEqual(price, "2750.00")          # price kept, not dropped
        self.assertIsNone(currency)                 # unknown stays unknown, never "USD"
        self.assertEqual(reason, "missing_currency")
        self.assertEqual(source_file, "E05.txt")
        self.assertEqual(source_phrase, phrase)     # reviewer sees the original text

        # Flagged before ranking: a buyer asking for USD must not get this quote.
        request = {"part_number": "TRAIN-PN-014", "condition": "OH", "currency": "USD", "sale_basis": "OUTRIGHT", "requested_quantity": 1}
        result = find_cheapest_sql(self.conn, request)
        self.assertEqual(result["status"], "no_eligible_quote")

    def test_missing_price_is_stored_for_review(self):
        quote = Quote(part_number="TRAIN-PN-014", quantity=3, condition='OH', currency="USD", price=None, price_basis="PER_UNIT", sale_basis="OUTRIGHT", core_charge=None, price_phrase=None)

        self.assertEqual(self.store(quote), "review")
        (price, reason) = self.conn.execute("SELECT price, reason FROM review_quotes").fetchone()
        self.assertIsNone(price)
        self.assertEqual(reason, "missing_price")

    def test_phrase_not_in_email_goes_to_review(self):
        # Valid structure, but the model "quoted" text the email does not contain.
        quote = Quote(part_number="TRAIN-PN-004", quantity=3, condition='SV', currency="USD", price=Decimal("14625.00"), price_basis="LOT", sale_basis="OUTRIGHT", core_charge=None, price_phrase="USD 14,625.00 per unit")

        self.assertEqual(self.store(quote, "E06.txt"), "review")
        (reason,) = self.conn.execute("SELECT reason FROM review_quotes").fetchone()
        self.assertEqual(reason, "phrase_not_in_source")

    def test_complete_quote_is_ranked_with_unit_price_and_source(self):
        # E06: lot total 14,625.00 for 3 units -> 4,875.00 each (hand-checked in 4.1).
        phrase = "USD 14,625.00 total for the lot"
        quote = Quote(part_number="TRAIN-PN-004", quantity=3, condition='SV', currency="USD", price=Decimal("14625.00"), price_basis="LOT", sale_basis="OUTRIGHT", core_charge=None, price_phrase=phrase)

        self.assertEqual(self.store(quote, "E06.txt"), "ranked")
        request = {"part_number": "TRAIN-PN-004", "condition": "SV", "currency": "USD", "sale_basis": "OUTRIGHT", "requested_quantity": 2}
        result = find_cheapest_sql(self.conn, request)
        self.assertEqual(result["best_quote_id"], "E06-1")
        self.assertEqual(result["unit_price"], "4875.00")
        (file_name, source_phrase) = self.conn.execute("SELECT file_name, source_phrase FROM quotes").fetchone()
        self.assertEqual((file_name, source_phrase), ("E06.txt", phrase))

    def test_ingest_email_is_rerun_safe_and_uses_header_supplier(self):
        phrase = "Price 2,750.00 each, outright."
        fake = lambda text: [Quote(part_number="TRAIN-PN-014", quantity=3, condition='OH', currency=None, price=Decimal("2750.00"), price_basis="PER_UNIT", sale_basis="OUTRIGHT", core_charge=None, price_phrase=phrase)]  # noqa: E731

        self.assertEqual(ingest_email(self.conn, EMAILS_DIR / "E05.txt", fake), ["review"])
        ingest_email(self.conn, EMAILS_DIR / "E05.txt", fake)

        rows = self.conn.execute("SELECT supplier, source_file, record_no FROM review_quotes").fetchall()
        self.assertEqual(rows, [("bluesky-components.example", "E05.txt", 1)])


class TestSourceHelpers(unittest.TestCase):
    def test_phrase_match_ignores_line_breaks(self):
        self.assertTrue(phrase_in_source("price\n  2,750.00", "Price is: price 2,750.00 each"))

    def test_missing_phrase_never_matches(self):
        self.assertFalse(phrase_in_source(None, "anything"))
        self.assertFalse(phrase_in_source("", "anything"))

    def test_supplier_without_from_header_raises(self):
        with self.assertRaises(ValueError):
            supplier_from_email("Subject: hi\n\nUSD 100.00")


if __name__ == "__main__":
    unittest.main()
