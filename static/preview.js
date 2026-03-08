// Système de prévisualisation avancé v2
class PreviewSystem {
    preview(content, type, agentName) {
        const detectedType = type || this.detectContentType(content);
        
        if (detectedType === 'python' && content.includes('Flask')) {
            this.previewFlaskApp(content, agentName);
        } else if (detectedType === 'python' || detectedType === 'javascript') {
            this.previewCode(content, detectedType, agentName);
        } else if (detectedType === 'html') {
            this.previewHTML(content, agentName);
        } else {
            this.previewText(content, agentName);
        }
    }

    detectContentType(content) {
        if (content.includes('<!DOCTYPE html>') || content.includes('<html')) return 'html';
        if (content.includes('def ') || content.includes('import ')) return 'python';
        if (content.includes('function ') || content.includes('const ')) return 'javascript';
        return 'text';
    }

    previewFlaskApp(code, agentName) {
        const cleanCode = code.replace(/```python/g, '').replace(/```/g, '').trim();
        const w = window.open('', '_blank', 'width=1400,height=900');
        w.document.write(`
<!DOCTYPE html>
<html>
<head>
    <title>Flask App - ${agentName}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #fff; font-family: Arial; display: flex; height: 100vh; }
        .sidebar { width: 50%; background: #1a1a2e; border-right: 2px solid #00ff88; overflow: auto; }
        .demo { width: 50%; background: #0f0f1e; padding: 30px; overflow: auto; }
        .header { background: #00ff88; color: #000; padding: 20px; font-weight: bold; font-size: 18px; }
        pre { padding: 20px; overflow-x: auto; font-size: 12px; line-height: 1.5; }
        .demo-section { background: rgba(0,255,136,0.1); border: 2px solid #00ff88; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .demo-section h3 { color: #00ff88; margin-bottom: 15px; }
        .endpoint { background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #00d4ff; }
        .method { display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; margin-right: 10px; font-size: 12px; }
        .post { background: #10b981; color: #000; }
        .get { background: #3b82f6; }
        .endpoint-path { color: #00d4ff; font-family: monospace; }
        .curl { background: #000; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 11px; overflow-x: auto; }
        .feature { display: flex; align-items: center; gap: 10px; padding: 10px; background: rgba(0,212,255,0.1); border-radius: 8px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="header">💻 CODE SOURCE</div>
        <pre>${cleanCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
    </div>
    <div class="demo">
        <h1 style="color: #00ff88; margin-bottom: 30px;">🚀 API REST - Démo Interactive</h1>
        
        <div class="demo-section">
            <h3>✨ Fonctionnalités</h3>
            <div class="feature">✅ Authentification JWT</div>
            <div class="feature">✅ Base de données SQLite</div>
            <div class="feature">✅ CRUD complet</div>
            <div class="feature">✅ Documentation Swagger</div>
        </div>

        <div class="demo-section">
            <h3>📡 Endpoints disponibles</h3>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-path">/register</span>
                <p style="margin-top: 10px; color: #888;">Inscription d'un nouvel utilisateur</p>
                <div class="curl">curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username":"john","password":"pass123"}'</div>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-path">/login</span>
                <p style="margin-top: 10px; color: #888;">Connexion et obtention du token JWT</p>
                <div class="curl">curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username":"john","password":"pass123"}'</div>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-path">/restaurants</span>
                <p style="margin-top: 10px; color: #888;">Liste des restaurants (auth requise)</p>
                <div class="curl">curl -X GET http://localhost:5000/restaurants -H "Authorization: Bearer YOUR_TOKEN"</div>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-path">/reservations</span>
                <p style="margin-top: 10px; color: #888;">Créer une réservation</p>
                <div class="curl">curl -X POST http://localhost:5000/reservations -H "Authorization: Bearer YOUR_TOKEN" -d '{"restaurant_id":1,"date":"2024-03-16"}'</div>
            </div>
        </div>

        <div class="demo-section">
            <h3>🎯 Pour tester l'API</h3>
            <ol style="line-height: 2; margin-left: 20px;">
                <li>Téléchargez le fichier .py</li>
                <li>Installez: <code style="background: #000; padding: 5px;">pip install flask flask-sqlalchemy flask-jwt-extended flask-swagger-ui</code></li>
                <li>Lancez: <code style="background: #000; padding: 5px;">python app.py</code></li>
                <li>Testez sur http://localhost:5000</li>
            </ol>
        </div>
    </div>
</body>
</html>
        `);
    }

    previewCode(content, language, agentName) {
        const cleanCode = content.replace(/```python/g, '').replace(/```javascript/g, '').replace(/```/g, '').trim();
        const w = window.open('', '_blank', 'width=1200,height=800');
        w.document.write(`
<!DOCTYPE html>
<html>
<head>
    <title>Code - ${agentName}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <style>
        body { margin: 0; background: #1a1a2e; color: #fff; font-family: 'Consolas', monospace; }
        .header { background: #0a0a0a; padding: 20px; border-bottom: 2px solid #00ff88; }
        .code-container { padding: 20px; overflow: auto; height: calc(100vh - 100px); }
        pre { margin: 0; border-radius: 8px; }
        .copy-btn { background: #00ff88; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-left: 20px; }
        .copy-btn:hover { background: #00d4ff; }
    </style>
</head>
<body>
    <div class="header">
        <h2>💻 Code ${language.toUpperCase()} - ${agentName}</h2>
        <button class="copy-btn" onclick="copyCode()">📋 Copier</button>
    </div>
    <div class="code-container">
        <pre><code class="language-${language}">${cleanCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
    </div>
    <script>
        hljs.highlightAll();
        function copyCode() {
            navigator.clipboard.writeText(\`${cleanCode.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`);
            alert('Code copié !');
        }
    </script>
</body>
</html>
        `);
    }

    previewHTML(content, agentName) {
        const cleanHTML = content.replace(/```html/g, '').replace(/```/g, '');
        const w = window.open('', '_blank', 'width=1200,height=800');
        w.document.write(`
<!DOCTYPE html>
<html>
<head>
    <title>Preview - ${agentName}</title>
    <style>
        body { margin: 0; font-family: Arial; }
        .preview-header { background: #1a1a2e; color: #00ff88; padding: 15px; position: sticky; top: 0; z-index: 1000; border-bottom: 2px solid #00ff88; }
    </style>
</head>
<body>
    <div class="preview-header"><h2>🌐 HTML - ${agentName}</h2></div>
    ${cleanHTML}
</body>
</html>
        `);
    }

    previewText(content, agentName) {
        const w = window.open('', '_blank', 'width=1200,height=800');
        w.document.write(`
<!DOCTYPE html>
<html>
<head>
    <title>Preview - ${agentName}</title>
    <style>
        body { margin: 0; background: #1a1a2e; color: #fff; font-family: Arial; }
        .header { background: #0a0a0a; padding: 20px; border-bottom: 2px solid #00ff88; }
        .content { padding: 30px; line-height: 1.8; max-width: 900px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="header"><h2>📄 Document - ${agentName}</h2></div>
    <div class="content"><pre style="white-space: pre-wrap; font-family: inherit;">${content}</pre></div>
</body>
</html>
        `);
    }
}

window.previewSystem = new PreviewSystem();
