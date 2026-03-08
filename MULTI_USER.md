# 🔐 Système Multi-Utilisateurs

## Fonctionnalités

✅ **Authentification** : Login/Register avec tokens
✅ **Base de données JSON** : Simple et portable
✅ **Clés API par utilisateur** : Chaque utilisateur configure ses propres clés
✅ **Données isolées** : Chaque utilisateur a ses propres candidatures

## Structure

```
data/
├── users.json          # Base de données utilisateurs
└── applications/       # Candidatures par utilisateur
    └── {username}/
        └── {timestamp}_{company}/
```

## Utilisation

### 1. Inscription
- Aller sur `/login`
- Cliquer sur "Inscription"
- Créer un compte

### 2. Configuration des clés API
- Se connecter
- Aller dans "Configuration"
- Ajouter vos clés API (Groq, Gemini, OpenAI)
- Choisir le provider par défaut

### 3. Utilisation
- Chaque utilisateur a ses propres :
  - Clés API
  - Profil
  - Candidatures générées
  - Historique de recherche

## Format users.json

```json
{
  "users": {
    "username": {
      "password": "hash_sha256",
      "email": "user@example.com",
      "created_at": "2026-03-08T21:00:00",
      "api_keys": {
        "groq": "gsk_...",
        "gemini": "AIza...",
        "openai": "sk-..."
      },
      "ai_provider": "gemini",
      "profile": {
        "name": "...",
        "email": "...",
        "github": "...",
        "portfolio": "..."
      },
      "background": {
        "formation": "...",
        "competences": "..."
      }
    }
  },
  "sessions": {
    "token_xyz": {
      "username": "username",
      "created_at": "2026-03-08T21:00:00"
    }
  }
}
```

## Sécurité

- ✅ Mots de passe hashés (SHA-256)
- ✅ Tokens de session sécurisés
- ✅ Clés API stockées par utilisateur
- ✅ Pas de partage de données entre utilisateurs

## Déploiement

Sur Railway, les données persistent dans le volume.
Chaque utilisateur peut utiliser l'app avec ses propres clés API.
