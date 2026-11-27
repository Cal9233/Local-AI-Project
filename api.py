"""HTTP interface for the quote rules in main.py.

This layer only parses requests and formats responses. Every rule (part match,
eligibility, cheapest pick, money formatting) runs in main.py, the same code the
CLI and the T01-T10 contract tests use.

Run from the project root:  uvicorn api:app --reload
"""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from main import (
    file_dir,
    filter_by_part_number,
    find_cheapest_eligible_quote,
    load_quotes,
)

app = FastAPI(title="Aviation Quote Intelligence Assistant")

# min_length=1 rejects ?part_number= (empty) with a 422: searching for nothing is a
# bad request, not a valid search that found nothing.
PartNumber = Annotated[str, Query(min_length=1)]


@app.get("/ping")
def ping() -> dict:
    """Health check: confirms the server is up."""
    return {"status": "ok"}


@app.get("/quotes")
def get_quotes(part_number: PartNumber) -> dict:
    """Return the IDs of quotes for an exact part number, in CSV order (T01, T10).

    status is "no_match" when no quote exists for the part. This differs on purpose
    from /cheapest's "no_eligible_quote", where quotes exist but none passes the rules.
    """
    matching = filter_by_part_number(load_quotes(file_dir), part_number)
    return {
        "status": "found" if matching else "no_match",
        "matching_quote_ids": matching,
    }


@app.get("/cheapest")
def get_cheapest(
    part_number: PartNumber,
    requested_quantity: int,
    condition: str,
    currency: str,
    sale_basis: str,
) -> dict:
    """Return the cheapest eligible quote, exactly as find_cheapest_eligible_quote does.

    Raises:
        HTTPException 400: a business rule rejected the request (e.g. quantity < 1);
            detail carries the rule's own message.
    Missing or non-integer parameters get FastAPI's automatic 422.
    """
    request = {
        "part_number": part_number,
        "requested_quantity": requested_quantity,
        "condition": condition,
        "currency": currency,
        "sale_basis": sale_basis,
    }
    quotes = load_quotes(file_dir)
    try:
        return find_cheapest_eligible_quote(quotes, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
