@echo off
REM Safe Orchestrator - Prevents Browser Opening Services
REM This starts orchestrator but blocks LinkedIn and WhatsApp watchers

echo Stopping any existing processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *orchestrator*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *linkedin*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *whatsapp*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo Starting orchestrator with browser protections...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start orchestrator in background
start /min "" python orchestrator.py

echo.
echo Orchestrator started with protections:
echo - Gmail Watcher (API-based, no browser)
echo - Reasoning Engine (no browser)
echo - Email Handler (no browser)
echo - Hilt Scheduler (no browser)
echo.
echo LinkedIn and WhatsApp watchers are blocked by resource limits.
echo No browsers should open from orchestrator.
echo.
pause