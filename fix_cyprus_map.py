import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env_inss')

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Exiting.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fix_cyprus():
    # Find the article that contains "Abdullah bin Zayed" and mapping it to the UAE map
    print("Finding the mislocated article...")
    # First search for any alert from today or recently with that headline
    query = supabase.table("security_alerts").select("id, headline, location_name, coordinates").ilike("headline", "%Abdullah bin Zayed%").execute()
    
    if len(query.data) == 0:
        # try another hint
        query = supabase.table("security_alerts").select("id, headline, location_name, coordinates").ilike("headline", "%discuss in Nicosia%").execute()
    
    if len(query.data) > 0:
        for alert in query.data:
            print(f"Found: {alert['headline']}")
            print(f"Current Location: {alert['location_name']}, Coordinates: {alert['coordinates']}")
            
            # Abu Dhabi UAE Coordinates
            res = supabase.table("security_alerts").update({
                "location_name": "Abu Dhabi (UAE)",
                "coordinates": "POINT(54.3773 24.4539)"
            }).eq("id", alert["id"]).execute()
            
            print(f"Updated article {alert['id']} to Abu Dhabi (UAE).")
    else:
        print("No matching alerts found.")

if __name__ == "__main__":
    fix_cyprus()
