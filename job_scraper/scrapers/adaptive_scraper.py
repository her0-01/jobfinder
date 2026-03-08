from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import setup_logger
import configparser
import urllib.parse

class AdaptiveScraper:
    """Scraper adaptatif qui essaie plusieurs méthodes"""
    
    def __init__(self, headless=True):
        self.logger = setup_logger('adaptive_scraper')
        self.logger.info("🚀 Initialisation AdaptiveScraper")
        
        # Smart Query Builder
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
            config.read(config_path)
            
            # Récupérer le provider configuré
            self.ai_provider = config.get('API', 'ai_provider', fallback='groq').upper()
            
            from ai_adapters.smart_query_builder import SmartQueryBuilder
            self.smart_query = SmartQueryBuilder()
            print(f"✅ Smart Query Builder activé ({self.ai_provider})")
        except Exception as e:
            self.smart_query = None
            self.ai_provider = "AUCUN"
            print(f"⚠️ Smart Query Builder désactivé: {e}")
        
        # Driver setup
        try:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if chrome_path:
                import undetected_chromedriver as uc
                self.driver = uc.Chrome(browser_executable_path=chrome_path, version_main=145)
                self.logger.info("✓ Chrome (undetected) initialisé")
            else:
                raise FileNotFoundError("Chrome non trouvé")
        except Exception as e:
            self.logger.warning(f"⚠️ Chrome échoué: {e}, utilisation Edge")
            from selenium import webdriver
            options = webdriver.EdgeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            try:
                self.driver = webdriver.Edge(options=options)
                self.logger.info("✓ Edge initialisé")
            except Exception as edge_error:
                self.logger.error(f"❌ Edge échoué: {edge_error}")
                raise Exception("Impossible d'initialiser Chrome ou Edge")
        
        self.jobs = []
    
    def scrape_generic(self, url, company_name, keywords, location="France", contract_type="Alternance"):
        """Scraping générique avec SOTA Scraper"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🏢 Scraping {company_name} (SOTA)")
        
        try:
            from scrapers.sota_scraper import SOTAScraper
            sota = SOTAScraper(self.driver)
            jobs = sota.scrape(url, keywords, location)
            
            if jobs:
                self.jobs.extend(jobs[:15])
                print(f"✅ {company_name}: {len(jobs[:15])} offres (SOTA)")
                return
            
            print(f"⚠️ {company_name}: Aucune offre trouvée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur {company_name}: {str(e)}")
            print(f"✗ {company_name}: {e}")
    
    def _scrape_classic(self, url, company_name, keywords, location, contract_type):
        """Méthode classique (fallback)"""
        self.logger.info(f"🔍 Méthode classique pour {company_name}")
        
        try:
            # Utiliser Smart Query Builder si disponible
            if self.smart_query:
                self.logger.info(f"🤖 Utilisation Smart Query Builder ({self.ai_provider})...")
                optimized_url = self.smart_query.analyze_and_build_url(
                    site_url=url,
                    keywords=keywords,
                    location=location,
                    contract_type=contract_type,
                    driver=self.driver
                )
                self.logger.info(f"✅ URL optimisée: {optimized_url[:100]}...")
                url = optimized_url
            
            self.logger.debug("Chargement de la page...")
            self.driver.get(url)
            time.sleep(5)
            self.logger.info("✓ Page chargée")
            
            # Accepter cookies
            self.logger.debug("Recherche bannière cookies...")
            try:
                for selector in ['[id*="cookie"] button', '[class*="cookie"] button', '#didomi-notice-agree-button', '.accept-cookies']:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        btn.click()
                        self.logger.info(f"✓ Cookies acceptés ({selector})")
                        time.sleep(1)
                        break
                    except: continue
            except: 
                self.logger.debug("Pas de bannière cookies")
            
            # Scroll pour charger contenu dynamique
            self.logger.debug("Scroll pour contenu dynamique...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(2)
            
            self.logger.debug("Parsing HTML avec BeautifulSoup...")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Chercher tous les liens
            all_links = soup.find_all('a', href=True)
            self.logger.info(f"📊 {len(all_links)} liens trouvés sur la page")
            
            job_links = []
            keywords_lower = keywords.lower().split()
            self.logger.debug(f"Filtrage avec keywords: {keywords_lower}")
            
            matched_links = 0
            for link in all_links:
                text = link.get_text().lower().strip()
                href = link['href']
                
                # EXCLUSIONS: Liens génériques à ignorer
                excluded = ['voir', 'toutes', 'nos offres', 'postulez', 'maintenant', 'choisir', 
                           'métier', 'carriere', 'careers', 'rejoindre', 'rejoignez', 'découvrir',
                           'voir les', 'en savoir', 'déposer', 'manage', 'partenaire', 'repenser', 
                           'partager', 'ressources humaines', 'power house', 'maintenance', 'travailler chez',
                           'offres d\'emploi', 'toutes les offres', 'voir l\'offre', 'voir toutes']
                
                if any(excl in text for excl in excluded):
                    continue
                
                # Longueur titre raisonnable
                if len(text) < 10 or len(text) > 200:
                    continue
                
                # Vérifier URL contient pattern job
                job_patterns = ['job', 'career', 'offre', 'emploi', 'poste', 'opportunit', 
                               'recrutement', 'apply', 'position', 'vacancy']
                
                if not any(pattern in href.lower() for pattern in job_patterns):
                    continue
                
                # MATCHING FLEXIBLE: au moins 1 keyword OU mots-clés métier
                tech_keywords = ['data', 'engineer', 'scientist', 'analyst', 'developer', 'développeur', 
                                'ingénieur', 'alternance', 'stage', 'apprenti', 'python', 'machine learning',
                                'big data', 'cloud', 'devops', 'fullstack', 'backend', 'frontend']
                
                if any(kw in text for kw in keywords_lower) or any(tech in text for tech in tech_keywords):
                    matched_links += 1
                    full_url = href if href.startswith('http') else (url.rstrip('/') + '/' + href.lstrip('/'))
                    
                    job_links.append({
                        'title': link.get_text().strip(),
                        'company': company_name,
                        'location': self._extract_location(link.parent.get_text() if link.parent else ''),
                        'link': full_url,
                        'source': f'{company_name} Careers',
                        'scraped_at': datetime.now().isoformat()
                    })
            
            self.logger.info(f"🔍 {matched_links} liens matchés avec keywords")
            
            # Dédoublonner par titre
            self.logger.debug(f"Dédoublonnage de {len(job_links)} offres...")
            seen_titles = set()
            unique_jobs = []
            for job in job_links:
                if job['title'] not in seen_titles:
                    seen_titles.add(job['title'])
                    unique_jobs.append(job)
            
            self.logger.info(f"📋 {len(unique_jobs)} offres uniques (avant limite)")
            self.jobs.extend(unique_jobs[:10])
            self.logger.info(f"✅ {company_name}: {len(unique_jobs[:10])} offres ajoutées")
            print(f"✓ {company_name}: {len(unique_jobs[:10])} offres")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur {company_name}: {str(e)}")
            self.logger.exception("Détails de l'erreur:")
            print(f"✗ {company_name}: {e}")
    
    def _extract_location(self, text):
        """Extraire localisation du texte"""
        locations = ['Paris', 'Lyon', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille', 
                    'Rennes', 'Grenoble', 'France', 'Remote', 'Télétravail']
        
        for loc in locations:
            if loc.lower() in text.lower():
                return loc
        
        return 'France'
    
    def scrape_all_companies(self, keywords="Data Engineer", location="France", contract_type="Alternance"):
        """Scraper toutes les entreprises avec Smart Query Builder"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🚀 DÉBUT SCRAPING MULTI-ENTREPRISES")
        self.logger.info(f"Keywords: {keywords} | Location: {location} | Contract: {contract_type}")
        self.logger.info(f"{'='*60}\n")
        print(f"\n🏢 Scraping sites carrières (adaptatif + IA)...\n")
        
        # URLs de base (Smart Query Builder les optimisera)
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
        
        for i, (company, url) in enumerate(companies.items(), 1):
            self.logger.info(f"\n[{i}/{len(companies)}] Traitement {company}...")
            self.scrape_generic(url, company, keywords, location, contract_type)
            time.sleep(2)
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"✅ SCRAPING TERMINÉ: {len(self.jobs)} offres totales")
        self.logger.info(f"{'='*60}\n")
        return self.jobs
    
    def close(self):
        self.logger.info("🔒 Fermeture du driver")
        self.driver.quit()
        self.logger.info("✓ Driver fermé")
