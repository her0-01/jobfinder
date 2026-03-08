"""
Scraper amélioré avec détection intelligente du contenu
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

class ImprovedScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
    
    def scrape_with_smart_detection(self, url, keywords, location):
        """Scraping intelligent avec détection du contenu dynamique"""
        print(f"\n🔍 Scraping: {url}")
        
        self.driver.get(url)
        
        # Attendre que la page charge
        time.sleep(3)
        
        # Accepter cookies
        self._accept_cookies()
        
        # Scroll pour charger le contenu dynamique
        self._scroll_to_load()
        
        # Attendre les offres
        jobs = self._wait_for_jobs()
        
        if not jobs:
            print("⚠️ Aucune offre détectée, tentative avec sélecteurs génériques...")
            jobs = self._fallback_scraping()
        
        # Filtrer par keywords
        filtered = self._filter_by_keywords(jobs, keywords)
        
        print(f"✅ {len(filtered)} offres trouvées")
        return filtered
    
    def _accept_cookies(self):
        """Accepter les cookies"""
        cookie_selectors = [
            'button[id*="accept"]',
            'button[id*="cookie"]',
            'button[class*="accept"]',
            'button[class*="cookie"]',
            '#didomi-notice-agree-button',
            '[data-testid="cookie-accept"]',
            'button:contains("Accepter")',
            'button:contains("Accept")'
        ]
        
        for selector in cookie_selectors:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                btn.click()
                time.sleep(1)
                return
            except:
                continue
    
    def _scroll_to_load(self):
        """Scroll pour charger le contenu dynamique"""
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/3});")
            time.sleep(1.5)
    
    def _wait_for_jobs(self):
        """Attendre que les offres se chargent"""
        # Sélecteurs courants pour les offres
        job_selectors = [
            '[data-testid*="job"]',
            '[class*="job-card"]',
            '[class*="jobCard"]',
            '[class*="job-item"]',
            '[class*="offer"]',
            '[class*="result"]',
            'article',
            '[role="article"]',
            '.job',
            '.offer'
        ]
        
        for selector in job_selectors:
            try:
                elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if len(elements) > 3:  # Au moins 3 offres
                    print(f"✅ {len(elements)} offres détectées avec: {selector}")
                    return self._extract_jobs_from_elements(elements)
            except:
                continue
        
        return []
    
    def _extract_jobs_from_elements(self, elements):
        """Extraire les infos des éléments"""
        jobs = []
        
        for elem in elements:
            try:
                # Trouver le titre
                title = None
                for tag in ['h2', 'h3', 'h4', 'a']:
                    try:
                        title_elem = elem.find_element(By.TAG_NAME, tag)
                        title = title_elem.text.strip()
                        if len(title) > 10:
                            break
                    except:
                        continue
                
                if not title or len(title) < 10:
                    continue
                
                # Trouver le lien
                link = None
                try:
                    link_elem = elem.find_element(By.TAG_NAME, 'a')
                    link = link_elem.get_attribute('href')
                except:
                    pass
                
                # Extraire entreprise et localisation du texte
                text = elem.text
                
                jobs.append({
                    'title': title,
                    'link': link or '',
                    'text': text
                })
            except:
                continue
        
        return jobs
    
    def _fallback_scraping(self):
        """Scraping de secours avec BeautifulSoup"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        jobs = []
        
        # Chercher tous les liens avec du texte significatif
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link['href']
            
            # Filtres
            if len(text) < 15 or len(text) > 200:
                continue
            
            # Doit contenir des mots-clés métier
            job_keywords = ['engineer', 'developer', 'data', 'analyst', 'scientist', 
                           'ingénieur', 'développeur', 'alternance', 'stage', 'apprenti']
            
            if not any(kw in text.lower() for kw in job_keywords):
                continue
            
            # Doit avoir un lien vers une offre
            if not any(p in href.lower() for p in ['job', 'offre', 'career', 'emploi']):
                continue
            
            jobs.append({
                'title': text,
                'link': href if href.startswith('http') else '',
                'text': text
            })
        
        return jobs
    
    def _filter_by_keywords(self, jobs, keywords):
        """Filtrer les offres par keywords"""
        keywords_lower = keywords.lower().split()
        
        filtered = []
        for job in jobs:
            text_lower = (job['title'] + ' ' + job.get('text', '')).lower()
            
            # Matching flexible: au moins 1 keyword principal
            main_keywords = [kw for kw in keywords_lower if len(kw) > 3]
            
            if any(kw in text_lower for kw in main_keywords):
                filtered.append(job)
        
        return filtered
