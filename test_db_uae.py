import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
if url and key:
    supabase = create_client(url, key)
    res = supabase.table('security_alerts').select('created_at', 'headline', 'country', 'raw_data', 'coordinates').execute()
    uae_alerts = []
    for r in res.data:
        loc_name = str(r.get('country') or '')
        if r.get('raw_data') and isinstance(r.get('raw_data'), dict):
            if 'loc_name' in r['raw_data']:
                loc_name = str(r['raw_data']['loc_name'])
        
        if "uae" in loc_name.lower() or "dubai" in loc_name.lower() or "dubai" in str(r.get('headline')).lower():
            uae_alerts.append(r)
            
    uae_alerts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    for a in uae_alerts[:3]:
        print(f"[{a['created_at']}] {a['headline']}")
        print(f"   -> coords: {a.get('coordinates')}")
        print("---")
    
    print("ALL LOCS:")
    for k, v in locs.items():
        if "uae" in str(k).lower() or "dubai" in str(k).lower() or "iran" in str(k).lower():
            print(f"{k}: {v}")
else:
    print('No credentials found in environment')
