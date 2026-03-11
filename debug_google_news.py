import feedparser
import requests

url = "https://news.google.com/rss/search?q=Israel+OR+Iran+OR+Lebanon+when:24h&hl=en-US&gl=US&ceid=US:en"
headers = {
    'User-Agent': 'Mozilla/5.0'
}
resp = requests.get(url, headers=headers, timeout=15)
feed = feedparser.parse(resp.content)

for entry in feed.entries[:5]:
    print(f"TITLE: {entry.title}")
    # Google News RSS entries often have a 'source' element
    source_name = "Unknown"
    if hasattr(entry, 'source'):
        source_name = entry.source.get('title', 'Unknown')
    elif ' - ' in entry.title:
        source_name = entry.title.split(' - ')[-1]
    
    print(f"DETECTED SOURCE: {source_name}")
    print(f"LINK: {entry.link}")
    print("-" * 30)
