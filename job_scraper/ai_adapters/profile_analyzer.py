import requests
from bs4 import BeautifulSoup
import json

class ProfileAnalyzer:
    """Analyse GitHub et Portfolio pour personnalisation"""
    
    def __init__(self, github_url, portfolio_url):
        self.github_url = github_url
        self.portfolio_url = portfolio_url
    
    def analyze_github(self):
        """Analyse les repos GitHub"""
        try:
            username = self.github_url.split('github.com/')[-1]
            api_url = f"https://api.github.com/users/{username}/repos"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code != 200:
                return {"error": "GitHub API error"}
            
            repos = response.json()
            
            # Extraire infos pertinentes
            projects = []
            languages = set()
            
            for repo in repos[:10]:  # Top 10 repos
                if not repo.get('fork'):
                    projects.append({
                        'name': repo['name'],
                        'description': repo.get('description', ''),
                        'language': repo.get('language', ''),
                        'stars': repo.get('stargazers_count', 0)
                    })
                    if repo.get('language'):
                        languages.add(repo['language'])
            
            return {
                'projects': projects,
                'languages': list(languages),
                'total_repos': len(repos),
                'summary': self._generate_github_summary(projects, languages)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_portfolio(self):
        """Analyse le portfolio"""
        try:
            response = requests.get(self.portfolio_url, timeout=10)
            if response.status_code != 200:
                return {"error": "Portfolio not accessible"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire texte principal
            text = soup.get_text()
            
            # Chercher compétences et projets
            skills = self._extract_skills(text)
            projects = self._extract_projects(soup)
            
            return {
                'skills': skills,
                'projects': projects,
                'summary': f"Portfolio avec {len(projects)} projets et expertise en {', '.join(skills[:5])}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_full_profile(self):
        """Analyse complète"""
        github_data = self.analyze_github()
        portfolio_data = self.analyze_portfolio()
        
        return {
            'github': github_data,
            'portfolio': portfolio_data,
            'combined_summary': self._combine_summaries(github_data, portfolio_data)
        }
    
    def _generate_github_summary(self, projects, languages):
        """Résumé GitHub"""
        top_projects = sorted(projects, key=lambda x: x['stars'], reverse=True)[:3]
        project_names = [p['name'] for p in top_projects]
        
        return f"Développeur actif avec {len(projects)} projets dont {', '.join(project_names)}. Expertise: {', '.join(list(languages)[:5])}"
    
    def _extract_skills(self, text):
        """Extraire compétences du texte"""
        common_skills = ['Python', 'JavaScript', 'React', 'Node', 'SQL', 'MongoDB', 
                        'Docker', 'AWS', 'Machine Learning', 'Data Science', 'TensorFlow',
                        'PyTorch', 'Spark', 'Kubernetes', 'FastAPI', 'Django', 'Flask']
        
        found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
        return found_skills
    
    def _extract_projects(self, soup):
        """Extraire projets du portfolio"""
        projects = []
        
        # Chercher sections projet
        for section in soup.find_all(['section', 'div'], class_=lambda x: x and 'project' in str(x).lower()):
            title = section.find(['h2', 'h3', 'h4'])
            if title:
                projects.append(title.get_text().strip())
        
        return projects[:5]
    
    def _combine_summaries(self, github_data, portfolio_data):
        """Combiner les analyses"""
        summary = []
        
        if 'summary' in github_data:
            summary.append(github_data['summary'])
        
        if 'summary' in portfolio_data:
            summary.append(portfolio_data['summary'])
        
        return " ".join(summary)
