import os
import json
import hashlib
import feedparser
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RSS_FEEDS = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "http://feeds.reuters.com/reuters/worldNews",
    "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml"
]

# Load keywords from shared config if possible, or define here
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "keywords.json")
try:
    with open(KEYWORDS_PATH, "r") as f:
        KEYWORDS = json.load(f)
except FileNotFoundError:
    # Fallback if keywords.json isn't found
    KEYWORDS = {"event_types": {}, "countries": {}}

# Simplified geocoding from city names (extendable)
CITY_COORDS = {
    "Beirut": [35.5018, 33.8938],
    "Gaza": [34.4668, 31.5017],
    "Tel Aviv": [34.7818, 32.0853],
    "Tehran": [51.3890, 35.6892],
    "Sanaa": [44.2062, 15.3547],
    "Baghdad": [44.3661, 33.3152],
    "Damascus": [36.2765, 33.5138]
}

def get_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def classify_event(text):
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

def process_feeds():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    new_alerts = []
    
    for feed_url in RSS_FEEDS:
        print(f"Polling {feed_url}...")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            headline = entry.title
            source = feed_url
            url = entry.link
            
            # 1. Deduplication Check (Simple check against recent entries or title hash)
            # In a production system, we'd check a Redis cache or the DB.
            # For now, we'll try-catch the insert or query first.
            
            event_type, country = classify_event(headline)
            
            # Skip if it doesn't seem relevant to a conflict/event (optional filter)
            if event_type == "Other" and country == "Unknown":
                continue

            # Basic location detection from text
            location_name = None
            coords = None
            for city, point in CITY_COORDS.items():
                if city.lower() in headline.lower():
                    location_name = city
                    lng, lat = point
                    coords = f"POINT({lng} {lat})"
                    break

            alert_data = {
                "headline": headline,
                "source": source,
                "url": url,
                "event_type": event_type,
                "country": country,
                "location_name": location_name,
                "coordinates": coords,
                "confidence": 0.8,
                "raw_data": {"summary": getattr(entry, 'summary', '')}
            }
            
            # Insert (Supabase unique constraint or manual check can handle dedup)
            try:
                # Check for existing headline to prevent spamming
                existing = supabase.table("security_alerts").select("id").eq("headline", headline).limit(1).execute()
                if not existing.data:
                    res = supabase.table("security_alerts").insert(alert_data).execute()
                    print(f"Inserted: {headline[:50]}...")
                else:
                    print(f"Skipped (Duplicate): {headline[:50]}...")
            except Exception as e:
                print(f"Error inserting: {e}")

if __name__ == "__main__":
    process_feeds()
