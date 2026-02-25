#!/usr/bin/env python3
"""
Gmail Setup Helper for Silver Tier AI Employee
Guides user through Gmail API setup and authentication
"""

import os
import json
import pickle
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser

def create_credentials_json():
    """Guide user to create credentials.json file"""
    print("=" * 60)
    print("Gmail API Setup - Step 1: Create credentials.json")
    print("=" * 60)
    
    print("\nTo use Gmail API, you need to create a credentials.json file.")
    print("This file contains your OAuth 2.0 client ID and secret.")
    print("\nFollow these steps to create it:")
    print("\n1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API:")
    print("   - Click 'Library' in the left sidebar")
    print("   - Search for 'Gmail API'")
    print("   - Click on 'Gmail API' and press 'Enable'")
    print("\n4. Create OAuth 2.0 credentials:")
    print("   - Go to 'Credentials' in the left sidebar")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Select 'Desktop application' as application type")
    print("   - Give it a name (e.g., 'AI Employee Gmail')")
    print("   - Click 'Create'")
    print("\n5. Download the credentials file:")
    print("   - Click the download icon next to your new client ID")
    print("   - Save the file as 'credentials.json' in your AI Employee Vault")
    print("\nAfter downloading credentials.json, press Enter to continue...")
    
    input()
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("\n❌ Error: credentials.json not found in current directory")
        print("Please download the credentials file from Google Cloud Console")
        print("and save it as 'credentials.json' in this directory.")
        return False
    
    # Validate credentials.json format
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Check if it has the expected structure
        if 'installed' not in creds_data and 'web' not in creds_data:
            print("\n❌ Error: credentials.json has unexpected format")
            print("Make sure you downloaded the correct file from Google Cloud Console")
            return False
        
        print("\n✅ credentials.json found and validated!")
        return True
        
    except json.JSONDecodeError:
        print("\n❌ Error: credentials.json is not a valid JSON file")
        return False
    except Exception as e:
        print(f"\n❌ Error reading credentials.json: {e}")
        return False

def authenticate_gmail():
    """Handle the OAuth flow to get access tokens"""
    print("\n" + "=" * 60)
    print("Gmail API Setup - Step 2: Authentication")
    print("=" * 60)
    
    print("\nNow we'll authenticate with your Gmail account.")
    print("This will open a browser window for you to grant permissions.")
    print("\nPress Enter to begin authentication...")
    input()
    
    # Scopes for Gmail API
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    
    # Check if token.pickle already exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, run the authorization flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Successfully refreshed existing credentials")
            except Exception as e:
                print(f"❌ Could not refresh credentials: {e}")
                creds = None
        
        if not creds:
            try:
                # Run the OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
                
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                print("\nTroubleshooting tips:")
                print("- Make sure you have internet connection")
                print("- Check that your firewall isn't blocking the connection")
                print("- Ensure the credentials.json file is valid")
                print("- Try running as administrator if on Windows")
                return False
        
        # Save the credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Credentials saved to token.pickle")
    
    # Test the Gmail API connection
    try:
        service = build('gmail', 'v1', credentials=creds)
        # Try to get basic profile info to verify the connection
        profile = service.users().getProfile(userId='me').execute()
        print(f"\n✅ Successfully connected to Gmail API!")
        print(f"   Email: {profile.get('emailAddress', 'Unknown')}")
        print(f"   Name: {profile.get('displayName', 'Unknown')}")
        return True
    except Exception as e:
        print(f"\n❌ Error testing Gmail API connection: {e}")
        return False

def update_env_file():
    """Update .env file with Gmail credentials information"""
    print("\n" + "=" * 60)
    print("Gmail API Setup - Step 3: Update .env file")
    print("=" * 60)
    
    # Read existing .env file if it exists
    env_path = Path('.env')
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Update with Gmail variables
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        client_config = creds_data.get('installed', creds_data.get('web', {}))
        
        env_vars['GMAIL_CREDENTIALS'] = 'credentials.json'
        env_vars['GMAIL_CLIENT_ID'] = client_config.get('client_id', '')
        env_vars['GMAIL_CLIENT_SECRET'] = client_config.get('client_secret', '')
        
        # Write updated .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')
        
        print(f"✅ Updated {env_path} with Gmail credentials")
        print("   - GMAIL_CREDENTIALS=credentials.json")
        print("   - GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET added")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False
    
    return True

def main():
    print("AI Employee Vault - Gmail API Setup Helper")
    print("This script will guide you through setting up Gmail API access")
    
    print(f"\nCurrent directory: {os.getcwd()}")
    
    # Step 1: Create credentials.json
    if not create_credentials_json():
        print("\n❌ Setup failed at Step 1: Creating credentials.json")
        print("Please follow the instructions and try again.")
        return
    
    # Step 2: Authenticate
    if not authenticate_gmail():
        print("\n❌ Setup failed at Step 2: Authentication")
        print("Please try again later.")
        return
    
    # Step 3: Update .env file
    if not update_env_file():
        print("\n❌ Setup failed at Step 3: Updating .env file")
        print("You may need to update it manually.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Gmail API Setup Complete!")
    print("=" * 60)
    
    print("\n✅ What was completed:")
    print("   - Verified credentials.json exists and is valid")
    print("   - Completed OAuth authentication flow")
    print("   - Saved access tokens to token.pickle")
    print("   - Updated .env file with Gmail credentials")
    
    print("\n🚀 You can now run the gmail_watcher.py script!")
    print("\nThe Gmail watcher will monitor for unread important emails")
    print("and create task files in the Needs_Action folder.")

if __name__ == "__main__":
    main()