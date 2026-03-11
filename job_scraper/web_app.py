from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from scrapers.universal_scraper import UniversalJobScraper
from scrapers.adaptive_scraper import AdaptiveScraper
from scrapers.sota_scraper import SOTAScraper
from ai_adapters.groq_multi_agent import GroqMultiAgentAdapter
from ai_adapters.latex_parser import LaTeXParser
from ai_adapters.profile_analyzer import ProfileAnalyzer
from ai_adapters.pdf_generator import PDFGenerator
from utils.user_manager import UserManager
from utils.database_manager import DatabaseManager
from utils.logger import setup_logger
import configparser
from datetime import datetime
import threading
from functools import wraps

from alert_scheduler import alert_system
from application_tracker import ApplicationTracker
from interview_prep import InterviewPrep
from smart_matcher import SmartMatcher

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Logger
logger = setup_logger('web_app')

# User Manager
user_manager = UserManager()

# Database Manager (si PostgreSQL disponible)
try:
    from utils.database_manager import DatabaseManager
    db_manager = DatabaseManager()
    use_database = True
    print("✅ PostgreSQL connected - Tables initialized")
except Exception as e:
    print(f"⚠️ PostgreSQL not available: {e}")
    db_manager = None
    use_database = False

# État global par utilisateur
user_sessions = {}
current_jobs = []
scraping_status = {"running": False, "progress": ""}

# Rendre scraping_status accessible globalement
import builtins
builtins.scraping_status = scraping_status

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(f"🔐 Auth check - Token: {token[:20]}... exists: {bool(token)}")
        username = user_manager.verify_token(token)
        print(f"🔐 Auth result - Username: {username}")
        
        if not username:
            return jsonify({'error': 'Non autorisé'}), 401
        
        request.username = username
        return f(*args, **kwargs)
    return decorated

def load_config():
    config = configparser.ConfigParser()
    config_path = 'config.ini'
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        # Config par défaut si fichier absent
        config['API'] = {'groq_api_key': os.getenv('GROQ_API_KEY', ''), 'gemini_api_key': os.getenv('GEMINI_API_KEY', ''), 'openai_api_key': os.getenv('OPENAI_API_KEY', '')}
        config['PROFILE'] = {'github': '', 'portfolio': ''}
        config['BACKGROUND'] = {}
        config['CV_PATH'] = {'base_cv': 'data/cv_base.md', 'base_cover_letter': 'data/lettre_motivation_base.txt'}
    return config

# Routes d'authentification
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    result = user_manager.register(
        data.get('username'),
        data.get('password'),
        data.get('email')
    )
    return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    result = user_manager.login(
        data.get('username'),
        data.get('password')
    )
    return jsonify(result)

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = user_manager.logout(token)
    return jsonify(result)

@app.route('/')
def index():
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/config')
def config_page():
    return render_template('config.html')

@app.route('/api/config', methods=['GET', 'POST'])
@require_auth
def manage_config():
    username = request.username
    
    if request.method == 'GET':
        config = user_manager.get_user_config(username)
        if not config:
            # Config par défaut
            config = {
                'api_keys': {'groq': '', 'gemini': '', 'openai': ''},
                'ai_provider': 'gemini',
                'profile': {},
                'background': {}
            }
        return jsonify(config)
    
    else:  # POST
        data = request.json
        result = user_manager.update_user_config(username, data)
        return jsonify(result)

# Variable globale pour contrôler l'arrêt
stop_scraping = False

@app.route('/api/scrape', methods=['POST'])
@require_auth
def scrape_jobs():
    username = request.username
    global current_jobs, scraping_status, stop_scraping
    
    data = request.json
    keywords = data.get('keywords', 'Data Engineer')
    location = data.get('location', 'France')
    contract_type = data.get('contract_type', 'Alternance')
    
    def run_scraping():
        global current_jobs, scraping_status, stop_scraping
        stop_scraping = False
        stop_event = threading.Event()
        
        try:
            # Essayer Playwright d'abord, fallback Selenium si erreur ou 0 résultats
            playwright_success = False
            try:
                scraping_status = {"running": True, "progress": "🚀 Tentative Playwright...", "can_stop": True}
                from orchestrator.auto_learning import AutoLearningOrchestrator
                orchestrator = AutoLearningOrchestrator()
                
                # Passer le stop_flag au scraper Playwright
                orchestrator.scraper.stop_flag = stop_event
                
                # Callback pour progression
                def update_status_playwright(site_name, index, total, jobs_count):
                    global scraping_status, stop_scraping, current_jobs
                    if stop_scraping:
                        stop_event.set()
                    current_jobs = list(orchestrator.scraper.jobs)
                    # Distinguer entreprises (1-15) et sites universels (16-23)
                    icon = "🏢" if index <= 15 else "🌐"
                    scraping_status = {"running": True, "progress": f"{icon} {site_name} ({index}/{total}) • {len(current_jobs)} offres", "can_stop": True}
                
                orchestrator.scraper.status_callback = update_status_playwright
                
                jobs = orchestrator.sync_search(keywords, location, contract_type)
                
                if len(jobs) > 0:
                    current_jobs = jobs
                    playwright_success = True
                    logger.info(f"✅ Playwright: {len(jobs)} offres")
                    
                    # CALCULER LES SCORES POUR PLAYWRIGHT
                    logger.info("🎯 Calcul des scores de pertinence avec IA...")
                    scraping_status = {"running": True, "progress": "🤖 Calcul des scores IA...", "can_stop": False}
                    
                    user_config = user_manager.get_user_config(username)
                    if user_config:
                        api_keys = user_config.get('api_keys', {})
                        api_key = api_keys.get('groq') or api_keys.get('gemini') or api_keys.get('openai')
                        
                        if api_key:
                            try:
                                groq = GroqMultiAgentAdapter(api_key)
                                profile = user_config.get('profile', {})
                                background = user_config.get('background', {})
                                
                                candidate_profile = f"RECHERCHE: {keywords}\nFORMATION: {background.get('formation_actuelle', '')} -> {background.get('formation_visee', '')}\nSPÉCIALISATION: {background.get('specialisation', '')}\nCOMPÉTENCES: {background.get('competences_cles', '')}"
                                
                                # Calculer par batch de 20 avec délai entre batches
                                batch_size = 20
                                for i in range(0, len(current_jobs), batch_size):
                                    batch = current_jobs[i:i+batch_size]
                                    
                                    for j, job in enumerate(batch):
                                        try:
                                            prompt = f"""Analyse la pertinence de cette offre pour ce candidat qui recherche "{keywords}". Note de 0 à 100.\n\nCANDIDAT:\n{candidate_profile}\n\nOFFRE:\nTitre: {job['title']}\nEntreprise: {job['company']}\nSource: {job.get('source', 'N/A')}\n\nCRITÈRES STRICTS:\n- Si le titre de l'offre ne correspond PAS du tout à la recherche: 0-30\n- Si le titre est vaguement lié: 30-50\n- Si le titre est dans le même domaine: 50-70\n- Si le titre correspond bien: 70-85\n- Si le titre correspond parfaitement: 85-100\n\nRéponds UNIQUEMENT avec un nombre entre 0 et 100."""
                                            
                                            score_text = groq._call_agent(
                                                model=groq.models["fast"],
                                                system="Tu es un expert en matching candidat/offre. Réponds uniquement avec un nombre.",
                                                prompt=prompt,
                                                max_tokens=10
                                            )
                                            
                                            import re
                                            numbers = re.findall(r'\d+', score_text)
                                            score = int(numbers[0]) if numbers else 50
                                            score = max(0, min(100, score))
                                            
                                            job['relevance_score'] = score
                                            
                                        except Exception as e:
                                            logger.warning(f"⚠️ Erreur score job {i+j}: {e}")
                                            job['relevance_score'] = 50.0
                                    
                                    # Log progression
                                    logger.info(f"🎯 Scores calculés: {min(i+batch_size, len(current_jobs))}/{len(current_jobs)}")
                                    scraping_status = {"running": True, "progress": f"🤖 Calcul scores: {min(i+batch_size, len(current_jobs))}/{len(current_jobs)}", "can_stop": False}
                                    
                                    # Délai entre batches pour éviter rate limit
                                    if i + batch_size < len(current_jobs):
                                        time.sleep(2)
                                
                                logger.info(f"✅ Scores calculés pour {len(current_jobs)} offres")
                            except Exception as e:
                                logger.error(f"❌ Erreur calcul scores: {e}")
                                for job in current_jobs:
                                    job['relevance_score'] = 50.0
                        else:
                            logger.warning("⚠️ Pas de clé API - scores par défaut")
                            for job in current_jobs:
                                job['relevance_score'] = 50.0
                    else:
                        for job in current_jobs:
                            job['relevance_score'] = 50.0
                else:
                    logger.warning("⚠️ Playwright: 0 résultats, fallback Selenium")
                    raise Exception("No results from Playwright")
            except Exception as playwright_error:
                logger.warning(f"⚠️ Playwright échoué: {playwright_error}, fallback Selenium")
                scraping_status = {"running": True, "progress": "🔄 Fallback Selenium...", "can_stop": True}
            
            if not playwright_success:
                # FALLBACK: Ancien système Selenium
                scraping_status = {"running": True, "progress": "🏢 Scraping sites carrières...", "can_stop": True}
                adaptive = AdaptiveScraper(headless=True)
                
                def update_status(company, index, total, jobs_count):
                    global scraping_status, stop_scraping, current_jobs
                    if stop_scraping:
                        stop_event.set()
                    current_jobs = list(adaptive.jobs)
                    scraping_status = {"running": True, "progress": f"🏢 {company} ({index}/15) • {len(current_jobs)} offres", "can_stop": True}
                
                adaptive.status_callback = update_status
                adaptive.stop_flag = stop_event
                corporate_jobs = adaptive.scrape_all_companies(keywords, location, contract_type)
                adaptive.close()
                current_jobs = list(corporate_jobs) if corporate_jobs else []
                
                if not stop_event.is_set():
                    from scrapers.universal_scraper import UniversalJobScraper
                    scraping_status = {"running": True, "progress": "🌐 Scraping sites universels...", "can_stop": True}
                    universal = UniversalJobScraper(headless=True)
                    
                    def update_status_universal(site, index, total, jobs_count):
                        global scraping_status, stop_scraping, current_jobs
                        if stop_scraping:
                            stop_event.set()
                        current_jobs = list(adaptive.jobs) + list(universal.jobs)
                        total_progress = 15 + index
                        scraping_status = {"running": True, "progress": f"🌐 {site} ({total_progress}/23) • {len(current_jobs)} offres", "can_stop": True}
                    
                    universal.status_callback = update_status_universal
                    universal.stop_flag = stop_event
                    universal_jobs = universal.scrape_all(keywords, location, contract_type)
                    universal.close()
                    
                    if universal_jobs:
                        current_jobs.extend(universal_jobs)
                
                # Dédupliquer
                seen = set()
                unique_jobs = []
                for job in current_jobs:
                    key = f"{job['title']}_{job['company']}"
                    if key not in seen:
                        seen.add(key)
                        unique_jobs.append(job)
                
                current_jobs = unique_jobs
                logger.info(f"✅ Selenium fallback: {len(current_jobs)} offres")
            
            # CALCULER LES SCORES UNIQUEMENT SI PAS DÉJÀ FAIT (fallback Selenium)
            if not playwright_success:
                logger.info("🎯 Calcul des scores de pertinence avec IA...")
                scraping_status = {"running": True, "progress": "🤖 Calcul des scores IA...", "can_stop": False}
                
                # Récupérer config utilisateur pour l'IA
                user_config = user_manager.get_user_config(username)
                if user_config:
                    api_keys = user_config.get('api_keys', {})
                    api_key = api_keys.get('groq') or api_keys.get('gemini') or api_keys.get('openai')
                    
                    if api_key:
                        try:
                            groq = GroqMultiAgentAdapter(api_key)
                            profile = user_config.get('profile', {})
                            background = user_config.get('background', {})
                            
                            candidate_profile = f"RECHERCHE: {keywords}\nFORMATION: {background.get('formation_actuelle', '')} -> {background.get('formation_visee', '')}\nSPÉCIALISATION: {background.get('specialisation', '')}\nCOMPÉTENCES: {background.get('competences_cles', '')}"
                            
                            # Calculer par batch de 20 avec délai entre batches
                            batch_size = 20
                            for i in range(0, len(current_jobs), batch_size):
                                batch = current_jobs[i:i+batch_size]
                                
                                for j, job in enumerate(batch):
                                    try:
                                        prompt = f"""Analyse la pertinence de cette offre pour ce candidat qui recherche "{keywords}". Note de 0 à 100.\n\nCANDIDAT:\n{candidate_profile}\n\nOFFRE:\nTitre: {job['title']}\nEntreprise: {job['company']}\nSource: {job['source']}\n\nCRITÈRES STRICTS:\n- Si le titre de l'offre ne correspond PAS du tout à la recherche: 0-30\n- Si le titre est vaguement lié: 30-50\n- Si le titre est dans le même domaine: 50-70\n- Si le titre correspond bien: 70-85\n- Si le titre correspond parfaitement: 85-100\n\nRéponds UNIQUEMENT avec un nombre entre 0 et 100."""
                                        
                                        score_text = groq._call_agent(
                                            model=groq.models["fast"],
                                            system="Tu es un expert en matching candidat/offre. Réponds uniquement avec un nombre.",
                                            prompt=prompt,
                                            max_tokens=10
                                        )
                                        
                                        import re
                                        numbers = re.findall(r'\d+', score_text)
                                        score = int(numbers[0]) if numbers else 50
                                        score = max(0, min(100, score))
                                        
                                        job['relevance_score'] = score
                                        
                                    except Exception as e:
                                        logger.warning(f"⚠️ Erreur score job {i+j}: {e}")
                                        job['relevance_score'] = 50.0
                                
                                # Log progression
                                logger.info(f"🎯 Scores calculés: {min(i+batch_size, len(current_jobs))}/{len(current_jobs)}")
                                scraping_status = {"running": True, "progress": f"🤖 Calcul scores: {min(i+batch_size, len(current_jobs))}/{len(current_jobs)}", "can_stop": False}
                                
                                # Délai entre batches pour éviter rate limit
                                if i + batch_size < len(current_jobs):
                                    time.sleep(2)
                            
                            logger.info(f"✅ Scores calculés pour {len(current_jobs)} offres")
                        except Exception as e:
                            logger.error(f"❌ Erreur calcul scores: {e}")
                            for job in current_jobs:
                                job['relevance_score'] = 50.0
                    else:
                        logger.warning("⚠️ Pas de clé API - scores par défaut")
                        for job in current_jobs:
                            job['relevance_score'] = 50.0
                else:
                    for job in current_jobs:
                        job['relevance_score'] = 50.0
            
            # Sauvegarder en DB
            if use_database:
                user_config = user_manager.get_user_config(username)
                if user_config and 'user_id' in user_config:
                    user_id = user_config['user_id']
                    search_id = db_manager.save_job_search(user_id, keywords, location, contract_type)
                    
                    # Sauvegarder chaque offre avec son score
                    for job in current_jobs:
                        # S'assurer que le score est présent
                        if 'relevance_score' not in job or job['relevance_score'] is None:
                            job['relevance_score'] = 50.0
                        
                        db_manager.save_job_offer(search_id, user_id, job)
                    
                    logger.info(f"✅ Sauvegardé en DB: {len(current_jobs)} offres avec scores")
            
            # Sauvegarder JSON
            with open('data/jobs_latest.json', 'w', encoding='utf-8') as f:
                json.dump(current_jobs, f, ensure_ascii=False, indent=2)
            
            scraping_status = {"running": False, "progress": f"✅ {len(current_jobs)} offres trouvées", "can_stop": False}
        
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            scraping_status = {"running": False, "progress": f"❌ Erreur: {str(e)}", "can_stop": False}
    
    thread = threading.Thread(target=run_scraping)
    thread.start()
    
    return jsonify({"status": "started"})

@app.route('/api/scrape/stop', methods=['POST'])
@require_auth
def stop_scrape():
    global stop_scraping
    stop_scraping = True
    return jsonify({"status": "stopping"})

@app.route('/api/jobs')
@require_auth
def get_jobs():
    return jsonify(current_jobs)

@app.route('/api/searches')
@require_auth
def get_searches():
    username = request.username
    if not use_database:
        return jsonify([])
    
    # Récupérer user_id depuis la DB
    user_config = user_manager.get_user_config(username)
    if not user_config or 'user_id' not in user_config:
        return jsonify([])
    
    user_id = user_config['user_id']
    searches = db_manager.get_user_searches(user_id)
    return jsonify(searches)

@app.route('/api/search/<int:search_id>/jobs')
@require_auth
def get_search_jobs(search_id):
    global current_jobs
    if not use_database:
        return jsonify([])
    
    jobs = db_manager.get_search_jobs(search_id)
    
    # Log pour déboguer
    logger.info(f"📊 Chargement recherche {search_id}: {len(jobs)} offres")
    if jobs:
        logger.info(f"🎯 Scores: {[j.get('relevance_score', 'N/A') for j in jobs[:5]]}")
    
    current_jobs = jobs  # Charger dans la session
    return jsonify(jobs)

@app.route('/api/status')
def get_status():
    return jsonify(scraping_status)

@app.route('/api/generate', methods=['POST'])
@require_auth
def generate_application():
    username = request.username
    data = request.json
    job_index = data.get('job_index')
    
    if job_index >= len(current_jobs):
        return jsonify({"error": "Job not found"}), 404
    
    job = current_jobs[job_index]
    
    # Récupérer config utilisateur
    user_config = user_manager.get_user_config(username)
    if not user_config:
        return jsonify({"error": "Configuration utilisateur manquante"}), 400
    
    # Récupérer clé API
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini') or api_keys.get('openai')
    
    if not api_key:
        return jsonify({"error": "Clé API manquante. Configurez-la dans Configuration."}), 400
    
    # Récupérer CV et lettre depuis la BD
    cv_content = user_config.get('cv_content')
    letter_base = user_config.get('cover_letter_template')
    
    if not cv_content:
        return jsonify({"error": "CV manquant. Ajoutez votre CV dans Configuration."}), 400
    
    if not letter_base:
        letter_base = "Je suis très intéressé(e) par ce poste."
    
    try:
        groq = GroqMultiAgentAdapter(api_key)
        profile = user_config.get('profile', {})
        background = user_config.get('background', {})
        
        # Analyser compatibilité
        match = groq.analyze_job_match(cv_content, job.get('description', job['title']))
        
        # Générer CV adapté
        adapted_cv = groq.generate_cv_adaptation(cv_content, job.get('description', job['title']), profile, background)
        
        # Générer lettre
        cover_letter = groq.generate_cover_letter_from_base(job, profile, adapted_cv, letter_base, background)
        
        # Sauvegarder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_clean = job['company'].replace(' ', '_')[:30]
        folder = Path(f'data/applications/{timestamp}_{company_clean}')
        folder.mkdir(parents=True, exist_ok=True)
        
        with open(folder / 'cv_adapted.md', 'w', encoding='utf-8') as f:
            f.write(adapted_cv)
        
        with open(folder / 'cover_letter.txt', 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        # Générer PDFs
        pdf_gen = PDFGenerator()
        cv_pdf = pdf_gen.generate_cv_pdf(adapted_cv, str(folder / 'cv_adapted.pdf'))
        letter_pdf = pdf_gen.generate_letter_pdf(cover_letter, profile, str(folder / 'cover_letter.pdf'))
        
        with open(folder / 'job_info.json', 'w', encoding='utf-8') as f:
            json.dump({
                'job': job,
                'match_analysis': match,
                'generated_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "folder": str(folder.name),
            "match_score": match.get('score', 0),
            "cv": adapted_cv,
            "letter": cover_letter,
            "is_latex": False
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/applications')
def list_applications():
    apps_dir = Path('data/applications')
    if not apps_dir.exists():
        return jsonify([])
    
    applications = []
    for folder in sorted(apps_dir.iterdir(), reverse=True):
        if folder.is_dir():
            info_file = folder / 'job_info.json'
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    applications.append({
                        'folder': folder.name,
                        'company': info['job']['company'],
                        'title': info['job']['title'],
                        'score': info['match_analysis'].get('score', 0),
                        'date': info['generated_at']
                    })
    
    return jsonify(applications)

@app.route('/api/application/<folder_name>')
def get_application(folder_name):
    folder = Path(f'data/applications/{folder_name}')
    
    # Détecter le type de CV
    cv_file = folder / 'cv_adapted.tex' if (folder / 'cv_adapted.tex').exists() else folder / 'cv_adapted.md'
    
    with open(cv_file, 'r', encoding='utf-8') as f:
        cv = f.read()
    
    with open(folder / 'cover_letter.txt', 'r', encoding='utf-8') as f:
        letter = f.read()
    
    with open(folder / 'job_info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    return jsonify({
        'cv': cv,
        'letter': letter,
        'info': info,
        'is_latex': cv_file.suffix == '.tex'
    })

@app.route('/api/calculate-relevance', methods=['POST'])
@require_auth
def calculate_relevance():
    username = request.username
    data = request.json
    jobs = data.get('jobs', [])
    search_keywords = data.get('keywords', '')  # Mots-clés de recherche
    
    # Récupérer config utilisateur depuis DB
    user_config = user_manager.get_user_config(username)
    if not user_config:
        for job in jobs:
            job['relevance_score'] = 50
        return jsonify({'jobs': jobs})
    
    # Récupérer clé API
    api_keys = user_config.get('api_keys', {})
    ai_provider = user_config.get('ai_provider', 'gemini')
    api_key = api_keys.get(ai_provider) or api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        for job in jobs:
            job['relevance_score'] = 50
        return jsonify({'jobs': jobs})
    
    try:
        groq = GroqMultiAgentAdapter(api_key)
        profile = user_config.get('profile', {})
        background = user_config.get('background', {})
        
        # Créer profil candidat
        candidate_profile = "RECHERCHE: {}\nFORMATION: {} -> {}\nSPÉCIALISATION: {}\nCOMPÉTENCES: {}\nPROJETS: {}\nMOTIVATION: {}\nOBJECTIFS: {}".format(
            search_keywords,
            background.get('formation_actuelle', ''),
            background.get('formation_visee', ''),
            background.get('specialisation', ''),
            background.get('competences_cles', ''),
            background.get('projets_majeurs', ''),
            background.get('motivation', ''),
            background.get('objectifs', '')
        )
        
        # Calculer score pour chaque offre
        for job in jobs:
            try:
                prompt = f"""Analyse la pertinence de cette offre pour ce candidat qui recherche "{search_keywords}". Note de 0 à 100.

CANDIDAT:
{candidate_profile}

OFFRE:
Titre: {job['title']}
Entreprise: {job['company']}
Source: {job['source']}

CRITÈRES STRICTS:
- Si le titre de l'offre ne correspond PAS du tout à la recherche: 0-30
- Si le titre est vaguement lié: 30-50
- Si le titre est dans le même domaine: 50-70
- Si le titre correspond bien: 70-85
- Si le titre correspond parfaitement: 85-100

Réponds UNIQUEMENT avec un nombre entre 0 et 100."""
                
                score_text = groq._call_agent(
                    model=groq.models["fast"],
                    system="Tu es un expert en matching candidat/offre. Réponds uniquement avec un nombre.",
                    prompt=prompt,
                    max_tokens=10
                )
                
                import re
                numbers = re.findall(r'\d+', score_text)
                score = int(numbers[0]) if numbers else 50
                score = max(0, min(100, score))
                
                job['relevance_score'] = score
                
            except Exception as e:
                job['relevance_score'] = 50
    
    except Exception as e:
        for job in jobs:
            job['relevance_score'] = 50
    
    # Trier par score
    jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return jsonify({'jobs': jobs})

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    data = request.json
    folder_name = data.get('folder')
    message = data.get('message')
    history = data.get('history', [])
    
    folder = Path(f'data/applications/{folder_name}')
    
    # Charger les documents actuels
    with open(folder / 'cv_adapted.md', 'r', encoding='utf-8') as f:
        cv = f.read()
    
    with open(folder / 'cover_letter.txt', 'r', encoding='utf-8') as f:
        letter = f.read()
    
    # Charger config
    config = load_config()
    groq = GroqMultiAgentAdapter(config['API']['groq_api_key'])
    
    # Construire le contexte
    context = f"""CV ACTUEL:
{cv[:1000]}

LETTRE ACTUELLE:
{letter[:1000]}

HISTORIQUE CONVERSATION:
{json.dumps(history[-3:], ensure_ascii=False)}
"""
    
    # Appeler l'IA
    response = groq._call_agent(
        model=groq.models["creative"],
        system="Tu es un assistant qui aide à améliorer des CV et lettres de motivation. Tu écoutes les demandes et proposes des modifications précises.",
        prompt=f"""{context}

DEMANDE UTILISATEUR: {message}

Réponds de manière concise et propose des modifications si nécessaire. Si l'utilisateur demande une modification, génère le nouveau contenu.""",
        max_tokens=1000
    )
    
    # Détecter si modification demandée
    updated_cv = None
    updated_letter = None
    
    if any(word in message.lower() for word in ['modifie', 'change', 'améliore', 'réécris', 'refais']):
        if 'cv' in message.lower():
            # Régénérer CV
            updated_cv = groq._call_agent(
                model=groq.models["balanced"],
                system="Tu es un expert en CV.",
                prompt=f"""CV ACTUEL:
{cv}

MODIFICATION DEMANDÉE: {message}

Génère le CV modifié en Markdown:""",
                max_tokens=2000
            )
            
            # Sauvegarder
            with open(folder / 'cv_adapted.md', 'w', encoding='utf-8') as f:
                f.write(updated_cv)
        
        if 'lettre' in message.lower():
            # Régénérer lettre
            updated_letter = groq._call_agent(
                model=groq.models["creative"],
                system="Tu es un expert en lettres de motivation. Écris comme un HUMAIN.",
                prompt=f"""LETTRE ACTUELLE:
{letter}

MODIFICATION DEMANDÉE: {message}

Génère la lettre modifiée:""",
                max_tokens=1000
            )
            
            # Sauvegarder
            with open(folder / 'cover_letter.txt', 'w', encoding='utf-8') as f:
                f.write(updated_letter)
    
    return jsonify({
        'response': response,
        'updated_cv': updated_cv,
        'updated_letter': updated_letter
    })

@app.route('/api/download/<folder_name>/<doc_type>')
def download_pdf(folder_name, doc_type):
    folder = Path(f'data/applications/{folder_name}')
    
    if doc_type == 'cv':
        file_path = folder / 'cv_adapted.pdf'
    elif doc_type == 'letter':
        file_path = folder / 'cover_letter.pdf'
    else:
        return jsonify({"error": "Invalid type"}), 400
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

# Nouvelles routes pour historique et statistiques
@app.route('/api/history/searches')
@require_auth
def get_search_history():
    """Récupère l'historique des recherches"""
    if not use_database:
        return jsonify([])
    
    username = request.username
    config = user_manager.get_user_config(username)
    user_id = config.get('user_id', 1)
    
    # TODO: Implémenter get_user_searches dans DatabaseManager
    return jsonify([])

@app.route('/api/history/offers')
@require_auth
def get_offers_history():
    """Récupère l'historique des offres trouvées"""
    if not use_database:
        return jsonify([])
    
    username = request.username
    config = user_manager.get_user_config(username)
    user_id = config.get('user_id', 1)
    
    offers = db_manager.get_user_job_offers(user_id, limit=100)
    return jsonify(offers)

@app.route('/api/history/applications')
@require_auth
def get_applications_history():
    """Récupère l'historique des candidatures"""
    if not use_database:
        return jsonify([])
    
    username = request.username
    config = user_manager.get_user_config(username)
    user_id = config.get('user_id', 1)
    
    applications = db_manager.get_user_applications(user_id, limit=50)
    return jsonify(applications)

@app.route('/api/stats')
@require_auth
def get_user_stats():
    """Statistiques utilisateur"""
    if not use_database:
        return jsonify({
            'total_searches': 0,
            'total_offers': 0,
            'total_applications': 0,
            'avg_relevance_score': 0
        })
    
    username = request.username
    config = user_manager.get_user_config(username)
    user_id = config.get('user_id', 1)
    
    offers = db_manager.get_user_job_offers(user_id, limit=1000)
    applications = db_manager.get_user_applications(user_id, limit=1000)
    
    avg_score = sum(o.get('relevance_score', 0) for o in offers) / len(offers) if offers else 0
    
    return jsonify({
        'total_searches': len(set(o.get('search_id') for o in offers)),
        'total_offers': len(offers),
        'total_applications': len(applications),
        'avg_relevance_score': round(avg_score, 1),
        'top_companies': _get_top_companies(offers),
        'top_sources': _get_top_sources(offers)
    })

def _get_top_companies(offers):
    """Top 5 entreprises"""
    from collections import Counter
    companies = [o.get('company') for o in offers if o.get('company')]
    return [{'name': c, 'count': count} for c, count in Counter(companies).most_common(5)]

def _get_top_sources(offers):
    """Top 5 sources"""
    from collections import Counter
    sources = [o.get('source_site') for o in offers if o.get('source_site')]
    return [{'name': s, 'count': count} for s, count in Counter(sources).most_common(5)]

# Routes pour Application Tracking
@app.route('/api/tracking/applications', methods=['GET'])
@require_auth
def get_tracking_applications():
    username = request.username
    user_config = user_manager.get_user_config(username)
    user_id = user_config.get('user_id', 1)
    
    tracker = ApplicationTracker()
    
    # Récupérer toutes les candidatures
    query = "SELECT * FROM application_tracking WHERE user_id = %s ORDER BY applied_date DESC"
    apps = tracker.db.execute_query(query, (user_id,), fetch=True)
    
    return jsonify([{
        'id': a[0],
        'job_title': a[2],
        'company': a[3],
        'applied_date': str(a[4]),
        'status': a[5],
        'last_update': str(a[6]),
        'next_followup': str(a[7]) if a[7] else None,
        'notes': a[8]
    } for a in apps])

@app.route('/api/tracking/add', methods=['POST'])
@require_auth
def add_tracking():
    username = request.username
    user_config = user_manager.get_user_config(username)
    user_id = user_config.get('user_id', 1)
    
    data = request.json
    tracker = ApplicationTracker()
    
    from datetime import datetime
    app_id = tracker.add_application(
        user_id,
        data['job_title'],
        data['company'],
        datetime.now(),
        data.get('status', 'sent')
    )
    
    return jsonify({'success': True, 'id': app_id})

@app.route('/api/tracking/update/<int:app_id>', methods=['POST'])
@require_auth
def update_tracking(app_id):
    data = request.json
    tracker = ApplicationTracker()
    tracker.update_status(app_id, data['status'], data.get('notes', ''))
    return jsonify({'success': True})

@app.route('/api/tracking/followups', methods=['GET'])
@require_auth
def get_followups():
    username = request.username
    user_config = user_manager.get_user_config(username)
    user_id = user_config.get('user_id', 1)
    
    tracker = ApplicationTracker()
    followups = tracker.get_followups_needed(user_id)
    
    return jsonify([{
        'id': f[0],
        'job_title': f[2],
        'company': f[3],
        'applied_date': str(f[4]),
        'next_followup': str(f[7]),
        'message': tracker.generate_followup_message({
            'job_title': f[2],
            'applied_date': f[4],
            'status': f[5]
        })
    } for f in followups])

@app.route('/api/tracking/pipeline', methods=['GET'])
@require_auth
def get_pipeline():
    username = request.username
    user_config = user_manager.get_user_config(username)
    user_id = user_config.get('user_id', 1)
    
    tracker = ApplicationTracker()
    pipeline = tracker.get_user_pipeline(user_id)
    success_rate = tracker.get_success_rate(user_id)
    
    return jsonify({
        'pipeline': [{'status': p[0], 'count': p[1], 'avg_days': float(p[2]) if p[2] else 0} for p in pipeline],
        'success_rate': success_rate
    })

# Routes pour Interview Prep
@app.route('/api/interview/questions', methods=['POST'])
@require_auth
def get_interview_questions():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    prep = InterviewPrep(api_key)
    questions = prep.generate_interview_questions(
        data['job_title'],
        data['company'],
        data.get('job_description', '')
    )
    
    return jsonify({'questions': questions})

@app.route('/api/interview/answer-tips', methods=['POST'])
@require_auth
def get_answer_tips():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    prep = InterviewPrep(api_key)
    tips = prep.generate_answer_tips(
        data['question'],
        data.get('user_profile', ''),
        data.get('job_description', '')
    )
    
    return jsonify({'tips': tips})

@app.route('/api/interview/company-analysis', methods=['POST'])
@require_auth
def analyze_company():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    prep = InterviewPrep(api_key)
    analysis = prep.analyze_company(data['company'])
    
    return jsonify({'analysis': analysis})

@app.route('/api/interview/questions-to-ask', methods=['POST'])
@require_auth
def get_questions_to_ask():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    prep = InterviewPrep(api_key)
    questions = prep.generate_questions_to_ask(data['job_title'], data['company'])
    
    return jsonify({'questions': questions})

@app.route('/api/interview/elevator-pitch', methods=['POST'])
@require_auth
def get_elevator_pitch():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    prep = InterviewPrep(api_key)
    pitch = prep.generate_elevator_pitch(data.get('user_profile', ''), data['job_title'])
    
    return jsonify({'pitch': pitch})

# Routes pour Smart Matcher
@app.route('/api/matcher/skill-gap', methods=['POST'])
@require_auth
def analyze_skill_gap():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    analysis = matcher.analyze_skill_gap(data['cv'], data['job_description'])
    
    return jsonify({'analysis': analysis})

@app.route('/api/matcher/learning-path', methods=['POST'])
@require_auth
def get_learning_path():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    plan = matcher.suggest_learning_path(data['missing_skills'], data['job_title'])
    
    return jsonify({'plan': plan})

@app.route('/api/matcher/alternative-jobs', methods=['POST'])
@require_auth
def get_alternative_jobs():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    alternatives = matcher.find_alternative_jobs(data['cv'], data['target_job'])
    
    return jsonify({'alternatives': alternatives})

@app.route('/api/matcher/optimize-cv', methods=['POST'])
@require_auth
def optimize_cv():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    optimization = matcher.optimize_cv_for_job(data['cv'], data['job_description'])
    
    return jsonify({'optimization': optimization})

@app.route('/api/matcher/salary-estimate', methods=['POST'])
@require_auth
def estimate_salary():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    salary_info = matcher.calculate_realistic_salary(
        data['job_title'],
        data['location'],
        data.get('experience_years', 0)
    )
    
    return jsonify({'salary_info': salary_info})

@app.route('/api/matcher/red-flags', methods=['POST'])
@require_auth
def detect_red_flags():
    username = request.username
    user_config = user_manager.get_user_config(username)
    api_keys = user_config.get('api_keys', {})
    api_key = api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        return jsonify({'error': 'Clé API manquante'}), 400
    
    data = request.json
    matcher = SmartMatcher(api_key)
    analysis = matcher.detect_red_flags(data['job_description'], data['company'])
    
    return jsonify({'analysis': analysis})

# Ajouter Playwright aux requirements
# pip install playwright
# playwright install chromium

if __name__ == '__main__':
    # Démarrer le système d'alertes en arrière-plan
    alert_system.start_background_checker()
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
