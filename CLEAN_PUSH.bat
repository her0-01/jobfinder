@echo off
echo ========================================
echo    NETTOYAGE ET PUSH VERS GITHUB
echo ========================================
echo.

echo [1/4] Suppression des cles API du code...
echo Cles API supprimees des fichiers NEXUS_AGENTIC.py et app.py
echo.

echo [2/4] Suppression de l'historique Git...
rd /s /q .git 2>nul
git init
git add .
git commit -m "NEXUS-OS: Multi-User Job Bot - Clean version without API keys"
echo.

echo [3/4] Configuration du remote...
git remote add origin https://github.com/her0-01/jobfinder.git
git branch -M main
echo.

echo [4/4] Push vers GitHub...
echo Une fenetre de connexion GitHub va s'ouvrir
echo Connectez-vous avec le compte her0-01
echo.
git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo    PUSH REUSSI!
    echo ========================================
    echo.
    echo IMPORTANT: Configurez vos variables d'environnement sur Railway:
    echo - GROQ_API_KEY=votre_cle_groq
    echo.
    echo Prochaine etape:
    echo 1. https://railway.app
    echo 2. New Project ^> Deploy from GitHub repo
    echo 3. Selectionnez: her0-01/jobfinder
    echo 4. Ajoutez la variable GROQ_API_KEY dans Settings
    echo.
) else (
    echo.
    echo ========================================
    echo    ERREUR DE PUSH
    echo ========================================
    echo.
)

pause
