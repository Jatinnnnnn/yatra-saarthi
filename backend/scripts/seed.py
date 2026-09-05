"""CSV -> SQLite. Phase 6 (pois + businesses). Chalao: python -m scripts.seed"""
import csv
from pathlib import Path

from app.db import get_conn, init_db
from app.data_loader import load_pois

BIZ_CSV = Path(__file__).resolve().parent.parent / "data" / "businesses.csv"


def seed():
    init_db()
    conn = get_conn()

    conn.execute("DELETE FROM pois")
    n = 0
    for p in load_pois():
        conn.execute("""
            INSERT INTO pois (name, city, district, lat, lng, category,
                              description_en, open_time, close_time, entry_cost,
                              is_indoor, is_sheltered, base_crowd_index, tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            p.get("name"), p.get("city"), p.get("district"), p.get("lat"),
            p.get("lng"), p.get("category"), p.get("description_en"),
            p.get("open_time"), p.get("close_time"), p.get("entry_cost"),
            p.get("is_indoor"), p.get("is_sheltered"),
            p.get("base_crowd_index"), p.get("tags"),
        ))
        n += 1

    m = 0
    if BIZ_CSV.exists():
        conn.execute("DELETE FROM businesses")
        with open(BIZ_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if not (r.get("name") or "").strip():
                    continue
                conn.execute("""
                    INSERT INTO businesses (name, type, city, district, price_min,
                                            price_max, price_unit, rating, is_indoor,
                                            tags, description_en)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    r["name"].strip(), (r.get("type") or "").strip(),
                    (r.get("city") or "").strip(), (r.get("district") or "").strip(),
                    float(r.get("price_min") or 0), float(r.get("price_max") or 0),
                    (r.get("price_unit") or "").strip(), float(r.get("rating") or 0),
                    int(r.get("is_indoor") or 0), (r.get("tags") or "").strip(),
                    (r.get("description_en") or "").strip(),
                ))
                m += 1

    conn.commit()
    conn.close()
    print(f"[seed] {n} POIs + {m} businesses -> yatra.db")


if __name__ == "__main__":
    seed()