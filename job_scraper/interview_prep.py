from ai_adapters.groq_multi_agent import GroqMultiAgentAdapter

class InterviewPrep:
    """Préparation intelligente aux entretiens avec IA"""
    
    def __init__(self, api_key):
        self.ai = GroqMultiAgentAdapter(api_key)
    
    def generate_interview_questions(self, job_title, company, job_description):
        """Générer questions d'entretien probables"""
        
        prompt = f"""Tu es un recruteur expert. Génère 10 questions d'entretien probables pour ce poste :

POSTE : {job_title}
ENTREPRISE : {company}
DESCRIPTION : {job_description[:500]}

Génère :
1. 3 questions techniques spécifiques au poste
2. 3 questions comportementales
3. 2 questions sur la motivation
4. 2 questions sur l'entreprise

Format : Question simple, une par ligne."""

        questions = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un expert en recrutement. Génère des questions d'entretien pertinentes.",
            prompt=prompt,
            max_tokens=1000
        )
        
        return questions.split('\n')
    
    def generate_answer_tips(self, question, user_profile, job_description):
        """Générer des conseils pour répondre à une question"""
        
        prompt = f"""Aide le candidat à répondre à cette question d'entretien :

QUESTION : {question}

PROFIL CANDIDAT : {user_profile}
POSTE VISÉ : {job_description[:300]}

Donne :
1. Structure de réponse (méthode STAR si applicable)
2. Points clés à mentionner
3. Exemple de réponse (2-3 phrases)
4. Pièges à éviter"""

        tips = self.ai._call_agent(
            model=self.ai.models['creative'],
            system="Tu es un coach en entretien d'embauche. Aide le candidat à briller.",
            prompt=prompt,
            max_tokens=500
        )
        
        return tips
    
    def analyze_company(self, company_name):
        """Analyser l'entreprise pour préparer l'entretien"""
        
        prompt = f"""Analyse l'entreprise {company_name} pour préparer un entretien :

1. Secteur d'activité et position sur le marché
2. Valeurs et culture d'entreprise
3. Actualités récentes importantes
4. Questions intelligentes à poser au recruteur
5. Points de vigilance

Sois concis et factuel."""

        analysis = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un expert en recherche d'entreprise.",
            prompt=prompt,
            max_tokens=800
        )
        
        return analysis
    
    def generate_questions_to_ask(self, job_title, company):
        """Générer questions à poser au recruteur"""
        
        prompt = f"""Génère 8 questions intelligentes à poser au recruteur pour le poste de {job_title} chez {company}.

Catégories :
- 2 questions sur le poste et les missions
- 2 questions sur l'équipe et l'environnement
- 2 questions sur l'évolution et la formation
- 2 questions sur l'entreprise et sa vision

Format : Question directe, une par ligne."""

        questions = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un coach carrière. Génère des questions pertinentes.",
            prompt=prompt,
            max_tokens=500
        )
        
        return questions.split('\n')
    
    def simulate_interview(self, job_title, company, user_answers):
        """Simuler un entretien et donner du feedback"""
        
        prompt = f"""Tu es un recruteur pour le poste de {job_title} chez {company}.

Le candidat a répondu aux questions. Analyse ses réponses et donne un feedback constructif :

RÉPONSES DU CANDIDAT :
{user_answers}

Évalue :
1. Clarté et structure des réponses (note /10)
2. Pertinence par rapport au poste (note /10)
3. Motivation et enthousiasme (note /10)
4. Points forts
5. Points à améliorer
6. Conseils concrets

Sois bienveillant mais honnête."""

        feedback = self.ai._call_agent(
            model=self.ai.models['balanced'],
            system="Tu es un recruteur bienveillant qui donne du feedback constructif.",
            prompt=prompt,
            max_tokens=800
        )
        
        return feedback
    
    def generate_elevator_pitch(self, user_profile, job_title):
        """Générer un pitch de 30 secondes"""
        
        prompt = f"""Génère un elevator pitch de 30 secondes (environ 80 mots) pour ce candidat :

PROFIL : {user_profile}
POSTE VISÉ : {job_title}

Le pitch doit :
- Commencer par qui tu es
- Mentionner ton expérience/formation clé
- Expliquer ce que tu cherches
- Finir par ta valeur ajoutée

Ton naturel et conversationnel."""

        pitch = self.ai._call_agent(
            model=self.ai.models['creative'],
            system="Tu es un coach en communication. Génère un pitch percutant.",
            prompt=prompt,
            max_tokens=200
        )
        
        return pitch
