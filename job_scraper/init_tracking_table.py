"""
Script pour créer la table application_tracking sur Railway
À exécuter une seule fois après déploiement
"""

from application_tracker import CREATE_TRACKING_TABLE
from utils.database_manager import DatabaseManager

try:
    db = DatabaseManager()
    db.execute_query(CREATE_TRACKING_TABLE)
    print('✅ Table application_tracking créée avec succès sur Railway')
except Exception as e:
    print(f'❌ Erreur: {e}')
