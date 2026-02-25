#!/usr/bin/env python3
"""
Test script for Gmail Watcher integration with reasoning
"""

import time
import os
from pathlib import Path

def test_gmail_integration():
    print("Testing Gmail Watcher Integration with Reasoning")
    print("="*50)
    
    print("\n1. Checking required files...")
    required_files = [
        'gmail_watcher.py',
        'reasoning_loop.py',  # May not exist in all setups
        'credentials.json',
        'token.pickle'
    ]
    
    for file in required_files:
        exists = os.path.exists(file)
        status = "[OK]" if exists else "[MISSING]"
        print(f"   {status} {file}")
    
    print("\n2. Checking directories...")
    dirs_to_check = ['Needs_Action', 'Logs']
    for dir_path in dirs_to_check:
        exists = os.path.exists(dir_path)
        status = "[OK]" if exists else "[MISSING]"
        print(f"   {status} {dir_path}/")
    
    print("\n3. Checking environment variables...")
    # Load environment variables from .env file
    import dotenv
    dotenv.load_dotenv()
    
    env_vars = ['GMAIL_CREDENTIALS', 'GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET']
    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        status = "[SET]" if value != 'NOT SET' else "[NOT SET]"
        print(f"   {status} {var}={value}")
    
    print("\n4. Preparing test scenario...")
    print("   - The gmail_watcher is already running via PM2")
    print("   - It checks for 'is:unread is:important' emails every 120 seconds")
    print("   - When found, it creates .md files in Needs_Action with high priority")
    print("   - It triggers reasoning_loop.py for each new task file")
    
    print("\n5. To test the full integration:")
    print("   a) Send yourself an email marked as 'Important'")
    print("   b) Mark it as unread")
    print("   c) Wait up to 2 minutes for the watcher to detect it")
    print("   d) Check Needs_Action folder for the new .md file")
    print("   e) Check Logs/gmail_watcher.log for processing logs")
    print("   f) Check if reasoning was triggered in the logs")
    
    print("\n6. Manual verification commands:")
    print("   # Check for new files in Needs_Action")
    print("   dir Needs_Action")
    print()
    print("   # Check the most recent log")
    print("   type Logs\\gmail_watcher.log")
    print()
    print("   # Check PM2 logs for the gmail_watcher")
    print("   pm2 logs gmail_watcher --lines 10")
    
    print("\n7. Expected behavior:")
    print("   - New important unread email -> .md file in Needs_Action")
    print("   - .md file contains email metadata in frontmatter")
    print("   - Reasoning engine is triggered for the new task")
    print("   - Task gets high priority status")
    
    print("\nIntegration test setup complete!")

if __name__ == "__main__":
    test_gmail_integration()