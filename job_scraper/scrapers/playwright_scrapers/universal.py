"""Scrapers Playwright pour tous les sites universels"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.parse

async def scrape_wttj_async(keywords, location="France", contract_type=""):
    jobs = []
    print(f"[WTTJ] Démarrage scraping: '{keywords}' @ '{location}'")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.welcometothejungle.com/fr/jobs?query={urllib.parse.quote(keywords)}&aroundQuery={urllib.parse.quote(location)}"
            print(f"[WTTJ] URL: {url}")
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all('li[data-testid="search-results-list-item-wrapper"]')
            print(f"[WTTJ] {len(cards)} cartes trouvées")
            for card in cards[:10]:  # Limité à 10
                try:
                    title_el = await card.query_selector('h2')
                    company_el = await card.query_selector('span.sc-TezEC')
                    link_el = await card.query_selector('a[href*="/jobs/"]')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.welcometothejungle.com{link}"
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'WTTJ',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"[WTTJ] ERREUR: {e}")
        finally:
            await browser.close()
    print(f"[WTTJ] Retour: {len(jobs[:10])} offres (limité à 10)")
    return jobs[:10]

async def scrape_apec_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles={urllib.parse.quote(keywords)}"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(4000)
            
            cards = await page.query_selector_all('div[data-testid="offer-card"]')
            for card in cards[:10]:  # Limité à 10
                try:
                    title_el = await card.query_selector('h3[data-testid="offer-title"]')
                    company_el = await card.query_selector('span[data-testid="company-name"]')
                    link_el = await card.query_selector('a')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.apec.fr{link}"
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'APEC',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"APEC error: {e}")
        finally:
            await browser.close()
    return jobs[:10]

async def scrape_hellowork_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.hellowork.com/fr-fr/emplois.html?k={urllib.parse.quote(keywords)}"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all('div[data-testid="job-card"]')
            for card in cards[:30]:
                try:
                    title_el = await card.query_selector('h3')
                    company_el = await card.query_selector('span[data-testid="company-name"]')
                    link_el = await card.query_selector('a')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'HelloWork',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"HelloWork error: {e}")
        finally:
            await browser.close()
    return jobs[:10]

async def scrape_meteojob_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.meteojob.com/recherche-emploi?keywords={urllib.parse.quote(keywords)}"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all('div[data-testid="job-card"]')
            for card in cards[:30]:
                try:
                    title_el = await card.query_selector('h3')
                    company_el = await card.query_selector('span')
                    link_el = await card.query_selector('a')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'Meteojob',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"Meteojob error: {e}")
        finally:
            await browser.close()
    return jobs[:10]

async def scrape_regionsjob_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.regionsjob.com/emplois/{urllib.parse.quote(keywords)}.html"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all('div[data-testid="job-card"]')
            for card in cards[:30]:
                try:
                    title_el = await card.query_selector('h3')
                    company_el = await card.query_selector('span')
                    link_el = await card.query_selector('a')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'RegionsJob',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"RegionsJob error: {e}")
        finally:
            await browser.close()
    return jobs[:10]

async def scrape_monster_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            url = f"https://www.monster.fr/emplois/recherche/?q={urllib.parse.quote(keywords)}"
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(3000)
            
            cards = await page.query_selector_all('div[class*="job-card"], article[class*="job"]')
            for card in cards[:10]:  # Limité à 10
                try:
                    title_el = await card.query_selector('h2, h3, a[class*="title"]')
                    company_el = await card.query_selector('.company, span[class*="company"]')
                    link_el = await card.query_selector('a')
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location,
                        'link': link,
                        'source': 'Monster',
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
        except Exception as e:
            print(f"Monster error: {e}")
        finally:
            await browser.close()
    return jobs[:10]
