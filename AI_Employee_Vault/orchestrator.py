import multiprocessing
import subprocess
import sys
import time
import signal
import os
import logging
import schedule
from datetime import datetime
import psutil
from dotenv import load_dotenv
import threading
import queue
import yaml
import json
from pathlib import Path
import glob
from typing import Dict, Any, Optional, Tuple, List

# Check for required modules and warn if missing
REQUIRED_MODULES = [
    'watchdog', 'psutil', 'schedule', 'dotenv', 'yaml'
]

missing_modules = []
for module in REQUIRED_MODULES:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f"WARNING: The following required modules are missing: {', '.join(missing_modules)}")
    print("Please run: pip install -r requirements.txt")

# Load environment variables
load_dotenv()

class AdvancedScheduler:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.log_queue = queue.Queue()
        self.task_queue = queue.PriorityQueue()
        self.resource_limits = {
            'cpu_threshold': float(os.getenv('CPU_THRESHOLD', '95.0')),
            'memory_threshold': float(os.getenv('MEMORY_THRESHOLD', '95.0')),
            'max_concurrent_watchers': int(os.getenv('MAX_CONCURRENT_WATCHERS', '3'))
        }
        
        # Load scheduling intervals from .env
        self.intervals = {
            'gmail_watcher': int(os.getenv('GMAIL_WATCHER_INTERVAL', '300')),  # 5 minutes
            'whatsapp_watcher': int(os.getenv('WHATSAPP_WATCHER_INTERVAL', '300')),  # 5 minutes
            'linkedin_watcher': int(os.getenv('LINKEDIN_WATCHER_INTERVAL', '300')),  # 5 minutes
            'reasoning_trigger': int(os.getenv('REASONING_INTERVAL', '60')),   # 1 minute
            'email_handler': int(os.getenv('EMAIL_HANDLER_INTERVAL', '30')),   # 30 seconds
            'linkedin_poster': int(os.getenv('LINKEDIN_POSTER_INTERVAL', '300')),  # 5 minutes
            'hilt_scheduler': int(os.getenv('HILT_SCHEDULER_INTERVAL', '60'))  # 1 minute
        }
        
        # Priority keywords mapping
        self.priority_keywords = {
            'high': os.getenv('HIGH_PRIORITY_KEYWORDS', 'urgent,important,emergency,critical,asap').split(','),
            'medium': os.getenv('MEDIUM_PRIORITY_KEYWORDS', 'normal,standard,regular').split(','),
            'low': os.getenv('LOW_PRIORITY_KEYWORDS', 'later,eventual,future').split(',')
        }
        
        # Setup logging
        self.setup_logging()
        
        # Component configurations with priority levels
        self.components = {
            'gmail_watcher': {
                'script': 'gmail_watcher.py',
                'interval': self.intervals['gmail_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.1  # Low resource usage
            },
            'whatsapp_watcher': {
                'script': 'whatsapp_watcher.py',
                'interval': self.intervals['whatsapp_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.15  # Medium resource usage
            },
            'linkedin_watcher': {
                'script': 'linkedin_watcher.py',
                'interval': self.intervals['linkedin_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.15  # Medium resource usage
            },
            'reasoning_trigger': {
                'script': 'reasoning_trigger.py',
                'interval': self.intervals['reasoning_trigger'],
                'process': None,
                'last_check': 0,
                'priority': 3,  # High priority
                'resource_usage': 0.2  # High resource usage
            },
            'email_handler': {
                'script': 'email_handler.py',
                'interval': self.intervals['email_handler'],
                'process': None,
                'last_check': 0,
                'priority': 3,  # High priority
                'resource_usage': 0.05  # Low resource usage
            },
            'linkedin_poster': {
                'script': 'linkedin_poster.py',
                'interval': self.intervals['linkedin_poster'],
                'process': None,
                'last_check': 0,
                'priority': 1,  # Low priority
                'resource_usage': 0.1  # Low resource usage
            },
            'hilt_scheduler': {
                'script': 'hilt_scheduler.py',
                'interval': self.intervals['hilt_scheduler'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.05  # Low resource usage
            }
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = 'Logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'orchestrator.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Advanced AI Orchestrator initialized with enhanced scheduling")
    
    def get_file_priority(self, file_path):
        """Extract priority from file frontmatter or content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if content.startswith('---'):
                end_frontmatter = content.find('---', 3)
                if end_frontmatter != -1:
                    frontmatter = content[4:end_frontmatter].strip()
                    try:
                        metadata = yaml.safe_load(frontmatter)
                        if metadata and 'priority' in metadata:
                            priority_map = {'high': 3, 'medium': 2, 'low': 1}
                            return priority_map.get(metadata['priority'], 2)
                    except:
                        pass
            
            # Check content for priority keywords
            content_lower = content.lower()
            for keyword in self.priority_keywords['high']:
                if keyword.strip() in content_lower:
                    return 3  # High priority
            
            for keyword in self.priority_keywords['medium']:
                if keyword.strip() in content_lower:
                    return 2  # Medium priority
            
            return 1  # Low priority
            
        except Exception as e:
            self.logger.error(f"Error determining priority for {file_path}: {e}")
            return 2  # Default to medium priority
    
    def sort_needs_action_by_priority(self):
        """Sort files in Needs_Action by priority and add to task queue"""
        try:
            needs_action_dir = os.path.join('AI_Employee_Vault', 'Needs_Action')
            if not os.path.exists(needs_action_dir):
                return
            
            files = glob.glob(os.path.join(needs_action_dir, '*'))
            priority_files = []
            
            for file_path in files:
                if os.path.isfile(file_path):
                    priority = self.get_file_priority(file_path)
                    priority_files.append((priority, file_path))
            
            # Sort by priority (highest first) and add to queue
            priority_files.sort(key=lambda x: x[0], reverse=True)
            
            for priority, file_path in priority_files:
                # Use negative priority for PriorityQueue (higher priority = lower number)
                self.task_queue.put((-priority, file_path))
            
            if priority_files:
                self.logger.info(f"Added {len(priority_files)} files to priority queue")
                
        except Exception as e:
            self.logger.error(f"Error sorting Needs_Action files: {e}")
    
    def check_system_resources(self):
        """Check system resources and adjust component execution"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100

            # Determine active watchers count
            active_watchers = sum(1 for name, config in self.components.items()
                                if name.endswith('_watcher') and self.is_component_running(name))

            # Adjust based on resource usage
            resource_status = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'active_watchers': active_watchers,
                'cpu_high': cpu_percent > self.resource_limits['cpu_threshold'],
                'memory_high': memory_percent > self.resource_limits['memory_threshold'],
                'too_many_watchers': active_watchers > self.resource_limits['max_concurrent_watchers']
            }

            return resource_status

        except psutil.AccessDenied:
            self.logger.error("Access denied when checking system resources. Running with limited privileges?")
            return {'cpu_high': False, 'memory_high': False, 'too_many_watchers': False}
        except psutil.Error as e:
            self.logger.error(f"Psutil error when checking system resources: {e}")
            return {'cpu_high': False, 'memory_high': False, 'too_many_watchers': False}
        except Exception as e:
            self.logger.error(f"Unexpected error checking system resources: {e}")
            return {'cpu_high': False, 'memory_high': False, 'too_many_watchers': False}
    
    def should_run_component(self, component_name):
        """Determine if component should run based on resource constraints"""
        if not component_name.endswith('_watcher'):
            return True  # Non-watchers always run
        
        resource_status = self.check_system_resources()
        
        # Don't run if resources are constrained
        if (resource_status['cpu_high'] or 
            resource_status['memory_high'] or 
            resource_status['too_many_watchers']):
            self.logger.warning(f"Resource constraints detected, skipping {component_name}")
            return False
        
        return True
    
    def start_component(self, component_name):
        """Start a component as a subprocess with resource checking"""
        try:
            # Check resource constraints before starting
            if not self.should_run_component(component_name):
                return False

            config = self.components[component_name]
            
            # Get the directory where orchestrator.py is located
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, config['script'])

            if not os.path.exists(script_path):
                self.logger.error(f"Script not found: {script_path}")
                return False

            # Start subprocess
            process = subprocess.Popen([
                sys.executable, script_path
            ])

            config['process'] = process
            config['last_check'] = time.time()

            self.logger.info(f"Started {component_name}: PID {process.pid} (Priority: {config['priority']})")
            return True

        except FileNotFoundError:
            self.logger.error(f"Python interpreter not found when starting {component_name}")
            return False
        except PermissionError:
            self.logger.error(f"Permission denied when starting {component_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error starting {component_name}: {e}")
            return False
    
    def stop_component(self, component_name):
        """Stop a component subprocess"""
        try:
            config = self.components[component_name]
            process = config['process']
            
            if process and process.poll() is None:  # Process is running
                # Try graceful shutdown first
                process.terminate()
                
                try:
                    process.wait(timeout=10)  # Wait up to 10 seconds
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    process.kill()
                    process.wait()
                
                config['process'] = None
                self.logger.info(f"Stopped {component_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error stopping {component_name}: {e}")
            return False
    
    def is_component_running(self, component_name):
        """Check if a component is currently running"""
        config = self.components[component_name]
        process = config['process']
        
        if process and process.poll() is None:
            return True
        return False
    
    def monitor_components(self):
        """Monitor and restart crashed components with priority consideration"""
        for name, config in self.components.items():
            if not self.is_component_running(name):
                # Check resource constraints before restarting
                if self.should_run_component(name):
                    self.logger.warning(f"{name} is not running, restarting...")
                    self.start_component(name)
    
    def check_folders(self):
        """Check folders for new files and trigger appropriate actions with priority"""
        try:
            # Sort Needs_Action files by priority
            self.sort_needs_action_by_priority()
            
            # Check Needs_Action folder for new files
            needs_action_dir = os.path.join('AI_Employee_Vault', 'Needs_Action')
            if os.path.exists(needs_action_dir):
                files = os.listdir(needs_action_dir)
                if files:
                    self.logger.info(f"Found {len(files)} files in Needs_Action, ensuring reasoning trigger is running")
                    if not self.is_component_running('reasoning_trigger'):
                        self.start_component('reasoning_trigger')
            
            # Check Approved folder for new files
            approved_dir = os.path.join('AI_Employee_Vault', 'Approved')
            if os.path.exists(approved_dir):
                files = os.listdir(approved_dir)
                if files:
                    self.logger.info(f"Found {len(files)} files in Approved, ensuring handlers are running")
                    if not self.is_component_running('email_handler'):
                        self.start_component('email_handler')
                    if not self.is_component_running('linkedin_poster'):
                        self.start_component('linkedin_poster')
            
            # Check Pending_Approval folder
            pending_dir = os.path.join('AI_Employee_Vault', 'Pending_Approval')
            if os.path.exists(pending_dir):
                files = os.listdir(pending_dir)
                if files:
                    self.logger.info(f"Found {len(files)} files in Pending_Approval, ensuring scheduler is running")
                    if not self.is_component_running('hilt_scheduler'):
                        self.start_component('hilt_scheduler')
        
        except Exception as e:
            self.logger.error(f"Error checking folders: {e}")
    
    def start_all_components(self):
        """Start all components with priority-based ordering"""
        self.logger.info("Starting all components with priority ordering...")
        
        # Sort components by priority (highest first)
        sorted_components = sorted(self.components.items(), key=lambda x: x[1]['priority'], reverse=True)
        
        for name, config in sorted_components:
            if not self.is_component_running(name):
                self.start_component(name)
                time.sleep(2)  # Small delay between startups
        
        self.logger.info("All components started with priority ordering")
    
    def stop_all_components(self):
        """Stop all components"""
        self.logger.info("Stopping all components...")
        
        for name in self.components.keys():
            self.stop_component(name)
        
        self.logger.info("All components stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        def scheduler_worker():
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
        
        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()
        return scheduler_thread
    
    def setup_schedules(self):
        """Setup scheduled tasks with configurable intervals"""
        # Schedule component monitoring
        schedule.every(30).seconds.do(self.monitor_components)
        
        # Schedule folder checks
        schedule.every(1).minutes.do(self.check_folders)
        
        # Schedule periodic restart checks
        schedule.every(10).minutes.do(self.ensure_all_running)
        
        # Schedule resource monitoring
        schedule.every(30).seconds.do(self.check_resource_usage)
        
        # Schedule priority queue processing
        schedule.every(30).seconds.do(self.process_priority_queue)
        
        # Schedule daily cleanup
        schedule.every().day.at("02:00").do(self.daily_cleanup)
        
        self.logger.info("Scheduled tasks setup with configurable intervals")
    
    def check_resource_usage(self):
        """Monitor and log resource usage"""
        try:
            resource_status = self.check_system_resources()
            
            self.logger.info(f"System Resources - CPU: {resource_status['cpu_percent']:.1f}%, "
                           f"Memory: {resource_status['memory_percent']:.1f}%, "
                           f"Disk: {resource_status['disk_percent']:.1f}%, "
                           f"Active Watchers: {resource_status['active_watchers']}")
            
            # Log warnings if thresholds exceeded
            if resource_status['cpu_high']:
                self.logger.warning(f"CPU usage high: {resource_status['cpu_percent']:.1f}%")
            if resource_status['memory_high']:
                self.logger.warning(f"Memory usage high: {resource_status['memory_percent']:.1f}%")
            if resource_status['too_many_watchers']:
                self.logger.warning(f"Too many watchers running: {resource_status['active_watchers']}")
                
        except Exception as e:
            self.logger.error(f"Error checking resource usage: {e}")
    
    def process_priority_queue(self):
        """Process high-priority tasks from the queue"""
        try:
            while not self.task_queue.empty():
                priority, file_path = self.task_queue.get_nowait()
                self.logger.info(f"Processing high-priority task: {file_path} (Priority: {-priority})")
                
                # Trigger reasoning for high-priority tasks
                if not self.is_component_running('reasoning_trigger'):
                    self.start_component('reasoning_trigger')
                
        except queue.Empty:
            pass  # Queue is empty, that's fine
        except Exception as e:
            self.logger.error(f"Error processing priority queue: {e}")
    
    def daily_cleanup(self):
        """Daily cleanup tasks"""
        try:
            self.logger.info("Starting daily cleanup...")
            
            # Archive old Done files (older than 7 days)
            self.archive_old_done_files()
            
            # Clean up old logs (older than 30 days)
            self.cleanup_old_logs()
            
            self.logger.info("Daily cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during daily cleanup: {e}")
    
    def archive_old_done_files(self):
        """Move old files from Done to archive"""
        try:
            done_dir = os.path.join('AI_Employee_Vault', 'Done')
            archive_dir = os.path.join('AI_Employee_Vault', 'Archive')
            
            if not os.path.exists(done_dir):
                return
            
            os.makedirs(archive_dir, exist_ok=True)
            
            import shutil
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for filename in os.listdir(done_dir):
                file_path = os.path.join(done_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        archive_path = os.path.join(archive_dir, filename)
                        shutil.move(file_path, archive_path)
                        self.logger.info(f"Archived old file: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error archiving old files: {e}")
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            logs_dir = 'Logs'
            if not os.path.exists(logs_dir):
                return
            
            import shutil
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(logs_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            self.logger.info(f"Removed old log: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    def ensure_all_running(self):
        """Ensure all critical components are running with resource awareness"""
        critical_components = ['gmail_watcher', 'whatsapp_watcher', 'linkedin_watcher', 
                             'reasoning_trigger', 'email_handler', 'hilt_scheduler']
        
        for component in critical_components:
            if not self.is_component_running(component):
                if self.should_run_component(component):
                    self.logger.info(f"Restarting critical component: {component}")
                    self.start_component(component)
    
    def run(self):
        """Main orchestrator loop"""
        self.logger.info("Advanced AI Orchestrator starting with enhanced scheduling...")
        
        # Setup schedules
        self.setup_schedules()
        
        # Start scheduler thread
        scheduler_thread = self.run_scheduler()
        
        # Start all components
        self.start_all_components()
        
        try:
            while self.running:
                # Monitor system health
                self.monitor_system_health()
                
                # Small sleep to prevent busy waiting
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def monitor_system_health(self):
        """Monitor system resources and process health"""
        try:
            # Check CPU and memory usage
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80 or memory_percent > 80:
                self.logger.warning(f"High system usage - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            
            # Check disk space
            disk_usage = psutil.disk_usage('.')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_percent > 90:
                self.logger.warning(f"Low disk space: {disk_percent:.1f}% used")
        
        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Initiating graceful shutdown...")
        
        # Stop all components
        self.stop_all_components()
        
        # Wait a bit for processes to terminate
        time.sleep(2)
        
        # Force kill any remaining processes
        self.force_kill_remaining_processes()
        
        self.logger.info("Shutdown complete")
    
    def force_kill_remaining_processes(self):
        """Force kill any remaining child processes"""
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            gone, alive = psutil.wait_procs(children, timeout=3)
            for p in alive:
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error killing remaining processes: {e}")

def main():
    """Main entry point"""
    orchestrator = AdvancedScheduler()
    orchestrator.run()

if __name__ == "__main__":
    main()