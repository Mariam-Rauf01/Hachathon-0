@echo off
REM AI Employee Vault - Targeted Service Stopper
REM This stops only our specific services

echo Stopping AI Employee Vault services...
echo.

REM Find and kill specific Python processes by script name
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find /i "gmail_watcher.py"') do taskkill /f /pid %%i >nul 2>&1
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find /i "filesystem_watcher.py"') do taskkill /f /pid %%i >nul 2>&1
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find /i "enhanced_dashboard_updater.py"') do taskkill /f /pid %%i >nul 2>&1

echo.
echo Targeted services stopped.
echo.
pause