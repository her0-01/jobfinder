"""Découverte automatique de nouveaux jobboards"""
import asyncio
from playwright.async_api import async_playwright

class SiteDiscoverer:
    async def discover(self, keywords=None):
        """Découvre automatiquement de nouveaux jobboards via Google"""
        if not keywords:
            keywords = ["site emploi france", "jobboard france", "offres emploi"]
        
        discovered = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for keyword in keywords:
                try:
                    await page.goto(f"https://www.google.com/search?q={keyword}")
                    await page.wait_for_timeout(2000)
                    
                    links = await page.query_selector_all("a")
                    for link in links[:50]:
                        href = await link.get_attribute("href")
                        if href and self._is_jobboard(href):
                            discovered.append({
                                "url": href,
                                "keyword": keyword,
                                "status": "discovered"
                            })
                except:
                    continue
            
            await browser.close()
        
        return self._deduplicate(discovered)
    
    def _is_jobboard(self, url):
        keywords = ["job", "emploi", "career", "carriere", "recrutement", "offre"]
        return any(k in url.lower() for k in keywords)
    
    def _deduplicate(self, sites):
        seen = set()
        unique = []
        for site in sites:
            domain = site["url"].split("/")[2] if "/" in site["url"] else site["url"]
            if domain not in seen:
                seen.add(domain)
                unique.append(site)
        return unique
