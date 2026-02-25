# Enhanced AI Employee Vault - Advanced Automation System

## Overview
This is an enhanced version of the AI employee system that monitors multiple inputs (files, emails, social media) and processes tasks automatically using AI reasoning. The system has been significantly improved with better security, performance, and reliability.

## Key Enhancements

### 1. Security Improvements
- **Secure Configuration Management**: Encrypted storage for sensitive data
- **Input Validation**: Protection against prompt injection and malicious input
- **File Size Limits**: Configurable limits to prevent resource exhaustion
- **Access Controls**: Improved file system permissions and validation

### 2. Performance Optimizations
- **Async/Await Architecture**: Non-blocking I/O operations for better responsiveness
- **Caching Mechanisms**: Reduce redundant computations and file operations
- **Resource Monitoring**: Dynamic adjustment of operations based on system load
- **Efficient File Processing**: Batch processing and optimized algorithms

### 3. Reliability Features
- **Enhanced Error Handling**: Comprehensive error catching and recovery
- **Automatic Restart Logic**: Intelligent restart mechanisms with exponential backoff
- **Health Monitoring**: Continuous system health checks
- **Zombie Process Cleanup**: Automatic cleanup of orphaned processes

### 4. Code Quality Improvements
- **Type Hints**: Full type annotations for better code understanding
- **Modular Design**: Better separation of concerns and reusable components
- **Comprehensive Logging**: Detailed logging with security and performance metrics
- **Testing Framework**: Enhanced test coverage and validation

## Prerequisites
- Python 3.8+
- Ollama with Qwen model (for AI reasoning) - optional but recommended
- Windows, macOS, or Linux operating system
- Additional dependencies as specified in requirements.txt

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

### 3. Enhanced Folder Structure
The system uses the following enhanced folder structure:
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
├── Temp/                 # Temporary files
├── Backup/               # Backup files
└── Logs/                 # System logs
```

### 4. Initialize Directories
Run the setup script to create all required directories:
```bash
python setup_directories.py
```

### 5. Running the Enhanced System
Start the entire system with a single command using the enhanced main:
```bash
python enhanced_main.py
```

Alternatively, you can run individual enhanced components:
- Enhanced file system watcher: `python enhanced_filesystem_watcher.py`
- Enhanced dashboard updater: `python enhanced_dashboard_updater.py`
- Enhanced orchestrator: `python enhanced_orchestrator.py`
- Enhanced reasoning engine: `python enhanced_reasoning_trigger.py`

## How It Works

### Enhanced File Processing Flow
1. User drops a file in the `Inbox` folder
2. The enhanced `filesystem_watcher.py` detects the new file with security validation
3. The file is securely copied to the `Needs_Action` folder
4. A metadata file is created alongside the copied file
5. The enhanced `reasoning_trigger.py` generates a detailed plan for the task using AI
6. The plan goes to `Pending_Approval` for human review
7. After approval, the task is executed
8. The enhanced `dashboard_updater.py` updates the dashboard with progress and metrics

### Multi-Source Input Processing
The system monitors multiple input sources:
- **File System**: Files dropped in the Inbox folder with validation
- **Gmail**: Monitored for new emails requiring action
- **WhatsApp**: Messages monitored for tasks
- **LinkedIn**: Posts and messages monitored for opportunities

### Enhanced AI Reasoning and Planning
When a task enters `Needs_Action`, the system:
1. Uses AI to analyze the request with security validation
2. Generates a detailed step-by-step plan with risk assessment
3. Submits the plan for human approval
4. Executes approved plans automatically
5. Tracks progress and updates the dashboard

## Configuration

### Environment Variables
Configure the `.env` file with:
- API keys and credentials for external services
- Scheduling intervals for different components
- Resource limits and thresholds
- Priority keywords for task classification
- Security settings (file size limits, timeouts, retry counts)

### Company Handbook
Update `Company_Handbook.md` with your organization's rules and procedures that the AI employee should follow.

## Testing the Enhanced System

### Quick Start Test
1. Start the enhanced system: `python enhanced_main.py`
2. Create a test file in the Inbox folder:
   ```bash
   echo "Process this document for me" > Inbox/test_task.txt
   ```
3. Check that the file moves to Needs_Action and a plan is generated

### Component Tests
Each enhanced component can be tested individually:
- File watcher: Drop files in Inbox and verify they're detected securely
- Dashboard: Run `python enhanced_dashboard_updater.py` to update the dashboard
- Reasoning: Add files to Needs_Action and verify plans are generated with proper structure

## Troubleshooting

### Common Issues
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Missing directories**: Run `python setup_directories.py`
- **Dashboard not updating**: Ensure `Dashboard.md` exists in the root
- **Components not starting**: Check the logs in the `Logs/` directory

### Error Logging
System errors are logged to the `Logs/` directory with timestamps and detailed context. Check these files if components fail to start or behave unexpectedly.

### Resource Management
The system monitors CPU, memory, and disk usage. If resources are low, non-critical components may pause automatically. Adjust thresholds in the `.env` file if needed.

## Architecture

### Enhanced Core Components
- **Enhanced Orchestrator**: Manages all system components with intelligent restart and health monitoring
- **Enhanced File System Watcher**: Monitors the Inbox for new files with security validation
- **Enhanced Reasoning Engine**: Generates plans for tasks using AI with security and quality checks
- **Enhanced Dashboard Updater**: Maintains the status dashboard with real-time metrics
- **Enhanced Service Watchers**: Monitor Gmail, WhatsApp, LinkedIn for new inputs
- **Enhanced Approval Handler**: Processes approved plans for execution

### Data Flow
Inputs → Needs_Action → Planning → Approval → Execution → Done → Archive

## Security Considerations
- Store credentials securely in the `.env` file (not committed to version control)
- Review all AI-generated plans before approval
- Monitor system logs regularly for security events
- Limit system permissions to necessary operations only
- Validate all inputs to prevent injection attacks
- Implement file size limits to prevent resource exhaustion

## Performance Tuning
- Adjust `MAX_FILE_SIZE` in .env to control file processing limits
- Tune `AI_TIMEOUT` to balance between patience and responsiveness
- Configure `MAX_RETRIES` and `RETRY_DELAY` for resilient operations
- Monitor resource usage and adjust component intervals as needed

## Contributing
Enhanced components are designed to be modular and extensible. When adding new features:
1. Follow the existing code patterns and architecture
2. Add appropriate error handling and logging
3. Include security validations where appropriate
4. Update documentation and tests
5. Follow the async/await patterns for I/O operations