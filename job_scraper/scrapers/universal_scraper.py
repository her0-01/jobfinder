from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time
import json
from datetime import datetime
import urllib.parse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger import setup_logger
import configparser

class UniversalJobScraper:
    def __init__(self, headless=True):
        self.logger = setup_logger('universal_scraper')
        self.logger.info("🚀 Initialisation UniversalJobScraper")
        
        # Smart Query Builder
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
            config.read(config_path)
            groq_key = config['API']['groq_api_key']
            from ai_adapters.smart_query_builder import SmartQueryBuilder
            self.smart_query = SmartQueryBuilder(groq_key)
            print("✅ Smart Query Builder activé")
        except Exception as e:
            self.smart_query = None
            print(f"⚠️ Smart Query Builder désactivé: {e}")
        
        # Driver setup
        try:
            # Essayer Chromium en premier (Railway/Linux)
            try:
                from selenium import webdriver as wd
                options = wd.ChromeOptions()
                options.binary_location = '/usr/bin/chromium'
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                self.driver = wd.Chrome(options=options)
                self.logger.info("✅ Chromium initialisé")
            except Exception as chromium_error:
                self.logger.warning(f"⚠️ Chromium échoué: {chromium_error}")
                
                # Fallback Chrome Windows
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
                    self.logger.info("✅ Chrome (undetected) initialisé")
                else:
                    raise FileNotFoundError("Chrome non trouvé")
        except Exception as e:
            self.logger.warning(f"⚠️ Chrome échoué: {e}, utilisation Edge")
            from selenium import webdriver
            options = webdriver.EdgeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            self.driver = webdriver.Edge(options=options)
            self.logger.info("✅ Edge initialisé")
        
        self.jobs = []
    
    def scrape_all(self, keywords, location="France", contract_type="Alternance"):
        """Scraper tous les sites"""
        print(f"\n🔍 Recherche: {keywords} | {location} | {contract_type}\n")
        
        self.scrape_indeed(keywords, location, contract_type)
        self.scrape_linkedin(keywords, location)
        self.scrape_welcometothejungle(keywords, location)
        self.scrape_apec(keywords, location)
        self.scrape_hellowork(keywords, location)
        self.scrape_meteojob(keywords, location)
        self.scrape_regionsjob(keywords, location)
        self.scrape_monster(keywords, location)
        
        return self.jobs
    
    def scrape_indeed(self, keywords, location, contract_type):
        self.logger.info(f"\n{'='*60}")
        self.logger.info("🔍 Scraping Indeed")
        try:
            url = f"https://fr.indeed.com/jobs?q={urllib.parse.quote(keywords)}&l={urllib.parse.quote(location)}"
            self.logger.debug(f"URL: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Vérifier si bloqué AVANT de continuer
            if 'cloudflare' in self.driver.page_source.lower() or 'blocked' in self.driver.page_source.lower() or 'ray id' in self.driver.page_source.lower():
                self.logger.warning("⚠️ Indeed bloqué par Cloudflare - SKIP")
                print("⚠ Indeed: Bloqué (Cloudflare) - passage aux autres sites")
                return
            
            # Accepter cookies
            try:
                cookie_btn = self.driver.find_element(By.CSS_SELECTOR, '#onetrust-accept-btn-handler, button[id*="accept"], button[id*="cookie"]')
                cookie_btn.click()
                time.sleep(2)
                self.logger.info("✓ Cookies acceptés")
            except: pass
            
            # Scroll
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 600);")
                time.sleep(1.5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Sélecteurs multiples pour Indeed (2024)
            job_cards = []
            selectors = [
                ('div', {'class': 'job_seen_beacon'}),
                ('td', {'class': 'resultContent'}),
                ('div', {'data-testid': 'slider_item'}),
                ('li', {'class': lambda x: x and 'css-' in x}),
                ('div', {'class': 'cardOutline'}),
                ('div', {'class': lambda x: x and 'job' in str(x).lower()})
            ]
            
            for tag, attrs in selectors:
                job_cards = soup.find_all(tag, attrs)
                if job_cards:
                    self.logger.info(f"✓ Sélecteur trouvé: {tag} {attrs} -> {len(job_cards)} cards")
                    break
            
            if not job_cards:
                self.logger.warning("⚠️ Aucune offre trouvée avec les sélecteurs")
                print("⚠ Indeed: 0 offres (sélecteurs obsolètes)")
                return
            
            self.logger.info(f"📊 {len(job_cards)} offres trouvées")
            
            for card in job_cards[:30]:
                try:
                    # Titre - sélecteurs multiples
                    title = None
                    for sel in ['h2.jobTitle', 'h2 span[title]', 'h2 a', 'a[class*="jobTitle"]', 'h2']:
                        elem = card.select_one(sel)
                        if elem:
                            title = elem.get('title') or elem.get_text(strip=True)
                            if title and len(title) > 3:
                                break
                    
                    if not title:
                        continue
                    
                    # Lien
                    link = None
                    for sel in ['h2 a', 'a[class*="jobTitle"]', 'a[href*="/rc/clk"]', 'a[href*="/viewjob"]']:
                        elem = card.select_one(sel)
                        if elem and elem.get('href'):
                            link = elem['href']
                            if link.startswith('/'):
                                link = 'https://fr.indeed.com' + link
                            break
                    
                    if not link or not link.startswith('http'):
                        continue
                    
                    # Entreprise
                    company = 'N/A'
                    for sel in ['span[data-testid="company-name"]', 'span.companyName', 'div.companyName', 'span[class*="company"]']:
                        elem = card.select_one(sel)
                        if elem:
                            company = elem.get_text(strip=True)
                            break
                    
                    # Localisation
                    loc = location
                    for sel in ['div[data-testid="text-location"]', 'div.companyLocation', 'span[class*="location"]']:
                        elem = card.select_one(sel)
                        if elem:
                            loc = elem.get_text(strip=True)
                            break
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': loc,
                        'link': link,
                        'source': 'Indeed',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)
                    self.logger.debug(f"✅ {title[:40]}")
                        
                except Exception as e:
                    self.logger.debug(f"⚠️ Erreur card: {e}")
                    continue
            
            count = len([j for j in self.jobs if j['source']=='Indeed'])
            self.logger.info(f"✅ Indeed: {count} offres")
            print(f"✓ Indeed: {count} offres")
        except Exception as e:
            self.logger.warning(f"⚠️ Indeed erreur (skip): {e}")
            print(f"⚠ Indeed: Erreur - passage aux autres sites")
    
    def scrape_linkedin(self, keywords, location):
        self.logger.info(f"\n{'='*60}")
        self.logger.info("🔍 Scraping LinkedIn")
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(keywords)}&location={urllib.parse.quote(location)}"
            self.driver.get(url)
            time.sleep(5)
            
            # Cookies
            try:
                for sel in ['button[action-type="ACCEPT"]', 'button[data-tracking-control-name*="accept"]', 'button[class*="cookie"]']:
                    try:
                        cookie_btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        cookie_btn.click()
                        time.sleep(2)
                        break
                    except: continue
            except: pass
            
            # Scroll
            for i in range(4):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1.5)
            
            # Sélecteur LinkedIn 2024 (vérifié)
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.base-card.job-search-card')
            self.logger.info(f"📋 LinkedIn: {len(cards)} cards trouvées")
            
            for card in cards[:50]:
                try:
                    # Titre (h3 dans base-card)
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, 'h3')
                        title = title_elem.text.strip()
                    except:
                        continue
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Link AVANT company (plus important)
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link, a[href*="/jobs/view"]')
                        link = link_elem.get_attribute('href')
                    except:
                        continue
                    
                    if not link or 'linkedin.com' not in link:
                        continue
                    
                    # Company (h4 ou subtitle)
                    company = 'N/A'
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, 'h4, .base-search-card__subtitle, a.hidden-nested-link')
                        company = company_elem.text.strip()
                    except: pass
                    
                    # Location
                    loc = location
                    try:
                        loc_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__location, span[class*="location"]')
                        loc = loc_elem.text.strip()
                    except: pass
                    
                    job = {
                        'title': title_elem.text.strip(),
                        'company': company,
                        'location': loc,
                        'link': link,
                        'source': 'LinkedIn',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)
                    self.logger.debug(f"✅ Ajouté: {job['title'][:40]}")
                except Exception as e:
                    self.logger.debug(f"⚠️ Erreur card: {e}")
            
            count = len([j for j in self.jobs if j['source']=='LinkedIn'])
            self.logger.info(f"✅ LinkedIn: {count} offres")
            print(f"✓ LinkedIn: {count} offres")
        except Exception as e:
            self.logger.error(f"❌ Erreur LinkedIn: {e}")
            print(f"✗ LinkedIn: {e}")
    
    def scrape_welcometothejungle(self, keywords, location):
        try:
            url = f"https://www.welcometothejungle.com/fr/jobs?query={urllib.parse.quote(keywords)}&aroundQuery={urllib.parse.quote(location)}"
            self.driver.get(url)
            time.sleep(5)
            
            # Cookies
            try:
                for sel in ['button[data-testid="button-accept-all"]', 'button[id*="accept"]', 'button[class*="cookie"]']:
                    try:
                        cookie_btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        cookie_btn.click()
                        time.sleep(2)
                        break
                    except: continue
            except: pass
            
            for i in range(2):
                self.driver.execute_script("window.scrollBy(0, 600);")
                time.sleep(1)
            
            # Sélecteur WTTJ 2024 (vérifié)
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="search-results-list-item-wrapper"]')[:30]
            self.logger.info(f"📋 WTTJ: {len(cards)} cards trouvées")
            for card in cards:
                try:
                    # Titre (h2 dans le card)
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, 'h2')
                        title = title_elem.text.strip()
                    except:
                        continue
                    
                    if not title:
                        continue
                    
                    # Company (span avec class contenant text)
                    company = 'N/A'
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, 'span.sc-TezEC, span[class*="wui-text"]')
                        company = company_elem.text.strip()
                    except: pass
                    
                    # Link (a principal)
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, 'a[href*="/jobs/"]')
                        link = link_elem.get_attribute('href')
                        if not link.startswith('http'):
                            link = 'https://www.welcometothejungle.com' + link
                    except:
                        continue
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'WTTJ',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)
                except: pass
            print(f"✓ WTTJ: {len([j for j in self.jobs if j['source']=='WTTJ'])} offres")
        except Exception as e:
            print(f"✗ WTTJ: {e}")
    
    def scrape_apec(self, keywords, location):
        try:
            url = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles={urllib.parse.quote(keywords)}"
            self.driver.get(url)
            time.sleep(6)

            # Cookies
            try:
                for sel in ['#didomi-notice-agree-button', 'button[id*="accept"]']:
                    try:
                        cookie_btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                        cookie_btn.click()
                        time.sleep(2)
                        break
                    except:
                        continue
            except:
                pass

            time.sleep(3)

            # Structure APEC 2024–2025
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="offer-card"]')[:30]
            self.logger.info(f"📋 APEC: {len(cards)} cards trouvées")

            if not cards:
                self.logger.warning("⚠️ APEC: Aucune offre (auth requise?)")
                print("⚠ APEC: 0 offres (authentification requise?)")
                return

            for card in cards:
                try:
                    # Titre
                    try:
                        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="offer-title"]').text.strip()
                    except:
                        continue

                    if not title:
                        continue

                    # Entreprise
                    try:
                        company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text.strip()
                    except:
                        company = "N/A"

                    # Lien
                    try:
                        link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        if not link.startswith("http"):
                            link = "https://www.apec.fr" + link
                    except:
                        continue

                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'APEC',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)

                except:
                    pass

            count = len([j for j in self.jobs if j['source'] == 'APEC'])
            print(f"✓ APEC: {count} offres")

        except Exception as e:
            self.logger.warning(f"⚠️ APEC erreur: {e}")
            print(f"⚠ APEC: Erreur - skip")
    def scrape_hellowork(self, keywords, location):
        try:
            url = f"https://www.hellowork.com/fr-fr/emplois.html?k={urllib.parse.quote(keywords)}"
            self.driver.get(url)
            time.sleep(5)

            # Cookies
            try:
                for sel in ['button[id*="accept"]', 'button[class*="accept"]', 'button[data-testid="cookie-accept"]']:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, sel).click()
                        time.sleep(2)
                        break
                    except:
                        continue
            except:
                pass

            # Scroll pour charger les offres
            for _ in range(4):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)

            # Structure HelloWork 2024–2025
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="job-card"]')[:30]
            self.logger.info(f"📋 HelloWork: {len(cards)} cards trouvées")

            if not cards:
                print("⚠ HelloWork: 0 offres")
                return

            for card in cards:
                try:
                    # Titre
                    try:
                        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="job-title"]').text.strip()
                    except:
                        continue

                    # Entreprise
                    try:
                        company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text.strip()
                    except:
                        company = "N/A"

                    # Lien
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    except:
                        continue

                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'HelloWork',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)

                except:
                    pass

            count = len([j for j in self.jobs if j['source'] == 'HelloWork'])
            print(f"✓ HelloWork: {count} offres")

        except Exception as e:
            print(f"⚠ HelloWork: Erreur - skip")
            self.logger.warning(f"⚠️ HelloWork erreur: {e}")

    
    def scrape_meteojob(self, keywords, location):
        try:
            url = f"https://www.meteojob.com/recherche-emploi?keywords={urllib.parse.quote(keywords)}"
            self.driver.get(url)
            time.sleep(5)

            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)

            # Structure Meteojob 2024–2025
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="job-card"]')[:30]
            self.logger.info(f"📋 Meteojob: {len(cards)} cards trouvées")

            if not cards:
                print("⚠ Meteojob: 0 offres")
                return

            for card in cards:
                try:
                    # Titre
                    try:
                        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="job-title"]').text.strip()
                    except:
                        continue

                    # Entreprise
                    try:
                        company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text.strip()
                    except:
                        company = "N/A"

                    # Lien
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    except:
                        continue

                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'Meteojob',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)

                except:
                    pass

            count = len([j for j in self.jobs if j['source'] == 'Meteojob'])
            print(f"✓ Meteojob: {count} offres")

        except Exception as e:
            print(f"⚠ Meteojob: Erreur - skip")
            self.logger.warning(f"⚠️ Meteojob erreur: {e}")
    def scrape_regionsjob(self, keywords, location):
        try:
            url = f"https://www.regionsjob.com/emplois/{urllib.parse.quote(keywords)}.html"
            self.driver.get(url)
            time.sleep(5)

            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)

            # Structure RegionsJob 2024–2025
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="job-card"]')[:30]
            self.logger.info(f"📋 RegionsJob: {len(cards)} cards trouvées")

            if not cards:
                print("⚠ RegionsJob: 0 offres")
                return

            for card in cards:
                try:
                    # Titre
                    try:
                        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="job-title"]').text.strip()
                    except:
                        continue

                    # Entreprise
                    try:
                        company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text.strip()
                    except:
                        company = "N/A"

                    # Lien
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    except:
                        continue

                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'RegionsJob',
                        'scraped_at': datetime.now().isoformat()
                    }
                    self.jobs.append(job)

                except:
                    pass

            count = len([j for j in self.jobs if j['source'] == 'RegionsJob'])
            print(f"✓ RegionsJob: {count} offres")

        except Exception as e:
            print(f"⚠ RegionsJob: Erreur - skip")
            self.logger.warning(f"⚠️ RegionsJob erreur: {e}")

    def scrape_monster(self, keywords, location):
        try:
            url = f"https://www.monster.fr/emplois/recherche/?q={urllib.parse.quote(keywords)}"
            self.driver.get(url)
            time.sleep(5)
            
            # Monster structure 2024
            cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="job-card"], article[class*="job"]')[:30]
            self.logger.info(f"📋 Monster: {len(cards)} cards trouvées")
            
            if not cards:
                self.logger.warning("⚠️ Monster: Aucune offre")
                print("⚠ Monster: 0 offres")
                return
            
            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, 'h2, h3, a[class*="title"]').text
                    company = card.find_element(By.CSS_SELECTOR, '.company, span[class*="company"]').text
                    link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    
                    if title and link:
                        job = {
                            'title': title,
                            'company': company if company else 'N/A',
                            'location': location,
                            'link': link,
                            'source': 'Monster',
                            'scraped_at': datetime.now().isoformat()
                        }
                        self.jobs.append(job)
                except: pass
            
            count = len([j for j in self.jobs if j['source']=='Monster'])
            print(f"✓ Monster: {count} offres")
        except Exception as e:
            self.logger.warning(f"⚠️ Monster erreur: {e}")
            print(f"⚠ Monster: Erreur - skip")
    
    def get_job_details(self, url):
        try:
            self.driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return soup.get_text()[:5000]
        except:
            return ""
    
    def close(self):
        self.logger.info("🔒 Fermeture du driver")
        self.driver.quit()
        self.logger.info("✓ Driver fermé")
