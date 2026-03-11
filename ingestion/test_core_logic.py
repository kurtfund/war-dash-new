import json
import os
import sys

# Add the current directory to sys.path to allow importing worker
sys.path.append(os.path.dirname(__file__))

def test_geofencing():
    print("\n--- TESTING GEOFENCING ---")
    
    # Load bounds from keywords.json
    keywords_path = os.path.join(os.path.dirname(__file__), "keywords.json")
    with open(keywords_path, "r") as f:
        config = json.load(f)
    
    bounds = config["GEOGRAPHIC_BOUNDS"]
    lat_min, lat_max = bounds["lat"]
    lon_min, lon_max = bounds["lon"]

    def is_within_bounds(lat, lon):
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

    scenarios = [
        {"name": "Tel Aviv", "lat": 32.0853, "lon": 34.7818, "expected": True},
        {"name": "Dubai", "lat": 25.2048, "lon": 55.2708, "expected": True},
        {"name": "Tehran", "lat": 35.6892, "lon": 51.3890, "expected": True},
        {"name": "Baghdad", "lat": 33.3152, "lon": 44.3661, "expected": True},
        {"name": "Cairo (Exclusion Test)", "lat": 30.0444, "lon": 31.2357, "expected": False},
        {"name": "Khartoum (Exclusion Test)", "lat": 15.5007, "lon": 32.5599, "expected": False},
        {"name": "Lagos (Exclusion Test)", "lat": 6.5244, "lon": 3.3792, "expected": False},
        {"name": "Suez Canal (Borderline Pass)", "lat": 29.9668, "lon": 32.5498, "expected": False}, # lon < 34
        {"name": "Eilat (Borderline Pass)", "lat": 29.5577, "lon": 34.9519, "expected": True}
    ]

    for s in scenarios:
        result = is_within_bounds(s["lat"], s["lon"])
        status = "✅ PASS" if result == s["expected"] else "❌ FAIL"
        print(f"  {status} | {s['name']}: Result={result}, Expected={s['expected']}")

def test_keywords():
    print("\n--- TESTING KEYWORD FILTERING ---")
    keywords_path = os.path.join(os.path.dirname(__file__), "keywords.json")
    with open(keywords_path, "r") as f:
        config = json.load(f)
    
    conflict = [k.lower() for k in config["CONFLICT_KEYWORDS"]]
    banned = [k.lower() for k in config["BANNED_KEYWORDS"]]

    def filter_check(text):
        text_lower = text.lower()
        has_conflict = any(k in text_lower for k in conflict)
        has_banned = any(k in text_lower for k in banned)
        return has_conflict and not has_banned

    scenarios = [
        {"text": "Missile strike in Gaza", "expected": True},
        {"text": "New pizza restaurant opens in Dubai", "expected": False},
        {"text": "IDF intercepts rocket over Tel Aviv", "expected": True},
        {"text": "Fashion week starts in Riyadh", "expected": False},
        {"text": "Severe explosion reported in Beirut", "expected": True},
        {"text": "Ramadan crescent moon sighted in Mecca", "expected": False},
        {"text": "Explosion in Kuwait due to gas leak", "expected": True}, # Still conflict/event of interest
    ]

    for s in scenarios:
        result = filter_check(s["text"])
        status = "✅ PASS" if result == s["expected"] else "❌ FAIL"
        print(f"  {status} | Text: {s['text'][:40]}... Result={result}")

if __name__ == "__main__":
    test_geofencing()
    test_keywords()
