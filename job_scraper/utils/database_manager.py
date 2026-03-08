"""
Database Manager - PostgreSQL pour persistance des données
Remplace le système JSON par une base de données PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self):
        # Railway fournit DATABASE_URL automatiquement
        self.database_url = os.getenv('DATABASE_URL')
        
        # Fallback vers SQLite en local si pas de PostgreSQL
        self.use_postgres = self.database_url is not None
        
        if self.use_postgres:
            self.conn = psycopg2.connect(self.database_url)
        else:
            # Fallback SQLite pour développement local
            import sqlite3
            os.makedirs('data', exist_ok=True)
            self.conn = sqlite3.connect('data/nexus.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        
        self.init_database()
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        cursor = self.conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Table clés API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR(50) NOT NULL,
                api_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, provider)
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                provider TEXT NOT NULL,
                api_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, provider),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table configurations utilisateur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_configs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                ai_provider VARCHAR(50) DEFAULT 'groq',
                github_url TEXT,
                portfolio_url TEXT,
                profile_data TEXT,
                background_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS user_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                ai_provider TEXT DEFAULT 'groq',
                github_url TEXT,
                portfolio_url TEXT,
                profile_data TEXT,
                background_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                token VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table recherches d'emploi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_searches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                search_query TEXT NOT NULL,
                location TEXT,
                contract_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS job_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                search_query TEXT NOT NULL,
                location TEXT,
                contract_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table offres d'emploi trouvées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_offers (
                id SERIAL PRIMARY KEY,
                search_id INTEGER REFERENCES job_searches(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                url TEXT,
                description TEXT,
                relevance_score FLOAT,
                source_site VARCHAR(100),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied BOOLEAN DEFAULT FALSE,
                applied_at TIMESTAMP
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS job_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER,
                user_id INTEGER,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                url TEXT,
                description TEXT,
                relevance_score REAL,
                source_site TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied INTEGER DEFAULT 0,
                applied_at TIMESTAMP,
                FOREIGN KEY(search_id) REFERENCES job_searches(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table candidatures générées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                job_offer_id INTEGER REFERENCES job_offers(id) ON DELETE CASCADE,
                cv_content TEXT,
                cover_letter TEXT,
                cv_pdf_path TEXT,
                cover_letter_pdf_path TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_offer_id INTEGER,
                cv_content TEXT,
                cover_letter TEXT,
                cv_pdf_path TEXT,
                cover_letter_pdf_path TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(job_offer_id) REFERENCES job_offers(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def create_user(self, username, password, email=None):
        """Crée un nouvel utilisateur"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s) RETURNING id' if self.use_postgres
                else 'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                (username, password_hash, email)
            )
            self.conn.commit()
            
            if self.use_postgres:
                user_id = cursor.fetchone()[0]
            else:
                user_id = cursor.lastrowid
            
            # Créer config par défaut
            cursor.execute(
                'INSERT INTO user_configs (user_id) VALUES (%s)' if self.use_postgres
                else 'INSERT INTO user_configs (user_id) VALUES (?)',
                (user_id,)
            )
            self.conn.commit()
            
            return {'success': True, 'user_id': user_id}
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username, password):
        """Authentifie un utilisateur"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            'SELECT id, username, email FROM users WHERE username = %s AND password_hash = %s' if self.use_postgres
            else 'SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        if user:
            # Mettre à jour last_login
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s' if self.use_postgres
                else 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'] if self.use_postgres else user[0],)
            )
            self.conn.commit()
            
            return {'success': True, 'user': dict(user) if self.use_postgres else {
                'id': user[0], 'username': user[1], 'email': user[2]
            }}
        
        return {'success': False, 'error': 'Invalid credentials'}
    
    def save_api_key(self, user_id, provider, api_key):
        """Sauvegarde une clé API"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT INTO api_keys (user_id, provider, api_key) 
                   VALUES (%s, %s, %s) 
                   ON CONFLICT (user_id, provider) 
                   DO UPDATE SET api_key = EXCLUDED.api_key''' if self.use_postgres
                else '''INSERT OR REPLACE INTO api_keys (user_id, provider, api_key) 
                        VALUES (?, ?, ?)''',
                (user_id, provider, api_key)
            )
            self.conn.commit()
            return {'success': True}
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_api_keys(self, user_id):
        """Récupère les clés API d'un utilisateur"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            'SELECT provider, api_key FROM api_keys WHERE user_id = %s' if self.use_postgres
            else 'SELECT provider, api_key FROM api_keys WHERE user_id = ?',
            (user_id,)
        )
        
        keys = cursor.fetchall()
        return {row['provider'] if self.use_postgres else row[0]: 
                row['api_key'] if self.use_postgres else row[1] for row in keys}
    
    def save_user_config(self, user_id, config):
        """Sauvegarde la configuration utilisateur"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                '''UPDATE user_configs SET 
                   ai_provider = %s, github_url = %s, portfolio_url = %s,
                   profile_data = %s, background_data = %s, updated_at = CURRENT_TIMESTAMP
                   WHERE user_id = %s''' if self.use_postgres
                else '''UPDATE user_configs SET 
                        ai_provider = ?, github_url = ?, portfolio_url = ?,
                        profile_data = ?, background_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?''',
                (config.get('ai_provider', 'groq'),
                 config.get('github_url'),
                 config.get('portfolio_url'),
                 json.dumps(config.get('profile', {})),
                 json.dumps(config.get('background', {})),
                 user_id)
            )
            self.conn.commit()
            return {'success': True}
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_config(self, user_id):
        """Récupère la configuration utilisateur"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            'SELECT * FROM user_configs WHERE user_id = %s' if self.use_postgres
            else 'SELECT * FROM user_configs WHERE user_id = ?',
            (user_id,)
        )
        
        config = cursor.fetchone()
        if config:
            result = dict(config) if self.use_postgres else {
                'ai_provider': config[2],
                'github_url': config[3],
                'portfolio_url': config[4],
                'profile_data': config[5],
                'background_data': config[6]
            }
            
            # Parser les JSON
            if result.get('profile_data'):
                result['profile'] = json.loads(result['profile_data'])
            if result.get('background_data'):
                result['background'] = json.loads(result['background_data'])
            
            return result
        
        return {}
    
    def save_job_search(self, user_id, query, location=None, contract_type=None):
        """Sauvegarde une recherche d'emploi"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            'INSERT INTO job_searches (user_id, search_query, location, contract_type) VALUES (%s, %s, %s, %s) RETURNING id' if self.use_postgres
            else 'INSERT INTO job_searches (user_id, search_query, location, contract_type) VALUES (?, ?, ?, ?)',
            (user_id, query, location, contract_type)
        )
        self.conn.commit()
        
        return cursor.fetchone()[0] if self.use_postgres else cursor.lastrowid
    
    def save_job_offer(self, search_id, user_id, offer_data):
        """Sauvegarde une offre d'emploi"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            '''INSERT INTO job_offers 
               (search_id, user_id, title, company, location, url, description, relevance_score, source_site)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''' if self.use_postgres
            else '''INSERT INTO job_offers 
                    (search_id, user_id, title, company, location, url, description, relevance_score, source_site)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (search_id, user_id, offer_data.get('title'), offer_data.get('company'),
             offer_data.get('location'), offer_data.get('url'), offer_data.get('description'),
             offer_data.get('relevance_score'), offer_data.get('source'))
        )
        self.conn.commit()
        
        return cursor.fetchone()[0] if self.use_postgres else cursor.lastrowid
    
    def get_user_job_offers(self, user_id, limit=50):
        """Récupère les offres d'emploi d'un utilisateur"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            '''SELECT * FROM job_offers 
               WHERE user_id = %s 
               ORDER BY scraped_at DESC 
               LIMIT %s''' if self.use_postgres
            else '''SELECT * FROM job_offers 
                    WHERE user_id = ? 
                    ORDER BY scraped_at DESC 
                    LIMIT ?''',
            (user_id, limit)
        )
        
        return [dict(row) if self.use_postgres else dict(zip(
            ['id', 'search_id', 'user_id', 'title', 'company', 'location', 'url', 
             'description', 'relevance_score', 'source_site', 'scraped_at', 'applied', 'applied_at'],
            row
        )) for row in cursor.fetchall()]
    
    def save_application(self, user_id, job_offer_id, cv_content, cover_letter, cv_pdf_path=None, cover_letter_pdf_path=None):
        """Sauvegarde une candidature générée"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            '''INSERT INTO applications 
               (user_id, job_offer_id, cv_content, cover_letter, cv_pdf_path, cover_letter_pdf_path)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id''' if self.use_postgres
            else '''INSERT INTO applications 
                    (user_id, job_offer_id, cv_content, cover_letter, cv_pdf_path, cover_letter_pdf_path)
                    VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, job_offer_id, cv_content, cover_letter, cv_pdf_path, cover_letter_pdf_path)
        )
        self.conn.commit()
        
        return cursor.fetchone()[0] if self.use_postgres else cursor.lastrowid
    
    def get_user_applications(self, user_id, limit=20):
        """Récupère les candidatures d'un utilisateur"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            '''SELECT a.*, j.title, j.company 
               FROM applications a
               JOIN job_offers j ON a.job_offer_id = j.id
               WHERE a.user_id = %s 
               ORDER BY a.generated_at DESC 
               LIMIT %s''' if self.use_postgres
            else '''SELECT a.*, j.title, j.company 
                    FROM applications a
                    JOIN job_offers j ON a.job_offer_id = j.id
                    WHERE a.user_id = ? 
                    ORDER BY a.generated_at DESC 
                    LIMIT ?''',
            (user_id, limit)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
