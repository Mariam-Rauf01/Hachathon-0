@echo off
echo Stopping AI Employee Vault System...
echo.

call pm2 stop all

echo.
echo System stopped successfully!
echo.
pause