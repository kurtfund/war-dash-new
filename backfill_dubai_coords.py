import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
if url and key:
    supabase = create_client(url, key)
    res = supabase.table('security_alerts').select('id', 'source', 'headline', 'raw_data').execute()
    updates = 0
    for r in res.data:
        src = str(r.get('source')).lower()
        if "khaleej" in src or "gulf news" in src or "the national" in src:
            rd = r.get('raw_data', {})
            # Only update if they were dumped in Middle East Regional or have no coords
            lat = rd.get('lat')
            if lat == 28.0 or lat is None or lat == 25.0:
                rd['lat'] = 25.2048
                rd['lon'] = 55.2708
                supabase.table('security_alerts').update({'raw_data': rd}).eq('id', r['id']).execute()
                updates += 1
                print(f"Updated Alert ID: {r['id']} ({src}) - {r['headline'][:30]}")
    print(f"Total Dubai Rows Backfilled: {updates}")
else:
    print('No credentials found')
