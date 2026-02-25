@echo off
REM Batch file to stop AI Employee Vault services

echo Stopping AI Employee Vault services...
cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

pm2 stop all

echo.
echo All services stopped.
echo.
pause