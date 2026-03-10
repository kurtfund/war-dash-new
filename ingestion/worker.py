import os
import json
import hashlib
import feedparser
import requests
import re
import spacy
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

load_dotenv()

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Middle East Bounding Box
BOUNDS = {
    "lat": (12, 42),
    "lon": (25, 65)
}

# --- DATA SOURCES ---
RSS_SOURCES = {
    "News": [
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.reuters.com/rssFeed/middleEast",
        "https://www.middleeasteye.net/rss",
        "https://www.timesofisrael.com/feed",
        "https://www.arabnews.com/rss",
        "https://www.haaretz.com/cmlink/1.640383",
        "https://www.thenationalnews.com/feeds/all-news.xml",
        "https://www.dailysabah.com/rss",
        "https://gulfnews.com/rss",
        "https://jordantimes.com/rss",
        "https://www.egypttoday.com/rss",
        "https://www.al-monitor.com/rss",
        "https://english.aawsat.com/rss.xml",
        "https://www.jpost.com/Rss",
        "https://www.aa.com.tr/en/rss",
        "https://www.kuwaittimes.com/feed/",
        "https://www.saudigazette.com.sa/rss",
        "https://www.qatar-tribune.com/feed/",
        "http://www.bna.bh/rss"
    ],
    "Military/Gov": [
        "https://www.idf.il/en/rss",
        "https://www.centcom.mil/News/News-RSS/",
        "https://www.mdn.ir/rss.xml",
        "https://www.mod.gov.sa/en/rss",
        "https://www.mofaic.gov.ae/rss",
        "https://www.tsk.tr/Feed",
        "http://www.jaf.mil.jo/rss",
        "http://www.mod.gov.om/rss",
        "http://www.palestine.ps/rss",
        "http://www.mod.gov.eg/rss",
        "https://www.mod.gov.qa/rss",
        "http://www.mod.gov.kw/rss",
        "http://www.mod.gov.bh/rss",
        "http://www.lebmod.gov.lb/rss",
        "http://www.mod.gov.ye/rss",
        "http://www.mod.mil.iq/rss"
    ],
    "OSINT": [
        "https://liveuamap.com/rss?region=middleeast",
        "http://syriahr.com/en/rss",
        "http://iraqsecuritywatch.com/rss",
        "http://yemenconflict.net/rss"
    ]
}

API_SOURCES = {
    "Disaster": [
        {"name": "USGS Earthquakes", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson", "type": "geojson_earthquake"},
        {"name": "NASA FIRMS Fires", "url": "https://firms.modaps.eosdis.nasa.gov/active_fire/geojson/z/1", "type": "geojson_fire"},
        {"name": "GDACS Disasters", "url": "https://www.gdacs.org/gdacsapi/api/events/geteventlist.geojson", "type": "geojson_generic"}
    ]
}

# Source Reliability Scoring
SOURCE_RELIABILITY = {
    "gov": 0.95,
    "mil": 0.95,
    "reuters": 0.90,
    "ap": 0.90,
    "aljazeera": 0.85,
    "haaretz": 0.85,
    "jpost": 0.85,
    "timesofisrael": 0.85,
    "middleeasteye": 0.75,
    "liveuamap": 0.70,
    "twitter": 0.40,
    "x.com": 0.40
}

# --- LOAD RESOURCES ---
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Warning: spaCy model not found. Attempting to download...")
    try:
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None

geolocator = Nominatim(user_agent="war_dash_osint_v2")

KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "keywords.json")
try:
    with open(KEYWORDS_PATH, "r") as f:
        KEYWORDS = json.load(f)
except:
    KEYWORDS = {"event_types": {}, "countries": {}}

# --- UTILITIES ---

def is_within_bounds(lat: float, lon: float) -> bool:
    if lat is None or lon is None: return False
    lat_min, lat_max = BOUNDS["lat"]
    lon_min, lon_max = BOUNDS["lon"]
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def get_source_confidence(url: str) -> float:
    url_lower = url.lower()
    for key, score in SOURCE_RELIABILITY.items():
        if key in url_lower:
            return score
    return 0.60 

def extract_casualties(text: str) -> int:
    patterns = [
        r'(\d+)\s+(?:killed|dead|fatalities|casualties|deadly)',
        r'(?:killed|dead|fatalities|casualties)\s+(?:of\s+)?(\d+)',
        r'death\s+toll\s+(?:reaches|of|is)\s+(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0

def detect_location(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not nlp: return None, None
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    for loc_name in entities:
        if loc_name in KEYWORDS.get("countries", {}): continue
        try:
            location = geolocator.geocode(loc_name, timeout=5)
            if location and is_within_bounds(location.latitude, location.longitude):
                return loc_name, f"POINT({location.longitude} {location.latitude})"
        except: continue
    return None, None

def classify_text(text: str):
    text = text.lower()
    event_type = "Other"
    for type_name, keywords in KEYWORDS.get("event_types", {}).items():
        if any(k in text for k in keywords):
            event_type = type_name
            break
    country = "Unknown"
    for country_name, keywords in KEYWORDS.get("countries", {}).items():
        if any(k in text for k in keywords):
            country = country_name
            break
    return event_type, country

def is_duplicate(supabase: Client, alert: Dict) -> bool:
    if not alert.get("location_name") or not alert.get("event_type"):
        return False
    thirty_mins_ago = (datetime.now() - timedelta(minutes=30)).isoformat()
    try:
        query = supabase.table("security_alerts") \
            .select("id") \
            .eq("event_type", alert["event_type"]) \
            .eq("location_name", alert["location_name"]) \
            .gte("created_at", thirty_mins_ago) \
            .execute()
        return len(query.data) > 0
    except: return False

# --- LOGIC ---

def process_alert_data(supabase: Client, headline: str, source: str, url: str, raw_data: Dict = None):
    print(f" -> Processing: {headline[:60]}...")
    event_type, country = classify_text(headline)
    deaths = extract_casualties(headline)
    confidence = get_source_confidence(source)
    loc_name, coords = detect_location(headline)
    
    alert_payload = {
        "headline": headline,
        "source": source,
        "url": url,
        "event_type": event_type,
        "country": country,
        "location_name": loc_name,
        "coordinates": coords,
        "deaths": deaths,
        "confidence": confidence,
        "raw_data": raw_data or {}
    }
    
    # Final filter: Must have a location or a country and be within bounds if geocoded
    if not alert_payload["coordinates"] and alert_payload["country"] == "Unknown":
        return

    if not is_duplicate(supabase, alert_payload):
        try:
            supabase.table("security_alerts").insert(alert_payload).execute()
            print(f"    [INSERTED] {event_type} | {country} | Deaths: {deaths}")
        except Exception as e:
            print(f"    [ERROR] {e}")
    else:
        print(f"    [SKIPPED] Duplicate detected.")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials")
        return
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Standard RSS
    for category, feeds in RSS_SOURCES.items():
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    process_alert_data(supabase, entry.title, feed_url, entry.link, {"summary": getattr(entry, 'summary', '')})
            except Exception as e:
                print(f"Error polling {feed_url}: {e}")

    # GeoJSON APIs
    for source_info in API_SOURCES["Disaster"]:
        try:
            r = requests.get(source_info['url'], timeout=10)
            for feature in r.json().get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                if geom.get('type') == 'Point':
                    lng, lat = geom['coordinates']
                    if is_within_bounds(lat, lng):
                        process_alert_data(supabase, props.get('title') or "Geo Event", source_info['url'], source_info['url'], props)
        except Exception as e:
            print(f"Error polling {source_info['name']}: {e}")

if __name__ == "__main__":
    main()
