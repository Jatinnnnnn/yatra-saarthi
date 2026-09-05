"""CSV padhne wala loader. Phase 1."""
import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "pois.csv"


def to_int(x, default=0):
    try:
        return int(str(x).strip())
    except (ValueError, TypeError):
        return default


def to_float(x, default=None):
    try:
        return float(str(x).strip())
    except (ValueError, TypeError):
        return default


def load_pois():
    pois = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("pois.csv khaali hai ya header missing - file save ki hai kya?")
        reader.fieldnames = [c.strip() for c in reader.fieldnames]
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue
            pois.append({
                "name": name,
                "city": (row.get("city") or "").strip(),
                "district": (row.get("district") or "").strip(),
                "lat": to_float(row.get("lat")),
                "lng": to_float(row.get("lng")),
                "category": (row.get("category") or "").strip(),
                "description_en": (row.get("description_en") or "").strip(),
                "open_time": (row.get("open_time") or "").strip(),
                "close_time": (row.get("close_time") or "").strip(),
                "entry_cost": to_int(row.get("entry_cost")),
                "is_indoor": to_int(row.get("is_indoor")),
                "is_sheltered": to_int(row.get("is_sheltered")),
                "base_crowd_index": to_int(row.get("base_crowd_index")),
                "tags": (row.get("tags") or "").strip(),
            })
    return pois