import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
if url and key:
    supabase = create_client(url, key)
    # Fetch the row
    res = supabase.table('wam_official_data').select('*').order('created_at', desc=True).limit(1).execute()
    if res.data:
        row = res.data[0]
        rd = row.get('raw_data', {})
        if rd:
            rd['daily_ballistic'] = 5
            rd['daily_cruise'] = 0
            rd['daily_uavs'] = 17
            
            supabase.table('wam_official_data').update({'raw_data': rd}).eq('id', row['id']).execute()
            print("Successfully backfilled the Daily Intel metrics onto the active WAM summary row!")
    else:
        print("No wam records found")
else:
    print('No credentials found')
