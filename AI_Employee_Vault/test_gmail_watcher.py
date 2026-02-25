#!/usr/bin/env python3
"""
Test script to verify Gmail watcher functionality
"""

import subprocess
import sys
import os
import time

def test_gmail_watcher():
    """Test if the Gmail watcher can start without errors"""
    print("Testing Gmail Watcher startup...")
    
    # Change to the vault directory
    vault_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(vault_dir)
    
    # Try to run the gmail_watcher.py directly to see any errors
    try:
        print("\nAttempting to start Gmail Watcher...")
        print("(This may take a moment and might open a browser for authentication if not already authenticated)")
        
        # Run the gmail watcher with timeout to prevent hanging
        process = subprocess.Popen([
            sys.executable, '-u', 'gmail_watcher.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for a few seconds to see if it starts successfully
        try:
            stdout, stderr = process.communicate(timeout=10)  # Wait 10 seconds max
            
            if process.returncode is None:
                # Process is still running, which is good
                print("✓ Gmail Watcher started successfully and is running!")
                print("  (Process is continuing in the background)")
                
                # Terminate the process since we were just testing
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
                assert True  # Test passed
            else:
                # Process exited with an error
                print(f"✗ Gmail Watcher exited with code {process.returncode}")
                if stderr:
                    print(f"Error output: {stderr.decode()}")
                if stdout:
                    print(f"Standard output: {stdout.decode()}")
                assert False, "Gmail watcher exited with error"
                
        except subprocess.TimeoutExpired:
            # Process is running beyond our test timeout, which is actually good
            print("✓ Gmail Watcher started successfully and is running!")
            
            # Terminate the process since we were just testing
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
            assert True  # Test passed
            
    except FileNotFoundError:
        print("✗ gmail_watcher.py not found in current directory")
        assert False, "gmail_watcher.py not found"
    except Exception as e:
        print(f"✗ Error starting Gmail Watcher: {e}")
        assert False, f"Error starting Gmail Watcher: {e}"

def check_prerequisites():
    """Check if all prerequisites for Gmail watcher are met"""
    print("Checking prerequisites for Gmail Watcher...")
    
    # Check if required files exist
    files_needed = [
        'gmail_watcher.py',
        'token.pickle',  # Authentication token
    ]
    
    client_secret_files = [f for f in os.listdir('.') if f.startswith('client_secret') and f.endswith('.json')]
    
    print(f"  ✓ gmail_watcher.py: {'Found' if os.path.exists('gmail_watcher.py') else 'MISSING'}")
    print(f"  ✓ token.pickle: {'Found' if os.path.exists('token.pickle') else 'Not found (will be created during auth)'}")
    print(f"  ✓ client_secret*.json: {'Found' if client_secret_files else 'MISSING'}")
    
    if not os.path.exists('gmail_watcher.py'):
        print("\n❌ ERROR: gmail_watcher.py is missing!")
        return False
        
    if not client_secret_files:
        print("\n❌ ERROR: No client_secret*.json file found!")
        print("   You need to download Google API credentials first.")
        return False
    
    # Check if required Python packages are installed
    try:
        import google.auth
        import google.oauth2
        import google.auth.transport.requests
        import googleapiclient.discovery
        import google_auth_oauthlib.flow
        print("  ✓ Google API libraries: Available")
    except ImportError as e:
        print(f"  ✗ Google API libraries: Missing ({e})")
        print("   Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    
    print("\n✓ All prerequisites appear to be in order!")
    return True

def main():
    print("=" * 60)
    print("Gmail Watcher Test Script")
    print("=" * 60)
    
    print("\nThis script will:")
    print("1. Check if all prerequisites are met")
    print("2. Test if the Gmail Watcher can start properly")
    print("3. Provide guidance if there are issues")
    
    print("\nCurrent directory:", os.getcwd())
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please resolve the issues above.")
        return
    
    print("\n" + "-" * 60)
    
    # Test the Gmail watcher
    test_gmail_watcher()
    
    print("\n" + "=" * 60)
    print("✅ Gmail Watcher test completed!")
    print("\nThe Gmail Watcher should work correctly when the system starts.")
    print("If you're having issues, it might be related to authentication.")
    print("\nIf this is your first time running the system, you may need to")
    print("authenticate with Google. Run the gmail_setup_helper.py script to do this.")
    
    print("\nFor reference: The Gmail integration uses the Google API,")
    print("which means it accesses Gmail programmatically without needing")
    print("to open a browser window continuously. The first time setup")
    print("may open a browser for authentication, but after that it runs")
    print("silently in the background.")

if __name__ == "__main__":
    main()