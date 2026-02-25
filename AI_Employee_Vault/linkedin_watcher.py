import asyncio
import os
import json
import time
import random
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import traceback

load_dotenv()

class LinkedInWatcher:
    def __init__(self):
        self.linkedin_url = "https://www.linkedin.com"
        self.session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
        self.keywords = os.getenv('LINKEDIN_KEYWORDS', 'lead,sale,inquiry,job,connect,opportunity,proposal,business,collaboration').split(',')
        self.username = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        
        # Ensure session directory exists
        os.makedirs(self.session_path, exist_ok=True)
        
        print(f"LinkedIn watcher initialized with session path: {self.session_path}")

    async def setup_context(self):
        """Setup Playwright context with persistent session - Stealth Mode"""
        print("Setting up Playwright context (Stealth Mode)...")
        
        # Check if session files exist
        storage_state_path = os.path.join(self.session_path, 'storage_state.json')
        if not os.path.exists(storage_state_path):
            print(f"Session file not found at {storage_state_path}")
            return None
            
        try:
            print("Launching browser with persistent context (Stealth)...")
            
            # Stealth browser options to avoid detection
            self.browser = await self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True,
                bypass_csp=True,
                locale='en-US,en;q=0.9',
                timezone_id='America/New_York',
                # Stealth options
                permissions=['geolocation', 'notifications'],
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                },
                # Evade webdriver detection
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--allow-running-insecure-content',
                    '--disable-webgl',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # Remove webdriver property
            await self.browser.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = { runtime: {} };
            """)
            
            print("Context launched successfully (Stealth Mode)")
            
            # Get or create a page
            if len(self.browser.pages) > 0:
                self.page = self.browser.pages[0]
            else:
                self.page = await self.browser.new_page()
                
            print("Page created/accessed successfully")
            
            # Add random delay to appear more human
            await self.page.wait_for_timeout(random.randint(1000, 3000))
            
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            await self.page.goto(f"{self.linkedin_url}/feed/", timeout=60000)
            
            # Wait for page to load and check for CAPTCHA
            print("Waiting for page to load...")
            try:
                # Wait up to 60 seconds for CAPTCHA or page to load
                await self.page.wait_for_load_state('domcontentloaded', timeout=30000)
                await self.page.wait_for_timeout(5000)
                
                # Check if CAPTCHA is present
                captcha_present = await self.page.query_selector('#captcha-internal, .captcha-container, [id*="captcha"]')
                if captcha_present:
                    print("CAPTCHA detected! Please solve it manually...")
                    # Give user 3 minutes to solve CAPTCHA
                    await self.page.wait_for_timeout(180000)
                
            except Exception as e:
                print(f"Page load check: {e}")
            
            # Random delay after navigation
            await self.page.wait_for_timeout(random.randint(2000, 5000))
            print("Navigation to LinkedIn feed completed")
            
            # Check if logged in
            is_logged_in = await self.check_logged_in()
            if not is_logged_in:
                print("Session invalid - please login manually and save session")
                await self.browser.close()
                return False
                
            print("LinkedIn watcher initialized with persistent session")
            return True
            
        except Exception as e:
            print(f"Error setting up persistent context: {e}")
            traceback.print_exc()
            return False

    async def check_logged_in(self):
        """Check if user is logged in by looking for profile element or title"""
        try:
            print("Checking if user is logged in...")
            
            # Wait a bit for page to load
            await self.page.wait_for_load_state('networkidle', timeout=30000)
            
            # Check for various elements that appear only when logged in
            logged_in_selectors = [
                '[data-test-id="profile-nav-item"]',  # Profile icon in header
                '[data-test-id="mynetwork-nav-item"]',  # My Network tab
                '[data-test-id="jobs-nav-item"]',  # Jobs tab
                '[data-test-id="messaging-nav-item"]',  # Messaging tab
                '[data-test-id="notifications-nav-item"]',  # Notifications tab
                'img[alt*="photo"]',  # Profile photo
                '.share-box-feed-entry__trigger',  # Share box
                '.global-nav__me',  # Profile dropdown
                '[aria-label="Account settings and support"]',  # Account menu
                'a[href^="/in/"]',  # Link to user's profile
                '[data-test-id="nav-settings"]',  # Settings icon
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        print(f"Found logged-in indicator: {selector}")
                        return True
                except:
                    continue
            
            # Check page title
            title = await self.page.title()
            if "LinkedIn" in title and "sign in" not in title.lower() and "log in" not in title.lower():
                print(f"Page title '{title}' suggests user is logged in")
                return True
            
            print("No login indicators found - user may not be logged in")
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False

    async def login_linkedin(self):
        """Login to LinkedIn"""
        print("Logging in to LinkedIn...")
        try:
            # Navigate to login page
            await self.page.goto(f"{self.linkedin_url}/login", timeout=60000)
            
            # Wait for page to load and potentially scroll to ensure elements are visible
            await self.page.wait_for_load_state('domcontentloaded')
            
            # Try to scroll to center of page to make login form visible
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
            await self.page.wait_for_timeout(2000)  # Wait for any animations
            
            # Define multiple possible selectors for login fields
            username_selectors = [
                '#username',  # Standard username field
                'input[name="session_key"]',  # LinkedIn-specific name attribute
                'input[id*="email"]',  # Email field with partial match
                'input[type="email"]',  # Email input type
                'input[placeholder*="email"]',  # Email placeholder
                'input[placeholder*="Email"]',  # Email placeholder with capital E
                'input[placeholder*="username"]',  # Username placeholder
            ]
            
            password_selectors = [
                '#password',  # Standard password field
                'input[name="session_password"]',  # LinkedIn-specific name attribute
                'input[type="password"]',  # Password input type
                'input[placeholder*="password"]',  # Password placeholder
                'input[placeholder*="Password"]',  # Password placeholder with capital P
            ]
            
            login_button_selectors = [
                'button[type="submit"]',  # Standard submit button
                'button[data-litms-control-urn="login-submit"]',  # LinkedIn-specific data attribute
                'button.button--primary',  # Primary button class
                '.btn__primary--large',  # Large primary button class
                'form[action*="login-submit"] button',  # Button inside login form
                '[data-test-id="sign-in-form__submit-btn"]',  # Modern LinkedIn selector
                'button[aria-label*="Sign in"]',  # Button with aria label
                'button:text("Sign in")',  # Button with text content
                'button:text("Log in")',  # Button with log in text
            ]
            
            # Find and fill username
            username_filled = False
            for selector in username_selectors:
                try:
                    # Wait for element to be visible and enabled
                    await self.page.wait_for_selector(selector, state='visible', timeout=10000)
                    await self.page.focus(selector)
                    await self.page.fill(selector, self.username)
                    print(f"Filled username using selector: {selector}")
                    username_filled = True
                    break
                except Exception as e:
                    print(f"Could not fill username with selector '{selector}': {e}")
                    continue
            
            if not username_filled:
                print("Could not find or fill username field")
                return False
            
            # Find and fill password
            password_filled = False
            for selector in password_selectors:
                try:
                    # Wait for element to be visible and enabled
                    await self.page.wait_for_selector(selector, state='visible', timeout=10000)
                    await self.page.focus(selector)
                    await self.page.fill(selector, self.password)
                    print(f"Filled password using selector: {selector}")
                    password_filled = True
                    break
                except Exception as e:
                    print(f"Could not fill password with selector '{selector}': {e}")
                    continue
            
            if not password_filled:
                print("Could not find or fill password field")
                return False
            
            # Find and click login button
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    # Wait for button to be visible and enabled
                    await self.page.wait_for_selector(selector, state='visible', timeout=10000)
                    await self.page.wait_for_selector(selector, state='enabled', timeout=5000)
                    await self.page.click(selector)
                    print(f"Clicked login button using selector: {selector}")
                    login_clicked = True
                    break
                except Exception as e:
                    print(f"Could not click login button with selector '{selector}': {e}")
                    continue
            
            if not login_clicked:
                print("Could not find or click login button")
                return False
            
            # Wait for navigation after login
            await self.page.wait_for_url(f"{self.linkedin_url}/feed/**", timeout=60000)
            
            print("LinkedIn login successful")
            return True
        except Exception as e:
            print(f"LinkedIn login failed: {e}")
            return False

    async def get_unread_messages(self):
        """Get unread messages from LinkedIn Messaging"""
        try:
            print("Accessing LinkedIn messaging...")
            await self.page.goto(f"{self.linkedin_url}/messaging/", timeout=60000)
            
            # Wait for messages to load
            await self.page.wait_for_selector('div.msg-thread, [data-test-id="messaging-thread"]', timeout=30000)
            
            # Find unread messages
            unread_messages = []
            message_threads = await self.page.query_selector_all('div.msg-thread, [data-test-id="messaging-thread"]')
            
            for thread in message_threads:
                # Check if thread is unread
                unread_indicators = [
                    '.msg-conversation-card__unread',
                    '[data-test-id*="unread"]',
                    '[class*="unread"]',
                    '[style*="font-weight: 600"]'  # Bold text often indicates unread
                ]
                
                is_unread = False
                for indicator in unread_indicators:
                    if await thread.query_selector(indicator):
                        is_unread = True
                        break
                
                if is_unread:
                    sender_selectors = [
                        '.msg-conversation-card__sender-name',
                        '.msg-thread__actor-name',
                        '[data-test-id*="sender"]',
                        'h3'
                    ]
                    
                    message_selectors = [
                        '.msg-conversation-card__message-snippet',
                        '.msg-thread__snippet',
                        '.msg-conversation-card__body'
                    ]
                    
                    sender = "Unknown"
                    for selector in sender_selectors:
                        sender_element = await thread.query_selector(selector)
                        if sender_element:
                            sender = await sender_element.text_content()
                            break
                    
                    message = ""
                    for selector in message_selectors:
                        message_element = await thread.query_selector(selector)
                        if message_element:
                            message = await message_element.text_content()
                            break
                    
                    if message.strip():
                        unread_messages.append({
                            'sender': sender.strip(),
                            'message': message.strip(),
                            'timestamp': datetime.now().isoformat(),
                            'type': 'linkedin_message'
                        })
            
            print(f"Found {len(unread_messages)} unread messages")
            return unread_messages
        except Exception as e:
            print(f"Error getting unread messages: {e}")
            return []

    async def get_notifications(self):
        """Get notifications from LinkedIn Notifications page"""
        try:
            print("Accessing LinkedIn notifications...")
            await self.page.goto(f"{self.linkedin_url}/notifications/", timeout=60000)
            
            # Wait for notifications to load
            await self.page.wait_for_selector('[data-test-id="notification-item"], .notification-card', timeout=30000)
            
            # Find new notifications
            all_items = []
            notification_elements = await self.page.query_selector_all('[data-test-id="notification-item"], .notification-card')
            
            for element in notification_elements:
                # Check if notification is new/unread
                timestamp_element = await element.query_selector('time')
                if timestamp_element:
                    # Get timestamp attribute
                    timestamp_attr = await timestamp_element.get_attribute('datetime')
                    if timestamp_attr:
                        timestamp = datetime.fromisoformat(timestamp_attr.replace('Z', '+00:00'))
                        # Consider notifications from the last day as "new"
                        if (datetime.now().astimezone() - timestamp).days <= 1:
                            actor_selectors = [
                                '[data-test-id="notification-actor"]',
                                '.notification-item__actor-name',
                                '.actor-name',
                                '.feed-shared-actor__name'
                            ]
                            
                            content_selectors = [
                                '[data-test-id="notification-content"]',
                                '.notification-content',
                                '.feed-shared-actor__description',
                                '.notification-item__description'
                            ]
                            
                            sender = "LinkedIn"
                            for selector in actor_selectors:
                                actor_element = await element.query_selector(selector)
                                if actor_element:
                                    sender = await actor_element.text_content()
                                    break
                            
                            content = "Notification"
                            for selector in content_selectors:
                                content_element = await element.query_selector(selector)
                                if content_element:
                                    content = await content_element.text_content()
                                    break
                            
                            all_items.append({
                                'sender': sender.strip(),
                                'content': content.strip(),
                                'timestamp': timestamp.isoformat(),
                                'type': 'linkedin_notification'
                            })
            
            print(f"Found {len(all_items)} new notifications")
            return all_items
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []

    def create_task_file(self, item):
        """Create a task file for a LinkedIn item"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_{item['type']}_{timestamp}.md"
        filepath = os.path.join("Needs_Action", filename)
        
        content = f"""# LinkedIn {item['type'].replace('_', ' ').title()}

**Timestamp:** {item['timestamp']}
**Sender:** {item['sender']}

## Content
{item.get('content', item.get('message', ''))}

## Action Required
- [ ] Review and respond appropriately
- [ ] Update status when completed

---
**Auto-generated by LinkedIn Watcher**
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created LinkedIn task: {filepath} (Priority: High)")
        return filepath

async def linkedin_watcher_loop():
    """Continuous monitoring loop for LinkedIn"""
    watcher = LinkedInWatcher()
    
    async with async_playwright() as pw:
        watcher.playwright = pw
        
        # Setup context
        success = await watcher.setup_context()
        if not success:
            print("Failed to setup LinkedIn context")
            return
        
        print("LinkedIn watcher started...")
        
        while True:
            try:
                # Get unread messages
                messages = await watcher.get_unread_messages()
                
                # Get notifications
                notifications = await watcher.get_notifications()
                
                # Combine all items
                all_items = messages + notifications
                
                # Process new items
                processed_count = 0
                for item in all_items:
                    # Check for keywords to determine priority
                    content = item.get('content', item.get('message', ''))
                    item['priority'] = 'High' if any(keyword.lower() in content.lower() for keyword in watcher.keywords) else 'Normal'
                    
                    # Create task file
                    watcher.create_task_file(item)
                    processed_count += 1
                
                print(f"[{datetime.now()}] Processed {processed_count} LinkedIn items")
                
                # Wait before next check
                await asyncio.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                print("LinkedIn watcher stopped by user.")
                break
            except Exception as e:
                print(f"LinkedIn watcher error: {e}")
                traceback.print_exc()
                await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    asyncio.run(linkedin_watcher_loop())