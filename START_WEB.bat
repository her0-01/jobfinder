@echo off
echo ========================================
echo   NEXUS AGENTIC AI - Web Application
echo   Revolutionary Multi-Agent System
echo ========================================
echo.
echo Installing dependencies...
pip install flask flask-socketio requests
echo.
echo Starting server...
echo.
echo Open your browser at: http://localhost:5000
echo.
cd /d "%~dp0"
python app.py
pause
