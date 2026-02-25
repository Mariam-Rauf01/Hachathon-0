import time
import functools
import logging
import os
from datetime import datetime
from typing import Callable, Any
import traceback

def with_retry(max_attempts: int = 5, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    Decorator for exponential backoff retry mechanism
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:  # Last attempt
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

def log_error(component: str, error: Exception, extra_info: dict = None):
    """
    Log error to dated log file with timestamp and component info
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = 'Logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create dated log file
        today = datetime.now().strftime('%Y-%m-%d')
        log_filename = f'{today}.log'
        log_filepath = os.path.join(logs_dir, log_filename)
        
        # Format error message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = (
            f"[{timestamp}] {component.upper()} - ERROR: {str(error)}\n"
            f"Exception Type: {type(error).__name__}\n"
            f"Traceback: {traceback.format_exc()}\n"
        )
        
        if extra_info:
            error_msg += f"Extra Info: {extra_info}\n"
        
        error_msg += "-" * 50 + "\n"
        
        # Write to log file
        with open(log_filepath, 'a', encoding='utf-8') as log_file:
            log_file.write(error_msg)
        
        # Also print to console
        print(f"ERROR LOGGED: {component} - {str(error)}")
        
    except Exception as log_error:
        # If logging fails, at least print to console
        print(f"FATAL ERROR LOGGING FAILED: {log_error}")
        print(f"ORIGINAL ERROR: {component} - {str(error)}")

def create_alert(component: str, error: Exception, description: str = ""):
    """
    Create an alert file in Needs_Action when critical failures occur
    """
    try:
        alert_filename = f"alert_{component}_{int(datetime.now().timestamp())}.md"
        alert_filepath = os.path.join("Needs_Action", alert_filename)
        
        alert_content = f"""# System Alert

**Component**: {component}
**Time**: {datetime.now().isoformat()}
**Error**: {str(error)}
**Type**: {type(error).__name__}

## Description
{description}

## Action Required
- [ ] Investigate the error above
- [ ] Check logs for more details
- [ ] Restart the component if needed
- [ ] Verify system health

## Error Details
```
{traceback.format_exc()}
```

## Status
- [ ] Alert acknowledged
- [ ] Issue resolved
- [ ] Component restarted
"""
        
        with open(alert_filepath, 'w', encoding='utf-8') as f:
            f.write(alert_content)
        
        print(f"ALERT CREATED: {alert_filepath}")
        
    except Exception as e:
        print(f"FAILED TO CREATE ALERT: {e}")

def setup_component_logger(component_name: str):
    """
    Setup logger for a specific component
    """
    logger = logging.getLogger(component_name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding multiple handlers
    if not logger.handlers:
        handler = logging.FileHandler(
            os.path.join('Logs', f'{component_name}_{datetime.now().strftime("%Y-%m")}.log')
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def check_component_health(component_name: str, max_failures: int = 3) -> bool:
    """
    Check if a component should be paused due to repeated failures
    """
    try:
        # Count recent failures in log
        logs_dir = 'Logs'
        today = datetime.now().strftime('%Y-%m-%d')
        log_filepath = os.path.join(logs_dir, f'{today}.log')
        
        if not os.path.exists(log_filepath):
            return True
        
        failure_count = 0
        with open(log_filepath, 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                if component_name.upper() in line and "ERROR:" in line:
                    failure_count += 1
                    if failure_count >= max_failures:
                        return False  # Too many failures, pause component
        
        return True  # Component is healthy
        
    except Exception:
        return True  # Assume healthy if we can't check