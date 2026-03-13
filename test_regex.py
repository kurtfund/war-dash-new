import re

titles = [
    "UAE air defences intercept 7 ballistic missiles, 27 UAVs",
    "UAE announces successful interception of 3 missiles and 10 drones",
    "UAE defense forces intercept 1 ballistic missile and 2 uav",
    "UAE intercepts 5 drones"
]

for title in titles:
    title_lower = title.lower()
    missiles = 0
    drones = 0
    m_match = re.search(r'(\d+)\s*(?:ballistic\s*)?missiles?', title_lower)
    if m_match: missiles = int(m_match.group(1))
    d_match = re.search(r'(\d+)\s*(?:uavs?|drones?)', title_lower)
    if d_match: drones = int(d_match.group(1))
    
    print(f"TITLE: {title}")
    print(f"M: {missiles}, D: {drones}\n")
