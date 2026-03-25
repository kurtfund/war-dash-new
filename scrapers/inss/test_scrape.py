import asyncio
from playwright.async_api import async_playwright

URL = "https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"

async def main():
    print("Launching playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        print("Navigating...")
        await page.goto(URL, wait_until="domcontentloaded")
        print("Sleeping 10s...")
        await asyncio.sleep(10)
        print("Evaluating...")
        body_text = await page.evaluate("document.body.innerText")
        with open("powerbi_dump.txt", "w") as f:
            f.write(body_text)
        print("Done. Saved to powerbi_dump.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
