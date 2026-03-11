"""Filtrage intelligent des offres d'emploi avec IA"""
import re
from typing import List, Dict

class SmartJobFilter:
    """Filtre intelligent IA pour éliminer les fausses offres"""
    
    def __init__(self, ai_adapter=None):
        self.ai_adapter = ai_adapter  # Groq/Gemini pour classification
    
    def is_valid_job_with_ai(self, job_title: str, search_keywords: str) -> Dict:
        """
        Utilise l'IA pour déterminer si c'est une vraie offre d'emploi
        
        Returns:
            {'is_valid': bool, 'confidence': float, 'reason': str}
        """
        if not self.ai_adapter:
            # Fallback sans IA
            return {'is_valid': True, 'confidence': 0.5, 'reason': 'No AI'}
        
        try:
            prompt = f"""Tu es un expert en classification d'offres d'emploi.

RECHERCHE: "{search_keywords}"
TITRE: "{job_title}"

QUESTION: Est-ce que "{job_title}" est une VRAIE offre d'emploi ou un lien de navigation/menu ?

CRITÈRES:
- VRAIE OFFRE = Titre de poste concret (ex: "Data Engineer", "Poissonnier", "Chef de projet")
- FAUX = Navigation ("Trier par", "Voir toutes"), Langue ("Français", "English"), Catégorie ("Offres d'emploi"), Nom entreprise seul ("BOUYGUES")

EXEMPLES:
- "Data Engineer - Alternance" → VRAIE (poste précis)
- "Poissonnier H/F" → VRAIE (métier)
- "Trier par Pertinence" → FAUX (bouton)
- "Offres d'emploi" → FAUX (catégorie)
- "Brazilian portuguese" → FAUX (langue)
- "BOUYGUES CONSTRUCTION" → FAUX (nom entreprise)
- "Ajusteur mouliste F-H" → VRAIE (métier)

Réponds en JSON:
{{
  "is_valid": true/false,
  "confidence": 0.0-1.0,
  "reason": "Explication courte(10 MOTS MAX)"
}}"""
            
            response = self.ai_adapter._call_agent(
                model=self.ai_adapter.models["fast"],
                system="Tu es un classificateur d'offres d'emploi. Réponds UNIQUEMENT en JSON valide.",
                prompt=prompt,
                max_tokens=100
            )
            
            # Parser la réponse JSON
            import json
            # Extraire le JSON de la réponse
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return {'is_valid': True, 'confidence': 0.5, 'reason': 'Parse error'}
                
        except Exception as e:
            print(f"⚠️ Erreur classification IA: {e}")
            return {'is_valid': True, 'confidence': 0.5, 'reason': str(e)}
    
    def calculate_relevance_with_ai(self, job_title: str, search_keywords: str) -> int:
        """
        Calcule un score de pertinence avec l'IA (0-100)
        """
        if not self.ai_adapter:
            return 50
        
        try:
            prompt = f"""Analyse la pertinence STRICTE.

RECHERCHE: "{search_keywords}"
TITRE OFFRE: "{job_title}"

RÈGLES:
1. Aucun mot-clé commun: 0-20
2. 1 mot-clé mais contexte différent: 20-40
3. Domaine proche: 40-60
4. Bon match avec différences: 60-80
5. Match parfait: 80-100

EXEMPLES:
- Recherche "Data Engineer" + "Poissonnier" = 0
- Recherche "Data Engineer" + "Software Engineer" = 40
- Recherche "Data Engineer" + "Data Analyst" = 60
- Recherche "Data Engineer Alternance" + "Data Engineer Junior" = 75
- Recherche "Data Engineer Alternance" + "Data Engineer - Alternance" = 95
- Recherche "Poissonnier" + "Poissonnier H/F" = 95
- Recherche "Poissonnier" + "Boucher" = 50

Réponds UNIQUEMENT avec un nombre 0-100."""
            
            response = self.ai_adapter._call_agent(
                model=self.ai_adapter.models["fast"],
                system="Tu es un expert strict. Réponds uniquement avec un nombre.",
                prompt=prompt,
                max_tokens=10
            )
            
            numbers = re.findall(r'\d+', response)
            score = int(numbers[0]) if numbers else 50
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"⚠️ Erreur scoring IA: {e}")
            return 50
    
    def filter_jobs(self, jobs: List[Dict], search_keywords: str, min_score: int = 30) -> List[Dict]:
        """
        Filtre les offres avec IA
        
        Args:
            jobs: Liste des offres
            search_keywords: Mots-clés de recherche
            min_score: Score minimum de pertinence (0-100)
        
        Returns:
            Liste des offres filtrées
        """
        filtered = []
        
        for job in jobs:
            title = job.get('title', '')
            
            # 1. Classification IA: vraie offre ou navigation ?
            classification = self.is_valid_job_with_ai(title, search_keywords)
            
            if not classification['is_valid']:
                print(f"❌ Exclu: {title[:50]} - {classification['reason']}")
                continue
            
            # 2. Score de pertinence IA
            score = self.calculate_relevance_with_ai(title, search_keywords)
            
            # 3. Filtrer selon le score minimum
            if score >= min_score:
                job['ai_relevance_score'] = score
                job['ai_confidence'] = classification['confidence']
                filtered.append(job)
                print(f"✅ Conservé: {title[:50]} - Score: {score}%")
            else:
                print(f"⚠️ Score trop bas: {title[:50]} - {score}%")
        
        return filtered
    
    def get_filter_stats(self, original_count: int, filtered_count: int) -> Dict:
        """Retourne des statistiques sur le filtrage"""
        removed = original_count - filtered_count
        removal_rate = (removed / original_count * 100) if original_count > 0 else 0
        
        return {
            'original_count': original_count,
            'filtered_count': filtered_count,
            'removed_count': removed,
            'removal_rate': round(removal_rate, 1)
        }


def test_filter():
    """Test du filtre intelligent"""
    filter = SmartJobFilter()
    
    # Test cases
    test_jobs = [
        {'title': 'Data Engineer - Alternance', 'company': 'Boursorama'},
        {'title': 'Trier par Pertinence', 'company': 'Safran'},
        {'title': 'Offres d\'emploi', 'company': 'Safran'},
        {'title': 'Ajusteur-euse mouliste F-H', 'company': 'Safran'},
        {'title': 'Brazilian portuguese', 'company': 'Alstom'},
        {'title': 'BOUYGUES CONSTRUCTION', 'company': 'Bouygues'},
        {'title': 'Software Engineer Junior', 'company': 'Google'},
        {'title': 'Data Analyst - Stage', 'company': 'Amazon'},
    ]
    
    search = "Data Engineer Alternance"
    
    print(f"🔍 Recherche: {search}\n")
    print(f"📊 {len(test_jobs)} offres avant filtrage\n")
    
    for job in test_jobs:
        is_valid = filter.is_valid_job(job)
        score = filter.calculate_relevance_score(job, search) if is_valid else 0
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {job['title'][:50]:50} | Score: {score:3}%")
    
    print("\n" + "="*70)
    filtered = filter.filter_jobs(test_jobs, search, min_score=30)
    print(f"\n✅ {len(filtered)} offres après filtrage (score >= 30%)")
    
    for job in filtered:
        print(f"  • {job['title']} - Score: {job['basic_relevance_score']}%")


if __name__ == "__main__":
    test_filter()
