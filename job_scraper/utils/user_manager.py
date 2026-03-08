"""
Gestionnaire d'utilisateurs avec JSON comme base de données
"""
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

class UserManager:
    def __init__(self, db_file='data/users.json'):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialiser la base de données si elle n'existe pas"""
        if not self.db_file.exists():
            self._save_db({'users': {}, 'sessions': {}})
    
    def _load_db(self):
        """Charger la base de données"""
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_db(self, data):
        """Sauvegarder la base de données"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _hash_password(self, password):
        """Hasher un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email):
        """Créer un nouvel utilisateur"""
        db = self._load_db()
        
        if username in db['users']:
            return {'success': False, 'error': 'Utilisateur existe déjà'}
        
        db['users'][username] = {
            'password': self._hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'api_keys': {
                'groq': '',
                'gemini': '',
                'openai': ''
            },
            'ai_provider': 'gemini',
            'profile': {},
            'background': {}
        }
        
        self._save_db(db)
        return {'success': True}
    
    def login(self, username, password):
        """Connexion utilisateur"""
        db = self._load_db()
        
        if username not in db['users']:
            return {'success': False, 'error': 'Utilisateur introuvable'}
        
        user = db['users'][username]
        if user['password'] != self._hash_password(password):
            return {'success': False, 'error': 'Mot de passe incorrect'}
        
        # Créer une session
        token = secrets.token_urlsafe(32)
        db['sessions'][token] = {
            'username': username,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_db(db)
        return {'success': True, 'token': token, 'username': username}
    
    def verify_token(self, token):
        """Vérifier un token de session"""
        db = self._load_db()
        
        if token not in db['sessions']:
            return None
        
        return db['sessions'][token]['username']
    
    def logout(self, token):
        """Déconnexion"""
        db = self._load_db()
        
        if token in db['sessions']:
            del db['sessions'][token]
            self._save_db(db)
        
        return {'success': True}
    
    def get_user_config(self, username):
        """Récupérer la config d'un utilisateur"""
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
        """Mettre à jour la config d'un utilisateur"""
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
