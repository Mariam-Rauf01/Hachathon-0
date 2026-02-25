@echo off
REM Batch file to check status of AI Employee Vault services

echo Checking AI Employee Vault System Status...
echo.

cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

echo Current Service Status:
pm2 status

echo.
echo Press any key to view dashboard...
pause >nul

echo.
echo Dashboard Content:
type Dashboard.md

echo.
echo Check complete.
pause