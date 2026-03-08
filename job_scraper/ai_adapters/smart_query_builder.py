import requests
import json
from bs4 import BeautifulSoup
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ai_adapters.universal_ai import get_ai_adapter

class SmartQueryBuilder:
    """Agent IA qui analyse les sites et construit les requêtes optimales"""
    
    def __init__(self, groq_api_key=None):
        self.ai = get_ai_adapter()  # Utilise le provider configuré
        self.cache = {}  # Cache des analyses par site
    
    def analyze_and_build_url(self, site_url, keywords, location, contract_type, driver):
        """Analyse le site et construit l'URL optimale"""
        
        # Vérifier le cache
        cache_key = f"{site_url}_{contract_type}"
        if cache_key in self.cache:
            return self._apply_params(self.cache[cache_key], keywords, location, contract_type)
        
        print(f"  🔍 Analyse IA du site {site_url}...")
        
        # 1. Charger la page de recherche
        driver.get(site_url)
        time.sleep(3)
        
        # 2. Extraire le HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 3. Analyser avec l'IA
        analysis = self._analyze_with_ai(site_url, html[:8000])
        
        # 4. Mettre en cache
        self.cache[cache_key] = analysis
        
        # 5. Construire l'URL
        return self._apply_params(analysis, keywords, location, contract_type)
    
    def _analyze_with_ai(self, site_url, html_sample):
        """Utilise l'IA pour analyser et construire l'URL de recherche"""
        
        # Prompt ultra-simple et court pour tous les providers
        prompt = f"""Site: {site_url}

HTML:
{html_sample[:3000]}

Trouve les paramètres URL pour recherche d'emploi.
Exemple: si tu vois "?q=test&location=paris", réponds {{"keywords":"q","location":"location"}}

JSON uniquement:"""

        try:
            response = self.ai.chat_completion_with_fallback(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=100,
                json_mode=True
            )
            
            # Nettoyage agressif pour tous les providers
            cleaned = response.strip()
            
            # Enlever markdown (```json ou ```)
            if '```' in cleaned:
                parts = cleaned.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json'):
                        part = part[4:].strip()
                    if part.startswith('{'):
                        cleaned = part
                        break
            
            # Extraire le premier objet JSON valide
            if '{' in cleaned:
                start = cleaned.index('{')
                # Trouver le } correspondant
                count = 0
                end = start
                for i in range(start, len(cleaned)):
                    if cleaned[i] == '{':
                        count += 1
                    elif cleaned[i] == '}':
                        count -= 1
                        if count == 0:
                            end = i + 1
                            break
                cleaned = cleaned[start:end]
            
            params = json.loads(cleaned)
            
            # Normaliser les clés (différents providers peuvent retourner différents formats)
            normalized = {}
            for key in ['keywords', 'keyword', 'search', 'query', 'q']:
                if key in params:
                    normalized['keywords'] = params[key]
                    break
            
            for key in ['location', 'loc', 'where', 'place']:
                if key in params:
                    normalized['location'] = params[key]
                    break
            
            for key in ['contract', 'type', 'contractType', 'jobType']:
                if key in params:
                    normalized['contract'] = params[key]
                    break
            
            # Si aucun param trouvé, utiliser fallback
            if not normalized:
                return self._fallback_analysis(site_url)
            
            return {
                'base_url': site_url,
                'params': normalized,
                'contract_values': {
                    'Alternance': 'alternance',
                    'CDI': 'cdi',
                    'CDD': 'cdd',
                    'Stage': 'stage'
                }
            }
            
        except Exception as e:
            # Fallback silencieux pour tous les cas d'erreur
            return self._fallback_analysis(site_url)
    
    def _fallback_analysis(self, site_url):
        """Analyse basique si l'IA échoue - détection intelligente des paramètres"""
        # Patterns courants pour les paramètres
        common_patterns = {
            'keywords': ['q', 'query', 'search', 'keyword', 'k', 'text', 'what'],
            'location': ['location', 'l', 'loc', 'where', 'city', 'place', 'region'],
            'contract': ['contract', 'type', 'contractType', 'jobType', 'employment']
        }
        
        # Essayer de détecter depuis l'URL
        params = {}
        if '?' in site_url:
            query_part = site_url.split('?')[1]
            existing_params = [p.split('=')[0] for p in query_part.split('&') if '=' in p]
            
            # Matcher avec les patterns
            for param_type, patterns in common_patterns.items():
                for existing in existing_params:
                    if any(pattern in existing.lower() for pattern in patterns):
                        params[param_type] = existing
                        break
        
        # Valeurs par défaut si rien trouvé
        if 'keywords' not in params:
            params['keywords'] = 'q'
        if 'location' not in params:
            params['location'] = 'location'
        if 'contract' not in params:
            params['contract'] = 'contract'
        
        return {
            "base_url": site_url,
            "params": params,
            "contract_values": {
                "Alternance": "alternance",
                "CDI": "cdi",
                "CDD": "cdd",
                "Stage": "stage"
            },
            "method": "GET"
        }
    
    def _apply_params(self, analysis, keywords, location, contract_type):
        """Applique les paramètres à l'analyse pour construire l'URL finale"""
        
        base = analysis.get('base_url', '')
        params = analysis.get('params', {})
        contract_values = analysis.get('contract_values', {})
        
        # Construire les paramètres
        url_params = []
        
        # Mots-clés
        if 'keywords' in params and keywords:
            url_params.append(f"{params['keywords']}={requests.utils.quote(keywords)}")
        
        # Localisation
        if 'location' in params and location:
            url_params.append(f"{params['location']}={requests.utils.quote(location)}")
        
        # Type de contrat
        if 'contract' in params and contract_type:
            contract_value = contract_values.get(contract_type, contract_type.lower())
            url_params.append(f"{params['contract']}={contract_value}")
        
        # Construire l'URL finale
        separator = '&' if '?' in base else '?'
        final_url = base + separator + '&'.join(url_params)
        
        return final_url
    
    def interact_with_filters(self, driver, analysis, keywords, location, contract_type):
        """Interagit avec les filtres du site (dropdowns, checkboxes)"""
        
        try:
            # Si l'analyse indique des éléments de formulaire
            if 'form_elements' in analysis:
                elements = analysis['form_elements']
                
                # Remplir le champ de recherche
                if 'search_input' in elements:
                    search_box = driver.find_element(By.CSS_SELECTOR, elements['search_input'])
                    search_box.clear()
                    search_box.send_keys(keywords)
                
                # Sélectionner la localisation
                if 'location_input' in elements:
                    location_box = driver.find_element(By.CSS_SELECTOR, elements['location_input'])
                    location_box.clear()
                    location_box.send_keys(location)
                
                # Sélectionner le type de contrat
                if 'contract_select' in elements:
                    contract_select = driver.find_element(By.CSS_SELECTOR, elements['contract_select'])
                    # Trouver l'option correspondante
                    options = contract_select.find_elements(By.TAG_NAME, 'option')
                    for option in options:
                        if contract_type.lower() in option.text.lower():
                            option.click()
                            break
                
                # Cliquer sur le bouton de recherche
                if 'submit_button' in elements:
                    submit = driver.find_element(By.CSS_SELECTOR, elements['submit_button'])
                    submit.click()
                    time.sleep(3)
                    return True
            
            return False
            
        except Exception as e:
            print(f"  ⚠️ Erreur interaction filtres: {e}")
            return False
