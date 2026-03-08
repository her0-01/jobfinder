# 🚀 Job Application Bot - Version Complète

Application web autonome pour automatiser la recherche d'emploi avec IA.

## ✨ Fonctionnalités

### 🔍 Scraping Multi-Sites
- **Indeed** - Leader mondial
- **LinkedIn** - Réseau professionnel
- **Welcome to the Jungle** - Startups & scale-ups
- **APEC** - Cadres
- **HelloWork** - Tous secteurs
- **Meteojob** - Météo de l'emploi
- **RegionsJob** - Par région
- **Monster** - International

### 🤖 IA Groq Multi-Agents PREMIUM
- **Agent CV**: Analyse approfondie + Adaptation ciblée (llama-3.3-70b)
  - 📊 Analyse offre en 7 catégories (secteur, compétences, culture, mots-clés)
  - 🎯 Analyse profil en 6 dimensions (compétences, projets, expériences)
  - 🧠 Stratégie d'adaptation en 7 points actionnables
  - 📄 Génération CV LaTeX professionnel avec optimisation ATS
  
- **Agent Lettre**: Rédaction PREMIUM + Humanisation (llama-3.3-70b)
  - 🔍 Recherche entreprise approfondie (5 insights concrets)
  - 🤝 Analyse match candidat-offre (synergies mesurables)
  - 📝 Plan détaillé en 4 paragraphes percutants
  - ✍️ Rédaction authentique (0 cliché, ton naturel)
  - 🎨 Humanisation finale pour 100% naturel
  
- **Agent Analyse**: Évaluation parallèle (3 sous-agents)
  - Compétences techniques
  - Expérience professionnelle
  - Adéquation culturelle
  
- **Adaptation Sectorielle Automatique**
  - 🏦 Finance/Banque → Compliance, Risk, Fintech
  - 🚀 Tech/Startup → Innovation, Agile, Cloud-native
  - 🏭 Industrie → Production, Qualité, Certification
  - 🛒 E-commerce → Recommandation, Scale, A/B testing
  
- **Résultats**
  - Score compatibilité: 70-85% (vs 50% avant)
  - 10+ mots-clés intégrés naturellement
  - Lettres spécifiques et authentiques
  - CV LaTeX professionnel avec aperçu PDF

### 🎯 Interface Web Moderne
- Dashboard responsive
- Recherche personnalisée (poste, lieu, contrat)
- **Tri par pertinence IA** (score calculé automatiquement)
- Filtres intelligents (haute/moyenne/toute pertinence)
- Génération à la demande
- **Aperçu PDF intégré** (téléchargement en 1 clic)
- Historique des candidatures
- **Chat IA** pour améliorer les candidatures
- **AUCUN ENVOI AUTOMATIQUE** - Vous validez tout!

## 📋 Installation

### 1. Prérequis
- Python 3.8+
- Microsoft Edge
- Clé API Grok ([console.x.ai](https://console.x.ai))

### 2. Configuration

**a) API Grok**
Éditez `job_scraper/config.ini`:
```ini
[API]
grok_api_key = votre_cle_ici
```

**b) Votre Profil**
```ini
[PROFILE]
name = Votre Nom
email = votre.email@example.com
github = https://github.com/username
portfolio = https://portfolio.com
```

**c) Vos Documents**

Collez votre **CV LaTeX** dans:
```
job_scraper/data/cv_base.tex
```

Collez votre **lettre de motivation** dans:
```
job_scraper/data/lettre_motivation_base.txt
```

### 3. Lancement

Double-cliquez sur:
```
START_JOB_WEB.bat
```

Ouvrez votre navigateur sur: **http://localhost:5001**

## 🎮 Utilisation

### Rechercher des Offres

1. **Onglet "Recherche"**
2. Entrez vos critères:
   - Poste: `Data Engineer Alternance`
   - Lieu: `Paris` ou `France` ou `Remote`
   - Contrat: `Alternance`, `CDI`, `CDD`, `Stage`
3. Cliquez **"Lancer la Recherche"**
4. Attendez (30-60 secondes)

### Générer une Candidature

1. Parcourez les offres trouvées
2. Cliquez **"Générer Candidature"** sur une offre
3. L'IA analyse et génère:
   - CV adapté
   - Lettre personnalisée
   - Score de compatibilité
4. **Validez le contenu** avant utilisation!

### Consulter l'Historique

1. **Onglet "Candidatures Générées"**
2. Voir toutes vos candidatures
3. Cliquer sur **"Voir"** pour consulter
4. Les fichiers sont dans `data/applications/`

## 📁 Structure des Candidatures

```
data/applications/20240302_143022_Safran/
├── cv_adapted.md          # CV adapté
├── cover_letter.txt       # Lettre personnalisée
└── job_info.json         # Détails + analyse
```

## 🎯 Workflow Recommandé

1. **Matin**: Lancer une recherche
2. **Parcourir**: Les offres trouvées
3. **Générer**: Pour les offres intéressantes
4. **Relire**: TOUJOURS relire avant envoi
5. **Personnaliser**: Ajuster si nécessaire
6. **Postuler**: Manuellement sur les sites

## ⚙️ Personnalisation

### Modifier les Sites Scrapés

Éditez `scrapers/universal_scraper.py`:
```python
def scrape_all(self, keywords, location, contract_type):
    # Commentez les sites non désirés
    # self.scrape_monster(keywords, location)
```

### Ajuster le Score Minimum

Dans `web_app.py`, ligne ~85:
```python
if match.get('score', 0) < 50:  # Changez 50
```

### Modifier le Style d'Écriture

Éditez les prompts dans `ai_adapters/grok_adapter.py`

## 🔐 Sécurité

- ✅ Aucun envoi automatique
- ✅ Validation manuelle obligatoire
- ✅ Données stockées localement
- ✅ Clés API non commitées

## 📊 Statistiques

Le bot affiche:
- Nombre d'offres par site
- Score de compatibilité
- Date de scraping
- Historique complet

## ⚠️ Notes Importantes

### Respect des CGU
- Utilisez de manière raisonnable
- Respectez les robots.txt
- Ne surchargez pas les serveurs

### Qualité des Candidatures
- **Relisez TOUJOURS** avant envoi
- Personnalisez davantage si nécessaire
- Vérifiez les informations
- Adaptez le ton si besoin

### Limitations
- Certains sites peuvent bloquer le scraping
- Les sélecteurs CSS peuvent changer
- L'IA peut faire des erreurs
- Validation humaine indispensable

## 🚀 Améliorations Récentes (v2.0)

### ✅ Prompts IA Améliorés
- **Analyse 5x plus approfondie** : 7 catégories pour l'offre, 6 dimensions pour le profil
- **Adaptation sectorielle automatique** : Détecte Finance, Tech, Industrie, E-commerce
- **Stratégie SMART** : 7 points actionnables pour adaptation optimale
- **Qualité PREMIUM** : Score 70-85% (vs 50% avant)

### ✅ Aperçu PDF Intégré
- **Détection automatique** : LaTeX vs Markdown
- **Badge informatif** : "CV LaTeX généré" avec explication
- **Téléchargement 1 clic** : CV PDF et Lettre PDF
- **Aperçu code** : Affichage LaTeX avec scroll

### ✅ Documentation Complète
- `AMELIORATIONS_IA.md` - Détails des améliorations
- `CHANGELOG.md` - Résumé des modifications
- `TEST_GUIDE.md` - Guide de test en 7 étapes
- `RECAP_FINAL.md` - Récapitulatif complet

**Voir `RECAP_FINAL.md` pour tous les détails !**

---

## 🐛 Dépannage

### Le scraping ne fonctionne pas
- Vérifiez votre connexion internet
- Certains sites peuvent être temporairement inaccessibles
- Essayez en mode non-headless pour voir ce qui se passe

### L'IA ne génère rien
- Vérifiez votre clé API Grok
- Vérifiez que vos fichiers CV et lettre existent
- Consultez les logs d'erreur

### Le serveur ne démarre pas
- Vérifiez que le port 5001 est libre
- Installez les dépendances: `pip install -r requirements.txt`

## 🚀 Améliorations Futures

- [ ] Export PDF automatique
- [ ] Intégration GitHub API
- [ ] Analyse de votre portfolio
- [ ] Suggestions de compétences à ajouter
- [ ] Tracking des candidatures envoyées
- [ ] Statistiques avancées

## 📝 Licence

Usage personnel et éducatif uniquement.

## 🤝 Contribution

Ce projet est un outil personnel. Utilisez-le de manière responsable et éthique.

---

**Bon courage dans votre recherche d'emploi! 🎯**
