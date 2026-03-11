"""Découverte automatique de sites carrières pertinents"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse, urljoin

class CareerSiteDiscovery:
    def __init__(self):
        self.cache_file = Path("data/discovered_career_sites.json")
        self.cache_file.parent.mkdir(exist_ok=True)
        self.discovered_sites = self._load_cache()
        
        # Charger la base de données de sites prédéfinis
        self.sites_db_file = Path(__file__).parent / "career_sites_db.json"
        self.sites_db = self._load_sites_db()
    
    def _load_sites_db(self):
        """Charge la base de données de sites prédéfinis"""
        if self.sites_db_file.exists():
            with open(self.sites_db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_cache(self):
        """Charge le cache des sites découverts"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Sauvegarde le cache"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.discovered_sites, f, ensure_ascii=False, indent=2)
    
    async def discover_career_sites(self, keywords, location="France", max_companies=20):
        """
        Découvre automatiquement les sites carrières pertinents
        
        Stratégie:
        1. Utiliser la base de données prédéfinie selon le secteur
        2. Compléter avec recherche Google si nécessaire
        """
        print(f"🔍 Découverte de sites carrières pour: {keywords} @ {location}")
        
        # Extraire le secteur/domaine des keywords
        sector = self._extract_sector(keywords)
        print(f"📊 Secteur détecté: {sector}")
        
        # Vérifier cache (valide 7 jours)
        cache_key = f"{sector}_{location}"
        if cache_key in self.discovered_sites:
            cached = self.discovered_sites[cache_key]
            cache_date = datetime.fromisoformat(cached['discovered_at'])
            if datetime.now() - cache_date < timedelta(days=7):
                print(f"💾 Cache valide: {len(cached['sites'])} sites")
                return cached['sites']
        
        # Utiliser la base de données prédéfinie
        discovered = []
        
        # Mapping secteur → catégories DB
        sector_mapping = {
            'data': ['data_tech', 'consulting'],
            'tech': ['data_tech', 'startup'],
            'finance': ['finance', 'consulting'],
            'ecommerce': ['ecommerce', 'startup'],
            'consulting': ['consulting']
        }
        
        # Trouver les catégories correspondantes
        categories = []
        for key, cats in sector_mapping.items():
            if key in sector.lower():
                categories.extend(cats)
        
        # Par défaut: toutes les catégories
        if not categories:
            categories = list(self.sites_db.keys())
        
        # Récupérer les sites de la DB
        for category in categories:
            if category in self.sites_db:
                for site in self.sites_db[category]:
                    if len(discovered) < max_companies:
                        discovered.append({
                            'name': site['name'],
                            'domain': site['domain'],
                            'career_url': site['career_url'],
                            'discovered_at': datetime.now().isoformat(),
                            'source': 'database'
                        })
        
        print(f"✅ {len(discovered)} sites depuis la base de données")
        
        # Sauvegarder en cache
        self.discovered_sites[cache_key] = {
            'sector': sector,
            'location': location,
            'sites': discovered,
            'discovered_at': datetime.now().isoformat()
        }
        self._save_cache()
        
        print(f"✅ {len(discovered)} sites carrières découverts")
        return discovered
    
    def _extract_sector(self, keywords):
        """Extrait le secteur/domaine des keywords"""
        # Mapping keywords → secteurs
        sectors = {
            'data': 'data science tech',
            'engineer': 'ingénierie tech',
            'développeur': 'développement logiciel',
            'finance': 'finance banque',
            'marketing': 'marketing digital',
            'commercial': 'vente commerce',
            'rh': 'ressources humaines',
            'logistique': 'supply chain logistique',
            'santé': 'santé médical',
            'juridique': 'droit juridique'
        }
        
        keywords_lower = keywords.lower()
        for key, sector in sectors.items():
            if key in keywords_lower:
                return sector
        
        return keywords  # Par défaut
    
    async def _search_companies(self, sector, location, max_companies):
        """Recherche les entreprises du secteur via Google"""
        companies = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Recherche Google avec user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Recherche Google
                queries = [
                    f"grandes entreprises {sector} {location} recrutement",
                    f"top entreprises {sector} France carrières",
                    f"{sector} {location} offres emploi site carrière"
                ]
                
                for query in queries:
                    print(f"🔎 Google: {query}")
                    
                    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"
                    await page.goto(url, timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Extraire les résultats
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Stratégie 1: Trouver les divs de résultats
                    results = soup.find_all('div', class_='g')
                    print(f"  📊 {len(results)} résultats Google trouvés")
                    
                    for result in results:
                        # Chercher le lien
                        link_tag = result.find('a', href=True)
                        if not link_tag:
                            continue
                        
                        href = link_tag['href']
                        
                        # Extraire l'URL réelle
                        if href.startswith('/url?q='):
                            match = re.search(r'/url\?q=([^&]+)', href)
                            if match:
                                url = match.group(1)
                            else:
                                continue
                        elif href.startswith('http'):
                            url = href
                        else:
                            continue
                        
                        # Vérifier que c'est un site d'entreprise
                        if self._is_company_site(url):
                            domain = urlparse(url).netloc
                            
                            # Éviter les doublons
                            if not any(c['domain'] == domain for c in companies):
                                company_name = self._extract_company_name(domain)
                                companies.append({
                                    'name': company_name,
                                    'domain': domain,
                                    'url': url
                                })
                                
                                print(f"  ✓ {company_name} ({domain})")
                                
                                if len(companies) >= max_companies:
                                    break
                    
                    if len(companies) >= max_companies:
                        break
                    
                    await page.wait_for_timeout(3000)  # Éviter rate limit
                
            except Exception as e:
                print(f"❌ Erreur recherche Google: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
        
        print(f"\n🎯 {len(companies)} entreprises trouvées")
        
        # Découvrir les pages carrières pour chaque entreprise
        career_sites = []
        for company in companies[:max_companies]:
            career_url = await self._find_career_page(company)
            if career_url:
                career_sites.append({
                    'name': company['name'],
                    'domain': company['domain'],
                    'career_url': career_url,
                    'discovered_at': datetime.now().isoformat()
                })
        
        return career_sites
    
    def _is_company_site(self, url):
        """Vérifie si l'URL est un site d'entreprise (pas LinkedIn, Indeed, etc.)"""
        excluded = [
            'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
            'apec.fr', 'welcometothejungle.com', 'hellowork.com',
            'wikipedia.org', 'youtube.com', 'facebook.com', 'twitter.com'
        ]
        
        domain = urlparse(url).netloc.lower()
        return not any(excl in domain for excl in excluded)
    
    def _extract_company_name(self, domain):
        """Extrait le nom de l'entreprise depuis le domaine"""
        # Retirer www, .com, .fr, etc.
        name = domain.replace('www.', '').split('.')[0]
        return name.capitalize()
    
    async def _find_career_page(self, company):
        """Trouve la page carrière d'une entreprise"""
        print(f"🔍 Recherche page carrière: {company['name']}")
        
        # URLs communes pour les pages carrières
        career_paths = [
            '/careers', '/career', '/jobs', '/emploi', '/recrutement',
            '/join-us', '/rejoindre', '/offres', '/opportunities',
            '/fr/careers', '/fr/emploi', '/en/careers'
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                base_url = f"https://{company['domain']}"
                
                # Essayer d'abord la page d'accueil
                await page.goto(base_url, timeout=10000)
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Chercher des liens vers carrières
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    text = link.get_text().lower()
                    
                    # Mots-clés carrières
                    career_keywords = ['carri', 'job', 'emploi', 'recrutement', 'rejoindre', 'opportunit']
                    
                    if any(kw in href or kw in text for kw in career_keywords):
                        career_url = urljoin(base_url, link['href'])
                        
                        # Vérifier que la page contient des offres
                        if await self._validate_career_page(page, career_url):
                            print(f"  ✅ Trouvé: {career_url}")
                            await browser.close()
                            return career_url
                
                # Si pas trouvé, essayer les chemins communs
                for path in career_paths:
                    try:
                        test_url = base_url + path
                        await page.goto(test_url, timeout=5000)
                        
                        if page.url != test_url and '404' not in page.url:
                            # Redirection = page existe
                            if await self._validate_career_page(page, page.url):
                                print(f"  ✅ Trouvé: {page.url}")
                                await browser.close()
                                return page.url
                    except:
                        continue
                
                print(f"  ❌ Pas de page carrière trouvée")
                
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
            
            finally:
                await browser.close()
        
        return None
    
    async def _validate_career_page(self, page, url):
        """Valide qu'une page contient bien des offres d'emploi"""
        try:
            await page.goto(url, timeout=10000)
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Chercher des indicateurs d'offres
            text = soup.get_text().lower()
            
            # Mots-clés positifs
            job_indicators = ['poste', 'offre', 'candidat', 'postuler', 'apply', 'position']
            
            # Compter les occurrences
            count = sum(text.count(indicator) for indicator in job_indicators)
            
            # Si au moins 5 occurrences = probablement une page d'offres
            return count >= 5
            
        except:
            return False


async def test_discovery():
    """Test du système de découverte"""
    discovery = CareerSiteDiscovery()
    
    # Test avec différents secteurs
    test_cases = [
        ("data engineer alternance", "France"),
        ("développeur web", "Paris"),
        ("commercial", "Lyon")
    ]
    
    for keywords, location in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {keywords} @ {location}")
        print('='*60)
        
        sites = await discovery.discover_career_sites(keywords, location, max_companies=10)
        
        print(f"\n📊 Résultats: {len(sites)} sites découverts")
        for site in sites:
            print(f"  • {site['name']}: {site['career_url']}")


if __name__ == "__main__":
    asyncio.run(test_discovery())
