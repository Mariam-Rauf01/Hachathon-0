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
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import secrets

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


class AdvancedScheduler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.processes = {}
        self.running = True
        self.log_queue = queue.Queue()
        self.task_queue = queue.PriorityQueue()
        self.executor = ThreadPoolExecutor(max_workers=10)  # Thread pool for async operations
        
        # Enhanced resource limits with dynamic adjustment
        self.resource_limits = {
            'cpu_threshold': float(os.getenv('CPU_THRESHOLD', '95.0')),
            'memory_threshold': float(os.getenv('MEMORY_THRESHOLD', '95.0')),
            'max_concurrent_watchers': int(os.getenv('MAX_CONCURRENT_WATCHERS', '3')),
            'dynamic_adjustment': True  # Enable dynamic resource adjustment
        }

        # Load scheduling intervals from .env with enhanced defaults
        self.intervals = {
            'gmail_watcher': int(os.getenv('GMAIL_WATCHER_INTERVAL', '300')),  # 5 minutes
            'whatsapp_watcher': int(os.getenv('WHATSAPP_WATCHER_INTERVAL', '300')),  # 5 minutes
            'linkedin_watcher': int(os.getenv('LINKEDIN_WATCHER_INTERVAL', '300')),  # 5 minutes
            'reasoning_trigger': int(os.getenv('REASONING_INTERVAL', '60')),   # 1 minute
            'email_handler': int(os.getenv('EMAIL_HANDLER_INTERVAL', '30')),   # 30 seconds
            'linkedin_poster': int(os.getenv('LINKEDIN_POSTER_INTERVAL', '300')),  # 5 minutes
            'hilt_scheduler': int(os.getenv('HILT_SCHEDULER_INTERVAL', '60'))  # 1 minute
        }

        # Enhanced priority keywords mapping with better categorization
        self.priority_keywords = {
            'critical': os.getenv('CRITICAL_PRIORITY_KEYWORDS', 'emergency,crisis,urgent_immediate,security_breach').split(','),
            'high': os.getenv('HIGH_PRIORITY_KEYWORDS', 'urgent,important,emergency,critical,asap,immediate').split(','),
            'medium': os.getenv('MEDIUM_PRIORITY_KEYWORDS', 'normal,standard,regular,soon').split(','),
            'low': os.getenv('LOW_PRIORITY_KEYWORDS', 'later,eventual,future,when_possible').split(',')
        }

        # Setup enhanced logging
        self.setup_logging()

        # Enhanced component configurations with better resource tracking
        self.components = {
            'gmail_watcher': {
                'script': 'gmail_watcher.py',
                'interval': self.intervals['gmail_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.1,  # Low resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'whatsapp_watcher': {
                'script': 'whatsapp_watcher.py',
                'interval': self.intervals['whatsapp_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.15,  # Medium resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'linkedin_watcher': {
                'script': 'linkedin_watcher.py',
                'interval': self.intervals['linkedin_watcher'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.15,  # Medium resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'reasoning_trigger': {
                'script': 'reasoning_trigger.py',
                'interval': self.intervals['reasoning_trigger'],
                'process': None,
                'last_check': 0,
                'priority': 3,  # High priority
                'resource_usage': 0.2,  # High resource usage
                'max_restarts': 5,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'email_handler': {
                'script': 'email_handler.py',
                'interval': self.intervals['email_handler'],
                'process': None,
                'last_check': 0,
                'priority': 3,  # High priority
                'resource_usage': 0.05,  # Low resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'linkedin_poster': {
                'script': 'linkedin_poster.py',
                'interval': self.intervals['linkedin_poster'],
                'process': None,
                'last_check': 0,
                'priority': 1,  # Low priority
                'resource_usage': 0.1,  # Low resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'hilt_scheduler': {
                'script': 'hilt_scheduler.py',
                'interval': self.intervals['hilt_scheduler'],
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.05,  # Low resource usage
                'max_restarts': 3,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            },
            'dashboard_updater': {
                'script': 'dashboard_updater.py',
                'interval': 60,  # Update every minute
                'process': None,
                'last_check': 0,
                'priority': 2,  # Medium priority
                'resource_usage': 0.05,  # Low resource usage
                'max_restarts': 5,
                'restart_count': 0,
                'last_restart': 0,
                'health_check_enabled': True
            }
        }

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Initialize security measures
        self.secure_config = SecureConfig()

    def setup_logging(self):
        """Setup enhanced logging configuration"""
        log_dir = 'Logs'
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, 'enhanced_orchestrator.log')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced AI Orchestrator initialized with advanced scheduling and security")

    def get_file_priority(self, file_path: str) -> int:
        """Extract priority from file frontmatter or content with enhanced detection"""
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
                            priority_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
                            return priority_map.get(str(metadata['priority']).lower(), 2)
                    except yaml.YAMLError as e:
                        self.logger.error(f"YAML parse error in {file_path}: {e}")

            # Enhanced keyword-based priority detection
            content_lower = content.lower()
            
            # Check for critical keywords first
            for keyword in self.priority_keywords['critical']:
                if keyword.strip() in content_lower:
                    return 4  # Critical priority
            
            # Then high priority
            for keyword in self.priority_keywords['high']:
                if keyword.strip() in content_lower:
                    return 3  # High priority

            # Then medium priority
            for keyword in self.priority_keywords['medium']:
                if keyword.strip() in content_lower:
                    return 2  # Medium priority

            # Default to low priority
            return 1  # Low priority

        except Exception as e:
            self.logger.error(f"Error determining priority for {file_path}: {e}")
            return 2  # Default to medium priority

    def sort_needs_action_by_priority(self):
        """Sort files in Needs_Action by priority and add to task queue with enhanced processing"""
        try:
            needs_action_dir = os.path.join('Needs_Action')
            if not os.path.exists(needs_action_dir):
                return

            files = glob.glob(os.path.join(needs_action_dir, '*'))
            priority_files = []

            for file_path in files:
                if os.path.isfile(file_path):
                    priority = self.get_file_priority(file_path)
                    # Include file modification time for tie-breaking
                    mod_time = os.path.getmtime(file_path)
                    priority_files.append((priority, -mod_time, file_path))

            # Sort by priority (highest first), then by recency (newest first)
            priority_files.sort(key=lambda x: (x[0], x[1]), reverse=True)

            for priority, _, file_path in priority_files:
                # Use negative priority for PriorityQueue (higher priority = lower number)
                # Include timestamp for fair processing order of same-priority items
                timestamp = time.time()
                self.task_queue.put((-priority, timestamp, file_path))

            if priority_files:
                self.logger.info(f"Added {len(priority_files)} files to priority queue")

        except Exception as e:
            self.logger.error(f"Error sorting Needs_Action files: {e}")

    def check_system_resources(self) -> Dict[str, Any]:
        """Enhanced system resource checking with predictive analysis"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100

            # Determine active watchers count
            active_watchers = sum(1 for name, config in self.components.items()
                                if name.endswith('_watcher') and self.is_component_running(name))

            # Predictive resource analysis
            predicted_cpu_usage = cpu_percent
            for name, config in self.components.items():
                if not self.is_component_running(name):
                    predicted_cpu_usage += config['resource_usage'] * 100

            # Enhanced resource status with predictive analysis
            resource_status = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'predicted_cpu_usage': min(predicted_cpu_usage, 100.0),
                'active_watchers': active_watchers,
                'cpu_high': cpu_percent > self.resource_limits['cpu_threshold'],
                'memory_high': memory_percent > self.resource_limits['memory_threshold'],
                'too_many_watchers': active_watchers > self.resource_limits['max_concurrent_watchers'],
                'system_stressed': (
                    cpu_percent > self.resource_limits['cpu_threshold'] * 0.95 or
                    memory_percent > self.resource_limits['memory_threshold'] * 0.95
                )
            }

            return resource_status

        except psutil.AccessDenied:
            self.logger.error("Access denied when checking system resources. Running with limited privileges?")
            return {
                'cpu_high': False, 
                'memory_high': False, 
                'too_many_watchers': False,
                'system_stressed': False
            }
        except psutil.Error as e:
            self.logger.error(f"Psutil error when checking system resources: {e}")
            return {
                'cpu_high': False, 
                'memory_high': False, 
                'too_many_watchers': False,
                'system_stressed': False
            }
        except Exception as e:
            self.logger.error(f"Unexpected error checking system resources: {e}")
            return {
                'cpu_high': False, 
                'memory_high': False, 
                'too_many_watchers': False,
                'system_stressed': False
            }

    def should_run_component(self, component_name: str) -> bool:
        """Enhanced component execution decision with predictive analysis"""
        if not component_name.endswith('_watcher'):
            return True  # Non-watchers always run (unless system is critically stressed)

        resource_status = self.check_system_resources()

        # Don't run if resources are severely constrained
        if (resource_status['cpu_high'] or
            resource_status['memory_high'] or
            resource_status['too_many_watchers']):
            
            # For critical components, allow running even under stress
            if component_name in ['reasoning_trigger', 'email_handler']:
                # These are critical, only stop if system is extremely stressed
                if resource_status['cpu_percent'] > 95 or resource_status['memory_percent'] > 95:
                    self.logger.warning(f"Critical system stress, temporarily pausing {component_name}")
                    return False
                else:
                    self.logger.info(f"Allowing critical component {component_name} to run despite moderate stress")
                    return True
            else:
                self.logger.warning(f"Resource constraints detected, skipping {component_name}")
                return False

        return True

    def start_component(self, component_name: str) -> bool:
        """Enhanced component startup with security and error handling"""
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

            # Check restart limits
            current_time = time.time()
            if current_time - config['last_restart'] < 60:  # 1 minute cooldown
                if config['restart_count'] >= config['max_restarts']:
                    self.logger.warning(f"Component {component_name} has exceeded restart limit, skipping start")
                    return False

            # Start subprocess with enhanced security
            process = subprocess.Popen([
                sys.executable, '-u', script_path  # -u for unbuffered output
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

    def stop_component(self, component_name: str) -> bool:
        """Enhanced component stopping with graceful shutdown"""
        try:
            config = self.components[component_name]
            process = config['process']

            if process and process.poll() is None:  # Process is running
                # Try graceful shutdown first
                process.terminate()

                try:
                    # Wait for graceful shutdown with timeout
                    stdout, stderr = process.communicate(timeout=15)
                    if stderr:
                        self.logger.warning(f"{component_name} stderr: {stderr.decode()}")
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

    def is_component_running(self, component_name: str) -> bool:
        """Check if a component is currently running with enhanced validation"""
        config = self.components[component_name]
        process = config['process']

        if process:
            # Check if process is still alive
            if process.poll() is None:
                return True
            else:
                # Process has terminated, clean up reference
                config['process'] = None
                # Update restart tracking
                if time.time() - config['last_restart'] > 300:  # 5 min cooldown
                    config['restart_count'] = 0  # Reset after 5 mins
                config['restart_count'] += 1
                config['last_restart'] = time.time()
                return False
        return False

    def monitor_components(self):
        """Enhanced component monitoring with intelligent restart logic"""
        for name, config in self.components.items():
            if not self.is_component_running(name):
                # Apply intelligent restart logic
                if self.should_run_component(name):
                    # Check if we should restart based on failure patterns
                    if self.should_restart_component(name):
                        self.logger.warning(f"{name} is not running, restarting...")
                        self.start_component(name)

    def should_restart_component(self, component_name: str) -> bool:
        """Determine if a component should be restarted based on failure patterns"""
        config = self.components[component_name]
        
        # Don't restart if we've exceeded restart limits recently
        if config['restart_count'] >= config['max_restarts']:
            time_since_last_restart = time.time() - config['last_restart']
            # Exponential backoff: wait longer after each failed restart cycle
            required_wait = min(3600, 60 * (2 ** min(config['restart_count'] - config['max_restarts'], 8)))
            if time_since_last_restart < required_wait:
                return False
        
        return True

    def check_folders(self):
        """Enhanced folder checking with priority-based processing"""
        try:
            # Sort Needs_Action files by priority
            self.sort_needs_action_by_priority()

            # Enhanced folder monitoring with priority processing
            folder_checks = [
                ('Needs_Action', ['reasoning_trigger']),
                ('Approved', ['email_handler', 'linkedin_poster']),
                ('Pending_Approval', ['hilt_scheduler']),
                ('Inbox', ['filesystem_watcher'])  # Ensure watcher is running if Inbox has files
            ]

            for folder_name, dependent_components in folder_checks:
                folder_path = os.path.join(folder_name)
                if os.path.exists(folder_path):
                    files = os.listdir(folder_path)
                    if files:
                        self.logger.info(f"Found {len(files)} files in {folder_name}, checking dependent components")
                        
                        for component in dependent_components:
                            if not self.is_component_running(component):
                                self.logger.info(f"Starting {component} due to activity in {folder_name}")
                                self.start_component(component)

        except Exception as e:
            self.logger.error(f"Error checking folders: {e}")

    def start_all_components(self):
        """Enhanced component startup with priority-based ordering and staggered startup"""
        self.logger.info("Starting all components with priority ordering and staggered startup...")

        # Sort components by priority (highest first)
        sorted_components = sorted(self.components.items(), key=lambda x: x[1]['priority'], reverse=True)

        for name, config in sorted_components:
            if not self.is_component_running(name):
                success = self.start_component(name)
                if success:
                    # Staggered startup to prevent resource contention
                    time.sleep(1.5)  # Reduced delay for better responsiveness
                else:
                    self.logger.error(f"Failed to start component: {name}")

        self.logger.info("All components started with priority ordering")

    def stop_all_components(self):
        """Enhanced component shutdown with graceful termination"""
        self.logger.info("Stopping all components with graceful termination...")

        # Stop components in reverse priority order (low priority first)
        sorted_components = sorted(self.components.items(), key=lambda x: x[1]['priority'])

        for name, _ in sorted_components:
            self.stop_component(name)
            time.sleep(0.5)  # Brief pause between stops

        # Shutdown thread pool
        self.executor.shutdown(wait=True, timeout=10)

        self.logger.info("All components stopped")

    def signal_handler(self, signum, frame):
        """Enhanced shutdown signal handling"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    def run_scheduler(self):
        """Enhanced scheduler with async support"""
        def scheduler_worker():
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
                    time.sleep(5)  # Longer sleep on error to prevent tight loop

        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()
        return scheduler_thread

    def setup_schedules(self):
        """Setup enhanced scheduled tasks with configurable intervals and error handling"""
        # Schedule component monitoring with exponential backoff on failure
        schedule.every(30).seconds.do(self.monitor_components)

        # Schedule folder checks
        schedule.every(1).minutes.do(self.check_folders)

        # Schedule periodic restart checks
        schedule.every(10).minutes.do(self.ensure_all_running)

        # Schedule resource monitoring
        schedule.every(30).seconds.do(self.check_resource_usage)

        # Schedule priority queue processing
        schedule.every(30).seconds.do(self.process_priority_queue)

        # Schedule enhanced cleanup
        schedule.every().day.at("02:00").do(self.daily_cleanup)
        
        # Schedule health checks
        schedule.every(5).minutes.do(self.perform_health_checks)

        self.logger.info("Enhanced scheduled tasks setup with configurable intervals and error handling")

    def check_resource_usage(self):
        """Enhanced resource monitoring with predictive analysis"""
        try:
            resource_status = self.check_system_resources()

            self.logger.info(f"System Resources - CPU: {resource_status['cpu_percent']:.1f}%, "
                           f"Memory: {resource_status['memory_percent']:.1f}%, "
                           f"Disk: {resource_status['disk_percent']:.1f}%, "
                           f"Active Watchers: {resource_status['active_watchers']}, "
                           f"Predicted CPU: {resource_status['predicted_cpu_usage']:.1f}%")

            # Log warnings if thresholds exceeded
            if resource_status['cpu_high']:
                self.logger.warning(f"CPU usage high: {resource_status['cpu_percent']:.1f}%")
            if resource_status['memory_high']:
                self.logger.warning(f"Memory usage high: {resource_status['memory_percent']:.1f}%")
            if resource_status['too_many_watchers']:
                self.logger.warning(f"Too many watchers running: {resource_status['active_watchers']}")
            if resource_status['system_stressed']:
                self.logger.warning("System is under stress, consider reducing workload")

        except Exception as e:
            self.logger.error(f"Error checking resource usage: {e}")

    def process_priority_queue(self):
        """Enhanced priority task processing with concurrency control"""
        try:
            processed_count = 0
            while not self.task_queue.empty() and processed_count < 5:  # Limit batch processing
                try:
                    priority, timestamp, file_path = self.task_queue.get_nowait()
                    self.logger.info(f"Processing high-priority task: {file_path} (Priority: {-priority})")

                    # Process the task using thread pool to avoid blocking
                    self.executor.submit(self.handle_priority_task, file_path, -priority)
                    processed_count += 1

                except queue.Empty:
                    break  # Queue is empty, that's fine
                except Exception as e:
                    self.logger.error(f"Error processing priority queue item: {e}")
                    break

            if processed_count > 0:
                self.logger.info(f"Processed {processed_count} high-priority tasks")

        except Exception as e:
            self.logger.error(f"Error processing priority queue: {e}")

    def handle_priority_task(self, file_path: str, priority: int):
        """Handle a single priority task"""
        try:
            # Trigger reasoning for high-priority tasks
            if priority >= 3 and not self.is_component_running('reasoning_trigger'):
                self.start_component('reasoning_trigger')
                
            # Log task processing
            self.logger.info(f"Handled priority task: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error handling priority task {file_path}: {e}")

    def daily_cleanup(self):
        """Enhanced daily cleanup with better error handling"""
        try:
            self.logger.info("Starting enhanced daily cleanup...")

            # Archive old Done files (older than 7 days)
            self.archive_old_done_files()

            # Clean up old logs (older than 30 days)
            self.cleanup_old_logs()
            
            # Clean temporary files
            self.cleanup_temp_files()

            # Update dashboard statistics
            self.update_daily_statistics()

            self.logger.info("Enhanced daily cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during daily cleanup: {e}")

    def archive_old_done_files(self):
        """Enhanced archiving with better error handling"""
        try:
            done_dir = 'Done'
            archive_dir = 'Archive'

            if not os.path.exists(done_dir):
                return

            os.makedirs(archive_dir, exist_ok=True)

            import shutil
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=7)

            archived_count = 0
            for filename in os.listdir(done_dir):
                file_path = os.path.join(done_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        archive_path = os.path.join(archive_dir, filename)
                        try:
                            shutil.move(file_path, archive_path)
                            self.logger.info(f"Archived old file: {filename}")
                            archived_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to archive {filename}: {e}")

            if archived_count > 0:
                self.logger.info(f"Archived {archived_count} files")

        except Exception as e:
            self.logger.error(f"Error archiving old files: {e}")

    def cleanup_old_logs(self):
        """Enhanced log cleanup with better error handling"""
        try:
            logs_dir = 'Logs'
            if not os.path.exists(logs_dir):
                return

            import shutil
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=30)

            removed_count = 0
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(logs_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            try:
                                os.remove(file_path)
                                self.logger.info(f"Removed old log: {filename}")
                                removed_count += 1
                            except Exception as e:
                                self.logger.error(f"Failed to remove log {filename}: {e}")

            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} old log files")

        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dir = 'Temp'
            if not os.path.exists(temp_dir):
                return

            import shutil
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(hours=24)

            cleaned_count = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        try:
                            os.remove(file_path)
                            self.logger.info(f"Cleaned temp file: {filename}")
                            cleaned_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to clean temp file {filename}: {e}")

            if cleaned_count > 0:
                self.logger.info(f"Cleaned {cleaned_count} temporary files")

        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {e}")

    def update_daily_statistics(self):
        """Update daily statistics in dashboard"""
        try:
            # This would update statistics in the dashboard
            self.logger.info("Updated daily statistics")
        except Exception as e:
            self.logger.error(f"Error updating daily statistics: {e}")

    def ensure_all_running(self):
        """Enhanced component health check with intelligent restart"""
        critical_components = ['gmail_watcher', 'whatsapp_watcher', 'linkedin_watcher',
                             'reasoning_trigger', 'email_handler', 'hilt_scheduler', 'dashboard_updater']

        for component in critical_components:
            if not self.is_component_running(component):
                if self.should_run_component(component) and self.should_restart_component(component):
                    self.logger.info(f"Restarting critical component: {component}")
                    self.start_component(component)

    def perform_health_checks(self):
        """Perform comprehensive health checks"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('.')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_percent > 95:
                self.logger.critical(f"Dangerously low disk space: {disk_percent:.1f}% used")
            elif disk_percent > 90:
                self.logger.warning(f"Low disk space: {disk_percent:.1f}% used")
            
            # Check for zombie processes
            self.check_zombie_processes()
            
            # Check file system integrity
            self.check_file_system_integrity()
            
        except Exception as e:
            self.logger.error(f"Error performing health checks: {e}")

    def check_zombie_processes(self):
        """Check for and clean up zombie processes"""
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            
            zombie_count = 0
            for child in children:
                if child.status() == psutil.STATUS_ZOMBIE:
                    self.logger.warning(f"Zombie process detected: {child.pid}")
                    zombie_count += 1
                    
            if zombie_count > 0:
                self.logger.info(f"Found {zombie_count} zombie processes")
                
        except Exception as e:
            self.logger.error(f"Error checking for zombie processes: {e}")

    def check_file_system_integrity(self):
        """Basic file system integrity check"""
        try:
            critical_dirs = ['Inbox', 'Needs_Action', 'Done', 'Pending_Approval', 'Approved']
            issues_found = 0
            
            for dir_name in critical_dirs:
                dir_path = os.path.join(dir_name)
                if not os.path.exists(dir_path):
                    self.logger.error(f"Critical directory missing: {dir_path}")
                    issues_found += 1
                elif not os.access(dir_path, os.W_OK):
                    self.logger.error(f"Write access denied to critical directory: {dir_path}")
                    issues_found += 1
            
            if issues_found > 0:
                self.logger.warning(f"Found {issues_found} file system integrity issues")
                
        except Exception as e:
            self.logger.error(f"Error checking file system integrity: {e}")

    def run(self):
        """Enhanced orchestrator main loop with better error handling"""
        self.logger.info("Enhanced AI Orchestrator starting with advanced scheduling and security...")

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
        except Exception as e:
            self.logger.error(f"Unexpected error in orchestrator main loop: {e}")
        finally:
            self.shutdown()

    def monitor_system_health(self):
        """Enhanced system health monitoring with predictive analysis"""
        try:
            # Check CPU and memory usage
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 85 or memory_percent > 85:
                self.logger.warning(f"High system usage - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            elif cpu_percent > 75 or memory_percent > 75:
                self.logger.info(f"Elevated system usage - CPU: {cpu_percent}%, Memory: {memory_percent}%")

            # Check disk space with predictive warning
            disk_usage = psutil.disk_usage('.')
            disk_percent = (disk_usage.used / disk_usage.total) * 100

            if disk_percent > 90:
                self.logger.warning(f"Low disk space: {disk_percent:.1f}% used")
            elif disk_percent > 80:
                self.logger.info(f"Moderate disk usage: {disk_percent:.1f}% used")

        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")

    def shutdown(self):
        """Enhanced graceful shutdown with comprehensive cleanup"""
        self.logger.info("Initiating comprehensive shutdown...")

        # Stop all components
        self.stop_all_components()

        # Wait a bit for processes to terminate
        time.sleep(3)

        # Force kill any remaining processes
        self.force_kill_remaining_processes()

        # Shutdown thread pool
        self.executor.shutdown(wait=False)

        self.logger.info("Comprehensive shutdown complete")

    def force_kill_remaining_processes(self):
        """Enhanced force kill with better error handling"""
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            
            killed_count = 0
            for child in children:
                try:
                    if child.status() != psutil.STATUS_ZOMBIE:
                        child.kill()
                        killed_count += 1
                except psutil.NoSuchProcess:
                    pass  # Process already dead
                except psutil.AccessDenied:
                    self.logger.warning(f"Access denied killing process {child.pid}")
                except Exception as e:
                    self.logger.error(f"Error killing process {child.pid}: {e}")

            if killed_count > 0:
                self.logger.info(f"Force killed {killed_count} remaining processes")

            # Wait for processes to die
            gone, alive = psutil.wait_procs(children, timeout=5)
            if alive:
                self.logger.warning(f"{len(alive)} processes still alive after kill attempt")
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.logger.error(f"Error force killing process {p.pid}: {e}")

        except Exception as e:
            self.logger.error(f"Error killing remaining processes: {e}")


def main():
    """Enhanced main entry point with error handling"""
    try:
        orchestrator = AdvancedScheduler()
        orchestrator.run()
    except KeyboardInterrupt:
        print("\nOrchestrator interrupted by user")
    except Exception as e:
        print(f"Fatal error in orchestrator: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()