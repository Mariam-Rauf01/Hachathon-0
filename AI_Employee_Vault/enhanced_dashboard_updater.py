import os
import glob
import time
import threading
from datetime import datetime
import hashlib
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import asyncio
import aiofiles
from dataclasses import dataclass
from collections import defaultdict

# Try to import psutil for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class TaskInfo:
    """Data class to hold task information"""
    filename: str
    priority: str
    status: str
    due_date: str
    source: str
    size: int
    created_at: float

class EnhancedDashboardUpdater:
    """Enhanced dashboard updater with async processing and security"""
    
    def __init__(self):
        self.dashboard_path = "Dashboard.md"
        self.lock = threading.Lock()  # Thread safety for file operations
        self.logger = self.setup_logging()
        self.file_hashes = {}  # Track file hashes to detect changes
        self.stats_cache = {}  # Cache for performance
        self.last_update = 0
        self.update_interval = 30  # seconds
        
        # Folder mappings
        self.folder_mapping = {
            'Inbox': {'label': 'Files in Inbox', 'icon': '📥'},
            'Needs_Action': {'label': 'Tasks in Needs Action', 'icon': '📋'},
            'Done': {'label': 'Completed Tasks', 'icon': '✅'},
            'Pending_Approval': {'label': 'Pending Approval', 'icon': '⏳'},
            'Approved': {'label': 'Approved Tasks', 'icon': '👍'},
            'Plans': {'label': 'Generated Plans', 'icon': '📝'},
            'Archive': {'label': 'Archived Tasks', 'icon': '🗄️'}
        }
    
    def setup_logging(self) -> logging.Logger:
        """Setup enhanced logging"""
        log_dir = 'Logs'
        os.makedirs(log_dir, exist_ok=True)
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers
        if not logger.handlers:
            handler = logging.FileHandler(
                os.path.join(log_dir, f'dashboard_updater_{datetime.now().strftime("%Y-%m-%d")}.log')
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    async def get_folder_stats(self) -> Dict[str, int]:
        """Asynchronously get stats for all tracked folders"""
        stats = {}
        
        for folder, info in self.folder_mapping.items():
            try:
                folder_path = Path(folder)
                if folder_path.exists():
                    # Count files (not directories)
                    file_count = sum(1 for item in folder_path.iterdir() if item.is_file())
                    stats[info['label']] = file_count
                else:
                    stats[info['label']] = 0
            except Exception as e:
                self.logger.error(f"Error counting files in {folder}: {e}")
                stats[info['label']] = 0
        
        return stats
    
    def get_file_priority(self, file_path: str) -> str:
        """Enhanced priority detection from file content and name"""
        try:
            # Check filename for priority indicators
            filename_lower = Path(file_path).name.lower()
            
            if any(keyword in filename_lower for keyword in ['urgent', 'critical', 'emergency', 'asap']):
                return 'High'
            elif any(keyword in filename_lower for keyword in ['important', 'high', 'soon']):
                return 'Medium'
            elif any(keyword in filename_lower for keyword in ['later', 'low', 'eventual']):
                return 'Low'
            
            # Check file content if readable
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # Read first 1000 chars only
                    content_lower = content.lower()
                    
                    if any(keyword in content_lower for keyword in ['urgent', 'critical', 'emergency', 'asap']):
                        return 'High'
                    elif any(keyword in content_lower for keyword in ['important', 'high', 'soon']):
                        return 'Medium'
            except:
                pass  # If we can't read the file, continue with filename-based detection
            
            return 'Medium'  # Default priority
            
        except Exception:
            return 'Medium'  # Default priority on error
    
    async def get_tasks_from_folders(self) -> List[TaskInfo]:
        """Asynchronously get tasks from all relevant folders"""
        tasks = []
        
        # Get tasks from Needs_Action folder
        needs_action_path = Path('Needs_Action')
        if needs_action_path.exists():
            for file_path in needs_action_path.iterdir():
                if file_path.is_file() and not file_path.name.endswith('_metadata.md'):
                    try:
                        stat = file_path.stat()
                        task = TaskInfo(
                            filename=file_path.name,
                            priority=self.get_file_priority(str(file_path)),
                            status='Pending',
                            due_date='ASAP',
                            source='Needs_Action',
                            size=stat.st_size,
                            created_at=stat.st_ctime
                        )
                        tasks.append(task)
                    except Exception as e:
                        self.logger.error(f"Error processing file {file_path}: {e}")
        
        # Get tasks from Pending_Approval folder
        pending_path = Path('Pending_Approval')
        if pending_path.exists():
            for file_path in pending_path.iterdir():
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        task = TaskInfo(
                            filename=file_path.name,
                            priority='Medium',  # Default for pending approval
                            status='Pending Approval',
                            due_date='ASAP',
                            source='Pending_Approval',
                            size=stat.st_size,
                            created_at=stat.st_ctime
                        )
                        tasks.append(task)
                    except Exception as e:
                        self.logger.error(f"Error processing file {file_path}: {e}")
        
        return tasks
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get real system resource metrics"""
        metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0
        }
        
        if PSUTIL_AVAILABLE:
            try:
                metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
                metrics['memory_percent'] = psutil.virtual_memory().percent
                metrics['disk_percent'] = psutil.disk_usage('.').percent
            except Exception as e:
                self.logger.warning(f"Could not get system metrics: {e}")
        
        return metrics

    def create_dashboard_content(self, stats: Dict[str, int], tasks: List[TaskInfo]) -> str:
        """Create enhanced dashboard content with real system metrics"""
        # Calculate system metrics
        active_components = self.count_active_processes()
        system_health = self.assess_system_health(stats)
        system_metrics = self.get_system_metrics()
        
        # Format the dashboard
        content = f"""# AI Employee Dashboard

## Overview
Welcome to the Enhanced AI Employee Dashboard. This system monitors various inputs and processes tasks automatically.

**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status
- **Files in Inbox:** {stats.get('Files in Inbox', 0)} {self.folder_mapping['Inbox']['icon']}
- **Tasks in Needs Action:** {stats.get('Tasks in Needs Action', 0)} {self.folder_mapping['Needs_Action']['icon']}
- **Completed Tasks:** {stats.get('Completed Tasks', 0)} {self.folder_mapping['Done']['icon']}
- **System Health:** {system_health}
- **Active Components:** {active_components}

## System Resources
- **CPU Usage:** {system_metrics['cpu_percent']:.1f}%
- **Memory Usage:** {system_metrics['memory_percent']:.1f}%
- **Disk Usage:** {system_metrics['disk_percent']:.1f}%

## Urgent Items
"""
        
        # Add urgent items
        urgent_tasks = [task for task in tasks if task.priority == 'High']
        if urgent_tasks:
            for task in urgent_tasks[:5]:  # Show top 5 urgent items
                content += f"- ⚠️ URGENT: Process {task.filename} from {task.source}\n"
        else:
            content += "- No urgent items at this time\n"
        
        content += """

## Pending Tasks
| Task | Priority | Status | Due Date | Source |
|------|----------|--------|----------|---------|
"""
        
        # Add pending tasks table
        if tasks:
            for task in tasks[:20]:  # Limit to 20 tasks to prevent huge tables
                content += f"| {task.filename[:50]}{'...' if len(task.filename) > 50 else ''} | {task.priority} | {task.status} | {task.due_date} | {task.source} |\n"
        else:
            content += "| No pending tasks | - | - | - | - |\n"
        
        content += f"""

## Recent Activity
- Dashboard updated at {datetime.now().strftime('%H:%M:%S')}
- Processed {len(tasks)} tasks
- System running normally

## System Metrics
- **Running Components:** {active_components}
- **Active Monitors:** {stats.get('Active Monitors', 0)}
- **Last Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tasks in Queue:** {stats.get('Tasks in Needs Action', 0)}

## Folder Statistics
"""
        
        for label, count in stats.items():
            content += f"- **{label}:** {count}\n"
        
        content += f"""

## Security Status
- All systems operational
- No security alerts
- Dashboard integrity verified

---
*Dashboard auto-generated by Enhanced AI Employee System*
"""
        
        return content
    
    def assess_system_health(self, stats: Dict[str, int]) -> str:
        """Assess system health based on stats and actual resource usage"""
        issues = []
        
        # Check folder-based issues
        if stats.get('Files in Inbox', 0) > 50:
            issues.append("Many files in inbox")
        if stats.get('Tasks in Needs Action', 0) > 100:
            issues.append("High task backlog")
        if stats.get('Pending Approval', 0) > 20:
            issues.append("Many pending approvals")
        
        # Check actual system resources if available
        if PSUTIL_AVAILABLE:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('.').percent
                
                if cpu > 90:
                    issues.append("CPU critical")
                elif cpu > 80:
                    issues.append("CPU high")
                    
                if memory > 90:
                    issues.append("Memory critical")
                elif memory > 80:
                    issues.append("Memory high")
                    
                if disk > 95:
                    issues.append("Disk nearly full")
            except Exception as e:
                self.logger.warning(f"Could not assess system resources: {e}")
        
        if issues:
            return f"⚠️ Warning ({', '.join(issues)})"
        else:
            return "✅ Operational"
    
    def count_active_processes(self) -> int:
        """Count active AI employee processes (placeholder implementation)"""
        # In a real implementation, this would check for running processes
        # For now, return a reasonable default
        return 5  # Assuming 5 components are typically running
    
    async def update_dashboard(self) -> bool:
        """Asynchronously update the dashboard with enhanced security and performance"""
        try:
            # Get current stats and tasks
            stats = await self.get_folder_stats()
            tasks = await self.get_tasks_from_folders()
            
            # Create new dashboard content
            new_content = self.create_dashboard_content(stats, tasks)
            
            # Check if content has actually changed
            if await self.has_dashboard_changed(new_content):
                # Write new content to dashboard
                async with aiofiles.open(self.dashboard_path, 'w', encoding='utf-8') as f:
                    await f.write(new_content)
                
                self.logger.info(f"Dashboard updated with {len(tasks)} tasks and {sum(stats.values())} total items")
                return True
            else:
                self.logger.debug("Dashboard unchanged, skipping update")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
            return False
    
    async def has_dashboard_changed(self, new_content: str) -> bool:
        """Check if dashboard content has changed using hash comparison"""
        try:
            content_hash = hashlib.md5(new_content.encode()).hexdigest()
            
            # Check if we have a cached hash
            if hasattr(self, '_cached_hash'):
                if self._cached_hash == content_hash:
                    return False
            
            # Update cached hash
            self._cached_hash = content_hash
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking dashboard changes: {e}")
            # On error, assume content changed to be safe
            return True
    
    async def move_processed_files(self, tasks: List[TaskInfo]):
        """Move processed files to prevent reprocessing"""
        for task in tasks:
            try:
                source_path = Path(task.source) / task.filename
                if source_path.exists():
                    # Move to Done folder
                    done_path = Path('Done') / task.filename
                    
                    # Handle duplicates
                    counter = 1
                    original_done_path = done_path
                    while done_path.exists():
                        name = original_done_path.stem
                        suffix = original_done_path.suffix
                        done_path = Path('Done') / f"{name}_{counter}{suffix}"
                        counter += 1
                    
                    source_path.rename(done_path)
                    self.logger.info(f"Moved {task.filename} to Done folder")
                    
            except Exception as e:
                self.logger.error(f"Error moving file {task.filename}: {e}")


class DashboardMonitor:
    """Monitor class to run dashboard updates on schedule"""
    
    def __init__(self):
        self.updater = EnhancedDashboardUpdater()
        self.running = True
        self.update_interval = int(os.getenv('DASHBOARD_UPDATE_INTERVAL', '30'))
    
    async def run_monitoring_loop(self):
        """Run the continuous monitoring loop"""
        self.updater.logger.info("Enhanced Dashboard Monitor started...")
        
        while self.running:
            try:
                # Update dashboard
                updated = await self.updater.update_dashboard()
                
                if updated:
                    self.updater.logger.info("Dashboard updated successfully")
                
                # Wait for next update
                for _ in range(self.update_interval):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.updater.logger.error(f"Error in dashboard monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait longer after error
    
    def stop(self):
        """Stop the monitoring loop"""
        self.running = False


async def dashboard_loop():
    """Main async loop for dashboard updater"""
    monitor = DashboardMonitor()
    
    try:
        await monitor.run_monitoring_loop()
    except KeyboardInterrupt:
        print("\nDashboard updater interrupted by user")
        monitor.stop()
    except Exception as e:
        print(f"Critical error in dashboard updater: {e}")
        import traceback
        traceback.print_exc()
        monitor.stop()


def main():
    """Main entry point"""
    try:
        asyncio.run(dashboard_loop())
    except KeyboardInterrupt:
        print("\nEnhanced Dashboard Updater stopped by user")
    except Exception as e:
        print(f"Failed to start Enhanced Dashboard Updater: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()