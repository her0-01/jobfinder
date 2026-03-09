-- Table des notifications d'alertes (in-app)
CREATE TABLE IF NOT EXISTS alert_notifications (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_title VARCHAR(500),
    job_company VARCHAR(200),
    job_link TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_notifs_user ON alert_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_notifs_read ON alert_notifications(read);

-- Table des alertes
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    keywords VARCHAR(500) NOT NULL,
    location VARCHAR(200),
    contract_type VARCHAR(50),
    frequency VARCHAR(20) DEFAULT 'daily',
    active BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des offres vues par alerte
CREATE TABLE IF NOT EXISTS alert_seen_jobs (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    job_link TEXT NOT NULL,
    seen_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(alert_id, job_link)
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(active);
CREATE INDEX IF NOT EXISTS idx_alert_seen_jobs_alert ON alert_seen_jobs(alert_id);
