"""Analyse automatique des sites découverts (reverse engineering)"""
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs

class SiteAnalyzer:
    async def analyze(self, site_url):
        """Analyse un site pour détecter les patterns d'URL"""
        test_queries = [
            {"keywords": "python developer", "location": "Paris"},
            {"keywords": "data scientist", "location": "Lyon"},
            {"keywords": "devops engineer", "location": "Marseille"}
        ]
        
        urls = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for query in test_queries:
                try:
                    await page.goto(site_url, timeout=10000)
                    
                    # Détecter champs de recherche
                    search_input = await page.query_selector("input[type='search'], input[name*='q'], input[placeholder*='recherche']")
                    location_input = await page.query_selector("input[name*='location'], input[name*='lieu']")
                    
                    if search_input:
                        await search_input.fill(query["keywords"])
                    if location_input:
                        await location_input.fill(query["location"])
                    
                    # Cliquer rechercher
                    submit_btn = await page.query_selector("button[type='submit'], input[type='submit']")
                    if submit_btn:
                        await submit_btn.click()
                        await page.wait_for_load_state("networkidle", timeout=5000)
                    
                    urls.append(page.url)
                except:
                    continue
            
            await browser.close()
        
        return self._extract_pattern(urls, test_queries)
    
    def _extract_pattern(self, urls, queries):
        """Extrait le pattern d'URL"""
        if not urls:
            return {}
        
        parsed = urlparse(urls[0])
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        params_map = {}
        for i, url in enumerate(urls):
            params = parse_qs(urlparse(url).query)
            for key, value in params.items():
                if queries[i]["keywords"].lower() in str(value).lower():
                    params_map["keywords"] = key
                if queries[i]["location"].lower() in str(value).lower():
                    params_map["location"] = key
        
        return {
            "base_url": base_url,
            "params": params_map,
            "pattern": self._build_pattern(base_url, params_map)
        }
    
    def _build_pattern(self, base_url, params):
        if not params:
            return base_url
        param_str = "&".join([f"{v}={{{k}}}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
