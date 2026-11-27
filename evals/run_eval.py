"""Field-level extraction accuracy on the checked emails in evals/.

Runs model.extract_quotes on each email (optionally several times), compares
each field with evals/expected.json, and checks where the pipeline routes each
record (ranked vs review). Model output varies, so report rates, not one run.

Usage (from the project root; run it as a module so `config` and `model` import):
    .venv/bin/python -m evals.run_eval --runs 3
    .venv/bin/python -m evals.run_eval --model qwen3.6:35b --runs 3 --warmup
    .venv/bin/python -m evals.run_eval --model claude-opus-5-5 --runs 1
    .venv/bin/python -m evals.run_eval --split dev --cases E05 E06
    .venv/bin/python -m evals.run_eval --cases E01 --timeout 1   # simulate a timeout
"""

import argparse
import json
import logging
import sqlite3
import statistics
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from config import LLM_MODEL
from database import create_db
from extraction import CENTS, store_extracted, supplier_from_email, unit_price
from model import PROMPT_VERSION, TIMEOUT, Quote, extract_quotes_with_reply

EVALS_DIR = Path(__file__).resolve().parent
# USD per million tokens (input, output), Anthropic first-party list prices, 2026-11.
# Check https://platform.claude.com/docs/en/about-claude/pricing before relying on them.
PRICES_PER_MTOK = {
    "claude-opus-5-5": (Decimal("4.00"), Decimal("20.00")),
    "claude-sonnet-5-5": (Decimal("2.00"), Decimal("10.00")),
    "claude-haiku-5-5": (Decimal("0.10"), Decimal("0.50")),
}
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


def call_cost_usd(model: str, input_tokens: int | None, output_tokens: int | None) -> Decimal | None:
    """Dollar cost of one hosted call from its token counts; None for local or unpriced models."""
    if model not in PRICES_PER_MTOK or input_tokens is None or output_tokens is None:
        return None
    in_price, out_price = PRICES_PER_MTOK[model]
    return (in_price * input_tokens + out_price * output_tokens) / Decimal(1_000_000)


def results_filename(when: datetime, model: str, prompt_version: str) -> str:
    """Results file name that records the model; ':' and '/' are not safe in file names."""
    safe = model.replace(":", "-").replace("/", "-")
    return f"{when:%Y-%m-%dT%H%M%S}_{safe}_{prompt_version}.json"


def run_case(case: dict, model: str = LLM_MODEL, timeout: float = TIMEOUT) -> dict:
    """Extract one email once; return per-field matches, counts, routing, stats, and any error."""
    path = EVALS_DIR / case["file"]
    text = path.read_text()
    start = time.perf_counter()
    try:
        quotes, reply = extract_quotes_with_reply(text, model, timeout)
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
        "input_tokens": reply.input_tokens, "output_tokens": reply.output_tokens,
        "thinking_chars": reply.thinking_chars, "tokens_per_s": reply.tokens_per_s,
        "cost_usd": None if (c := call_cost_usd(model, reply.input_tokens, reply.output_tokens)) is None
        else str(c.quantize(Decimal("0.000001"))),
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
            "unknowns": unknown_counts(rs, cases),
            "latency": spread([r["latency_s"] for r in rs if "error" not in r]),
            "output_tokens": spread([r["output_tokens"] for r in rs if r.get("output_tokens") is not None]),
            "thinking_chars": spread([r["thinking_chars"] for r in rs if r.get("thinking_chars") is not None]),
            "tokens_per_s": spread([r["tokens_per_s"] for r in rs if r.get("tokens_per_s")]),
            "cost_usd": str(sum((Decimal(r["cost_usd"]) for r in rs if r.get("cost_usd")), Decimal(0))),
        }
    return summary


def spread(values: list[float]) -> dict | None:
    """Median, min and max of a list of numbers; None when there are none."""
    if not values:
        return None
    return {"median": round(statistics.median(values), 1), "min": round(min(values), 1),
            "max": round(max(values), 1), "n": len(values)}


def unknown_counts(results: list[dict], cases: dict) -> dict:
    """How the model handled fields the email does not state (expected null).

    kept_null: the model correctly left it null. invented: the model filled in a value.
    Counts only paired records, so a missing record is not double-counted here.
    """
    kept = invented = 0
    for r in results:
        if "error" in r:
            continue
        for exp, got in pair_records(cases[r["id"]]["records"], r["extracted"]):
            if got is None:
                continue
            for f in FIELDS:
                if exp[f] is None:
                    if got[f] is None:
                        kept += 1
                    else:
                        invented += 1
    return {"kept_null": kept, "invented": invented}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=1, help="extractions per email")
    parser.add_argument("--split", choices=["dev", "held_out", "all"], default="all")
    parser.add_argument("--cases", nargs="*", help="only these case IDs, e.g. E05 E06")
    parser.add_argument("--model", default=LLM_MODEL,
                        help="Ollama model name, or claude-* for the Anthropic API")
    parser.add_argument("--timeout", type=float, default=TIMEOUT, help="seconds per model call")
    parser.add_argument("--warmup", action="store_true",
                        help="make one unscored call first so model load time is not counted")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    data = json.loads((EVALS_DIR / "expected.json").read_text())
    cases = {c["id"]: c for c in data["cases"]
             if (args.split == "all" or c["split"] == args.split)
             and (not args.cases or c["id"] in args.cases)}

    cold_start_s = None
    if args.warmup and cases:
        first = next(iter(cases.values()))
        cold_start_s = run_case(first, args.model, args.timeout)["latency_s"]
        print(f"warm-up ({first['id']}, not scored): {cold_start_s}s")

    results = []
    for case in cases.values():
        for run in range(1, args.runs + 1):
            r = run_case(case, args.model, args.timeout)
            results.append(r)
            if "error" in r:
                print(f"{r['id']} run {run}: ERROR {r['error']}")
            else:
                wrong = [f for f in FIELDS if r["matches"][f] < r["expected_records"]]
                print(f"{r['id']} run {run}: {r['extracted_records']}/{r['expected_records']} records, "
                      f"wrong fields={wrong or '-'}, routes={r['routes']}, review={r['review_reasons']}, "
                      f"{r['latency_s']}s")

    summary = summarize(results, cases)
    print(f"\nModel {args.model}, prompt {PROMPT_VERSION}, {args.runs} run(s) per email")
    for split, s in summary.items():
        print(f"\n[{split}] {s['runs']} runs, {s['errors']} errors, "
              f"record count exact {s['record_count_exact']}/{s['runs']}")
        for f in FIELDS:
            n, d = s["field_matches"][f], s["expected_records"]
            print(f"  {f:<12} {n}/{d}" + (f"  ({n / d:.0%})" if d else ""))
        u = s["unknowns"]
        print(f"  unknowns     kept null {u['kept_null']}, invented {u['invented']}")
        print(f"  latency s    {s['latency']}")
        print(f"  out tokens   {s['output_tokens']}  tok/s {s['tokens_per_s']}  cost USD {s['cost_usd']}")

    out_dir = EVALS_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / results_filename(datetime.now(), args.model, PROMPT_VERSION)
    out.write_text(json.dumps({
        "model": args.model, "prompt_version": PROMPT_VERSION, "runs": args.runs,
        "timeout_s": args.timeout, "cold_start_s": cold_start_s,
        "summary": summary, "results": results,
    }, indent=1))
    print(f"\nSaved {out.relative_to(EVALS_DIR.parent)}")


if __name__ == "__main__":
    sys.exit(main())
