import os
import glob
from datetime import datetime

def update_dashboard():
    """
    Reads files in the Needs_Action folder and updates Dashboard.md with relevant information.
    """
    # Get all files in Needs_Action folder
    needs_action_files = glob.glob("Needs_Action/*")
    
    # Read current dashboard content
    with open("Dashboard.md", "r", encoding="utf-8") as f:
        dashboard_content = f.read()
    
    # Find the pending tasks section in the dashboard
    lines = dashboard_content.split('\n')
    new_lines = []
    in_pending_tasks_section = False
    tasks_table_updated = False
    
    for line in lines:
        if "| Task | Priority | Status | Due Date |" in line:
            in_pending_tasks_section = True
            new_lines.append(line)
            # Add new tasks from Needs_Action folder
            if not tasks_table_updated:
                for file_path in needs_action_files:
                    filename = os.path.basename(file_path)
                    if not filename.endswith('_metadata.md'):  # Skip metadata files
                        # Add a new row for each file in Needs_Action
                        new_task_row = f"| Process file: {filename} | Medium | Pending | ASAP |"
                        new_lines.append(new_task_row)
                tasks_table_updated = True
        elif in_pending_tasks_section and line.strip().startswith('|'):
            # Skip existing task rows since we're replacing them
            continue
        elif in_pending_tasks_section and line.strip() == '':
            # End of the table, reset flag
            in_pending_tasks_section = False
            new_lines.append(line)
        elif "Last updated:" in line:
            # Update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_lines.append(f"Last updated: {timestamp}")
        elif "Urgent Items" in line:
            # Add urgent items from Needs_Action files
            new_lines.append(line)
            for file_path in needs_action_files:
                filename = os.path.basename(file_path)
                if '[URGENT]' in filename.upper() or '_urgent' in filename.lower():
                    new_lines.append(f"- URGENT: Process {filename}")
        else:
            new_lines.append(line)
    
    # Write updated dashboard back to file
    with open("Dashboard.md", "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))
    
    print(f"Dashboard updated with {len([f for f in needs_action_files if not f.endswith('_metadata.md')])} new tasks from Needs_Action folder.")
    
    # Move processed files to Done folder
    for file_path in needs_action_files:
        if not file_path.endswith('_metadata.md'):  # Don't move metadata files
            filename = os.path.basename(file_path)
            done_path = os.path.join("Done", filename)
            
            # Handle duplicate filenames in Done folder
            counter = 1
            original_done_path = done_path
            while os.path.exists(done_path):
                name, ext = os.path.splitext(original_done_path)
                done_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Move the file to Done folder
            os.rename(file_path, done_path)
            print(f"Moved {filename} to Done folder.")

if __name__ == "__main__":
    update_dashboard()