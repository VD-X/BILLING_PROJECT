import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import sys
import pickle

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from utils.data import cosmetic_products, grocery_products, drink_products, prices
from utils.ui import set_page_style, display_success_message, display_error_message

# Set page config
st.set_page_config(
    page_title="Product Management",
    page_icon="📦",
    layout="wide"
)

# Apply custom styling
set_page_style()

# Define file paths for product data and inventory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")

# Initialize session state for search results
if "search_results" not in st.session_state:
    st.session_state.search_results = []

# Function to load product data
def load_product_data():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with existing data from utils/data.py
        products = {
            "Cosmetics": cosmetic_products,
            "Groceries": grocery_products,
            "Drinks": drink_products
        }
        save_product_data(products)
        return products

# Function to save product data
def save_product_data(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=4)

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
        save_inventory_data(inventory)
        return inventory

# Function to save inventory data
def save_inventory_data(inventory):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=4)

# Function to update prices.py
def update_prices_file():
    products = load_product_data()
    all_prices = {}
    
    for category, category_products in products.items():
        for product_type, variants in category_products.items():
            for variant in variants:
                all_prices[variant["name"]] = variant["price"]
    
    # Save to pickle file for easy loading
    with open(os.path.join(DATA_DIR, "prices.pkl"), 'wb') as f:
        pickle.dump(all_prices, f)
    
    return all_prices

# Load data
products = load_product_data()
inventory = load_inventory_data()

# Title
st.title("Product Management System")

# Create tabs for different functions
tabs = st.tabs(["Product Categories", "Add New Products", "Inventory Management", "Search Products"])

# Product Categories Tab
with tabs[0]:
    st.header("Manage Product Categories")
    
    # Add new category
    with st.expander("Add New Product Category"):
        new_category = st.text_input("New Category Name", key="new_category")
        if st.button("Add Category"):
            if new_category:
                if new_category not in products:
                    products[new_category] = {}
                    save_product_data(products)
                    display_success_message(f"Category '{new_category}' added successfully!")
                    st.rerun()
                else:
                    display_error_message(f"Category '{new_category}' already exists!")
            else:
                display_error_message("Please enter a category name!")
    
    # Display existing categories
    for category in products:
        st.subheader(category)
        
        # Add new product type to this category
        with st.expander(f"Add New Product Type to {category}"):
            new_product_type = st.text_input("New Product Type", key=f"new_product_type_{category}")
            if st.button("Add Product Type", key=f"add_product_type_{category}"):
                if new_product_type:
                    if new_product_type not in products[category]:
                        products[category][new_product_type] = []
                        save_product_data(products)
                        display_success_message(f"Product type '{new_product_type}' added to {category}!")
                        st.rerun()
                    else:
                        display_error_message(f"Product type '{new_product_type}' already exists in {category}!")
                else:
                    display_error_message("Please enter a product type name!")
        
        # Display product types in this category
        for product_type in products[category]:
            st.write(f"**{product_type}**")
            
            # Display variants in a table
            if products[category][product_type]:
                variants_df = pd.DataFrame(products[category][product_type])
                st.dataframe(variants_df)
            else:
                st.info(f"No products added to {product_type} yet.")

# Add New Products Tab
with tabs[1]:
    st.header("Add New Products")
    
    # Select category
    category = st.selectbox("Select Category", list(products.keys()))
    
    if category:
        # Select product type
        product_type = st.selectbox("Select Product Type", list(products[category].keys()))
        
        if product_type:
            with st.form("add_product_form"):
                st.subheader(f"Add New Product to {category} - {product_type}")
                
                product_name = st.text_input("Product Name")
                product_price = st.number_input("Product Price (₹)", min_value=0.0, step=0.5)
                initial_stock = st.number_input("Initial Stock Quantity", min_value=0, step=1, value=10)
                
                submitted = st.form_submit_button("Add Product")
                
                if submitted:
                    if product_name:
                        # Check if product already exists
                        exists = False
                        for variant in products[category][product_type]:
                            if variant["name"] == product_name:
                                exists = True
                                break
                        
                        if not exists:
                            # Add to products
                            products[category][product_type].append({
                                "name": product_name,
                                "price": product_price
                            })
                            save_product_data(products)
                            
                            # Add to inventory
                            inventory[product_name] = {
                                "quantity": initial_stock,
                                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_inventory_data(inventory)
                            
                            # Update prices
                            update_prices_file()
                            
                            display_success_message(f"Product '{product_name}' added successfully!")
                            st.rerun()
                        else:
                            display_error_message(f"Product '{product_name}' already exists!")
                    else:
                        display_error_message("Please enter a product name!")

# Inventory Management Tab
with tabs[2]:
    st.header("Inventory Management")
    
    # Search for product in inventory
    search_term = st.text_input("Search Product", key="inventory_search")
    
    if search_term:
        # Filter inventory based on search term
        filtered_inventory = {k: v for k, v in inventory.items() if search_term.lower() in k.lower()}
        
        if filtered_inventory:
            # Convert to DataFrame for better display
            inventory_df = pd.DataFrame([
                {
                    "Product": product,
                    "Quantity": data["quantity"],
                    "Last Updated": data["last_updated"]
                }
                for product, data in filtered_inventory.items()
            ])
            
            st.dataframe(inventory_df)
            
            # Select product to update
            selected_product = st.selectbox("Select Product to Update", list(filtered_inventory.keys()))
            
            if selected_product:
                with st.form("update_inventory_form"):
                    current_qty = inventory[selected_product]["quantity"]
                    st.write(f"Current Quantity: {current_qty}")
                    
                    update_type = st.radio("Update Type", ["Set New Quantity", "Add Stock", "Remove Stock"])
                    
                    if update_type == "Set New Quantity":
                        new_qty = st.number_input("New Quantity", min_value=0, step=1, value=current_qty)
                    elif update_type == "Add Stock":
                        add_qty = st.number_input("Quantity to Add", min_value=1, step=1, value=1)
                        new_qty = current_qty + add_qty
                    else:  # Remove Stock
                        if current_qty <= 0:
                            st.warning("No stock to remove.")
                            remove_qty = 0
                            new_qty = 0
                        else:
                            remove_qty = st.number_input("Quantity to Remove", min_value=1, max_value=current_qty, step=1, value=1)
                            new_qty = current_qty - remove_qty
                    
                    submitted = st.form_submit_button("Update Inventory")
                    
                    if submitted:
                        inventory[selected_product]["quantity"] = new_qty
                        inventory[selected_product]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_inventory_data(inventory)
                        display_success_message(f"Inventory for '{selected_product}' updated successfully!")
                        st.rerun()
        else:
            st.info("No products found matching your search term.")
    else:
        # Show all inventory
        inventory_df = pd.DataFrame([
            {
                "Product": product,
                "Quantity": data["quantity"],
                "Last Updated": data["last_updated"]
            }
            for product, data in inventory.items()
        ])
        
        st.dataframe(inventory_df)

# Search Products Tab
with tabs[3]:
    st.header("Search Products")
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_term = st.text_input("Search Products", key="product_search")
    
    with search_col2:
        search_category = st.selectbox("Category Filter", ["All Categories"] + list(products.keys()))
    
    if st.button("Search"):
        results = []
        
        if search_category == "All Categories":
            categories_to_search = products.keys()
        else:
            categories_to_search = [search_category]
        
        for category in categories_to_search:
            for product_type, variants in products[category].items():
                for variant in variants:
                    if search_term.lower() in variant["name"].lower():
                        # Check inventory
                        stock = inventory.get(variant["name"], {}).get("quantity", 0)
                        
                        results.append({
                            "Category": category,
                            "Type": product_type,
                            "Name": variant["name"],
                            "Price": variant["price"],
                            "Stock": stock
                        })
        
        if results:
            st.session_state.search_results = results
            
            # Display results in a table
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)
            
            # Add to bill section
            st.subheader("Add to Current Bill")
            
            selected_product = st.selectbox("Select Product", [r["Name"] for r in results])
            
            if selected_product:
                # Find the selected product in results
                product_info = next((r for r in results if r["Name"] == selected_product), None)
                
                if product_info:
                    st.write(f"**Product:** {product_info['Name']}")
                    st.write(f"**Price:** ₹{product_info['Price']}")
                    st.write(f"**Available Stock:** {product_info['Stock']}")
                    
                    # Add to bill button
                    quantity = st.number_input("Quantity", min_value=1, max_value=product_info['Stock'], step=1, value=1)
                    
                    if st.button("Add to Bill"):
                        # Store in session state to be used in the main app
                        if "selected_products" not in st.session_state:
                            st.session_state.selected_products = []
                        
                        st.session_state.selected_products.append({
                            "category": product_info["Category"],
                            "type": product_info["Type"],
                            "name": product_info["Name"],
                            "price": product_info["Price"],
                            "quantity": quantity
                        })
                        
                        # Update inventory
                        inventory[product_info["Name"]]["quantity"] -= quantity
                        save_inventory_data(inventory)
                        
                        display_success_message(f"Added {quantity} x {product_info['Name']} to bill!")
                        st.rerun()
        else:
            st.info("No products found matching your search criteria.")

# Display selected products for the current bill
if "selected_products" in st.session_state and st.session_state.selected_products:
    st.sidebar.header("Current Bill Items")
    
    for i, product in enumerate(st.session_state.selected_products):
        st.sidebar.write(f"{product['quantity']} x {product['name']} - ₹{product['price'] * product['quantity']}")
    
    if st.sidebar.button("Clear Bill"):
        st.session_state.selected_products = []
        st.rerun()
    
    if st.sidebar.button("Go to Billing"):
        # Redirect to main billing page
        st.switch_page("streamlit_app.py")
