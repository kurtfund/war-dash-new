import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from worker import should_filter_alert

# The problem alert
headline = "India news: Clashes erupt in Kolkata ahead of Modi rally"
source = "Deutsche Welle (DW)"
url = "https://www.dw.com/en/india..."

reject, reason, event_type, country = should_filter_alert(headline, source, url)

if reject:
    print(f"SUCCESS: Alert rejected. Reason: {reason}")
else:
    print("FAIL: Alert was NOT rejected!")
    
