"""Scraper universel Playwright - Remplace universal_scraper.py"""
import asyncio
from scrapers.playwright_scrapers.indeed import scrape_indeed_async
from scrapers.playwright_scrapers.linkedin import scrape_linkedin_async
from scrapers.playwright_scrapers.companies import scrape_all_companies_async, scrape_company_async
from scrapers.playwright_scrapers.universal import (
    scrape_wttj_async, scrape_apec_async, scrape_hellowork_async,
    scrape_meteojob_async, scrape_regionsjob_async, scrape_monster_async
)
from scrapers.career_site_discovery import CareerSiteDiscovery
from utils.cache import JobCache
from nlp_preprocess.normalizer import NLPNormalizer
from utils.fallback import FallbackSystem
from utils.logger import setup_logger
from utils.smart_filter import SmartJobFilter

logger = setup_logger('playwright_universal')

class PlaywrightUniversalScraper:
    def __init__(self):
        self.cache = JobCache()
        self.normalizer = NLPNormalizer()
        self.fallback = FallbackSystem()
        self.smart_filter = None  # Sera initialisé avec l'IA
        self.jobs = []
        self.status_callback = None  # Callback pour progression
        self.stop_flag = None  # Flag pour arrêt
    
    async def scrape_all_async(self, keywords, location="France", contract_type=""):
        """Scrape TOUS les sites (23 sites: 8 universels + 15 entreprises) en SÉQUENTIEL"""
        import builtins
        normalized_keywords = self.normalizer.normalize(keywords)
        
        # Vérifier cache
        cached = self.cache.get(normalized_keywords, location, "all")
        if cached:
            logger.info(f"💾 Cache hit: {len(cached)} offres")
            self.jobs = cached
            return cached
        
        logger.info(f"🚀 Scraping séquentiel: {normalized_keywords} @ {location}")
        logger.info(f"📝 Keywords originaux: '{keywords}' → normalisés: '{normalized_keywords}'")
        
        jobs = []
        
        # PHASE 0: Découverte automatique de sites carrières (si activé)
        use_discovery = True  # Paramètre pour activer/désactiver
        discovered_sites = []
        
        if use_discovery:
            logger.info(f"\n🔍 PHASE 0: Découverte automatique de sites carrières...\n")
            try:
                discovery = CareerSiteDiscovery()
                discovered_sites = await discovery.discover_career_sites(keywords, location, max_companies=10)
                logger.info(f"✅ {len(discovered_sites)} sites découverts automatiquement")
            except Exception as e:
                logger.error(f"❌ Erreur découverte: {e}")
        
        # PHASE 1: Sites carrières (15 fixes + découverts)
        companies = {
            'Bouygues': 'https://joining.bouygues.com/global/fr/search-results',
            'Alstom': 'https://jobsearch.alstom.com/search/',
            'Stellantis': 'https://careers.stellantis.com/job-search-results/',
            'Renault': 'https://www.renaultgroup.com/carrieres-renault/nos-offres-monde/',
            'Société Générale': 'https://careers.societegenerale.com/rechercher',
            'BNP Paribas': 'https://group.bnpparibas/emploi-carriere/toutes-offres-emploi',
            'Schneider Electric': 'https://careers.se.com/jobs',
            'Safran': 'https://www.safran-group.com/fr/offres',
            'Thales': 'https://careers.thalesgroup.com/global/en/search-results',
            'Airbus': 'https://ag.wd3.myworkdayjobs.com/en-US/Airbus',
            'Orange': 'https://orange.jobs/jobs/search.do',
            'Capgemini': 'https://www.capgemini.com/fr-fr/carrieres/rejoignez-nous/rechercher-une-offre-d-emploi/',
            'Atos': 'https://atos.net/en/careers',
            'Dassault Systèmes': 'https://careers.3ds.com/fr/jobs',
            'TotalEnergies': 'https://totalenergies.avature.net/fr_FR/careers/SearchJobs',
        }
        
        logger.info(f"\n🏢 PHASE 1: Scraping {len(companies)} sites carrières...\n")
        
        for i, (company_name, company_url) in enumerate(companies.items(), 1):
            # Vérifier stop_flag
            if self.stop_flag and self.stop_flag.is_set():
                logger.info(f"⏹️ Arrêt demandé - Skip entreprises restantes")
                break
            
            logger.info(f"\n[{i}/15] 🏢 {company_name}...")
            
            try:
                from scrapers.playwright_scrapers.companies import scrape_company_async
                result = await scrape_company_async(company_url, company_name, normalized_keywords, location)
                if isinstance(result, list):
                    jobs.extend(result)
                    self.jobs = jobs  # Mettre à jour self.jobs en temps réel
                    logger.info(f"✅ {company_name}: {len(result)} offres")
                    print(f"✓ {company_name}: {len(result)} offres")
            except Exception as e:
                logger.error(f"❌ {company_name} erreur: {e}")
                print(f"✗ {company_name}: Erreur")
            
            # Mettre à jour le statut APRÈS avoir ajouté les offres
            if hasattr(builtins, 'scraping_status'):
                builtins.scraping_status = {"running": True, "progress": f"🏢 {company_name} ({i}/15) • {len(jobs)} offres"}
            
            if self.status_callback:
                self.status_callback(company_name, i, 15, len(jobs))
        
        # PHASE 1.5: Sites découverts automatiquement
        if discovered_sites:
            logger.info(f"\n🆕 PHASE 1.5: Scraping {len(discovered_sites)} sites découverts...\n")
            
            for i, site in enumerate(discovered_sites, 1):
                if self.stop_flag and self.stop_flag.is_set():
                    logger.info(f"⏹️ Arrêt demandé - Skip sites découverts")
                    break
                
                company_name = site['name']
                career_url = site['career_url']
                
                logger.info(f"\n[D{i}/{len(discovered_sites)}] 🆕 {company_name}...")
                
                try:
                    result = await scrape_company_async(career_url, company_name, normalized_keywords, location)
                    if isinstance(result, list):
                        jobs.extend(result)
                        self.jobs = jobs
                        logger.info(f"✅ {company_name}: {len(result)} offres")
                        print(f"✓ {company_name} (découvert): {len(result)} offres")
                except Exception as e:
                    logger.error(f"❌ {company_name} erreur: {e}")
                    print(f"✗ {company_name}: Erreur")
                
                total_companies = 15 + i
                if hasattr(builtins, 'scraping_status'):
                    builtins.scraping_status = {"running": True, "progress": f"🆕 {company_name} ({total_companies}/?) • {len(jobs)} offres"}
                
                if self.status_callback:
                    self.status_callback(f"{company_name} (découvert)", total_companies, 23 + len(discovered_sites), len(jobs))
        
        # PHASE 2: Sites universels (8 sites)
        sites = [
            ('Indeed', scrape_indeed_async),
            ('LinkedIn', scrape_linkedin_async),
            ('WTTJ', scrape_wttj_async),
            ('APEC', scrape_apec_async),
            ('HelloWork', scrape_hellowork_async),
            ('Meteojob', scrape_meteojob_async),
            ('RegionsJob', scrape_regionsjob_async),
            ('Monster', scrape_monster_async)
        ]
        
        logger.info(f"\n🌐 PHASE 2: Scraping {len(sites)} sites universels...\n")
        
        # Scraper chaque site avec progression
        for i, (site_name, scrape_func) in enumerate(sites, 1):
            # Vérifier stop_flag
            if self.stop_flag and self.stop_flag.is_set():
                logger.info(f"⏹️ Arrêt demandé - Skip sites restants")
                break
            
            # Progression totale: 15 entreprises + i sites universels
            total_progress = 15 + i
            
            logger.info(f"\n[{total_progress}/23] 🌐 {site_name}...")
            
            try:
                result = await scrape_func(normalized_keywords, location, contract_type)
                if isinstance(result, list):
                    jobs.extend(result)
                    self.jobs = jobs  # Mettre à jour self.jobs en temps réel
                    logger.info(f"✅ {site_name}: {len(result)} offres")
                    print(f"✓ {site_name}: {len(result)} offres")
            except Exception as e:
                logger.error(f"❌ {site_name} erreur: {e}")
                print(f"✗ {site_name}: Erreur")
            
            # Mettre à jour le statut APRÈS avoir ajouté les offres
            if hasattr(builtins, 'scraping_status'):
                builtins.scraping_status = {"running": True, "progress": f"🌐 {site_name} ({total_progress}/23) • {len(jobs)} offres"}
            
            if self.status_callback:
                self.status_callback(site_name, total_progress, 23, len(jobs))
        
        logger.info(f"📊 Total avant dédupe: {len(jobs)} offres")
        
        # Dédupliquer
        seen = set()
        unique = []
        for job in jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        logger.info(f"📊 Après dédupe: {len(unique)} offres")
        
        # FILTRAGE INTELLIGENT avec IA
        if self.smart_filter:
            logger.info(f"\n🧠 Filtrage intelligent IA des offres...")
            filtered = self.smart_filter.filter_jobs(unique, keywords, min_score=30)
            stats = self.smart_filter.get_filter_stats(len(unique), len(filtered))
            logger.info(f"✅ Filtrage: {stats['removed_count']} offres exclues ({stats['removal_rate']}%)")
            logger.info(f"🎯 {len(filtered)} offres pertinentes conservées")
        else:
            logger.warning("⚠️ Filtre IA non disponible - conservation de toutes les offres")
            filtered = unique
        
        # Fallback si 0 résultats
        if len(filtered) == 0:
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
                    filtered.extend(result)
        
        # Sauvegarder cache
        if len(filtered) > 0:
            self.cache.set(normalized_keywords, location, "all", filtered)
        
        self.jobs = filtered
        logger.info(f"✅ {len(filtered)} offres trouvées")
        return filtered
    
    def scrape_all(self, keywords, location="France", contract_type=""):
        """Version synchrone pour compatibilité"""
        return asyncio.run(self.scrape_all_async(keywords, location, contract_type))
