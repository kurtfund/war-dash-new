import sys
import os

# 1. Bridge VITE_ variables to standard ones for the worker at the very top
if os.getenv("VITE_SUPABASE_URL") and not os.getenv("SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = os.getenv("VITE_SUPABASE_URL")


# Add the current directory to path so ingestion can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.worker import main

if __name__ == "__main__":
    print("[*] Starting Intelligence Worker from Root Shim...")
    main()
