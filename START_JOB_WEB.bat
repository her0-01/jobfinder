@echo off
echo ========================================
echo    JOB APPLICATION BOT - WEB INTERFACE
echo ========================================
echo.

cd job_scraper

echo [1/2] Installation des dependances...
pip install -r requirements.txt --quiet

echo [2/2] Demarrage du serveur web...
echo.
echo Interface disponible sur: http://localhost:5001
echo.
python web_app.py

pause
