import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.environ.get("VITE_SUPABASE_URL")
key: str = os.environ.get("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Delete the bad summary so it can be re-inserted
res1 = supabase.table("security_alerts").delete().eq("event_type", "OFFICIAL_SUMMARY").execute()
print("Deleted summaries:", len(res1.data))

# Delete wsaz.com alerts
res2 = supabase.table("security_alerts").delete().ilike("url", "%wsaz.com%").execute()
print("Deleted wsaz.com alerts:", len(res2.data))
