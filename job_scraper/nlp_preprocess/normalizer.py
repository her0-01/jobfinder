import re
import unicodedata

class NLPNormalizer:
    def __init__(self):
        self.stopwords = {"le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "a", "au", "en", "dans", "pour"}
        self.synonyms = {
            "dev": "developpeur",
            "devops": "developpeur operations",
            "fullstack": "full stack",
            "ia": "intelligence artificielle",
            "ml": "machine learning"
        }
    
    def normalize(self, text):
        text = text.lower()
        text = self._remove_accents(text)
        for abbr, full in self.synonyms.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text)
        words = [w for w in text.split() if w not in self.stopwords]
        return " ".join(words)
    
    def _remove_accents(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    def simplify(self, text):
        words = self.normalize(text).split()
        return " ".join(words[:3])
