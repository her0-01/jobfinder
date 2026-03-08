# 🚂 Déploiement sur Railway.app

## Commandes à exécuter :

```bash
# 1. Nettoyer le repo
cd "c:\Users\user\Downloads\SE décentralisé\nexus-os"
CLEAN_FOR_GITHUB.bat

# 2. Initialiser Git
git init
git add .
git commit -m "Initial commit: NEXUS-OS"

# 3. Créer repo GitHub
# Aller sur https://github.com/new
# Nom: nexus-os
# Public ou Private

# 4. Push vers GitHub (remplacer YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/nexus-os.git
git branch -M main
git push -u origin main

# 5. Déployer sur Railway
# Aller sur https://railway.app
# Se connecter avec GitHub
# New Project > Deploy from GitHub repo
# Sélectionner nexus-os
```

## Configuration Railway :

### Variables d'environnement à ajouter :
```
GROQ_API_KEY=votre_clé_groq
GEMINI_API_KEY=votre_clé_gemini
OPENAI_API_KEY=votre_clé_openai
PORT=5001
```

### Fichiers créés pour Railway :
- ✅ `Procfile` - Commande de démarrage
- ✅ `nixpacks.toml` - Installation Chrome
- ✅ `Dockerfile` - Image avec Chrome
- ✅ `web_app.py` - Modifié pour port dynamique

## Railway détectera automatiquement :
- Python 3.9
- requirements.txt
- Procfile

## Après déploiement :
1. Railway vous donnera une URL : `https://nexus-os-production.up.railway.app`
2. Ouvrir l'URL dans le navigateur
3. Configurer vos clés API dans l'interface

## Crédits Railway :
- 5$ gratuits par mois
- Suffisant pour ~500h d'utilisation
- Pas de carte bancaire requise initialement

## Troubleshooting :
Si Chrome ne fonctionne pas, vérifier les logs Railway et s'assurer que `nixpacks.toml` est bien détecté.
