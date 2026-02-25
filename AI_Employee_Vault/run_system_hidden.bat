@echo off
REM Batch file to run AI Employee Vault services in background without showing command prompts

echo Stopping any existing processes...
FOR /F "tokens=1,2 delims= " %%i in ('pm2 jlist ^| findstr "gmail_watcher\|filesystem_watcher\|dashboard_updater" ^| findstr "online"') do (
    pm2 stop %%j
)

echo.
echo Starting services in background...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start services in background without showing command windows
start /min "" cmd /c pm2 start gmail_watcher.py --name gmail_watcher >nul 2>&1
timeout /t 2 /nobreak >nul
start /min "" cmd /c pm2 start filesystem_watcher.py --name filesystem_watcher >nul 2>&1
timeout /t 2 /nobreak >nul
start /min "" cmd /c pm2 start enhanced_dashboard_updater.py --name dashboard_updater >nul 2>&1

echo.
echo System started in background!
echo.
echo Services are running without visible command prompts.
echo No browsers will open for Gmail, WhatsApp, or LinkedIn.
echo.
echo To check status: Open command prompt and run "pm2 status"
echo To view dashboard: Open command prompt and run "type Dashboard.md"
echo.
echo System will continue running in background until you stop it.
echo.
pause