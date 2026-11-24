CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id TEXT NOT NULL,
    supplier TEXT NOT NULL,
    part_number TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (typeof(quantity) = 'integer' AND quantity > 0),
    condition TEXT NOT NULL CHECK (condition IN ('OH', 'SV', 'NE')),
    unit_price INTEGER NOT NULL CHECK (typeof(unit_price) = 'integer' AND unit_price > 0),
    currency TEXT NOT NULL CHECK (currency IN ('USD', 'EUR')),
    sale_basis TEXT NOT NULL CHECK (sale_basis IN ('EXCHANGE', 'OUTRIGHT')),
    file_name TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    quote_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(quote_id, supplier)
)