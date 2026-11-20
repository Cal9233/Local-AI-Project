import csv
from pathlib import Path 
from decimal import Decimal

file_path = Path(__file__).resolve().parent 
file = file_path / "data" / "sample_quotes"

def load_quotes(path):
    with open(path, "r") as file:
        csv_reader = csv.DictReader(file)
        data = []
        for row in csv_reader:
            row['quantity'] = int(row['quantity'])
            row['unit_price'] = Decimal(row['unit_price'])
            data.append(row)
        return data

def main():
    pn = input("Enter part number: ")
    quotes = load_quotes(file_path)
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