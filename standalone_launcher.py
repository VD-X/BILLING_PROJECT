import os
import sys
import subprocess
import threading
import time
import webbrowser

def open_browser():
    """Open the browser after giving the server time to start."""
    time.sleep(3)
    webbrowser.open('http://localhost:8501')

def main():
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the base directory
    os.chdir(base_dir)
    
    # Print startup message
    print("=" * 60)
    print("Starting Grocery Billing System...")
    print("=" * 60)
    print("Please wait while the application loads...")
    print("A browser window will open automatically.")
    print("=" * 60)
    
    # Start browser thread
    threading.Thread(target=open_browser).start()
    
    # Update this to match your main file name
    main_file = 'Home.py'  # Main entry point of the application
    
    # Run the Streamlit app
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", main_file, "--server.port=8501", "--browser.serverAddress=localhost"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()