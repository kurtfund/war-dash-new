import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
if url and key:
    supabase = create_client(url, key)
    res = supabase.table('security_alerts').select('id', 'raw_data').eq('event_type', 'OFFICIAL_SUMMARY').execute()
    updates = 0
    for r in res.data:
        rd = r.get('raw_data', {})
        if 'lat' not in rd or 'lon' not in rd:
            rd['lat'] = 24.4539
            rd['lon'] = 54.3773
            supabase.table('security_alerts').update({'raw_data': rd}).eq('id', r['id']).execute()
            updates += 1
            print(f"Updated Alert ID: {r['id']}")
    print(f"Total Rows Backfilled: {updates}")
else:
    print('No credentials found in environment')
