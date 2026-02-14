# Quick Start Guide: Personal AI Employee in VS Code

## Setting Up Your Environment

### 1. Open the Project in VS Code
- Open VS Code
- Select "File" → "Open Folder"
- Navigate to and select the `AI_Employee_Vault` folder
- You should see the folder structure in the Explorer panel

### 2. Install Python Extension (Recommended)
- Press `Ctrl+Shift+X` to open Extensions
- Search for "Python" by Microsoft
- Click "Install" to get syntax highlighting and debugging support

### 3. Install Required Python Packages
- Open the integrated terminal in VS Code (`Ctrl+`` ` or "Terminal" → "New Terminal")
- Run the following command:
```bash
pip install watchdog
```

## Running the File System Watcher

### Method 1: Using VS Code Terminal
1. Open the integrated terminal (`Ctrl+`` `)
2. Navigate to the vault directory if needed:
   ```bash
   cd AI_Employee_Vault
   ```
3. Run the watcher script:
   ```bash
   python filesystem_watcher.py
   ```
4. Keep the terminal window open to keep the watcher running

### Method 2: Using VS Code's Run and Debug
1. Create a `.vscode/launch.json` file in your project root:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Run File System Watcher",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/filesystem_watcher.py",
               "console": "integratedTerminal"
           }
       ]
   }
   ```
2. Press `F5` or click "Run and Debug" → "Run File System Watcher"

## Working with the Dashboard Updater in VS Code

### 1. Accessing the Dashboard Updater
- Open the integrated terminal in VS Code
- Navigate to the AI_Employee_Vault directory
- Run the dashboard updater script from this terminal to ensure it has access to the vault files

### 2. Example Dashboard Updater Commands
From the terminal in the vault directory, you can run:
```bash
python dashboard_updater.py
```

This script will read all files in Needs_Action and update Dashboard.md with relevant information.

## VS Code Tips for Managing Your AI Employee

### 1. File Management
- Use the Explorer panel to easily navigate between Dashboard.md, Company_Handbook.md, and the three main folders
- Right-click on files to rename, delete, or move them between folders
- Use the search function (`Ctrl+Shift+F`) to find specific content across all vault files

### 2. Markdown Preview
- Click the "Open Preview" button (or press `Ctrl+Shift+V`) when viewing .md files to see formatted content
- Use split view to edit and preview simultaneously

### 3. Integrated Terminal Commands
Useful commands to run in the integrated terminal:
```bash
# Start the file watcher
python filesystem_watcher.py

# List files in Needs_Action
dir Needs_Action  # Windows
ls Needs_Action   # Mac/Linux

# Check the last update to Dashboard
type Dashboard.md  # Windows
cat Dashboard.md   # Mac/Linux
```

## Development Workflow

### Daily Operations
1. **Start the watcher**: Run `python filesystem_watcher.py` in a terminal
2. **Monitor Inbox**: Add files to the Inbox folder for processing
3. **Check Needs_Action**: Review files that need attention
4. **Update Dashboard**: Use the dashboard updater script to update Dashboard.md with new information
5. **Complete tasks**: Move completed files to the Done folder

### Best Practices
- Keep the file system watcher running during your work session
- Regularly update Dashboard.md to maintain an accurate overview
- Follow the guidelines in Company_Handbook.md when processing tasks
- Use the metadata files created by the watcher to understand file context

## Troubleshooting in VS Code

### If the File Watcher Doesn't Work
- Ensure you've installed the watchdog package: `pip install watchdog`
- Check that VS Code has the necessary file system permissions
- Try running VS Code as administrator if you encounter permission issues

### If the Dashboard Updater Isn't Working
- Verify Python is properly installed and accessible from the command line
- Ensure you're running the dashboard updater script from within the AI_Employee_Vault directory
- Check that the Python script has proper permissions to read and write files

### General Issues
- Restart VS Code if you encounter unexpected behavior
- Check the Problems panel (`Ctrl+Shift+M`) for any detected issues
- Use the Output panel to view detailed logs from extensions