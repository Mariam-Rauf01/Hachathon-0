@echo off
REM AI Employee Vault - Prevent Browser Services
REM This ensures no browser-opening services start

echo Ensuring no browser services are running...
echo.

REM Stop any existing orchestrator, linkedin, or whatsapp processes
taskkill /f /im python.exe /fi "WINDOWTITLE eq *orchestrator*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *linkedin*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *whatsapp*" >nul 2>&1

echo.
echo Blocked services (will not start):
echo - orchestrator.py (contains LinkedIn/WhatsApp watchers)
echo - linkedin_watcher.py (opens LinkedIn browser)
echo - whatsapp_watcher.py (opens WhatsApp browser)
echo.
echo Allowed services (safe to run):
echo - gmail_watcher.py (uses API, no browser)
echo - filesystem_watcher.py (no browser)
echo - enhanced_dashboard_updater.py (no browser)
echo.
echo To start safe services, run: safe_start.bat
echo.
pause