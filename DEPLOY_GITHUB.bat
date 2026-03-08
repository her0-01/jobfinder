@echo off
echo ========================================
echo    DEPLOIEMENT VERS GITHUB
echo ========================================
echo.

REM Etape 1: Nettoyage
echo [1/4] Nettoyage du repo...
call CLEAN_FOR_GITHUB.bat

REM Etape 2: Git init
echo.
echo [2/4] Initialisation Git...
git init
git add .
git commit -m "NEXUS-OS: Multi-User Job Bot with SOTA Scraper - AI-powered job application automation"

REM Etape 3: Push vers GitHub
echo.
echo [3/4] Push vers GitHub (her0-01/jobfinder)...
git remote add origin https://github.com/her0-01/jobfinder.git
git branch -M main
git push -u origin main --force

REM Etape 4: Railway
echo.
echo [4/4] Deploiement Railway
echo ========================================
echo.
echo 1. Allez sur: https://railway.app
echo 2. Connectez-vous avec GitHub
echo 3. New Project > Deploy from GitHub repo
echo 4. Selectionnez: her0-01/jobfinder
echo 5. Railway deploie automatiquement
echo.
echo ========================================
echo    DEPLOIEMENT TERMINE
echo ========================================
echo.
pause
