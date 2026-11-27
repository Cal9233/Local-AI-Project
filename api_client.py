"""Call the running API as a client (httpx) and compare with the contract.

Start the server first:  uvicorn api:app
Then:                    uv run python api_client.py
"""

import json
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
CONTRACT = Path(__file__).resolve().parent / "data" / "expected_results.json"


def main() -> None:
    """Send each cheapest/filter contract case to the API and report match or mismatch."""
    cases = json.loads(CONTRACT.read_text())["test_cases"]
    path_for = {"find_cheapest_eligible_quote": "/cheapest", "filter_by_part_number": "/quotes"}
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        for case in cases:
            res = client.get(path_for[case["action"]], params=case["input"])
            body = res.json()
            if case["action"] == "filter_by_part_number":
                body.pop("status")  # the contract for this action has no status field
            ok = res.status_code == 200 and body == case["expected"]
            print(f"{case['id']}  {res.status_code}  {'OK' if ok else 'MISMATCH ' + str(body)}")
        bad = client.get("/cheapest", params={**cases[1]["input"], "requested_quantity": 0})
        print(f"qty=0  {bad.status_code}  {bad.json()}")


if __name__ == "__main__":
    main()
