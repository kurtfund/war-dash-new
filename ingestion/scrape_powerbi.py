import asyncio
import os
import re
import json
from playwright.async_api import async_playwright
from supabase import create_client, Client
from dotenv import load_dotenv

# Load Supabase credentials
load_dotenv()
load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Exiting.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
URL = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

def parse_inss_data(body_text):
    stats = {}
    
    # 1. Israeli Casualties
    # Example format: "Fatalities 14| Injured 2,888" -> need to match near "Israeli Casualties"
    israel_match = re.search(r'Israeli Casualties\s*Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    if israel_match:
        stats['israel_fatalities'] = israel_match.group(1).replace(',', '')
        stats['israel_injured'] = israel_match.group(2).replace(',', '')

    # 2. Lebanon Casualties
    lebanon_match = re.search(r'Lebanon Casualties\s*Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    if lebanon_match:
        stats['lebanon_fatalities'] = lebanon_match.group(1).replace(',', '')
        stats['lebanon_injured'] = lebanon_match.group(2).replace(',', '')
        
    # 3. Displaced Persons (Israel)
    displaced_il_match = re.search(r'Displaced Persons in Israel\s*~([\d,]+)', body_text, flags=re.IGNORECASE)
    if displaced_il_match:
        stats['displaced_israel'] = displaced_il_match.group(1).replace(',', '')

    # 4. Displaced Persons (Lebanon)
    displaced_lb_match = re.search(r'Displaced Persons in Lebanon\s*~([\d,]+)', body_text, flags=re.IGNORECASE)
    if displaced_lb_match:
        stats['displaced_lebanon'] = displaced_lb_match.group(1).replace(',', '')

    # 5. Targeted Killings
    targeted_match = re.search(r'Targeted Killings\s*~([\d,]+)', body_text, flags=re.IGNORECASE)
    if targeted_match:
        stats['targeted_killings'] = targeted_match.group(1).replace(',', '')
        
    # 6. Strikes in Iran
    strikes_us_match = re.search(r'American Strikes in Iran\s*[\n\r]*(\d+)', body_text, flags=re.IGNORECASE)
    strikes_il_match = re.search(r'Israeli Strikes in Iran\s*[\n\r]*(\d+)', body_text, flags=re.IGNORECASE)
    
    # Due to structure it might just be the numbers after "Israeli Strikes in Iran"
    if 'American Strikes in Iran' in body_text:
         # Find all large numbers in the general area
         strike_numbers = re.findall(r'\b([1-9]\d{2,})\b', body_text.split('Number of Strikes in Iran')[1][:100])
         if len(strike_numbers) >= 2:
             stats['iran_strikes_us'] = strike_numbers[0]
             stats['iran_strikes_israel'] = strike_numbers[1]

    return stats

async def main():
    print("Launching playwright to scrape INSS PowerBI...")
    stats = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")
        
        await asyncio.sleep(10) # Wait for renders
        body_text = await page.evaluate("document.body.innerText")
        stats = parse_inss_data(body_text)
        await browser.close()
        
    print("Parsed Stats:", stats)
    
    if stats and 'israel_fatalities' in stats: # Basic validation
        payload = {
            "source": "INSS",
            "source_url": URL,
            "headline": json.dumps(stats),
            "event_type": "INSS_STATS",
            "country": "Regional",
            "severity_score": 100
        }
        
        print("Uploading to Supabase...")
        res = supabase.table('security_alerts').insert(payload).execute()
        print("Upload successful!")
    else:
        print("Failed to parse critical stats. Aborting upload.")

if __name__ == "__main__":
    asyncio.run(main())
