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
    print("Running database cleanup to thin out high-volume sources and reset for feed variety...")
    
    # Identify high volume sources
    high_volume_sources = [
        "Asharq Al-Awsat",
        "Middle East Eye",
        "Anadolu Agency"
    ]
    
    # We fetch all the recent alerts from these sources
    for source in high_volume_sources:
        print(f"Cleaning out backlog for: {source}")
        
        # We pull the IDs of everything from this source
        res = supabase.table('security_alerts').select('id').eq('source', source).order('created_at', desc=True).limit(200).execute()
        
        if hasattr(res, 'data') and len(res.data) > 20: 
            # We keep the newest 20 of each, and delete the rest so the feed doesn't scroll forever with just them.
            ids_to_delete = [item['id'] for item in res.data[20:]]
            if ids_to_delete:
                print(f"Deleting {len(ids_to_delete)} historical entries for {source} to restore feed variety.")
                # Supabase Python SDK doesn't natively support "delete where ID in list" in a single call simply, so we loop batch.
                for i in range(0, len(ids_to_delete), 50):
                    batch = ids_to_delete[i:i+50]
                    supabase.table('security_alerts').delete().in_('id', batch).execute()

    print("Cleanup complete.")

if __name__ == "__main__":
    clean_db()
