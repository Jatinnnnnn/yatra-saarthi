"""Storm replan - outdoor jagahon ko indoor se badalna. Phase 5."""
from app.optimizer import score_poi


def _is_outdoor(p):
    return (p.get("is_indoor") or 0) != 1 and (p.get("is_sheltered") or 0) != 1


def replan_plan(days, pois, intent, weather):
    if (weather.get("condition") or "").upper() != "STORM":
        return days, []

    pool = {p.get("name"): p for p in pois}
    indoor_pool = [p for p in pois if not _is_outdoor(p)]
    used = {item["name"] for d in days for item in d["pois"]}
    changes = []

    for d in days:
        new_pois = []
        for item in d["pois"]:
            p = pool.get(item["name"])
            if p and _is_outdoor(p):
                repl = None
                for cand in sorted(indoor_pool,
                                   key=lambda c: score_poi(c, intent)[0],
                                   reverse=True):
                    if cand.get("name") not in used:
                        repl = cand
                        break
                if repl is None:
                    # koi indoor alternative free nahi -> safety first: cancel
                    changes.append({
                        "day": d["day"],
                        "removed": item["name"],
                        "added": None,
                        "reason_hi": (f"⛈ Storm alert: {item['name']} outdoor hai aur koi "
                                      f"indoor alternative free nahi tha - activity cancel (safety first)"),
                    })
                    continue
                if repl:
                    used.add(repl.get("name"))
                    sc, reasons = score_poi(repl, intent)
                    new_pois.append({
                        "name": repl.get("name"),
                        "category": repl.get("category"),
                        "score": sc,
                        "reasons": reasons + ["indoor swap (storm)"],
                        "entry_cost": repl.get("entry_cost") or 0,
                        "crowd": repl.get("base_crowd_index") or 0,
                    })
                    changes.append({
                        "day": d["day"],
                        "removed": item["name"],
                        "added": repl.get("name"),
                        "reason_hi": (f"⛈ Storm alert: {item['name']} outdoor tha, "
                                      f"isliye {repl.get('name')} (indoor/sheltered) me badla"),
                    })
                    continue
            new_pois.append(item)
        d["pois"] = new_pois
        d["day_cost"] = sum(x.get("entry_cost") or 0 for x in new_pois)
        d["avg_crowd"] = (round(sum(x.get("crowd") or 0 for x in new_pois) / len(new_pois))
                          if new_pois else 0)
    return days, changes