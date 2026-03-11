"""Système de logs avancés"""
import logging
from datetime import datetime
from pathlib import Path

class AdvancedLogger:
    def __init__(self, name="jobfinder"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Créer dossier logs
        Path("logs").mkdir(exist_ok=True)
        
        # Handler fichier
        fh = logging.FileHandler(f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log")
        fh.setLevel(logging.DEBUG)
        
        # Handler console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_scraping_start(self, site, keywords, location):
        self.logger.info(f"🚀 Scraping {site}: '{keywords}' @ '{location}'")
    
    def log_scraping_end(self, site, count, duration):
        self.logger.info(f"✅ {site}: {count} offres en {duration:.2f}s")
    
    def log_error(self, site, error):
        self.logger.error(f"❌ {site}: {error}")
    
    def log_cache_hit(self, keywords, count):
        self.logger.info(f"💾 Cache hit: {count} offres pour '{keywords}'")
    
    def log_fallback(self, original, simplified):
        self.logger.warning(f"🔄 Fallback: '{original}' → '{simplified}'")
