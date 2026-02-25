#!/usr/bin/env python3
"""
Main entry point for the AI Employee Vault system.

This script starts all necessary components to run the complete AI employee system.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def setup_environment():
    """Ensure the environment is properly set up."""
    # Change to the project directory
    project_dir = Path(__file__).parent.resolve()
    os.chdir(project_dir)
    
    # Create required directories if they don't exist
    dirs_to_create = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Pending_Approval',
        'Approved',
        'Plans',
        'Logs',
        'Archive'
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'watchdog',
        'psutil',
        'schedule',
        'python-dotenv',
        'PyYAML'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def start_component(name, script_path, args=None):
    """Start a component as a subprocess."""
    try:
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        process = subprocess.Popen(cmd)
        print(f"Started {name} with PID {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start {name}: {e}")
        return None

def main():
    """Main function to start the AI Employee system."""
    print("Starting AI Employee Vault System...")
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Ensure Dashboard.md exists
    if not os.path.exists('Dashboard.md'):
        print("Creating initial Dashboard.md...")
        with open('Dashboard.md', 'w', encoding='utf-8') as f:
            f.write("""# AI Employee Dashboard

## Overview
Welcome to the AI Employee Dashboard. This system monitors various inputs and processes tasks automatically.

**Last updated:** 2026-02-14 00:00:00

## Current Status
- **Files in Inbox:** 0
- **Tasks in Needs Action:** 0
- **Completed Tasks:** 0
- **System Health:** Operational

## Urgent Items
- No urgent items at this time

## Pending Tasks
| Task | Priority | Status | Due Date |
|------|----------|--------|----------|

## Recent Activity
- No recent activity

## System Metrics
- **Running Components:** 0
- **Active Monitors:** 0
- **Last Processed:** Never
""")
    
    print("Starting system components...")
    
    # Start the orchestrator (this manages all other components)
    orchestrator_process = start_component(
        "Orchestrator", 
        "orchestrator.py"
    )
    
    if not orchestrator_process:
        print("Failed to start orchestrator. Exiting.")
        sys.exit(1)
    
    print("\nAI Employee Vault System is now running!")
    print("Components started:")
    print("- Orchestrator (manages all other components)")
    print("\nPress Ctrl+C to stop the system...")
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            # Check if orchestrator is still running
            if orchestrator_process.poll() is not None:
                print("Orchestrator process ended unexpectedly. Exiting.")
                break
    except KeyboardInterrupt:
        print("\nShutting down AI Employee Vault System...")
        if orchestrator_process.poll() is None:
            orchestrator_process.terminate()
            try:
                orchestrator_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                orchestrator_process.kill()
        print("System shut down complete.")

if __name__ == "__main__":
    main()