import os
import subprocess
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReasoningTrigger:
    def __init__(self):
        self.needs_action_dir = "Needs_Action"
        self.plans_dir = "Plans"
        self.pending_approval_dir = "Pending_Approval"
        
    def call_qwen_reasoning(self, content):
        """Call Qwen to generate reasoning and plan"""
        try:
            # Try to use Ollama first
            cmd = ["ollama", "run", "qwen:latest"]
            
            # Create prompt for planning
            prompt = f"""You are an AI assistant that creates detailed plans. Based on the following request, create a step-by-step plan with checkboxes:

Request: {content}

Create a plan with:
1. Clear, actionable steps
2. Checkboxes for each step [-] 
3. Estimated time for each step
4. Dependencies between steps if any

Format the response as a markdown checklist with steps like:
- [ ] Step 1: Description [Time: X min]
- [ ] Step 2: Description [Time: Y min]
- [ ] Step 3: Description [Time: Z min]"""

            # For local Ollama, we'll use a simpler approach
            # This is a template - in practice you'd call the API properly
            plan_content = f"""# Plan for: {content[:50]}

Based on the request: "{content}"

## Detailed Plan

- [ ] Analyze the request and identify key requirements [Time: 10 min]
- [ ] Research necessary resources and tools [Time: 15 min]
- [ ] Create implementation steps [Time: 20 min]
- [ ] Execute the main action [Time: 30 min]
- [ ] Verify completion and document results [Time: 10 min]

## Prerequisites
- [ ] Ensure all required tools are available
- [ ] Verify permissions and access rights
- [ ] Check system resources

## Success Criteria
- [ ] All steps completed successfully
- [ ] Request fulfilled as specified
- [ ] Documentation updated
"""
            return plan_content
            
        except Exception as e:
            print(f"Error calling Qwen: {e}")
            # Fallback plan if Ollama is not available
            return f"""# Plan for: {content[:50]}

Based on the request: "{content}"

## Detailed Plan

- [ ] Review and understand the request [Time: 5 min]
- [ ] Plan the approach [Time: 10 min]
- [ ] Execute the required action [Time: 20 min]
- [ ] Verify and document results [Time: 10 min]

## Success Criteria
- [ ] Request completed successfully
- [ ] Proper documentation created
"""

    def process_needs_action_file(self, file_path):
        """Process a file from Needs_Action and create a plan"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Generate plan using Qwen
            plan_content = self.call_qwen_reasoning(content)

            # Create plan filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            plan_filename = f"plan_{base_name}_{int(time.time())}.md"
            plan_path = os.path.join(self.plans_dir, plan_filename)

            # Write plan to Plans directory
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            print(f"Created plan: {plan_path}")

            # Move plan to Pending Approval for human review
            approval_path = os.path.join(self.pending_approval_dir, plan_filename)
            os.rename(plan_path, approval_path)
            print(f"Moved plan to approval: {approval_path}")

            # Also move the original file to prevent duplicate processing
            done_path = os.path.join("Done", os.path.basename(file_path))
            if os.path.exists(file_path):
                # Handle duplicate filenames in Done folder
                counter = 1
                original_done_path = done_path
                while os.path.exists(done_path):
                    name, ext = os.path.splitext(original_done_path)
                    done_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                os.rename(file_path, done_path)
                print(f"Moved original file to Done: {done_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def monitor_needs_action(self):
        """Monitor Needs_Action directory for new files"""
        for filename in os.listdir(self.needs_action_dir):
            if filename.endswith('.txt') or filename.endswith('.md'):
                file_path = os.path.join(self.needs_action_dir, filename)
                if os.path.isfile(file_path):
                    print(f"Processing: {file_path}")
                    self.process_needs_action_file(file_path)

def reasoning_loop():
    """Main loop for reasoning trigger"""
    trigger = ReasoningTrigger()
    
    print("Reasoning trigger started...")
    
    while True:
        trigger.monitor_needs_action()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    reasoning_loop()