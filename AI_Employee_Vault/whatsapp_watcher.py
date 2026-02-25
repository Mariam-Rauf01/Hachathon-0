import asyncio
from playwright.async_api import async_playwright
import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WhatsAppWatcher:
    def __init__(self):
        self.browser = None
        self.page = None
        self.last_messages = set()
        self.whatsapp_url = "https://web.whatsapp.com"
        
    async def initialize_browser(self):
        """Initialize Playwright browser for WhatsApp"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        await self.page.goto(self.whatsapp_url)
        print("WhatsApp Web opened. Please scan QR code if prompted...")
        
        # Wait for user to scan QR code
        await self.page.wait_for_timeout(10000)
    
    async def get_unread_messages(self):
        """Get unread messages from WhatsApp Web"""
        try:
            # Wait for chat list to load
            await self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=5000)
            
            # Get all chat elements
            chats = await self.page.query_selector_all('div[data-testid="chat"]')
            
            messages = []
            for chat in chats:
                try:
                    # Click on chat to open it
                    await chat.click()
                    
                    # Wait for messages to load
                    await self.page.wait_for_timeout(2000)
                    
                    # Get messages from the chat
                    message_elements = await self.page.query_selector_all(
                        'div[data-testid="msg"] div[data-testid="msg-text"]'
                    )
                    
                    for msg_elem in message_elements:
                        msg_text = await msg_elem.text_content()
                        
                        # Check if this message is new
                        msg_hash = hash(msg_text)
                        if msg_hash not in self.last_messages:
                            self.last_messages.add(msg_hash)
                            
                            # Get sender info
                            sender_elem = await msg_elem.query_selector('span')
                            sender = await sender_elem.text_content() if sender_elem else "Unknown"
                            
                            messages.append({
                                'sender': sender,
                                'message': msg_text,
                                'timestamp': time.time(),
                                'chat_name': await chat.text_content()
                            })
                
                except Exception as e:
                    continue  # Skip if chat loading fails
            
            return messages
            
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    async def process_new_messages(self):
        """Process new WhatsApp messages and create tasks"""
        messages = await self.get_unread_messages()
        
        for msg in messages:
            # Create task file in Needs_Action based on message content
            task_filename = f"whatsapp_{str(int(msg['timestamp']))[-6:]}_{msg['sender'][:20].replace(' ', '_')}.txt"
            task_path = os.path.join("Needs_Action", task_filename)
            
            with open(task_path, 'w') as f:
                f.write(f"WHATSAPP MESSAGE\n")
                f.write(f"From: {msg['sender']}\n")
                f.write(f"Chat: {msg['chat_name']}\n")
                f.write(f"Message: {msg['message']}\n")
                f.write(f"Time: {time.ctime(msg['timestamp'])}\n\n")
                f.write("# Action needed:\n")
                f.write("- [ ] Review message content\n")
                f.write("- [ ] Determine required response\n")
                f.write("- [ ] Respond appropriately\n")
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

async def whatsapp_monitor_loop():
    """Continuous monitoring loop for WhatsApp"""
    watcher = WhatsAppWatcher()
    
    try:
        await watcher.initialize_browser()
        print("WhatsApp watcher started...")
        
        while True:
            await watcher.process_new_messages()
            await asyncio.sleep(300)  # Check every 5 minutes
            
    except KeyboardInterrupt:
        print("WhatsApp watcher stopped.")
    except Exception as e:
        print(f"WhatsApp watcher error: {e}")
    finally:
        await watcher.close()

if __name__ == "__main__":
    asyncio.run(whatsapp_monitor_loop())