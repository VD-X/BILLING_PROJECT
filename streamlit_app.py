import streamlit as st
import pandas as pd
import os
import json
import pickle
from datetime import datetime
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.bill_operations import (
    generate_bill_number, 
    calculate_total, 
    generate_bill, 
    save_bill, 
    print_bill, 
    export_bill_to_excel
)
from utils.pdf_operations import extract_pdf_text, save_bill_to_pdf
from utils.email_utils import send_email
from utils.data import prices as default_prices, cosmetic_products as default_cosmetic_products, grocery_products as default_grocery_products, drink_products as default_drink_products
from utils.ui import (
    set_page_style,
    display_customer_info_section,
    display_product_selection,
    display_bill_operations_section,
    display_bill_content,
    display_success_message,
    display_error_message
)

# Set page config
st.set_page_config(
    page_title="Grocery Billing System",
    page_icon="🛒",
    layout="wide"
)

# Apply custom styling
set_page_style()

# Define file paths for product data and inventory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
PRICES_FILE = os.path.join(DATA_DIR, "prices.pkl")

# Function to load product data
def load_product_data():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with existing data from utils/data.py
        products = {
            "Cosmetics": default_cosmetic_products,
            "Groceries": default_grocery_products,
            "Drinks": default_drink_products
        }
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(products, f, indent=4)
        return products

# Function to load inventory data
def load_inventory_data():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize empty inventory
        inventory = {}
        # Add all existing products with default inventory of 10
        products = load_product_data()
        for category, category_products in products.items():
            for product_type, variants in category_products.items():
                for variant in variants:
                    product_name = variant["name"]
                    inventory[product_name] = {
                        "quantity": 10,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(inventory, f, indent=4)
        return inventory

# Function to load prices
def load_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        # Use default prices
        return default_prices

# Define a function to get the appropriate bills directory
def get_bills_directory():
    """Returns the appropriate directory for storing bills based on environment"""
    # Check if we're running on Streamlit Cloud or similar service
    if os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD'):
        # Use a temporary directory for cloud deployment
        bills_dir = Path(tempfile.gettempdir()) / "grocery_billing_bills"
    else:
        # For local development, use the saved_bills directory in the project
        bills_dir = Path(__file__).parent / "saved_bills"
    
    # Ensure the directory exists
    os.makedirs(str(bills_dir), exist_ok=True)
    return str(bills_dir)

# Initialize the bills directory
BILLS_DIRECTORY = get_bills_directory()
st.session_state.bills_directory = BILLS_DIRECTORY

# Initialize session state
if "billnumber" not in st.session_state:
    st.session_state.billnumber = generate_bill_number()

# Load product and inventory data
products = load_product_data()
cosmetic_products = products.get("Cosmetics", default_cosmetic_products)
grocery_products = products.get("Groceries", default_grocery_products)
drink_products = products.get("Drinks", default_drink_products)
inventory = load_inventory_data()
prices = load_prices()

# Initialize session state for selected products from search
if "selected_products" not in st.session_state:
    st.session_state.selected_products = []

# Title
st.title("Grocery Billing System")

# Get customer information
customer_name, phone_number = display_customer_info_section()

# Add a search bar for products
st.sidebar.markdown('<div class="section-header">Product Search</div>', unsafe_allow_html=True)
search_term = st.sidebar.text_input("Search for products", key="main_search")
if st.sidebar.button("Search"):
    if search_term:
        st.switch_page("pages/product_management.py")

# Display products from search if any were selected
if st.session_state.selected_products:
    st.markdown('<div class="section-header">Selected Products from Search</div>', unsafe_allow_html=True)
    
    # Create a DataFrame for better display
    selected_df = pd.DataFrame([
        {
            "Product": item["name"],
            "Price": f"₹{item['price']}",
            "Quantity": item["quantity"],
            "Total": f"₹{item['price'] * item['quantity']}"
        }
        for item in st.session_state.selected_products
    ])
    
    st.dataframe(selected_df)
    
    if st.button("Clear Selected Products"):
        st.session_state.selected_products = []
        st.rerun()

# Get product selections with inventory awareness
cosmetic_items, grocery_items, drink_items = display_product_selection(
    cosmetic_products, grocery_products, drink_products, prices, inventory
)

# Bill operations section
bill_op_cols = display_bill_operations_section()

# Calculate button
with bill_op_cols[0]:
    if st.button("Calculate Total", key="calc_button"):
        if not customer_name:
            display_error_message("Please enter customer name")
        elif not phone_number:
            display_error_message("Please enter phone number")
        elif not any(qty > 0 for qty in {**cosmetic_items, **grocery_items, **drink_items}.values()) and not st.session_state.selected_products:
            display_error_message("Please select at least one product")
        else:
            # Add products from search to appropriate categories
            for item in st.session_state.selected_products:
                category = item["category"]
                if category == "Cosmetics":
                    cosmetic_items[item["name"]] = item["quantity"]
                elif category == "Groceries":
                    grocery_items[item["name"]] = item["quantity"]
                elif category == "Drinks":
                    drink_items[item["name"]] = item["quantity"]
            
            # Calculate totals
            totals = calculate_total(cosmetic_items, grocery_items, drink_items, prices)
            st.session_state.totals = totals
            
            # Generate bill
            bill_content = generate_bill(
                customer_name, 
                phone_number, 
                st.session_state.billnumber, 
                cosmetic_items, 
                grocery_items, 
                drink_items, 
                totals,
                prices
            )
            st.session_state.bill_content = bill_content

            # --- Automatically save PDF to saved_bills ---
            try:
                from utils.pdf_operations import save_bill_to_pdf
                save_bill_to_pdf(
                    bill_content,
                    st.session_state.billnumber,
                    bills_directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_bills"),
                    customer_name=customer_name,
                    phone_number=phone_number,
                    cosmetic_items=cosmetic_items,
                    grocery_items=grocery_items,
                    drink_items=drink_items,
                    totals=totals,
                    prices=prices
                )
            except Exception as e:
                display_error_message(f"Error auto-saving PDF: {e}")

            # Update inventory after bill calculation
            all_items = {**cosmetic_items, **grocery_items, **drink_items}
            for product, quantity in all_items.items():
                if quantity > 0 and product in inventory:
                    inventory[product]["quantity"] = max(0, inventory[product]["quantity"] - quantity)
                    inventory[product]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save updated inventory
            with open(INVENTORY_FILE, 'w') as f:
                json.dump(inventory, f, indent=4)
            
            # Clear selected products from search
            st.session_state.selected_products = []
            
            # Display success message
            display_success_message("Bill calculated successfully!")

# Save Bill button
with bill_op_cols[1]:
    if st.button("Save Bill", key="save_button"):
        if "bill_content" in st.session_state:
            # Save TXT file
            result_txt = save_bill(
                st.session_state.bill_content,
                st.session_state.billnumber,
                customer_name,
                phone_number,
                cosmetic_items,
                grocery_items,
                drink_items,
                st.session_state.totals,
                prices,
                bills_directory=st.session_state.bills_directory  # Pass the directory
            )
            # Save PDF file
            try:
                from utils.pdf_operations import save_bill_to_pdf
                result_pdf = save_bill_to_pdf(
                    st.session_state.bill_content,
                    st.session_state.billnumber,
                    bills_directory=st.session_state.bills_directory,
                    customer_name=customer_name,
                    phone_number=phone_number,
                    cosmetic_items=cosmetic_items,
                    grocery_items=grocery_items,
                    drink_items=drink_items,
                    totals=st.session_state.totals,
                    prices=prices
                )
                display_success_message(result_txt)
                display_success_message(result_pdf)
            except Exception as e:
                display_success_message(result_txt)
                display_error_message(f"Error saving PDF: {e}")
        else:
            display_error_message("Please calculate the bill first")

# Print Bill button
with bill_op_cols[2]:
    if st.button("Print Bill", key="print_button"):
        if "bill_content" in st.session_state:
            result = print_bill(st.session_state.bill_content)
            if result.startswith("Error") or "only available" in result:
                display_error_message(result)
            else:
                display_success_message(result)
        else:
            display_error_message("Please calculate the bill first")

# Email Bill button
with bill_op_cols[3]:
    if st.button("Email Bill", key="email_button", type="primary"):
        if "bill_content" in st.session_state:
            st.session_state.show_email_form = True
        else:
            display_error_message("Please calculate the bill first")

# Export to Excel button
with st.container():
    if st.button("Export to Excel", key="excel_button"):
        if "totals" in st.session_state:
            file_path = export_bill_to_excel(
                customer_name,
                phone_number,
                st.session_state.billnumber,
                cosmetic_items,
                grocery_items,
                drink_items,
                st.session_state.totals,
                prices,
                bills_directory=st.session_state.bills_directory  # Pass the directory
            )
            display_success_message(f"Bill exported to {file_path}")
        else:
            display_error_message("Please calculate the bill first")

# Email form section
if "show_email_form" in st.session_state and st.session_state.show_email_form:
    st.markdown("## Send Bill via Email")
    
    email_col1, email_col2 = st.columns(2)
    
    with email_col1:
        security_code = st.text_input("Security Code", type="password", key="security_code")
        
    with email_col2:
        receiver_email = st.text_input("Customer Email", key="receiver_email")
        
    email_action_col1, email_action_col2 = st.columns(2)
    with email_action_col1:
        if st.button("Send Email", key="send_email_button"):
            if security_code and receiver_email:
                try:
                    # Path to the PDF bill - UPDATED
                    pdf_path = os.path.join(st.session_state.bills_directory, f"{st.session_state.billnumber}.pdf")
                    
                    # Check if PDF exists
                    if not os.path.exists(pdf_path):
                        # Try to save the bill to PDF first if it doesn't exist
                        save_bill_to_pdf(
                            st.session_state.bill_content,
                            st.session_state.billnumber,
                            bills_directory=st.session_state.bills_directory  # Pass the directory
                        )
                    
                    # Check again if PDF exists after trying to save
                    if os.path.exists(pdf_path):
                        # Email content
                        subject = f"Your Invoice #{st.session_state.billnumber}"
                        message = f"""Dear {customer_name},

Thank you for your purchase. Please find your invoice attached to this email.

Invoice Number: {st.session_state.billnumber}
Date: {datetime.now().strftime("%d-%m-%Y")}

If you have any questions about this invoice, please contact our customer service.

Best regards,
Grocery Billing System
"""
                        
                        # Send the email with PDF attachment
                        from utils.email_utils import send_bill_pdf_with_security_code
                        result = send_bill_pdf_with_security_code(
                            security_code=security_code,
                            receiver_email=receiver_email,
                            subject=subject,
                            message=message,
                            pdf_path=pdf_path
                        )
                        
                        if "successfully" in result:
                            display_success_message(result)
                            st.session_state.show_email_form = False
                        else:
                            display_error_message(result)
                    else:
                        display_error_message("Could not create PDF bill. Please save the bill first.")
                except Exception as e:
                    display_error_message(f"Error sending email: {str(e)}")
            else:
                display_error_message("Please fill all email fields")
    
    with email_action_col2:
        if st.button("Cancel", key="cancel_email_button"):
            st.session_state.show_email_form = False
            st.rerun()

# Display bill content if available
if "bill_content" in st.session_state:
    display_bill_content(st.session_state.bill_content)

# Reset button to clear the form
st.sidebar.markdown("---")
if st.sidebar.button("New Bill"):
    # Generate a new bill number
    st.session_state.billnumber = generate_bill_number()
    # Clear session state
    if "bill_content" in st.session_state:
        del st.session_state.bill_content
    if "totals" in st.session_state:
        del st.session_state.totals
    if "show_email_form" in st.session_state:
        del st.session_state.show_email_form
    # Clear selected products from search
    st.session_state.selected_products = []
    # Rerun the app
    st.rerun()

# Add link to Product Management page
st.sidebar.markdown("---")
st.sidebar.markdown("### Manage Products & Inventory")
if st.sidebar.button("Go to Product Management"):
    st.switch_page("pages/product_management.py")

# Add this new section for email setup
st.sidebar.markdown("---")
with st.sidebar.expander("Email Setup"):
    st.write("Set up your email credentials with a security code")
    sender_email = st.text_input("Sender Email", key="setup_sender_email")
    sender_password = st.text_input("App Password", type="password", key="setup_sender_password")
    security_code = st.text_input("Create Security Code", type="password", key="setup_security_code")
    
    if st.button("Save Credentials"):
        if sender_email and sender_password and security_code:
            from utils.email_utils import setup_email_credentials
            if setup_email_credentials(sender_email, sender_password, security_code):
                st.success("Email credentials saved successfully!")
                st.info("You can now use your security code to send emails.")
            else:
                st.error("Failed to save email credentials.")
        else:
            st.warning("Please fill in all fields.")
