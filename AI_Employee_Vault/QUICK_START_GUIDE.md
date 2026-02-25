# Quick Start Guide - AI Employee Vault

## Getting Started in 5 Minutes

Follow these simple steps to get your AI Employee system up and running quickly.

### Step 1: Clone and Navigate
```bash
cd AI_Employee_Vault
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Directories
```bash
python setup_directories.py
```

### Step 4: Start the System
```bash
python main.py
```

### Step 5: Test the System
In a new terminal, create a test task:
```bash
echo "Send an email to john@example.com saying hello" > Inbox/test_task.txt
```

Watch as the system automatically:
1. Detects your task
2. Creates a plan
3. Updates the dashboard

## Understanding the Flow

1. **Inbox** → Drop files here to create tasks
2. **Needs_Action** → Tasks awaiting processing
3. **Plans** → AI-generated action plans
4. **Pending_Approval** → Plans awaiting human approval
5. **Approved** → Approved plans ready for execution
6. **Done** → Completed tasks
7. **Dashboard.md** → Real-time status view

## Essential Commands

- Start everything: `python main.py`
- Check dashboard: `cat Dashboard.md`
- Add a task: `echo "your task" > Inbox/task.txt`
- View logs: Check the `Logs/` directory

## Troubleshooting Quick Fixes

- **System won't start**: Run `pip install -r requirements.txt`
- **Dashboard not updating**: Ensure `Dashboard.md` exists
- **Tasks not processing**: Check that all directories exist with `python setup_directories.py`

## Next Steps

1. Customize `Company_Handbook.md` with your business rules
2. Update `.env` with your service credentials
3. Modify `SKILL.md` with custom AI prompts for your use cases
4. Explore individual components: `filesystem_watcher.py`, `reasoning_trigger.py`, etc.

That's it! Your AI Employee is now ready to automate tasks.