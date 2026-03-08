# 🤖 NEXUS-OS - Système Multi-Agents IA

Plateforme complète d'automatisation de recherche d'emploi avec agents IA et scraping intelligent.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Fonctionnalités

### 💼 Job Application Bot
- 🔍 **Scraping intelligent** de 15+ sites d'emploi (Indeed, LinkedIn, WTTJ, APEC, sites carrières...)
- 🤖 **IA Vision** pour analyse automatique des formulaires de recherche
- 📝 **Adaptation automatique** de CV et lettres de motivation par IA
- 🎯 **Scoring de pertinence** des offres
- 🌐 **Interface web moderne** avec dashboard interactif
- ✅ **Validation manuelle** (pas d'envoi automatique)

### 🧠 Multi-Agents IA
- 🔄 **Compatible** avec Groq, Gemini, OpenAI
- 🛡️ **Fallback automatique** entre providers
- 📊 **Analyse de profil** GitHub et Portfolio
- 💬 **Chat interactif** pour améliorer les candidatures

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

1. **Rechercher des offres**
   - Entrez vos critères (mots-clés, localisation, type de contrat)
   - Lancez le scraping (15+ sites analysés)
   - Consultez les résultats avec score de pertinence

2. **Générer une candidature**
   - Sélectionnez une offre
   - L'IA adapte votre CV et génère une lettre personnalisée
   - Téléchargez les PDFs

3. **Affiner avec le chat**
   - Discutez avec l'IA pour améliorer vos documents
   - Modifications en temps réel

## 🛠️ Technologies

- **Backend** : Python, Flask
- **Scraping** : Selenium, BeautifulSoup, Undetected ChromeDriver
- **IA** : Groq (Llama 3.3), Gemini, OpenAI
- **Frontend** : HTML, CSS, JavaScript
- **PDF** : LaTeX, Markdown

## 🔐 Sécurité

- ✅ Clés API non commitées (.gitignore)
- ✅ Données personnelles locales uniquement
- ✅ Pas d'envoi automatique de candidatures
- ✅ Validation manuelle obligatoire

## 📊 Sites Supportés

### Sites d'emploi
- Indeed, LinkedIn, Welcome to the Jungle, APEC, Hellowork, Meteojob, Cadremploi, Monster

### Sites carrières (IA Vision)
- Bouygues, Alstom, Stellantis, Renault, Société Générale, BNP Paribas, Schneider Electric, Safran, Thales, Airbus, Orange, Capgemini, Atos, Dassault Systèmes, TotalEnergies

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
