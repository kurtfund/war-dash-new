import os
import json
import hashlib
import feedparser
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional

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

# --- KEYWORDS & GEODATA ---
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "keywords.json")
try:
    with open(KEYWORDS_PATH, "r") as f:
        KEYWORDS = json.load(f)
except:
    KEYWORDS = {"event_types": {}, "countries": {}}

CITY_COORDS = {
    "Beirut": [35.5018, 33.8938],
    "Gaza": [34.4668, 31.5017],
    "Tel Aviv": [34.7818, 32.0853],
    "Tehran": [51.3890, 35.6892],
    "Sanaa": [44.2062, 15.3547],
    "Baghdad": [44.3661, 33.3152],
    "Damascus": [36.2765, 33.5138],
    "Amman": [35.9239, 31.9454],
    "Cairo": [31.2357, 30.0444],
    "Riyadh": [46.6753, 24.7136]
}

# --- UTILITIES ---

def is_within_bounds(lat: float, lon: float) -> bool:
    lat_min, lat_max = BOUNDS["lat"]
    lon_min, lon_max = BOUNDS["lon"]
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

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

# --- FETCHERS ---

def fetch_rss(feed_url: str, category: str, supabase: Client):
    print(f"Polling RSS [{category}]: {feed_url}")
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        headline = entry.title
        url = entry.link
        
        event_type, country = classify_text(headline)
        
        # Geocode if not provided (RSS usually doesn't have coords)
        location_name = None
        coords = None
        for city, point in CITY_COORDS.items():
            if city.lower() in headline.lower():
                location_name = city
                lng, lat = point
                if is_within_bounds(lat, lng):
                    coords = f"POINT({lng} {lat})"
                    break
        
        if not coords and country == "Unknown":
            continue # Hard filter for relevance in this phase

        upload_alert(supabase, {
            "headline": headline,
            "source": feed_url,
            "url": url,
            "event_type": event_type,
            "country": country,
            "location_name": location_name,
            "coordinates": coords,
            "confidence": 0.7,
            "raw_data": {"category": category, "summary": getattr(entry, 'summary', '')}
        })

def fetch_geojson(source_info: Dict, supabase: Client):
    print(f"Polling GeoJSON: {source_info['name']}")
    try:
        r = requests.get(source_info['url'], timeout=10)
        data = r.json()
        
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            
            if geom.get('type') == 'Point':
                lng, lat = geom['coordinates']
                if not is_within_bounds(lat, lng):
                    continue
                
                headline = props.get('title') or props.get('name') or props.get('eventname') or "Geometric Alert"
                event_type = "Disaster"
                if source_info['type'] == 'geojson_fire': event_type = "Fire/Anomaly"
                if source_info['type'] == 'geojson_earthquake': event_type = "Earthquake"

                upload_alert(supabase, {
                    "headline": headline,
                    "source": source_info['url'],
                    "event_type": event_type,
                    "coordinates": f"POINT({lng} {lat})",
                    "confidence": 0.9,
                    "raw_data": props
                })
    except Exception as e:
        print(f"Error fetching GeoJSON {source_info['name']}: {e}")

def upload_alert(supabase: Client, alert: Dict):
    try:
        # Deduplication based on headline (very basic)
        existing = supabase.table("security_alerts").select("id").eq("headline", alert["headline"]).limit(1).execute()
        if not existing.data:
            supabase.table("security_alerts").insert(alert).execute()
            print(f" -> Inserted: {alert['headline'][:50]}...")
    except Exception as e:
        print(f" -> DB Error: {e}")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Poll RSS Sources
    for category, feeds in RSS_SOURCES.items():
        for feed in feeds:
            fetch_rss(feed, category, supabase)

    # Poll API Sources
    for category, sources in API_SOURCES.items():
        for source in sources:
            fetch_geojson(source, supabase)

if __name__ == "__main__":
    main()
