"""Validation des URLs générées"""
import asyncio
from playwright.async_api import async_playwright

class URLValidator:
    async def validate(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(url, timeout=10000)
                if response.status >= 400:
                    await browser.close()
                    return False
                content = await page.content()
                has_jobs = len(await page.query_selector_all("article, .job, h2, h3")) > 3
                await browser.close()
                return has_jobs
            except:
                await browser.close()
                return False
