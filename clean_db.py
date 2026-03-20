import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('.env_inss')

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Exiting.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_db():
    print("Running database cleanup to purge old aviation/business alerts...")
    # Delete alerts that talk about flights or airlines based on our new banned keywords
    for keyword in ["flight", "flights", "airline", "airlines", "aviation", "economy", "stocks", "earnings", "business", "airport"]:
        res = supabase.table('security_alerts').delete().ilike('headline', f'%{keyword}%').execute()
        if hasattr(res, 'data') and len(res.data) > 0:
            print(f"Deleted {len(res.data)} alerts matching '{keyword}'")

if __name__ == "__main__":
    clean_db()
