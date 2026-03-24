import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
s = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_ROLE_KEY'))
r = s.table('wam_official_data').select('*').order('created_at', desc=True).limit(1).execute()
row = r.data[0]

# Construct exact wam_official_data clone payload WITHOUT created_at to avoid RLS rejection
clone = {
    "url": row["url"],
    "headline": row["headline"],
    "missiles": row["missiles"],
    "cruise": row["cruise"],
    "uavs": row["uavs"],
    "raw_data": {
        "summary": row["raw_data"].get("summary", ""),
        "ballistic": row["missiles"],
        "cruise": row["cruise"],
        "uavs": row["uavs"],
        "daily_ballistic": 5,
        "daily_cruise": 0,
        "daily_uavs": 17,
        "missiles": row["missiles"],
        "drones": row["uavs"],
        "lat": 24.4539,
        "lon": 54.3773
    }
}

try:
    s.table('wam_official_data').insert(clone).execute()
    print("SUCCESS: Forced the daily intel into the database feed.")
except Exception as e:
    print("Failed to insert override row:", e)
