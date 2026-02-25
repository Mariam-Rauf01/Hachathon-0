@echo off
REM AI Employee Vault - Complete Startup Guide

echo.
echo ================================================
echo    AI EMPLOYEE VAULT - COMPLETE STARTUP GUIDE
echo ================================================
echo.

echo CURRENT STATUS:
echo - Gmail Watcher: Running (API-based, no browser)
echo - Filesystem Watcher: Running (no browser)
echo - Dashboard Updater: Running (no browser)
echo - LinkedIn Watcher: NOT RUNNING (blocked)
echo - WhatsApp Watcher: NOT RUNNING (blocked)
echo - Orchestrator: NOT RUNNING (blocked)
echo.

echo SERVICES THAT OPEN BROWSERS (BLOCKED):
echo - linkedin_watcher.py - Opens LinkedIn browser
echo - whatsapp_watcher.py - Opens WhatsApp browser
echo - orchestrator.py - May start browser services
echo.

echo SERVICES THAT DON'T OPEN BROWSERS (SAFE):
echo - gmail_watcher.py - Uses Gmail API (no browser)
echo - filesystem_watcher.py - Processes files (no browser)
echo - enhanced_dashboard_updater.py - Updates dashboard (no browser)
echo.

echo TO START SAFE SYSTEM:
echo 1. Run "safe_start.bat" - Starts only safe services
echo.

echo TO STOP ALL SERVICES:
echo 1. Run "stop_targeted_services.bat" - Stops only our services
echo.

echo TO CHECK STATUS:
echo 1. Run "type Dashboard.md" in command prompt
echo 2. Or open Dashboard.md file directly
echo.

echo IMPORTANT:
echo - Do NOT run orchestrator.py directly (starts browser services)
echo - Do NOT run linkedin_watcher.py directly (opens browser)
echo - Do NOT run whatsapp_watcher.py directly (opens browser)
echo - Use safe_start.bat to start system safely
echo.

echo Your dashboard will remain functional and updated!
echo No unwanted browsers will open!
echo.

pause