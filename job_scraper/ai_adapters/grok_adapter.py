import requests
import json
from datetime import datetime

class GrokAIAdapter:
    def __init__(self, api_key):
        self.api_key = api_key
        # Détecter si c'est Groq ou Grok
        if api_key.startswith('gsk_'):
            # Clé Groq
            self.base_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile"
        else:
            # Clé Grok (x.ai)
            self.base_url = "https://api.x.ai/v1/chat/completions"
            self.model = "grok-beta"
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_cv_adaptation(self, base_cv, job_description, profile):
        """Adapter le CV pour une offre spécifique"""
        prompt = f"""Tu es un expert en recrutement. Adapte ce CV pour correspondre parfaitement à cette offre d'emploi.

PROFIL CANDIDAT:
- Nom: {profile['name']}
- GitHub: {profile['github']}
- Portfolio: {profile['portfolio']}

CV DE BASE:
{base_cv}

OFFRE D'EMPLOI:
{job_description}

INSTRUCTIONS:
1. Réorganise les compétences pour mettre en avant celles demandées
2. Adapte les descriptions de projets pour correspondre aux besoins
3. Utilise les mots-clés de l'offre
4. Garde un ton professionnel et authentique
5. Format: Markdown

Génère le CV adapté:"""

        response = self._call_api(prompt, max_tokens=2000)
        return response
    
    def generate_cover_letter_from_base(self, job_info, profile, cv_content, base_letter):
        """Générer une lettre en s'inspirant de la base"""
        prompt = f"""Tu es un expert en candidatures. Adapte cette lettre de motivation pour cette offre.

LETTRE DE BASE (ton et style à conserver):
{base_letter}

PROFIL:
- Nom: {profile['name']}
- Email: {profile['email']}

OFFRE:
- Poste: {job_info['title']}
- Entreprise: {job_info['company']}
- Description: {job_info.get('description', '')[:1000]}

CV DU CANDIDAT:
{cv_content[:800]}

INSTRUCTIONS:
1. Garde le ton et style de la lettre de base
2. Adapte le contenu pour cette offre spécifique
3. Montre la compréhension de l'entreprise et du poste
4. Lie expérience du CV aux besoins de l'offre
5. Reste authentique et humain
6. Maximum 300 mots

Lettre adaptée:"""

        response = self._call_api(prompt, max_tokens=1000)
        return response
    
    def analyze_job_match(self, cv_content, job_description):
        """Analyser la compatibilité CV/offre"""
        prompt = f"""Analyse la compatibilité entre ce CV et cette offre. Note de 0 à 100.

CV:
{cv_content[:1500]}

OFFRE:
{job_description[:1500]}

Réponds en JSON:
{{
  "score": 85,
  "strengths": ["point fort 1", "point fort 2"],
  "gaps": ["manque 1", "manque 2"],
  "recommendations": ["conseil 1", "conseil 2"]
}}"""

        response = self._call_api(prompt, max_tokens=500)
        try:
            return json.loads(response)
        except:
            return {"score": 0, "error": "Parse error"}
    
    def humanize_text(self, text):
        """Rendre le texte plus humain"""
        prompt = f"""Réécris ce texte pour qu'il paraisse plus naturel et humain, sans perdre le professionnalisme:

{text}

Texte humanisé:"""

        return self._call_api(prompt, max_tokens=1000)
    
    def _call_api(self, prompt, max_tokens=1000):
        """Appel API Grok/Groq"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Tu es un assistant expert en recrutement et rédaction professionnelle."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Erreur API: {response.status_code}"
                
        except Exception as e:
            return f"Erreur: {str(e)}"
