import json
from pathlib import Path

class URLLearner:
    def __init__(self):
        self.patterns_file = Path(__file__).parent / "patterns.json"
        self.patterns = self._load()
    
    def _load(self):
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "indeed": {"base": "https://fr.indeed.com/jobs", "params": {"q": "keywords", "l": "location"}},
            "linkedin": {"base": "https://www.linkedin.com/jobs/search", "params": {"keywords": "keywords", "location": "location"}}
        }
    
    def build_url(self, site, keywords, location):
        if site not in self.patterns:
            return None
        pattern = self.patterns[site]
        params = "&".join([f"{k}={v}" for k, v in pattern["params"].items()])
        url = f"{pattern['base']}?{params}"
        return url.replace("keywords", keywords).replace("location", location)
    
    def save(self):
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
