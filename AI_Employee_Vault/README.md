# AI Employee Vault - Advanced Automation System

## Overview
This is an advanced AI employee system that monitors multiple inputs (files, emails, social media) and processes tasks automatically using AI reasoning. The system consists of:
- A vault folder structure for organizing tasks
- Multiple watchers for different input sources (files, Gmail, WhatsApp, LinkedIn)
- AI-powered reasoning and planning engine
- Dashboard for monitoring and status updates
- Approval workflow for sensitive actions

## Prerequisites
- Python 3.8+
- Ollama with Qwen model (for AI reasoning) - optional but recommended
- Windows, macOS, or Linux operating system

## Setup

### 1. Install Dependencies
```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
```

Update the `.env` file with your actual credentials for Gmail, LinkedIn, etc.

### 3. Folder Structure
The system uses the following folder structure:
```
AI_Employee_Vault/
├── Dashboard.md          # Real-time summary
├── Company_Handbook.md   # Rules and guidelines
├── SKILL.md              # AI skill definitions
├── Inbox/                # Drop files here for processing
├── Needs_Action/         # Files awaiting processing
├── Plans/                # Generated action plans
├── Pending_Approval/     # Plans awaiting human approval
├── Approved/             # Approved plans ready for execution
├── Done/                 # Completed tasks
├── Archive/              # Archived completed tasks
└── Logs/                 # System logs
```

### 4. Initialize Directories
Run the setup script to create all required directories:
```bash
python setup_directories.py
```

### 5. Running the System
Start the entire system with a single command:
```bash
python main.py
```

Alternatively, you can run individual components:
- File system watcher: `python filesystem_watcher.py`
- Dashboard updater: `python dashboard_updater.py`
- Orchestrator: `python orchestrator.py`

## How It Works

### File Processing Flow
1. User drops a file in the `Inbox` folder
2. The `filesystem_watcher.py` detects the new file
3. The file is copied to the `Needs_Action` folder
4. A metadata file is created alongside the copied file
5. The `reasoning_trigger.py` generates a plan for the task
6. The plan goes to `Pending_Approval` for human review
7. After approval, the task is executed
8. The `dashboard_updater.py` updates the dashboard with progress

### Multi-Source Input Processing
The system monitors multiple input sources:
- **File System**: Files dropped in the Inbox folder
- **Gmail**: Monitored for new emails requiring action
- **WhatsApp**: Messages monitored for tasks
- **LinkedIn**: Posts and messages monitored for opportunities

### AI Reasoning and Planning
When a task enters `Needs_Action`, the system:
1. Uses AI to analyze the request
2. Generates a detailed step-by-step plan
3. Submits the plan for human approval
4. Executes approved plans automatically

## Configuration

### Environment Variables
Configure the `.env` file with:
- API keys and credentials for external services
- Scheduling intervals for different components
- Resource limits and thresholds
- Priority keywords for task classification

### Company Handbook
Update `Company_Handbook.md` with your organization's rules and procedures that the AI employee should follow.

## Testing the System

### Quick Start Test
1. Start the system: `python main.py`
2. Create a test file in the Inbox folder:
   ```bash
   echo "Process this document for me" > Inbox/test_task.txt
   ```
3. Check that the file moves to Needs_Action and a plan is generated

### Component Tests
Each component can be tested individually:
- File watcher: Drop files in Inbox and verify they're detected
- Dashboard: Run `python dashboard_updater.py` to update the dashboard
- Reasoning: Add files to Needs_Action and verify plans are generated

## Troubleshooting

### Common Issues
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Missing directories**: Run `python setup_directories.py`
- **Dashboard not updating**: Ensure `Dashboard.md` exists in the root
- **Components not starting**: Check the logs in the `Logs/` directory

### Error Logging
System errors are logged to the `Logs/` directory with timestamps. Check these files if components fail to start or behave unexpectedly.

### Resource Management
The system monitors CPU, memory, and disk usage. If resources are low, non-critical components may pause automatically. Adjust thresholds in the `.env` file if needed.

## Architecture

### Core Components
- **Orchestrator**: Manages all system components and their lifecycle
- **File System Watcher**: Monitors the Inbox for new files
- **Reasoning Engine**: Generates plans for tasks using AI
- **Dashboard Updater**: Maintains the status dashboard
- **Service Watchers**: Monitor Gmail, WhatsApp, LinkedIn for new inputs
- **Approval Handler**: Processes approved plans for execution

### Data Flow
Inputs → Needs_Action → Planning → Approval → Execution → Done → Archive

## Security Considerations
- Store credentials securely in the `.env` file (not committed to version control)
- Review all AI-generated plans before approval
- Monitor system logs regularly
- Limit system permissions to necessary operations only