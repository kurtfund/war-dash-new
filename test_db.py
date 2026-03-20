import os
from dotenv import load_dotenv
load_dotenv(".env")
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table("security_alerts").select("headline, created_at, source, event_type").order("created_at", desc=True).limit(25).execute()

print(f"{'CREATED_AT':<25} | {'SOURCE':<20} | {'EVENT':<10} | HEADLINE")
for r in res.data:
    print(f"{r['created_at'][:22]:<25} | {r['source'][:15]:<20} | {r['event_type']:<10} | {r['headline'][:50]}")
