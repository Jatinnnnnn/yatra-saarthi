"""CSV ki safai check karta hai. Chalao:  python -m scripts.validate_data"""
import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "pois.csv"
CITIES = {"Rishikesh", "Haridwar", "Dehradun", "Mussoorie", "Nainital", "Tehri", "Other"}
CATEGORIES = {"TEMPLE", "NATURE", "ADVENTURE", "MUSEUM", "SHOPPING",
              "VIEWPOINT", "CULTURAL", "WELLNESS", "LANDMARK", "FOOD"}
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def main():
    errors = []
    seen = set()
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):   # row 2 = pehli data row
            name = (r.get("name") or "").strip()
            if not name:
                errors.append(f"row {i}: name khaali hai")
                continue
            if name in seen:
                errors.append(f"row {i}: duplicate name '{name}'")
            seen.add(name)

            if (r.get("city") or "").strip() not in CITIES:
                errors.append(f"row {i}: galat city '{r.get('city')}'")
            if (r.get("category") or "").strip() not in CATEGORIES:
                errors.append(f"row {i}: galat category '{r.get('category')}'")

            for col, lo, hi in (("lat", 28.5, 31.5), ("lng", 77.5, 81.5)):
                v = (r.get(col) or "").strip()
                try:
                    if not (lo <= float(v) <= hi):
                        errors.append(f"row {i}: {col} Uttarakhand se bahar: {v}")
                except ValueError:
                    errors.append(f"row {i}: {col} number nahi hai: '{v}'")

            for col in ("open_time", "close_time"):
                v = (r.get(col) or "").strip()
                if not TIME_RE.match(v):
                    errors.append(f"row {i}: {col} HH:MM format nahi: '{v}'")

            for col in ("is_indoor", "is_sheltered"):
                if (r.get(col) or "").strip() not in ("0", "1"):
                    errors.append(f"row {i}: {col} sirf 0/1: '{r.get(col)}'")

            cost = (r.get("entry_cost") or "").strip()
            if cost and not cost.isdigit():
                errors.append(f"row {i}: entry_cost number nahi: '{cost}'")

            crowd = (r.get("base_crowd_index") or "").strip()
            if not (crowd.isdigit() and 0 <= int(crowd) <= 100):
                errors.append(f"row {i}: base_crowd_index 0-100 nahi: '{crowd}'")

            if not (r.get("tags") or "").strip():
                errors.append(f"row {i}: tags khaali")

    if errors:
        print(f"❌ {len(errors)} galtiyan mili — seed mat karo:")
        for e in errors:
            print("  ", e)
        sys.exit(1)
    print("✅ CSV saaf hai — ab seed kar sakte ho")


if __name__ == "__main__":
    main()