import os
import glob
from datetime import datetime

def update_dashboard():
    """
    Reads files in the Needs_Action folder and updates Dashboard.md with relevant information.
    """
    # Get all files in Needs_Action folder
    needs_action_files = glob.glob("Needs_Action/*")

    # Filter out metadata files
    task_files = [f for f in needs_action_files if not os.path.basename(f).endswith('_metadata.md')]

    # Read current dashboard content
    dashboard_path = "Dashboard.md"
    if not os.path.exists(dashboard_path):
        # Create a basic dashboard if it doesn't exist
        create_basic_dashboard()

    with open(dashboard_path, "r", encoding="utf-8") as f:
        dashboard_content = f.read()

    # Split the dashboard content into lines
    lines = dashboard_content.split('\n')
    new_lines = []

    # Flags to track where we are in the dashboard
    in_pending_tasks_section = False
    tasks_table_updated = False
    urgent_items_updated = False

    for i, line in enumerate(lines):
        if "| Task | Priority | Status | Due Date |" in line and not tasks_table_updated:
            # Add the header line
            new_lines.append(line)

            # Add new tasks from Needs_Action folder
            for file_path in task_files:
                filename = os.path.basename(file_path)
                # Add a new row for each file in Needs_Action
                new_task_row = f"| Process file: {filename} | Medium | Pending | ASAP |"
                new_lines.append(new_task_row)

            tasks_table_updated = True
        elif "| Task | Priority | Status | Due Date |" in line and tasks_table_updated:
            # Skip existing task rows since we've already added new ones
            continue
        elif line.strip().startswith('|') and tasks_table_updated and not line.strip().startswith('| Task |'):
            # Skip existing task rows
            continue
        elif "Last updated:" in line:
            # Update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_lines.append(f"**Last updated:** {timestamp}")
        elif "Urgent Items" in line and not urgent_items_updated:
            # Add urgent items from Needs_Action files
            new_lines.append(line)
            for file_path in needs_action_files:
                filename = os.path.basename(file_path)
                if '[URGENT]' in filename.upper() or '_urgent' in filename.lower():
                    new_lines.append(f"- URGENT: Process {filename}")
            urgent_items_updated = True
        elif "Urgent Items" in line and urgent_items_updated:
            # Skip existing urgent items
            continue
        elif line.strip().startswith('- URGENT:') and urgent_items_updated:
            # Skip existing urgent items
            continue
        else:
            new_lines.append(line)

    # Write updated dashboard back to file
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))

    print(f"Dashboard updated with {len(task_files)} new tasks from Needs_Action folder.")

    # Move processed files to Done folder
    for file_path in task_files:
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
        try:
            os.rename(file_path, done_path)
            print(f"Moved {filename} to Done folder.")
        except OSError as e:
            print(f"Error moving {filename} to Done folder: {e}")
            # If we can't move the file, at least try to remove it to prevent reprocessing
            try:
                os.remove(file_path)
                print(f"Deleted {filename} to prevent reprocessing after error.")
            except OSError:
                print(f"Could not delete {filename} either, it may be locked by another process.")

def create_basic_dashboard():
    """Create a basic dashboard file if it doesn't exist."""
    with open("Dashboard.md", "w", encoding="utf-8") as f:
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

if __name__ == "__main__":
    update_dashboard()