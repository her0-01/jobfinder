#!/usr/bin/env python3
"""Test rapide de l'API Groq"""
import os
from groq import Groq

# Récupérer la clé depuis l'env ou config
api_key = os.getenv('GROQ_API_KEY', '')

if not api_key:
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('API', 'groq_api_key', fallback='')

if not api_key:
    print("❌ Pas de clé API Groq trouvée")
    exit(1)

print(f"🔑 Clé API: {api_key[:10]}...")

try:
    print("🚀 Test connexion Groq...")
    client = Groq(api_key=api_key)
    
    print("📤 Envoi requête test...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Dis juste 'OK' si tu me reçois"}],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"✅ Réponse reçue: {result}")
    print("✅ Groq fonctionne parfaitement !")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
