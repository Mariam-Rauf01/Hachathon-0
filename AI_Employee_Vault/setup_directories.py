import os

def setup_directories():
    """Create all required directories for the AI Employee system."""
    directories = [
        "Inbox",
        "Needs_Action", 
        "Done",
        "Pending_Approval",
        "Approved",
        "Plans",
        "Logs",
        "Archive"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

if __name__ == "__main__":
    setup_directories()
    print("Directory setup complete!")