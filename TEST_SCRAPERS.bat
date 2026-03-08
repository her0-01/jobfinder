@echo off
echo ========================================
echo    TEST AUTOMATIQUE DES SCRAPERS
echo ========================================
echo.

cd job_scraper

echo Lancement des tests...
echo.
python test_scrapers.py

echo.
echo ========================================
echo    Tests termines
echo ========================================
pause
