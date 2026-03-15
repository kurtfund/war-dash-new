import asyncio
from playwright.async_api import async_playwright
import re

URL = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

async def main():
    print("Launching playwright to scrape INSS PowerBI...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")
        
        await asyncio.sleep(10) # Wait for renders
        body_text = await page.evaluate("document.body.innerText")
        print("--- BODY TEXT START ---")
        print(body_text)
        print("--- BODY TEXT END ---")

        strikes_match = re.search(r'American Strikes in Iran\s*Israeli Strikes in Iran\s*([\d,]+)\s*([\d,]+)', body_text, flags=re.IGNORECASE)
        if strikes_match:
            print(f"Match 1: {strikes_match.group(1)}")
            print(f"Match 2: {strikes_match.group(2)}")
        else:
            print("Regex for strikes failed. Let's look for 'Strikes in Iran'...")
            find_strikes = re.findall(r'.{0,30}Strikes in Iran.{0,30}', body_text, flags=re.IGNORECASE)
            print("Found near 'Strikes in Iran':", find_strikes)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
