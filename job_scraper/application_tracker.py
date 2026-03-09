from datetime import datetime, timedelta
from utils.database_manager import DatabaseManager

class ApplicationTracker:
    """Suivi intelligent des candidatures avec relances automatiques"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_application(self, user_id, job_title, company, applied_date, status='sent'):
        """Ajouter une candidature au suivi"""
        query = """
        INSERT INTO application_tracking 
        (user_id, job_title, company, applied_date, status, last_update, next_followup)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        RETURNING id
        """
        # Relance automatique dans 7 jours
        next_followup = applied_date + timedelta(days=7)
        
        result = self.db.execute_query(
            query, 
            (user_id, job_title, company, applied_date, status, next_followup),
            fetch=True
        )
        return result[0][0] if result else None
    
    def update_status(self, application_id, new_status, notes=''):
        """
        Mettre à jour le statut d'une candidature
        Statuts: sent, viewed, interview_scheduled, interview_done, offer, rejected
        """
        query = """
        UPDATE application_tracking 
        SET status = %s, last_update = NOW(), notes = %s
        WHERE id = %s
        """
        self.db.execute_query(query, (new_status, notes, application_id))
        
        # Calculer prochaine relance selon statut
        if new_status == 'sent':
            next_followup = datetime.now() + timedelta(days=7)
        elif new_status == 'viewed':
            next_followup = datetime.now() + timedelta(days=3)
        elif new_status == 'interview_scheduled':
            next_followup = None  # Pas de relance
        else:
            next_followup = None
        
        if next_followup:
            query = "UPDATE application_tracking SET next_followup = %s WHERE id = %s"
            self.db.execute_query(query, (next_followup, application_id))
    
    def get_followups_needed(self, user_id):
        """Récupérer les candidatures nécessitant une relance"""
        query = """
        SELECT * FROM application_tracking
        WHERE user_id = %s 
        AND next_followup <= NOW()
        AND status NOT IN ('rejected', 'offer')
        ORDER BY next_followup ASC
        """
        return self.db.execute_query(query, (user_id,), fetch=True)
    
    def get_user_pipeline(self, user_id):
        """Récupérer le pipeline complet de l'utilisateur"""
        query = """
        SELECT 
            status,
            COUNT(*) as count,
            AVG(EXTRACT(EPOCH FROM (NOW() - applied_date))/86400) as avg_days
        FROM application_tracking
        WHERE user_id = %s
        GROUP BY status
        """
        return self.db.execute_query(query, (user_id,), fetch=True)
    
    def get_success_rate(self, user_id):
        """Calculer le taux de succès"""
        query = """
        SELECT 
            COUNT(*) FILTER (WHERE status = 'offer') as offers,
            COUNT(*) FILTER (WHERE status = 'interview_done') as interviews,
            COUNT(*) as total
        FROM application_tracking
        WHERE user_id = %s
        """
        result = self.db.execute_query(query, (user_id,), fetch=True)
        if result:
            offers, interviews, total = result[0]
            return {
                'offer_rate': (offers / total * 100) if total > 0 else 0,
                'interview_rate': (interviews / total * 100) if total > 0 else 0,
                'total_applications': total
            }
        return {'offer_rate': 0, 'interview_rate': 0, 'total_applications': 0}
    
    def generate_followup_message(self, application):
        """Générer un message de relance personnalisé"""
        days_since = (datetime.now() - application['applied_date']).days
        
        if application['status'] == 'sent':
            return f"""Bonjour,

Je me permets de revenir vers vous concernant ma candidature pour le poste de {application['job_title']} envoyée il y a {days_since} jours.

Je reste très intéressé(e) par cette opportunité et serais ravi(e) d'échanger avec vous.

Cordialement"""
        
        elif application['status'] == 'viewed':
            return f"""Bonjour,

Suite à notre dernier échange concernant le poste de {application['job_title']}, je souhaitais savoir où en est le processus de recrutement.

Je reste à votre disposition pour toute information complémentaire.

Cordialement"""
        
        return ""

# SQL pour créer la table
CREATE_TRACKING_TABLE = """
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
);

CREATE INDEX IF NOT EXISTS idx_tracking_user ON application_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_status ON application_tracking(status);
CREATE INDEX IF NOT EXISTS idx_tracking_followup ON application_tracking(next_followup);
"""

tracker = ApplicationTracker()
