from groq import Groq
import json
import time
from selenium.webdriver.common.by import By
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ai_adapters.universal_ai import get_ai_adapter

class VisionGuidedScraper:
    """Scraper guidé par IA - VERSION SIMPLIFIÉE"""
    
    def __init__(self, driver):
        self.ai = get_ai_adapter()  # Utilise le provider configuré
        self.driver = driver
        # Récupérer le nom du provider pour les logs
        self.provider_name = self.ai.provider.upper()
    
    def analyze_page_structure(self, html_content, keywords, location):
        """Trouve les champs du formulaire de recherche"""
        
        prompt = f"""HTML:
{html_content[:5000]}

TROUVE formulaire recherche pour "{keywords}".

RETOURNE JSON:
{{
  "search_input": "input[name='q']" ou null,
  "location_input": "input[name='location']" ou null,
  "search_button": "button[type='submit']" ou null
}}"""

        try:
            response = self.ai.chat_completion_with_fallback(
                messages=[
                    {"role": "system", "content": "Expert web scraping. Trouve sélecteurs CSS formulaire."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            print(f"  ⚠️ Erreur IA: {e}")
            return None
    
    def _parse_selector(self, selector):
        """Parse sélecteur CSS"""
        if not selector:
            return None, None, None
        
        name_match = re.search(r"name=['\"]([^'\"]+)['\"]", selector)
        id_match = re.search(r"id=['\"]([^'\"]+)['\"]", selector)
        type_match = re.search(r"type=['\"]([^'\"]+)['\"]", selector)
        
        return (name_match.group(1) if name_match else None,
                id_match.group(1) if id_match else None,
                type_match.group(1) if type_match else None)
    
    def smart_scrape(self, url, company_name, keywords, location, contract_type):
        """Scraping intelligent"""
        print(f"\n🤖 Scraping IA: {company_name}")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Cookies
            try:
                for sel in ['button[id*="accept"]', '#didomi-notice-agree-button']:
                    try:
                        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.CSS_SELECTOR, sel))
                        time.sleep(1)
                        break
                    except: pass
            except: pass
            
            # Scroll
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3)
            
            # Analyser
            print(f"  🔍 Analyse avec {self.provider_name}...")
            selectors = self.analyze_page_structure(self.driver.page_source, keywords, location)
            
            if not selectors:
                print("  ⚠️ Analyse échouée")
                return []
            
            print(f"  ✅ Sélecteurs: {selectors}")
            
            # Remplir formulaire
            form_filled = False
            
            if selectors.get('search_input'):
                try:
                    name, id_val, _ = self._parse_selector(selectors['search_input'])
                    elem = None
                    
                    if name:
                        try:
                            elem = self.driver.find_element(By.NAME, name)
                        except: pass
                    
                    if not elem and id_val:
                        try:
                            elem = self.driver.find_element(By.ID, id_val)
                        except: pass
                    
                    if elem and self.driver.execute_script("return arguments[0].offsetWidth > 0;", elem):
                        self.driver.execute_script(
                            "arguments[0].focus(); arguments[0].value = arguments[1]; "
                            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                            elem, keywords
                        )
                        form_filled = True
                        print(f"  ✅ Recherche: {keywords}")
                except:
                    pass
            
            if selectors.get('location_input'):
                try:
                    name, id_val, _ = self._parse_selector(selectors['location_input'])
                    elem = None
                    
                    if name:
                        try:
                            elem = self.driver.find_element(By.NAME, name)
                        except: pass
                    
                    if not elem and id_val:
                        try:
                            elem = self.driver.find_element(By.ID, id_val)
                        except: pass
                    
                    if elem and self.driver.execute_script("return arguments[0].offsetWidth > 0;", elem):
                        self.driver.execute_script(
                            "arguments[0].focus(); arguments[0].value = arguments[1]; "
                            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                            elem, location
                        )
                        print(f"  ✅ Localisation: {location}")
                except:
                    pass
            
            if selectors.get('search_button'):
                try:
                    name, id_val, type_val = self._parse_selector(selectors['search_button'])
                    elem = None
                    
                    if type_val:
                        try:
                            elem = self.driver.find_element(By.XPATH, f"//button[@type='{type_val}'] | //input[@type='{type_val}']")
                        except: pass
                    
                    if not elem and id_val:
                        try:
                            elem = self.driver.find_element(By.ID, id_val)
                        except: pass
                    
                    if elem:
                        self.driver.execute_script("setTimeout(() => arguments[0].click(), 100);", elem)
                        time.sleep(5)
                        form_filled = True
                        print("  ✅ Recherche lancée")
                except:
                    pass
            
            # Scraper résultats
            if form_filled:
                print("  🔍 Scraping résultats...")
                jobs = []
                links = self.driver.find_elements(By.TAG_NAME, 'a')
                
                for link in links[:50]:
                    try:
                        title = link.text.strip()
                        href = link.get_attribute('href')
                        
                        if not href or not title or len(title) < 15 or len(title) > 150:
                            continue
                        
                        if 'job' not in href.lower() and 'offre' not in href.lower():
                            continue
                        
                        tech_kw = ['data', 'engineer', 'developer', 'analyst', 'scientist', 'alternance', 'stage']
                        if any(kw in title.lower() for kw in tech_kw):
                            jobs.append({
                                'title': title,
                                'company': company_name,
                                'location': location,
                                'link': href,
                                'source': f'{company_name} Careers',
                                'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S')
                            })
                    except:
                        continue
                
                print(f"  ✅ {len(jobs)} offres")
                return jobs[:15]
            
            return []
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return []
