"""Orchestrateur async avec asyncio.gather()"""
import asyncio
from scrapers.playwright_scrapers.indeed import scrape_indeed_async
from scrapers.playwright_scrapers.linkedin import scrape_linkedin_async

class AsyncOrchestrator:
    def __init__(self):
        self.results = []
        self.progress = {}
    
    async def run_all(self, keywords, location, contract_type):
        """Exécute tous les scrapers en parallèle avec asyncio.gather()"""
        tasks = [
            self._run_scraper("Indeed", scrape_indeed_async(keywords, location, contract_type)),
            self._run_scraper("LinkedIn", scrape_linkedin_async(keywords, location, contract_type)),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
        
        return all_jobs
    
    async def _run_scraper(self, name, coro):
        """Exécute un scraper avec gestion d'erreur"""
        self.progress[name] = {"status": "running"}
        try:
            jobs = await coro
            self.progress[name] = {"status": "done", "count": len(jobs)}
            return jobs
        except Exception as e:
            self.progress[name] = {"status": "error", "error": str(e)}
            return []
