import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

# Mock entry
class MockEntry:
    def __init__(self, title, link, published_parsed):
        self.title = title
        self.link = link
        self.published_parsed = published_parsed
        self.summary = "Test summary"

# Load env
load_dotenv('dashboard/.env.local')
url = os.environ.get('VITE_SUPABASE_URL')
key = os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_ANON_KEY')

if not url or not key:
    print("Missing keys")
    sys.exit(1)

supabase = create_client(url, key)

from ingestion.worker import process_alert_data, is_duplicate

# Clean db first
supabase.table("security_alerts").delete().eq("headline", "Test Drone Strike in Iran").execute()
supabase.table("security_alerts").delete().eq("headline", "Test Drone Strike in Iran - FakeNews").execute()

# Create a mock entry that was published 3 days ago
pub_date_obj = datetime.utcnow() - timedelta(days=3)
pub_parsed = pub_date_obj.timetuple()
iso_pub = pub_date_obj.isoformat()

print("Inserting first time...")
process_alert_data(supabase, "Test Drone Strike in Iran - FakeNews", "FakeNews", "http://test", {}, iso_pub)

print("Checking db...")
res = supabase.table("security_alerts").select("*").eq("headline", "Test Drone Strike in Iran").execute()
print(f"Items found: {len(res.data)}")
if res.data:
    print("Created at:", res.data[0]['created_at'])

print("Inserting duplicate with same exact cleaned headline...")
process_alert_data(supabase, "Test Drone Strike in Iran - AnotherSource", "AnotherSource", "http://test", {}, iso_pub)

print("Checking db again (should still be 1)...")
res2 = supabase.table("security_alerts").select("*").eq("headline", "Test Drone Strike in Iran").execute()
print(f"Items found: {len(res2.data)}")

# Cleanup
supabase.table("security_alerts").delete().eq("headline", "Test Drone Strike in Iran").execute()

