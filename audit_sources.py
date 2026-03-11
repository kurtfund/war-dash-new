import requests
import feedparser
import sys
import os

from ingestion.worker import should_filter_alert, get_clean_source_name

COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

import urllib3
urllib3.disable_warnings()

urls = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"
]

import requests
for url in urls:
    print(f"\n--- AUDITING: {url} ---")
    resp = requests.get(url, headers=COMMON_HEADERS, verify=False)
    feed = feedparser.parse(resp.content)
    print(f"Total entries found: {len(feed.entries)}")
    
    passed = 0
    for entry in feed.entries[:15]:
        headline = entry.title
        source = get_clean_source_name(entry.link, headline)
        should_reject, reason, event_type, country = should_filter_alert(headline, source, entry.link)
        
        status = "REJECTED" if should_reject else "PASSED"
        print(f"[{status}] Source: {source} | {headline[:60]}...")
        if should_reject:
            print(f"    Reason: {reason}")

print("\n--- MANUAL BYPASS TEST ---")
test_cases = [
    ("Putin warns of escalation in Iran", "Google News"),
    ("Trump discusses Israel security", "Google News"),
    ("Russia deployment in Syria confirmed", "LiveUAMap"),
    ("Ukraine forces reclaim Bakhmut", "BBC News"),
    ("Zelenskyy visits front lines", "Reuters")
]

for headline, source in test_cases:
    url = f"https://example.com/{source.lower()}"
    should_reject, reason, event_type, country = should_filter_alert(headline, source, url)
    status = "PASSED (By-pass)" if not should_reject else "REJECTED"
    print(f"[{status}] {headline}")
    if should_reject:
        print(f"    Reason: {reason}")
    
