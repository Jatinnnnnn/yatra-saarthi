"""YATRA-SAARTHI API - main file (Phases 0-6 complete)."""
from fastapi import FastAPI
from pydantic import BaseModel

from app.db import get_conn, init_db
from app.intent import parse_intent
from app.optimizer import recommend, pack_days
from app.replan import replan_plan
from app.weather import get_weather, set_storm, clear as clear_weather

app = FastAPI(title="YATRA-SAARTHI API")

init_db()


# ── Phase 0: health ──────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.6"}


# ── Phase 2: data DB se ──────────────────────────────────────
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


# ── Phase 3: intent parser ───────────────────────────────────
class QueryIn(BaseModel):
    query: str


@app.post("/api/parse")
def parse(q: QueryIn):
    return parse_intent(q.query)


# ── Phase 4: scoring + planning ──────────────────────────────
@app.get("/api/recommend")
def recommend_endpoint(query: str, top: int = 5):
    pois = _all_pois()
    intent = parse_intent(query)
    return {"intent": intent, "top_picks": recommend(pois, intent, top)}


def _all_pois():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM pois").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _all_businesses():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM businesses").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/plan")
def plan(query: str):
    pois = _all_pois()
    intent = parse_intent(query)
    pool = [p for p in pois if (p.get("district") or "") == intent.get("destination_district")]
    days, total_cost = pack_days(pool, intent)

    weather = get_weather()
    changes = []
    if weather["condition"] == "STORM":
        days, changes = replan_plan(days, pool, intent, weather)
        total_cost = sum(d["day_cost"] for d in days)

    # local business booster: har plan me 3 local suggestions
    businesses = _all_businesses()
    bpool = [b for b in businesses if b.get("district") == intent.get("destination_district")] or businesses
    suggested = []
    for btype in ("HOMESTAY", "WORKSHOP", "RESTAURANT"):
        pick = next((b for b in bpool if b.get("type") == btype), None)
        if pick:
            suggested.append(pick)

    return {
        "intent": intent,
        "weather": weather,
        "days": days,
        "total_cost": total_cost,
        "budget": intent.get("total_budget"),
        "within_budget": total_cost <= (intent.get("total_budget") or 0),
        "replan_changes": changes,
        "explanation_hi": (f"⛈ आंधी-तूफ़ान की चेतावनी: {len(changes)} गतिविधियाँ इनडोर बदली गईं"
                           if changes else ""),
        "suggested_businesses": suggested[:3],
    }


# ── Phase 5: weather sim ─────────────────────────────────────
@app.get("/api/weather")
def weather():
    return get_weather()


@app.post("/api/sim/storm")
def sim_storm(district: str = "Dehradun"):
    return set_storm(district)


@app.post("/api/sim/clear")
def sim_clear():
    return clear_weather()


# ── Phase 6: businesses + bookings + analytics ───────────────
class BookingIn(BaseModel):
    business_name: str
    amount: float


@app.get("/api/businesses")
def list_businesses(district: str | None = None):
    conn = get_conn()
    if district:
        rows = conn.execute("SELECT * FROM businesses WHERE district = ?", (district,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM businesses").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/bookings")
def book(b: BookingIn):
    conn = get_conn()
    row = conn.execute("SELECT * FROM businesses WHERE name = ?", (b.business_name,)).fetchone()
    if not row:
        conn.close()
        return {"error": f"business nahi mila: {b.business_name}"}
    fee = round(b.amount * 0.04, 2)      # 4% platform
    local = round(b.amount - fee, 2)     # 96% seedha local ko
    conn.execute("INSERT INTO bookings (business_name, amount, platform_fee, local_share) VALUES (?,?,?,?)",
                 (b.business_name, b.amount, fee, local))
    conn.commit()
    conn.close()
    return {"business": b.business_name, "amount": b.amount,
            "platform_fee": fee, "local_share": local,
            "message_hi": f"₹{local} seedha local business ko mila"}


@app.get("/api/admin/analytics")
def analytics():
    conn = get_conn()
    tot = conn.execute("SELECT COUNT(*), COALESCE(SUM(amount),0), COALESCE(SUM(platform_fee),0), COALESCE(SUM(local_share),0) FROM bookings").fetchone()
    top = conn.execute("SELECT business_name, SUM(amount) AS rev FROM bookings GROUP BY business_name ORDER BY rev DESC LIMIT 5").fetchall()
    conn.close()
    return {"total_bookings": tot[0], "gross_revenue": tot[1],
            "platform_fee": tot[2], "local_revenue": tot[3],
            "top_businesses": [dict(r) for r in top],
            "tagline": "Every trip we replan is a crowd we redistribute and a rupee we move from an OTA to a local."}