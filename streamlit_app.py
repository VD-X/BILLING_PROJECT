import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sys

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
from utils.data import prices, cosmetic_products, grocery_products, drink_products
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

# Initialize session state
if "billnumber" not in st.session_state:
    st.session_state.billnumber = generate_bill_number()

# Title
st.title("Grocery Billing System")

# Get customer information
customer_name, phone_number = display_customer_info_section()

# Get product selections
cosmetic_items, grocery_items, drink_items = display_product_selection(
    cosmetic_products, grocery_products, drink_products, prices
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
        elif not any(qty > 0 for qty in {**cosmetic_items, **grocery_items, **drink_items}.values()):
            display_error_message("Please select at least one product")
        else:
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
            
            # Display success message
            display_success_message("Bill calculated successfully!")

# Add the rest of your bill operation buttons (Save, Print, Email, Export)
with bill_op_cols[1]:
    if st.button("Save Bill", key="save_button"):
        if "bill_content" in st.session_state:
            result = save_bill(
                st.session_state.bill_content,
                st.session_state.billnumber,
                customer_name,
                phone_number,
                cosmetic_items,
                grocery_items,
                drink_items,
                st.session_state.totals,
                prices
            )
            display_success_message(result)
        else:
            display_error_message("Please calculate the bill first")
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
with bill_op_cols[3]:
    if st.button("Email Bill", key="email_button", type="primary"):
        if "bill_content" in st.session_state:
            st.session_state.show_email_form = True
        else:
            display_error_message("Please calculate the bill first")

# Add a new column for Export to Excel button
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
                prices
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
                    # Path to the PDF bill
                    pdf_path = f"d:\\adv billing\\bills\\{st.session_state.billnumber}.pdf"
                    
                    # Check if PDF exists
                    if not os.path.exists(pdf_path):
                        # Try to save the bill to PDF first if it doesn't exist
                        save_bill_to_pdf(
                            st.session_state.bill_content,
                            st.session_state.billnumber
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
    # Rerun the app to clear inputs
    st.rerun()

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


# Add this to your imports section
from utils.bill_operations import send_bill_pdf_to_customer

# Add this function to your Streamlit app
def email_bill_section():
    st.header("Email Bill to Customer")
    
    # Input fields
    bill_number = st.text_input("Bill Number")
    customer_email = st.text_input("Customer Email")
    customer_name = st.text_input("Customer Name")
    security_code = st.text_input("Security Code", type="password")
    
    if st.button("Send Bill"):
        if not bill_number or not customer_email or not customer_name or not security_code:
            st.error("Please fill in all fields")
        else:
            # Update the function to use security code
            from utils.email_utils import send_bill_pdf_with_security_code
            
            # Path to the PDF bill
            pdf_path = f"d:\\adv billing\\bills\\{bill_number}.pdf"
            
            # Check if PDF exists
            if not os.path.exists(pdf_path):
                st.error(f"Error: Bill PDF not found for {bill_number}")
            else:
                # Email content
                subject = f"Your Invoice #{bill_number}"
                message = f"""Dear {customer_name},

Thank you for your purchase. Please find your invoice attached to this email.

Invoice Number: {bill_number}
Date: {datetime.datetime.now().strftime("%d-%m-%Y")}

If you have any questions about this invoice, please contact our customer service.

Best regards,
Grocery Billing System
"""
                
                # Send the email with PDF attachment
                result = send_bill_pdf_with_security_code(
                    security_code=security_code,
                    receiver_email=customer_email,
                    subject=subject,
                    message=message,
                    pdf_path=pdf_path
                )
                
                if "successfully" in result:
                    st.success(result)
                else:
                    st.error(result)