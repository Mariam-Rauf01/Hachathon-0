import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

class EmailActionHandler:
    def __init__(self):
        self.approved_dir = "Approved"
        self.smtp_config = {
            'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD')
        }
    
    def send_email(self, to_email, subject, body, cc=None, bcc=None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            recipients = [to_email]
            if cc:
                recipients.append(cc)
            if bcc:
                recipients.extend(bcc.split(',') if isinstance(bcc, str) else bcc)
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['username'], recipients, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def process_approved_email_task(self, file_path):
        """Process an approved email task file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse email task (simple parsing - could be enhanced)
            lines = content.split('\n')
            email_info = {}
            
            for line in lines:
                if line.startswith('TO:'):
                    email_info['to'] = line.replace('TO:', '').strip()
                elif line.startswith('SUBJECT:'):
                    email_info['subject'] = line.replace('SUBJECT:', '').strip()
                elif line.startswith('CC:'):
                    email_info['cc'] = line.replace('CC:', '').strip()
                elif line.startswith('BCC:'):
                    email_info['bcc'] = line.replace('BCC:', '').strip()
            
            # Extract email body (everything after headers)
            body_start = 0
            for i, line in enumerate(lines):
                if line.strip() == '':
                    body_start = i + 1
                    break
            
            email_body = '\n'.join(lines[body_start:])
            
            # Send the email
            success = self.send_email(
                email_info.get('to', ''),
                email_info.get('subject', 'No Subject'),
                email_body,
                email_info.get('cc'),
                email_info.get('bcc')
            )
            
            if success:
                # Move to Done after successful send
                done_path = os.path.join("Done", os.path.basename(file_path))
                os.rename(file_path, done_path)
                print(f"Email task completed: {done_path}")
            else:
                # Move to Needs_Action if failed
                needs_action_path = os.path.join("Needs_Action", os.path.basename(file_path))
                os.rename(file_path, needs_action_path)
                print(f"Email task failed, moved back to Needs_Action: {needs_action_path}")
                
        except Exception as e:
            print(f"Error processing email task {file_path}: {e}")
    
    def monitor_approved_tasks(self):
        """Monitor Approved directory for email tasks"""
        for filename in os.listdir(self.approved_dir):
            if filename.endswith('_email.txt') or 'email' in filename.lower():
                file_path = os.path.join(self.approved_dir, filename)
                if os.path.isfile(file_path):
                    print(f"Processing email task: {file_path}")
                    self.process_approved_email_task(file_path)

def email_handler_loop():
    """Main loop for email action handler"""
    handler = EmailActionHandler()
    
    print("Email action handler started...")
    
    while True:
        handler.monitor_approved_tasks()
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    email_handler_loop()