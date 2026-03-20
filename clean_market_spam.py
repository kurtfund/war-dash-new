import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

print("Deleting all MARKET_DATA from security_alerts table...")
res = supabase.table("security_alerts").delete().eq("event_type", "MARKET_DATA").execute()
print(f"Deleted {len(res.data)} market data rows from security_alerts.")
