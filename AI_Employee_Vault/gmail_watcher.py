#!/usr/bin/env python3
"""
Gmail Watcher for Silver Tier AI Employee
Monitors Gmail for unread important emails using Google API
"""

import os
import pickle
import json
import time
import logging
import subprocess
from datetime import datetime
from email.utils import parsedate_to_datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/gmail_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GmailWatcher:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        self.credentials_path = os.getenv('GMAIL_CREDENTIALS', 'credentials.json')
        self.token_path = 'token.pickle'
        self.service = None
        self.processed_ids = set()
        self.retry_delay = 30  # seconds
        self.max_retries = 3
        
        # Create Logs directory if it doesn't exist
        Path('Logs').mkdir(exist_ok=True)
        Path('Needs_Action').mkdir(exist_ok=True)

    def authenticate(self):
        """Authenticate with Google API using stored credentials"""
        try:
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or obtain new credentials if needed
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        logger.error(f"Failed to refresh credentials: {e}")
                        creds = None
                
                if not creds:
                    # Run OAuth flow to get new credentials
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def extract_email_info(self, message):
        """Extract relevant information from a Gmail message"""
        headers = message['payload'].get('headers', [])
        
        # Extract key headers
        email_info = {
            'from': '',
            'subject': '',
            'received_time': '',
            'snippet': message.get('snippet', '')
        }
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            
            if name == 'from':
                email_info['from'] = value
            elif name == 'subject':
                email_info['subject'] = value
            elif name == 'date':
                email_info['received_time'] = value
        
        # Convert received_time to datetime if possible
        if email_info['received_time']:
            try:
                dt = parsedate_to_datetime(email_info['received_time'])
                email_info['received_time'] = dt.isoformat()
            except:
                pass  # Keep original format if parsing fails
        
        return email_info

    def create_task_file(self, email_info, message_id):
        """Create a markdown task file in Needs_Action folder"""
        # Sanitize filename
        subject = email_info['subject'][:50].replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        filename = f"gmail_{message_id[:8]}_{subject}.md"
        filepath = Path('Needs_Action') / filename
        
        # Create frontmatter
        frontmatter = f"""---
type: email
from: "{email_info['from']}"
subject: "{email_info['subject']}"
received: "{email_info['received_time']}"
priority: high
status: pending
---

# Email from {email_info['from']}

**Subject:** {email_info['subject']}

**Received:** {email_info['received_time']}

## Content Preview

{email_info['snippet']}

## Action Required

Review this important email and determine necessary actions.
"""
        
        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        logger.info(f"Created task file: {filepath}")
        
        # Trigger reasoning engine if the file was created successfully
        self.trigger_reasoning(filepath)
        
        return filepath

    def trigger_reasoning(self, filepath):
        """Trigger the reasoning engine to process the new task file"""
        try:
            # Check for different possible reasoning files
            reasoning_scripts = ['reasoning_loop.py', 'reasoning_trigger.py', 'enhanced_reasoning_trigger.py']
            
            for script in reasoning_scripts:
                if os.path.exists(script):
                    logger.info(f"Triggering reasoning with {script} for: {filepath}")
                    # Call reasoning script as a subprocess
                    result = subprocess.run([
                        'python', script, str(filepath)
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.info(f"Reasoning triggered successfully for: {filepath} using {script}")
                        return  # Exit after successful execution
                    else:
                        logger.error(f"Reasoning failed for {filepath} using {script}: {result.stderr}")
            
            logger.warning("No reasoning script found, skipping reasoning trigger")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Reasoning timed out for: {filepath}")
        except Exception as e:
            logger.error(f"Error triggering reasoning for {filepath}: {e}")

    def check_unread_important_emails(self):
        """Check for unread important emails and create task files"""
        try:
            # Query for unread important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=20  # Limit to prevent too many files at once
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread important emails found")
                return
            
            logger.info(f"Found {len(messages)} unread important emails")
            
            for message in messages:
                message_id = message['id']
                
                # Skip if already processed
                if message_id in self.processed_ids:
                    continue
                
                try:
                    # Get full message details
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=message_id
                    ).execute()
                    
                    # Extract email information
                    email_info = self.extract_email_info(full_message)
                    
                    # Create task file
                    self.create_task_file(email_info, message_id)
                    
                    # Add to processed set
                    self.processed_ids.add(message_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message {message_id}: {e}")
                    continue
        
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            if e.resp.status == 401:
                logger.info("Re-authentication required")
                return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
        
        return True

    def run(self):
        """Main monitoring loop"""
        logger.info("Starting Gmail Watcher...")
        
        # Authenticate
        if not self.authenticate():
            logger.error("Failed to authenticate. Exiting.")
            return
        
        # Load previously processed IDs from a file to persist across restarts
        processed_file = Path('Logs/processed_gmail_ids.json')
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
            except Exception as e:
                logger.error(f"Error loading processed IDs: {e}")
        
        while True:
            try:
                logger.info("Checking for unread important emails...")
                
                success = self.check_unread_important_emails()
                
                if not success:
                    logger.warning("Error occurred during email check. Retrying after delay...")
                    time.sleep(self.retry_delay)
                    continue
                
                # Save processed IDs periodically
                try:
                    with open(processed_file, 'w') as f:
                        json.dump(list(self.processed_ids), f)
                except Exception as e:
                    logger.error(f"Error saving processed IDs: {e}")
                
                # Wait before next check
                logger.info(f"Waiting 120 seconds before next check...")
                time.sleep(120)
                
            except KeyboardInterrupt:
                logger.info("Gmail Watcher stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

def main():
    watcher = GmailWatcher()
    watcher.run()

if __name__ == '__main__':
    main()