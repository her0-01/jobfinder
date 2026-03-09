# 🤖 NEXUS-OS - Système Multi-Agents IA

Plateforme complète d'automatisation de recherche d'emploi avec agents IA et scraping intelligent.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Fonctionnalités

### 💼 Job Application Bot
- 🔍 **Scraping intelligent** de 23 sites d'emploi (Indeed, LinkedIn, WTTJ, APEC + 15 sites carrières)
- 🤖 **IA Smart Query Builder** pour optimiser automatiquement les recherches
- 📊 **Progression en temps réel** avec noms des sites scrapés
- ⏹️ **Bouton STOP** pour arrêter et garder les résultats déjà trouvés
- 📜 **Historique automatique** des recherches avec sauvegarde instantanée
- 👥 **Multi-utilisateurs** avec authentification et base PostgreSQL
- 📝 **Adaptation automatique** de CV et lettres de motivation par IA
- 🎯 **Scoring de pertinence** des offres par IA
- 🌐 **Interface web moderne** avec dashboard interactif
- ✅ **Validation manuelle** (pas d'envoi automatique)

### 🧠 Multi-Agents IA
- 🔄 **Compatible** avec Groq, Gemini, OpenAI
- 🛡️ **Fallback automatique** entre providers
- 📊 **Analyse de profil** GitHub et Portfolio
- 💬 **Chat interactif** pour améliorer les candidatures
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
   - Suivez la progression : "Bouygues (1/15)", "Indeed (1/8)"...
   - Cliquez sur ⏹️ **STOP** à tout moment pour garder les résultats
   - Consultez les résultats avec score de pertinence IA

### 3. **Historique automatique**
   - Onglet "📜 Historique" pour voir toutes vos recherches
   - Sauvegarde automatique dès qu'il y a des résultats
   - Rechargez les offres d'une ancienne recherche en 1 clic

### 4. **Générer une candidature**
   - Sélectionnez une offre
   - L'IA adapte votre CV et génère une lettre personnalisée
   - Téléchargez les PDFs

### 5. **Affiner avec le chat**
   - Discutez avec l'IA pour améliorer vos documents
   - Modifications en temps réel

## 🛠️ Technologies

- **Backend** : Python, Flask, PostgreSQL
- **Scraping** : Selenium, BeautifulSoup, Chromium (Railway)
- **IA** : Groq (Llama 3.3), Gemini, OpenAI, Smart Query Builder
- **Frontend** : HTML, CSS, JavaScript (temps réel)
- **PDF** : LaTeX, Markdown
- **Déploiement** : Railway avec PostgreSQL

## 🔐 Sécurité

- ✅ **Multi-utilisateurs** avec authentification sécurisée
- ✅ **PostgreSQL** pour persistance des données
- ✅ Clés API stockées par utilisateur
- ✅ Sessions sécurisées avec tokens
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
