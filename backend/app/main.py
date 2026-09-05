from fastapi import FastAPI

from app.db import get_conn, init_db

app = FastAPI(title="YATRA-SAARTHI API")

init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1"}


@app.get("/api/pois")
def list_pois(city: str | None = None):
    conn = get_conn()
    if city:
        rows = conn.execute("SELECT * FROM pois WHERE city = ?", (city,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM pois").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/stats")
def stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM pois").fetchone()[0]
    indoor = conn.execute("SELECT COUNT(*) FROM pois WHERE is_indoor = 1").fetchone()[0]
    avg = conn.execute("SELECT AVG(base_crowd_index) FROM pois").fetchone()[0] or 0
    conn.close()
    return {"total": total, "indoor_count": indoor, "avg_crowd": round(avg, 1)}