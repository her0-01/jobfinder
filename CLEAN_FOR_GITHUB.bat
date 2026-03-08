@echo off
echo ========================================
echo    NETTOYAGE REPO POUR GITHUB
echo ========================================
echo.

REM Supprimer les logs
echo [1/8] Suppression des logs...
if exist "job_scraper\logs\*.log" del /Q "job_scraper\logs\*.log"

REM Supprimer les fichiers debug HTML
echo [2/8] Suppression fichiers debug...
if exist "job_scraper\debug_*.html" del /Q "job_scraper\debug_*.html"

REM Supprimer les anciennes documentations
echo [3/8] Suppression docs obsoletes...
cd job_scraper
if exist "AMELIORATIONS_IA.md" del /Q "AMELIORATIONS_IA.md"
if exist "CHANGELOG.md" del /Q "CHANGELOG.md"
if exist "COMPATIBILITE_IA.md" del /Q "COMPATIBILITE_IA.md"
if exist "INDEX.md" del /Q "INDEX.md"
if exist "MULTI_AGENTS.md" del /Q "MULTI_AGENTS.md"
if exist "RAPPORT_TESTS.md" del /Q "RAPPORT_TESTS.md"
if exist "RATE_LIMIT_GUIDE.md" del /Q "RATE_LIMIT_GUIDE.md"
if exist "RECAP_FINAL.md" del /Q "RECAP_FINAL.md"
if exist "RESUME_EXPRESS.md" del /Q "RESUME_EXPRESS.md"
if exist "SMART_QUERY_BUILDER.md" del /Q "SMART_QUERY_BUILDER.md"
if exist "TEST_GUIDE.md" del /Q "TEST_GUIDE.md"
cd ..

REM Supprimer les fichiers de test
echo [4/8] Suppression fichiers de test...
cd job_scraper
if exist "test_*.py" del /Q "test_*.py"
if exist "list_*.py" del /Q "list_*.py"
if exist "show_provider.py" del /Q "show_provider.py"
cd ..

REM Supprimer les anciens scrapers
echo [5/8] Suppression anciens fichiers...
if exist "job_scraper\ai_adapters\vision_scraper_old.py" del /Q "job_scraper\ai_adapters\vision_scraper_old.py"
if exist "job_scraper\scrapers\corporate_scraper.py" del /Q "job_scraper\scrapers\corporate_scraper.py"

REM Supprimer les données sensibles
echo [6/8] Nettoyage donnees...
if exist "job_scraper\data\jobs_latest.json" del /Q "job_scraper\data\jobs_latest.json"
if exist "job_scraper\data\test_results.json" del /Q "job_scraper\data\test_results.json"
if exist "job_scraper\data\applications\*" rmdir /S /Q "job_scraper\data\applications"
mkdir "job_scraper\data\applications"

REM Nettoyer config.ini (garder seulement l'exemple)
echo [7/8] Nettoyage config...
if exist "job_scraper\config.ini" (
    echo [API] > job_scraper\config.ini.backup
    echo groq_api_key = YOUR_GROQ_KEY >> job_scraper\config.ini.backup
    echo gemini_api_key = YOUR_GEMINI_KEY >> job_scraper\config.ini.backup
    echo openai_api_key = YOUR_OPENAI_KEY >> job_scraper\config.ini.backup
    echo ai_provider = gemini >> job_scraper\config.ini.backup
)

REM Supprimer les docs racine obsolètes
echo [8/8] Nettoyage racine...
if exist "QUICKSTART.md" del /Q "QUICKSTART.md"
if exist "STRUCTURE.md" del /Q "STRUCTURE.md"

echo.
echo ========================================
echo    NETTOYAGE TERMINE
echo ========================================
echo.
echo Fichiers conserves:
echo   - Code source essentiel
echo   - README.md principal
echo   - README_COMPLET.md (job_scraper)
echo   - requirements.txt
echo   - Scripts de demarrage (.bat)
echo   - Templates et static
echo.
echo Fichiers supprimes:
echo   - Logs (*.log)
echo   - Fichiers debug (debug_*.html)
echo   - Documentations obsoletes
echo   - Fichiers de test
echo   - Donnees sensibles
echo.
pause
