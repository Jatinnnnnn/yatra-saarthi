"""Intent parser ke tests. Chalao:  python tests/test_intent.py   (backend/ se)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.intent import parse_intent  # noqa: E402

CASES = [
    ("4 din rishikesh me 20000 budget", "num_days", 4),
    ("4 din rishikesh me 20000 budget", "total_budget", 20000),
    ("20k budget hai", "total_budget", 20000),
    ("hum 6 log jaayenge", "num_travelers", 6),
    ("solo trip", "num_travelers", 1),
    ("bheed pasand nahi hai", "crowd_preference", "LOW"),
    ("we hate crowds", "crowd_preference", "LOW"),
    ("popular famous spots dikha do", "crowd_preference", "HIGH"),
    ("normal trip karo", "crowd_preference", "MEDIUM"),
    ("haridwar me ganga aarti", "destination_district", "Haridwar"),
    ("mussoorie trip", "destination_district", "Dehradun"),
    ("rafting trekking karni hai", "interests", ["adventure"]),
    ("mandir darshan karna hai", "interests", ["temple"]),
    ("homestay me rehna hai", "stay_preference", "HOMESTAY"),
    ("pure veg food", "food_preference", "VEG"),
]

fail = 0
for query, field, expected in CASES:
    got = parse_intent(query).get(field)
    if got == expected:
        print(f"  OK  {query!r:42s} {field} = {got!r}")
    else:
        fail += 1
        print(f"  FAIL {query!r:42s} {field}: got {got!r}, want {expected!r}")

print(f"\n{len(CASES) - fail}/{len(CASES)} passed")
sys.exit(1 if fail else 0)