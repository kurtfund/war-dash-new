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
    
    # 1. Regional Casualties (Middle East)
    reg_fatal_match = re.search(r'Casualties in the Middle East:\s*Fatalities:\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    reg_inj_match = re.search(r'Injured:\s*([\d,]+)', body_text[reg_fatal_match.end() if reg_fatal_match else 0:reg_fatal_match.end()+100 if reg_fatal_match else len(body_text)], flags=re.IGNORECASE)
    
    if reg_fatal_match: stats['regional_fatalities'] = reg_fatal_match.group(1).replace(',', '')
    if reg_inj_match: stats['regional_injured'] = reg_inj_match.group(1).replace(',', '')

    # 2. Iranian Casualties & Targeted Killings
    iran_fatal_match = re.search(r'Iranian Casualties:\s*Fatalities:\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    if iran_fatal_match: stats['iranian_fatalities'] = iran_fatal_match.group(1).replace(',', '')
    
    targeted_match = re.search(r'Targeted Killings:\s*~?([\d,]+)', body_text, flags=re.IGNORECASE)
    if targeted_match: stats['targeted_killings'] = targeted_match.group(1).replace(',', '')

    # 3. Military Activity & Inventory
    missiles_target_me_match = re.search(r'Launches Toward the Middle East:\s*Missiles:\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    uav_target_me_match = re.search(r'UAVs:\s*([\d,]+)', body_text[missiles_target_me_match.end() if missiles_target_me_match else 0:missiles_target_me_match.end()+100 if missiles_target_me_match else len(body_text)], flags=re.IGNORECASE)
    
    if missiles_target_me_match: stats['launches_missiles'] = missiles_target_me_match.group(1).replace(',', '')
    if uav_target_me_match: stats['launches_uavs'] = uav_target_me_match.group(1).replace(',', '')
    
    # 4. Iranian Inventory & Targeting
    iran_inv_match = re.search(r'Iranian Ballistic Missile Inventory:\s*([\d,\-]+)', body_text, flags=re.IGNORECASE)
    if iran_inv_match: stats['iranian_missile_inventory'] = iran_inv_match.group(1)
    
    countries_targeted_match = re.search(r'Countries Targeted by Iran:\s*(\d+)', body_text, flags=re.IGNORECASE)
    if countries_targeted_match: stats['iran_countries_targeted'] = countries_targeted_match.group(1)

    # 5. Strikes in Iran
    strikes_us_match = re.search(r'American Strikes\s*([\d,]+)', body_text, flags=re.IGNORECASE)
    if strikes_us_match: stats['iran_strikes_us'] = strikes_us_match.group(1).replace(',', '')
    
    strikes_il_match = re.search(r'Israeli Strikes\s*([\d,]+)', body_text[strikes_us_match.end() if strikes_us_match else 0:strikes_us_match.end()+100 if strikes_us_match else len(body_text)], flags=re.IGNORECASE)
    if strikes_il_match: stats['iran_strikes_israel'] = strikes_il_match.group(1).replace(',', '')

    # Fallback to older format parsing if new fields aren't found
    if 'iran_strikes_us' not in stats and 'American Strikes in Iran' in body_text:
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
    
    if stats and ('regional_fatalities' in stats or 'iran_strikes_us' in stats): # Validation based on new fields
        payload = {
            "source": "INSS",
            "url": URL,
            "headline": json.dumps(stats),
            "event_type": "INSS_STATS",
            "country": "Regional"
        }
        
        print("Uploading to Supabase...")
        res = supabase.table('security_alerts').insert(payload).execute()
        print("Upload successful!")
    else:
        print("Failed to parse critical stats. Aborting upload.")

if __name__ == "__main__":
    asyncio.run(main())
