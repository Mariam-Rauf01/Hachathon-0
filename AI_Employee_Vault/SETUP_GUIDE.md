# Silver Tier AI Employee Setup Guide

## Prerequisites

### System Requirements
- Python 3.13+ installed
- Node.js (for optional Node.js components)
- Git for Windows
- Ollama (for local Qwen model) - optional but recommended

### Python Dependencies
```bash
pip install google-api-python-client google-auth-oauthlib watchdog playwright schedule smtplib python-dotenv
playwright install
```

### Environment Variables
Create a `.env` file in the AI_Employee_Vault directory:
```env
# Gmail API
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# LinkedIn Settings
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Ollama Settings
OLLAMA_MODEL=qwen:latest
```

## Setup Instructions

### 1. Download and Install Ollama (Optional but Recommended)
```bash
# Download from https://ollama.ai
# Install and run: ollama serve
# Pull Qwen model: ollama pull qwen:latest
```

### 2. Configure Gmail API
1. Go to Google Cloud Console
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials.json and place in AI_Employee_Vault directory

### 3. Configure Email Settings
1. Enable 2-factor authentication on Gmail
2. Generate app password for SMTP
3. Update .env file with credentials

### 4. Configure LinkedIn (Optional)
1. Update .env file with LinkedIn credentials
2. Note: LinkedIn may require additional security measures

## Running the System

### 1. Start Individual Components

**Gmail Watcher:**
```bash
cd AI_Employee_Vault
python gmail_watcher.py
```

**WhatsApp Watcher:**
```bash
cd AI_Employee_Vault
python whatsapp_watcher.py
```

**Reasoning Trigger:**
```bash
cd AI_Employee_Vault
python reasoning_trigger.py
```

**Email Handler:**
```bash
cd AI_Employee_Vault
python email_handler.py
```

**LinkedIn Poster:**
```bash
cd AI_Employee_Vault
python linkedin_poster.py
```

**HITL Scheduler:**
```bash
cd AI_Employee_Vault
python hilt_scheduler.py
```

### 2. Run All Components (Recommended)
Create a master script `run_all.py`:
```python
import subprocess
import threading
import sys

def run_script(script_name):
    subprocess.run([sys.executable, script_name])

scripts = [
    'gmail_watcher.py',
    'whatsapp_watcher.py', 
    'reasoning_trigger.py',
    'email_handler.py',
    'linkedin_poster.py',
    'hilt_scheduler.py'
]

threads = []
for script in scripts:
    thread = threading.Thread(target=run_script, args=(script,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Testing Instructions

### Test 1: Basic File Processing
1. Create a test file in `Inbox`:
```bash
echo "Test task: Send email to john@example.com about project update" > "AI_Employee_Vault/Inbox/test_task.txt"
```

2. Wait for system to process:
   - File moves to `Needs_Action`
   - Reasoning trigger creates plan in `Plans`
   - Move plan to `Pending_Approval`
   - Manually move to `Approved` to trigger action

### Test 2: Email Sending
1. Create email task in `Approved`:
```bash
echo "TO: test@example.com
SUBJECT: Test Email
BODY: This is a test email from AI Employee." > "AI_Employee_Vault/Approved/test_email.txt"
```

2. Email handler should process and send the email

### Test 3: LinkedIn Posting (Manual Approval Required)
1. Create post task in `Approved`:
```bash
echo "POST: This is a test LinkedIn post from our AI Employee system
HASHTAGS: #AI #Automation #Business" > "AI_Employee_Vault/Approved/test_linkedin_post.txt"
```

2. LinkedIn poster should create the post

### Test 4: Gmail Monitoring
1. Send email to monitored account
2. Gmail watcher should create task in `Needs_Action`

### Test 5: WhatsApp Monitoring
1. Receive WhatsApp message (requires browser access)
2. WhatsApp watcher should create task in `Needs_Action`

## Approval Workflow

### Standard Process:
1. Task appears in `Inbox`
2. Moves to `Needs_Action` (automated)
3. Reasoning trigger creates plan in `Plans`
4. Plan moves to `Pending_Approval` (automated)
5. Human reviews and moves to `Approved` (manual)
6. Action executes (automated)
7. Task moves to `Done` (automated)

### Emergency Override:
- Move files directly to `Approved` to skip approval
- Move files to `Needs_Action` to restart process
- Check `Done` folder for completed tasks

## Troubleshooting

### Common Issues:

**Gmail API Error:**
- Check credentials.json file
- Verify OAuth consent screen setup
- Ensure Gmail API is enabled

**Playwright Browser Issues:**
- Run `playwright install` again
- Check if Chrome/Chromium is installed
- Ensure sufficient system resources

**Email Sending Failures:**
- Verify SMTP settings
- Check app password (not regular password)
- Ensure 2FA is enabled on Gmail

**Ollama Connection Issues:**
- Verify `ollama serve` is running
- Check model is downloaded: `ollama list`
- Test connection: `ollama run qwen:latest`

### Logging:
- Check console output for real-time status
- Review Dashboard.md for system status
- Check individual component logs

## Security Considerations

### Data Protection:
- Store credentials securely
- Use environment variables for sensitive data
- Regular backup of important files
- Monitor access to vault directories

### API Limits:
- Gmail API has rate limits
- LinkedIn may restrict automated posting
- Space out requests appropriately

## Maintenance

### Daily:
- Check Dashboard.md for system status
- Review `Pending_Approval` queue
- Verify all components are running

### Weekly:
- Clean up old files in `Done` folder
- Update Dashboard.md metrics
- Review system performance

### Monthly:
- Rotate API keys and passwords
- Update dependencies
- Review and archive old logs

## Scaling Tips

### Performance:
- Adjust polling intervals based on needs
- Use scheduling for heavy operations
- Monitor system resources

### Reliability:
- Implement error recovery mechanisms
- Add health checks for critical components
- Consider running in containers for stability