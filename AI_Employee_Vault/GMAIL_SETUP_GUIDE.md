# Gmail Integration Guide

## How Gmail Integration Works

The AI Employee Vault system uses the **Gmail API** (not browser automation) to monitor your Gmail account for new emails. This approach is:

- More secure than browser automation
- More reliable and faster
- Doesn't require a browser to stay open
- Runs silently in the background

## Authentication Process

1. The first time you run the system, it will need to authenticate with your Gmail account
2. This creates a `token.pickle` file that stores your credentials securely
3. After initial authentication, the system can access your Gmail without further interaction

## Setting Up Gmail Access

### Option 1: Using the Setup Helper (Recommended)
```bash
python gmail_setup_helper.py
```
This will guide you through the authentication process step-by-step.

### Option 2: Manual Authentication
Run the system normally, and when the `gmail_watcher.py` starts, it will:
1. Open your default browser to Google's authentication page
2. Ask you to log in and grant permission to the app
3. Create the `token.pickle` file for future use

## Troubleshooting Common Issues

### "No client_secret*.json file found"
- You need to set up Google API credentials first
- Visit https://console.cloud.google.com/
- Create a new project or select an existing one
- Enable the Gmail API
- Create credentials (OAuth 2.0 Client IDs)
- Download the credentials file and rename it to `client_secret*.json`

### "Authentication keeps failing"
- Check your internet connection
- Make sure your system clock is accurate
- Try deleting `token.pickle` and re-authenticating
- Run as administrator if on Windows

### "Gmail watcher not starting"
- Verify all required Python packages are installed:
  ```bash
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

## Important Notes

- Your Gmail password is never stored anywhere
- The system only reads emails (doesn't send or modify them)
- You can revoke access anytime from your Google Account settings
- The authentication token typically lasts for several weeks before needing refresh
</content>