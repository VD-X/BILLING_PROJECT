import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys

# Set page config
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database service and config
try:
    from db_service import DatabaseService
    from config import init_config
except ImportError as e:
    st.error(f"Error importing modules: {str(e)}")
    st.error("Please make sure all required modules are installed and the project structure is correct.")
    st.stop()

# Initialize services
config = init_config()
db_service = DatabaseService(config)

# Ensure temp directory exists for exports
temp_dir = config.get("temp_dir")
if not temp_dir:
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
    config["temp_dir"] = temp_dir
os.makedirs(temp_dir, exist_ok=True)

# Page title and description
st.title("Sales Analytics Dashboard")
st.write("View sales trends, product performance, and forecasts based on your billing data.")

# Load sales data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sales_data():
    sales_df = db_service.load_data("sales")
    
    # Create sample data if no data exists (for demonstration)
    if sales_df.empty:
        st.warning("No sales data available. Displaying sample data for demonstration.")
        # Generate sample data
        sample_data = []
        categories = ["Cosmetics", "Grocery", "Drinks"]
        products = {
            "Cosmetics": ["Soap", "Shampoo", "Face Cream", "Lotion", "Perfume"],
            "Grocery": ["Rice", "Flour", "Sugar", "Salt", "Oil"],
            "Drinks": ["Water", "Soda", "Juice", "Coffee", "Tea"]
        }
        
        # Generate 30 days of sample data
        for i in range(30):
            date = (datetime.now() - timedelta(days=30-i)).strftime("%Y-%m-%d %H:%M:%S")
            bill_number = f"BILL-{date[:8]}-{1000+i}"
            
            # Random number of items (1-5)
            num_items = np.random.randint(1, 6)
            items = []
            subtotal = 0
            
            for _ in range(num_items):
                category = np.random.choice(categories)
                item_name = np.random.choice(products[category])
                quantity = np.random.randint(1, 4)
                price = np.random.uniform(5, 50)
                total = quantity * price
                subtotal += total
                
                items.append({
                    "category": category,
                    "item_name": item_name,
                    "quantity": quantity,
                    "price": price,
                    "total": total
                })
            
            tax = subtotal * 0.05
            total = subtotal + tax
            
            sample_data.append({
                "bill_number": bill_number,
                "customer_name": f"Customer {i+1}",
                "phone_number": f"555-{1000+i}",
                "date": date,
                "items": items,
                "subtotal": subtotal,
                "tax": tax,
                "total": total,
                "timestamp": date
            })
        
        sales_df = pd.DataFrame(sample_data)
    
    # Ensure date column is datetime
    if 'date' in sales_df.columns:
        sales_df['date'] = pd.to_datetime(sales_df['date'])
    
    return sales_df

sales_df = load_sales_data()

# Date filter
st.sidebar.header("Filter Data")
if 'date' in sales_df.columns and not sales_df.empty:
    min_date = sales_df['date'].min().date()
    max_date = sales_df['date'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    
    # Filter data by date
    filtered_df = sales_df[(sales_df['date'].dt.date >= start_date) & 
                           (sales_df['date'].dt.date <= end_date)]
elif sales_df.empty:
    st.warning("No sales data available. Please create some bills first.")
    # Create empty filtered_df to avoid errors
    filtered_df = sales_df.copy()
else:
    st.error("Date column not found in sales data.")
    st.stop()

# Display key metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = len(filtered_df)
    st.metric("Total Sales", total_sales)

with col2:
    total_revenue = filtered_df['total'].sum()
    st.metric("Total Revenue", f"${total_revenue:.2f}")

with col3:
    avg_sale = total_revenue / total_sales if total_sales > 0 else 0
    st.metric("Average Sale", f"${avg_sale:.2f}")

with col4:
    unique_customers = filtered_df['customer_name'].nunique()
    st.metric("Unique Customers", unique_customers)

# Sales over time
st.header("Sales Over Time")

# Group by date
daily_sales = filtered_df.groupby(filtered_df['date'].dt.date).agg({
    'total': 'sum',
    'bill_number': 'count'
}).reset_index()
daily_sales.columns = ['date', 'revenue', 'sales_count']

# Plot
fig = px.line(daily_sales, x='date', y=['revenue', 'sales_count'], 
              title='Daily Sales and Revenue',
              labels={'value': 'Amount', 'date': 'Date', 'variable': 'Metric'},
              color_discrete_sequence=['#1f77b4', '#ff7f0e'])

st.plotly_chart(fig, use_container_width=True)

# Sales by category
st.header("Sales by Category")

# Extract items from nested structure
all_items = []
for _, row in filtered_df.iterrows():
    if 'items' in row and isinstance(row['items'], list):
        for item in row['items']:
            if isinstance(item, dict) and 'category' in item:
                item_data = {
                    'date': row['date'],
                    'bill_number': row['bill_number'],
                    'category': item['category'],
                    'item_name': item.get('item_name', 'Unknown'),
                    'quantity': item.get('quantity', 0),
                    'price': item.get('price', 0),
                    'total': item.get('total', 0)
                }
                all_items.append(item_data)

if all_items:
    items_df = pd.DataFrame(all_items)
    
    # Category breakdown
    category_sales = items_df.groupby('category').agg({
        'total': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(category_sales, values='total', names='category', 
                    title='Revenue by Category',
                    hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(category_sales, x='category', y='total',
                    title='Revenue by Category',
                    labels={'total': 'Revenue', 'category': 'Category'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Top selling products
    st.header("Top Selling Products")
    product_sales = items_df.groupby('item_name').agg({
        'total': 'sum',
        'quantity': 'sum'
    }).reset_index().sort_values('total', ascending=False).head(10)
    
    fig = px.bar(product_sales, x='item_name', y='total',
                title='Top 10 Products by Revenue',
                labels={'total': 'Revenue', 'item_name': 'Product'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Sales by day of week
    st.header("Sales by Day of Week")
    items_df['day_of_week'] = items_df['date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    day_sales = items_df.groupby('day_of_week').agg({
        'total': 'sum'
    }).reset_index()
    
    # Reorder days
    day_sales['day_of_week'] = pd.Categorical(day_sales['day_of_week'], categories=day_order, ordered=True)
    day_sales = day_sales.sort_values('day_of_week')
    
    fig = px.bar(day_sales, x='day_of_week', y='total',
                title='Sales by Day of Week',
                labels={'total': 'Revenue', 'day_of_week': 'Day'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No detailed item data available in the sales records.")

# Sales forecast
st.header("Sales Forecast")

if len(daily_sales) > 5:  # Need enough data for forecasting
    # Prepare data for forecasting
    daily_sales['day_number'] = range(len(daily_sales))
    
    # Train model
    X = daily_sales[['day_number']]
    y = daily_sales['revenue']
    model = LinearRegression()
    model.fit(X, y)
    
    # Forecast next 7 days
    last_day = daily_sales['day_number'].max()
    future_days = pd.DataFrame({'day_number': range(last_day + 1, last_day + 8)})
    future_days['revenue'] = model.predict(future_days[['day_number']])
    
    # Create dates for future days
    last_date = daily_sales['date'].max()
    future_days['date'] = [last_date + timedelta(days=i+1) for i in range(len(future_days))]
    
    # Combine actual and forecast
    forecast_df = pd.concat([
        daily_sales[['date', 'revenue']].assign(type='Actual'),
        future_days[['date', 'revenue']].assign(type='Forecast')
    ])
    
    # Plot
    fig = px.line(forecast_df, x='date', y='revenue', color='type',
                 title='Sales Forecast (Next 7 Days)',
                 labels={'revenue': 'Revenue', 'date': 'Date'},
                 color_discrete_sequence=['#1f77b4', '#ff7f0e'])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display forecast table
    st.subheader("Forecast Values")
    st.dataframe(future_days[['date', 'revenue']].rename(
        columns={'date': 'Date', 'revenue': 'Forecasted Revenue'}
    ).style.format({'Forecasted Revenue': '${:.2f}'}))
    
    # Show model performance
    st.subheader("Model Performance")
    r2_score = model.score(X, y)
    st.write(f"R² Score: {r2_score:.4f}")
    
    # Coefficient interpretation
    slope = model.coef_[0]
    trend = "upward" if slope > 0 else "downward"
    st.write(f"Sales are showing a {trend} trend of ${abs(slope):.2f} per day.")
else:
    st.info("Not enough data for forecasting. Need at least 5 days of sales data.")

# Add download button for analytics data
st.sidebar.header("Export Data")
if st.sidebar.button("Export Analytics to Excel"):
    try:
        # Create Excel file
        excel_path = os.path.join(temp_dir, f"sales_analytics_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Write different sheets
            filtered_df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            if not daily_sales.empty:
                daily_sales.to_excel(writer, sheet_name='Daily Sales', index=False)
            
            # Fix for item details sheets
            if all_items:
                # Make sure items_df exists and is not empty
                if 'items_df' in locals() and not items_df.empty:
                    items_df.to_excel(writer, sheet_name='Item Details', index=False)
                
                # Make sure category_sales exists and is not empty
                if 'category_sales' in locals() and not category_sales.empty:
                    category_sales.to_excel(writer, sheet_name='Category Sales', index=False)
                
                # Make sure product_sales exists and is not empty
                if 'product_sales' in locals() and not product_sales.empty:
                    product_sales.to_excel(writer, sheet_name='Top Products', index=False)
            
            # Fix for forecast sheet
            if len(daily_sales) > 5 and 'future_days' in locals() and not future_days.empty:
                future_days.to_excel(writer, sheet_name='Forecast', index=False)
        
        # Create download link
        with open(excel_path, 'rb') as f:
            data = f.read()
        
        st.sidebar.download_button(
            label="Download Excel File",
            data=data,
            file_name=f"sales_analytics_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.sidebar.success("Excel file generated successfully!")
    except Exception as e:
        st.sidebar.error(f"Error generating Excel file: {str(e)}")

# Add refresh button
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Grocery Billing System - Analytics Dashboard")