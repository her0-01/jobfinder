# 🔔 Système d'Alertes Automatiques

## Comment ça fonctionne

### 1. **Création d'alerte par l'utilisateur**
- L'utilisateur crée une alerte avec :
  - Mots-clés (ex: "Data Engineer Remote")
  - Localisation
  - Fréquence (instantané/quotidien/hebdomadaire)

### 2. **Scheduler en arrière-plan**
- Un processus Python (`alert_scheduler.py`) tourne en continu
- Vérifie toutes les alertes actives selon leur fréquence
- Scrape les sites d'emploi pour chaque alerte

### 3. **Détection de nouvelles offres**
- Compare avec les offres déjà vues (stockées en DB)
- Filtre uniquement les nouvelles offres

### 4. **Notification**
- Envoie un email avec les nouvelles offres
- Peut aussi envoyer des notifications push (à implémenter)

## Installation

### 1. Créer les tables
```bash
psql -U postgres -d nexus_db -f sql/create_alerts_tables.sql
```

### 2. Configurer l'email
Éditer `alert_scheduler.py` :
```python
smtp_server = "smtp.gmail.com"
sender_email = "votre-email@gmail.com"
sender_password = "votre-mot-de-passe-app"  # Mot de passe d'application Gmail
```

### 3. Lancer le scheduler
```bash
# En local
python alert_scheduler.py

# Sur Railway (ajouter dans Procfile)
worker: python alert_scheduler.py
```

## Déploiement Railway

### 1. Ajouter worker dans Procfile
```
web: python web_app.py
worker: python alert_scheduler.py
```

### 2. Variables d'environnement
- `DATABASE_URL` : URL PostgreSQL
- `SMTP_EMAIL` : Email expéditeur
- `SMTP_PASSWORD` : Mot de passe app Gmail

### 3. Activer le worker
Dans Railway Dashboard :
- Aller dans Settings
- Ajouter un nouveau service "Worker"
- Déployer

## API Routes à ajouter

```python
@app.route('/api/alerts', methods=['GET', 'POST'])
@require_auth
def manage_alerts():
    if request.method == 'GET':
        # Récupérer alertes de l'utilisateur
        alerts = db_manager.get_user_alerts(user_id)
        return jsonify(alerts)
    else:
        # Créer nouvelle alerte
        data = request.json
        alert_id = db_manager.create_alert(
            user_id=user_id,
            keywords=data['keywords'],
            location=data['location'],
            frequency=data['frequency']
        )
        return jsonify({'id': alert_id})

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
@require_auth
def delete_alert(alert_id):
    db_manager.delete_alert(alert_id, user_id)
    return jsonify({'success': True})
```

## Avantages

✅ **Automatique** - Pas besoin de chercher manuellement
✅ **Temps réel** - Alertes instantanées possibles
✅ **Multi-critères** - Plusieurs alertes par utilisateur
✅ **Email** - Notifications directes dans la boîte mail
✅ **Pas de doublons** - Système de tracking des offres vues
✅ **Scalable** - Peut gérer des milliers d'utilisateurs

## Améliorations futures

- 📱 Notifications push mobile
- 🤖 Filtrage IA avancé (score de pertinence)
- 📊 Statistiques d'alertes (taux de clics, etc.)
- 🔗 Intégration Telegram/Slack/Discord
- ⚡ Webhooks pour intégrations tierces
