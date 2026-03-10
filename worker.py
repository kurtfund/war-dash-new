import sys
import os

# Add the current directory to path so ingestion can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.worker import main

if __name__ == "__main__":
    print("[*] Starting Intelligence Worker from Root Shim...")
    main()
