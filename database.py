import csv
import sqlite3
from decimal import Decimal
from pathlib import Path

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

def insert_review_quote(conn, record):
    """Insert one extracted record into review_quotes and commit.

    `record` is a dict whose keys match the review_quotes columns. This function
    stores what it is given; deciding *whether* a record needs review is the
    caller's job (extraction.store_extracted).
    """
    sql = (
        "INSERT INTO review_quotes (supplier, part_number, quantity, condition, price, price_basis, "
        "currency, sale_basis, core_charge, reason, source_file, record_no, source_phrase) "
        "VALUES (:supplier, :part_number, :quantity, :condition, :price, :price_basis, "
        ":currency, :sale_basis, :core_charge, :reason, :source_file, :record_no, :source_phrase) "
        "ON CONFLICT (source_file, record_no) DO NOTHING"
    )
    conn.execute(sql, record)
    conn.commit()


def insert_extracted_quote(conn, record):
    """Insert one rankable extracted quote into `quotes` and commit.

    `record` keys match the quotes columns; unit_price is integer cents.
    Rerun-safe: the same (quote_id, supplier) is stored once.
    """
    sql = (
        "INSERT INTO quotes (quote_id, supplier, part_number, quantity, condition, unit_price, "
        "currency, sale_basis, file_name, row_number, source_phrase) "
        "VALUES (:quote_id, :supplier, :part_number, :quantity, :condition, :unit_price, "
        ":currency, :sale_basis, :file_name, :row_number, :source_phrase) "
        "ON CONFLICT (quote_id, supplier) DO NOTHING"
    )
    conn.execute(sql, record)
    conn.commit()


def filter_by_part_number_sql(conn, part_number):
    sql = "SELECT quote_id, part_number FROM quotes WHERE part_number = ? ORDER BY row_number"
    res = conn.cursor().execute(sql, (part_number,))
    result = [row[0] for row in res.fetchall()]
    return result

def find_cheapest_sql(conn, request):
    where = "WHERE part_number = ? AND condition = ? AND currency = ? AND sale_basis = ? AND quantity >= ?"
    params = (request["part_number"], request["condition"], request["currency"], request["sale_basis"], request["requested_quantity"])
    cur = conn.cursor()

    # Query 1: every eligible quote, in CSV order (traceability).
    eligible_ids = [row[0] for row in cur.execute(f"SELECT quote_id FROM quotes {where} ORDER BY row_number", params).fetchall()]

    # Query 2: the winner — ranking rule (price, then quote_id) lives in SQL.
    best = cur.execute(f"SELECT quote_id, unit_price FROM quotes {where} ORDER BY unit_price, quote_id LIMIT 1", params).fetchone()

    if best is None:
        return {"status": "no_eligible_quote", "eligible_quote_ids": [], "best_quote_id": None, "unit_price": None, "line_total": None}

    best_id, price_cents = best
    unit_price = Decimal(price_cents) / 100
    line_total = unit_price * request["requested_quantity"]
    cents = Decimal("0.01")
    return {"status": "found", "eligible_quote_ids": eligible_ids, "best_quote_id": best_id, "unit_price": str(unit_price.quantize(cents)), "line_total": str(line_total.quantize(cents))}


def main():
    conn = sqlite3.connect("quotes.db")
    create_db(conn)
    import_quotes(conn, quotes_dir)

if __name__ == "__main__":
    main()