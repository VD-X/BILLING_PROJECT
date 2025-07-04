import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import json
import hashlib
import streamlit as st

# We'll use Streamlit secrets for cloud deployment
# For local development, we'll use a fallback file
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "email_credentials.json")

def setup_email_credentials(email, password, security_code):
    """
    Set up email credentials with a security code for future use.
    For cloud deployment, this will be handled via Streamlit secrets.
    For local development, we'll save to a file.
    
    Args:
        email: The email address
        password: The email password or app password
        security_code: A security code to protect the credentials
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Hash the security code
        hashed_code = hashlib.sha256(security_code.encode()).hexdigest()
        
        # Create credentials dictionary
        credentials = {
            "sender_email": email,
            "sender_password": password,
            "hashed_code": hashed_code
        }
        
        # For local development, save to file
        # In cloud deployment, this should be set up in Streamlit secrets
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
            
        # Display instructions for Streamlit Cloud
        if os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD'):
            st.info("For Streamlit Cloud deployment, please add these credentials to your secrets.toml file.")
        
        return True
    except Exception as e:
        print(f"Error setting up email credentials: {e}")
        return False

def verify_security_code(security_code):
    """
    Verify a security code against the stored hash.
    For cloud deployment, checks against Streamlit secrets.
    For local development, checks against file.
    
    Args:
        security_code: The security code to verify
        
    Returns:
        tuple: (bool, dict) - Success status and credentials if successful
    """
    try:
        # First check if we're in Streamlit Cloud and have secrets configured
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            # Get the stored security code hash from secrets
            stored_hash = st.secrets.email.get('hashed_code')
            # If no stored hash in secrets, fall back to file
            if stored_hash:
                # Hash the provided code
                hashed_code = hashlib.sha256(security_code.encode()).hexdigest()
                
                # Verify against secrets
                if hashed_code == stored_hash:
                    # Return credentials from secrets
                    return True, {
                        "sender_email": st.secrets.email.get('sender_email'),
                        "sender_password": st.secrets.email.get('sender_password')
                    }
                else:
                    return False, None
        
        # Fall back to file-based verification for local development
        if not os.path.exists(CREDENTIALS_FILE):
            return False, None
        
        # Read credentials from file
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
        
        # Hash the provided code
        hashed_code = hashlib.sha256(security_code.encode()).hexdigest()
        
        # Verify against file
        if hashed_code == credentials.get("hashed_code"):
            return True, credentials
        else:
            return False, None
    except Exception as e:
        print(f"Error verifying security code: {e}")
        return False, None

def send_bill_pdf_with_security_code(security_code, receiver_email, subject, message, pdf_path):
    """
    Send an email with a PDF bill attachment using stored credentials and a security code.
    
    Args:
        security_code: The security code to access stored credentials
        receiver_email: The recipient's email address
        subject: The email subject
        message: The email message content
        pdf_path: Path to the PDF bill to attach
        
    Returns:
        str: Success or error message
    """
    # Verify security code
    verified, credentials = verify_security_code(security_code)
    
    if not verified or not credentials:
        return "Invalid security code or no credentials found"
    
    try:
        # Check if PDF file exists
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at {pdf_path}"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = credentials["sender_email"]
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Attach PDF file
        with open(pdf_path, 'rb') as file:
            pdf_attachment = MIMEApplication(file.read(), _subtype="pdf")
            pdf_filename = os.path.basename(pdf_path)
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            msg.attach(pdf_attachment)
        
        # Connect to SMTP server (using Gmail as an example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to account
        server.login(credentials["sender_email"], credentials["sender_password"])
        
        # Send email
        server.send_message(msg)
        
        # Close connection
        server.quit()
        
        return f"Bill PDF successfully sent to {receiver_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def send_email(receiver_email, subject, message):
    """
    Send a simple email without attachments.
    
    Args:
        receiver_email: The recipient's email address
        subject: The email subject
        message: The email message content
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    try:
        # Verify security code and get credentials
        if not os.path.exists(CREDENTIALS_FILE):
            return False, "Email credentials not found. Please set up email credentials first."
        
        # Read credentials
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
        
        sender_email = credentials.get("sender_email")
        sender_password = credentials.get("sender_password")
        
        if not sender_email or not sender_password:
            return False, "Invalid email credentials"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to SMTP server (using Gmail as an example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to account
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        
        # Close connection
        server.quit()
        
        return True, f"Email successfully sent to {receiver_email}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"