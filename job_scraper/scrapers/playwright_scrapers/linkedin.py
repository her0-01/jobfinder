"""Scraper LinkedIn avec Playwright async"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.parse

async def scrape_linkedin_async(keywords, location="France", contract_type=""):
    jobs = []
    print(f"[LinkedIn] Démarrage scraping: '{keywords}' @ '{location}'")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(keywords)}&location={urllib.parse.quote(location)}"
            print(f"[LinkedIn] URL: {url}")
            await page.goto(url, timeout=15000)
            print(f"[LinkedIn] Page chargée, attente 3s...")
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all("div.base-card")
            print(f"[LinkedIn] {len(cards)} cartes trouvées")
            
            for card in cards[:10]:  # Limité à 10 offres
                try:
                    title_el = await card.query_selector("h3")
                    company_el = await card.query_selector("h4")
                    location_el = await card.query_selector("span.job-search-card__location")
                    link_el = await card.query_selector("a.base-card__full-link")
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "link": link,
                        "source": "LinkedIn",
                        "scraped_at": datetime.now().isoformat()
                    })
                except Exception as card_error:
                    print(f"[LinkedIn] Erreur carte: {card_error}")
                    continue
            
            print(f"[LinkedIn] {len(jobs)} offres extraites")
        
        except Exception as e:
            print(f"[LinkedIn] ERREUR GLOBALE: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    print(f"[LinkedIn] Retour: {len(jobs[:10])} offres (limité à 10)")
    return jobs[:10]  # Limité à 10
