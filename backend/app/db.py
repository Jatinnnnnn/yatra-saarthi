"""SQLite connection + schema. Phase 6 (pois + businesses + bookings)."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "yatra.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pois (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL UNIQUE,
            city             TEXT NOT NULL,
            district         TEXT,
            lat              REAL,
            lng              REAL,
            category         TEXT,
            description_en   TEXT,
            open_time        TEXT,
            close_time       TEXT,
            entry_cost       INTEGER DEFAULT 0,
            is_indoor        INTEGER DEFAULT 0,
            is_sheltered     INTEGER DEFAULT 0,
            base_crowd_index INTEGER DEFAULT 0,
            tags             TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL UNIQUE,
            type           TEXT,
            city           TEXT,
            district       TEXT,
            price_min      REAL,
            price_max      REAL,
            price_unit     TEXT,
            rating         REAL,
            is_indoor      INTEGER DEFAULT 0,
            tags           TEXT,
            description_en TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            amount        REAL NOT NULL,
            platform_fee  REAL,
            local_share   REAL,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()