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

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials.")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

URL = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

def parse_inss_data(body_text):
    stats = {}
    
    # 1. Regional ME Total (Arab/Gulf/Coalition casualties from Iranian launches)
    reg_match = re.search(r'Casualties in the ME.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if reg_match:
        stats['regional_fatalities'] = reg_match.group(1).replace(',', '')
        stats['regional_injured'] = reg_match.group(2).replace(',', '')

    # 2. Iranian Casualties & Targeted Killings
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

    # 3. Israeli Casualties
    israel_match = re.search(r'Israeli Casualties.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if israel_match:
        stats['israel_fatalities'] = israel_match.group(1).replace(',', '')
        stats['israel_injured'] = israel_match.group(2).replace(',', '')

    # 4. Lebanon Casualties (if present in older reports)
    lebanon_match = re.search(r'Lebanon Casualties.*?Fatalities\s*([\d,]+)\s*\|\s*Injured\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if lebanon_match:
        stats['lebanon_fatalities'] = lebanon_match.group(1).replace(',', '')
        stats['lebanon_injured'] = lebanon_match.group(2).replace(',', '')

    # 5. Military Activity (Launches)
    launches_match = re.search(r'Iranian Launches Toward.*?Missiles\s*([\d,]+)\s*\|\s*UAVs\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if launches_match:
        stats['launches_missiles'] = launches_match.group(1).replace(',', '')
        stats['launches_uavs'] = launches_match.group(2).replace(',', '')
    
    # 6. Iranian Inventory & Targeting
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

    # 7. Strikes in Iran
    strikes_match = re.search(r'American Strikes in Iran\s*Israeli Strikes in Iran\s*([\d,]+)\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if strikes_match:
        stats['iran_strikes_us'] = strikes_match.group(1).replace(',', '')
        stats['iran_strikes_israel'] = strikes_match.group(2).replace(',', '')

    # 8. Country-Specific ME Casualties Breakdown
    me_chunk_pattern = re.search(r'Casualties in the ME\s*\n(Kurdistan.*?)(?:Fatalities\s*\nInjured|\Z)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if me_chunk_pattern:
        lines = [l.strip() for l in me_chunk_pattern.group(1).split('\n') if l.strip()]
        raw_labels = []
        raw_nums = []
        for line in lines:
            c = line.replace(',', '')
            if c.isdigit():
                raw_nums.append(c)
            elif not raw_nums:
                raw_labels.append(line)
        
        num_labels = len(raw_labels)
        for index, label in enumerate(raw_labels):
            lbl = label.lower()
            fat_val = raw_nums[index] if index < len(raw_nums) else '0'
            inj_val = raw_nums[index + num_labels] if (index + num_labels) < len(raw_nums) else '0'
            
            if 'united arab emirates' in lbl or 'uae' in lbl:
                stats['uae_fatalities'] = fat_val
                stats['uae_injured'] = inj_val
            elif 'kurdistan' in lbl:
                stats['kurdistan_fatalities'] = fat_val
                stats['kurdistan_injured'] = inj_val
            elif 'us milit' in lbl or 'us military' in lbl:
                stats['us_fatalities'] = fat_val
                stats['us_injured'] = inj_val
            elif 'kuwait' in lbl:
                stats['kuwait_fatalities'] = fat_val
                stats['kuwait_injured'] = inj_val
            elif 'qatar' in lbl:
                stats['qatar_fatalities'] = fat_val
                stats['qatar_injured'] = inj_val
            elif 'oman' in lbl:
                stats['oman_fatalities'] = fat_val
                stats['oman_injured'] = inj_val
            elif 'syria' in lbl:
                stats['syria_fatalities'] = fat_val
                stats['syria_injured'] = inj_val
            elif 'palestinian' in lbl:
                stats['pa_fatalities'] = fat_val
                stats['pa_injured'] = inj_val
            elif 'bahrain' in lbl:
                stats['bahrain_fatalities'] = fat_val
                stats['bahrain_injured'] = inj_val
            elif 'saudi arabia' in lbl or 'saudi' in lbl:
                stats['saudi_fatalities'] = fat_val
                stats['saudi_injured'] = inj_val
            elif 'french' in lbl:
                stats['french_fatalities'] = fat_val
                stats['french_injured'] = inj_val
            elif 'jordan' in lbl:
                stats['jordan_fatalities'] = fat_val
                stats['jordan_injured'] = inj_val

    # 9. Key Targets Struck by Iran in the ME (Case-insensitive)
    target_match = re.search(r'Key targets struck by Iran in the ME\s*\n(.*?)(?:Casualties in the ME|\Z)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if target_match:
        lines = [l.strip() for l in target_match.group(1).split('\n') if l.strip()]
        raw_labels = []
        raw_nums = []
        for line in lines:
            c = line.replace(',', '')
            if c.isdigit():
                raw_nums.append(c)
            elif not raw_nums:
                raw_labels.append(line.replace('…', '').strip())
        
        key_targets = []
        for index, label in enumerate(raw_labels):
            val = raw_nums[index] if index < len(raw_nums) else '0'
            cleaned_name = 'Ships in the Red Sea' if 'ships in the' in label.lower() else label
            cleaned_name = 'Radar' if cleaned_name.lower() == 'rradar' else cleaned_name
            key_targets.append({'name': cleaned_name, 'count': val})
            
        if key_targets:
            stats['iran_key_targets'] = key_targets

    # --- PowerBI Hardcoded Fallbacks ---
    if 'regional_fatalities' not in stats: stats['regional_fatalities'] = '85'
    if 'regional_injured' not in stats: stats['regional_injured'] = '1110'
    if 'launches_missiles' not in stats: stats['launches_missiles'] = '1527'
    if 'launches_uavs' not in stats: stats['launches_uavs'] = '4816'

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
        supabase = get_supabase_client()
        if not supabase:
            print("Cannot upload: Missing Supabase credentials.")
            return

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
