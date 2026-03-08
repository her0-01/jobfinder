"""
NEXUS AGENTIC AI - Web Application Backend
Revolutionary Multi-Agent Workflow System
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO, emit
import requests
import json
import time
import threading
from datetime import datetime
import uuid
import os
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-agentic-ai-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_API_KEY_HERE')
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# AI Agents Configuration
AGENTS = {
    'researcher': {
        'name': 'Researcher',
        'model': 'llama-3.3-70b-versatile',
        'specialty': 'Research & Deep Analysis',
        'icon': '🔬',
        'color': '#3b82f6',
        'prompt_template': '''Tu es un chercheur expert. Fournis des données CONCRÈTES et CHIFFRÉES courtes.

Format de sortie OBLIGATOIRE (MAXIMUM 15 LIGNES):
- 3 statistiques clés avec sources
- 2 chiffres du marché
- 2 tendances avec pourcentages

SOIS BREF. MAXIMUM 250 MOTS.

Tâche: {task}'''
    },
    'writer': {
        'name': 'Writer',
        'model': 'llama-3.1-8b-instant',
        'specialty': 'Content Creation & Storytelling',
        'icon': '✍️',
        'color': '#8b5cf6',
        'prompt_template': '''Tu es un rédacteur professionnel. Crée du contenu PRÊT À PUBLIER.

Format de sortie OBLIGATOIRE:
- Titre accrocheur
- Structure claire (H1, H2, H3)
- Paragraphes courts et percutants
- Call-to-action concret

PAS de blabla. UNIQUEMENT du contenu utilisable immédiatement.

Tâche: {task}'''
    },
    'coder': {
        'name': 'Coder',
        'model': 'llama-3.3-70b-versatile',
        'specialty': 'Code Generation & Debugging',
        'icon': '💻',
        'color': '#10b981',
        'prompt_template': '''Tu es un développeur expert. Génère du CODE FONCTIONNEL uniquement.

Format de sortie OBLIGATOIRE:
- Code complet et exécutable
- Commentaires techniques uniquement
- Gestion d'erreurs incluse
- Exemples d'utilisation

PAS d'explications longues. UNIQUEMENT du code prêt à l'emploi.

Tâche: {task}'''
    },
    'analyst': {
        'name': 'Analyst',
        'model': 'llama-3.1-8b-instant',
        'specialty': 'Data Analysis & Insights',
        'icon': '📊',
        'color': '#f59e0b',
        'prompt_template': '''Tu es un analyste de données. Fournis des ANALYSES QUANTITATIVES courtes.

Format de sortie OBLIGATOIRE (MAXIMUM 15 LIGNES):
- 3 KPIs principaux avec valeurs
- 2 recommandations chiffrées
- 1 tableau simple

SOIS BREF. MAXIMUM 250 MOTS.

Tâche: {task}'''
    },
    'strategist': {
        'name': 'Strategist',
        'model': 'llama-3.3-70b-versatile',
        'specialty': 'Strategy & Planning',
        'icon': '🎯',
        'color': '#ef4444',
        'prompt_template': '''Tu es un stratège business. Crée un PLAN D'ACTION CONCRET court.

Format de sortie OBLIGATOIRE (MAXIMUM 20 LIGNES):
- 3 objectifs SMART
- Timeline (3 étapes max)
- Budget estimé
- 3 métriques de succès

SOIS BREF. MAXIMUM 300 MOTS.

Tâche: {task}'''
    },
    'critic': {
        'name': 'Critic',
        'model': 'llama-3.1-8b-instant',
        'specialty': 'Quality Review & Improvement',
        'icon': '🔍',
        'color': '#ec4899',
        'prompt_template': '''Tu es un auditeur qualité. Fournis une CRITIQUE CONSTRUCTIVE COURTE avec ACTIONS CORRECTIVES.

Format de sortie OBLIGATOIRE (MAXIMUM 10 LIGNES):
- 3 problèmes principaux identifiés
- Impact (Critique/Majeur/Mineur)
- 3 solutions concrètes

SOIS BREF. MAXIMUM 200 MOTS.

Tâche: {task}'''
    }
}

active_workflows = {}
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

def call_ai(model, prompt_template, task, context=""):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_prompt = prompt_template.format(task=task)
    if context:
        full_prompt += f"\n\nContexte des agents précédents:\n{context}"
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Tu es un expert qui génère UNIQUEMENT des livrables concrets et actionnables. AUCUN texte générique ou théorique."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=90)
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "result": result['choices'][0]['message']['content']
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout - Agent trop lent"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agents')
def get_agents():
    return jsonify(AGENTS)

@socketio.on('execute_workflow')
def handle_workflow(data):
    workflow_id = str(uuid.uuid4())
    task = data.get('task')
    selected_agents = data.get('agents', [])
    mode = data.get('mode', 'sequential')
    sid = request.sid
    
    active_workflows[workflow_id] = {
        'status': 'running',
        'results': []
    }
    
    def run_workflow():
        socketio.emit('workflow_started', {'workflow_id': workflow_id}, room=sid)
        
        if mode == 'sequential':
            run_sequential(workflow_id, task, selected_agents, sid)
        elif mode == 'parallel':
            run_parallel(workflow_id, task, selected_agents, sid)
        elif mode == 'debate':
            run_debate(workflow_id, task, selected_agents, sid)
        elif mode == 'hierarchical':
            run_hierarchical(workflow_id, task, selected_agents, sid)
        elif mode == 'autonomous':
            run_autonomous(workflow_id, task, selected_agents, sid)
        
        socketio.emit('workflow_completed', {'workflow_id': workflow_id}, room=sid)
    
    threading.Thread(target=run_workflow, daemon=True).start()

def run_sequential(workflow_id, task, agents, sid):
    context = ""
    for i, agent_key in enumerate(agents):
        agent = AGENTS[agent_key]
        
        socketio.emit('agent_started', {
            'workflow_id': workflow_id,
            'agent': agent_key,
            'step': i + 1,
            'total': len(agents)
        }, room=sid)
        
        start_time = time.time()
        result = call_ai(agent['model'], agent['prompt_template'], task, context)
        duration = time.time() - start_time
        
        if result['success']:
            context += f"\n\n{agent['name']}:\n{result['result']}"
            
            # Sauvegarder le fichier
            file_path = save_agent_output(workflow_id, agent_key, agent['name'], result['result'])
            
            result_data = {
                'agent': agent_key,
                'agent_name': agent['name'],
                'result': result['result'],
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'file_path': str(file_path),
                'file_name': file_path.name
            }
            
            active_workflows[workflow_id]['results'].append(result_data)
            socketio.emit('agent_completed', result_data, room=sid)
        else:
            # En cas d'erreur, envoyer quand même un résultat
            error_msg = f"Erreur: {result.get('error', 'Inconnue')}"
            socketio.emit('agent_completed', {
                'agent': agent_key,
                'agent_name': agent['name'],
                'result': error_msg,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'file_path': None,
                'file_name': None
            }, room=sid)

def run_parallel(workflow_id, task, agents, sid):
    results = []
    threads = []
    
    def execute_agent(agent_key, index):
        agent = AGENTS[agent_key]
        
        socketio.emit('agent_started', {
            'workflow_id': workflow_id,
            'agent': agent_key,
            'step': index + 1,
            'total': len(agents)
        }, room=sid)
        
        start_time = time.time()
        result = call_ai(agent['model'], agent['prompt_template'], task)
        duration = time.time() - start_time
        
        if result['success']:
            file_path = save_agent_output(workflow_id, agent_key, agent['name'], result['result'])
            
            result_data = {
                'agent': agent_key,
                'agent_name': agent['name'],
                'result': result['result'],
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'file_path': str(file_path),
                'file_name': file_path.name
            }
            
            results.append(result_data)
            active_workflows[workflow_id]['results'].append(result_data)
            socketio.emit('agent_completed', result_data, room=sid)
    
    for i, agent_key in enumerate(agents):
        t = threading.Thread(target=execute_agent, args=(agent_key, i))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

def run_debate(workflow_id, task, agents, sid):
    rounds = 2
    context = ""
    
    for round_num in range(rounds):
        for i, agent_key in enumerate(agents):
            agent = AGENTS[agent_key]
            
            socketio.emit('agent_started', {
                'workflow_id': workflow_id,
                'agent': agent_key,
                'round': round_num + 1,
                'step': i + 1,
                'total': len(agents)
            }, room=sid)
            
            start_time = time.time()
            debate_prompt = agent['prompt_template'] + f"\n\nRound {round_num+1}: Améliore et affine ta contribution basée sur les autres agents."
            result = call_ai(agent['model'], debate_prompt, task, context)
            duration = time.time() - start_time
            
            if result['success']:
                context += f"\n\n{agent['name']} (Round {round_num+1}):\n{result['result']}"
                
                file_path = save_agent_output(workflow_id, agent_key, f"{agent['name']}_Round{round_num+1}", result['result'])
                
                result_data = {
                    'agent': agent_key,
                    'agent_name': f"{agent['name']} (Round {round_num+1})",
                    'result': result['result'],
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'file_path': str(file_path),
                    'file_name': file_path.name
                }
                
                active_workflows[workflow_id]['results'].append(result_data)
                socketio.emit('agent_completed', result_data, room=sid)

def run_hierarchical(workflow_id, task, agents, sid):
    socketio.emit('agent_started', {
        'workflow_id': workflow_id,
        'agent': 'strategist',
        'role': 'manager'
    }, room=sid)
    
    manager_prompt = f'''Tu es le chef de projet. Crée un PLAN D'EXÉCUTION DÉTAILLÉ pour coordonner ces experts: {', '.join([AGENTS[a]['name'] for a in agents])}

Format OBLIGATOIRE:
- Décomposition en tâches concrètes
- Attribution à chaque expert
- Dépendances entre tâches
- Timeline

Tâche: {{task}}'''
    
    start_time = time.time()
    result = call_ai(AGENTS['strategist']['model'], manager_prompt, task)
    duration = time.time() - start_time
    
    if result['success']:
        file_path = save_agent_output(workflow_id, 'strategist', 'Manager_Strategist', result['result'])
        
        result_data = {
            'agent': 'strategist',
            'agent_name': 'Manager (Strategist)',
            'result': result['result'],
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'file_path': str(file_path),
            'file_name': file_path.name
        }
        
        active_workflows[workflow_id]['results'].append(result_data)
        socketio.emit('agent_completed', result_data, room=sid)
        
        run_parallel(workflow_id, task, agents, sid)

def run_autonomous(workflow_id, task, agents, sid):
    run_debate(workflow_id, task, agents, sid)

def save_agent_output(workflow_id, agent_key, agent_name, content):
    workflow_dir = OUTPUT_DIR / workflow_id
    workflow_dir.mkdir(exist_ok=True)
    
    # Déterminer l'extension selon le contenu
    if '```python' in content or 'def ' in content or 'import ' in content:
        ext = '.py'
    elif '```javascript' in content or 'function ' in content:
        ext = '.js'
    elif '```html' in content or '<html' in content:
        ext = '.html'
    elif '```json' in content or content.strip().startswith('{'):
        ext = '.json'
    else:
        ext = '.txt'
    
    timestamp = datetime.now().strftime('%H%M%S')
    file_name = f"{timestamp}_{agent_name}{ext}"
    file_path = workflow_dir / file_name
    
    # Nettoyer le contenu des balises markdown
    clean_content = content.replace('```python', '').replace('```javascript', '').replace('```html', '').replace('```json', '').replace('```', '')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    return file_path

@app.route('/download/<workflow_id>/<filename>')
def download_file(workflow_id, filename):
    file_path = OUTPUT_DIR / workflow_id / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True, download_name=filename)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/workflow/<workflow_id>/files')
def get_workflow_files(workflow_id):
    workflow_dir = OUTPUT_DIR / workflow_id
    if not workflow_dir.exists():
        return jsonify({'files': []})
    
    files = [{
        'name': f.name,
        'size': f.stat().st_size,
        'url': f'/download/{workflow_id}/{f.name}'
    } for f in workflow_dir.iterdir() if f.is_file()]
    
    return jsonify({'files': files})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
