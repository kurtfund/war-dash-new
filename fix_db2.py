import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("VITE_SUPABASE_URL")
key = os.environ.get("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}"
}

# Delete OFFICIAL SUMMARY
r1 = requests.delete(f"{url}/rest/v1/security_alerts?event_type=eq.OFFICIAL_SUMMARY", headers=headers)
print("Deleted summaries status:", r1.status_code)

# Get the rows matching wsaz.com using the correct ilike syntax
# In PostgREST, ilike expects the pattern to be embedded in the query string 
r2 = requests.delete(f"{url}/rest/v1/security_alerts?url=ilike.*wsaz.com*", headers=headers)
print("Deleted wsaz status:", r2.status_code)
