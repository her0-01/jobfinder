@echo off
echo ========================================
echo Installation JobFinder v2.0
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Installation Playwright...
pip install playwright
if %errorlevel% neq 0 (
    echo ERREUR: Installation Playwright echouee
    pause
    exit /b 1
)

echo.
echo [2/2] Installation Chromium...
playwright install chromium
if %errorlevel% neq 0 (
    echo ERREUR: Installation Chromium echouee
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation terminee!
echo ========================================
echo.
echo Pour tester:
echo   python test_system.py
echo.
pause
