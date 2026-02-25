import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_session():
    # Use the session path from environment variable or default
    session_path = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session')
    os.makedirs(session_path, exist_ok=True)
    
    print(f"Creating LinkedIn session in: {session_path}")
    
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Keep browser visible
            args=[
                '--start-maximized',  # Start maximized
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--start-maximized',  # Start maximized (centered)
            ]
        )
        
        print("Browser launched, creating page...")
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Set viewport to match window size
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US,en;q=0.9',
            timezone_id='America/New_York',
        )
        
        page = await context.new_page()
        
        print("Navigating to LinkedIn login page...")
        await page.goto('https://www.linkedin.com/login', timeout=60000, wait_until='networkidle')
        
        # Bring page to front to ensure visibility
        await page.bring_to_front()
        
        # Execute JavaScript to maximize window (centered)
        await page.evaluate("""
            () => {
                window.moveTo((screen.availWidth - window.innerWidth) / 2, (screen.availHeight - window.innerHeight) / 2);
                window.resizeTo(screen.availWidth, screen.availHeight);
            }
        """)
        
        # Wait for page to fully load
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(2000)
        
        # Scroll to top of page to ensure login form is visible
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)
        
        # Check if page loaded properly - reload if blank
        try:
            await page.wait_for_selector('body', timeout=5000)
            body_text = await page.evaluate('document.body.innerText')
            if len(body_text) < 100:
                print("Page appears blank, reloading...")
                await page.reload(wait_until='networkidle')
                await page.wait_for_timeout(2000)
        except:
            print("Reloading page...")
            await page.reload(wait_until='networkidle')
        
        print("Page loaded. Now please:")
        print("1. Enter your email/phone in the email field")
        print("2. Enter your password in the password field")
        print("3. Click the 'Sign in' button")
        print("4. Complete any additional verification steps if prompted")
        print("If the page is blank or not loading, press Ctrl+C to stop and run again.")
        print("The page will stay open for 15 minutes to allow you to log in.")
        print("After you've successfully logged in, close the browser window manually.")
        print("The session will be saved automatically when you close the browser.")
        
        # Stay alive for 15 minutes to give ample time for login
        total_wait_time = 900  # 15 minutes in seconds
        print(f"Browser will stay open for {total_wait_time} seconds. Please complete your login now.")
        
        # Keep the script running while user logs in
        for i in range(total_wait_time):
            try:
                # Check if the page is still open by trying to interact with it
                await page.wait_for_timeout(1000)  # Wait 1 second
                
                # Every 60 seconds, print a status message
                if i % 60 == 0:
                    print(f"Waiting... {total_wait_time - i} seconds remaining. Please continue with your login.")
                
                # Check if we're logged in by looking for elements that appear only when logged in
                try:
                    if await page.query_selector('[data-test-id="profile-nav-item"]'):
                        print("Detected successful login! Session will be saved when you close the browser.")
                        break
                except:
                    pass  # Continue if page is closed
                    
            except Exception as e:
                print(f"Browser may have been closed: {e}")
                break
        
        print("Checking if user is logged in before saving session...")
        
        try:
            # Check if user is logged in by looking for elements that appear only when logged in
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
            ]
            
            is_logged_in = False
            for selector in logged_in_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Confirmed logged in - found element: {selector}")
                        is_logged_in = True
                        break
                except:
                    continue
            
            if is_logged_in:
                print("User appears to be logged in. Saving session...")
                # Save the session state
                storage_state_path = os.path.join(session_path, 'storage_state.json')
                await context.storage_state(path=storage_state_path)
                print(f"Session saved to: {storage_state_path}")
            else:
                print("User does not appear to be logged in. No session saved.")
                print("Please try logging in again.")
        except:
            print("Browser was closed before checking login status.")
        
        print("Session creation process complete!")
        print("Please close the browser window if it's still open.")

if __name__ == "__main__":
    asyncio.run(create_session())