#!/bin/bash
set -e

echo "🔧 Installing Playwright browsers..."
playwright install chromium || echo "⚠️ Playwright install failed, using Selenium fallback"

echo "🚀 Starting application..."
python web_app.py
