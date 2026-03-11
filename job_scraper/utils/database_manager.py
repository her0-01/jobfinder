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
                cv_content TEXT,
                cover_letter_template TEXT,
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
                cv_content TEXT,
                cover_letter_template TEXT,
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
        
        # Table application_tracking pour suivi des candidatures
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_tracking (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                job_title VARCHAR(500) NOT NULL,
                company VARCHAR(200) NOT NULL,
                applied_date DATE NOT NULL,
                status VARCHAR(50) DEFAULT 'sent',
                last_update TIMESTAMP DEFAULT NOW(),
                next_followup TIMESTAMP,
                notes TEXT,
                contact_email VARCHAR(200),
                contact_name VARCHAR(200),
                interview_date TIMESTAMP,
                salary_proposed VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS application_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                applied_date DATE NOT NULL,
                status TEXT DEFAULT 'sent',
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_followup TIMESTAMP,
                notes TEXT,
                contact_email TEXT,
                contact_name TEXT,
                interview_date TIMESTAMP,
                salary_proposed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Index pour application_tracking
        if self.use_postgres:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_user ON application_tracking(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_status ON application_tracking(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_followup ON application_tracking(next_followup)')
        
        # Table alerts pour alertes personnalisées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                keywords TEXT NOT NULL,
                location TEXT,
                frequency VARCHAR(50) DEFAULT 'daily',
                active BOOLEAN DEFAULT TRUE,
                last_check TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                keywords TEXT NOT NULL,
                location TEXT,
                frequency TEXT DEFAULT 'daily',
                active INTEGER DEFAULT 1,
                last_check TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table alert_notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_notifications (
                id SERIAL PRIMARY KEY,
                alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                job_title TEXT NOT NULL,
                job_company TEXT,
                job_link TEXT,
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS alert_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                user_id INTEGER,
                job_title TEXT NOT NULL,
                job_company TEXT,
                job_link TEXT,
                read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(alert_id) REFERENCES alerts(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Table alert_seen_jobs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_seen_jobs (
                id SERIAL PRIMARY KEY,
                alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
                job_link TEXT NOT NULL,
                seen_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(alert_id, job_link)
            )
        ''' if self.use_postgres else '''
            CREATE TABLE IF NOT EXISTS alert_seen_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                job_link TEXT NOT NULL,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(alert_id, job_link),
                FOREIGN KEY(alert_id) REFERENCES alerts(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        print("✅ Toutes les tables créées avec succès (users, api_keys, user_configs, sessions, job_searches, job_offers, applications, application_tracking, alerts, alert_notifications, alert_seen_jobs)")
    
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
                   profile_data = %s, background_data = %s, 
                   cv_content = %s, cover_letter_template = %s,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE user_id = %s''' if self.use_postgres
                else '''UPDATE user_configs SET 
                        ai_provider = ?, github_url = ?, portfolio_url = ?,
                        profile_data = ?, background_data = ?,
                        cv_content = ?, cover_letter_template = ?,
                        updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?''',
                (config.get('ai_provider', 'groq'),
                 config.get('github_url'),
                 config.get('portfolio_url'),
                 json.dumps(config.get('profile', {})),
                 json.dumps(config.get('background', {})),
                 config.get('cv_content'),
                 config.get('cover_letter_template'),
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
                'background_data': config[6],
                'cv_content': config[7] if len(config) > 7 else None,
                'cover_letter_template': config[8] if len(config) > 8 else None
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
        
        # Support 'link' ou 'url'
        url = offer_data.get('link') or offer_data.get('url')
        relevance_score = offer_data.get('relevance_score', 50)
        
        cursor.execute(
            '''INSERT INTO job_offers 
               (search_id, user_id, title, company, location, url, description, relevance_score, source_site)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''' if self.use_postgres
            else '''INSERT INTO job_offers 
                    (search_id, user_id, title, company, location, url, description, relevance_score, source_site)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (search_id, user_id, offer_data.get('title'), offer_data.get('company'),
             offer_data.get('location'), url, offer_data.get('description'),
             relevance_score, offer_data.get('source'))
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
    
    def get_user_searches(self, user_id, limit=20):
        """Récupère l'historique des recherches d'un utilisateur"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            '''SELECT s.*, COUNT(j.id) as jobs_count
               FROM job_searches s
               LEFT JOIN job_offers j ON s.id = j.search_id
               WHERE s.user_id = %s
               GROUP BY s.id
               ORDER BY s.created_at DESC
               LIMIT %s''' if self.use_postgres
            else '''SELECT s.*, COUNT(j.id) as jobs_count
                    FROM job_searches s
                    LEFT JOIN job_offers j ON s.id = j.search_id
                    WHERE s.user_id = ?
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                    LIMIT ?''',
            (user_id, limit)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_search_jobs(self, search_id):
        """Récupère toutes les offres d'une recherche spécifique avec leurs scores"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        cursor.execute(
            '''SELECT id, search_id, user_id, title, company, location, url, 
                      description, relevance_score, source_site, scraped_at, applied, applied_at
               FROM job_offers 
               WHERE search_id = %s 
               ORDER BY relevance_score DESC, scraped_at DESC''' if self.use_postgres
            else '''SELECT id, search_id, user_id, title, company, location, url, 
                           description, relevance_score, source_site, scraped_at, applied, applied_at
                    FROM job_offers 
                    WHERE search_id = ? 
                    ORDER BY relevance_score DESC, scraped_at DESC''',
            (search_id,)
        )
        
        jobs = cursor.fetchall()
        
        if self.use_postgres:
            return [{
                'id': row['id'],
                'title': row['title'],
                'company': row['company'],
                'location': row['location'],
                'link': row['url'],
                'description': row['description'],
                'relevance_score': float(row['relevance_score']) if row['relevance_score'] else 50.0,
                'source': row['source_site'],
                'scraped_at': row['scraped_at']
            } for row in jobs]
        else:
            return [{
                'id': row[0],
                'title': row[3],
                'company': row[4],
                'location': row[5],
                'link': row[6],
                'description': row[7],
                'relevance_score': float(row[8]) if row[8] else 50.0,
                'source': row[9],
                'scraped_at': row[10]
            } for row in jobs]
    
    def save_alert_notification(self, alert_id, user_id, job):
        """Sauvegarder une notification d'alerte"""
        query = """INSERT INTO alert_notifications (alert_id, user_id, job_title, job_company, job_link, created_at) 
                   VALUES (%s, %s, %s, %s, %s, NOW())"""
        self.execute_query(query, (alert_id, user_id, job['title'], job['company'], job['link']))
    
    def get_user_notifications(self, user_id, unread_only=False):
        """Récupérer les notifications d'un utilisateur"""
        query = "SELECT * FROM alert_notifications WHERE user_id = %s"
        if unread_only:
            query += " AND read = FALSE"
        query += " ORDER BY created_at DESC LIMIT 50"
        return self.execute_query(query, (user_id,), fetch=True)
    
    def mark_notification_read(self, notification_id):
        """Marquer une notification comme lue"""
        query = "UPDATE alert_notifications SET read = TRUE WHERE id = %s"
        self.execute_query(query, (notification_id,))
    
    def get_unread_count(self, user_id):
        """Compter les notifications non lues"""
        query = "SELECT COUNT(*) FROM alert_notifications WHERE user_id = %s AND read = FALSE"
        result = self.execute_query(query, (user_id,), fetch=True)
        return result[0][0] if result else 0

    def get_active_alerts(self):
        """Récupérer toutes les alertes actives"""
        query = "SELECT * FROM alerts WHERE active = TRUE"
        return self.execute_query(query, fetch=True)
    
    def update_alert_last_check(self, alert_id):
        """Mettre à jour la date de dernière vérification"""
        query = "UPDATE alerts SET last_check = NOW() WHERE id = %s"
        self.execute_query(query, (alert_id,))
    
    def get_seen_job_links(self, alert_id):
        """Récupérer les liens d'offres déjà vues pour une alerte"""
        query = "SELECT job_link FROM alert_seen_jobs WHERE alert_id = %s"
        results = self.execute_query(query, (alert_id,), fetch=True)
        return [r[0] for r in results] if results else []
    
    def mark_job_as_seen(self, alert_id, job_link):
        """Marquer une offre comme vue"""
        query = "INSERT INTO alert_seen_jobs (alert_id, job_link, seen_at) VALUES (%s, %s, NOW()) ON CONFLICT DO NOTHING"
        self.execute_query(query, (alert_id, job_link))
    
    def get_user_by_id(self, user_id):
        """Récupérer un utilisateur par ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None
    
    def execute_query(self, query, params=None, fetch=False):
        """Exécuter une requête SQL générique"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor) if self.use_postgres else self.conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                self.conn.commit()
                return cursor
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Database error: {e}")
            raise

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
