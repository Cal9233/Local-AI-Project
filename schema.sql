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
    -- Source: CSV file + row, or email file + record number within that email.
    file_name TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    -- Exact text from an email supporting the price; NULL for CSV rows.
    source_phrase TEXT,
    quote_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(quote_id, supplier)
);

-- Extracted records that must not be ranked (missing currency, price, condition,
-- or an unverifiable price phrase). Values are kept exactly as extracted; price is
-- a decimal string because a review record may have no unit price to convert to cents.
CREATE TABLE IF NOT EXISTS review_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier TEXT NOT NULL,
    part_number TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (typeof(quantity) = 'integer' AND quantity > 0),
    condition TEXT CHECK (condition IN ('OH', 'SV', 'NE')),
    price TEXT,
    price_basis TEXT NOT NULL CHECK (price_basis IN ('PER_UNIT', 'LOT')),
    currency TEXT,
    sale_basis TEXT NOT NULL CHECK (sale_basis IN ('EXCHANGE', 'OUTRIGHT')),
    core_charge TEXT,
    reason TEXT NOT NULL,
    source_file TEXT NOT NULL,
    record_no INTEGER NOT NULL,
    source_phrase TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_file, record_no)
);
