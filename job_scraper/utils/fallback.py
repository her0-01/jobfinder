"""Système de fallback intelligent pour ne jamais renvoyer 0 résultats"""
import re

class FallbackSystem:
    def __init__(self):
        self.synonyms = {
            "dev": ["développeur", "developer"],
            "devops": ["développeur opérations", "dev ops"],
            "fullstack": ["full stack", "full-stack"],
            "frontend": ["front end", "front-end"],
            "backend": ["back end", "back-end"],
            "ia": ["intelligence artificielle", "ai"],
            "ml": ["machine learning", "apprentissage automatique"],
        }
    
    def simplify_keywords(self, keywords):
        """Simplifie les mots-clés pour fallback"""
        words = keywords.lower().split()
        # Garder les 2 premiers mots importants
        important = [w for w in words if len(w) > 3]
        return " ".join(important[:2]) if important else keywords
    
    def get_synonyms(self, keywords):
        """Retourne des synonymes pour fallback"""
        keywords_lower = keywords.lower()
        for abbr, full_list in self.synonyms.items():
            if abbr in keywords_lower:
                return [keywords_lower.replace(abbr, syn) for syn in full_list]
        return []
    
    def remove_location(self, location):
        """Fallback sans localisation"""
        return ""
    
    def get_generic_keywords(self, keywords):
        """Extrait le mot-clé le plus générique"""
        words = keywords.lower().split()
        # Prendre le premier mot significatif
        for word in words:
            if len(word) > 4:
                return word
        return keywords
