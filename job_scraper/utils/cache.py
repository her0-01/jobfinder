"""Cache intelligent SQLite pour éviter de re-scraper"""
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class JobCache:
    def __init__(self, db_path="data/cache.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def _generate_key(self, keywords, location, site):
        data = f"{keywords}|{location}|{site}".lower()
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, keywords, location, site):
        key = self._generate_key(keywords, location, site)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM cache WHERE cache_key = ? AND expires_at > datetime('now')", (key,))
        result = cursor.fetchone()
        conn.close()
        return json.loads(result[0]) if result else None
    
    def set(self, keywords, location, site, data, ttl_hours=1):
        key = self._generate_key(keywords, location, site)
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO cache (cache_key, data, expires_at) VALUES (?, ?, ?)",
                      (key, json.dumps(data), expires_at))
        conn.commit()
        conn.close()
    
    def clear_expired(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE expires_at < datetime('now')")
        conn.commit()
        conn.close()
