import os
import streamlit as st

def get_config():
    """Get configuration based on environment"""
    # Check if running in cloud environment
    is_cloud = os.environ.get('IS_CLOUD', 'False').lower() == 'true'
    
    # Configuration dictionary
    config = {
        "is_cloud": is_cloud,
        "mongodb_uri": os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'),
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