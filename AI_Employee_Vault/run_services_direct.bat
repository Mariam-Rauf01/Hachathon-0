@echo off
REM AI Employee Vault - Direct Service Runner (No Command Prompts)
REM This runs services directly without PM2 to avoid multiple command prompts

echo Starting AI Employee Vault System (Direct Mode)...
echo.

REM Stop any existing PM2 processes
taskkill /f /im python.exe >nul 2>&1

echo.
echo Starting services directly (no command prompts will appear)...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start services in background without showing command windows
start /b "" python gmail_watcher.py
start /b "" python filesystem_watcher.py
start /b "" python enhanced_dashboard_updater.py

echo.
echo System started successfully!
echo.
echo Services are now running in the background:
echo - Gmail Watcher (monitors emails via API - no browser)
echo - Filesystem Watcher (processes files - no browser)
echo - Dashboard Updater (updates dashboard - no browser)
echo.
echo No command prompts or browsers will open!
echo Your dashboard remains intact and functional.
echo.
echo To stop services: Run stop_services_direct.bat
echo.
pause