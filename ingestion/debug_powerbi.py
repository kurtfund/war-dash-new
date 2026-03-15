import requests
import json
import re

url = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

response = requests.get(url)
content = response.text

# PowerBI usually embeds the config in the initial HTML
match = re.search(r'var config = (\{.*?\});', content)
if match:
    # We might have the config
    print("Found config!")
    config = json.loads(match.group(1))
    print(json.dumps(config, indent=2)[:500])
else:
    print("Could not find config block in HTML.")
