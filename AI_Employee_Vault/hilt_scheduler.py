import schedule
import time
import os
import shutil
from datetime import datetime
import threading

class HITLScheduler:
    def __init__(self):
        self.pending_approval_dir = "Pending_Approval"
        self.approved_dir = "Approved"
        self.needs_action_dir = "Needs_Action"
        self.done_dir = "Done"
        
    def check_approvals(self):
        """Check for approved files and move them to Approved directory"""
        print(f"[{datetime.now()}] Checking for approvals...")
        
        for filename in os.listdir(self.pending_approval_dir):
            file_path = os.path.join(self.pending_approval_dir, filename)
            
            # In real implementation, this would check if file was manually approved
            # For demo purposes, we'll simulate checking for approval markers
            if self.is_approved(file_path):
                approved_path = os.path.join(self.approved_dir, filename)
                shutil.move(file_path, approved_path)
                print(f"Approved: {filename} -> {self.approved_dir}")
    
    def is_approved(self, file_path):
        """Check if a file is approved (in real implementation, this would be manual check)"""
        # This is a simplified version - in practice, the user would manually move files
        # from Pending_Approval to Approved to indicate approval
        return False  # Always return False for demo - user moves files manually
    
    def schedule_tasks(self):
        """Setup scheduled tasks"""
        # Schedule various tasks
        schedule.every(1).minutes.do(self.check_approvals)  # Check for approvals every minute
        
        # Add other scheduled tasks as needed
        schedule.every(5).minutes.do(self.cleanup_temp_files)
        schedule.every(10).minutes.do(self.update_dashboard)
        
        print("Scheduler initialized with tasks:")
        print("- Check approvals every 1 minute")
        print("- Cleanup temp files every 5 minutes") 
        print("- Update dashboard every 10 minutes")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        print(f"[{datetime.now()}] Cleaning up temporary files...")
        # Add cleanup logic here
    
    def update_dashboard(self):
        """Update dashboard with current status"""
        print(f"[{datetime.now()}] Updating dashboard...")
        
        # Count files in each directory
        pending_count = len(os.listdir(self.pending_approval_dir))
        approved_count = len(os.listdir(self.approved_dir))
        needs_action_count = len(os.listdir(self.needs_action_dir))
        done_count = len(os.listdir(self.done_dir))
        
        # Update dashboard counters (simplified)
        dashboard_path = "Dashboard.md"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update placeholders (simplified)
            content = content.replace('[count]', str(pending_count + approved_count + needs_action_count))
            content = content.replace('<!-- BALANCE PLACEHOLDER -->', f"${1000 + (pending_count * 100)}")
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.schedule_tasks()
        
        print("Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(1)

def run_hilt_scheduler():
    """Main function to run the HITL scheduler"""
    scheduler = HITLScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    run_hilt_scheduler()