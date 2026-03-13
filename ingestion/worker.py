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
    if "aljazeera" in url_lower: return "Al Jazeera"
    if "timesofisrael" in url_lower: return "Times of Israel"
    if "haaretz" in url_lower: return "Haaretz"
    if "jpost" in url_lower: return "Jerusalem Post"
    if "thecradle" in url_lower: return "The Cradle"
    if "middleeasteye" in url_lower: return "Middle East Eye"
    if "aa.com.tr" in url_lower: return "Anadolu Agency"
    if "saudigazette" in url_lower: return "Saudi Gazette"
    if "dailysabah" in url_lower: return "Daily Sabah"
    if "rt.com" in url_lower: return "RT News"
    if "bbc" in url_lower: return "BBC News"
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
        "syria", "iraq", "yemen", "lebanon", "damascus", "baghdad", "sanaa"
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
    catchall_geo = ["africa", "sudan", "mali", "chad", "belarus", "ukraine", "ukrainian", "russia", "russian", "moscow", "kiev"]
    for k in catchall_geo:
        if k in text:
            if not has_theater_context:
                return True, f"Non-Theatre Geography ({k})", "Other", "Unknown"
    # 5. Strict Conflict Keyword Enforcement
    is_official_source = any(k in url.lower() for k in ["idf.il", "centcom.mil", "mofaic.gov.ae", "wam.ae/en/rss"])
    has_conflict_keyword = any(kw.lower() in text for kw in KEYWORDS.get("CONFLICT_KEYWORDS", []))
    
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

        # Check 2: Event + Location Match (Window: 12 Hours around the article's time)
        # Fallback for slight headline variations of the same event
        twelve_hours_before = (alert_time - timedelta(hours=12)).isoformat()
        twelve_hours_after = (alert_time + timedelta(hours=12)).isoformat()
        
        if alert.get("location_name") and alert.get("event_type") and alert["location_name"] != "Unknown":
            query_event = supabase.table("security_alerts") \
                .select("id") \
                .eq("event_type", alert["event_type"]) \
                .eq("location_name", alert["location_name"]) \
                .gte("created_at", twelve_hours_before) \
                .lte("created_at", twelve_hours_after) \
                .execute()
            if len(query_event.data) > 0:
                return True
        
        return False
    except: return False

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
    confidence = get_source_confidence(source)
    loc_name, lat, lon = detect_location(headline)

    # --- THEATER ENFORCEMENT ---
    EXCLUDED_REGIONS = KEYWORDS.get("EXCLUDED_REGIONS", [])
    # REJECT if geocoded to an excluded region
    if loc_name and any(region.lower() in loc_name.lower() for region in EXCLUDED_REGIONS):
        log_rejection(headline, f"Geocoded to Excluded Region ({loc_name})")
        return

    # REJECT Unknown/Low-Auth if not high kinetic score
    is_high_authority = any(cat in source for cat in ["Military/Gov", "OSINT"])
    is_kinetic = event_type in ["AIRSTRIKE", "MISSILE", "NAVAL", "DRONE", "ARTILLERY", "GROUND OPS"]
    if not loc_name and not is_high_authority and not is_kinetic:
        log_rejection(headline, "Unknown Location / Low Context")
        return
    
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

    if raw_data is None: raw_data = {}
    if lat is not None and lon is not None:
        raw_data["lat"] = lat
        raw_data["lon"] = lon
    
    alert_payload = {
        "headline": headline,
        "source": get_clean_source_name(url, headline),
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
                    raw_feed_data[(category, url)] = feed.entries[:20]
            except Exception as e:
                print(f"    [POLL_ERROR] {url}: {e}")

        # 2. Interleave and Flatten All Gathered Intel
        # We take entry[0] from every sources, then entry[1], etc.
        interleaved_entries = []
        max_entries = 20
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
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from datetime import datetime
                try:
                    pub_date = datetime(*entry.published_parsed[:6]).isoformat()
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
        try:
            print("[*] Fetching WAM Official MOFA Summary via Google News...")
            # wam.ae has aggressive F5 bot protection, so we use Google News index as a proxy
            wam_rss_url = "https://news.google.com/rss/search?q=site:wam.ae+intercept+OR+missile+OR+drone+OR+defense+OR+military+when:1d&hl=en-US&gl=US&ceid=US:en"
            r_wam = requests.get(wam_rss_url, timeout=15, headers=COMMON_HEADERS, verify=False)
            wam_feed = feedparser.parse(r_wam.content)
            
            # Sort entries chronologically to prevent older relevant articles from superseding recent ones
            entries = sorted(wam_feed.entries, key=lambda x: getattr(x, 'published_parsed', ()), reverse=True)
            
            # Keywords indicating an official kinetic operations summary
            required_kws = ["intercept"]
            kinetic_kws = ["missile", "drone", "uav", "target", "munition", "salvo"]
            
            for entry in entries:
                raw_title = entry.title
                # Clean Google News suffix
                cleaned_title = raw_title.replace("- وكالة وام", "").replace("- WAM", "").strip()
                title_lower = cleaned_title.lower()
                desc = getattr(entry, 'summary', '').lower()
                
                # We strictly want the tactical intercept summaries, not diplomatic calls
                if all(kw in title_lower for kw in required_kws) and any(kw in title_lower for kw in kinetic_kws):
                    clean_summary = getattr(entry, 'summary', '')
                    clean_summary = re.sub(r'<[^>]+>', '', clean_summary) # Strip HTML
                    clean_summary = clean_summary.strip()
                    if not clean_summary: clean_summary = cleaned_title

                    
                    # Deduplication specifically for OFFICIAL_SUMMARY
                    now = datetime.utcnow()
                    twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
                    
                    query_summary = supabase.table("security_alerts") \
                        .select("id") \
                        .eq("event_type", "OFFICIAL_SUMMARY") \
                        .eq("headline", cleaned_title) \
                        .gte("created_at", twenty_four_hours_ago) \
                        .execute()
                        
                    if len(query_summary.data) == 0:
                        payload = {
                            "headline": cleaned_title,
                            "source": "UAE MOFA (WAM)",
                            "url": entry.link,
                            "event_type": "OFFICIAL_SUMMARY",
                            "country": "UAE",
                            "location_name": "Abu Dhabi (Federal)",
                            "coordinates": "POINT(54.3773 24.4539)",
                            "deaths": 0,
                            "confidence": 1.0,
                            "raw_data": {"summary": clean_summary[:500]},
                            "created_at": now.isoformat()
                        }
                        supabase.table("security_alerts").insert(payload).execute()
                        print(f"    [MOFA SUMMARY INSERTED] {cleaned_title[:40]}...")
                    break # Stop after finding the latest valid defense article

                    
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

        print("--- Sourcing pass finished. Handing back to main loop. ---")

if __name__ == "__main__":
    main()
