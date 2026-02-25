import os
import subprocess
import json
import time
import asyncio
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from pathlib import Path
import hashlib
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple
import yaml

# Enhanced configuration and utilities
class EnhancedConfig:
    """Enhanced configuration with validation and security"""
    
    def __init__(self):
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB default
        self.ai_timeout = int(os.getenv('AI_TIMEOUT', '300'))  # 5 minutes default
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '5'))
        self.ollama_endpoint = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434/api/generate')
        
    def validate_file_size(self, file_path: str) -> bool:
        """Validate file size against configured limit"""
        try:
            size = os.path.getsize(file_path)
            return size <= self.max_file_size
        except OSError:
            return False


class EnhancedLogger:
    """Enhanced logging with security and performance monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup enhanced logging configuration"""
        log_dir = 'Logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'reasoning_trigger_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def log_security_event(self, event_type: str, details: str):
        """Log security-related events"""
        self.logger.warning(f"SECURITY EVENT - {event_type}: {details}")
        
    def log_performance_metric(self, metric: str, value: float):
        """Log performance metrics"""
        self.logger.info(f"PERFORMANCE - {metric}: {value}")


class AIClient:
    """Enhanced AI client with error handling and retry logic"""
    
    def __init__(self, config: EnhancedConfig, logger: EnhancedLogger):
        self.config = config
        self.logger = logger
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def call_ollama(self, prompt: str, model: str = "qwen:latest") -> Optional[str]:
        """Enhanced Ollama API call with retry logic and error handling"""
        url = self.config.ollama_endpoint
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            }
        }
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.logger.debug(f"Calling Ollama API (attempt {attempt + 1})")
                
                async with self.session.post(url, json=payload, timeout=self.config.ai_timeout) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.logger.info(f"Ollama API call successful (attempt {attempt + 1})")
                        return result.get('response', '')
                    else:
                        self.logger.logger.warning(f"Ollama API returned status {response.status} (attempt {attempt + 1})")
                        
            except asyncio.TimeoutError:
                self.logger.logger.warning(f"Ollama API call timed out (attempt {attempt + 1})")
            except aiohttp.ClientError as e:
                self.logger.logger.warning(f"Ollama API client error (attempt {attempt + 1}): {e}")
            except Exception as e:
                self.logger.logger.error(f"Unexpected error in Ollama API call (attempt {attempt + 1}): {e}")
                
            if attempt < self.config.max_retries - 1:
                self.logger.logger.info(f"Waiting {self.config.retry_delay} seconds before retry...")
                await asyncio.sleep(self.config.retry_delay)
                
        self.logger.logger.error("All Ollama API attempts failed")
        return None


class EnhancedReasoningEngine:
    """Enhanced reasoning engine with security and performance optimizations"""
    
    def __init__(self):
        self.config = EnhancedConfig()
        self.logger = EnhancedLogger()
        self.needs_action_dir = "Needs_Action"
        self.plans_dir = "Plans"
        self.pending_approval_dir = "Pending_Approval"
        self.temp_dir = "Temp"
        
        # Create directories if they don't exist
        for directory in [self.needs_action_dir, self.plans_dir, self.pending_approval_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Initialize file processing cache
        self.processed_files = set()
        self.processing_locks = {}  # Track files currently being processed
        
    async def call_ai_reasoning(self, content: str) -> str:
        """Enhanced AI reasoning with security and quality checks"""
        # Sanitize content to prevent prompt injection
        sanitized_content = self.sanitize_content(content)
        
        # Create detailed prompt for planning
        prompt = self.create_detailed_prompt(sanitized_content)
        
        async with AIClient(self.config, self.logger) as ai_client:
            response = await ai_client.call_ollama(prompt)
            
        if response:
            # Validate and format the response
            formatted_response = self.format_plan_response(response, sanitized_content)
            return formatted_response
        else:
            # Fallback plan if AI call fails
            return self.create_fallback_plan(sanitized_content)
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent prompt injection and security issues"""
        # Remove potential prompt injection patterns
        sanitized = re.sub(r'<\|.*?\|>', '', content)  # Remove <|...|> patterns
        sanitized = re.sub(r'\{.*?\}', '', sanitized)  # Remove {...} patterns that might be instructions
        sanitized = sanitized.replace('[INST]', '').replace('[/INST]', '')  # Remove instruction tags
        sanitized = sanitized.replace('<s>', '').replace('</s>', '')  # Remove token tags
        
        # Limit length to prevent overly large prompts
        max_length = 5000  # Characters
        if len(sanitized) > max_length:
            self.logger.log_security_event("CONTENT_TRUNCATED", f"Content too long ({len(sanitized)} chars), truncated to {max_length}")
            sanitized = sanitized[:max_length]
            
        return sanitized.strip()
    
    def create_detailed_prompt(self, content: str) -> str:
        """Create a detailed prompt for the AI to generate a comprehensive plan"""
        return f"""You are an expert business process planner. Create a detailed, actionable plan based on the following request:

REQUEST: {content}

Create a comprehensive plan that includes:

1. CLEAR OBJECTIVES: Define what success looks like
2. STEP-BY-STEP PROCESS: Break down the task into specific, actionable steps
3. RESOURCE REQUIREMENTS: Identify tools, permissions, and resources needed
4. TIMELINE ESTIMATES: Provide realistic time estimates for each step
5. RISK ASSESSMENT: Identify potential challenges and mitigation strategies
6. SUCCESS METRICS: Define how to measure completion and success
7. DEPENDENCIES: Note any prerequisites or sequential requirements

Format your response as a markdown document with:
- A title based on the request
- Sections for each of the above points
- Checkboxes for each action step [-]
- Time estimates for each major step
- Priority levels (High/Medium/Low) for each task

Be specific, actionable, and thorough."""

    def format_plan_response(self, response: str, original_content: str) -> str:
        """Format and validate the AI response"""
        # Basic validation to ensure response has structure
        if not response.strip():
            return self.create_fallback_plan(original_content)
            
        # Ensure proper markdown structure
        if not response.startswith('#'):
            response = f"# Plan for: {original_content[:50] if len(original_content) > 50 else original_content}\n\n{response}"
            
        # Add metadata section
        metadata = f"""## Request Details
- **Original Request**: {original_content[:200]}{"..." if len(original_content) > 200 else ""}
- **Generated At**: {datetime.now().isoformat()}
- **AI Model**: Ollama/qwen

"""
        
        # Insert metadata after the first heading
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# ') or line.startswith('#'):
                lines.insert(i + 1, metadata)
                break
        
        formatted_response = '\n'.join(lines)
        
        # Validate that it contains actionable elements
        if '- [ ]' not in formatted_response and '##' not in formatted_response[100:]:
            # Add a basic structure if missing
            formatted_response += f"""

## Action Steps
- [ ] Review and understand the request: {original_content[:100]}{"..." if len(original_content) > 100 else ""}
- [ ] Plan the approach based on requirements
- [ ] Execute the necessary actions
- [ ] Verify completion and document results

## Success Criteria
- [ ] Request fulfilled as specified
- [ ] Proper documentation created
- [ ] Stakeholders notified of completion
"""
        
        return formatted_response
    
    def create_fallback_plan(self, content: str) -> str:
        """Create a fallback plan when AI is unavailable"""
        self.logger.logger.warning("Using fallback plan generation due to AI unavailability")
        
        return f"""# Plan for: {content[:50] if len(content) > 50 else content}

## Request Analysis
The system attempted to generate a detailed plan using AI but encountered an issue. This is a fallback plan.

## Action Steps
- [ ] Review and understand the request: {content[:100]}{"..." if len(content) > 100 else ""}
- [ ] Research necessary resources and tools
- [ ] Create implementation steps
- [ ] Execute the required action
- [ ] Verify and document results

## Notes
- This plan was generated without AI assistance
- Review carefully before approval
- Consider consulting additional resources for complex requests

## Success Criteria
- [ ] Request completed successfully
- [ ] Proper documentation created
- [ ] Stakeholders notified of completion
"""

    async def process_needs_action_file(self, file_path: str) -> bool:
        """Enhanced file processing with security and error handling"""
        try:
            # Check if file is already being processed
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            if file_hash in self.processing_locks:
                self.logger.logger.info(f"File {file_path} is already being processed, skipping")
                return False
                
            self.processing_locks[file_hash] = True
            
            # Validate file
            if not self.config.validate_file_size(file_path):
                self.logger.log_security_event("FILE_TOO_LARGE", f"File {file_path} exceeds size limit")
                return False
                
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                self.logger.logger.warning(f"Empty file: {file_path}")
                await self.move_to_done(file_path)
                return False
            
            # Generate plan using AI
            self.logger.logger.info(f"Generating plan for: {file_path}")
            plan_content = await self.call_ai_reasoning(content)
            
            if not plan_content.strip():
                self.logger.logger.error(f"Failed to generate plan for: {file_path}")
                return False
            
            # Create plan filename with timestamp and content hash
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            plan_filename = f"plan_{base_name}_{content_hash}_{timestamp}.md"
            plan_path = os.path.join(self.temp_dir, plan_filename)  # Write to temp first
            
            # Write plan to temporary location
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)
            
            # Validate plan content before moving
            if await self.validate_plan_content(plan_path):
                # Move plan to Plans directory
                final_plan_path = os.path.join(self.plans_dir, plan_filename)
                os.rename(plan_path, final_plan_path)
                
                self.logger.logger.info(f"Created validated plan: {final_plan_path}")
                
                # Move plan to Pending Approval for human review
                approval_path = os.path.join(self.pending_approval_dir, plan_filename)
                os.rename(final_plan_path, approval_path)
                self.logger.logger.info(f"Moved plan to approval: {approval_path}")
                
                # Move the original file to prevent duplicate processing
                await self.move_to_done(file_path)
                
                return True
            else:
                self.logger.logger.error(f"Invalid plan content generated for: {file_path}")
                # Clean up invalid plan
                if os.path.exists(plan_path):
                    os.remove(plan_path)
                return False
                
        except Exception as e:
            self.logger.logger.error(f"Error processing {file_path}: {e}")
            return False
        finally:
            # Release processing lock
            if file_hash in self.processing_locks:
                del self.processing_locks[file_hash]
    
    async def validate_plan_content(self, plan_path: str) -> bool:
        """Validate that the generated plan has proper structure"""
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for basic plan structure
            has_title = content.startswith('#')
            has_steps = '- [ ]' in content or '- [X]' in content
            has_sections = '##' in content
            
            is_valid = has_title and (has_steps or has_sections)
            
            if not is_valid:
                self.logger.logger.warning(f"Plan validation failed for: {plan_path}")
                
            return is_valid
        except Exception as e:
            self.logger.logger.error(f"Error validating plan {plan_path}: {e}")
            return False
    
    async def move_to_done(self, file_path: str):
        """Move original file to Done folder with duplicate handling"""
        try:
            done_path = os.path.join("Done", os.path.basename(file_path))
            
            # Handle duplicate filenames in Done folder
            counter = 1
            original_done_path = done_path
            while os.path.exists(done_path):
                name, ext = os.path.splitext(original_done_path)
                done_path = f"{name}_{counter}{ext}"
                counter += 1

            # Move the file to Done folder
            os.rename(file_path, done_path)
            self.logger.logger.info(f"Moved original file to Done: {done_path}")
            
        except OSError as e:
            self.logger.logger.error(f"Error moving {file_path} to Done folder: {e}")
            # If we can't move the file, try to copy and then remove original
            try:
                backup_path = os.path.join("Temp", f"backup_{int(time.time())}_{os.path.basename(file_path)}")
                import shutil
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
                self.logger.logger.info(f"Backed up and removed {file_path} due to move error")
            except Exception as e2:
                self.logger.logger.error(f"Could not backup {file_path} either: {e2}")

    async def monitor_needs_action(self) -> int:
        """Monitor Needs_Action directory for new files with enhanced processing"""
        try:
            # Get all files in Needs_Action folder
            needs_action_files = []
            for filename in os.listdir(self.needs_action_dir):
                if filename.endswith(('.txt', '.md', '.csv', '.json')):
                    file_path = os.path.join(self.needs_action_dir, filename)
                    if os.path.isfile(file_path):
                        # Check if file was recently modified (avoid processing incomplete files)
                        mod_time = os.path.getmtime(file_path)
                        if time.time() - mod_time > 2:  # File older than 2 seconds
                            needs_action_files.append(file_path)
            
            processed_count = 0
            for file_path in needs_action_files:
                success = await self.process_needs_action_file(file_path)
                if success:
                    processed_count += 1
                    # Small delay to prevent overwhelming the AI
                    await asyncio.sleep(0.5)
            
            if processed_count > 0:
                self.logger.logger.info(f"Processed {processed_count} files from Needs_Action")
                
            return processed_count
            
        except Exception as e:
            self.logger.logger.error(f"Error monitoring Needs_Action: {e}")
            return 0


class EnhancedReasoningTrigger:
    """Enhanced reasoning trigger with async processing and monitoring"""
    
    def __init__(self):
        self.engine = EnhancedReasoningEngine()
        self.running = True
        self.check_interval = int(os.getenv('REASONING_CHECK_INTERVAL', '60'))  # Default 1 minute
        self.batch_size = int(os.getenv('REASONING_BATCH_SIZE', '5'))  # Process up to 5 files per cycle
        
    async def run_monitoring_loop(self):
        """Main async monitoring loop"""
        self.logger = self.engine.logger
        self.logger.logger.info("Enhanced Reasoning Trigger started...")
        
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running:
            try:
                # Process files with rate limiting
                processed_count = await self.engine.monitor_needs_action()
                
                if processed_count > 0:
                    consecutive_errors = 0  # Reset error counter on success
                else:
                    # Small delay when no files to process
                    await asyncio.sleep(min(self.check_interval, 30))  # Don't wait too long if there might be new files
                
                # Check for shutdown condition periodically
                await asyncio.sleep(1)
                
            except Exception as e:
                consecutive_errors += 1
                self.logger.logger.error(f"Error in monitoring loop (error #{consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.logger.critical("Too many consecutive errors, shutting down")
                    break
                
                # Wait before retrying after error
                await asyncio.sleep(min(30, self.check_interval))  # Max 30s wait after error
    
    def stop(self):
        """Stop the monitoring loop"""
        self.running = False


async def reasoning_loop():
    """Enhanced main loop for reasoning trigger"""
    trigger = EnhancedReasoningTrigger()
    
    try:
        await trigger.run_monitoring_loop()
    except KeyboardInterrupt:
        print("\nReasoning trigger interrupted by user")
        trigger.stop()
    except Exception as e:
        print(f"Critical error in reasoning trigger: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    # Run the async event loop
    try:
        asyncio.run(reasoning_loop())
    except KeyboardInterrupt:
        print("\nEnhanced Reasoning Trigger stopped by user")
    except Exception as e:
        print(f"Failed to start Enhanced Reasoning Trigger: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()