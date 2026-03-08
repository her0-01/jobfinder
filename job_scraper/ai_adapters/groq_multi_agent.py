import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class GroqMultiAgentAdapter:
    """Système multi-agents avec Groq pour optimiser les candidatures"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Modèles disponibles sur Groq
        self.models = {
            "fast": "llama-3.1-8b-instant",      # Rapide, tâches simples
            "balanced": "llama-3.3-70b-versatile", # Équilibré
            "creative": "llama-3.3-70b-versatile", # Créatif
            "precise": "llama-3.3-70b-versatile"   # Précis
        }
    
    def generate_cv_adaptation(self, base_cv, job_description, profile, background):
        """Agent CV: Adaptation PREMIUM avec analyse complète en batch"""
        print("  🤖 Agent CV: Analyse PREMIUM en cours...")
        
        # BATCH 1: Analyse approfondie de l'offre
        print("    [1/4] Analyse de l'offre...")
        job_analysis = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un expert en analyse d'offres d'emploi. Tu extrais PRÉCISÉMENT les besoins réels de l'entreprise.",
            prompt=f"""Analyse APPROFONDIE de cette offre:

DESCRIPTION COMPLÈTE:
{job_description[:2500]}

EXTRAIS avec PRÉCISION:

1. SECTEUR & CONTEXTE:
   - Secteur d'activité (Finance, Tech, Industrie, etc.)
   - Type d'entreprise (Startup, PME, Grand groupe, etc.)
   - Enjeux métier spécifiques

2. COMPÉTENCES TECHNIQUES (par priorité):
   - Langages/frameworks OBLIGATOIRES
   - Technologies SOUHAITÉES
   - Outils/plateformes mentionnés

3. COMPÉTENCES MÉTIER:
   - Domaines d'expertise (ML, Data Engineering, BI, etc.)
   - Méthodologies (Agile, DevOps, etc.)
   - Certifications ou connaissances spécifiques

4. SOFT SKILLS & CULTURE:
   - Qualités humaines recherchées
   - Mode de travail (équipe, autonomie, etc.)
   - Valeurs de l'entreprise

5. MOTS-CLÉS STRATÉGIQUES:
   - Termes techniques à intégrer absolument
   - Verbes d'action utilisés
   - Expressions spécifiques au secteur

6. NIVEAU & CONTEXTE:
   - Expérience attendue
   - Type de missions (POC, production, R&D, etc.)
   - Environnement de travail

Format JSON structuré:
{{
  "sector": {{"industry": "", "company_type": "", "challenges": []}},
  "tech_skills": {{"required": [], "preferred": [], "tools": []}},
  "business_skills": {{"domains": [], "methodologies": [], "certifications": []}},
  "soft_skills": [],
  "culture": {{"values": [], "work_style": ""}},
  "keywords": {{"technical": [], "action_verbs": [], "sector_specific": []}},
  "level": {{"experience": "", "mission_type": "", "environment": ""}}
}}""",
            max_tokens=800
        )
        
        # BATCH 2: Analyse du profil candidat
        print("    [2/4] Analyse du profil candidat...")
        candidate_analysis = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un expert en valorisation de profils. Tu identifies les ATOUTS CONCRETS et MESURABLES.",
            prompt=f"""Analyse COMPLÈTE de ce profil candidat:

CV COMPLET:
{base_cv[:2500]}

CONTEXTE FORMATION:
- Formation actuelle: {background.get('formation_actuelle', 'N/A')}
- Formation visée: {background.get('formation_visee', 'N/A')}
- Spécialisation: {background.get('specialisation', 'N/A')}

COMPÉTENCES DÉCLARÉES:
{background.get('competences_cles', 'N/A')}

PROJETS RÉALISÉS:
{background.get('projets_majeurs', 'N/A')}

MOTIVATION & OBJECTIFS:
- Motivation: {background.get('motivation', 'N/A')[:300]}
- Objectifs: {background.get('objectifs', 'N/A')[:300]}

PROFIL EN LIGNE:
- GitHub: {profile.get('github', 'N/A')}
- Portfolio: {profile.get('portfolio', 'N/A')}
- Analyse: {profile.get('analysis', 'N/A')[:400]}

IDENTIFIE avec PRÉCISION:

1. COMPÉTENCES TECHNIQUES (avec niveau):
   - Langages maîtrisés
   - Frameworks/librairies utilisés
   - Outils et plateformes

2. EXPÉRIENCES PROFESSIONNELLES:
   - Entreprises et contextes
   - Missions réalisées avec RÉSULTATS
   - Technologies utilisées en production

3. PROJETS MARQUANTS:
   - Titre et objectif
   - Stack technique
   - Résultats/impact mesurable

4. POINTS FORTS DIFFÉRENCIANTS:
   - Ce qui rend ce profil unique
   - Combinaisons de compétences rares
   - Réalisations concrètes

5. SOFT SKILLS DÉMONTRÉS:
   - Travail en équipe (preuves)
   - Autonomie (exemples)
   - Autres qualités avec contexte

6. AXES DE DÉVELOPPEMENT:
   - Compétences en cours d'acquisition
   - Domaines d'intérêt pour progression

Format JSON détaillé:
{{
  "technical_skills": {{"languages": [], "frameworks": [], "tools": [], "platforms": []}},
  "experiences": [{{"company": "", "role": "", "achievements": [], "tech_stack": []}}],
  "projects": [{{"name": "", "description": "", "tech": [], "results": ""}}],
  "differentiators": [],
  "soft_skills": [{{"skill": "", "proof": ""}}],
  "growth_areas": []
}}""",
            max_tokens=900
        )
        
        # BATCH 3: Stratégie d'adaptation SMART
        print("    [3/4] Création de la stratégie SMART...")
        strategy = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un stratège en recrutement. Tu crées des stratégies de matching PRÉCISES et ACTIONNABLES.",
            prompt=f"""Crée une STRATÉGIE D'ADAPTATION PREMIUM:

ANALYSE OFFRE:
{job_analysis}

ANALYSE CANDIDAT:
{candidate_analysis}

CRÉE UNE STRATÉGIE DÉTAILLÉE:

1. MATCHING COMPÉTENCES:
   - Quelles compétences candidat correspondent EXACTEMENT aux besoins
   - Comment reformuler pour matcher les mots-clés de l'offre
   - Compétences à mettre en AVANT (top 5)
   - Compétences à minimiser ou retirer

2. VALORISATION EXPÉRIENCES:
   - Quelle expérience mettre en premier
   - Comment réécrire les missions pour coller à l'offre
   - Résultats chiffrés à ajouter
   - Verbes d'action à utiliser

3. SÉLECTION & DÉTAIL PROJETS:
   - Top 3 projets les plus pertinents
   - Angle de présentation pour chaque projet
   - Technologies à mentionner explicitement
   - Résultats/impact à mettre en avant

4. INTÉGRATION MOTS-CLÉS:
   - Liste des 10 mots-clés CRITIQUES à intégrer
   - Où les placer naturellement (sections)
   - Expressions sectorielles à utiliser

5. STRUCTURE & ORDRE:
   - Ordre optimal des sections
   - Ce qui doit être en haut (visible immédiatement)
   - Ce qui peut être réduit ou déplacé

6. ANGLE DE PRÉSENTATION:
   - Positionnement global (ex: "Expert Data avec focus BI")
   - Ton à adopter (technique, business, innovant, etc.)
   - Message clé à faire passer

7. ADAPTATIONS SPÉCIFIQUES AU SECTEUR:
   - Terminologie sectorielle à utiliser
   - Standards du secteur à respecter
   - Éléments culturels à intégrer

Format: Texte structuré et ACTIONNABLE.""",
            max_tokens=800
        )
        
        # BATCH 4: Génération du CV adapté PREMIUM en LaTeX
        print("    [4/4] Génération du CV PREMIUM LaTeX...")
        adapted_cv = self._call_agent(
            model=self.models["creative"],
            system="Tu es un expert en rédaction de CV LaTeX. Tu MODIFIES UNIQUEMENT le contenu textuel, JAMAIS la structure LaTeX.",
            prompt=f"""ADAPTE ce CV LaTeX pour cette offre en modifiant UNIQUEMENT le contenu textuel.

STRATÉGIE D'ADAPTATION:
{strategy}

CV DE BASE (LaTeX) - NE PAS TOUCHER LA STRUCTURE:
{base_cv}

CONTEXTE CANDIDAT:
- Formation: {background.get('formation_actuelle', '')} → {background.get('formation_visee', '')}
- Spécialisation: {background.get('specialisation', '')}
- Compétences clés: {background.get('competences_cles', '')[:300]}
- Projets majeurs: {background.get('projets_majeurs', '')[:300]}

RÈGLES ABSOLUES:

1. STRUCTURE À NE JAMAIS MODIFIER:
   ✅ GARDE: \\documentclass, \\usepackage, \\definecolor, \\geometry, \\renewcommand
   ✅ GARDE: \\begin{{tikzpicture}}, \\draw, \\fill, \\node, \\timelineentry
   ✅ GARDE: \\begin{{tabular}}, \\begin{{multicols}}, \\begin{{itemize}}
   ✅ GARDE: Toutes les couleurs (newBleuTech, accentTeal, safranBlue, iutVannesBlue)
   ✅ GARDE: Tous les \\tech{{}}, \\textcolor, \\textbf, \\footnotesize
   ✅ GARDE: Les coordonnées tikz (-0.2,0), (-2.9), (-5.4), (-7.8)

2. CE QUI PEUT ÊTRE MODIFIÉ (CONTENU UNIQUEMENT):
   ✅ Section "Profil": Adapte le texte pour matcher l'offre
   ✅ Expériences: Reformule les descriptions des bullet points
   ✅ Compétences: Réorganise l'ordre selon la stratégie (garde les \\tech{{}})
   ✅ Projets (si section existe): Détaille ceux pertinents pour l'offre

3. EXEMPLE DE MODIFICATION CORRECTE:
   AVANT: \\item \\tech{{Reporting}}: Développement d'outils BI
   APRÈS: \\item \\tech{{Reporting}}: Développement d'outils BI métiers avec Power BI et Tableau pour optimiser la prise de décision

4. INTERDICTIONS STRICTES:
   ❌ NE PAS supprimer de sections
   ❌ NE PAS changer les couleurs ou commandes LaTeX
   ❌ NE PAS modifier la structure tikzpicture
   ❌ NE PAS toucher au préambule (avant \\begin{{document}})
   ❌ NE PAS inventer d'expériences ou compétences

5. ADAPTATION INTELLIGENTE:
   - Intègre les mots-clés de l'offre NATURELLEMENT dans les descriptions
   - Mets en avant les compétences pertinentes en les détaillant
   - Reformule pour matcher le vocabulaire de l'offre
   - Reste 100% AUTHENTIQUE

GÉNÈRE LE CV LATEX COMPLET avec UNIQUEMENT le contenu textuel adapté:""",
            max_tokens=3500
        )
        
        print("    ✅ CV PREMIUM généré !")
        return adapted_cv
    
    def generate_cover_letter_from_base(self, job_info, profile, cv_content, base_letter, background, output_format='text'):
        """Agent Lettre: Génération PREMIUM en batch multi-agents"""
        print("  ✉️ Agent Lettre: Génération PREMIUM en cours...")
        
        # BATCH 1: Recherche approfondie sur l'entreprise
        print("    [1/5] Recherche entreprise...")
        company_research = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un expert en recherche d'entreprises et analyse sectorielle. Tu fournis des insights CONCRETS et ACTIONNABLES.",
            prompt=f"""Analyse APPROFONDIE de cette entreprise et ce poste:

ENTREPRISE: {job_info['company']}
POSTE: {job_info['title']}

DESCRIPTION COMPLÈTE:
{job_info.get('description', '')[:2000]}

FOURNIS:

1. SECTEUR & POSITIONNEMENT:
   - Secteur d'activité précis
   - Position sur le marché (leader, challenger, niche, etc.)
   - Spécificités métier

2. ENJEUX DU POSTE:
   - Pourquoi ce recrutement (croissance, transformation, remplacement, etc.)
   - Challenges concrets du poste
   - Impact attendu du candidat

3. CULTURE & VALEURS:
   - Valeurs détectées dans l'offre
   - Style de management probable
   - Environnement de travail

4. POINTS D'ACCROCHE:
   - 3 éléments spécifiques à mentionner pour montrer la recherche
   - Projets/initiatives de l'entreprise à valoriser
   - Aspects attractifs pour un candidat data

5. ANGLE D'APPROCHE RECOMMANDÉ:
   - Ton à adopter (technique, business, innovant, etc.)
   - Ce qui va séduire cette entreprise
   - Erreurs à éviter

Format structuré et actionnable.""",
            max_tokens=700
        )
        
        # BATCH 2: Analyse du match candidat-offre
        print("    [2/5] Analyse du match...")
        match_analysis = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un expert en matching candidat-offre. Tu identifies les SYNERGIES CONCRÈTES et MESURABLES.",
            prompt=f"""Analyse APPROFONDIE du match entre ce candidat et cette offre:

CANDIDAT:
- Formation: {background.get('formation_actuelle', '')} → {background.get('formation_visee', '')}
- Spécialisation: {background.get('specialisation', '')}
- Compétences: {background.get('competences_cles', '')[:400]}
- Projets: {background.get('projets_majeurs', '')[:400]}
- Motivation: {background.get('motivation', '')[:300]}
- Objectifs: {background.get('objectifs', '')[:300]}

EXTRAITS CV:
{cv_content[:800]}

OFFRE:
Poste: {job_info['title']}
Entreprise: {job_info['company']}
Description: {job_info.get('description', '')[:1000]}

IDENTIFIE:

1. TOP 3 POINTS FORTS:
   - Compétence/expérience candidat qui matche PARFAITEMENT
   - Pourquoi c'est pertinent pour CE poste
   - Comment le formuler dans la lettre

2. PROJETS/EXPÉRIENCES À MENTIONNER:
   - 2 projets les plus pertinents
   - Angle de présentation pour chaque
   - Résultats concrets à mettre en avant
   - Lien avec les besoins de l'offre

3. COMPÉTENCES CLÉS:
   - 5 compétences techniques à mentionner explicitement
   - 3 soft skills à démontrer avec exemples
   - Terminologie exacte à utiliser

4. VALEUR AJOUTÉE UNIQUE:
   - Ce qui différencie ce candidat
   - Combinaison de compétences rare
   - Atout spécifique pour cette entreprise

5. ANGLE DE MOTIVATION AUTHENTIQUE:
   - Pourquoi CE poste (pas un autre)
   - Pourquoi CETTE entreprise (spécifique)
   - Lien avec objectifs de carrière
   - Enthousiasme réel et justifié

Format: Structuré et ACTIONNABLE pour rédaction.""",
            max_tokens=700
        )
        
        # BATCH 3: Structure et plan de la lettre
        print("    [3/5] Création du plan...")
        letter_plan = self._call_agent(
            model=self.models["balanced"],
            system="Tu es un expert en structure de lettres de motivation. Tu crées des plans PERCUTANTS et ENGAGEANTS.",
            prompt=f"""Crée un PLAN DÉTAILLÉ de lettre de motivation:

RECHERCHE ENTREPRISE:
{company_research}

ANALYSE MATCH:
{match_analysis}

STYLE DE BASE (à conserver):
{base_letter[:500]}

CRÉE UN PLAN EN 4 PARAGRAPHES:

§ PARAGRAPHE 1 - ACCROCHE (3-4 phrases):
   - Phrase d'ouverture percutante
   - Pourquoi CETTE entreprise spécifiquement (insight concret)
   - Pourquoi CE poste (lien avec parcours)
   - Transition vers compétences
   → Points clés à aborder:
   → Ton à adopter:
   → Mots-clés à intégrer:

§ PARAGRAPHE 2 - COMPÉTENCES & PROJETS (4-5 phrases):
   - Compétence technique #1 avec exemple concret
   - Projet pertinent avec résultat mesurable
   - Compétence technique #2 avec contexte
   - Lien avec besoins de l'offre
   → Projets à mentionner:
   → Résultats à mettre en avant:
   → Technologies à citer:

§ PARAGRAPHE 3 - VALEUR AJOUTÉE & MOTIVATION (4-5 phrases):
   - Ce qui rend le candidat unique
   - Soft skills démontrés (avec preuve)
   - Motivation authentique et spécifique
   - Vision de la contribution à l'entreprise
   → Différenciateurs à mettre en avant:
   → Valeurs à aligner:
   → Impact attendu:

§ PARAGRAPHE 4 - CONCLUSION DYNAMIQUE (2-3 phrases):
   - Résumé de la valeur apportée
   - Enthousiasme pour la suite
   - Call-to-action (disponibilité pour échange)
   → Message final:
   → Ton de clôture:

Format: Plan DÉTAILLÉ et ACTIONNABLE.""",
            max_tokens=800
        )
        
        # BATCH 4: Rédaction de la lettre PREMIUM
        print("    [4/5] Rédaction de la lettre...")
        
        # Extraire infos du profil
        name = profile.get('name', 'Candidat')
        email = profile.get('email', '')
        phone = profile.get('phone', '')
        address = base_letter.split('\n')[1] if len(base_letter.split('\n')) > 1 else ''
        
        letter = self._call_agent(
            model=self.models["creative"],
            system="Tu es un expert en lettres de motivation premium. Tu écris des lettres AUTHENTIQUES, ENGAGEANTES et HUMAINES qui se démarquent.",
            prompt=f"""Rédige une lettre de motivation PREMIUM selon ce plan:

PLAN:
{letter_plan}

CONTEXTE:
- Candidat: {name}
- Email: {email}
- Téléphone: {phone}
- Adresse: {address}
- Poste: {job_info['title']}
- Entreprise: {job_info['company']}

TON À SUIVRE:
{base_letter[:500]}

RÈGLES STRICTES:
1. COMMENCE par l'en-tête: {name}\n{address}\n{phone}\n{email}
2. ÉCRIS COMME UN HUMAIN - "je", "mon", "mes"
3. Sois NATUREL et AUTHENTIQUE - pas de clichés
4. Utilise des EXEMPLES CONCRETS du match analysis
5. Montre de l'ENTHOUSIASME réel et spécifique
6. Intègre les insights entreprise NATURELLEMENT
7. Phrases courtes et percutantes
8. 300-350 mots (4 paragraphes)
9. Termine par formule de politesse
10. AUCUN mot générique ("dynamique", "motivé", "passionné")
11. Objet: {job_info['title']} - Alternance

Lettre PREMIUM:""",
            max_tokens=1000
        )
        
        # BATCH 5: Humanisation et polish final
        print("    [5/5] Humanisation finale...")
        final_letter = self._call_agent(
            model=self.models["creative"],
            system="Tu es un expert en écriture naturelle. Tu perfectionnes les textes pour qu'ils sonnent 100% humains.",
            prompt=f"""Perfectionne cette lettre:

{letter}

Améliorations:
1. Fluidité des transitions
2. Varie la longueur des phrases
3. Ajoute des nuances humaines
4. Vérifie que ça sonne naturel
5. Garde le contenu exact
6. Maximum 350 mots

Lettre finale:""",
            max_tokens=1000
        )
        
        print("    ✅ Lettre PREMIUM générée !")
        return final_letter
    
    def analyze_job_match(self, cv_content, job_description):
        """Agent Analyse: Évaluation parallèle"""
        print("  📊 Agent Analyse: Évaluation...")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 3 agents en parallèle pour analyse complète
            futures = {
                executor.submit(
                    self._analyze_skills_match,
                    cv_content, job_description
                ): "skills",
                executor.submit(
                    self._analyze_experience_match,
                    cv_content, job_description
                ): "experience",
                executor.submit(
                    self._analyze_culture_match,
                    cv_content, job_description
                ): "culture"
            }
            
            results = {}
            for future in as_completed(futures):
                key = futures[future]
                results[key] = future.result()
        
        # Calcul du score global
        score = (
            results["skills"]["score"] * 0.5 +
            results["experience"]["score"] * 0.3 +
            results["culture"]["score"] * 0.2
        )
        
        return {
            "score": int(score),
            "strengths": results["skills"]["strengths"] + results["experience"]["strengths"],
            "gaps": results["skills"]["gaps"] + results["experience"]["gaps"],
            "recommendations": [
                "Mets en avant tes compétences en " + ", ".join(results["skills"]["strengths"][:2]),
                "Développe ton expérience en " + ", ".join(results["skills"]["gaps"][:2]) if results["skills"]["gaps"] else "Continue sur cette voie"
            ]
        }
    
    def _analyze_skills_match(self, cv, job):
        """Sous-agent: Compétences"""
        response = self._call_agent(
            model=self.models["fast"],
            system="Tu es un expert en compétences techniques.",
            prompt=f"""Compare les compétences:

CV: {cv[:800]}
OFFRE: {job[:800]}

Réponds en JSON:
{{"score": 75, "strengths": ["Python", "ML"], "gaps": ["Docker"]}}""",
            max_tokens=200
        )
        try:
            return json.loads(response)
        except:
            return {"score": 50, "strengths": [], "gaps": []}
    
    def _analyze_experience_match(self, cv, job):
        """Sous-agent: Expérience"""
        response = self._call_agent(
            model=self.models["fast"],
            system="Tu es un expert en parcours professionnels.",
            prompt=f"""Évalue l'expérience:

CV: {cv[:800]}
OFFRE: {job[:800]}

Réponds en JSON:
{{"score": 80, "strengths": ["Projets data"], "gaps": ["Production"]}}""",
            max_tokens=200
        )
        try:
            return json.loads(response)
        except:
            return {"score": 50, "strengths": [], "gaps": []}
    
    def _analyze_culture_match(self, cv, job):
        """Sous-agent: Culture"""
        response = self._call_agent(
            model=self.models["fast"],
            system="Tu es un expert en culture d'entreprise.",
            prompt=f"""Évalue l'adéquation culturelle:

CV: {cv[:800]}
OFFRE: {job[:800]}

Réponds en JSON:
{{"score": 70, "strengths": ["Innovation"], "gaps": []}}""",
            max_tokens=200
        )
        try:
            return json.loads(response)
        except:
            return {"score": 50, "strengths": [], "gaps": []}
    
    def _call_agent(self, model, system, prompt, max_tokens=1000):
        """Appel API Groq pour un agent avec timeout et retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=45
                )
                
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                elif response.status_code == 429:
                    wait_time = 10 * (attempt + 1)
                    print(f"  ⏳ Rate limit - Attente {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 400:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"  ⚠️ Erreur 400: {error_msg[:100]}")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    return f"Erreur API 400: {error_msg[:200]}"
                else:
                    return f"Erreur API: {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print(f"  ⏱️ Timeout - Retry {attempt + 1}/{max_retries}...")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return "Erreur: Timeout API"
            except Exception as e:
                print(f"  ❌ Erreur: {str(e)[:100]}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return f"Erreur: {str(e)[:200]}"
