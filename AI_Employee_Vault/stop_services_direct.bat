@echo off
REM AI Employee Vault - Stop Direct Services
REM This stops the directly running services

echo Stopping AI Employee Vault services...
echo.

REM Kill the Python processes for our services
taskkill /f /im python.exe /fi "WINDOWTITLE eq *gmail_watcher*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *filesystem_watcher*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *enhanced_dashboard_updater*" >nul 2>&1

REM Alternative: Kill all Python processes (more aggressive)
REM taskkill /f /im python.exe >nul 2>&1

echo.
echo Services stopped.
echo.
echo Note: If you had other Python programs running, they may have been stopped too.
echo.
pause