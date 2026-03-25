import os
import sys
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scrape_powerbi import parse_inss_data, URL
from playwright.async_api import async_playwright

load_dotenv('../../.env')
url: str = os.environ.get("VITE_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Cannot find service role key!")
    sys.exit(1)

supabase: Client = create_client(url, key)

async def main():
    print("Scraping...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(8)
        body_text = await page.evaluate("document.body.innerText")
        stats = parse_inss_data(body_text)
        await browser.close()
        
    print("Uploading to isolated INSS table via Service Role...")
    payload = {
        "source_url": URL,
        "stats": stats
    }
    res = supabase.table('inss_casualties_data').insert(payload).execute()
    print("Upload successful!", len(res.data))

if __name__ == "__main__":
    asyncio.run(main())
