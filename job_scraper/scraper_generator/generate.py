"""Génération automatique de scrapers Playwright"""
import asyncio
from playwright.async_api import async_playwright

class ScraperGenerator:
    async def generate(self, site_url, site_name):
        """Génère automatiquement un scraper pour un site"""
        selectors = await self._detect_selectors(site_url)
        code = self._generate_code(site_name, site_url, selectors)
        
        filepath = f"scrapers/playwright_scrapers/generated_{site_name.lower()}.py"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        
        return filepath
    
    async def _detect_selectors(self, url):
        """Détecte automatiquement les sélecteurs CSS"""
        selectors = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_timeout(2000)
                
                # Détecter blocs d'offres
                job_containers = await page.query_selector_all("article, .job, [class*='offer'], [class*='job-card']")
                
                if job_containers:
                    first_job = job_containers[0]
                    
                    # Détecter titre
                    title = await first_job.query_selector("h2, h3, [class*='title']")
                    if title:
                        selectors["title"] = "h2, h3"
                    
                    # Détecter entreprise
                    company = await first_job.query_selector("[class*='company'], [class*='entreprise']")
                    if company:
                        selectors["company"] = "[class*='company']"
                    
                    # Détecter localisation
                    location = await first_job.query_selector("[class*='location'], [class*='lieu']")
                    if location:
                        selectors["location"] = "[class*='location']"
                    
                    # Détecter lien
                    link = await first_job.query_selector("a")
                    if link:
                        selectors["link"] = "a"
                    
                    selectors["container"] = "article, .job, [class*='offer']"
            
            except:
                pass
            
            await browser.close()
        
        return selectors
    
    def _generate_code(self, site_name, site_url, selectors):
        """Génère le code Python du scraper"""
        return f'''"""Scraper auto-généré pour {site_name}"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def scrape_{site_name.lower()}_async(keywords, location="France", contract_type=""):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("{site_url}", timeout=15000)
            await page.wait_for_timeout(2000)
            
            containers = await page.query_selector_all("{selectors.get('container', 'article')}")
            
            for container in containers[:50]:
                try:
                    title_el = await container.query_selector("{selectors.get('title', 'h2')}")
                    company_el = await container.query_selector("{selectors.get('company', 'span')}")
                    location_el = await container.query_selector("{selectors.get('location', 'span')}")
                    link_el = await container.query_selector("{selectors.get('link', 'a')}")
                    
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "N/A"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    jobs.append({{
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "link": link,
                        "source": "{site_name}",
                        "scraped_at": datetime.now().isoformat()
                    }})
                except:
                    continue
        
        except Exception as e:
            print(f"{site_name} error: {{e}}")
        
        finally:
            await browser.close()
    
    return jobs
'''
