import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import numpy as np
from sklearn.linear_model import LinearRegression
import tempfile

# Set page config
st.set_page_config(
    page_title="Billing Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Billing Analytics Dashboard")

# Function to load billing data
def load_billing_data():
    try:
        # For cloud deployment, check if there are any bills in the temporary directory
        temp_dir = os.path.join(tempfile.gettempdir(), "grocery_billing_bills")
        excel_dir = os.path.join(temp_dir, "excel_bills")
        
        # Check if the directory exists
        if not os.path.exists(excel_dir):
            return None
            
        # List all Excel files in the directory
        excel_files = [f for f in os.listdir(excel_dir) if f.endswith('.xlsx')]
        
        if not excel_files:
            return None
            
        # Create a list to store all dataframes
        all_data = []
        
        # Read each Excel file and extract the billing information
        for file in excel_files:
            file_path = os.path.join(excel_dir, file)
            try:
                # Read the Excel file
                df = pd.read_excel(file_path, header=None)
                
                # Extract bill information
                bill_number = df.iloc[1, 1]
                date_str = df.iloc[2, 1]
                customer_name = df.iloc[3, 1]
                phone_number = df.iloc[4, 1]
                
                # Find the subtotal, tax, and total rows
                for i in range(len(df)):
                    if df.iloc[i, 0] == "Subtotal:":
                        subtotal = df.iloc[i, 3]
                    elif df.iloc[i, 0] == "Tax (18%):":
                        tax = df.iloc[i, 3]
                    elif df.iloc[i, 0] == "Total:":
                        total = df.iloc[i, 3]
                
                # Create a dictionary with the bill information
                bill_data = {
                    'Bill Number': bill_number,
                    'Date': pd.to_datetime(date_str, format='%d-%m-%Y %H:%M:%S', errors='coerce'),
                    'Customer Name': customer_name,
                    'Phone Number': phone_number,
                    'Subtotal': subtotal,
                    'Tax': tax,
                    'Total': total
                }
                
                all_data.append(bill_data)
            except Exception as e:
                st.warning(f"Error reading file {file}: {str(e)}")
                continue
        
        if not all_data:
            return None
            
        # Create a dataframe from all the bill data
        billing_df = pd.DataFrame(all_data)
        return billing_df
        
    except Exception as e:
        st.error(f"Error loading billing data: {str(e)}")
        return None

# Load the billing data
billing_data = load_billing_data()

if billing_data is None:
    st.warning("Excel file not found. Please generate some bills first.")
    
    # Show a sample dashboard preview
    st.subheader("Sample Dashboard Preview")
    st.info("This is how the dashboard will look once you generate bills.")
    
    # Display a sample image or description
    st.image("https://via.placeholder.com/800x400?text=Sample+Analytics+Dashboard", 
             caption="Sample Analytics Dashboard")
else:
    # Continue with your existing dashboard code using billing_data
    # ...

    # Example: Display basic statistics
    st.subheader("Basic Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bills", len(billing_data))
    
    with col2:
        st.metric("Total Revenue", f"₹{billing_data['Total'].sum():.2f}")
    
    with col3:
        st.metric("Average Bill Amount", f"₹{billing_data['Total'].mean():.2f}")
    
    with col4:
        st.metric("Total Tax Collected", f"₹{billing_data['Tax'].sum():.2f}")
    
    # Add more visualizations as needed
    # ...