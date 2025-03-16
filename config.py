import os
import streamlit as st
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    return importlib.util.find_spec(package_name) is not None

def get_config():
    """Get configuration based on environment"""
    # Check if running in cloud environment
    is_cloud = os.environ.get('IS_CLOUD', 'False').lower() == 'true'
    
    # Check for required packages
    required_packages = ['fpdf', 'pymongo', 'qrcode', 'pandas', 'matplotlib']
    missing_packages = [pkg for pkg in required_packages if not check_package(pkg)]
    
    if missing_packages:
        st.error(f"Missing required packages: {', '.join(missing_packages)}. Please install them using pip.")
        st.code("pip install " + " ".join(missing_packages))
    
    # MongoDB connection string with URL-encoded password
    mongodb_uri = os.environ.get(
        'MONGODB_URI', 
        "mongodb+srv://VDX:VDX%40018238@cluster0.tqqoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    
    # Configuration dictionary
    config = {
        "is_cloud": is_cloud,
        "mongodb_uri": mongodb_uri,
        "db_name": "grocery_billing",
        "temp_dir": os.environ.get('TEMP_DIR', os.path.join(os.path.dirname(__file__), 'temp'))
    }
    
    # Create temp directory if it doesn't exist
    os.makedirs(config["temp_dir"], exist_ok=True)
    
    return config

# Initialize configuration as a session state variable
def init_config():
    if 'config' not in st.session_state:
        st.session_state.config = get_config()
    return st.session_state.config