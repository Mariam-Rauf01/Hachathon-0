import asyncio
from playwright.async_api import async_playwright
import time
import random
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LinkedInPoster:
    def __init__(self):
        self.browser = None
        self.page = None
        self.linkedin_url = "https://www.linkedin.com"
        self.username = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        
    async def login_linkedin(self):
        """Login to LinkedIn with Stealth Mode"""
        self.playwright = await async_playwright().start()
        
        # Stealth browser options
        self.browser = await self.playwright.chromium.launch(
            headless=False,
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
        
        # Create stealth context
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US,en;q=0.9',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add stealth script to remove automation detection
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
        
        self.page = await self.context.new_page()
        
        # Random delay to appear human
        await self.page.wait_for_timeout(random.randint(1000, 2000))
        
        # Navigate to LinkedIn
        await self.page.goto(f"{self.linkedin_url}/login")
        await self.page.wait_for_timeout(random.randint(2000, 4000))
        
        # Check for CAPTCHA on login page
        captcha_present = await self.page.query_selector('#captcha-internal, .captcha-container')
        if captcha_present:
            print("CAPTCHA detected! Please solve it manually...")
            # Give user 3 minutes to solve CAPTCHA
            await self.page.wait_for_timeout(180000)
        
        # Fill in login credentials
        await self.page.fill('input#username', self.username)
        await self.page.wait_for_timeout(random.randint(500, 1500))
        await self.page.fill('input#password', self.password)
        await self.page.wait_for_timeout(random.randint(500, 1500))
        
        # Click login button
        await self.page.click('button[type="submit"]')
        
        # Wait for login to complete with longer delay for CAPTCHA
        await self.page.wait_for_timeout(random.randint(8000, 15000))
        
        # Verify login by checking for feed
        try:
            await self.page.wait_for_selector('div.feed-shared-update-v2', timeout=15000)
            print("LinkedIn login successful")
        except:
            print("LinkedIn login failed - may need CAPTCHA or session refresh")
            # Try to save the session for next time
            try:
                await self.context.storage_state(path='./linkedin_session/storage_state.json')
                print("Session saved for next time")
            except:
                pass
            raise Exception("Failed to login to LinkedIn")
    
    async def create_post(self, post_content, hashtags=None):
        """Create a LinkedIn post"""
        try:
            # Navigate to home/feed
            await self.page.goto(f"{self.linkedin_url}/feed/")
            await self.page.wait_for_timeout(3000)
            
            # Click on the post creation box
            await self.page.click('button[aria-label="Start a post"]')
            await self.page.wait_for_timeout(2000)
            
            # Fill in the post content
            await self.page.fill('div[contenteditable="true"][data-test-id="artdeco-text-input--textarea"]', post_content)
            
            # Add hashtags if provided
            if hashtags:
                await self.page.type('div[contenteditable="true"][data-test-id="artdeco-text-input--textarea"]', f"\n\n{hashtags}")
            
            # Click post button
            await self.page.click('button[aria-label="Post"]')
            
            # Wait for post to be published
            await self.page.wait_for_timeout(5000)
            
            print(f"LinkedIn post created successfully: {post_content[:50]}...")
            return True
            
        except Exception as e:
            print(f"Error creating LinkedIn post: {e}")
            return False
    
    async def process_approved_post_task(self, file_path):
        """Process an approved LinkedIn post task file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract post content from file
            lines = content.split('\n')
            post_content = ""
            hashtags = None
            
            for line in lines:
                if line.startswith('POST:'):
                    post_content = line.replace('POST:', '', 1).strip()
                elif line.startswith('HASHTAGS:'):
                    hashtags = line.replace('HASHTAGS:', '', 1).strip()
            
            if not post_content:
                # If no POST: prefix, use entire content as post
                post_content = content.strip()
            
            # Create the post
            success = await self.create_post(post_content, hashtags)
            
            if success:
                # Move to Done after successful post
                done_path = os.path.join("Done", os.path.basename(file_path))
                os.rename(file_path, done_path)
                print(f"LinkedIn post task completed: {done_path}")
            else:
                # Move to Needs_Action if failed
                needs_action_path = os.path.join("Needs_Action", os.path.basename(file_path))
                os.rename(file_path, needs_action_path)
                print(f"LinkedIn post task failed, moved back to Needs_Action: {needs_action_path}")
                
        except Exception as e:
            print(f"Error processing LinkedIn post task {file_path}: {e}")
    
    async def monitor_approved_posts(self):
        """Monitor Approved directory for LinkedIn post tasks"""
        for filename in os.listdir("Approved"):
            if 'linkedin' in filename.lower() or 'post' in filename.lower():
                file_path = os.path.join("Approved", filename)
                if os.path.isfile(file_path):
                    print(f"Processing LinkedIn post task: {file_path}")
                    await self.process_approved_post_task(file_path)
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

async def linkedin_poster_loop():
    """Main loop for LinkedIn poster"""
    poster = LinkedInPoster()
    
    try:
        await poster.login_linkedin()
        print("LinkedIn poster started...")
        
        while True:
            await poster.monitor_approved_posts()
            await asyncio.sleep(300)  # Check every 5 minutes
            
    except Exception as e:
        print(f"LinkedIn poster error: {e}")
    finally:
        await poster.close()

if __name__ == "__main__":
    asyncio.run(linkedin_poster_loop())