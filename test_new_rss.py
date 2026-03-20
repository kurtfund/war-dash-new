import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingestion.worker import run_poll_cycle
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("NO SUPABASE CREDS")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Starting manual run_poll_cycle override...")
run_poll_cycle(supabase)
print("Done.")
