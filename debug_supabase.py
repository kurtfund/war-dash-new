import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('dashboard/.env')

url = os.environ.get("VITE_SUPABASE_URL")
key = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not url or not key:
    print("Missing credentials")
    sys.exit(1)

supabase: Client = create_client(url, key)

print("Checking for INSS_STATS...")
res = supabase.table('security_alerts').select('*').eq('event_type', 'INSS_STATS').order('created_at', desc=True).limit(5).execute()
print(f"Found {len(res.data)} INSS_STATS records.")
for r in res.data:
    print(r['headline'], r['created_at'])

print("\nChecking for SYSTEM ERRORs...")
res = supabase.table('security_alerts').select('*').ilike('headline', '%SYSTEM ERROR%').order('created_at', desc=True).limit(5).execute()
print(f"Found {len(res.data)} SYSTEM ERROR records.")
for r in res.data:
    print(r['headline'], r['created_at'])

print("\nChecking for OFFICIAL_SUMMARY...")
res = supabase.table('security_alerts').select('headline, created_at, raw_data').eq('event_type', 'OFFICIAL_SUMMARY').order('created_at', desc=True).limit(5).execute()
print(f"Found {len(res.data)} OFFICIAL_SUMMARY records.")
for r in res.data:
    print(r['created_at'], r['raw_data'])
