import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('dashboard/.env.local')
url = os.environ.get('VITE_SUPABASE_URL')
key = os.environ.get('VITE_SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('VITE_SUPABASE_ANON_KEY')
supabase = create_client(url, key)

res = supabase.table('security_alerts').select('id, headline').order('created_at', desc=True).limit(200).execute()
to_delete = []
seen_headlines = set()

import re

for row in res.data:
    low = row['headline'].lower()
    
    # 1. Check for out-of-scope regions or sports
    bad_words = ['azerbaijan', 'armenia', 'taiwan', 'china', 'football', 'asian cup', 'coach', 'stadium']
    if any(bw in low for bw in bad_words):
        to_delete.append(row['id'])
        print('Deleting Out-of-Scope:', row['headline'])
        continue
    
    # 2. Check for exact duplicate headlines (regardless of source)
    # Strip any trailing "- Source"
    cleaned_head = re.sub(r'\s+-\s+[^-]+$', '', low).strip()
    
    if cleaned_head in seen_headlines:
        to_delete.append(row['id'])
        print('Deleting Duplicate:', row['headline'])
    else:
        seen_headlines.add(cleaned_head)

for did in to_delete:
    supabase.table('security_alerts').delete().eq('id', did).execute()

print(f"Cleanup complete. Deleted {len(to_delete)} rows.")
