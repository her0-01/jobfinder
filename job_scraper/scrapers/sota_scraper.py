"""
Scraper SOTA - State of the Art
- Anti-détection
- Extraction intelligente
- Retry automatique
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import re

class SOTAScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def scrape(self, url, keywords, location):
        """Scraping SOTA avec toutes les optimisations"""
        print(f"\n🚀 SOTA Scraping: {url}")
        
        # 1. Charger avec user-agent réaliste
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.driver.get(url)
        
        # 2. Attendre chargement initial
        time.sleep(4)
        
        # 3. Cookies
        self._smart_cookie_accept()
        
        # 4. Scroll progressif (simule humain)
        self._human_scroll()
        
        # 5. Attendre le contenu dynamique
        self._wait_for_dynamic_content()
        
        # 6. Extraction multi-méthode
        jobs = self._extract_jobs_multi_method()
        
        # 7. Filtrage intelligent
        filtered = self._smart_filter(jobs, keywords)
        
        # 8. Enrichissement
        enriched = self._enrich_jobs(filtered, url)
        
        print(f"✅ {len(enriched)} offres de qualité extraites")
        return enriched
    
    def _smart_cookie_accept(self):
        """Acceptation intelligente des cookies"""
        selectors = [
            '#didomi-notice-agree-button',
            'button[id*="accept" i]',
            'button[class*="accept" i]',
            'button:has-text("Accepter")',
            'button:has-text("Accept")',
            '[data-testid*="cookie" i] button',
            '.cookie-banner button:first-child'
        ]
        
        for sel in selectors:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
                    return True
            except:
                continue
        return False
    
    def _human_scroll(self):
        """Scroll qui simule un humain"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(5):
            # Scroll aléatoire
            scroll_to = int(total_height * (i + 1) / 5)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            time.sleep(0.8 + (i * 0.2))  # Temps variable
    
    def _wait_for_dynamic_content(self):
        """Attendre que le contenu JS se charge"""
        # Attendre que le nombre de liens augmente
        initial_links = len(self.driver.find_elements(By.TAG_NAME, 'a'))
        
        for _ in range(3):
            time.sleep(2)
            current_links = len(self.driver.find_elements(By.TAG_NAME, 'a'))
            if current_links > initial_links * 1.5:
                break
    
    def _extract_jobs_multi_method(self):
        """Extraction avec plusieurs méthodes"""
        jobs = []
        
        # Méthode 1: Sélecteurs spécifiques
        jobs.extend(self._method_specific_selectors())
        
        # Méthode 2: Analyse sémantique
        if len(jobs) < 5:
            jobs.extend(self._method_semantic_analysis())
        
        # Méthode 3: Pattern matching
        if len(jobs) < 5:
            jobs.extend(self._method_pattern_matching())
        
        # Dédupliquer
        seen = set()
        unique = []
        for job in jobs:
            key = job['title'].lower().strip()
            if key not in seen and len(key) > 10:
                seen.add(key)
                unique.append(job)
        
        return unique
    
    def _method_specific_selectors(self):
        """Méthode 1: Sélecteurs CSS spécifiques"""
        selectors = [
            # Indeed
            '.job_seen_beacon',
            '[data-testid="job-card"]',
            '.jobsearch-ResultsList > li',
            # LinkedIn
            '.job-card-container',
            '.jobs-search__results-list > li',
            # WTTJ
            '[data-testid="job-list-item"]',
            # Bouygues
            '.search-results-list .job',
            '[class*="JobCard"]',
            # Génériques
            'article[class*="job" i]',
            '[class*="job-card" i]',
            '[data-job-id]'
        ]
        
        jobs = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) >= 3:
                    print(f"✅ {len(elements)} offres avec: {selector}")
                    for elem in elements:
                        job = self._extract_from_element(elem)
                        if job:
                            jobs.append(job)
                    if jobs:
                        return jobs
            except:
                continue
        
        return jobs
    
    def _method_semantic_analysis(self):
        """Méthode 2: Analyse sémantique du HTML"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        jobs = []
        
        # Chercher les articles/divs qui ressemblent à des offres
        for tag in soup.find_all(['article', 'div', 'li']):
            # Doit avoir un titre (h2, h3, h4)
            title_tag = tag.find(['h2', 'h3', 'h4', 'a'])
            if not title_tag:
                continue
            
            title = title_tag.get_text().strip()
            
            # Filtres de qualité
            if len(title) < 15 or len(title) > 150:
                continue
            
            # Doit contenir des mots-clés métier
            job_words = ['engineer', 'developer', 'analyst', 'scientist', 'manager',
                        'ingénieur', 'développeur', 'analyste', 'chef', 'responsable',
                        'alternance', 'stage', 'cdi', 'cdd']
            
            if not any(word in title.lower() for word in job_words):
                continue
            
            # Trouver le lien
            link_tag = tag.find('a', href=True)
            link = link_tag['href'] if link_tag else ''
            
            # Extraire entreprise et localisation
            text = tag.get_text()
            company = self._extract_company(text)
            location = self._extract_location(text)
            
            jobs.append({
                'title': title,
                'link': link,
                'company': company,
                'location': location,
                'source': 'semantic'
            })
        
        return jobs
    
    def _method_pattern_matching(self):
        """Méthode 3: Pattern matching sur tous les liens"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        jobs = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Le lien doit pointer vers une offre
            if not any(p in href.lower() for p in ['job', 'offre', 'career', 'emploi', 'poste']):
                continue
            
            # Le texte doit être un titre d'offre
            if len(text) < 15 or len(text) > 150:
                continue
            
            # Doit contenir des mots métier
            if not re.search(r'(engineer|developer|analyst|scientist|ingénieur|développeur|alternance|stage)', text, re.I):
                continue
            
            jobs.append({
                'title': text,
                'link': href,
                'company': '',
                'location': '',
                'source': 'pattern'
            })
        
        return jobs
    
    def _extract_from_element(self, elem):
        """Extraire les infos d'un élément"""
        try:
            # Titre
            title = None
            for tag in ['h2', 'h3', 'h4', 'a', 'span']:
                try:
                    title_elem = elem.find_element(By.TAG_NAME, tag)
                    title = title_elem.text.strip()
                    if len(title) > 15:
                        break
                except:
                    continue
            
            if not title or len(title) < 15:
                return None
            
            # Lien
            link = ''
            try:
                link_elem = elem.find_element(By.TAG_NAME, 'a')
                link = link_elem.get_attribute('href') or ''
            except:
                pass
            
            # Texte complet
            text = elem.text
            
            return {
                'title': title,
                'link': link,
                'company': self._extract_company(text),
                'location': self._extract_location(text),
                'source': 'element'
            }
        except:
            return None
    
    def _extract_company(self, text):
        """Extraire le nom de l'entreprise"""
        # Patterns courants
        patterns = [
            r'(?:chez|at|@)\s+([A-Z][A-Za-z\s&]+)',
            r'([A-Z][A-Za-z\s&]{3,30})(?:\s*-\s*[A-Z])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_location(self, text):
        """Extraire la localisation"""
        locations = ['Paris', 'Lyon', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille',
                    'Marseille', 'Nice', 'Strasbourg', 'Rennes', 'Grenoble',
                    'France', 'Remote', 'Télétravail', 'Île-de-France']
        
        for loc in locations:
            if loc in text:
                return loc
        
        return 'France'
    
    def _smart_filter(self, jobs, keywords):
        """Filtrage intelligent par keywords"""
        keywords_lower = keywords.lower().split()
        
        # Mots-clés principaux (> 3 lettres)
        main_kw = [kw for kw in keywords_lower if len(kw) > 3]
        
        filtered = []
        for job in jobs:
            text = (job['title'] + ' ' + job.get('company', '') + ' ' + job.get('location', '')).lower()
            
            # Exclure les éléments de navigation
            exclude_words = ['affichage', 'résultats', 'voir', 'toutes', 'page', 'suivant', 'précédent']
            if any(word in text for word in exclude_words):
                continue
            
            # Score de matching
            score = sum(1 for kw in main_kw if kw in text)
            
            if score >= 1:  # Au moins 1 keyword principal
                job['match_score'] = score
                filtered.append(job)
        
        # Trier par score
        filtered.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return filtered
    
    def _enrich_jobs(self, jobs, base_url):
        """Enrichir les offres"""
        from urllib.parse import urljoin
        
        for job in jobs:
            # Compléter les URLs relatives
            if job['link'] and not job['link'].startswith('http'):
                job['link'] = urljoin(base_url, job['link'])
            
            # Ajouter timestamp
            from datetime import datetime
            job['scraped_at'] = datetime.now().isoformat()
        
        return jobs
