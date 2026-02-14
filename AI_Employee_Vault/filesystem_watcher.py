import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

class FileDropHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder, needs_action_folder):
        self.inbox_folder = inbox_folder
        self.needs_action_folder = needs_action_folder

    def on_created(self, event):
        if not event.is_directory:
            self.process_new_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            # Handle files moved into the inbox
            if event.dest_path.startswith(self.inbox_folder):
                self.process_new_file(event.dest_path)

    def process_new_file(self, file_path):
        """Process a new file dropped in the inbox folder"""
        try:
            # Get file information
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1]
            
            print(f"New file detected: {file_name}")
            
            # Copy file to Needs_Action folder
            destination_path = os.path.join(self.needs_action_folder, file_name)
            
            # Handle duplicate filenames
            counter = 1
            original_destination = destination_path
            while os.path.exists(destination_path):
                name, ext = os.path.splitext(original_destination)
                destination_path = f"{name}_{counter}{ext}"
                counter += 1
            
            shutil.copy2(file_path, destination_path)
            print(f"Copied {file_name} to Needs_Action folder")
            
            # Create metadata file
            metadata_filename = f"{os.path.splitext(file_name)[0]}_metadata.md"
            metadata_path = os.path.join(self.needs_action_folder, metadata_filename)
            
            with open(metadata_path, 'w', encoding='utf-8') as meta_file:
                meta_file.write(f"""# File Metadata

## Original Information
- **Original Name:** {file_name}
- **File Type:** {file_ext if file_ext else 'Unknown'}
- **Size:** {file_size} bytes
- **Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status:** New file in queue
- **Action Required:** Review and process

## Description
This file was automatically detected in the Inbox folder and moved to Needs_Action for processing.
""")
            
            print(f"Created metadata file: {metadata_filename}")
            
            # Optionally delete the original file from inbox after copying
            # Uncomment the next line if you want to move instead of copy
            # os.remove(file_path)
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")


def main():
    # Define folder paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    inbox_folder = os.path.join(base_dir, "Inbox")
    needs_action_folder = os.path.join(base_dir, "Needs_Action")
    
    # Ensure directories exist
    os.makedirs(inbox_folder, exist_ok=True)
    os.makedirs(needs_action_folder, exist_ok=True)
    
    # Create event handler
    event_handler = FileDropHandler(inbox_folder, needs_action_folder)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, inbox_folder, recursive=False)
    
    # Start the observer
    observer.start()
    print(f"File system watcher started. Monitoring: {inbox_folder}")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFile system watcher stopped.")
    
    observer.join()


if __name__ == "__main__":
    main()