# 🤖 NEXUS-OS - Système Multi-Agents IA

Plateforme complète d'automatisation de recherche d'emploi avec agents IA et scraping intelligent.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Responsive](https://img.shields.io/badge/Design-Responsive-success.svg)]()
[![Playwright](https://img.shields.io/badge/Scraping-Playwright-orange.svg)]()

## ✨ Fonctionnalités

### 💼 Job Application Bot
- 🔍 **Scraping intelligent** de 23 sites d'emploi (Indeed, LinkedIn, WTTJ, APEC + 15 sites carrières)
- 🤖 **IA Smart Query Builder** pour optimiser automatiquement les recherches
- 📊 **Progression en temps réel** avec compteur précis (X/23 sites)
- ⏹️ **Bouton STOP** pour arrêter et garder les résultats déjà trouvés
- 📜 **Historique automatique** avec sauvegarde des scores de pertinence
- 👥 **Multi-utilisateurs** avec authentification et base PostgreSQL
- 📝 **Adaptation automatique** de CV et lettres de motivation par IA
- 🎯 **Scoring de pertinence** des offres par IA (préservé dans l'historique)
- 🌐 **Interface web 100% responsive** (mobile/tablet/desktop)
- ✅ **Validation manuelle** (pas d'envoi automatique)
- 🚀 **Playwright + Selenium** avec fallback automatique

### 🧠 Multi-Agents IA
- 🔄 **Compatible** avec Groq, Gemini, OpenAI
- 🛡️ **Fallback automatique** entre providers
- 📊 **Analyse de profil** GitHub et Portfolio
- 💬 **Chat interactif** pour améliorer les candidatures
- 🔍 **Analyse complète** : Skill gap, Red flags, Salaire estimé
- 🎤 **Préparation entretien** : Questions probables, Elevator pitch
- 🚀 **Déployé sur Railway** avec PostgreSQL

## 🚀 Installation Rapide

### 1. Cloner le repo
```bash
git clone https://github.com/votre-username/nexus-os.git
cd nexus-os
```

### 2. Installer les dépendances
```bash
# Windows
INSTALL_DEPS.bat

# Linux/Mac
pip install -r job_scraper/requirements.txt
```

### 3. Configuration
```bash
cd job_scraper
cp config.ini.example config.ini
# Éditez config.ini avec vos clés API
```

**Obtenir une clé API gratuite :**
- **Groq** : https://console.groq.com (Recommandé - Gratuit et rapide)
- **Gemini** : https://ai.google.dev (Gratuit avec quotas)
- **OpenAI** : https://platform.openai.com (Payant)

### 4. Vos documents
Placez vos documents dans `job_scraper/data/` :
- `cv_base.tex` ou `cv_base.md` : Votre CV
- `lettre_motivation_base.txt` : Votre lettre type

### 5. Lancer l'application
```bash
# Windows
START_JOB_WEB.bat

# Linux/Mac
cd job_scraper
python web_app.py
```

Ouvrez http://localhost:5001

## 📖 Documentation

- **Guide complet** : [job_scraper/README_COMPLET.md](job_scraper/README_COMPLET.md)
- **Configuration** : Voir `config.ini.example`

## 🎯 Utilisation

### 1. **Créer un compte**
   - Inscrivez-vous sur l'interface web
   - Configurez vos clés API (Groq recommandé)

### 2. **Rechercher des offres**
   - Entrez vos critères (mots-clés, localisation, type de contrat)
   - Lancez le scraping (23 sites analysés en temps réel)
   - Suivez la progression : "🏢 Bouygues (1/15)", "🌐 Indeed (16/23)"...
   - Cliquez sur ⏹️ **STOP** à tout moment pour garder les résultats
   - Consultez les résultats avec score de pertinence IA

### 3. **Historique automatique**
   - Onglet "📜 Historique" pour voir toutes vos recherches
   - Sauvegarde automatique dès qu'il y a des résultats
   - **Scores de pertinence préservés** lors du rechargement
   - Rechargez les offres d'une ancienne recherche en 1 clic

### 4. **Filtres et tri intelligents**
   - **Trier par** : Pertinence (IA), Date, Entreprise, Salaire
   - **Filtrer par** : Toutes, Haute pertinence, Moyenne et haute
   - **Filtres rapides** : Remote, CDI, Alternance, Stage, Urgent
   - Compteur d'offres visibles en temps réel

### 5. **Générer une candidature**
   - Sélectionnez une offre
   - L'IA adapte votre CV et génère une lettre personnalisée
   - Téléchargez les PDFs

### 6. **Analyser une offre** 🔍
   - **Analyse des compétences** : Skill gap détaillé
   - **Red flags** : Points de vigilance sur l'offre/entreprise
   - **Estimation salariale** : Fourchette réaliste selon le marché

### 7. **Préparer un entretien** 🎤
   - **Questions probables** : Liste des questions à préparer
   - **Analyse entreprise** : Culture, valeurs, actualités
   - **Questions à poser** : Questions intelligentes pour le recruteur
   - **Elevator pitch** : Présentation de 30 secondes personnalisée

### 8. **Affiner avec le chat**
   - Discutez avec l'IA pour améliorer vos documents
   - Modifications en temps réel

## 🛠️ Technologies

- **Backend** : Python, Flask, PostgreSQL
- **Scraping** : Playwright (prioritaire) + Selenium (fallback), Chromium (Railway)
- **IA** : Groq (Llama 3.3), Gemini, OpenAI, Smart Query Builder
- **Frontend** : HTML5, CSS3 (Responsive SOTA), JavaScript (temps réel)
- **PDF** : LaTeX, Markdown
- **Déploiement** : Railway avec PostgreSQL
- **Design** : Mobile-first, Responsive (320px → 4K)

## 🔐 Sécurité

- ✅ **Multi-utilisateurs** avec authentification sécurisée
- ✅ **PostgreSQL** pour persistance des données
- ✅ Clés API stockées par utilisateur (chiffrées)
- ✅ Sessions sécurisées avec tokens
- ✅ **Scores de pertinence sauvegardés** en base de données
- ✅ Pas d'envoi automatique de candidatures
- ✅ Validation manuelle obligatoire

## 📊 Sites Supportés (23 sites)

### Sites d'emploi universels (8)
- **Indeed** - Scraping avancé avec détection Cloudflare
- **LinkedIn** - Jobs publics sans authentification
- **Welcome to the Jungle** - Startups et scale-ups
- **APEC** - Cadres et ingénieurs
- **HelloWork** - Offres généralistes
- **Meteojob** - Tous secteurs
- **RegionsJob** - Offres régionales
- **Monster** - International

### Sites carrières entreprises (15)
- **Bouygues, Alstom, Stellantis, Renault** - Industrie & Transport
- **Société Générale, BNP Paribas** - Finance
- **Schneider Electric, Safran, Thales, Airbus** - Aéronautique & Défense
- **Orange, Capgemini, Atos, Dassault Systèmes** - Tech & IT
- **TotalEnergies** - Énergie

🤖 **Smart Query Builder IA** optimise automatiquement les URLs de recherche pour chaque site

### 🎯 Progression en temps réel
```
🏢 Bouygues (1/15) • 3 offres
🏢 Alstom (2/15) • 7 offres
...
🏢 TotalEnergies (15/15) • 45 offres
🌐 Indeed (16/23) • 52 offres
🌐 LinkedIn (17/23) • 61 offres
...
🌐 Monster (23/23) • 120 offres
✅ 120 offres trouvées
```

## 🎨 Interface Responsive

### 📱 Mobile (320px - 767px)
- Layout vertical optimisé
- Navigation tactile
- Boutons pleine largeur
- Tabs wrappés
- Filtres empilés

### 📱 Tablet (768px - 1024px)
- Grid 2 colonnes
- Espacement équilibré
- Navigation horizontale

### 🖥️ Desktop (>1024px)
- Layout complet
- Grid 3+ colonnes
- Toutes les fonctionnalités

### 🖥️ 4K/Large screens
- Contenu centré
- Max-width 1400px
- Espacement optimal

**Technologies utilisées** :
- `clamp()` pour tailles fluides
- `min()` pour éviter débordements
- `grid-template-columns: repeat(auto-fit, minmax(...))`
- Media queries stratégiques (480px, 768px, 1024px)
- Mobile-first approach

## 🆕 Nouveautés v2.0

### ✨ Améliorations majeures
- ✅ **Progression précise** : Compteur (X/23) en temps réel
- ✅ **Historique intelligent** : Scores de pertinence préservés
- ✅ **Design responsive** : 100% mobile/tablet/desktop
- ✅ **Filtres améliorés** : Compteur d'offres visibles
- ✅ **Tri optimisé** : Par date, salaire, pertinence, entreprise
- ✅ **Playwright prioritaire** : Scraping plus rapide et fiable
- ✅ **Fallback Selenium** : Sécurité si Playwright échoue
- ✅ **Notifications visuelles** : Feedback à chaque action
- ✅ **Analyse complète** : Skill gap, Red flags, Salaire
- ✅ **Préparation entretien** : Questions, Pitch, Analyse entreprise

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Disclaimer

Cet outil est destiné à un usage personnel et éducatif. Respectez les conditions d'utilisation des sites scrapés. L'envoi de candidatures reste manuel et sous votre responsabilité.

## 🙏 Remerciements

- [Groq](https://groq.com) pour leur API rapide et gratuite
- [Google Gemini](https://ai.google.dev) pour leur modèle performant
- La communauté open-source

---

**Développé avec ❤️ pour automatiser intelligemment la recherche d'emploi**
