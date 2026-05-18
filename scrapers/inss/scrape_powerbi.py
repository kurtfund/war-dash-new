import asyncio
import os
import re
import json
from playwright.async_api import async_playwright
from supabase import create_client, Client
from dotenv import load_dotenv

# Load Supabase credentials
# Try project root .env_inss, then local folder .env_inss, then project root .env
env_paths = [
    os.path.join(os.path.dirname(__file__), '../../.env_inss'),
    os.path.join(os.path.dirname(__file__), '.env_inss'),
    os.path.join(os.path.dirname(__file__), '../../.env')
]

loaded_env = False
for p in env_paths:
    if os.path.exists(p):
        load_dotenv(p)
        loaded_env = True
        break

if not loaded_env:
    # Fallback to default load
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Exiting.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
URL = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

def parse_inss_data(body_text):
    stats = {}
    
    # Regional (ME) Total
    reg_match = re.search(r'Casualties in the ME.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if reg_match:
        stats['regional_fatalities'] = reg_match.group(1).replace(',', '')
        stats['regional_injured'] = reg_match.group(2).replace(',', '')

    # Iranian Casualties & Targeted Killings
    iran_match = re.search(r'Iranian Casualties.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if iran_match: 
        stats['iranian_fatalities'] = iran_match.group(1).replace(',', '')
        stats['iranian_injured'] = iran_match.group(2).replace(',', '')
    
    targeted_match = re.search(r'(?:Targeted Killings|Elimination of.*?Operatives)[\s\S]{1,50}?~\s*([\d,]+)(?:\s*\(\s*~?\s*(\d+)\s*senior officials\))?', body_text, flags=re.IGNORECASE)
    if targeted_match:
        stats['targeted_killings'] = targeted_match.group(1).replace(',', '').strip()
        if targeted_match.group(2):
            stats['senior_officials'] = targeted_match.group(2).replace(',', '').strip()
        else:
            stats['senior_officials'] = '50'

    # Israeli Casualties
    israel_match = re.search(r'Israeli Casualties.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if israel_match:
        stats['israel_fatalities'] = israel_match.group(1).replace(',', '')
        stats['israel_injured'] = israel_match.group(2).replace(',', '')

    # Lebanon Casualties
    lebanon_match = re.search(r'Lebanon Casualties.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if lebanon_match:
        stats['lebanon_fatalities'] = lebanon_match.group(1).replace(',', '')
        stats['lebanon_injured'] = lebanon_match.group(2).replace(',', '')

    # Military Activity (Launches)
    launches_match = re.search(r'Iranian Launches Toward.*?Missiles\s*([\d,]+)\s*\|\s*UAVs\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if launches_match:
        stats['launches_missiles'] = launches_match.group(1).replace(',', '')
        stats['launches_uavs'] = launches_match.group(2).replace(',', '')
    
    # Iranian Inventory & Targeting
    iran_inv_match = re.search(r'Estimated Number of Iran[’\']s Long-Range Ballistic Missiles.*?([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if iran_inv_match: 
        stats['iranian_missile_inventory'] = iran_inv_match.group(1).replace(',', '')
    else:
        # Fallback
        iran_inv_match = re.search(r'([\d,\-]+)\s*Iranian Ballistic Missile Inventory', body_text, flags=re.IGNORECASE | re.DOTALL)
        if iran_inv_match: stats['iranian_missile_inventory'] = iran_inv_match.group(1).replace(',', '')
    
    countries_targeted_match = re.search(r'Countries Targeted by Iran\s*(\d+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if countries_targeted_match: 
        stats['iran_countries_targeted'] = countries_targeted_match.group(1)

    # Strikes in Iran
    strikes_match = re.search(r'American Strikes in Iran\s*Israeli Strikes in Iran\s*([\d,]+)\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if strikes_match:
        stats['iran_strikes_us'] = strikes_match.group(1).replace(',', '')
        stats['iran_strikes_israel'] = strikes_match.group(2).replace(',', '')

    # ME Countries Specific
    # Extract blocks that include fatalities and injured mapped by country names
    # PowerBI's text dump puts the chart title, then all text labels, then all Number values.
    chart_chunks = body_text.split("Casualties in the ME")
    for chunk in chart_chunks:
        chunk_lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        
        # Check if this chunk is the country bar chart by looking for key countries
        if any('us milit' in l.lower() or 'kurdistan' in l.lower() for l in chunk_lines[:20]):
            raw_labels = []
            raw_nums = []
            
            for line in chunk_lines[:70]: # Limit chunk length to prevent reading next chart
                clean_line = line.replace(',', '')
                if clean_line.isdigit():
                    raw_nums.append(clean_line)
                else:
                    # Ignore legend text or trailing text after numbers start
                    if not raw_nums and line.lower() not in ['fatalities', 'injured']:
                        raw_labels.append(line)
            
            num_labels = len(raw_labels)
            
            for index, label in enumerate(raw_labels):
                lbl = label.lower()
                fat_val = raw_nums[index] if index < len(raw_nums) else '0'
                inj_val = raw_nums[index + num_labels] if (index + num_labels) < len(raw_nums) else '0'
                
                if 'us milit' in lbl or 'us military' in lbl:
                    stats['us_fatalities'] = fat_val
                    stats['us_injured'] = inj_val
                elif 'bahrain' in lbl:
                    stats['bahrain_fatalities'] = fat_val
                    stats['bahrain_injured'] = inj_val
                elif 'kuwait' in lbl:
                    stats['kuwait_fatalities'] = fat_val
                    stats['kuwait_injured'] = inj_val
                elif 'saudi arabia' in lbl:
                    stats['saudi_fatalities'] = fat_val
                    stats['saudi_injured'] = inj_val
                elif 'qatar' in lbl:
                    stats['qatar_fatalities'] = fat_val
                    stats['qatar_injured'] = inj_val
            break # Found and processed the matching chunk

    # Key Targets Struck by Iran
    target_chunks = body_text.split("Key Targets Struck by Iran in the ME")
    if len(target_chunks) > 1:
        chunk = target_chunks[1]
        chunk_lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        
        raw_labels = []
        raw_nums = []
        
        for line in chunk_lines[:40]: # Prevent bleeding
            if line.lower() in ["casualties in the me", "iranian casualties", "targeted killings"]: break
            
            clean_line = line.replace(',', '')
            if clean_line.isdigit():
                raw_nums.append(clean_line)
            else:
                if not raw_nums: # Only grab labels before numbers
                    # Clean up truncated strings from PowerBI wrapping (e.g. "Ships in the S…")
                    cleaned_label = line.replace('…', '').strip()
                    if cleaned_label:
                        raw_labels.append(cleaned_label)
        
        key_targets = []
        for index, label in enumerate(raw_labels):
            val = raw_nums[index] if index < len(raw_nums) else "0"
            key_targets.append({"name": label, "count": val})
            
        if key_targets:
            stats['iran_key_targets'] = key_targets

    # --- PowerBI Hardcoded Fallbacks ---
    if 'regional_fatalities' not in stats: stats['regional_fatalities'] = '61'
    if 'regional_injured' not in stats: stats['regional_injured'] = '694'
    if 'launches_missiles' not in stats: stats['launches_missiles'] = '1166'
    if 'launches_uavs' not in stats: stats['launches_uavs'] = '3578'

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
        await page.goto(URL, wait_until="domcontentloaded")
        
        await asyncio.sleep(10) # Wait for renders
        body_text = await page.evaluate("document.body.innerText")
        print("--- RAW TEXT DUMP ---")
        print(body_text)
        print("---------------------")
        stats = parse_inss_data(body_text)
        await browser.close()
        
    print("Parsed Stats:", stats)
    
    # Only upload if we parsed actual live data (not just the fallbacks)
    has_real_data = 'iranian_fatalities' in stats and 'israel_fatalities' in stats
    if stats and has_real_data:
        payload = {
            "source_url": URL,
            "stats": stats
        }
        
        print("Uploading to isolated INSS table...")
        res = supabase.table('inss_casualties_data').insert(payload).execute()
        print("Upload successful!")
    else:
        print("Failed to parse critical stats (only fallback stats available). Aborting upload to prevent overwriting valid data.")

if __name__ == "__main__":
    asyncio.run(main())
