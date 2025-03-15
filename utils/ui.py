import os
import streamlit as st
from utils.pdf_operations import extract_pdf_text

def set_page_style():
    """Set the page style and CSS for the application."""
    # Apply custom CSS
    st.markdown("""
    <style>
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Section headers */
        .section-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-weight: bold;
            font-size: 16px;
            margin-top: 10px;
        }
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def display_customer_info_section():
    """Display the customer information section and return the input values."""
    st.markdown('<div class="section-header">Customer Information</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
    with col2:
        phone_number = st.text_input("Phone Number")
    
    return customer_name, phone_number

def display_product_selection(cosmetic_products, grocery_products, drink_products, prices):
    """Display product selection section with variants"""
    st.markdown('<div class="section-header">Product Selection</div>', unsafe_allow_html=True)
    
    # Create tabs for different product categories
    tabs = st.tabs(["Cosmetics", "Groceries", "Drinks"])
    
    # Initialize dictionaries to store selected quantities
    cosmetic_items = {}
    grocery_items = {}
    drink_items = {}
    
    # Cosmetics tab
    with tabs[0]:
        st.markdown("### Cosmetic Products")
        
        # Create an expander for each product type
        for product_type, variants in cosmetic_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"cosmetic_{variant['name']}"
                        )
                        cosmetic_items[variant['name']] = qty
    
    # Groceries tab
    with tabs[1]:
        st.markdown("### Grocery Products")
        
        # Create an expander for each product type
        for product_type, variants in grocery_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"grocery_{variant['name']}"
                        )
                        grocery_items[variant['name']] = qty
    
    # Drinks tab
    with tabs[2]:
        st.markdown("### Drink Products")
        
        # Create an expander for each product type
        for product_type, variants in drink_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"drink_{variant['name']}"
                        )
                        drink_items[variant['name']] = qty
    
    return cosmetic_items, grocery_items, drink_items

def display_bill_operations_section():
    """Display the bill operations section with buttons."""
    st.markdown('<div class="section-header">Bill Operations</div>', unsafe_allow_html=True)
    return st.columns(4)

def display_bill_content(bill_content):
    """Display the bill content in a formatted way."""
    st.markdown('<div class="section-header">Bill Preview</div>', unsafe_allow_html=True)
    
    # Create a styled container for the bill with improved text visibility and professional design
    st.markdown("""
    <div style="border: 1px solid #2e7d32; border-radius: 8px; overflow: hidden; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="background-color: #2e7d32; padding: 15px; text-align: center;">
            <h3 style="color: white; margin: 0; font-size: 20px; font-weight: bold;">OFFICIAL RECEIPT</h3>
        </div>
        <div style="padding: 20px; background-color: white; font-family: 'Courier New', monospace; white-space: pre-wrap; color: #000; font-weight: 700; line-height: 1.6; font-size: 15px; text-align: center;">
        {}
        </div>
        <div style="background-color: #f1f8e9; padding: 12px; border-top: 1px solid #c8e6c9; text-align: center;">
            <p style="margin: 0; color: #2e7d32; font-size: 14px; font-weight: 500;">Thank you for shopping with us!</p>
        </div>
    </div>
    """.format(bill_content.replace('\n', '<br>').replace(' ', '&nbsp;')), unsafe_allow_html=True)

def display_error_message(message, icon="⚠️"):
    """
    Display a styled error message with an optional icon.
    
    Args:
        message (str): The error message to display
        icon (str): An emoji icon to display with the message
    """
    st.markdown(f"""
    <div style="background-color: #ffebee; border-left: 4px solid #c62828; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #c62828; display: flex; align-items: center;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <span><strong>Error:</strong> {message}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_success_message(message, icon="✅"):
    """
    Display a styled success message with an optional icon.
    
    Args:
        message (str): The success message to display
        icon (str): An emoji icon to display with the message
    """
    st.markdown(f"""
    <div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 15px; margin: 20px 0; border-radius: 4px;">
        <p style="margin: 0; color: #1b5e20; display: flex; align-items: center;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <span><strong>Success!</strong> {message}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Alias for backward compatibility
def set_custom_style():
    """
    Set custom styles for the application.
    This is an alias for set_page_style for backward compatibility.
    """
    return set_page_style()