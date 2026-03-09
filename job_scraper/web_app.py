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
import configparser
from datetime import datetime
import threading
from functools import wraps

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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

@app.route('/api/scrape', methods=['POST'])
@require_auth
def scrape_jobs():
    username = request.username
    global current_jobs, scraping_status
    
    data = request.json
    keywords = data.get('keywords', 'Data Engineer')
    location = data.get('location', 'France')
    contract_type = data.get('contract_type', 'Alternance')
    
    def run_scraping():
        global current_jobs, scraping_status
        scraping_status = {"running": True, "progress": "Scraping sites d'emploi..."}
        
        try:
            # Sauvegarder la recherche en DB
            search_id = None
            user_id = None
            if use_database:
                # Récupérer user_id depuis username
                from utils.user_manager import UserManager
                um = UserManager()
                result = um.login(username, '')  # Juste pour récupérer user_id
                if result.get('user_id'):
                    user_id = result['user_id']
                    search_id = db_manager.save_job_search(user_id, keywords, location, contract_type)
            
            # Scraping sites carrières avec IA Vision
            adaptive = AdaptiveScraper(headless=True)
            
            # Hook pour mettre à jour le statut
            def update_status(company, index, total, jobs_count):
                global scraping_status
                scraping_status["running"] = True
                scraping_status["progress"] = f"🏢 {company} ({index}/{total}) - {jobs_count} offres trouvées"
            
            adaptive.status_callback = update_status
            corporate_jobs = adaptive.scrape_all_companies(keywords, location, contract_type)
            adaptive.close()
            
            current_jobs.extend(corporate_jobs)
            
            # Dédupliquer
            seen = set()
            unique_jobs = []
            for job in current_jobs:
                key = f"{job['title']}_{job['company']}"
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
                    
                    # Sauvegarder en DB
                    if use_database and search_id and user_id:
                        db_manager.save_job_offer(search_id, user_id, job)
            
            current_jobs = unique_jobs
            
            # Sauvegarder en JSON aussi (fallback)
            with open('data/jobs_latest.json', 'w', encoding='utf-8') as f:
                json.dump(current_jobs, f, ensure_ascii=False, indent=2)
            
            scraping_status = {"running": False, "progress": f"✓ {len(current_jobs)} offres trouvées"}
        except Exception as e:
            scraping_status = {"running": False, "progress": f"❌ Erreur: {str(e)}"}
    
    thread = threading.Thread(target=run_scraping)
    thread.start()
    
    return jsonify({"status": "started"})

@app.route('/api/jobs')
def get_jobs():
    return jsonify(current_jobs)

@app.route('/api/status')
def get_status():
    return jsonify(scraping_status)

@app.route('/api/generate', methods=['POST'])
def generate_application():
    data = request.json
    job_index = data.get('job_index')
    
    if job_index >= len(current_jobs):
        return jsonify({"error": "Job not found"}), 404
    
    job = current_jobs[job_index]
    
    # Charger config
    config = load_config()
    groq = GroqMultiAgentAdapter(config['API']['groq_api_key'])
    profile = dict(config['PROFILE'])
    background = dict(config['BACKGROUND']) if 'BACKGROUND' in config else {}
    
    # Analyser GitHub et Portfolio
    print("  🔍 Analyse GitHub et Portfolio...")
    analyzer = ProfileAnalyzer(profile['github'], profile['portfolio'])
    profile_data = analyzer.get_full_profile()
    profile['analysis'] = profile_data.get('combined_summary', '')
    
    # Charger CV
    cv_path = config['CV_PATH'].get('base_cv', 'data/cv_base.tex')
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_content = f.read()
    
    if cv_path.endswith('.tex'):
        cv_text = LaTeXParser.extract_text(cv_content)
    else:
        cv_text = cv_content
    
    # Charger lettre de base
    letter_path = config['CV_PATH'].get('base_cover_letter', 'data/lettre_motivation_base.txt')
    with open(letter_path, 'r', encoding='utf-8') as f:
        letter_base = f.read()
    
    # Récupérer détails offre
    scraper = UniversalJobScraper(headless=True)
    job['description'] = scraper.get_job_details(job['link'])
    scraper.close()
    
    # Analyser compatibilité
    match = groq.analyze_job_match(cv_text, job['description'])
    
    # Générer CV adapté
    adapted_cv = groq.generate_cv_adaptation(cv_text, job['description'], profile, background)
    
    # Sauvegarder en LaTeX si le CV de base est en LaTeX
    if cv_path.endswith('.tex'):
        # Nettoyer le code LaTeX généré (enlever les balises markdown si présentes)
        adapted_cv = adapted_cv.replace('```latex', '').replace('```', '').strip()
        cv_filename = 'cv_adapted.tex'
    else:
        cv_filename = 'cv_adapted.md'
    
    # Générer lettre
    cover_letter = groq.generate_cover_letter_from_base(job, profile, adapted_cv, letter_base, background)
    
    # Sauvegarder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    company_clean = job['company'].replace(' ', '_')[:30]
    folder = Path(f'data/applications/{timestamp}_{company_clean}')
    folder.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder Markdown ou LaTeX
    with open(folder / cv_filename, 'w', encoding='utf-8') as f:
        f.write(adapted_cv)
    
    with open(folder / 'cover_letter.txt', 'w', encoding='utf-8') as f:
        f.write(cover_letter)
    
    # Générer PDFs
    print("  📄 Génération des PDFs...")
    pdf_gen = PDFGenerator()
    
    # Si LaTeX, compiler directement, sinon convertir depuis Markdown
    if cv_path.endswith('.tex'):
        cv_pdf = pdf_gen.compile_latex_to_pdf(adapted_cv, str(folder / 'cv_adapted.pdf'))
    else:
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
        "is_latex": cv_path.endswith('.tex')
    })

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
    
    # Récupérer config utilisateur depuis DB
    user_config = user_manager.get_user_config(username)
    if not user_config:
        # Scores par défaut si pas de config
        for job in jobs:
            job['relevance_score'] = 50
        return jsonify({'jobs': jobs})
    
    # Récupérer clé API
    api_keys = user_config.get('api_keys', {})
    ai_provider = user_config.get('ai_provider', 'gemini')
    api_key = api_keys.get(ai_provider) or api_keys.get('groq') or api_keys.get('gemini')
    
    if not api_key:
        # Pas de clé API, scores par défaut
        for job in jobs:
            job['relevance_score'] = 50
        return jsonify({'jobs': jobs})
    
    try:
        groq = GroqMultiAgentAdapter(api_key)
        profile = user_config.get('profile', {})
        background = user_config.get('background', {})
        
        # Créer profil candidat pour comparaison
        candidate_profile = "FORMATION: {} -> {}\nSPÉCIALISATION: {}\nCOMPÉTENCES: {}\nPROJETS: {}\nMOTIVATION: {}\nOBJECTIFS: {}".format(
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
                # Utiliser IA pour scorer
                prompt = f"""Analyse la pertinence de cette offre pour ce candidat. Note de 0 à 100.

CANDIDAT:
{candidate_profile}

OFFRE:
Titre: {job['title']}
Entreprise: {job['company']}
Source: {job['source']}

Réponds UNIQUEMENT avec un nombre entre 0 et 100."""
                
                score_text = groq._call_agent(
                    model=groq.models["fast"],
                    system="Tu es un expert en matching candidat/offre. Réponds uniquement avec un nombre.",
                    prompt=prompt,
                    max_tokens=10
                )
                
                # Extraire le score
                import re
                numbers = re.findall(r'\d+', score_text)
                score = int(numbers[0]) if numbers else 50
                score = max(0, min(100, score))
                
                job['relevance_score'] = score
                
            except Exception as e:
                job['relevance_score'] = 50
    
    except Exception as e:
        # Erreur globale, scores par défaut
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


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
