"""Orchestrateur principal auto-apprenant et auto-maintenable"""
import asyncio
from scrapers.playwright_universal import PlaywrightUniversalScraper
from site_discovery.discover import SiteDiscoverer
from site_analyzer.analyze import SiteAnalyzer
from scraper_generator.generate import ScraperGenerator
from site_monitor.monitor import SiteMonitor
from url_learning.learner import URLLearner
from url_validator.validator import URLValidator
from nlp_preprocess.normalizer import NLPNormalizer
from utils.cache import JobCache
from utils.fallback import FallbackSystem
from utils.advanced_logger import AdvancedLogger
import time

class AutoLearningOrchestrator:
    """Orchestrateur auto-apprenant, auto-découvrant et auto-corrigeant"""
    
    def __init__(self):
        self.scraper = PlaywrightUniversalScraper()
        self.discoverer = SiteDiscoverer()
        self.analyzer = SiteAnalyzer()
        self.generator = ScraperGenerator()
        self.monitor = SiteMonitor()
        self.url_learner = URLLearner()
        self.url_validator = URLValidator()
        self.normalizer = NLPNormalizer()
        self.cache = JobCache()
        self.fallback = FallbackSystem()
        self.logger = AdvancedLogger("orchestrator")
    
    async def search(self, keywords, location="France", contract_type=""):
        """Recherche principale avec tous les modules"""
        start_time = time.time()
        
        # Normaliser
        normalized = self.normalizer.normalize(keywords)
        self.logger.log_scraping_start("ALL", normalized, location)
        
        # Vérifier cache
        cached = self.cache.get(normalized, location, "all")
        if cached:
            self.logger.log_cache_hit(normalized, len(cached))
            return cached
        
        # Scraping
        jobs = await self.scraper.scrape_all_async(normalized, location, contract_type)
        
        # Fallback si nécessaire
        if len(jobs) == 0:
            simple = self.normalizer.simplify(keywords)
            self.logger.log_fallback(keywords, simple)
            jobs = await self.scraper.scrape_all_async(simple, location, contract_type)
        
        duration = time.time() - start_time
        self.logger.log_scraping_end("ALL", len(jobs), duration)
        
        # Sauvegarder cache
        if len(jobs) > 0:
            self.cache.set(normalized, location, "all", jobs)
        
        return jobs
    
    async def discover_new_sites(self):
        """Découvre automatiquement de nouveaux jobboards"""
        self.logger.logger.info("🔍 Découverte de nouveaux sites...")
        sites = await self.discoverer.discover()
        self.logger.logger.info(f"✅ {len(sites)} sites découverts")
        return sites
    
    async def analyze_site(self, site_url):
        """Analyse un site pour détecter les patterns"""
        self.logger.logger.info(f"🔬 Analyse de {site_url}...")
        pattern = await self.analyzer.analyze(site_url)
        self.logger.logger.info(f"✅ Pattern détecté: {pattern}")
        return pattern
    
    async def generate_scraper(self, site_url, site_name):
        """Génère automatiquement un scraper"""
        self.logger.logger.info(f"🤖 Génération scraper pour {site_name}...")
        filepath = await self.generator.generate(site_url, site_name)
        self.logger.logger.info(f"✅ Scraper généré: {filepath}")
        return filepath
    
    async def monitor_sites(self, sites):
        """Monitore les sites et régénère si nécessaire"""
        self.logger.logger.info("👁️ Monitoring des sites...")
        for site_name, site_url in sites.items():
            await self.monitor.auto_regenerate(site_name, site_url)
        self.logger.logger.info("✅ Monitoring terminé")
    
    def sync_search(self, keywords, location="France", contract_type=""):
        """Version synchrone pour compatibilité"""
        return asyncio.run(self.search(keywords, location, contract_type))
