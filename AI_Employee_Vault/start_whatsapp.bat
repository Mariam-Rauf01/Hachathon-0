@echo off
REM Start WhatsApp Watcher for Liking and Interactions

echo Starting WhatsApp Watcher...
echo This will open WhatsApp in a browser window.
echo.

cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start WhatsApp watcher
start "" python whatsapp_watcher.py

echo.
echo WhatsApp Watcher started!
echo.
echo Instructions:
echo 1. A browser window should open automatically with WhatsApp Web
echo 2. On your phone, open WhatsApp and scan the QR code
echo 3. Once logged in, you can use WhatsApp for liking and interactions
echo.
echo Note: The system will monitor WhatsApp for messages and interactions
echo.
echo To stop: Close the browser window and/or run stop_whatsapp.bat
echo.
pause