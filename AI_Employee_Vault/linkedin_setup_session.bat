@echo off
REM LinkedIn Direct Login Setup - Persistent Session
REM This creates a persistent browser session to avoid captchas

echo Setting up LinkedIn Direct Login...
echo.

cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

echo Creating persistent LinkedIn session...
echo This will open LinkedIn in a browser with saved session data.
echo.

REM Start the create_linkedin_session script which creates a persistent session
start "" python create_linkedin_session.py

echo.
echo LinkedIn session setup started!
echo.
echo Instructions:
echo 1. A browser window will open with LinkedIn
echo 2. Log in manually with your credentials
echo 3. Complete any security verifications (captcha, etc.) once
echo 4. The session will be saved for future automated access
echo 5. Close the browser when login is successful
echo.
echo After this one-time setup, future automated access should work without captchas
echo.
pause