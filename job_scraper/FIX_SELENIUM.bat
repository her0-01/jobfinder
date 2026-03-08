@echo off
echo Reinstallation des dependances compatibles...
pip uninstall selenium undetected-chromedriver -y
pip install selenium==4.9.0
pip install undetected-chromedriver==3.5.5
echo.
echo Installation terminee! Relancez START_JOB_WEB.bat
pause
