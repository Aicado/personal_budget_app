import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 1200})

        # Go to the app
        await page.goto("http://localhost:5173")

        # Wait for data to load
        await page.wait_for_selector("text=Checking")

        # Click Expand Transactions
        await page.click("text=Expand Transactions")

        # Wait for the transactions to be fetched (or at least the table to appear)
        await page.wait_for_selector("table")

        # Take a screenshot of the expanded state
        await page.screenshot(path="expansion_details.png")

        # Verify the negative currency formatting if possible
        # Our sample data had -100.5
        negative_text = await page.query_selector("text=-$100.50")
        if negative_text:
            print("Verified negative currency formatting: -$100.50")
        else:
            print("Could not find -$100.50 in the UI")
            # Let's check what IS there
            content = await page.content()
            if "$-100.50" in content:
                 print("Found INCORRECT formatting: $-100.50")
            elif "$100.50" in content:
                 print("Found positive $100.50")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
