"""Scraper universel Playwright - Remplace universal_scraper.py"""
import asyncio
from scrapers.playwright_scrapers.indeed import scrape_indeed_async
from scrapers.playwright_scrapers.linkedin import scrape_linkedin_async
from scrapers.playwright_scrapers.companies import scrape_all_companies_async
from scrapers.playwright_scrapers.universal import (
    scrape_wttj_async, scrape_apec_async, scrape_hellowork_async,
    scrape_meteojob_async, scrape_regionsjob_async, scrape_monster_async
)
from utils.cache import JobCache
from nlp_preprocess.normalizer import NLPNormalizer
from utils.fallback import FallbackSystem
from utils.logger import setup_logger

logger = setup_logger('playwright_universal')

class PlaywrightUniversalScraper:
    def __init__(self):
        self.cache = JobCache()
        self.normalizer = NLPNormalizer()
        self.fallback = FallbackSystem()
        self.jobs = []
    
    async def scrape_all_async(self, keywords, location="France", contract_type=""):
        """Scrape TOUS les sites (23 sites) en parallèle avec Playwright"""
        normalized_keywords = self.normalizer.normalize(keywords)
        
        # Vérifier cache
        cached = self.cache.get(normalized_keywords, location, "all")
        if cached:
            logger.info(f"💾 Cache hit: {len(cached)} offres")
            self.jobs = cached
            return cached
        
        logger.info(f"🚀 Scraping parallèle: {normalized_keywords} @ {location}")
        logger.info(f"📝 Keywords originaux: '{keywords}' → normalisés: '{normalized_keywords}'")
        
        # Lancer TOUS les scrapers en parallèle
        tasks = [
            # Sites universels (8)
            scrape_indeed_async(normalized_keywords, location, contract_type),
            scrape_linkedin_async(normalized_keywords, location, contract_type),
            scrape_wttj_async(normalized_keywords, location, contract_type),
            scrape_apec_async(normalized_keywords, location, contract_type),
            scrape_hellowork_async(normalized_keywords, location, contract_type),
            scrape_meteojob_async(normalized_keywords, location, contract_type),
            scrape_regionsjob_async(normalized_keywords, location, contract_type),
            scrape_monster_async(normalized_keywords, location, contract_type),
            # Sites carrières (15)
            scrape_all_companies_async(normalized_keywords, location, contract_type),
        ]
        
        logger.info(f"🔄 Lancement de {len(tasks)} scrapers en parallèle...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"✅ Scrapers terminés, traitement des résultats...")
        
        jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Scraper {i} erreur: {result}")
            elif isinstance(result, list):
                logger.info(f"✅ Scraper {i}: {len(result)} offres")
                jobs.extend(result)
            else:
                logger.warning(f"⚠️ Scraper {i}: résultat inattendu {type(result)}")
        
        logger.info(f"📊 Total avant dédupe: {len(jobs)} offres")
        
        logger.info(f"📊 Total avant dédupe: {len(jobs)} offres")
        
        # Fallback si 0 résultats
        if len(jobs) == 0:
            logger.warning("⚠️ 0 résultats, fallback activé")
            logger.info(f"🔄 Fallback 1: simplification '{keywords}' → '{self.normalizer.simplify(keywords)}'")
            simple = self.normalizer.simplify(keywords)
            tasks = [
                scrape_indeed_async(simple, location, contract_type),
                scrape_linkedin_async(simple, location, contract_type),
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    jobs.extend(result)
            
            if len(jobs) == 0:
                tasks = [
                    scrape_indeed_async(keywords, "", contract_type),
                    scrape_linkedin_async(keywords, "", contract_type),
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, list):
                        jobs.extend(result)
        
        # Dédupliquer
        seen = set()
        unique = []
        for job in jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        # Sauvegarder cache
        if len(unique) > 0:
            self.cache.set(normalized_keywords, location, "all", unique)
        
        self.jobs = unique
        logger.info(f"✅ {len(unique)} offres trouvées")
        return unique
    
    def scrape_all(self, keywords, location="France", contract_type=""):
        """Version synchrone pour compatibilité"""
        return asyncio.run(self.scrape_all_async(keywords, location, contract_type))
