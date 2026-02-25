@echo off
echo Starting AI Employee Vault System...
echo.

echo Stopping any existing processes...
call pm2 stop all

echo.
echo Starting essential services (no browsers)...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

call pm2 start gmail_watcher.py --name gmail_watcher
call pm2 start filesystem_watcher.py --name filesystem_watcher
call pm2 start enhanced_dashboard_updater.py --name dashboard_updater

echo.
echo System started successfully!
echo.
echo Services running:
echo - Gmail Watcher (monitors emails via API - no browser)
echo - Filesystem Watcher (processes files - no browser) 
echo - Dashboard Updater (updates dashboard - no browser)
echo.
echo No unwanted browsers will open!
echo.
echo To check status: pm2 status
echo To view dashboard: type Dashboard.md
echo.
pause