import re

full_text = "... intercepted nine ballistic missiles and 33 drones... Since the start of the blatant Iranian attacks, UAE air defence systems have intercepted 294 ballistic missiles, 15 cruise missiles and 1,600 drones."

word_to_num = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 
    'nineteen': 19, 'twenty': 20
}

def parse_num_match(m):
    m = m.lower().replace(',', '').strip()
    if m in word_to_num: return word_to_num[m]
    try: return int(m)
    except: return 0

ballistic = 0
cruise = 0
uavs = 0

num_pattern = r'(\d+(?:,\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)'

target_sentence_match = re.search(r'since the (?:onset|start|beginning)[^\.]+', full_text, re.IGNORECASE)

if target_sentence_match:
    target_sentence = target_sentence_match.group(0)
    print("Found target sentence:", target_sentence)
    
    b_matches = re.findall(num_pattern + r'\s+(?:ballistic\s*)?missiles?', target_sentence, re.IGNORECASE)
    print("b_matches:", b_matches)
    if b_matches: ballistic = max([parse_num_match(m) for m in b_matches])
    
    c_matches = re.findall(num_pattern + r'\s+cruise\s*missiles?', target_sentence, re.IGNORECASE)
    print("c_matches:", c_matches)
    if c_matches: cruise = max([parse_num_match(m) for m in c_matches])
    
    u_matches = re.findall(num_pattern + r'\s+(?:uavs?|drones?)', target_sentence, re.IGNORECASE)
    print("u_matches:", u_matches)
    if u_matches: uavs = max([parse_num_match(m) for m in u_matches])
else:
    print("No target sentence.")

print(f"B: {ballistic}, C: {cruise}, D: {uavs}")
