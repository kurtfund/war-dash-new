import sys
import os

# Add the current directory to path so ingestion can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.worker import main

if __name__ == "__main__":
    # Bridge VITE_ variables to standard ones for the worker
    if os.getenv("VITE_SUPABASE_URL") and not os.getenv("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = os.getenv("VITE_SUPABASE_URL")
    if os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
    elif os.getenv("VITE_SUPABASE_ANON_KEY") and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.getenv("VITE_SUPABASE_ANON_KEY")

    print("[*] Starting Intelligence Worker from Root Shim...")
    main()
