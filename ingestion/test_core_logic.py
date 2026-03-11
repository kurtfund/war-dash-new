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

from worker import should_filter_alert, KEYWORDS

def test_keywords():
    print("\n--- TESTING KEYWORD FILTERING (PRODUCTION LOGIC) ---")
    
    scenarios = [
        {"text": "Missile strike in Gaza", "source": "OSINT", "expected": True}, # Should NOT be filtered
        {"text": "New pizza restaurant opens in Dubai", "source": "News", "expected": False}, # Should be filtered
        {"text": "IDF intercepts rocket over Tel Aviv", "source": "Military/Gov", "expected": True},
        {"text": "Fashion week starts in Riyadh", "source": "News", "expected": False},
        {"text": "Severe explosion reported in Beirut", "source": "News", "expected": True},
        {"text": "Ramadan crescent moon sighted in Mecca", "source": "News", "expected": False},
        {"text": "Explosion in Kuwait due to gas leak", "source": "News", "expected": True},
        {"text": "Heavy rain and weather forecast for Khartoum, Sudan", "source": "News", "expected": False},
        {"text": "Video support from storks to the campaign of DMD patient", "source": "News", "expected": False},
        {"text": "Partly cloudy and sunny weather will prevail", "source": "News", "expected": False},
        {"text": "Houthi missile strike on vessel in Red Sea", "source": "OSINT", "expected": True}
    ]

    for s in scenarios:
        # should_filter_alert returns (should_reject, reason, type, country)
        should_reject, reason, event_type, country = should_filter_alert(s["text"], s["source"], "")
        # Result is True if it passes (not filtered), False if it is filtered
        result = not should_reject
        status = "✅ PASS" if result == s["expected"] else "❌ FAIL"
        print(f"  {status} | Text: {s['text'][:40]}... Result={'KEEP' if result else 'REJECT'} (Reason: {reason})")

if __name__ == "__main__":
    test_geofencing()
    test_keywords()
