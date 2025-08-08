-- This schema creates the tables managed by the Python API server itself.
-- It does not include the tables from the main ERP database.

CREATE TABLE IF NOT EXISTS quote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_call_id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    description TEXT,
    customer_name TEXT,
    status TEXT,
    tech_count INTEGER,
    tech_hours REAL,
    travel_hours REAL,
    tech_rate REAL,
    travel_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_call_id, revision)
);

CREATE TABLE IF NOT EXISTS quote_line_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    part_number TEXT,
    description TEXT,
    vendor TEXT,
    on_hand TEXT,
    quantity INTEGER,
    unit_cost REAL,
    total_cost REAL,
    FOREIGN KEY (quote_id) REFERENCES quote (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subcontractor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    contact_name TEXT,
    contact_details TEXT,
    cost REAL,
    FOREIGN KEY (quote_id) REFERENCES quote (id) ON DELETE CASCADE
);