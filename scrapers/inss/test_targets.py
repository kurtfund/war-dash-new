import re

with open('powerbi_dump.txt', 'r') as f:
    body_text = f.read()

target_chunks = body_text.split("Key Targets Struck by Iran in the ME")
if len(target_chunks) > 1:
    chunk = target_chunks[1]
    chunk_lines = [line.strip() for line in chunk.split('\n') if line.strip()]
    
    raw_labels = []
    raw_nums = []
    
    for line in chunk_lines[:40]: # Prevent bleeding
        if line.lower() in ["casualties in the me", "iranian casualties", "targeted killings"]: 
            break
        
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
        
    print("Found key targets:")
    print(key_targets)
else:
    print("Could not find 'Key Targets Struck by Iran in the ME'")
