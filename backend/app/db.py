"""SQLite connection + schema. Phase 2."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "yatra.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # rows ko dict jaisa bana deta hai
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
    conn.commit()
    conn.close()