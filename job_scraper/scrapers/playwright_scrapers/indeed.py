"""Scraper Indeed avec Playwright async"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.parse

async def scrape_indeed_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            url = f"https://fr.indeed.com/jobs?q={urllib.parse.quote(keywords)}&l={urllib.parse.quote(location)}"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            if 'cloudflare' in (await page.content()).lower():
                await browser.close()
                return []
            
            try:
                await page.click('#onetrust-accept-btn-handler', timeout=2000)
            except:
                pass
            
            cards = await page.query_selector_all("div.job_seen_beacon")
            
            for card in cards[:50]:
                try:
                    title_el = await card.query_selector("h2.jobTitle span")
                    company_el = await card.query_selector("span[data-testid='company-name']")
                    location_el = await card.query_selector("div[data-testid='text-location']")
                    link_el = await card.query_selector("h2.jobTitle a")
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and link.startswith("/"):
                        link = f"https://fr.indeed.com{link}"
                    
                    jobs.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "link": link,
                        "source": "Indeed",
                        "scraped_at": datetime.now().isoformat()
                    })
                except:
                    continue
        
        except Exception as e:
            print(f"Indeed error: {e}")
        
        finally:
            await browser.close()
    
    return jobs
