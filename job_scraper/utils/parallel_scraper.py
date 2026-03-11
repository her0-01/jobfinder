"""Orchestrateur parallèle pour scraping ultra-rapide"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class ParallelScraper:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.results = []
        self.progress = {}
        self.stop_flag = False
    
    def run_parallel(self, scrapers, keywords, location, contract_type):
        """Exécute les scrapers en parallèle"""
        self.stop_flag = False
        self.results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for i, (name, scraper_func, scraper_obj) in enumerate(scrapers, 1):
                if self.stop_flag:
                    break
                
                future = executor.submit(
                    self._run_single,
                    name, scraper_func, scraper_obj, keywords, location, contract_type, i, len(scrapers)
                )
                futures.append(future)
            
            # Attendre tous les résultats
            for future in futures:
                if not self.stop_flag:
                    try:
                        jobs = future.result(timeout=30)
                        if jobs:
                            self.results.extend(jobs)
                    except Exception as e:
                        print(f"Erreur scraper: {e}")
        
        return self.results
    
    def _run_single(self, name, scraper_func, scraper_obj, keywords, location, contract_type, index, total):
        """Exécute un scraper individuel"""
        start = time.time()
        self.progress[name] = {"status": "running", "jobs": 0}
        
        try:
            scraper_func(keywords, location, contract_type)
            jobs = [j for j in scraper_obj.jobs if j['source'] == name]
            
            elapsed = time.time() - start
            self.progress[name] = {
                "status": "completed",
                "jobs": len(jobs),
                "time": f"{elapsed:.1f}s"
            }
            
            return jobs
        except Exception as e:
            self.progress[name] = {"status": "error", "error": str(e)}
            return []
    
    def stop(self):
        self.stop_flag = True
