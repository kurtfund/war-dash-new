import os
import json
import time
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

# Middle East Bounding Box (Strict: Excludes Africa completely)
BOUNDS = {
    "lat": (16, 45), # Excludes Sudan (Khartoum is ~15.5)
    "lon": (34, 65)  # Excludes Libya/Egypt Desert
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
        "http://www.bna.bh/rss",
        "https://www.rt.com/rss/news/",
        "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/middleeast/rss.xml",
        "https://www.wam.ae/en/rss/all",
        "https://news.google.com/rss/search?q=UAE+Dubai+location:UAE&hl=en-AE&gl=AE&ceid=AE:en",
        "https://www.dailystar.com.lb/rss",
        "https://asharq.com/rss/"
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
    ],
    "Aircraft": [
        {"name": "OpenSky Network", "url": "https://opensky-network.org/api/states/all", "type": "opensky"}
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

# geolocator moved to top with custom UA


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

from geopy.geocoders import ArcGIS

# ArcGIS is generally more reliable than Nominatim for free-tier OSINT geocoding
geolocator = ArcGIS(user_agent="war_dash_osint_monitor_v4")

NATIONALITY_MAP = {
    "iranian": "Iran", "syrian": "Syria", "lebanese": "Lebanon", 
    "israeli": "Israel", "iraqi": "Iraq", "turkish": "Turkey", "yemeni": "Yemen",
    "qatari": "Qatar", "bahraini": "Bahrain", "kuwaiti": "Kuwait", 
    "jordanian": "Jordan", "saudi": "Saudi Arabia", "palestinian": "Palestine",
    "emirati": "UAE", "houthi": "Yemen", "hezbollah": "Lebanon", "hamas": "Gaza"
}

def detect_location(text: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
    if not nlp: return None, None, None
    doc = nlp(text)
    
    # Prioritize entities: GPE (Places) > LOC (Landmarks) > NORP (Nationalities)
    gpe_candidates = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    loc_candidates = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "FAC"]]
    norp_candidates = []
    
    # Map nationalities to countries
    for ent in doc.ents:
        if ent.label_ == "NORP" and ent.text.lower() in NATIONALITY_MAP:
            norp_candidates.append(NATIONALITY_MAP[ent.text.lower()])
        elif ent.label_ in ["NORP", "ORG"]:
            norp_candidates.append(ent.text)

    # Priority order:
    # 1. Targets (places following verbs like 'hits', 'strikes', 'towards')
    # 2. General GPEs
    # 3. LOC/FAC
    # 4. NORP (Nationalities)
    
    targeting_verbs = ["hits", "strikes", "towards", "targets", "at", "into", "on"]
    target_places = []
    
    # Simple regex-based targeting detection to boost accuracy
    lower_text = text.lower()
    for verb in targeting_verbs:
        pattern = f"{verb}\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)"
        matches = re.findall(pattern, text)
        for m in matches:
            target_places.append(m)

    candidates = target_places + gpe_candidates + loc_candidates
    if not candidates:
        candidates = norp_candidates

    seen = set()
    unique_candidates = []
    for c in candidates:
        if c.lower() not in seen:
            unique_candidates.append(c)
            seen.add(c.lower())
    
    # Process top candidates
    for loc_name in unique_candidates[:4]:
        try:
            time.sleep(0.5)
            location = geolocator.geocode(loc_name, timeout=10)
            if location and is_within_bounds(location.latitude, location.longitude):
                print(f"      [GEO_SUCCESS] {loc_name} -> {location.latitude}, {location.longitude}")
                return loc_name, location.latitude, location.longitude
        except Exception as e:
            print(f"      [GEO_ERROR] {loc_name}: {e}")
            continue
            
    return None, None, None

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

from deep_translator import GoogleTranslator

# Strict conflict keywords for "War-Themed" feed
CONFLICT_KEYWORDS = [
    "missile", "rocket", "strike", "airstrike", "explosion", "bomb", "blast",
    "fighter", "drone", "uav", "navy", "warship", "destroyer", "casualty",
    "killed", "death", "fatality", "dead", "injured", "intercepted", "shot down",
    "flight track", "defense", "security", "forces", "conflict", "clash", "operation",
    "economic", "trade", "investment", "financial", "growth"
]

BANNED_KEYWORDS = [
    "restaurant", "dining", "menu", "shopping", "festival", "holiday", 
    "visit", "tourist", "resort", "hotel", "spa", "exclusive", "fashion",
    "little caesars", "pizza", "burger", "cuisine", "gourmet", "luxury",
    "lifestyle", "entertainment", "culture", "sport", "football", "cricket",
    "vacation", "brunch", "dinner", "lunch", "breakfast", "recipe",
    "franchisee", "franchise", "expansion", "best spots", "spots to spot", "fireworks",
    "concert", "showbiz", "celebrity", "movie", "film", "series",
    "ramadan crescent", "cannon", "ramadan locations", "national day", "celebration",
    "parking", "traffic", "weather forecast", "temperature", "gold rate"
]

def process_alert_data(supabase: Client, headline: str, source: str, url: str, raw_data: Dict = None):
    # 1. Translation Layer
    original_headline = headline
    try:
        # Simple heuristic: if it contains non-latin chars or user wants all translated
        # Actually GoogleTranslator detects automatically
        headline = GoogleTranslator(source='auto', target='en').translate(headline)
        if headline != original_headline:
            print(f" [TRANSLATED] {original_headline[:30]}... -> {headline[:30]}...")
    except Exception as e:
        print(f" [TRANS_ERROR] {e}")

    # 2. Theme & Content Filter
    lower_headline = headline.lower()
    is_war_themed = any(keyword in lower_headline for keyword in CONFLICT_KEYWORDS)
    is_banned = any(bk in lower_headline for bk in BANNED_KEYWORDS)
    if is_banned:
        print(f" [FILTERED (Banned Content)] {headline[:60]}...")
        return
    
    # 3. Category Trust / Intelligence Logic
    # High-authority sources (Military/Gov/OSINT) are ALWAYS war-themed/contextual
    # so we bypass the strict keyword check for them.
    is_high_authority = any(cat in source for cat in ["Military/Gov", "OSINT"])
    
    event_type, country = classify_text(headline)
    
    # Priority Bypass: If it mentions key regional hubs (Dubai, Riyadh, etc.) or is a Flight/Disaster
    # we allow it even if not strictly 'kinetic'
    is_regional_hub = any(hub in lower_headline for hub in ["dubai", "uae", "emirates", "abu dhabi", "saudi", "riyadh", "qatar", "doha", "manama"])
    is_from_uae_source = any(site in source.lower() for site in ["wam.ae", "gulfnews.com", "thenationalnews.com", "news.google.com"])
    is_flight = "flight track" in lower_headline
    
    # CRITICAL: Even if it's a regional hub, if it's NOT war-themed and NOT a disaster/flight/High-Auth,
    # we block it to prevent Little Caesars/Tourism noise.
    if (not is_war_themed and not is_flight and not is_high_authority and 
        event_type not in ["MISSILE", "AIRSTRIKE", "NAVAL"]):
        # Allow disasters/flights from hubs, but block general noise
        if event_type != "Disaster":
             print(f" [FILTERED (Regional Noise)] {headline[:60]}...")
             return

    print(f" -> Processing: {headline[:60]}...")
    deaths = extract_casualties(headline)
    confidence = get_source_confidence(source)
    loc_name, lat, lon = detect_location(headline)
    
    if raw_data is None: raw_data = {}
    if lat is not None and lon is not None:
        raw_data["lat"] = lat
        raw_data["lon"] = lon
    
    alert_payload = {
        "headline": headline,
        "source": source,
        "url": url,
        "event_type": event_type,
        "country": country,
        "location_name": loc_name,
        "coordinates": f"POINT({lon} {lat})" if lat is not None else None,
        "deaths": deaths,
        "confidence": confidence,
        "raw_data": raw_data
    }
    
    # Allow feed updates even without specific coordinates
    if alert_payload["country"] == "Unknown" and not alert_payload["location_name"]:
        if not alert_payload["coordinates"]:
            return

    if not is_duplicate(supabase, alert_payload):
        try:
            # Add a small random millisecond offset to the current time to guarantee ordering
            from datetime import datetime
            import random
            now = datetime.utcnow()
            # Random offset between 0 and 999 milliseconds
            micro_offset = random.randint(0, 999999)
            alert_payload["created_at"] = now.replace(microsecond=micro_offset).isoformat()
            
            supabase.table("security_alerts").insert(alert_payload).execute()
            print(f"    [INSERTED] {event_type} | {country} | {source[:20]}... | {alert_payload['created_at']}")
        except Exception as e:
            print(f"    [ERROR] {e}")
    else:
        print(f"    [SKIPPED] Duplicate detected.")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials")
        return
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("--- OSINT WORKER STARTED (POLLING EVERY 10 MINS) ---")
    
    while True:
        # Dictionary to store entries per feed: { (category, url): [entries] }
        raw_feed_data = {}
        
        # 1. Gather all data first
        all_sources = []
        for category, feeds in RSS_SOURCES.items():
            for feed_url in feeds:
                all_sources.append((category, feed_url))
        
        print(f"[*] Gathering intel from {len(all_sources)} sources...")
        for category, url in all_sources:
            try:
                # Use browser-like headers and ignore SSL errors for sensitive gov sites
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                # We disable SSL verify for gov sites as they freqently have cert issues
                resp = requests.get(url, timeout=15, headers=headers, verify=False)
                feed = feedparser.parse(resp.content)
                # Take top 5 from each. We'll interleave them later.
                raw_feed_data[(category, url)] = feed.entries[:5]
            except Exception as e:
                print(f"    [POLL_ERROR] {url}: {e}")

        # 2. Interleave and Flatten All Gathered Intel
        # We take entry[0] from every sources, then entry[1], etc.
        interleaved_entries = []
        max_entries = 5
        for i in range(max_entries):
            # For each pass, shuffle the sources to avoid bias
            source_keys = list(raw_feed_data.keys())
            import random
            random.shuffle(source_keys)
            
            for sk in source_keys:
                if i < len(raw_feed_data[sk]):
                    interleaved_entries.append((sk, raw_feed_data[sk][i]))

        print(f"[*] Processing {len(interleaved_entries)} interleaved events from {len(source_keys)} unique sources...")
        sources_used = [s[0][1] for s in interleaved_entries[:10]]
        print(f"    [FEED_SAMPLE] Top sources: {', '.join(sources_used)}")
        
        for source_key, entry in interleaved_entries:
            # We process them one by one with a slight delay
            # This ensures distinct created_at timestamps for the dashboard ordering
            process_alert_data(supabase, entry.title, source_key[0], entry.link, {"summary": getattr(entry, 'summary', '')})
            time.sleep(1.0) 

        # GeoJSON APIs (Keep these at the end)
        for cat, sources in API_SOURCES.items():
            for source_info in sources:
                try:
                    r = requests.get(source_info['url'], timeout=10)
                    for feature in r.json().get('features', []):
                        props = feature.get('properties', {})
                        geom = feature.get('geometry', {})
                        if geom.get('type') == 'Point':
                            lng, lat = geom['coordinates']
                            if is_within_bounds(lat, lng):
                                process_alert_data(supabase, props.get('title') or "Geo Event", source_info['name'], source_info['url'], props)
                                time.sleep(0.2)
                except Exception as e:
                    print(f"Error polling {source_info['name']}: {e}")

        # Live Flight Data (OpenSky)
        try:
            lamin, lamax = BOUNDS["lat"]
            lomin, lomax = BOUNDS["lon"]
            opensky_url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            r = requests.get(opensky_url, timeout=15)
            states = r.json().get('states', [])
            if states:
                # Pick up to 5 interesting flights to avoid spamming
                for s in states[:5]:
                    icao24, callsign, origin = s[0], s[1].strip(), s[2]
                    lat, lon = s[6], s[5]
                    alt = s[7] or 0
                    if lat and lon:
                        headline = f"FLIGHT TRACK: {callsign or icao24} active in regional airspace (Alt: {int(alt)}m)"
                        process_alert_data(supabase, headline, "OpenSky Network", "https://opensky-network.org", {"icao24": icao24, "lat": lat, "lon": lon})
        except Exception as e:
            print(f"Error polling OpenSky: {e}")

        print("--- POLL CYCLE COMPLETE. SLEEPING 10 MINS ---")
        time.sleep(600)

if __name__ == "__main__":
    main()
