import os
import subprocess
import sys

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    # Running as executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the base directory
os.chdir(base_dir)

# Run the Streamlit app
# Update this line with your actual main file name (Home.py or main.py)
main_file = "Home.py"  # Change this to your actual main file name

subprocess.call([
    "streamlit", "run", 
    os.path.join(base_dir, main_file),
    "--browser.serverAddress=localhost",
    "--server.headless=true"
])