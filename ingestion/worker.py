import os
import sys
import json
import time
import hashlib
import feedparser
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from supabase import create_client, Client
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging
import subprocess

# Configure basic logging for tenacity
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

# --- LOAD RESOURCES SAFELY ---
# Handles Python 3.14 breaking changes inside pydantic v1 (dependency of spacy)
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Warning: spaCy model not found. Attempting to download...")
        try:
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except:
            nlp = None
except Exception as e:
    print(f"Warning: Failed to import spacy ({e}). NLP features will be disabled. Running geographical fallback mode.")
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
BANNED_KEYWORDS.extend(["wsaz", "wsaz.com", "armenian", "armenia", "yerevan", "sport", "cyprus", "nicosia"])
KEYWORDS = KEYWORDS_CONFIG # For backward compatibility in classify_text

# Source Reliability Scoring
SOURCE_RELIABILITY = {
    "gov": 0.95,
    "mil": 0.95,
    "reuters": 0.90,
    "bbc": 0.90,
    "theguardian": 0.90,
    "nytimes": 0.90,
    "apnews": 0.90,
    "newsatme": 0.90,
    "associated-press": 0.90,
    "bloomberg": 0.90,
    "france24": 0.85,
    "dw.com": 0.85,
    "irna": 0.80,
    "presstv": 0.75,
    "tehrantimes": 0.75,
    "tasnimnews": 0.75,
    "mehrnews": 0.75,
    "rt.com": 0.65,
    "wam.ae": 0.85,
    "thenationalnews": 0.75,
    "khaleejtimes": 0.75,
    "gulfnews": 0.75,
    "alarabiya": 0.80,
    "arabnews": 0.75,
    "aawsat": 0.80,
    "aljazeera": 0.85,
    "dailynewsegypt": 0.75,
    "middleeasteye": 0.75,
    "middleeastmonitor": 0.75,
    "haaretz": 0.85,
    "jpost": 0.85,
    "timesofisrael": 0.85,
    "liveuamap": 0.70,
    "twitter": 0.40,
    "x.com": 0.40
}

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

def get_clean_source_name(url: str, headline: str = "") -> str:
    """
    Maps URLs to human-readable names.
    Specifically solves for Google News RSS wrappers like WAM.
    """
    url_lower = url.lower()

    # 0. Google News Source Extraction
    # Google News RSS titles usually end with " - Publisher Name"
    if "news.google.com" in url_lower and headline:
        if " - " in headline:
            parts = headline.split(" - ")
            if len(parts) > 1:
                return parts[-1].strip()
    
    # 1. Government & Military
    if "idf.il" in url_lower: return "IDF (Israel Defense Forces)"
    if "centcom.mil" in url_lower: return "US CENTCOM"
    if "mod.gov.sa" in url_lower: return "Saudi Ministry of Defense"
    if "mofaic.gov.ae" in url_lower: return "UAE MOFA"
    
    # 2. WAM Specific (Google News Wrapper)
    if "source:emirates_news_agency" in url_lower or "wam.ae" in url_lower:
        return "WAM (Emirates News Agency)"
    
    # 3. Major Institutional
    if "reuters" in url_lower: return "Reuters"
    if "bbc" in url_lower: return "BBC News"
    if "theguardian" in url_lower: return "The Guardian"
    if "apnews" in url_lower or "associated-press" in url_lower or "newsatme" in url_lower: return "Associated Press (AP)"
    if "bloomberg" in url_lower: return "Bloomberg"
    if "france24" in url_lower: return "France 24"
    if "dw.com" in url_lower: return "Deutsche Welle (DW)"
    
    if "irna" in url_lower: return "IRNA"
    if "presstv" in url_lower: return "Press TV"
    if "tehrantimes" in url_lower: return "Tehran Times"
    if "tasnimnews" in url_lower: return "Tasnim News Agency"
    if "mehrnews" in url_lower: return "Mehr News Agency"
    if "rt.com" in url_lower: return "RT News"
    
    if "khaleejtimes" in url_lower: return "Khaleej Times"
    if "gulfnews" in url_lower: return "Gulf News"
    if "alarabiya" in url_lower: return "Al Arabiya"
    if "aawsat" in url_lower: return "Asharq Al-Awsat"
    if "arabnews" in url_lower: return "Arab News"
    
    if "aljazeera" in url_lower: return "Al Jazeera"
    if "dailynewsegypt" in url_lower: return "Daily News Egypt"
    if "middleeasteye" in url_lower: return "Middle East Eye"
    if "middleeastmonitor" in url_lower: return "Middle East Monitor"
    
    if "haaretz" in url_lower: return "Haaretz"
    if "jpost" in url_lower: return "Jerusalem Post"
    if "timesofisrael" in url_lower: return "Times of Israel"

    if "jordantimes" in url_lower: return "The Jordan Times"
    if "dailystar" in url_lower: return "The Daily Star"
    if "egypttoday" in url_lower: return "Egypt Today"
    if "al-monitor" in url_lower: return "Al-Monitor"
    if "kuwaittimes" in url_lower: return "Kuwait Times"
    if "qatar-tribune" in url_lower: return "Qatar Tribune"
    if "bna.bh" in url_lower: return "Bahrain News Agency"
    
    # "The National" (UAE) vs "The National Interest" (US)
    if "thenationalnews.com" in url_lower: return "The National (UAE)"
    if "the national" in headline.lower() or "the+national" in url_lower:
        if "the national interest" in headline.lower() or "nationalinterest.org" in url_lower:
            return "The National Interest"
        return "The National (UAE)"

    if "thecradle" in url_lower: return "The Cradle"
    if "aa.com.tr" in url_lower: return "Anadolu Agency"
    if "saudigazette" in url_lower: return "Saudi Gazette"
    if "dailysabah" in url_lower: return "Daily Sabah"
    
    if "nytimes" in url_lower: return "New York Times"
    
    # 4. OSINT
    if "liveuamap" in url_lower: return "LiveUAMap (OSINT)"
    
    # 5. APIs
    if "earthquake.usgs.gov" in url_lower: return "USGS Earthquakes"
    if "gdacs.org" in url_lower: return "GDACS Disaster Alerts"
    if "opensky-network" in url_lower: return "OpenSky Network"

    # Fallback to domain
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain.replace("www.", "")

def log_rejection(headline: str, reason: str):
    print(f"    [REJECTED] {reason} | {headline[:60]}...")

def should_filter_alert(headline: str, source: str, url: str) -> Tuple[bool, str, str, str]:
    """
    Returns (should_reject, reason, event_type, country)
    """
    text = headline.lower()
    # Theater bypass set (allow banned figures/regions if these theater keywords are present)
    theater_bypass = [
        "iran", "israel", "hezbollah", "houthi", "hamas", "gaza", "beirut", "tehran", "tel aviv", "jerusalem",
        "syria", "iraq", "yemen", "lebanon", "damascus", "baghdad", "sanaa", "west bank", "gaza strip", "palestine",
        "red sea", "gulf of aden", "arabian sea", "persian gulf", "middle east", "uae", "emirates", "abu dhabi",
        "dubai", "saudi", "riyadh", "egypt", "cairo", "jordan", "amman", "qatar", "doha", "kuwait", "oman", 
        "bahrain", "manama", "idf", "irgc"
    ]
    has_theater_context = any(tk in text for tk in theater_bypass)

    # 1. Banned Keywords (Hard Reject with Smart Bypass)
    # Banned keywords that can be bypassed by theater context (e.g. Putin + Iran)
    geopolitical_banned = ["putin", "trump", "zelensky", "zelenskyy", "kremlin", "nato", "russia", "russian", "ukraine", "ukrainian"]
    
    for word in BANNED_KEYWORDS:
        word_clean = word.strip().lower()
        if not word_clean: continue
        pattern = r'\b' + re.escape(word_clean) + r'\b'
        if re.search(pattern, text):
            # Bypass logic for geopolitical names
            if word_clean in geopolitical_banned and has_theater_context:
                print(f" [BYPASS] Allowing banned entity '{word_clean}' due to theater context.")
                continue
            return True, f"Banned Keyword ({word_clean})", "Other", "Unknown"
            
    # 2. Excluded Regions (Theater Hardening with Smart Bypass)
    EXCLUDED_REGIONS = KEYWORDS.get("EXCLUDED_REGIONS", [])
    EXCLUDED_REGIONS.extend(["cyprus", "nicosia"])
    # Regions that can be bypassed by theater context
    bypassable_regions = ["russia", "belarus", "ukraine", "moscow", "kiev", "kyiv"]

    for region in EXCLUDED_REGIONS:
        region_clean = region.strip().lower()
        if not region_clean: continue
        pattern = r'\b' + re.escape(region_clean) + r'\b'
        if re.search(pattern, text):
            # Bypass logic for specific regions
            if region_clean in bypassable_regions and has_theater_context:
                print(f" [BYPASS] Allowing excluded region '{region_clean}' due to theater context.")
                continue
            return True, f"Excluded Region ({region_clean})", "Other", "Unknown"

    # 3. Text Classification
    event_type, country = classify_text(headline)
    
    # 4. Strict Theatre Check (Catch-all for explicit theater bypass)
    catchall_geo = ["africa", "sudan", "mali", "chad", "belarus", "ukraine", "ukrainian", "russia", "russian", "moscow", "kiev", "armenia", "armenian", "yerevan", "india", "pakistan", "afghanistan", "kolkata", "delhi", "mumbai"]
    for k in catchall_geo:
        if k in text:
            if not has_theater_context:
                return True, f"Non-Theatre Geography ({k})", "Other", "Unknown"
                
    # 5. Strict Conflict Keyword Enforcement
    is_official_source = any(k in url.lower() for k in ["idf.il", "centcom.mil", "mofaic.gov.ae", "wam.ae/en/rss"])
    has_conflict_keyword = any(kw.lower() in text for kw in KEYWORDS.get("CONFLICT_KEYWORDS", []))
    
    # 6. ABSOLUTE THEATER LOCK: All news must have theater context unless from an official source
    if not has_theater_context and not is_official_source:
        return True, "No Middle East Theater Context (Locked)", "Other", "Unknown"

    if not has_conflict_keyword and not is_official_source:
        return True, "No Conflict Keyword (Generic News Blocked)", "Other", "Unknown"

    return False, None, event_type, country

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
    gpe_candidates = []
    loc_candidates = []
    norp_candidates = []
    
    if nlp is not None:
        doc = nlp(text)
        
        # Prioritize entities: GPE (Places) > LOC (Landmarks) > NORP (Nationalities)
        gpe_candidates = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        loc_candidates = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "FAC"]]
        
        # Map nationalities to countries
        for ent in doc.ents:
            if ent.label_ == "NORP" and ent.text.lower() in NATIONALITY_MAP:
                norp_candidates.append(NATIONALITY_MAP[ent.text.lower()])
            elif ent.label_ in ["NORP", "ORG"]:
                norp_candidates.append(ent.text)
    else:
        # --- Native Fallback when NLP is disabled due to Python 3.14 bug ---
        lower_text = text.lower()
        fallback_places = [
            "Israel", "Lebanon", "Iran", "Yemen", "Iraq", "Syria", "Gaza", 
            "UK", "USA", "UAE", "Saudi Arabia", "Abu Dhabi", "Dubai", 
            "Tehran", "Beirut", "Tel Aviv", "Jerusalem", "Baghdad", "Sanaa", "Damascus"
        ]
        for fp in fallback_places:
            if fp.lower() in lower_text:
                gpe_candidates.append(fp)

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
        
    try:
        alert_time_str = alert.get("created_at") or datetime.utcnow().isoformat()
        try:
            alert_time = datetime.fromisoformat(alert_time_str)
        except:
            alert_time = datetime.utcnow()
        
        # Check 1: Exact Headline Match (Any time - if we've seen this exact headline, skip it)
        query_headline = supabase.table("security_alerts") \
            .select("id") \
            .eq("headline", headline) \
            .limit(1) \
            .execute()
        
        if len(query_headline.data) > 0:
            return True

        # We removed Check 2 (Event + Location Match) because it was far too greedy 
        # and blocking valid news events that share the same general type and location (e.g., Israel strikes Iran multiple times a day).
        return False
    except Exception as e:
        print(f"Dedup error: {e}")
        return False

# --- LOGIC ---

def process_alert_data(supabase: Client, headline: str, source: str, url: str, raw_data: Dict = None, published_at: str = None):
    # Synchronize time to UTC for Supabase
    from datetime import datetime
    
    # 1. Strip defensive whitespace and Google News suffixes
    headline = headline.strip() if headline else ""
    if not headline: return
    
    # Strip common Google News RSS suffixes (e.g., " - Al Jazeera", " - WVLT")
    headline = re.sub(r'\s+-\s+[^-]+$', '', headline).strip()
    
    original_headline = headline
    try:
        from deep_translator import GoogleTranslator
        headline = GoogleTranslator(source='auto', target='en').translate(headline)
        if headline != original_headline:
            print(f" [TRANSLATED] {original_headline[:30]}... -> {headline[:30]}...")
    except Exception as e:
        pass # Silently fail translation and use original if API limits hit
    
    # 2. Hardened Filtering
    should_reject, reason, event_type, country = should_filter_alert(headline, source, url)
    if should_reject:
        log_rejection(headline, reason)
        return

    print(f" -> Processing: {headline[:60]}...")
    deaths = extract_casualties(headline)
    confidence = get_source_confidence(url)
    loc_name, lat, lon = detect_location(headline)

    # --- INTELLIGENCE FALLBACK ---
    # --- INTELLIGENCE FALLBACK ---
    # Guarantee Coordinates: If any news passes the filters above, it MUST be mapped!
    # If spaCy couldn't find a location, we default the marker to the source's region or the map center.
    if not loc_name or lat is None or lon is None:
        source_lower = url.lower()
        if "idf.il" in source_lower or "jpost" in source_lower or "timesofisrael" in source_lower: loc_name, lat, lon = "Israel", 31.0461, 34.8516
        elif "mod.gov.sa" in source_lower or "saudigazette" in source_lower: loc_name, lat, lon = "Saudi Arabia", 23.8859, 45.0792
        elif "ir" in source_lower or "tasnim" in source_lower: loc_name, lat, lon = "Iran", 32.4279, 53.6880
        elif "aljazeera" in source_lower: loc_name, lat, lon = "Qatar (Al Jazeera)", 25.276987, 51.520008
        elif "wam.ae" in source_lower or "mofaic" in source_lower: loc_name, lat, lon = "UAE", 23.4241, 53.8478
        elif "thecradle" in source_lower: loc_name, lat, lon = "Lebanon (The Cradle)", 33.8938, 35.5018
        elif "centcom.mil" in source_lower: loc_name, lat, lon = "Middle East (CENTCOM)", 25.0, 45.0
        elif "yem" in source_lower: loc_name, lat, lon = "Yemen", 15.5527, 48.5164
        elif "iq" in source_lower: loc_name, lat, lon = "Iraq", 33.2232, 43.6793
        elif "rt.com" in source_lower: loc_name, lat, lon = "Syria (RT)", 33.5138, 36.2765
        else: loc_name, lat, lon = "Middle East Regional", 28.0, 45.0

    # --- THEATER ENFORCEMENT ---
    EXCLUDED_REGIONS = KEYWORDS.get("EXCLUDED_REGIONS", [])
    # REJECT if geocoded to an excluded region
    if loc_name and any(region.lower() in loc_name.lower() for region in EXCLUDED_REGIONS) and loc_name != "Middle East Regional":
        log_rejection(headline, f"Geocoded to Excluded Region ({loc_name})")
        return

    # REJECT Unknown/Low-Auth if not high kinetic score
    is_high_authority = any(cat in source for cat in ["Military/Gov", "OSINT"])
    is_kinetic = event_type in ["AIRSTRIKE", "MISSILE", "NAVAL", "DRONE", "ARTILLERY", "GROUND OPS"]
    if not loc_name and not is_high_authority and not is_kinetic:
        log_rejection(headline, "Unknown Location / Low Context")
        return

    if raw_data is None: raw_data = {}
    if lat is not None and lon is not None:
        raw_data["lat"] = lat
        raw_data["lon"] = lon
    
    alert_payload = {
        "headline": headline,
        "source": get_clean_source_name(url, original_headline),
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

    # Assign correct timestamp before duplicate checking
    if published_at:
        alert_payload["created_at"] = published_at
    else:
        from datetime import datetime
        import random
        now = datetime.utcnow()
        micro_offset = random.randint(0, 999999)
        alert_payload["created_at"] = now.replace(microsecond=micro_offset).isoformat()

    if not is_duplicate(supabase, alert_payload):
        try:
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

    print("--- OSINT WORKER STARTED (POLLING EVERY 1 MINS) ---")
    
    # ONE-TIME CLEANUP FOR BANNED KEYWORDS (Prevents old alerts from showing up)
    try:
        print("Running database cleanup to purge old bad alerts...")
        supabase.table('security_alerts').delete().ilike('headline', '%Modi%').execute()
        supabase.table('security_alerts').delete().ilike('headline', '%Kolkata%').execute()
        print("Database cleanup successful.")
    except Exception as e:
        print(f"Database cleanup failed: {e}")

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

        print("--- POLL CYCLE COMPLETE. SLEEPING 1 MINS ---")
        time.sleep(60)


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
        
        # Common browser-like headers for all requests
        COMMON_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

        print(f"[*] Gathering intel from {len(all_sources)} sources...")
        prev_cat = ""
        for category, url in all_sources:
            if category != prev_cat:
                print(f"[*] Polling Category: {category}...")
                prev_cat = category
            
            try:
                # Custom HTML Scraper for RT Trends
                if "rt.com/trends/" in url:
                    resp = requests.get(url, timeout=15, headers=COMMON_HEADERS, verify=False)
                    links = []
                    for chunk in resp.text.split('href="'):
                        if chunk.startswith('/news/'):
                            link = chunk.split('"')[0]
                            full_url = "https://www.rt.com" + link
                            if not any(x.link == full_url for x in links):
                                class DummyEntry:
                                    def __init__(self, title, link):
                                        self.title = title
                                        self.link = link
                                        self.summary = "Extracted from RT Trends"
                                title_slug = link.split('/')[-2].replace('-', ' ').title()
                                links.append(DummyEntry(title_slug, full_url))
                                if len(links) >= 20: break
                    raw_feed_data[(category, url)] = links
                else:
                    # Use browser-like headers and ignore SSL errors for sensitive gov sites
                    resp = requests.get(url, timeout=15, headers=COMMON_HEADERS, verify=False)
                    feed = feedparser.parse(resp.content)
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
        if interleaved_entries:
            sources_used = [s[0][1] for s in interleaved_entries[:10]]
            print(f"    [FEED_SAMPLE] Top sources: {', '.join(sources_used)}")
        
        for source_key, entry in interleaved_entries:
            # Try to extract the actual article publication date to maintain chronological integrity
            pub_date = None
            from datetime import datetime, timezone
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # Use feedparser's parsed struct if available
                try:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                except: pass
            elif hasattr(entry, 'published') and entry.published:
                # Try raw string
                try:
                    from dateutil import parser
                    pub_date = parser.parse(entry.published).astimezone(timezone.utc).isoformat()
                except: pass
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                # Try updated field
                try:
                    pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()
                except: pass

            process_alert_data(supabase, entry.title, source_key[0], entry.link, {"summary": getattr(entry, 'summary', '')}, published_at=pub_date)
            time.sleep(0.5) 

        # GeoJSON APIs (Keep these at the end)
        for cat, sources in API_SOURCES.items():
            for source_info in sources:
                try:
                    r = requests.get(source_info['url'], timeout=10, headers=COMMON_HEADERS)
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

        # --- MARKET DATA UPDATE ---
        try:
            print("[*] Fetching Live Market Data from Yahoo Finance...")
            tickers = ['AED=X', 'CL=F', 'GC=F', '^TASI.SR', '^GSPC', 'AAPL', '2222.SR']
            market_payload = {}

            for t in tickers:
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{t}"
                try:
                    # Reuse COMMON_HEADERS and session from outer scope if possible, but requests is fine
                    r = requests.get(url, headers=COMMON_HEADERS, timeout=10)
                    data = r.json()['chart']['result'][0]['meta']
                    price = data['regularMarketPrice']
                    prev_close = data['chartPreviousClose']
                    pct_change = ((price - prev_close) / prev_close) * 100
                    market_payload[t] = {"price": price, "change": pct_change}
                except Exception as e:
                    print(f"    [MARKET_ERROR] Failed to fetch {t}: {e}")

            if market_payload:
                now = datetime.utcnow()
                payload = {
                    "headline": "Live Market Pulse Update",
                    "source": "Yahoo Finance (Backend)",
                    "url": "https://finance.yahoo.com",
                    "event_type": "MARKET_DATA",
                    "country": "Global",
                    "location_name": "Global Markets",
                    "deaths": 0,
                    "confidence": 1.0,
                    "raw_data": market_payload,
                    "created_at": now.isoformat()
                }
                
                supabase.table("security_alerts").insert(payload).execute()
                print("    [MARKET DATA INSERTED]")
        except Exception as e:
            print(f"Error in Market Pulse fetch: {e}")

        # --- OFFICIAL MOFA SUMMARY AUTO-UPDATE ---
        # --- OFFICIAL MOFA SUMMARY AUTO-UPDATE ---
        try:
            print("[*] Fetching WAM Official MOFA Summary via Direct API...")
            from bs4 import BeautifulSoup
            import re
            from datetime import timedelta
            
            # Deep Crawl of WAM Latest News API
            wam_articles = []
            
            API_HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.wam.ae/en'
            }
            
            try:
                # Get the view for latest news
                view_url = "https://www.wam.ae/api/app/views/GetViewByUrl?url=en/list/latest-news"
                resp = requests.get(view_url, headers=API_HEADERS, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    import json
                    dumped = json.dumps(data)
                    # Find all slugs, prioritizing ones that look like military updates
                    slugs = re.findall(r'"slug"\s*:\s*"([^"]+)"', dumped)
                    target_slug_found = False
                    for s in slugs:
                        url = f"https://www.wam.ae/en/article/{s}"
                        if 'engage' in s.lower() or 'ballistic' in s.lower() or 'intercept' in s.lower():
                            # Move these high-priority slugs to the front of the line
                            wam_articles.insert(0, url)
                            target_slug_found = True
                        else:
                            wam_articles.append(url)
                            
                    # Fallback for today just in case the view API missed it entirely
                    hardcoded_backup = "https://www.wam.ae/en/article/bz8e7gc-uae-air-defences-engage-ballistic-missiles-uavs"
                    if not target_slug_found and hardcoded_backup not in wam_articles:
                        wam_articles.insert(0, hardcoded_backup)
            except Exception as e:
                print(f"      [WAM_VIEW_API_ERROR]: {e}")
                
            # Remove duplicates while preserving order
            wam_articles = list(dict.fromkeys(wam_articles))
            
            full_text = ""
            latest_article_captured = None

            for article_url in wam_articles[:40]: # Check up to 40 recent news items
                try:
                    slug_match = re.search(r'article/([^/?]+)', article_url)
                    if not slug_match: continue
                    slug = slug_match.group(1)
                    
                    api_url = f"https://www.wam.ae/api/app/articles/GetArticleBySlug?slug={slug}"
                    resp = requests.get(api_url, headers=API_HEADERS, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        body = data.get('body', '')
                        summary = data.get('summary', '')
                        subTitle = data.get('subTitle', '') # Often contains the key data on WAM
                        
                        # Combine text components
                        content = f"{subTitle} {summary} {body}".strip()
                        
                        # Check for our key targets
                        if "ballistic" in content.lower() or "intercepted" in content.lower() or "engaged" in content.lower():
                            if re.search(r'\d+\s+(?:ballistic|cruise|uav|drone)', content, re.IGNORECASE):
                                full_text = content
                                latest_article_captured = article_url
                                break # Found the intercept report
                except Exception as e:
                    print(f"      [WAM_ARTICLE_API_ERROR] {article_url}: {e}")

            if full_text.strip():
                # --- QUANTITATIVE EXTRACTION ---
                word_to_num = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
                    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 
                    'nineteen': 19, 'twenty': 20
                }
                
                def parse_num_match(m):
                    m = m.lower().replace(',', '').strip()
                    if m in word_to_num: return word_to_num[m]
                    try: return int(m)
                    except: return 0

                ballistic = 0
                cruise = 0
                uavs = 0
                
                num_pattern = r'(\d+(?:,\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)'
                
                # Contextual Extraction: Find the sentence describing the totals
                # Clean text to remove extra whitespaces
                clean_text = re.sub(r'\s+', ' ', full_text)
                
                # Use the improved regex from our test script
                engaged_match = re.search(r'engaged\s+.*?(?:ballistic|cruise|uav|drone).*?since', clean_text, re.IGNORECASE)
                if not engaged_match:
                    engaged_match = re.search(r'[^.]*(?:ballistic|cruise|uav|drone)[^.]*', clean_text, re.IGNORECASE)
                
                if engaged_match:
                    context = engaged_match.group(0)
                    print(f"    [WAM_EXTRACT] Context: {context[:100]}...")
                    
                    b_matches = re.findall(num_pattern + r'\s+(?:ballistic\s*)?missiles?', context, re.IGNORECASE)
                    if b_matches: ballistic = max([parse_num_match(m) for m in b_matches])
                    
                    c_matches = re.findall(num_pattern + r'\s+cruise\s*missiles?', context, re.IGNORECASE)
                    if c_matches: cruise = max([parse_num_match(m) for m in c_matches])
                    
                    u_matches = re.findall(num_pattern + r'\s+(?:uavs?|drones?)', context, re.IGNORECASE)
                    if u_matches: uavs = max([parse_num_match(m) for m in u_matches])
                
                if ballistic == 0 and cruise == 0 and uavs == 0:
                    print("    [MOFA SUMMARY SKIPPED] No quantitative totals found in active WAM articles.")
                else:
                    now = datetime.utcnow()
                    pub_date_iso = now.isoformat()
                    cleaned_title = f"UAE MOFA Update: {ballistic} Ballistic Missiles, {uavs} UAVs Intercepted"
                    
                    # Check for existing alert with same numbers to avoid spam
                    query_summary = supabase.table("wam_official_data") \
                        .select("id") \
                        .eq("missiles", ballistic) \
                        .eq("uavs", uavs) \
                        .execute()
                        
                    if len(query_summary.data) == 0:
                        payload = {
                            "headline": cleaned_title,
                            "source": "UAE MOFA (WAM)",
                            "url": latest_article_captured or "https://www.wam.ae/en/list/latest-news",
                            "event_type": "OFFICIAL_SUMMARY",
                            "country": "UAE",
                            "location_name": "Abu Dhabi (Federal)",
                            "coordinates": "POINT(54.3773 24.4539)",
                            "deaths": 0,
                            "confidence": 1.0,
                            "raw_data": {
                                "summary": full_text[:500] if full_text else cleaned_title,
                                "ballistic": ballistic,
                                "cruise": cruise,
                                "uavs": uavs,
                                "missiles": ballistic + cruise, 
                                "drones": uavs 
                            },
                            "created_at": pub_date_iso
                        }
                        supabase.table("security_alerts").insert(payload).execute()
                        print(f"    [MOFA SUMMARY INSERTED] (B: {ballistic}, C: {cruise}, D: {uavs})")
                        
                        # Store in isolated table
                        isolated_payload = {
                            "url": latest_article_captured,
                            "headline": full_text[:500] if full_text else "WAM Quantitative Data Extracted",
                            "missiles": ballistic,
                            "cruise": cruise,
                            "uavs": uavs,
                            "raw_data": {
                                "ballistic": ballistic,
                                "cruise": cruise,
                                "uavs": uavs
                            }
                        }
                        
                        try:
                            print(f"      -> Upserting Official Summary (Isolating): {ballistic} Ballistic, {cruise} Cruise, {uavs} UAVs")
                            supabase.table('wam_official_data').insert(isolated_payload).execute()
                        except Exception as e:
                            print(f"      [SUPABASE_SUMMARY_INSERT_ERROR]: {e}")
                    else:
                        print(f"    [MOFA SUMMARY SKIPPED] Data (B:{ballistic}, D:{uavs}) already recorded.")
            else:
                print("    [MOFA SUMMARY ERROR] Could not find relevant intercept data in standard WAM articles.")
                 
        except Exception as e:
            print(f"Error fetching WAM MOFA Summary: {e}")
        # Live Flight Data (OpenSky)
        try:
            lamin, lamax = BOUNDS["lat"]
            lomin, lomax = BOUNDS["lon"]
            opensky_url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            r = requests.get(opensky_url, timeout=15, headers=COMMON_HEADERS)
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

        # INSS Scraper completely disabled on production server due to headless browser build limits
        pass


        print("--- Sourcing pass finished. Handing back to main loop. ---")

if __name__ == "__main__":
    main()
