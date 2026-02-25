#!/usr/bin/env python3
"""
Gmail Setup Helper for AI Employee Vault

This script helps users set up Gmail authentication for the AI Employee system.
The system uses Gmail API (not browser automation) to monitor emails securely.
"""

import os
import pickle
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import glob

def authenticate_gmail():
    """
    Manually run the Gmail authentication flow to create token.pickle
    This will open a browser window for the user to authenticate
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    
    # Look for available credential files
    client_secret_files = glob.glob("client_secret*.json")
    if not client_secret_files:
        print("ERROR: No client_secret*.json file found!")
        print("Please ensure you have downloaded the Google API credentials file.")
        return False
        
    credentials_path = client_secret_files[0]
    print(f"Using credential file: {credentials_path}")
    
    # Check if token.pickle already exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If no valid credentials, run the authorization flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Successfully refreshed existing credentials.")
            except Exception as e:
                print(f"Could not refresh credentials: {e}")
                print("Will start fresh authentication flow...")
                creds = None
                
        if not creds:
            try:
                # Run the OAuth flow - this will open a browser window
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
                print("Authentication successful! Credentials obtained.")
            except Exception as e:
                print(f"Authentication failed: {e}")
                print("\nTroubleshooting tips:")
                print("1. Make sure you have internet connection")
                print("2. Check that your firewall/proxy isn't blocking the connection")
                print("3. Ensure the client_secret file is valid")
                print("4. Try running as administrator if on Windows")
                return False
        
        # Save the credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("Credentials saved to token.pickle")
        
        # Test the Gmail API connection
        try:
            service = build('gmail', 'v1', credentials=creds)
            # Try to get basic profile info to verify the connection
            profile = service.users().getProfile(userId='me').execute()
            print(f"\n✓ Successfully connected to Gmail API!")
            print(f"  Email: {profile.get('emailAddress', 'Unknown')}")
            print(f"  Name: {profile.get('displayName', 'Unknown')}")
            return True
        except Exception as e:
            print(f"\n✗ Error testing Gmail API connection: {e}")
            return False
    else:
        print("Credentials are already valid and up-to-date.")
        return True

def main():
    print("=" * 60)
    print("AI Employee Vault - Gmail Authentication Setup Helper")
    print("=" * 60)
    
    print("\nAbout Gmail Integration:")
    print("- The system uses Gmail API (not browser automation) to monitor emails")
    print("- This is more secure and reliable than browser-based methods")
    print("- You only need to authenticate once, then it runs in the background")
    print("- Your credentials are stored securely in token.pickle")
    
    print("\nPrerequisites:")
    print("- Internet connection")
    print("- Google account with Gmail enabled")
    print("- Client secret file (should be named client_secret*.json)")
    
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"Client secret files found: {len(glob.glob('client_secret*.json'))}")
    
    if os.path.exists('token.pickle'):
        print("✓ Token file (token.pickle) already exists")
    else:
        print("⚠ Token file (token.pickle) does not exist - authentication needed")
    
    print("\n" + "=" * 60)
    
    response = input("\nWould you like to set up Gmail authentication now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        success = authenticate_gmail()
        if success:
            print("\n🎉 Gmail authentication completed successfully!")
            print("\nThe AI Employee system will now be able to monitor your Gmail.")
            print("The gmail_watcher component will automatically start when you run the main system.")
        else:
            print("\n❌ Gmail authentication failed.")
            print("Please try again or check the troubleshooting tips above.")
    else:
        print("\nSkipping Gmail authentication setup.")
        print("Note: The gmail_watcher will attempt authentication when first started.")

if __name__ == "__main__":
    main()