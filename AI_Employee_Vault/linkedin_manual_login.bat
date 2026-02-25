@echo off
REM LinkedIn Manual Login Setup
REM This opens LinkedIn for manual login to establish trusted session

echo Opening LinkedIn for manual login...
echo.

cd /d "C:\Users\HAROON TRADERS\OneDrive\Desktop\hack 0\AI_Employee_Vault"

REM Start the keep_browser_open script to maintain a manual session
start "" python keep_browser_open.py

echo.
echo LinkedIn login page opened in your default browser!
echo.
echo Instructions:
echo 1. Complete the login manually in the browser
echo 2. Perform any required verifications (captcha, etc.)
echo 3. Navigate around LinkedIn to establish a trusted session
echo 4. Leave the browser open while using the system
echo.
echo This helps establish a trusted session that reduces captcha challenges
echo.
pause