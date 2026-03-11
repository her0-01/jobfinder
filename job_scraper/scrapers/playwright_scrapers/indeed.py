"""Scraper Indeed avec Playwright async"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.parse

async def scrape_indeed_async(keywords, location="France", contract_type=""):
    jobs = []
    print(f"[Indeed] Démarrage scraping: '{keywords}' @ '{location}'")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            url = f"https://fr.indeed.com/jobs?q={urllib.parse.quote(keywords)}&l={urllib.parse.quote(location)}"
            print(f"[Indeed] URL: {url}")
            await page.goto(url, timeout=15000)
            print(f"[Indeed] Page chargée, attente 3s...")
            await page.wait_for_timeout(3000)
            
            content = await page.content()
            if 'cloudflare' in content.lower():
                print(f"[Indeed] Cloudflare détecté, abandon")
                await browser.close()
                return []
            
            print(f"[Indeed] Pas de Cloudflare, recherche cookies...")
            try:
                await page.click('#onetrust-accept-btn-handler', timeout=2000)
                print(f"[Indeed] Cookies acceptés")
            except:
                print(f"[Indeed] Pas de popup cookies")
                pass
            
            cards = await page.query_selector_all("div.job_seen_beacon")
            print(f"[Indeed] {len(cards)} cartes trouvées")
            
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
                except Exception as card_error:
                    print(f"[Indeed] Erreur carte: {card_error}")
                    continue
            
            print(f"[Indeed] {len(jobs)} offres extraites")
        
        except Exception as e:
            print(f"[Indeed] ERREUR GLOBALE: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    print(f"[Indeed] Retour: {len(jobs)} offres")
    return jobs
