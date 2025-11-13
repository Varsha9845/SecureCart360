#!/usr/bin/env python3
"""
SecureCart360 data loader.

Creates/overwrites ecommerce.db, builds normalized tables with foreign keys,
imports CSV data from ./data/, records an audit entry, and prints summary stats.

Usage:
    python scripts/load_into_sqlite.py
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

DATA_DIR = Path("data")
DB_PATH = Path("ecommerce.db")

CSV_FILES = {
    "customers": DATA_DIR / "customers.csv",
    "products": DATA_DIR / "products.csv",
    "orders": DATA_DIR / "orders.csv",
    "order_items": DATA_DIR / "order_items.csv",
    "fraud_signals": DATA_DIR / "fraud_signals.csv",
}


def ensure_csvs_exist() -> None:
    missing = [path for path in CSV_FILES.values() if not path.exists()]
    if missing:
        print("ERROR: Missing CSV files:")
        for path in missing:
            print(f"  - {path}")
        sys.exit(1)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS audit_log;
        DROP TABLE IF EXISTS fraud_signals;
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            country TEXT NOT NULL,
            loyalty_tier TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            sku TEXT NOT NULL
        );

        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            order_total REAL NOT NULL,
            payment_method TEXT NOT NULL,
            order_status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE fraud_signals (
            order_id TEXT PRIMARY KEY,
            ip_country TEXT NOT NULL,
            billing_country TEXT NOT NULL,
            device_change_flag INTEGER NOT NULL,
            high_value_flag INTEGER NOT NULL,
            payment_risk_score REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            detail TEXT
        );
        """
    )


def load_csv(conn: sqlite3.Connection, table_name: str, csv_path: Path) -> None:
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError(f"CSV {csv_path} has no header row")
        columns = reader.fieldnames
        placeholders = ",".join("?" for _ in columns)
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        rows = []
        for row in reader:
            rows.append([(None if value == "" else value) for value in (row[col] for col in columns)])

        if rows:
            conn.executemany(insert_sql, rows)


def insert_audit_log(conn: sqlite3.Connection) -> None:
    detail = f"Loaded CSVs: {', '.join(path.name for path in CSV_FILES.values())}"
    conn.execute(
        "INSERT INTO audit_log(action, timestamp, detail) VALUES (?, ?, ?)",
        ("load_into_sqlite", datetime.utcnow().isoformat(), detail),
    )


def print_metrics(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    tables = ["customers", "products", "orders", "order_items", "fraud_signals", "audit_log"]
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count}")

    total_revenue = cursor.execute("SELECT ROUND(SUM(order_total), 2) FROM orders").fetchone()[0]
    avg_order_value = cursor.execute("SELECT ROUND(AVG(order_total), 2) FROM orders").fetchone()[0]
    print(f"total_revenue: {total_revenue or 0:.2f}")
    print(f"avg_order_value: {avg_order_value or 0:.2f}")


def main() -> None:
    ensure_csvs_exist()

    if DB_PATH.exists():
        print(f"Removing existing database: {DB_PATH}")
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        create_schema(conn)

        print("Loading CSV data...")
        load_csv(conn, "customers", CSV_FILES["customers"])
        load_csv(conn, "products", CSV_FILES["products"])
        load_csv(conn, "orders", CSV_FILES["orders"])
        load_csv(conn, "order_items", CSV_FILES["order_items"])
        load_csv(conn, "fraud_signals", CSV_FILES["fraud_signals"])
        insert_audit_log(conn)

        conn.commit()

        print("Summary:")
        print_metrics(conn)

    print(f"Database created at {DB_PATH.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
