import csv

pn = input("Enter part number: ")

with open("./data/sample_quotes.csv", "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    found = False
    value = ''
    for row in csv_reader:
        qty = int(row['quantity'])
        availablity = f"{qty} available" if qty > 0 else "None available"
        match = row['part_number']
        if pn == match:
            print(f"{row['quote_id']}: {row['part_number']}, {row['condition']}, {availablity}, {row['currency']} {row['unit_price']}")
            found = True
    if found == False: 
        print(f"No quotes found for {pn}.")

  