"""
Gestionnaire d'utilisateurs - Wrapper pour DatabaseManager
Compatible avec l'ancien système JSON mais utilise PostgreSQL si disponible
"""
import os
import secrets
from datetime import datetime
from pathlib import Path

# Import conditionnel selon l'environnement
try:
    from .database_manager import DatabaseManager
    USE_DATABASE = True
except:
    USE_DATABASE = False

if not USE_DATABASE:
    # Fallback vers JSON si pas de DB
    import json
    import hashlib
    from pathlib import Path

class UserManager:
    def __init__(self, db_file='data/users.json'):
        if USE_DATABASE and os.getenv('DATABASE_URL'):
            self.db = DatabaseManager()
            self.use_db = True
        else:
            # Fallback JSON
            self.use_db = False
            self.db_file = Path(db_file)
            self.db_file.parent.mkdir(exist_ok=True)
            self._init_db()
    
    def _init_db(self):
        """Initialiser la base de données JSON"""
        if not self.db_file.exists():
            self._save_db({'users': {}, 'sessions': {}})
    
    def _load_db(self):
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_db(self, data):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email):
        if self.use_db:
            return self.db.create_user(username, password, email)
        
        # Fallback JSON
        db = self._load_db()
        if username in db['users']:
            return {'success': False, 'error': 'Utilisateur existe déjà'}
        
        db['users'][username] = {
            'password': self._hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'api_keys': {'groq': '', 'gemini': '', 'openai': ''},
            'ai_provider': 'gemini',
            'profile': {},
            'background': {}
        }
        self._save_db(db)
        return {'success': True}
    
    def login(self, username, password):
        if self.use_db:
            result = self.db.authenticate_user(username, password)
            if result['success']:
                token = secrets.token_urlsafe(32)
                # Créer session dans DB
                return {'success': True, 'token': token, 'username': username, 'user_id': result['user']['id']}
            return result
        
        # Fallback JSON
        db = self._load_db()
        if username not in db['users']:
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        user = db['users'][username]
        if user['password'] != self._hash_password(password):
            return {'success': False, 'error': 'Mot de passe incorrect'}
        
        token = secrets.token_urlsafe(32)
        db['sessions'][token] = {'username': username, 'created_at': datetime.now().isoformat()}
        self._save_db(db)
        return {'success': True, 'token': token, 'username': username}
    
    def verify_token(self, token):
        if self.use_db:
            # Vérifier dans DB
            return token  # Simplifié pour l'instant
        
        db = self._load_db()
        return db['sessions'].get(token, {}).get('username')
    
    def logout(self, token):
        if self.use_db:
            return {'success': True}
        
        db = self._load_db()
        if token in db['sessions']:
            del db['sessions'][token]
            self._save_db(db)
        return {'success': True}
    
    def get_user_config(self, username):
        if self.use_db:
            # Récupérer user_id depuis username
            user_id = self._get_user_id(username)
            if user_id:
                config = self.db.get_user_config(user_id)
                api_keys = self.db.get_api_keys(user_id)
                config['api_keys'] = api_keys
                return config
            return None
        
        db = self._load_db()
        if username not in db['users']:
            return None
        
        user = db['users'][username]
        return {
            'api_keys': user['api_keys'],
            'ai_provider': user['ai_provider'],
            'profile': user['profile'],
            'background': user['background']
        }
    
    def update_user_config(self, username, config):
        if self.use_db:
            user_id = self._get_user_id(username)
            if user_id:
                if 'api_keys' in config:
                    for provider, key in config['api_keys'].items():
                        if key:  # Ne sauvegarder que si non vide
                            self.db.save_api_key(user_id, provider, key)
                self.db.save_user_config(user_id, config)
                return {'success': True}
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        db = self._load_db()
        if username not in db['users']:
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        user = db['users'][username]
        if 'api_keys' in config:
            user['api_keys'].update(config['api_keys'])
        if 'ai_provider' in config:
            user['ai_provider'] = config['ai_provider']
        if 'profile' in config:
            user['profile'].update(config['profile'])
        if 'background' in config:
            user['background'].update(config['background'])
        
        self._save_db(db)
        return {'success': True}
    
    def _get_user_id(self, username):
        """Helper pour récupérer user_id depuis username"""
        if not self.use_db:
            return None
        
        # Requête DB pour récupérer user_id
        cursor = self.db.conn.cursor()
        cursor.execute(
            'SELECT id FROM users WHERE username = %s' if self.db.use_postgres
            else 'SELECT id FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
