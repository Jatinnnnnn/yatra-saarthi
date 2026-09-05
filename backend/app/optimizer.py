"""Plan banana - Part A: POIs ko score karna + reason dena. Phase 4.
   Part B (dinon me packing) isi file me aage judhega."""


def _tags(poi):
    return [t.strip().lower() for t in (poi.get("tags") or "").split(",") if t.strip()]


def score_poi(poi, intent):
    """Ek POI ko intent ke hisaab se score + reasons deta hai."""
    score = 0
    reasons = []

    # 1) interest match - sabse bada weight
    cat = (poi.get("category") or "").lower()
    tags = _tags(poi)
    matched = [i for i in intent.get("interests", []) if i == cat or i in tags]
    if matched:
        score += 50
        reasons.append(f"interest match: {', '.join(matched)}")

    # 2) crowd preference
    crowd = poi.get("base_crowd_index") or 0
    pref = (intent.get("crowd_preference") or "MEDIUM").upper()
    if pref == "LOW":
        score += (100 - crowd) // 2
        if crowd <= 40:
            reasons.append(f"quiet spot (crowd {crowd}/100)")
    elif pref == "HIGH":
        score += crowd // 2
        if crowd >= 70:
            reasons.append(f"popular spot (crowd {crowd}/100)")
    else:
        score += 25

    return score, reasons


def recommend(pois, intent, top=5):
    """District filter -> score -> sort -> top N."""
    pool = [p for p in pois
            if (p.get("district") or "") == intent.get("destination_district")]
    out = []
    for p in pool:
        sc, reasons = score_poi(p, intent)
        out.append({
            "name": p.get("name"),
            "city": p.get("city"),
            "score": sc,
            "reasons": reasons,
            "entry_cost": p.get("entry_cost") or 0,
            "crowd": p.get("base_crowd_index") or 0,
        })
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:top]

# ─────────────────────────────────────────────
# Part B: scored POIs ko dinon me pack karna
# ─────────────────────────────────────────────
from collections import Counter

MAX_PER_DAY = 3


def pack_days(pois, intent):
    days_n = intent.get("num_days") or 3
    budget = intent.get("total_budget") or 15000
    per_day = budget // days_n          # har din ka budget hissa

    scored = []
    for p in pois:
        sc, reasons = score_poi(p, intent)
        scored.append((sc, p, reasons))
    scored.sort(key=lambda x: x[0], reverse=True)   # best pehle

    days, total_cost, idx = [], 0, 0
    for d in range(1, days_n + 1):
        day_pois, day_cost = [], 0
        while idx < len(scored) and len(day_pois) < MAX_PER_DAY:
            sc, p, reasons = scored[idx]
            idx += 1
            cost = p.get("entry_cost") or 0
            if day_cost + cost > per_day:
                continue                # aaj ke budget me nahi samaya -> chhoda
            day_pois.append({
                "name": p.get("name"),
                "category": p.get("category"),
                "score": sc,
                "reasons": reasons,
                "entry_cost": cost,
                "crowd": p.get("base_crowd_index") or 0,
            })
            day_cost += cost
        theme = (Counter(x["category"].title() for x in day_pois).most_common(1)[0][0]
                 if day_pois else "Rest / free exploration")
        days.append({
            "day": d,
            "theme": theme,
            "pois": day_pois,
            "day_cost": day_cost,
            "avg_crowd": round(sum(x["crowd"] for x in day_pois) / len(day_pois)) if day_pois else 0,
        })
        total_cost += day_cost
    return days, total_cost