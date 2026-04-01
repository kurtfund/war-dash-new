import re

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
    strikes_match = re.search(r'(?:Number of Strikes in Iran|Israeli Strikes in Iran).*?American Strikes in Iran.*?([\d,]+)\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if strikes_match:
        stats['iran_strikes_israel'] = strikes_match.group(1).replace(',', '')
        stats['iran_strikes_us'] = strikes_match.group(2).replace(',', '')

    # ME Countries Specific
    chart_chunks = body_text.split("Casualties in the ME")
    for chunk in chart_chunks:
        chunk_lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        
        if any('us milit' in l.lower() or 'kurdistan' in l.lower() for l in chunk_lines[:20]):
            raw_labels = []
            raw_nums = []
            
            for line in chunk_lines[:70]:
                clean_line = line.replace(',', '')
                if clean_line.isdigit():
                    raw_nums.append(clean_line)
                else:
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
            break

    # Key Targets Struck by Iran
    target_chunks = body_text.split("Key Targets Struck by Iran in the ME")
    if len(target_chunks) > 1:
        chunk = target_chunks[1]
        chunk_lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        
        raw_labels = []
        raw_nums = []
        
        for line in chunk_lines[:40]: 
            if line.lower() in ["casualties in the me", "iranian casualties", "targeted killings"]: break
            
            clean_line = line.replace(',', '')
            if clean_line.isdigit():
                raw_nums.append(clean_line)
            else:
                if not raw_nums: 
                    cleaned_label = line.replace('…', '').strip()
                    if cleaned_label:
                        raw_labels.append(cleaned_label)
        
        key_targets = []
        for index, label in enumerate(raw_labels):
            val = raw_nums[index] if index < len(raw_nums) else "0"
            key_targets.append({"name": label, "count": val})
            
        if key_targets:
            stats['iran_key_targets'] = key_targets

    return stats

if __name__ == "__main__":
    with open('powerbi_dump.txt', 'r') as f:
        text = f.read()
    stats = parse_inss_data(text)
    for k, v in stats.items():
        print(f"{k}: {v}")
