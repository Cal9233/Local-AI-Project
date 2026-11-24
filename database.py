import sqlite3
import csv
from pathlib import Path
from decimal import Decimal

table_schema = Path("schema.sql").read_text()
quotes_dir = Path("data/sample_quotes.csv")

def load_quotes(path):
    with open(path, "r") as file:
        csv_reader = csv.DictReader(file)
        data = []
        i = 2
        for row in csv_reader:
            row['quantity'] = int(row['quantity'])
            row['unit_price'] = int(Decimal(row['unit_price']) * 100)
            row['file_name'] = Path(path).name
            row['row_number'] = i
            i += 1
            data.append(row)
        return data



def create_db(conn):
    cur = conn.cursor()
    cur.executescript(table_schema)


def import_quotes(conn, csv_path):
    quotes = load_quotes(csv_path)
    sql = "INSERT INTO quotes (quote_id, supplier, part_number, quantity, condition, unit_price, currency, sale_basis, file_name, row_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (quote_id, supplier) DO NOTHING"
    for row in quotes:
        conn.cursor().execute(sql, (row["quote_id"], row["supplier"], row["part_number"], row["quantity"], row["condition"], row["unit_price"], row["currency"], row["sale_basis"], row["file_name"], row["row_number"]))
    conn.commit()

def filter_by_part_number_sql(conn, part_number):
    return

def find_cheapest_sql(conn, request):
    select_sql = "SELECT quote_id, unit_price FROM quotes WHERE part_number = ? AND condition = ? AND currency = ? AND sale_basis = ? AND quantity >= ? ORDER BY unit_price, quote_id LIMIT 1"


def main():
    conn = sqlite3.connect("quotes.db")
    create_db(conn)
    import_quotes(conn, quotes_dir)

if __name__ == "__main__":
    main()