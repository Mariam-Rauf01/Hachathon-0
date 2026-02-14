# Personal AI Employee - Bronze Tier

## Overview
This is a simple AI employee system that monitors a file system and processes tasks using Claude Code. The system consists of:
- A vault folder structure for organizing tasks
- A file system watcher that detects new files
- Claude Code skills for processing tasks

## Prerequisites
- Python 3.13+
- Claude Code installed
- Node.js v24+ (optional, for advanced features)
- GitHub Desktop (for version control)

## Setup

### 1. Install Dependencies
```bash
pip install watchdog
```

### 2. Folder Structure
The system uses the following folder structure:
```
AI_Employee_Vault/
├── Dashboard.md          # Real-time summary
├── Company_Handbook.md   # Rules and guidelines
├── SKILL.md              # Claude Code skills definition
├── Inbox/                # Drop files here for processing
├── Needs_Action/         # Files awaiting processing
└── Done/                 # Completed tasks
```

### 3. Running the File System Watcher
```bash
cd AI_Employee_Vault
python filesystem_watcher.py
```
Keep this running in a separate terminal window.

### 4. Using the Dashboard Updater
Run the dashboard updater script from inside the vault directory:
```bash
cd AI_Employee_Vault
python dashboard_updater.py
```

## How It Works

### File Processing Flow
1. User drops a file in the `Inbox` folder
2. The `filesystem_watcher.py` detects the new file
3. The file is copied to the `Needs_Action` folder
4. A metadata file is created alongside the copied file
5. The `dashboard_updater.py` script processes items in `Needs_Action` and updates the dashboard

## How It Works

### File Processing Flow
1. User drops a file in the `Inbox` folder
2. The `filesystem_watcher.py` detects the new file
3. The file is copied to the `Needs_Action` folder
4. A metadata file is created alongside the copied file
5. The `dashboard_updater.py` script processes items in `Needs_Action` and updates the dashboard

## Testing the System

### Test Scenario 1: File Drop Processing
1. Ensure the file system watcher is running:
   ```bash
   python filesystem_watcher.py
   ```
2. Create a test file in the Inbox folder:
   ```bash
   echo "Test file content" > Inbox/test_file.txt
   ```
3. Check that the file was copied to Needs_Action along with its metadata file

### Test Scenario 2: Dashboard Updater Processing
1. Place a file in Needs_Action (or let the watcher put one there)
2. Run the dashboard updater script to process the file:
   ```bash
   python dashboard_updater.py
   ```

### Test Scenario 3: Full Workflow
1. Start the file system watcher
2. Drop a file in the Inbox folder
3. Wait for the watcher to process it
4. Run the dashboard updater script to process the newly created file in Needs_Action
5. Verify that Dashboard.md was updated appropriately

## Troubleshooting

### File Watcher Issues
- If the file watcher doesn't detect new files, ensure you have proper file permissions
- On some systems, you may need to run with elevated privileges

### Claude Integration
- Make sure Claude Code is properly installed and accessible from your command line
- Run Claude from within the AI_Employee_Vault directory to ensure it has access to the vault files

### Common Errors
- "Permission denied": Check file permissions for the vault directories
- "Module not found": Install missing Python packages with pip
- "File not found": Ensure file paths are correct and relative to the vault root