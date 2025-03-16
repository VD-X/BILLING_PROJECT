import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import our services
from config import init_config
from db_service import DatabaseService
from file_service import FileService

# Initialize configuration
config = init_config()

# Initialize services
db_service = DatabaseService(config)
file_service = FileService(config)

# Set page config
st.set_page_config(
    page_title="Grocery Billing System",
    page_icon="🛒",
    layout="wide"
)

# Main app
def main():
    st.title("Grocery Billing System")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select a page", 
        ["Billing", "Inventory", "Analytics", "Reports"]
    )
    
    # Display selected page
    if page == "Billing":
        billing_page()
    elif page == "Inventory":
        inventory_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Reports":
        reports_page()

# Billing page
def billing_page():
    st.header("Billing")
    
    # Load inventory data
    inventory_df = db_service.load_data("inventory")
    
    if inventory_df.empty:
        st.warning("No inventory data available. Please add items to inventory first.")
        return
    
    # Create a form for billing
    with st.form("billing_form"):
        # Customer information
        customer_name = st.text_input("Customer Name")
        customer_phone = st.text_input("Customer Phone")
        
        # Item selection
        st.subheader("Select Items")
        
        # Create empty bill items dataframe
        if 'bill_items' not in st.session_state:
            st.session_state.bill_items = pd.DataFrame(columns=["Item", "Price", "Quantity", "Total"])
        
        # Display available items
        selected_item = st.selectbox("Select Item", inventory_df["item_name"].tolist())
        item_price = float(inventory_df[inventory_df["item_name"] == selected_item]["price"].values[0])
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Add item button
        add_item = st.form_submit_button("Add Item")
        
        if add_item:
            # Calculate total
            total = item_price * quantity
            
            # Add to bill items
            new_item = pd.DataFrame({
                "Item": [selected_item],
                "Price": [item_price],
                "Quantity": [quantity],
                "Total": [total]
            })
            
            st.session_state.bill_items = pd.concat([st.session_state.bill_items, new_item], ignore_index=True)
    
    # Display current bill
    if not st.session_state.bill_items.empty:
        st.subheader("Current Bill")
        st.dataframe(st.session_state.bill_items)
        
        # Calculate grand total
        grand_total = st.session_state.bill_items["Total"].sum()
        st.subheader(f"Grand Total: ${grand_total:.2f}")
        
        # Generate bill button
        if st.button("Generate Bill"):
            # Create bill data
            bill_data = {
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": st.session_state.bill_items.to_dict('records'),
                "total_amount": grand_total
            }
            
            # Save to database
            db_service.save_data("bills", bill_data)
            
            # Generate PDF bill
            bill_df = st.session_state.bill_items.copy()
            bill_df["Price"] = bill_df["Price"].apply(lambda x: f"${x:.2f}")
            bill_df["Total"] = bill_df["Total"].apply(lambda x: f"${x:.2f}")
            
            # Add customer info and grand total
            bill_info = pd.DataFrame({
                "Item": ["", "Customer:", "Phone:", "Date:", "", "Grand Total:"],
                "Price": ["", customer_name, customer_phone, datetime.now().strftime("%Y-%m-%d"), "", ""],
                "Quantity": ["", "", "", "", "", ""],
                "Total": ["", "", "", "", "", f"${grand_total:.2f}"]
            })
            
            full_bill = pd.concat([bill_info.iloc[:4], bill_df, bill_info.iloc[4:]], ignore_index=True)
            
            pdf_path = file_service.generate_pdf(
                full_bill, 
                f"bill_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
                title=f"Invoice #{datetime.now().strftime('%Y%m%d%H%M')}"
            )
            
            # Provide download link
            st.markdown(
                file_service.get_download_link(pdf_path, "Download Bill PDF"),
                unsafe_allow_html=True
            )
            
            # Generate QR code for bill
            qr_data = f"Bill #{datetime.now().strftime('%Y%m%d%H%M')}\nCustomer: {customer_name}\nTotal: ${grand_total:.2f}"
            qr_code = file_service.generate_qr_code(qr_data)
            st.image(qr_code, width=200)
            
            # Clear bill items
            st.session_state.bill_items = pd.DataFrame(columns=["Item", "Price", "Quantity", "Total"])
            st.success("Bill generated successfully!")

# Inventory page
def inventory_page():
    st.header("Inventory Management")
    
    # Load inventory data
    inventory_df = db_service.load_data("inventory")
    
    # Display current inventory
    if not inventory_df.empty:
        st.subheader("Current Inventory")
        st.dataframe(inventory_df)
    
    # Add new item form
    with st.form("add_item_form"):
        st.subheader("Add New Item")
        item_name = st.text_input("Item Name")
        item_price = st.number_input("Price", min_value=0.01, step=0.01)
        item_quantity = st.number_input("Quantity", min_value=1, step=1)
        item_category = st.text_input("Category")
        
        # Submit button
        submit = st.form_submit_button("Add Item")
        
        if submit:
            # Create item data
            item_data = {
                "item_name": item_name,
                "price": item_price,
                "quantity": item_quantity,
                "category": item_category,
                "added_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Save to database
            db_service.save_data("inventory", item_data)
            st.success(f"Item '{item_name}' added successfully!")
            st.experimental_rerun()

# Analytics page
def analytics_page():
    st.header("Analytics Dashboard")
    
    # Load bills data
    bills_df = db_service.load_data("bills")
    
    if bills_df.empty:
        st.warning("No billing data available for analysis.")
        return
    
    # Extract items from bills
    items_list = []
    for _, bill in bills_df.iterrows():
        for item in bill["items"]:
            item["bill_date"] = bill["date"]
            items_list.append(item)
    
    items_df = pd.DataFrame(items_list)
    
    # Convert date strings to datetime
    bills_df["date"] = pd.to_datetime(bills_df["date"])
    items_df["bill_date"] = pd.to_datetime(items_df["bill_date"])
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${bills_df['total_amount'].sum():.2f}")
    with col2:
        st.metric("Total Orders", len(bills_df))
    with col3:
        st.metric("Average Order Value", f"${bills_df['total_amount'].mean():.2f}")
    
    # Sales over time
    st.subheader("Sales Over Time")
    sales_over_time = bills_df.groupby(bills_df['date'].dt.date)['total_amount'].sum().reset_index()
    st.line_chart(sales_over_time.set_index('date'))
    
    # Top selling items
    st.subheader("Top Selling Items")
    top_items = items_df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(top_items.set_index('Item')['Quantity'])
    
    # Sales by category (if category data is available)
    if 'category' in items_df.columns:
        st.subheader("Sales by Category")
        category_sales = items_df.groupby('category')['Total'].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(category_sales.set_index('category'))
    
    # Export analytics data
    if st.button("Export Analytics Data"):
        # Create Excel with multiple sheets
        excel_path = file_service.generate_excel(
            {
                'Sales Summary': sales_over_time,
                'Top Items': top_items,
                'All Bills': bills_df
            },
            f"analytics_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        
        st.markdown(
            file_service.get_download_link(excel_path, "Download Analytics Excel"),
            unsafe_allow_html=True
        )

# Reports page
def reports_page():
    st.header("Reports")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Load bills data
    bills_df = db_service.load_data("bills")
    
    if bills_df.empty:
        st.warning("No billing data available for reports.")
        return
    
    # Convert date strings to datetime
    bills_df["date"] = pd.to_datetime(bills_df["date"])
    
    # Filter by date range
    filtered_bills = bills_df[
        (bills_df["date"].dt.date >= start_date) & 
        (bills_df["date"].dt.date <= end_date)
    ]
    
    # Report types
    report_type = st.selectbox(
        "Select Report Type",
        ["Sales Summary", "Customer Report", "Inventory Movement"]
    )
    
    if report_type == "Sales Summary":
        # Sales summary report
        st.subheader("Sales Summary Report")
        
        # Calculate metrics
        total_sales = filtered_bills["total_amount"].sum()
        total_orders = len(filtered_bills)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sales", f"${total_sales:.2f}")
        with col2:
            st.metric("Total Orders", total_orders)
        with col3:
            st.metric("Average Order Value", f"${avg_order_value:.2f}")
        
        # Daily sales
        daily_sales = filtered_bills.groupby(filtered_bills['date'].dt.date)['total_amount'].sum().reset_index()
        daily_sales.columns = ["Date", "Sales"]
        
        st.subheader("Daily Sales")
        st.dataframe(daily_sales)
        st.line_chart(daily_sales.set_index("Date"))
        
        # Generate report
        if st.button("Generate Sales Report"):
            # Create report dataframe
            report_df = daily_sales.copy()
            
            # Add summary row
            summary = pd.DataFrame({
                "Date": ["TOTAL"],
                "Sales": [total_sales]
            })
            report_df = pd.concat([report_df, summary], ignore_index=True)
            
            # Format currency
            report_df["Sales"] = report_df["Sales"].apply(lambda x: f"${x:.2f}")
            
            # Generate PDF
            pdf_path = file_service.generate_pdf(
                report_df,
                f"sales_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
                title=f"Sales Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
            )
            
            st.markdown(
                file_service.get_download_link(pdf_path, "Download Sales Report PDF"),
                unsafe_allow_html=True
            )
    
    elif report_type == "Customer Report":
        # Customer report
        st.subheader("Customer Report")
        
        # Group by customer
        customer_data = filtered_bills.groupby(["customer_name", "customer_phone"]).agg(
            total_orders=pd.NamedAgg(column="date", aggfunc="count"),
            total_spent=pd.NamedAgg(column="total_amount", aggfunc="sum"),
            last_order=pd.NamedAgg(column="date", aggfunc="max")
        ).reset_index()
        
        # Calculate average order value
        customer_data["avg_order_value"] = customer_data["total_spent"] / customer_data["total_orders"]
        
        # Format for display
        display_data = customer_data.copy()
        display_data["total_spent"] = display_data["total_spent"].apply(lambda x: f"${x:.2f}")
        display_data["avg_order_value"] = display_data["avg_order_value"].apply(lambda x: f"${x:.2f}")
        display_data["last_order"] = display_data["last_order"].dt.strftime("%Y-%m-%d")
        
        st.dataframe(display_data)
        
        # Generate report
        if st.button("Generate Customer Report"):
            # Generate PDF
            pdf_path = file_service.generate_pdf(
                display_data,
                f"customer_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
                title=f"Customer Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
            )
            
            st.markdown(
                file_service.get_download_link(pdf_path, "Download Customer Report PDF"),
                unsafe_allow_html=True
            )
    
    elif report_type == "Inventory Movement":
        # Inventory movement report
        st.subheader("Inventory Movement Report")
        
        # Load inventory data
        inventory_df = db_service.load_data("inventory")
        
        if inventory_df.empty:
            st.warning("No inventory data available.")
            return
        
        # Extract items from bills
        items_list = []
        for _, bill in filtered_bills.iterrows():
            for item in bill["items"]:
                item["bill_date"] = bill["date"]
                items_list.append(item)
        
        items_df = pd.DataFrame(items_list)
        
        # Group by item
        if not items_df.empty:
            item_movement = items_df.groupby("Item")["Quantity"].sum().reset_index()
            item_movement.columns = ["Item", "Quantity Sold"]
            
            # Merge with inventory
            if "item_name" in inventory_df.columns and "quantity" in inventory_df.columns:
                inventory_simple = inventory_df[["item_name", "quantity"]].copy()
                inventory_simple.columns = ["Item", "Current Stock"]
                
                movement_report = pd.merge(item_movement, inventory_simple, on="Item", how="outer").fillna(0)
                
                st.dataframe(movement_report)
                
                # Generate report
                if st.button("Generate Inventory Report"):
                    # Generate PDF
                    pdf_path = file_service.generate_pdf(
                        movement_report,
                        f"inventory_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
                        title=f"Inventory Movement ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
                    )
                    
                    st.markdown(
                        file_service.get_download_link(pdf_path, "Download Inventory Report PDF"),
                        unsafe_allow_html=True
                    )
            else:
                st.dataframe(item_movement)
        else:
            st.info("No items sold in the selected date range.")

# Run the app
if __name__ == "__main__":
    main()