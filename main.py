import csv

def load_quotes(path):
    with open(path, "r") as file:
        csv_reader = csv.DictReader(file)
        data = []
        for row in csv_reader:
            data.append(row)
        return data

def main():
    pn = input("Enter part number: ")
    quotes = load_quotes("./data/sample_quotes.csv")
    found = False
    for row in quotes:
        qty = int(row['quantity'])
        availablity = f"{qty} available" if qty > 0 else "None available"
        match = row['part_number']
        if pn == match:
            print(f"{row['quote_id']}: {row['part_number']}, {row['condition']}, {availablity}, {row['currency']} {row['unit_price']}")
            found = True
    if found == False: 
        print(f"No quotes found for {pn}.")

if __name__ == "__main__":
    main()