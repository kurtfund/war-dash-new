import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv(".env")
supabase = create_client(os.getenv("VITE_SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
print("Testing dedup fetch:")
res = supabase.table("security_alerts").select("headline", "created_at", "source", "event_type").order("created_at", desc=True).limit(20).execute()
for r in res.data:
    print(f"{r['created_at']} | {r['event_type']} | {r['source']} | {r['headline'][:50]}")
