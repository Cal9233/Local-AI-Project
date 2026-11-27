import csv
from decimal import Decimal
from pathlib import Path

file_path = Path(__file__).resolve().parent.parent  # project root
file_dir = file_path / "data" / "sample_quotes.csv"

def load_quotes(path):
    with open(path, "r") as file:
        csv_reader = csv.DictReader(file)
        data = []
        for row in csv_reader:
            row['quantity'] = int(row['quantity'])
            row['unit_price'] = Decimal(row['unit_price'])
            data.append(row)
        return data

def filter_by_part_number(quotes, part_number):
    result = []
    for q in quotes:
        if part_number == q["part_number"]:
            result.append(q["quote_id"])
    return result

def validate_request(request):
    qty = request["requested_quantity"]
    if not isinstance(qty, int):
        raise TypeError(f"requested_quantity must be a whole number, got {qty!r}")
    if qty < 1:
        raise ValueError(f"requested_quantity must be at least 1, got {qty}")

def is_eligible(quote, request):
    result = False
    if (
        quote["part_number"] == request["part_number"]
        and quote["condition"] == request["condition"]
        and quote["currency"] == request["currency"]
        and quote["sale_basis"] == request["sale_basis"]
        and quote["quantity"] >= int(request["requested_quantity"])
    ):
        result = True
    return result

def find_eligible(quotes, request):
    validate_request(request)
    result = []
    for q in quotes:
        if is_eligible(q, request):
            result.append(q["quote_id"])
    return result

def eligible_quotes(quotes, request):
    validate_request(request)
    result = []
    for q in quotes:
        if is_eligible(q, request):
            result.append(q)
    return result

def price_then_id(q):
    return (q["unit_price"], q["quote_id"])

def find_cheapest_eligible_quote(quotes, request):
    q_rows = eligible_quotes(quotes, request)
    if len(q_rows) == 0:
        return {"status": "no_eligible_quote", "eligible_quote_ids": [], "best_quote_id": None, "unit_price": None, "line_total": None}
    best = min(q_rows, key=price_then_id)
    line_total = best["unit_price"] * request["requested_quantity"]
    return {"status": "found", "eligible_quote_ids": [i["quote_id"] for i in q_rows], "best_quote_id": best["quote_id"], "unit_price": str(best["unit_price"].quantize(Decimal("0.01"))), "line_total": str(line_total.quantize(Decimal("0.01")))}

def main():
    pn = input("Enter part number: ")
    quotes = load_quotes(file_dir)
    found = False
    for row in quotes:
        match = row['part_number']
        availability = f"{row['quantity']} available" if row['quantity'] > 0 else "None available"
        if pn == match:
            print(f"{row['quote_id']}: {row['part_number']}, {row['condition']}, {availability}, {row['currency']} {row['unit_price']}")
            found = True
    if found == False: 
        print(f"No quotes found for {pn}.")

if __name__ == "__main__":
    main()