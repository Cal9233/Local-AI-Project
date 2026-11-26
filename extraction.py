"""Extract -> validate -> store pipeline for supplier emails.

The model only extracts. Code decides whether a quote can be ranked, does the
arithmetic, assigns IDs, and checks the model's supporting phrase against the email.
"""

import re
import sqlite3
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from database import insert_extracted_quote, insert_review_quote
from model import PriceBasis, Quote

CENTS = Decimal("0.01")
SUPPORTED_CURRENCIES = {"USD", "EUR"}


def unit_price(quote: Quote) -> Decimal:
    """Return the per-unit price of a quote that has a price, quantized to cents.

    A LOT price is divided by quantity. The Quote schema guarantees quantity > 0.
    Review records never reach this function (see store_extracted).
    """
    if quote.price_basis == PriceBasis.PER_UNIT:
        return quote.price.quantize(CENTS)
    return (quote.price / quote.quantity).quantize(CENTS)


def _normalize(text: str) -> str:
    """Collapse whitespace so a phrase split across lines still matches."""
    return re.sub(r"\s+", " ", text).strip()


def phrase_in_source(phrase: str | None, source_text: str) -> bool:
    """Return True if `phrase` appears in `source_text` (whitespace-insensitive)."""
    if not phrase:
        return False
    return _normalize(phrase) in _normalize(source_text)


def supplier_from_email(email_text: str) -> str:
    """Return the sender's domain from the email's From: header.

    Raises:
        ValueError: the email has no From: line with an address.
    """
    match = re.search(r"^From:.*?@([\w.-]+)", email_text, re.MULTILINE)
    if match is None:
        raise ValueError("email has no From: address; supplier unknown")
    return match.group(1).lower()


def review_reason(quote: Quote, source_text: str) -> str | None:
    """Return why a quote cannot be ranked, or None if it can be.

    Checks run in order and the first failure wins:
    missing price, missing currency, unsupported currency, missing condition
    (ranking needs an exact condition match), and a price phrase that is not in
    the email (the price cannot be traced to its source).
    """
    if quote.price is None:
        return "missing_price"
    if quote.currency is None:
        return "missing_currency"
    if quote.currency not in SUPPORTED_CURRENCIES:
        return "unsupported_currency"
    if quote.condition is None:
        return "missing_condition"
    if not phrase_in_source(quote.price_phrase, source_text):
        return "phrase_not_in_source"
    return None


def _text(value: Decimal | None) -> str | None:
    """Format an optional Decimal as a two-decimal string, keeping None as None."""
    return None if value is None else str(value.quantize(CENTS))


def store_extracted(
    conn: sqlite3.Connection,
    quote: Quote,
    *,
    source_file: str,
    source_text: str,
    supplier: str,
    record_no: int,
) -> str:
    """Store one validated quote: rankable ones in `quotes`, the rest in `review_quotes`.

    Args:
        conn: open SQLite connection with the schema created.
        quote: a validated Quote from the model.
        source_file: name of the email/document the quote came from.
        source_text: full text of that source, used to verify the price phrase.
        supplier: supplier identifier (from the email header, not the model).
        record_no: 1-based position of this quote within the source.

    Returns:
        "ranked" or "review".
    """
    reason = review_reason(quote, source_text)
    if reason is not None:
        # Review records never reach unit_price(): store the raw price and basis.
        insert_review_quote(conn, {
            "supplier": supplier,
            "part_number": quote.part_number,
            "quantity": quote.quantity,
            "condition": quote.condition.value if quote.condition else None,
            "price": _text(quote.price),
            "price_basis": quote.price_basis.value,
            "currency": quote.currency,
            "sale_basis": quote.sale_basis.value,
            "core_charge": _text(quote.core_charge),
            "reason": reason,
            "source_file": source_file,
            "record_no": record_no,
            "source_phrase": quote.price_phrase,
        })
        return "review"

    insert_extracted_quote(conn, {
        "quote_id": f"{Path(source_file).stem}-{record_no}",
        "supplier": supplier,
        "part_number": quote.part_number,
        "quantity": quote.quantity,
        "condition": quote.condition.value,
        "unit_price": int(unit_price(quote) * 100),
        "currency": quote.currency,
        "sale_basis": quote.sale_basis.value,
        "file_name": source_file,
        "row_number": record_no,
        "source_phrase": quote.price_phrase,
    })
    return "ranked"


def ingest_email(
    conn: sqlite3.Connection,
    path: Path,
    extract: Callable[[str], list[Quote]],
) -> list[str]:
    """Run one email through extract -> validate -> store.

    Args:
        conn: open SQLite connection with the schema created.
        path: the email file.
        extract: returns validated quotes for an email's text
            (model.extract_quotes in production, a fake in tests).

    Returns:
        One outcome ("ranked" / "review") per extracted quote, in order.
    """
    text = Path(path).read_text()
    supplier = supplier_from_email(text)
    return [
        store_extracted(
            conn, quote,
            source_file=Path(path).name, source_text=text,
            supplier=supplier, record_no=i,
        )
        for i, quote in enumerate(extract(text), start=1)
    ]
