import os
import sys
import json
import time
import hashlib
import feedparser
import requests
import re
import spacy
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from supabase import create_client, Client
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging

# Configure basic logging for tenacity
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

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

# Load Dynamic Configurations
CONFIG_PATH = os.path.dirname(__file__)
def load_config(filename, default):
    path = os.path.join(CONFIG_PATH, filename)
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return default

KEYWORDS_CONFIG = load_config("keywords.json", {"GEOGRAPHIC_BOUNDS": {"lat": [16, 45], "lon": [34, 65]}, "CONFLICT_KEYWORDS": [], "BANNED_KEYWORDS": [], "event_types": {}, "countries": {}})
SOURCES_CONFIG = load_config("sources.json", {"RSS_SOURCES": {}, "API_SOURCES": {}})

BOUNDS = KEYWORDS_CONFIG.get("GEOGRAPHIC_BOUNDS", {"lat": [16, 45], "lon": [34, 65]})
RSS_SOURCES = SOURCES_CONFIG.get("RSS_SOURCES", {})
API_SOURCES = SOURCES_CONFIG.get("API_SOURCES", {})
CONFLICT_KEYWORDS = KEYWORDS_CONFIG.get("CONFLICT_KEYWORDS", [])
BANNED_KEYWORDS = KEYWORDS_CONFIG.get("BANNED_KEYWORDS", [])
KEYWORDS = KEYWORDS_CONFIG # For backward compatibility in classify_text

# Source Reliability Scoring
SOURCE_RELIABILITY = {
    "gov": 0.95, "mil": 0.95, "reuters": 0.90, "ap": 0.90,
    "aljazeera": 0.85, "haaretz": 0.85, "jpost": 0.85, "timesofisrael": 0.85,
    "middleeasteye": 0.75, "liveuamap": 0.70, "twitter": 0.40, "x.com": 0.40
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
    "emirati": "UAE", "houthi": "Yemen", "hezbollah": "Lebanon", "hamas": "Gaza",
    "idf": "Israel", "centcom": "Middle East", "mod": "Middle East"
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
    # Use headline for strict deduplication
    headline = alert.get("headline", "")
    if not headline:
        return False
        
    # Synchronization Fix: Use utcnow() to match Supabase storage
    now = datetime.utcnow()
    twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
    thirty_mins_ago = (now - timedelta(minutes=30)).isoformat()

    try:
        # Check 1: Exact Headline Match (Window: 24 Hours)
        # Prevents identical news repeating throughout the day
        query_headline = supabase.table("security_alerts") \
            .select("id") \
            .eq("headline", headline) \
            .gte("created_at", twenty_four_hours_ago) \
            .execute()
        
        if len(query_headline.data) > 0:
            return True

        # Check 2: Event + Location Match (Window: 30 Mins)
        # Fallback for slight headline variations of the same event
        if alert.get("location_name") and alert.get("event_type"):
            query_event = supabase.table("security_alerts") \
                .select("id") \
                .eq("event_type", alert["event_type"]) \
                .eq("location_name", alert["location_name"]) \
                .gte("created_at", thirty_mins_ago) \
                .execute()
            if len(query_event.data) > 0:
                return True
        
        return False
    except: return False

# --- LOGIC ---

from deep_translator import GoogleTranslator

# Strict conflict keywords for "War-Themed" feed
def log_rejection(headline: str, reason: str):
    print(f"    [REJECTED] {reason} | {headline[:50]}...")

def process_alert_data(supabase: Client, headline: str, source: str, url: str, raw_data: Dict = None):
    # Defensive: Clean headline
    headline = headline.strip() if headline else ""
    if not headline: return

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
        log_rejection(headline, "Banned Content")
        return
    
    # 3. Category Trust / Intelligence Logic
    is_high_authority = any(cat in source for cat in ["Military/Gov", "OSINT"])
    event_type, country = classify_text(headline)
    
    is_flight = "flight track" in lower_headline
    
    # CRITICAL: Even if it's a regional hub, if it's NOT war-themed and NOT a disaster/flight/High-Auth,
    # we block it to prevent Little Caesars/Tourism noise.
    if (not is_war_themed and not is_flight and not is_high_authority and 
        event_type not in ["MISSILE", "AIRSTRIKE", "NAVAL"]):
        if event_type != "Disaster":
             log_rejection(headline, "Irrelevant Noise")
             return

    print(f" -> Processing: {headline[:60]}...")
    deaths = extract_casualties(headline)
    confidence = get_source_confidence(source)
    loc_name, lat, lon = detect_location(headline)
    
    # --- INTELLIGENCE FALLBACK ---
    # If official military source has no location, default to source country
    if not loc_name and is_high_authority:
        source_lower = url.lower()
        if "idf.il" in source_lower: loc_name, lat, lon = "Israel", 31.0461, 34.8516
        elif "centcom.mil" in source_lower: loc_name, lat, lon = "Middle East (CENTCOM)", 25.0, 45.0
        elif "mod.gov.sa" in source_lower: loc_name, lat, lon = "Saudi Arabia", 23.8859, 45.0792
        elif "ir" in source_lower: loc_name, lat, lon = "Iran", 32.4279, 53.6880
        elif "yem" in source_lower: loc_name, lat, lon = "Yemen", 15.5527, 48.5164
        elif "iq" in source_lower: loc_name, lat, lon = "Iraq", 33.2232, 43.6793
        elif "pal" in source_lower: loc_name, lat, lon = "Palestine", 31.9522, 35.2332
        elif "liveuamap" in source_lower: loc_name, lat, lon = "Middle East (OSINT)", 30.0, 35.0
    
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
    # Re-check environment inside main to ensure shimmed/bridged variables are captured
    global SUPABASE_URL, SUPABASE_KEY
    if not SUPABASE_URL: SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    if not SUPABASE_KEY: SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print(f"CRITICAL: Missing Supabase credentials. URL Found: {bool(SUPABASE_URL)}, KEY Found: {bool(SUPABASE_KEY)}")
        print(f"[*] Available Environment Keys: {', '.join(os.environ.keys())}")
        return
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("--- OSINT WORKER STARTED (POLLING EVERY 10 MINS) ---")
    
    # Heartbeat configuration
    last_heartbeat = time.time()
    
    while True:
        # Heartbeat logic: Log every 10 mins (600s) to keep Render happy
        if time.time() - last_heartbeat >= 600:
            print(f"[*] [HEARTBEAT] Worker is alive and healthy. Timestamp: {datetime.now().isoformat()}")
            last_heartbeat = time.time()

        try:
            run_poll_cycle(supabase)
        except Exception as e:
            print(f"CRITICAL ERROR in poll cycle: {e}")
            print("[*] Retrying in 30 seconds due to network/db blip...")
            time.sleep(30)
            continue

        print("--- POLL CYCLE COMPLETE. SLEEPING 10 MINS ---")
        time.sleep(600)

@retry(
    wait=wait_fixed(30), 
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception)),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def run_poll_cycle(supabase: Client):
        raw_feed_data = {}
        
        # 1. Gather all data first
        all_sources = []
        for category, feeds in RSS_SOURCES.items():
            for feed_url in feeds:
                all_sources.append((category, feed_url))
        
        print(f"[*] Gathering intel from {len(all_sources)} sources...")
        prev_cat = ""
        for category, url in all_sources:
            if category != prev_cat:
                print(f"[*] Polling Category: {category}...")
                prev_cat = category
            
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

        print("--- POLL CYCLE COMPLETE. SLEEPING 2 MINS ---")
        time.sleep(120)

if __name__ == "__main__":
    main()
