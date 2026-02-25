@echo off
REM Stop WhatsApp Watcher

echo Stopping WhatsApp Watcher...
echo.

taskkill /f /im python.exe /fi "WINDOWTITLE eq *whatsapp_watcher*"

echo.
echo WhatsApp Watcher stopped.
echo.
pause