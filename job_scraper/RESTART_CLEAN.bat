@echo off
echo Nettoyage cache Python...
del /s /q *.pyc 2>nul
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

echo Arret processus Python...
taskkill /F /IM python.exe 2>nul

echo Attente 3 secondes...
timeout /t 3 /nobreak >nul

echo Demarrage serveur Flask...
python web_app.py

pause
