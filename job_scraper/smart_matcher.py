from ai_adapters.groq_multi_agent import GroqMultiAgentAdapter

class SmartMatcher:
    """Matching intelligent avec analyse des gaps de compétences"""
    
    def __init__(self, api_key):
        self.ai = GroqMultiAgentAdapter(api_key)
    
    def analyze_skill_gap(self, user_cv, job_description):
        """Analyser l'écart de compétences entre CV et offre"""
        
        prompt = f"""Analyse l'écart entre le profil du candidat et l'offre d'emploi.

CV CANDIDAT :
{user_cv[:1500]}

OFFRE D'EMPLOI :
{job_description[:1500]}

Fournis :
1. COMPÉTENCES MATCHING (✅) : Compétences que le candidat possède
2. COMPÉTENCES MANQUANTES (❌) : Compétences requises mais absentes
3. COMPÉTENCES À DÉVELOPPER (⚠️) : Compétences partielles à renforcer
4. SCORE GLOBAL : Note sur 100
5. RECOMMANDATIONS : 3 actions concrètes pour combler les gaps

Format clair et structuré."""

        analysis = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un expert RH qui analyse les profils candidats.",
            prompt=prompt,
            max_tokens=1000
        )
        
        return analysis
    
    def suggest_learning_path(self, missing_skills, job_title):
        """Suggérer un parcours d'apprentissage pour combler les gaps"""
        
        prompt = f"""Le candidat vise le poste de {job_title} mais il lui manque ces compétences :

{', '.join(missing_skills)}

Propose un plan d'apprentissage sur 3 mois :

1. SEMAINE 1-4 : Compétence prioritaire
   - Ressources (cours en ligne, livres, projets)
   - Temps estimé
   - Objectif mesurable

2. SEMAINE 5-8 : Deuxième compétence
   - Ressources
   - Temps estimé
   - Objectif mesurable

3. SEMAINE 9-12 : Troisième compétence
   - Ressources
   - Temps estimé
   - Objectif mesurable

Sois concret et actionnable."""

        plan = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un conseiller en formation professionnelle.",
            prompt=prompt,
            max_tokens=1000
        )
        
        return plan
    
    def find_alternative_jobs(self, user_cv, target_job):
        """Trouver des postes alternatifs adaptés au profil"""
        
        prompt = f"""Le candidat vise le poste de {target_job} mais n'a peut-être pas toutes les compétences.

PROFIL :
{user_cv[:1000]}

Suggère 5 postes alternatifs :
1. Plus accessibles (niveau inférieur)
2. Similaires (même niveau, autre angle)
3. Évolutifs (tremplin vers le poste visé)

Pour chaque poste :
- Nom du poste
- Pourquoi c'est adapté
- Compétences à développer pour évoluer

Format : Liste numérotée claire."""

        alternatives = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un conseiller en orientation professionnelle.",
            prompt=prompt,
            max_tokens=800
        )
        
        return alternatives
    
    def optimize_cv_for_job(self, user_cv, job_description):
        """Optimiser le CV pour une offre spécifique"""
        
        prompt = f"""Optimise ce CV pour cette offre d'emploi :

CV ACTUEL :
{user_cv[:1500]}

OFFRE :
{job_description[:1000]}

Recommandations :
1. MOTS-CLÉS À AJOUTER : Liste des mots-clés importants manquants
2. SECTIONS À RENFORCER : Quelles parties développer
3. EXPÉRIENCES À METTRE EN AVANT : Lesquelles prioriser
4. COMPÉTENCES À AJOUTER : Compétences pertinentes à mentionner
5. FORMAT : Suggestions de présentation

Sois spécifique et actionnable."""

        optimization = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un expert en optimisation de CV.",
            prompt=prompt,
            max_tokens=800
        )
        
        return optimization
    
    def calculate_realistic_salary(self, job_title, location, experience_years):
        """Estimer un salaire réaliste"""
        
        prompt = f"""Estime une fourchette de salaire réaliste pour :

POSTE : {job_title}
LOCALISATION : {location}
EXPÉRIENCE : {experience_years} ans

Fournis :
1. FOURCHETTE BASSE : Salaire minimum attendu
2. FOURCHETTE MÉDIANE : Salaire moyen du marché
3. FOURCHETTE HAUTE : Salaire pour profil senior/expert
4. FACTEURS INFLUENÇANT : Ce qui peut faire varier le salaire
5. CONSEIL NÉGOCIATION : Comment négocier efficacement

Base-toi sur le marché français actuel."""

        salary_info = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un expert en rémunération et marché de l'emploi.",
            prompt=prompt,
            max_tokens=500
        )
        
        return salary_info
    
    def detect_red_flags(self, job_description, company_name):
        """Détecter les red flags dans une offre"""
        
        prompt = f"""Analyse cette offre d'emploi pour détecter d'éventuels red flags :

ENTREPRISE : {company_name}
OFFRE :
{job_description[:1000]}

Vérifie :
1. 🚩 RED FLAGS : Signaux d'alerte (salaire non mentionné, "famille", horaires flous, etc.)
2. ⚠️ POINTS DE VIGILANCE : Éléments à clarifier en entretien
3. ✅ POINTS POSITIFS : Ce qui est rassurant
4. 💡 QUESTIONS À POSER : Questions pour lever les doutes

Sois honnête et protège le candidat."""

        analysis = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un conseiller qui protège les candidats des mauvaises opportunités.",
            prompt=prompt,
            max_tokens=600
        )
        
        return analysis

matcher = SmartMatcher
