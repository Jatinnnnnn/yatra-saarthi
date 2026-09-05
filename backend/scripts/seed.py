"""CSV → SQLite. Chalao:  python -m scripts.seed   (backend/ folder se)"""
from app.db import get_conn, init_db
from app.data_loader import load_pois     # tumhara Phase 1 wala loader


def seed():
    init_db()
    pois = load_pois()
    conn = get_conn()
    conn.execute("DELETE FROM pois")      # purana data saaf → fresh start
    n = 0
    for p in pois:
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
    conn.commit()
    conn.close()
    print(f"[seed] {n} POIs database me daal diye → yatra.db")


if __name__ == "__main__":
    seed()