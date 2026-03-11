import os
import sys
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("dashboard/.env.local")
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("FATAL: Supabase credentials not found in env.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("[*] Fetching Live Market Data from Yahoo Finance...")
tickers = ['AED=X', 'NG=F', 'CL=F', 'GC=F', '^TASI.SR', '^VIX']
market_payload = {}

for t in tickers:
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{t}"
    try:
        r = requests.get(url, headers=COMMON_HEADERS, timeout=10)
        data = r.json()['chart']['result'][0]['meta']
        price = data['regularMarketPrice']
        prev_close = data['chartPreviousClose']
        pct_change = ((price - prev_close) / prev_close) * 100
        market_payload[t] = {"price": price, "change": pct_change}
        print(f"Success: {t} -> {price}")
    except Exception as e:
        print(f"Failed to fetch {t}: {e}")

if market_payload:
    now = datetime.utcnow()
    payload = {
        "headline": "Live Market Pulse Update",
        "source": "Yahoo Finance (Backend Auth)",
        "url": "https://finance.yahoo.com",
        "event_type": "MARKET_DATA",
        "country": "Global",
        "location_name": "Global Markets",
        "deaths": 0,
        "confidence": 1.0,
        "raw_data": market_payload,
        "created_at": now.isoformat()
    }
    
    response = supabase.table("security_alerts").insert(payload).execute()
    print("    [MARKET DATA INSERTED]")
    print(response.data)
else:
    print("No market payload generated.")
