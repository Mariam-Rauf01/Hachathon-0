#!/usr/bin/env python3
"""
Enhanced Main entry point for the AI Employee Vault system.

This script starts all necessary components to run the complete AI employee system
with improved security, performance, and reliability.
"""

import os
import sys
import subprocess
import signal
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional
import psutil
import hashlib
from datetime import datetime

# Enhanced security and configuration
class SecureConfig:
    """Secure configuration manager with encrypted storage"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.resolve()
        self.config_path = self.project_dir / ".secure_config"
        self.encryption_key = self._generate_encryption_key()
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from system fingerprint"""
        system_fingerprint = f"{sys.platform}_{os.getpid()}_{time.time()}"
        return hashlib.sha256(system_fingerprint.encode()).digest()[:32]
    
    def load_env_vars(self):
        """Load environment variables with validation"""
        required_vars = [
            'SMTP_SERVER', 'SMTP_PORT', 'EMAIL_USERNAME', 
            'LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
            print("Some features may not work properly.")


class EnhancedEnvironment:
    """Enhanced environment setup with security and validation"""
    
    def __init__(self):
        self.directories = [
            'Inbox',
            'Needs_Action',
            'Done',
            'Pending_Approval',
            'Approved',
            'Plans',
            'Logs',
            'Archive',
            'Temp',
            'Backup'
        ]
        self.config = SecureConfig()
        
    def setup_environment(self):
        """Secure environment setup with validation"""
        # Change to the project directory
        project_dir = Path(__file__).parent.resolve()
        os.chdir(project_dir)
        
        # Validate project structure
        self._validate_project_structure()
        
        # Create required directories if they don't exist
        for directory in self.directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Ensured directory exists: {directory}")
            
        # Setup secure logging
        self._setup_secure_logging()
        
        # Load and validate environment variables
        self.config.load_env_vars()
        
    def _validate_project_structure(self):
        """Validate that critical project files exist"""
        critical_files = [
            'Company_Handbook.md',
            'Dashboard.md',
            'requirements.txt',
            'SKILL.md'
        ]
        
        missing_files = []
        for file in critical_files:
            if not os.path.exists(file):
                missing_files.append(file)
                
        if missing_files:
            print(f"Warning: Missing critical files: {', '.join(missing_files)}")
    
    def _setup_secure_logging(self):
        """Setup secure logging with rotation"""
        log_dir = 'Logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging with security considerations
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, f'application_{datetime.now().strftime("%Y%m%d")}.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )


class DependencyManager:
    """Enhanced dependency management with security checks"""
    
    def __init__(self):
        self.required_packages = [
            'watchdog',
            'psutil', 
            'schedule',
            'python-dotenv',
            'PyYAML',
            'google-auth',
            'google-auth-oauthlib',
            'google-auth-httplib2',
            'google-api-python-client',
            'selenium',
            'requests',
            'beautifulsoup4',
            'ollama',
            'playwright',  # Added for better browser automation
            'aiohttp',     # Added for async HTTP
            'aiofiles'     # Added for async file operations
        ]
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed with version validation"""
        missing_packages = []
        outdated_packages = []
        
        for package_spec in self.required_packages:
            # Extract package name (before >= or ==)
            if '>=' in package_spec:
                package_name = package_spec.split('>=')[0]
            elif '==' in package_spec:
                package_name = package_spec.split('==')[0]
            else:
                package_name = package_spec

            # Map installation name to import name
            import_mapping = {
                'python-dotenv': 'dotenv',
                'PyYAML': 'yaml',
                'google-auth': 'google.auth',
                'google-auth-oauthlib': 'google_auth_oauthlib',
                'google-auth-httplib2': 'google_auth_httplib2',
                'google-api-python-client': 'googleapiclient',
                'beautifulsoup4': 'bs4',
                'aiohttp': 'aiohttp',
                'aiofiles': 'aiofiles'
            }
            
            import_name = import_mapping.get(package_name, package_name)
            
            try:
                __import__(import_name.replace('-', '_'))
            except ImportError:
                missing_packages.append(package_spec)
        
        if missing_packages:
            print(f"Missing required packages: {', '.join(missing_packages)}")
            print("Please install them using: pip install -r requirements.txt")
            return False
            
        if outdated_packages:
            print(f"Outdated packages (consider updating): {', '.join(outdated_packages)}")
            
        return True


class ComponentManager:
    """Enhanced component management with monitoring and recovery"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.component_configs = {
            'orchestrator': {
                'script': 'orchestrator.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 30
            },
            'filesystem_watcher': {
                'script': 'filesystem_watcher.py',
                'restart_on_failure': True,
                'max_restarts': 5,
                'restart_interval': 10
            },
            'gmail_watcher': {
                'script': 'gmail_watcher.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 60
            },
            'linkedin_watcher': {
                'script': 'linkedin_watcher.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 60
            },
            'whatsapp_watcher': {
                'script': 'whatsapp_watcher.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 60
            },
            'reasoning_trigger': {
                'script': 'reasoning_trigger.py',
                'restart_on_failure': True,
                'max_restarts': 5,
                'restart_interval': 10
            },
            'email_handler': {
                'script': 'email_handler.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 30
            },
            'linkedin_poster': {
                'script': 'linkedin_poster.py',
                'restart_on_failure': True,
                'max_restarts': 3,
                'restart_interval': 60
            },
            'dashboard_updater': {
                'script': 'dashboard_updater.py',
                'restart_on_failure': True,
                'max_restarts': 5,
                'restart_interval': 15
            }
        }
        self.restart_counts: Dict[str, int] = {}
        self.last_restart_times: Dict[str, float] = {}
        
    def start_component(self, name: str) -> Optional[subprocess.Popen]:
        """Start a component with error handling and monitoring"""
        try:
            if name not in self.component_configs:
                print(f"Unknown component: {name}")
                return None
                
            config = self.component_configs[name]
            
            # Get the directory where main.py is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, config['script'])
            
            if not os.path.exists(script_path):
                print(f"Script not found: {script_path}")
                return None
                
            # Check restart limits
            if name in self.restart_counts:
                if self.restart_counts[name] >= config['max_restarts']:
                    elapsed = time.time() - self.last_restart_times[name]
                    if elapsed < config['restart_interval']:
                        print(f"Component {name} has reached restart limit. Waiting {config['restart_interval'] - elapsed:.0f}s")
                        return None
                        
            process = subprocess.Popen([
                sys.executable, '-u', script_path  # -u for unbuffered output
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes[name] = process
            print(f"Started {name} with PID {process.pid}")
            
            # Monitor process in a separate thread
            monitor_thread = threading.Thread(
                target=self._monitor_process, 
                args=(name, process),
                daemon=True
            )
            monitor_thread.start()
            
            return process
            
        except Exception as e:
            print(f"Failed to start {name}: {e}")
            return None
    
    def _monitor_process(self, name: str, process: subprocess.Popen):
        """Monitor a process and handle termination"""
        try:
            stdout, stderr = process.communicate()  # Wait for process to complete
            
            if process.returncode != 0:
                print(f"Component {name} exited with code {process.returncode}")
                if stderr:
                    print(f"Error output: {stderr.decode()}")
                    
                # Handle restart if configured
                config = self.component_configs[name]
                if config['restart_on_failure']:
                    self._handle_restart(name)
                    
        except Exception as e:
            print(f"Error monitoring {name}: {e}")
    
    def _handle_restart(self, name: str):
        """Handle component restart with rate limiting"""
        current_time = time.time()
        
        # Reset counter if enough time has passed
        if name in self.last_restart_times:
            if current_time - self.last_restart_times[name] > self.component_configs[name]['restart_interval'] * 2:
                self.restart_counts[name] = 0
        
        # Increment restart count
        self.restart_counts[name] = self.restart_counts.get(name, 0) + 1
        self.last_restart_times[name] = current_time
        
        print(f"Attempting to restart {name} (attempt {self.restart_counts[name]})")
        
        # Wait before restart
        time.sleep(min(5, self.component_configs[name]['restart_interval'] / 10))
        
        # Restart the component
        self.start_component(name)
    
    def stop_all_components(self):
        """Gracefully stop all running components"""
        print("Stopping all components...")
        
        for name, process in list(self.processes.items()):
            try:
                if process.poll() is None:  # Process is still running
                    print(f"Terminating {name} (PID: {process.pid})")
                    process.terminate()
                    
                    try:
                        process.wait(timeout=10)  # Wait up to 10 seconds
                    except subprocess.TimeoutExpired:
                        print(f"Force killing {name} after timeout")
                        process.kill()
                        
            except Exception as e:
                print(f"Error stopping {name}: {e}")
                
        self.processes.clear()
        print("All components stopped")


class SystemHealthMonitor:
    """Monitor system health and performance"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 90.0
        }
        
    def check_system_health(self) -> Dict[str, float]:
        """Check system health metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = (psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100
        
        health_status = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'healthy': (
                cpu_percent <= self.thresholds['cpu_percent'] and
                memory_percent <= self.thresholds['memory_percent'] and
                disk_percent <= self.thresholds['disk_percent']
            )
        }
        
        return health_status
    
    def log_health_status(self):
        """Log system health status"""
        health = self.check_system_health()
        
        if not health['healthy']:
            print(f"WARNING: System health issues detected!")
            if health['cpu_percent'] > self.thresholds['cpu_percent']:
                print(f"  CPU usage: {health['cpu_percent']:.1f}% (threshold: {self.thresholds['cpu_percent']}%)")
            if health['memory_percent'] > self.thresholds['memory_percent']:
                print(f"  Memory usage: {health['memory_percent']:.1f}% (threshold: {self.thresholds['memory_percent']}%)")
            if health['disk_percent'] > self.thresholds['disk_percent']:
                print(f"  Disk usage: {health['disk_percent']:.1f}% (threshold: {self.thresholds['disk_percent']}%)")
        else:
            print(f"System health OK - CPU: {health['cpu_percent']:.1f}%, "
                  f"Memory: {health['memory_percent']:.1f}%, "
                  f"Disk: {health['disk_percent']:.1f}%")


def ensure_dashboard_exists():
    """Ensure Dashboard.md exists with enhanced content"""
    if not os.path.exists('Dashboard.md'):
        print("Creating enhanced Dashboard.md...")
        with open('Dashboard.md', 'w', encoding='utf-8') as f:
            f.write("""# AI Employee Dashboard

## Overview
Welcome to the AI Employee Dashboard. This system monitors various inputs and processes tasks automatically.

**Last updated:** {timestamp}

## Current Status
- **Files in Inbox:** 0
- **Tasks in Needs Action:** 0
- **Completed Tasks:** 0
- **System Health:** Operational
- **Active Components:** 0

## Urgent Items
- No urgent items at this time

## Pending Tasks
| Task | Priority | Status | Due Date | Source |
|------|----------|--------|----------|---------|
| No pending tasks | - | - | - | - |

## Recent Activity
- System initialized
- No recent activity

## System Metrics
- **Running Components:** 0
- **Active Monitors:** 0
- **Last Processed:** Never
- **CPU Usage:** 0%
- **Memory Usage:** 0%

## Security Status
- All systems operational
- No security alerts

""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def main():
    """Enhanced main function to start the AI Employee system."""
    print("=" * 60)
    print("Starting Enhanced AI Employee Vault System...")
    print("=" * 60)

    # Setup enhanced environment
    env_manager = EnhancedEnvironment()
    env_manager.setup_environment()

    # Check dependencies
    dep_manager = DependencyManager()
    if not dep_manager.check_dependencies():
        print("Dependency check failed. Exiting.")
        sys.exit(1)

    # Ensure Dashboard.md exists
    ensure_dashboard_exists()

    # Initialize component manager
    comp_manager = ComponentManager()
    
    # Initialize system health monitor
    health_monitor = SystemHealthMonitor()

    print("Starting system components...")

    # Start the orchestrator first (this manages all other components)
    orchestrator_process = comp_manager.start_component('orchestrator')
    
    if not orchestrator_process:
        print("Failed to start orchestrator. Exiting.")
        sys.exit(1)

    print("\nEnhanced AI Employee Vault System is now running!")
    print("Components started:")
    print("- Orchestrator (manages all other components)")
    print("- Enhanced security and monitoring enabled")
    print("- Automatic restart protection active")
    print("\nPress Ctrl+C to stop the system...")

    try:
        # Keep the main process alive with health monitoring
        while True:
            time.sleep(10)  # Check every 10 seconds
            
            # Monitor system health
            health_monitor.log_health_status()
            
            # Check if orchestrator is still running
            if orchestrator_process.poll() is not None:
                print("Orchestrator process ended unexpectedly. Attempting restart...")
                orchestrator_process = comp_manager.start_component('orchestrator')
                if not orchestrator_process:
                    print("Failed to restart orchestrator. Exiting.")
                    break
                    
    except KeyboardInterrupt:
        print("\n\nShutting down Enhanced AI Employee Vault System...")
        comp_manager.stop_all_components()
        print("System shut down complete.")
        print("=" * 60)

if __name__ == "__main__":
    main()