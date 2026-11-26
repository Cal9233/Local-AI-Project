"""Field-level extraction accuracy on the checked emails in evals/.

Runs model.extract_quotes on each email (optionally several times), compares
each field with evals/expected.json, and checks where the pipeline routes each
record (ranked vs review). Model output varies, so report rates, not one run.

Usage (from the project root):
    .venv/bin/python -m evals.run_eval --runs 3
    .venv/bin/python -m evals.run_eval --split dev --cases E05 E06
"""

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

from config import LLM_MODEL
from database import create_db
from extraction import CENTS, store_extracted, supplier_from_email, unit_price
from model import PROMPT_VERSION, Quote, extract_quotes

EVALS_DIR = Path(__file__).resolve().parent
FIELDS = ["part_number", "quantity", "condition", "unit_price", "currency", "sale_basis", "core_charge"]


def as_record(quote: Quote) -> dict:
    """Turn an extracted Quote into the expected.json record shape (strings for money)."""
    return {
        "part_number": quote.part_number,
        "quantity": quote.quantity,
        "condition": quote.condition.value if quote.condition else None,
        "unit_price": None if quote.price is None else str(unit_price(quote)),
        "currency": quote.currency,
        "sale_basis": quote.sale_basis.value,
        "core_charge": None if quote.core_charge is None else str(quote.core_charge.quantize(CENTS)),
    }


def pair_records(expected: list[dict], got: list[dict]) -> list[tuple[dict, dict | None]]:
    """Pair each expected record with the unused extracted record that matches most fields.

    Unpaired expected records get None (every field counts as wrong).
    """
    unused = list(got)
    pairs = []
    for exp in expected:
        best = max(unused, key=lambda g: sum(g[f] == exp[f] for f in FIELDS), default=None)
        if best is not None:
            unused.remove(best)
        pairs.append((exp, best))
    return pairs


def run_case(case: dict) -> dict:
    """Extract one email once; return per-field matches, counts, routing, and any error."""
    path = EVALS_DIR / case["file"]
    text = path.read_text()
    start = time.perf_counter()
    try:
        quotes = extract_quotes(text)
    except Exception as err:  # noqa: BLE001 - an eval records every failure instead of stopping
        return {"id": case["id"], "error": f"{type(err).__name__}: {err}"[:300],
                "latency_s": round(time.perf_counter() - start, 1)}
    latency = round(time.perf_counter() - start, 1)

    got = [as_record(q) for q in quotes]
    matches = {f: 0 for f in FIELDS}
    for exp, g in pair_records(case["records"], got):
        for f in FIELDS:
            matches[f] += int(g is not None and g[f] == exp[f])

    # Route through the real storage rules into a throwaway database.
    conn = sqlite3.connect(":memory:")
    create_db(conn)
    supplier = supplier_from_email(text)
    routes = [
        store_extracted(conn, q, source_file=path.name, source_text=text, supplier=supplier, record_no=i)
        for i, q in enumerate(quotes, start=1)
    ]
    reasons = [r for (r,) in conn.execute("SELECT reason FROM review_quotes ORDER BY record_no")]
    conn.close()

    return {
        "id": case["id"], "latency_s": latency,
        "expected_records": len(case["records"]), "extracted_records": len(got),
        "matches": matches, "routes": routes, "review_reasons": reasons,
        "extracted": got,
    }


def summarize(results: list[dict], cases: dict) -> dict:
    """Aggregate per-field accuracy by split: matches / expected records over all runs."""
    summary = {}
    for split in sorted({c["split"] for c in cases.values()}):
        rs = [r for r in results if cases[r["id"]]["split"] == split]
        total = sum(len(cases[r["id"]]["records"]) for r in rs)
        fields = {f: sum(r.get("matches", {}).get(f, 0) for r in rs) for f in FIELDS}
        summary[split] = {
            "runs": len(rs),
            "errors": sum("error" in r for r in rs),
            "record_count_exact": sum(r.get("extracted_records") == len(cases[r["id"]]["records"]) for r in rs),
            "expected_records": total,
            "field_matches": fields,
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=1, help="extractions per email")
    parser.add_argument("--split", choices=["dev", "held_out", "all"], default="all")
    parser.add_argument("--cases", nargs="*", help="only these case IDs, e.g. E05 E06")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    data = json.loads((EVALS_DIR / "expected.json").read_text())
    cases = {c["id"]: c for c in data["cases"]
             if (args.split == "all" or c["split"] == args.split)
             and (not args.cases or c["id"] in args.cases)}

    results = []
    for case in cases.values():
        for run in range(1, args.runs + 1):
            r = run_case(case)
            results.append(r)
            if "error" in r:
                print(f"{r['id']} run {run}: ERROR {r['error']}")
            else:
                wrong = [f for f in FIELDS if r["matches"][f] < r["expected_records"]]
                print(f"{r['id']} run {run}: {r['extracted_records']}/{r['expected_records']} records, "
                      f"wrong fields={wrong or '-'}, routes={r['routes']}, review={r['review_reasons']}, "
                      f"{r['latency_s']}s")

    summary = summarize(results, cases)
    print(f"\nModel {LLM_MODEL}, prompt {PROMPT_VERSION}, {args.runs} run(s) per email")
    for split, s in summary.items():
        print(f"\n[{split}] {s['runs']} runs, {s['errors']} errors, "
              f"record count exact {s['record_count_exact']}/{s['runs']}")
        for f in FIELDS:
            n, d = s["field_matches"][f], s["expected_records"]
            print(f"  {f:<12} {n}/{d}" + (f"  ({n / d:.0%})" if d else ""))

    out_dir = EVALS_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{datetime.now():%Y-%m-%dT%H%M%S}_{PROMPT_VERSION}.json"
    out.write_text(json.dumps({
        "model": LLM_MODEL, "prompt_version": PROMPT_VERSION, "runs": args.runs,
        "summary": summary, "results": results,
    }, indent=1))
    print(f"\nSaved {out.relative_to(EVALS_DIR.parent)}")


if __name__ == "__main__":
    sys.exit(main())
