"""SQLite storage: remembers processed invoices to catch duplicates."""

import sqlite3
from pathlib import Path

DEFAULT_DB = "docsentinel.db"


def connect(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    """Open the database and create the table on first use."""
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices (
            vendor_gstin   TEXT NOT NULL,
            invoice_number TEXT NOT NULL,
            file           TEXT,
            decision       TEXT,
            processed_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (vendor_gstin, invoice_number)
        )
        """
    )
    return conn


def seen_invoices(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    """Return every (vendor_gstin, invoice_number) already processed."""
    rows = conn.execute("SELECT vendor_gstin, invoice_number FROM invoices")
    return {(gstin, number) for gstin, number in rows}


def save_invoice(
    conn: sqlite3.Connection,
    vendor_gstin: str,
    invoice_number: str,
    file: str,
    decision: str,
) -> None:
    """Record a processed invoice. A duplicate key is ignored, not saved twice."""
    conn.execute(
        "INSERT OR IGNORE INTO invoices (vendor_gstin, invoice_number, file, decision)"
        " VALUES (?, ?, ?, ?)",
        (vendor_gstin, invoice_number, file, decision),
    )
    conn.commit()
