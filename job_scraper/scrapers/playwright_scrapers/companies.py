"""Scraper Playwright pour tous les sites carrières"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from bs4 import BeautifulSoup

async def scrape_company_async(url, company_name, keywords, location="France"):
    """Scrape un site carrière avec Playwright"""
    jobs = []
    print(f"[{company_name}] Démarrage scraping: '{keywords}'")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print(f"[{company_name}] URL: {url}")
            await page.goto(url, timeout=15000)
            print(f"[{company_name}] Page chargée, attente 3s...")
            await page.wait_for_timeout(3000)
            
            # Accepter cookies
            try:
                await page.click('[id*="cookie"] button, [class*="cookie"] button, #didomi-notice-agree-button', timeout=2000)
                print(f"[{company_name}] Cookies acceptés")
            except:
                print(f"[{company_name}] Pas de popup cookies")
                pass
            
            # Scroll
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
            await page.wait_for_timeout(2000)
            print(f"[{company_name}] Scroll effectué")
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Trouver tous les liens
            all_links = soup.find_all('a', href=True)
            print(f"[{company_name}] {len(all_links)} liens trouvés")
            
            print(f"[{company_name}] {len(all_links)} liens trouvés")
            
            keywords_lower = keywords.lower().split()
            excluded = ['voir', 'toutes', 'nos offres', 'postulez', 'maintenant', 'choisir', 
                       'métier', 'carriere', 'careers', 'rejoindre', 'découvrir']
            
            candidates = 0
            for link in all_links:
                text = link.get_text().lower().strip()
                href = link['href']
                
                if any(excl in text for excl in excluded):
                    continue
                
                if len(text) < 10 or len(text) > 200:
                    continue
                
                job_patterns = ['job', 'career', 'offre', 'emploi', 'poste', 'opportunit']
                if not any(pattern in href.lower() for pattern in job_patterns):
                    continue
                
                candidates += 1
                
                if href.startswith('http'):
                    full_url = href
                else:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    full_url = base_url + href if href.startswith('/') else f"{base_url}/{href}"
                
                jobs.append({
                    'title': link.get_text().strip(),
                    'company': company_name,
                    'location': location,
                    'link': full_url,
                    'source': f'{company_name} Careers',
                    'scraped_at': datetime.now().isoformat()
                })
            
            print(f"[{company_name}] {candidates} liens candidats, {len(jobs)} offres extraites")
            
            # Dédupliquer
            seen = set()
            unique = []
            for job in jobs:
                if job['title'] not in seen:
                    seen.add(job['title'])
                    unique.append(job)
            
            await browser.close()
            print(f"[{company_name}] Retour: {len(unique[:10])} offres (limité à 10)")
            return unique[:10]
        
        except Exception as e:
            print(f"[{company_name}] ERREUR GLOBALE: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return []

async def scrape_all_companies_async(keywords, location="France", contract_type=""):
    """Scrape 5 entreprises seulement (au lieu de 15) pour éviter OOM"""
    print(f"[Companies] Démarrage scraping de 5 entreprises: '{keywords}'")
    companies = {
        'Bouygues': 'https://joining.bouygues.com/global/fr/search-results',
        'Alstom': 'https://jobsearch.alstom.com/search/',
        'Renault': 'https://www.renaultgroup.com/carrieres-renault/nos-offres-monde/',
        'Safran': 'https://www.safran-group.com/fr/offres',
        'Orange': 'https://orange.jobs/jobs/search.do',
    }
    
    print(f"[Companies] Lancement de {len(companies)} scrapers SÉQUENTIELLEMENT...")
    all_jobs = []
    for name, url in companies.items():
        try:
            result = await scrape_company_async(url, name, keywords, location)
            if isinstance(result, list):
                print(f"[Companies] {name}: {len(result)} offres")
                all_jobs.extend(result)
        except Exception as e:
            print(f"[Companies] {name} erreur: {e}")
    
    print(f"[Companies] Total: {len(all_jobs)} offres")
    return all_jobs
