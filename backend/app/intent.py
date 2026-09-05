"""Natural language -> intent (rule-based). Phase 3."""
import re

KEYWORDS = {
    "adventure": ["adventure", "rafting", "trek", "bungee", "thrill", "kayak",
                  "camping", "saahasik", "ट्रेक", "राफ्टिंग"],
    "nature": ["nature", "scenic", "waterfall", "jungle", "forest", "view",
               "sunset", "sunrise", "प्रकृति", "पहाड़"],
    "temple": ["temple", "mandir", "aarti", "darshan", "pooja", "spiritual",
               "मंदिर", "आरती", "दर्शन"],
    "food": ["food", "cafe", "restaurant", "thali", "khana", "खाना", "थाली"],
    "shopping": ["shopping", "market", "bazaar", "handicraft", "बाज़ार", "खरीदारी"],
    "wellness": ["yoga", "ayurveda", "meditation", "spa", "योग", "ध्यान"],
    "culture": ["museum", "heritage", "culture", "art", "संग्रहालय"],
    "family": ["family", "kids", "children", "bachche", "परिवार", "बच्चे"],
}

# LOW pehle check hota hai - isliye "hate crowds" jaisi lines HIGH me nahi girti
CROWD_LOW = ["kam bheed", "bheed kam", "low crowd", "quiet", "shant", "शांत",
             "peaceful", "offbeat", "not crowded", "avoid crowd",
             "hate crowd", "bheed pasand nahi", "bheed nahi", "कम भीड़"]
CROWD_HIGH = ["crowded", "busy", "popular", "famous", "bheed wala", "लोकप्रिय", "मशहूर"]

DISTRICTS = {
    "Dehradun": ["rishikesh", "dehradun", "mussoorie", "ऋषिकेश", "देहरादून", "मसूरी"],
    "Haridwar": ["haridwar", "har ki pauri", "हरिद्वार", "हर की पौड़ी"],
    "Nainital": ["nainital", "naini", "भीमताल"],
    "Tehri": ["tehri", "new tehri"],
}


def parse_intent(query: str) -> dict:
    s = (query or "").lower()

    interests = [tag for tag, words in KEYWORDS.items() if any(w in s for w in words)]
    if not interests:
        interests = ["nature", "temple"]

    if any(w in s for w in CROWD_LOW):
        crowd = "LOW"
    elif any(w in s for w in CROWD_HIGH):
        crowd = "HIGH"
    else:
        crowd = "MEDIUM"

    days = 3
    m = re.search(r"(\d+)\s*[-\s]?(?:din|days?|day|दिन)", s)
    if m:
        days = int(m.group(1))

    budget = 15000
    m = re.search(r"₹\s*([\d,]+)", s)
    if m:
        budget = int(m.group(1).replace(",", ""))
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:k|हजार|hazaar|thousand)", s)
        if m:
            budget = int(float(m.group(1)) * 1000)
        else:
            m = re.search(r"(\d{4,7})\s*(?:ka\s+|ke\s+)?(?:budget|rupaye|rupay|rs\.?|mein|me\b)", s)
            if not m:
                m = re.search(r"(?:budget|mein|me)\s*(?:₹\s*)?(\d{4,7})", s)
            if m:
                budget = int(m.group(1))

    travelers = 2
    m = re.search(r"(\d+)\s*(?:log|logo|people|persons?|friends?|jan|लोग)", s)
    if m:
        travelers = int(m.group(1))
    if "solo" in s or "akela" in s:
        travelers = 1
    if "couple" in s or "jodi" in s:
        travelers = 2

    district = "Dehradun"
    for d, words in DISTRICTS.items():
        if any(w in s for w in words):
            district = d
            break

    stay = "ANY"
    if "homestay" in s or "होमस्टे" in s:
        stay = "HOMESTAY"
    elif "hotel" in s or "resort" in s:
        stay = "HOTEL"

    food = "ANY"
    if "non-veg" in s or "nonveg" in s:
        food = "NONVEG"
    elif "veg" in s:
        food = "VEG"

    return {
        "num_days": days,
        "num_travelers": travelers,
        "total_budget": budget,
        "interests": interests,
        "crowd_preference": crowd,
        "destination_district": district,
        "stay_preference": stay,
        "food_preference": food,
        "parse_source": "RULE_BASED",
        "confidence": 0.8,
        "raw_query": query,
    }