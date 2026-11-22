import csv
from pathlib import Path 
from decimal import Decimal

file_path = Path(__file__).resolve().parent 
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
        raise ValueError(f"requested_quantity must be a whole number, got {qty!r}")
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