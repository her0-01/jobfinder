# 🚀 Déploiement Railway avec PostgreSQL

## 1️⃣ Push le code sur GitHub

```bash
git add .
git commit -m "Add PostgreSQL support for persistent storage"
git push origin main
```

## 2️⃣ Créer le projet Railway

1. Allez sur https://railway.app
2. Connectez-vous avec GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Sélectionnez **her0-01/jobfinder**

## 3️⃣ Ajouter PostgreSQL

Dans le dashboard Railway :

1. Cliquez sur **"+ New"** dans votre projet
2. Sélectionnez **"Database"** → **"Add PostgreSQL"**
3. Railway crée automatiquement la variable `DATABASE_URL`

## 4️⃣ Variables d'environnement (optionnelles)

Dans **Variables** du service web :

```bash
# Optionnel - Clés API par défaut (les utilisateurs peuvent mettre les leurs)
GROQ_API_KEY=gsk_votre_cle
GEMINI_API_KEY=votre_cle_gemini
OPENAI_API_KEY=sk-votre_cle_openai

# Requis
PORT=5001
PYTHONUNBUFFERED=1
```

## 5️⃣ Vérifier le déploiement

Railway va automatiquement :
- ✅ Installer PostgreSQL
- ✅ Créer les tables automatiquement au premier lancement
- ✅ Installer Chrome/Chromium
- ✅ Installer les dépendances Python
- ✅ Lancer l'application

## 📊 Structure de la base de données

### Tables créées automatiquement :

1. **users** - Utilisateurs (username, password_hash, email)
2. **api_keys** - Clés API par utilisateur et provider
3. **user_configs** - Configurations (ai_provider, github_url, portfolio_url, profile, background)
4. **sessions** - Sessions de connexion
5. **job_searches** - Historique des recherches
6. **job_offers** - Offres d'emploi trouvées (avec score de pertinence)
7. **applications** - Candidatures générées (CV, lettres, PDFs)

## 🔄 Fonctionnement

### En production (Railway avec PostgreSQL) :
- ✅ Données persistantes entre déploiements
- ✅ Historique complet des recherches
- ✅ Candidatures sauvegardées
- ✅ Multi-utilisateurs avec isolation des données

### En local (sans PostgreSQL) :
- ✅ Fallback automatique vers SQLite
- ✅ Fichier `data/nexus.db` créé localement
- ✅ Même fonctionnalités qu'en production

## 🎯 Avantages PostgreSQL

1. **Persistance** : Les données survivent aux redéploiements
2. **Performance** : Requêtes optimisées, index automatiques
3. **Scalabilité** : Supporte des milliers d'utilisateurs
4. **Historique** : Toutes les recherches et candidatures sont conservées
5. **Analytics** : Possibilité d'analyser les données (taux de succès, meilleurs sites, etc.)

## 🔍 Accéder à la base de données

Dans Railway, cliquez sur PostgreSQL → **Data** pour voir les tables et données.

Ou connectez-vous via CLI :
```bash
railway connect postgres
```

## 📝 Requêtes utiles

```sql
-- Voir tous les utilisateurs
SELECT username, email, created_at FROM users;

-- Statistiques par utilisateur
SELECT u.username, COUNT(j.id) as total_offers, AVG(j.relevance_score) as avg_score
FROM users u
LEFT JOIN job_offers j ON u.id = j.user_id
GROUP BY u.username;

-- Meilleures offres
SELECT title, company, relevance_score, source_site
FROM job_offers
WHERE user_id = 1
ORDER BY relevance_score DESC
LIMIT 10;
```

## ⚠️ Important

- La base de données PostgreSQL sur Railway est **gratuite** jusqu'à 500 MB
- Les données sont **automatiquement sauvegardées**
- Pas besoin de configuration manuelle, tout est automatique !

---

**C'est tout ! Railway + PostgreSQL = Déploiement en 5 minutes** 🚀
