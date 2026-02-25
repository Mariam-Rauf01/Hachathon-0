import webbrowser
import time

print("Opening LinkedIn login page in your default browser...")
print("Please log in to LinkedIn now.")
print("The browser will stay open after login.")
print("Close the browser only when you're done logging in.")

# Open LinkedIn login page in the default browser
webbrowser.open('https://www.linkedin.com/login')

print("\nBrowser opened. Please complete your LinkedIn login now.")
print("This script will keep running to prevent the browser from closing.")
print("You can close this command prompt after logging in,")
print("but KEEP THE BROWSER WINDOW OPEN.")

# Keep the script running indefinitely
try:
    while True:
        time.sleep(60)  # Sleep for 60 seconds
        print("Still running... Browser should remain open.")
except KeyboardInterrupt:
    print("\nScript terminated. You can now close the browser if needed.")