from datetime import datetime
from utils.database_manager import DatabaseManager
from scrapers.universal_scraper import UniversalJobScraper
import threading
import time

class SimpleAlertSystem:
    """Système d'alertes simple sans email - notifications in-app uniquement"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.running = False
        
    def check_alerts_once(self):
        """Vérifier toutes les alertes une fois"""
        try:
            alerts = self.db.get_active_alerts()
            
            for alert in alerts:
                user_id = alert['user_id']
                keywords = alert['keywords']
                location = alert.get('location', 'France')
                
                # Scraper rapidement (5 offres max)
                scraper = UniversalJobScraper(headless=True)
                jobs = scraper.scrape_all(keywords, location)[:5]
                scraper.close()
                
                # Filtrer nouvelles offres
                seen_links = self.db.get_seen_job_links(alert['id'])
                new_jobs = [j for j in jobs if j['link'] not in seen_links]
                
                if new_jobs:
                    # Sauvegarder les nouvelles offres
                    for job in new_jobs:
                        self.db.save_alert_notification(alert['id'], user_id, job)
                        self.db.mark_job_as_seen(alert['id'], job['link'])
                    
                    print(f"✅ Alerte {alert['id']}: {len(new_jobs)} nouvelles offres")
                
                # Mettre à jour last_check
                self.db.update_alert_last_check(alert['id'])
                
        except Exception as e:
            print(f"❌ Erreur check alerts: {e}")
    
    def start_background_checker(self):
        """Lancer vérification en arrière-plan (toutes les heures)"""
        def checker_loop():
            while self.running:
                self.check_alerts_once()
                time.sleep(3600)  # 1 heure
        
        self.running = True
        thread = threading.Thread(target=checker_loop, daemon=True)
        thread.start()
        print("🔔 Système d'alertes démarré")
    
    def stop(self):
        self.running = False

# Instance globale
alert_system = SimpleAlertSystem()
