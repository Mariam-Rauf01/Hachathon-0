@echo off
REM AI Employee Vault - Safe Startup (No Browsers)
REM This starts only safe services that don't open browsers

echo Stopping any existing processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *linkedin*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *whatsapp*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *gmail*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *filesystem*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *dashboard*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *orchestrator*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo Starting safe services (no browsers will open)...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start only safe services that don't open browsers
start /min "" python gmail_watcher.py
timeout /t 1 /nobreak >nul
start /min "" python filesystem_watcher.py
timeout /t 1 /nobreak >nul
start /min "" python enhanced_dashboard_updater.py

echo.
echo Safe system started!
echo.
echo Running services (no browsers):
echo - Gmail Watcher (API-based, no browser)
echo - Filesystem Watcher (no browser)
echo - Dashboard Updater (no browser)
echo.
echo No LinkedIn or WhatsApp browsers will open!
echo Your dashboard remains functional.
echo.
pause