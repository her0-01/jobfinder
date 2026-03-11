#!/bin/bash
# Script d'installation pour Railway

echo "Installation des dependances..."
pip install -r requirements.txt

# Essayer d'installer Playwright (optionnel)
echo "Tentative installation Playwright..."
pip install playwright 2>/dev/null && playwright install chromium 2>/dev/null || echo "Playwright non installe, fallback Selenium actif"

echo "Installation terminee"
