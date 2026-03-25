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
    
    targeted_match = re.search(r'Targeted Killings.*?~?([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if targeted_match: 
        stats['targeted_killings'] = targeted_match.group(1).replace(',', '')

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
    launches_match = re.search(r'Iranian Launches Toward the ME.*?Missiles\s*([\d,]+)\s*\|\s*UAVs\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if launches_match:
        stats['launches_missiles'] = launches_match.group(1).replace(',', '')
        stats['launches_uavs'] = launches_match.group(2).replace(',', '')
    
    # Iranian Inventory & Targeting
    iran_inv_match = re.search(r'Estimated Number of Iran[’\']s Long-Range Ballistic Missiles.*?([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if iran_inv_match: 
        stats['iranian_missile_inventory'] = iran_inv_match.group(1)
    else:
        # Fallback
        iran_inv_match = re.search(r'([\d,\-]+)\s*Iranian Ballistic Missile Inventory', body_text, flags=re.IGNORECASE | re.DOTALL)
        if iran_inv_match: stats['iranian_missile_inventory'] = iran_inv_match.group(1)
    
    countries_targeted_match = re.search(r'Countries Targeted by Iran\s*(\d+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if countries_targeted_match: 
        stats['iran_countries_targeted'] = countries_targeted_match.group(1)

    # Strikes in Iran
    strikes_match = re.search(r'Number of Strikes in Iran.*?Israeli Strikes in Iran.*?American Strikes in Iran.*?([\d,]+)\s*([\d,]+)', body_text, flags=re.IGNORECASE | re.DOTALL)
    if strikes_match:
        stats['iran_strikes_israel'] = strikes_match.group(1).replace(',', '')
        stats['iran_strikes_us'] = strikes_match.group(2).replace(',', '')

    # ME Countries Specific
    # The block starts with "Casualties in the ME" (second occurrence) or we can just find the list of names.
    # It ends with "Fatalities\nInjured"
    me_block_match = re.search(r'Casualties in the ME\s*\n(US Milit.*?)\nFatalities\nInjured', body_text, flags=re.IGNORECASE | re.DOTALL)
    if me_block_match:
        lines = [line.strip() for line in me_block_match.group(1).split('\n') if line.strip()]
        # We expect N labels, N fatalities, N injured. Total 3N lines.
        # But some labels might be split or varying.
        # Let's count back: the last 2N lines are numbers, the first N lines are strings.
        # Actually it's exactly 13 countries. So 39 lines.
        # Let's dynamically find where numbers start.
        first_num_idx = -1
        for i, line in enumerate(lines):
            if line.isdigit():
                first_num_idx = i
                break
        
        if first_num_idx != -1:
            labels = lines[:first_num_idx]
            numbers = lines[first_num_idx:]
            half = len(numbers) // 2
            fatalities = numbers[:half]
            injured = numbers[half:]
            
            for index, label in enumerate(labels):
                lbl = label.lower()
                if 'us milit' in lbl:
                    stats['us_fatalities'] = fatalities[index]
                    stats['us_injured'] = injured[index]
                elif 'bahrain' in lbl:
                    stats['bahrain_fatalities'] = fatalities[index]
                    stats['bahrain_injured'] = injured[index]
                elif 'kuwait' in lbl:
                    stats['kuwait_fatalities'] = fatalities[index]
                    stats['kuwait_injured'] = injured[index]
                elif 'saudi arabia' in lbl:
                    stats['saudi_fatalities'] = fatalities[index]
                    stats['saudi_injured'] = injured[index]
                elif 'qatar' in lbl:
                    stats['qatar_fatalities'] = fatalities[index]
                    stats['qatar_injured'] = injured[index]

    return stats

if __name__ == "__main__":
    with open('/Users/kirkspencer/Documents/war-dash-new/powerbi_dump.txt', 'r') as f:
        text = f.read()
    stats = parse_inss_data(text)
    for k, v in stats.items():
        print(f"{k}: {v}")
