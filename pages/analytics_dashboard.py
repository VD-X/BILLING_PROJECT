import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import tempfile
import re
from collections import Counter

# Set page config
st.set_page_config(
    page_title="Billing Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Add auto-refresh functionality
st.cache_data.clear()
st.cache_resource.clear()

# Add refresh button and auto-refresh interval
refresh_col1, refresh_col2 = st.columns([1, 5])
with refresh_col1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
with refresh_col2:
    auto_refresh = st.selectbox(
        "Auto-refresh interval",
        ["Off", "30 seconds", "1 minute", "5 minutes"],
        index=0
    )

if auto_refresh != "Off":
    intervals = {
        "30 seconds": 30,
        "1 minute": 60,
        "5 minutes": 300
    }
    st.query_params["refresh_interval"] = intervals[auto_refresh]
    st.rerun()

st.title("Real-time Billing Analytics Dashboard")

# Function to load billing data
@st.cache_data(ttl=30)  # Cache data for 30 seconds
def load_billing_data():
    try:
        # Use vdx_excel_bills.xlsx for real-time analytics
        vdx_excel = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vdx_excel_bills.xlsx")
        
        if not os.path.exists(vdx_excel):
            st.error("vdx_excel_bills.xlsx not found. Please ensure the file exists in the project directory.")
            return None
        
        try:
            # Read the Excel file with purchase time information
            df = pd.read_excel(vdx_excel)
            
            # Convert the dataframe to the required format
            billing_df = pd.DataFrame({
                'Bill Number': df['Bill Number'],
                'Date': pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce'),
                'Customer Name': df['Customer Name'],
                'Phone Number': df['Phone Number'],
                'Subtotal': df['Subtotal'],
                'Tax': df['Tax'],
                'Total': df['Total']
            })
            
            # Try to extract product categories from bill data if available
            try:
                # Load bill text files to extract product information
                bills_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_bills")
                if os.path.exists(bills_folder):
                    # Create dictionaries to store product information by bill number
                    cosmetic_items_by_bill = {}
                    grocery_items_by_bill = {}
                    drink_items_by_bill = {}
                    
                    for txt_file in os.listdir(bills_folder):
                        if txt_file.endswith(".txt"):
                            bill_number = os.path.splitext(txt_file)[0]
                            file_path = os.path.join(bills_folder, txt_file)
                            
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Extract product categories
                                cosmetics_match = re.search(r'COSMETICS:(.*?)(?=GROCERY:|DRINKS:|Subtotal:|$)', content, re.DOTALL)
                                grocery_match = re.search(r'GROCERY:(.*?)(?=COSMETICS:|DRINKS:|Subtotal:|$)', content, re.DOTALL)
                                drinks_match = re.search(r'DRINKS:(.*?)(?=COSMETICS:|GROCERY:|Subtotal:|$)', content, re.DOTALL)
                                
                                cosmetic_items = []
                                grocery_items = []
                                drink_items = []
                                
                                if cosmetics_match:
                                    cosmetic_items = [item.strip() for item in cosmetics_match.group(1).strip().split('\n') if item.strip()]
                                if grocery_match:
                                    grocery_items = [item.strip() for item in grocery_match.group(1).strip().split('\n') if item.strip()]
                                if drinks_match:
                                    drink_items = [item.strip() for item in drinks_match.group(1).strip().split('\n') if item.strip()]
                                
                                cosmetic_items_by_bill[bill_number] = cosmetic_items
                                grocery_items_by_bill[bill_number] = grocery_items
                                drink_items_by_bill[bill_number] = drink_items
                    
                    # Add product category columns to the dataframe
                    billing_df['Cosmetic Items'] = billing_df['Bill Number'].map(lambda x: cosmetic_items_by_bill.get(str(x), []))
                    billing_df['Grocery Items'] = billing_df['Bill Number'].map(lambda x: grocery_items_by_bill.get(str(x), []))
                    billing_df['Drink Items'] = billing_df['Bill Number'].map(lambda x: drink_items_by_bill.get(str(x), []))
                    
                    # Add category counts
                    billing_df['Cosmetic Count'] = billing_df['Cosmetic Items'].apply(len)
                    billing_df['Grocery Count'] = billing_df['Grocery Items'].apply(len)
                    billing_df['Drink Count'] = billing_df['Drink Items'].apply(len)
                    billing_df['Total Items'] = billing_df['Cosmetic Count'] + billing_df['Grocery Count'] + billing_df['Drink Count']
            except Exception as e:
                st.warning(f"Could not extract product information from bills: {str(e)}")
                # Add empty product columns
                billing_df['Cosmetic Items'] = [[] for _ in range(len(billing_df))]
                billing_df['Grocery Items'] = [[] for _ in range(len(billing_df))]
                billing_df['Drink Items'] = [[] for _ in range(len(billing_df))]
                billing_df['Cosmetic Count'] = 0
                billing_df['Grocery Count'] = 0
                billing_df['Drink Count'] = 0
                billing_df['Total Items'] = 0
            
            return billing_df
            
        except Exception as e:
            st.error(f"Error reading vdx_excel_bills.xlsx: {str(e)}")
            return None
        
    except Exception as e:
        st.error(f"Error loading billing data: {str(e)}")
        return None

# Load the billing data
billing_data = load_billing_data()

if billing_data is None:
    st.warning("No billing data found. Please generate some bills first.")
    st.info("The dashboard will automatically update when new bills are generated.")
else:
    # Overview Statistics Section
    st.subheader("📊 Overview Statistics")
    overview_tabs = st.tabs(["Key Metrics", "Growth Analysis"])
    
    with overview_tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        total_bills = len(billing_data)
        total_revenue = billing_data['Total'].sum()
        avg_bill = billing_data['Total'].mean()
        total_tax = billing_data['Tax'].sum()
        
        with col1:
            st.metric("Total Bills", f"{total_bills:,d}")
        with col2:
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        with col3:
            st.metric("Average Bill", f"₹{avg_bill:,.2f}")
        with col4:
            st.metric("Total Tax", f"₹{total_tax:,.2f}")
    
    with overview_tabs[1]:
        # Calculate day-over-day growth
        daily_revenue = billing_data.groupby(billing_data['Date'].dt.date)['Total'].sum()
        daily_growth = daily_revenue.pct_change() * 100
        avg_growth = daily_growth.mean()
        
        growth_col1, growth_col2 = st.columns(2)
        with growth_col1:
            st.metric("Average Daily Growth", f"{avg_growth:.1f}%")
        with growth_col2:
            last_day_growth = daily_growth.iloc[-1] if len(daily_growth) > 0 else 0
            st.metric("Last Day Growth", f"{last_day_growth:.1f}%")
    
    # Time Analysis Section
    st.subheader("📅 Time Analysis")
    time_tabs = st.tabs(["Daily Trends", "Hourly Analysis", "Monthly Overview"])
    
    with time_tabs[0]:
        # Enhanced daily trend with moving average
        daily_data = billing_data.groupby(billing_data['Date'].dt.date).agg({
            'Total': 'sum',
            'Bill Number': 'count'
        }).reset_index()
        daily_data['MA7'] = daily_data['Total'].rolling(window=7).mean()
        
        fig_daily = px.line(daily_data, x='Date', y=['Total', 'MA7'],
                           title='Daily Revenue with 7-day Moving Average',
                           labels={'value': 'Revenue (₹)', 'Date': 'Date', 'variable': 'Metric'},
                           color_discrete_map={'Total': 'blue', 'MA7': 'red'})
        fig_daily.update_layout(legend_title_text='', 
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with time_tabs[1]:
        # Hourly analysis
        billing_data['Hour'] = billing_data['Date'].dt.hour
        hourly_data = billing_data.groupby('Hour').agg({
            'Total': 'sum',
            'Bill Number': 'count'
        }).reset_index()
        
        fig_hourly = px.bar(hourly_data, x='Hour', y=['Total', 'Bill Number'],
                            title='Hourly Distribution',
                            barmode='group',
                            labels={'Hour': 'Hour of Day', 'value': 'Count/Revenue', 'variable': 'Metric'})
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with time_tabs[2]:
        # Enhanced monthly analysis
        billing_data['Month'] = billing_data['Date'].dt.strftime('%B %Y')
        monthly_stats = billing_data.groupby('Month').agg({
            'Total': ['sum', 'mean', 'count', 'std'],
            'Tax': 'sum'
        }).round(2)
        monthly_stats.columns = ['Total Revenue', 'Avg Bill', 'Number of Bills', 'Std Dev', 'Total Tax']
        monthly_stats = monthly_stats.reset_index()
        
        st.dataframe(
            monthly_stats.style.format({
                'Total Revenue': '₹{:,.2f}',
                'Avg Bill': '₹{:,.2f}',
                'Std Dev': '₹{:,.2f}',
                'Total Tax': '₹{:,.2f}'
            }),
            use_container_width=True
        )
    
    # Customer Analysis Section
    st.subheader("👥 Customer Insights")
    customer_tabs = st.tabs(["Top Customers", "Customer Distribution", "Purchase History", "Category Preferences", "RFM Analysis", "Customer Retention"])
    
    with customer_tabs[0]:
        # Top customers by total spending
        top_customers = billing_data.groupby('Customer Name').agg({
            'Total': 'sum',
            'Bill Number': 'count'
        }).reset_index()
        top_customers.columns = ['Customer Name', 'Total Spending', 'Number of Visits']
        top_customers = top_customers.sort_values('Total Spending', ascending=False).head(10)
        
        fig_top_customers = px.bar(top_customers,
                                   x='Customer Name',
                                   y='Total Spending',
                                   title='Top 10 Customers by Spending',
                                   labels={'Total Spending': 'Total Spending (₹)'})
        st.plotly_chart(fig_top_customers, use_container_width=True)
    
    with customer_tabs[1]:
        # Customer spending distribution
        fig_dist = px.histogram(billing_data,
                               x='Total',
                               title='Distribution of Bill Amounts',
                               labels={'Total': 'Bill Amount (₹)', 'count': 'Number of Bills'})
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with customer_tabs[2]:
        # Customer Purchase History Analysis
        st.subheader("Customer Purchase History")
        
        # Customer selector
        # Convert customer names to strings to avoid type comparison issues
        customers = sorted([str(name) for name in billing_data['Customer Name'].unique() if name is not None and not pd.isna(name)])
        if customers:
            selected_customer = st.selectbox("Select Customer", customers)
            
            # Filter data for selected customer
            customer_data = billing_data[billing_data['Customer Name'] == selected_customer]
            
            if not customer_data.empty:
                # Show customer metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Visits", f"{len(customer_data)}")
                with col2:
                    st.metric("Total Spent", f"₹{customer_data['Total'].sum():,.2f}")
                with col3:
                    st.metric("Avg. Bill Amount", f"₹{customer_data['Total'].mean():,.2f}")
                with col4:
                    days_since_last = (datetime.now() - customer_data['Date'].max()).days
                    st.metric("Last Visit", f"{days_since_last} days ago")
                
                # Purchase timeline
                st.subheader("Purchase Timeline")
                purchase_history = customer_data.sort_values('Date')
                fig = px.line(purchase_history, 
                              x='Date', 
                              y='Total',
                              markers=True,
                              title=f"Purchase History for {selected_customer}",
                              labels={'Total': 'Bill Amount (₹)', 'Date': 'Purchase Date'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Purchase details table
                st.subheader("Purchase Details")
                purchase_details = purchase_history[['Date', 'Bill Number', 'Total', 'Total Items']]
                purchase_details = purchase_details.sort_values('Date', ascending=False)
                purchase_details.columns = ['Purchase Date', 'Bill Number', 'Amount (₹)', 'Items Purchased']
                st.dataframe(purchase_details, use_container_width=True)
            else:
                st.info("No purchase data available for this customer.")
        else:
            st.info("No customer data available.")
    
    with customer_tabs[3]:
        # Product Category Preferences by Customer
        st.subheader("Category Preferences Analysis")
        
        # Check if we have category data
        if 'Cosmetic Count' in billing_data.columns:
            # Customer selector
            # Convert customer names to strings to avoid type comparison issues
            customers = sorted([str(name) for name in billing_data['Customer Name'].unique() if name is not None and not pd.isna(name)])
            if customers:
                selected_customer = st.selectbox("Select Customer", customers, key="cat_pref_customer")
                
                # Filter data for selected customer
                customer_data = billing_data[billing_data['Customer Name'] == selected_customer]
                
                if not customer_data.empty:
                    # Calculate category totals
                    cosmetic_total = customer_data['Cosmetic Count'].sum()
                    grocery_total = customer_data['Grocery Count'].sum()
                    drink_total = customer_data['Drink Count'].sum()
                    
                    # Create category preference pie chart
                    category_data = pd.DataFrame({
                        'Category': ['Cosmetics', 'Grocery', 'Drinks'],
                        'Count': [cosmetic_total, grocery_total, drink_total]
                    })
                    
                    fig = px.pie(category_data, 
                                values='Count', 
                                names='Category',
                                title=f"Category Preferences for {selected_customer}",
                                color_discrete_sequence=px.colors.sequential.Viridis)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show most frequently purchased items if available
                    st.subheader("Most Frequently Purchased Items")
                    
                    # Combine all items from all bills
                    all_cosmetic_items = []
                    all_grocery_items = []
                    all_drink_items = []
                    
                    for items in customer_data['Cosmetic Items']:
                        all_cosmetic_items.extend(items)
                    for items in customer_data['Grocery Items']:
                        all_grocery_items.extend(items)
                    for items in customer_data['Drink Items']:
                        all_drink_items.extend(items)
                    
                    # Count item frequencies
                    cosmetic_counts = pd.Series(all_cosmetic_items).value_counts().reset_index()
                    grocery_counts = pd.Series(all_grocery_items).value_counts().reset_index()
                    drink_counts = pd.Series(all_drink_items).value_counts().reset_index()
                    
                    # Display top items in each category
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("Top Cosmetic Items")
                        if not cosmetic_counts.empty:
                            cosmetic_counts.columns = ['Item', 'Count']
                            st.dataframe(cosmetic_counts.head(5), use_container_width=True)
                        else:
                            st.info("No cosmetic items purchased")
                    
                    with col2:
                        st.write("Top Grocery Items")
                        if not grocery_counts.empty:
                            grocery_counts.columns = ['Item', 'Count']
                            st.dataframe(grocery_counts.head(5), use_container_width=True)
                        else:
                            st.info("No grocery items purchased")
                    
                    with col3:
                        st.write("Top Drink Items")
                        if not drink_counts.empty:
                            drink_counts.columns = ['Item', 'Count']
                            st.dataframe(drink_counts.head(5), use_container_width=True)
                        else:
                            st.info("No drink items purchased")
                else:
                    st.info("No purchase data available for this customer.")
            else:
                st.info("No customer data available.")
        else:
            st.info("Category data not available. Please ensure bills contain product information.")
    
    with customer_tabs[4]:
        # RFM (Recency, Frequency, Monetary) Analysis
        st.subheader("RFM Customer Segmentation")
        
        # Calculate RFM metrics
        if len(billing_data) > 0:
            # Get the most recent date in the dataset
            max_date = billing_data['Date'].max()
            
            # Group by customer and calculate RFM metrics
            rfm = billing_data.groupby('Customer Name').agg({
                'Date': lambda x: (max_date - x.max()).days,  # Recency
                'Bill Number': 'count',  # Frequency
                'Total': 'sum'  # Monetary
            }).reset_index()
            
            # Rename columns
            rfm.columns = ['Customer Name', 'Recency', 'Frequency', 'Monetary']
            
            # Create RFM scores (1-5, 5 being the best)
            # Handle potential duplicate values by using rank for all metrics
            try:
                # Try standard quantile cut first
                rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
            except ValueError:
                # If we get duplicate values error, use rank method
                rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1])
                
            # Always use rank method for frequency and monetary to be safe
            rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
            rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
            
            # Calculate RFM Score
            rfm['RFM_Score'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
            
            # Create customer segments
            def segment_customer(score):
                if score >= 13:
                    return 'Champions'
                elif score >= 10:
                    return 'Loyal Customers'
                elif score >= 7:
                    return 'Potential Loyalists'
                elif score >= 5:
                    return 'At Risk'
                else:
                    return 'Needs Attention'
            
            rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)
            
            # Display RFM segments
            segment_counts = rfm['Segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig = px.pie(segment_counts, 
                        values='Count', 
                        names='Segment',
                        title='Customer Segments Distribution',
                        color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display RFM metrics by segment
            segment_metrics = rfm.groupby('Segment').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean',
                'Customer Name': 'count'
            }).reset_index()
            
            segment_metrics.columns = ['Segment', 'Avg. Days Since Last Purchase', 'Avg. Purchase Frequency', 'Avg. Spending (₹)', 'Customer Count']
            segment_metrics = segment_metrics.sort_values('Customer Count', ascending=False)
            
            st.dataframe(segment_metrics.style.format({
                'Avg. Days Since Last Purchase': '{:.1f}',
                'Avg. Purchase Frequency': '{:.1f}',
                'Avg. Spending (₹)': '₹{:,.2f}'
            }), use_container_width=True)
            
            # Show customer details by segment
            selected_segment = st.selectbox("Select Segment to View Customers", rfm['Segment'].unique())
            segment_customers = rfm[rfm['Segment'] == selected_segment].sort_values('RFM_Score', ascending=False)
            
            st.dataframe(segment_customers[['Customer Name', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']].style.format({
                'Recency': '{:.0f} days',
                'Monetary': '₹{:,.2f}'
            }), use_container_width=True)
            
            # Recommendations based on segments
            st.subheader("Recommended Actions")
            
            recommendations = {
                'Champions': "These are your best customers! Reward them with loyalty programs, exclusive offers, and premium services.",
                'Loyal Customers': "Focus on maintaining their loyalty with personalized offers and regular communication.",
                'Potential Loyalists': "Encourage more frequent purchases with targeted promotions and incentives.",
                'At Risk': "Re-engage these customers with special offers, discounts, or personalized outreach.",
                'Needs Attention': "Consider recovery campaigns with significant incentives to bring these customers back."
            }
            
            st.info(recommendations.get(selected_segment, "No specific recommendations available."))
        else:
            st.info("Not enough data for RFM analysis. Please generate more bills.")
    
    with customer_tabs[5]:
        # Customer Retention Analysis
        st.subheader("Customer Retention Analysis")
        
        if len(billing_data) > 0:
            # Calculate first and last purchase dates for each customer
            customer_activity = billing_data.groupby('Customer Name').agg({
                'Date': ['min', 'max', 'count']
            }).reset_index()
            
            customer_activity.columns = ['Customer Name', 'First Purchase', 'Last Purchase', 'Purchase Count']
            
            # Calculate customer lifetime in days
            customer_activity['Customer Lifetime (days)'] = (customer_activity['Last Purchase'] - customer_activity['First Purchase']).dt.days
            
            # Calculate days since last purchase
            today = datetime.now()
            customer_activity['Days Since Last Purchase'] = (today - customer_activity['Last Purchase']).dt.days
            
            # Define active customers (purchased in last 30 days)
            customer_activity['Status'] = customer_activity['Days Since Last Purchase'].apply(
                lambda x: 'Active' if x <= 30 else ('Inactive' if x <= 90 else 'Churned')
            )
            
            # Customer status distribution
            status_counts = customer_activity['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(status_counts, 
                        values='Count', 
                        names='Status',
                        title='Customer Status Distribution',
                        color_discrete_map={'Active': 'green', 'Inactive': 'orange', 'Churned': 'red'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Customer retention over time
            billing_data['YearMonth'] = billing_data['Date'].dt.strftime('%Y-%m')
            monthly_active = billing_data.groupby('YearMonth')['Customer Name'].nunique().reset_index()
            monthly_active.columns = ['Month', 'Active Customers']
            
            fig = px.line(monthly_active, 
                         x='Month', 
                         y='Active Customers',
                         markers=True,
                         title='Monthly Active Customers',
                         labels={'Month': 'Month', 'Active Customers': 'Number of Active Customers'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Customer churn risk
            st.subheader("Customers at Risk of Churning")
            at_risk = customer_activity[
                (customer_activity['Status'] == 'Inactive') & 
                (customer_activity['Purchase Count'] > 1)
            ].sort_values('Days Since Last Purchase', ascending=False)
            
            if not at_risk.empty:
                at_risk_display = at_risk[['Customer Name', 'Last Purchase', 'Purchase Count', 'Days Since Last Purchase']]
                at_risk_display.columns = ['Customer Name', 'Last Purchase Date', 'Total Purchases', 'Days Since Last Purchase']
                
                st.dataframe(at_risk_display, use_container_width=True)
                
                # Recommended re-engagement strategy
                st.subheader("Re-engagement Recommendations")
                st.info("Consider sending personalized offers to these customers based on their previous purchase history. "
                       "A discount on their favorite product categories could encourage them to return.")
            else:
                st.info("No customers currently at risk of churning.")
        else:
            st.info("Not enough data for retention analysis. Please generate more bills.")
    
    # Product Analytics Section
    st.subheader("📦 Product Analytics")
    product_tabs = st.tabs(["Sales by Category", "Product Performance", "Cross-Category Insights", "Seasonal Trends"])
    
    with product_tabs[0]:
        # Sales by Category Analysis
        st.subheader("Sales by Category")
        
        if 'Cosmetic Count' in billing_data.columns and len(billing_data) > 0:
            # Calculate total sales and count by category
            category_data = pd.DataFrame({
                'Category': ['Cosmetics', 'Grocery', 'Drinks'],
                'Item Count': [billing_data['Cosmetic Count'].sum(), 
                               billing_data['Grocery Count'].sum(), 
                               billing_data['Drink Count'].sum()]
            })
            
            # Filter out categories with zero items
            category_data = category_data[category_data['Item Count'] > 0]
            
            if not category_data.empty:
                # Create a pie chart for category distribution
                fig = px.pie(category_data, 
                            values='Item Count', 
                            names='Category',
                            title='Sales Distribution by Category',
                            color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
                # Category sales over time
                billing_data['YearMonth'] = billing_data['Date'].dt.strftime('%Y-%m')
                monthly_category = billing_data.groupby('YearMonth').agg({
                    'Cosmetic Count': 'sum',
                    'Grocery Count': 'sum',
                    'Drink Count': 'sum'
                }).reset_index()
                
                # Reshape for plotting
                monthly_category_long = pd.melt(
                    monthly_category, 
                    id_vars=['YearMonth'],
                    value_vars=['Cosmetic Count', 'Grocery Count', 'Drink Count'],
                    var_name='Category', 
                    value_name='Count'
                )
                
                # Clean category names
                monthly_category_long['Category'] = monthly_category_long['Category'].str.replace(' Count', '')
                
                # Create line chart
                fig = px.line(monthly_category_long, 
                             x='YearMonth', 
                             y='Count',
                             color='Category',
                             markers=True,
                             title='Category Sales Trends Over Time',
                             labels={'YearMonth': 'Month', 'Count': 'Number of Items Sold'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available for analysis.")
        else:
            st.info("Category data not available. Please ensure bills contain product information.")
    
    with product_tabs[1]:
        # Product Performance Analysis
        st.subheader("Product Performance Analysis")
        
        if 'Cosmetic Items' in billing_data.columns and len(billing_data) > 0:
            # Collect all items across all bills
            all_cosmetic_items = []
            all_grocery_items = []
            all_drink_items = []
            
            for items in billing_data['Cosmetic Items']:
                if isinstance(items, list):
                    all_cosmetic_items.extend(items)
            
            for items in billing_data['Grocery Items']:
                if isinstance(items, list):
                    all_grocery_items.extend(items)
            
            for items in billing_data['Drink Items']:
                if isinstance(items, list):
                    all_drink_items.extend(items)
            
            # Count occurrences of each item
            cosmetic_counts = pd.DataFrame(Counter(all_cosmetic_items).most_common(), columns=['Item', 'Count'])
            grocery_counts = pd.DataFrame(Counter(all_grocery_items).most_common(), columns=['Item', 'Count'])
            drink_counts = pd.DataFrame(Counter(all_drink_items).most_common(), columns=['Item', 'Count'])
            
            # Combine all products for overall analysis
            all_products = []
            if not cosmetic_counts.empty:
                cosmetic_counts['Category'] = 'Cosmetics'
                all_products.append(cosmetic_counts)
            
            if not grocery_counts.empty:
                grocery_counts['Category'] = 'Grocery'
                all_products.append(grocery_counts)
            
            if not drink_counts.empty:
                drink_counts['Category'] = 'Drinks'
                all_products.append(drink_counts)
            
            if all_products:
                all_products_df = pd.concat(all_products, ignore_index=True)
                
                # Top 10 products overall
                top_products = all_products_df.sort_values('Count', ascending=False).head(10)
                
                fig = px.bar(top_products, 
                           x='Count', 
                           y='Item',
                           color='Category',
                           title='Top 10 Best-Selling Products',
                           labels={'Count': 'Number of Sales', 'Item': 'Product'},
                           orientation='h')
                st.plotly_chart(fig, use_container_width=True)
                
                # Allow filtering by category
                selected_category = st.selectbox(
                    "Select Category for Detailed Analysis",
                    ['All Categories'] + list(all_products_df['Category'].unique())
                )
                
                if selected_category == 'All Categories':
                    filtered_products = all_products_df
                else:
                    filtered_products = all_products_df[all_products_df['Category'] == selected_category]
                
                # Show detailed table
                st.subheader(f"Detailed Product Performance: {selected_category}")
                st.dataframe(filtered_products.sort_values('Count', ascending=False), use_container_width=True)
            else:
                st.info("No product data available for analysis.")
        else:
            st.info("Product data not available. Please ensure bills contain product information.")
    
    with product_tabs[2]:
        # Cross-Category Insights
        st.subheader("Cross-Category Purchase Insights")
        
        if 'Cosmetic Count' in billing_data.columns and len(billing_data) > 0:
            # Create category purchase indicators
            billing_data['Bought Cosmetics'] = billing_data['Cosmetic Count'] > 0
            billing_data['Bought Grocery'] = billing_data['Grocery Count'] > 0
            billing_data['Bought Drinks'] = billing_data['Drink Count'] > 0
            
            # Calculate co-occurrence of categories
            cosmetics_and_grocery = billing_data[(billing_data['Bought Cosmetics']) & (billing_data['Bought Grocery'])].shape[0]
            cosmetics_and_drinks = billing_data[(billing_data['Bought Cosmetics']) & (billing_data['Bought Drinks'])].shape[0]
            grocery_and_drinks = billing_data[(billing_data['Bought Grocery']) & (billing_data['Bought Drinks'])].shape[0]
            all_categories = billing_data[(billing_data['Bought Cosmetics']) & (billing_data['Bought Grocery']) & (billing_data['Bought Drinks'])].shape[0]
            
            # Calculate total bills with each category
            total_cosmetics = billing_data[billing_data['Bought Cosmetics']].shape[0]
            total_grocery = billing_data[billing_data['Bought Grocery']].shape[0]
            total_drinks = billing_data[billing_data['Bought Drinks']].shape[0]
            
            # Create co-occurrence matrix for heatmap
            categories = ['Cosmetics', 'Grocery', 'Drinks']
            co_occurrence = np.zeros((3, 3))
            
            # Fill the matrix
            co_occurrence[0, 0] = total_cosmetics
            co_occurrence[1, 1] = total_grocery
            co_occurrence[2, 2] = total_drinks
            co_occurrence[0, 1] = co_occurrence[1, 0] = cosmetics_and_grocery
            co_occurrence[0, 2] = co_occurrence[2, 0] = cosmetics_and_drinks
            co_occurrence[1, 2] = co_occurrence[2, 1] = grocery_and_drinks
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=co_occurrence,
                x=categories,
                y=categories,
                colorscale='Viridis',
                showscale=True
            ))
            
            fig.update_layout(
                title='Category Co-occurrence Matrix',
                xaxis_title='Category',
                yaxis_title='Category'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display cross-selling insights
            st.subheader("Cross-Selling Opportunities")
            
            insights = []
            if total_cosmetics > 0 and total_grocery > 0:
                cosmetics_to_grocery = cosmetics_and_grocery / total_cosmetics * 100
                grocery_to_cosmetics = cosmetics_and_grocery / total_grocery * 100
                insights.append(f"• {cosmetics_to_grocery:.1f}% of customers who buy Cosmetics also buy Grocery items")
                insights.append(f"• {grocery_to_cosmetics:.1f}% of customers who buy Grocery items also buy Cosmetics")
            
            if total_cosmetics > 0 and total_drinks > 0:
                cosmetics_to_drinks = cosmetics_and_drinks / total_cosmetics * 100
                drinks_to_cosmetics = cosmetics_and_drinks / total_drinks * 100
                insights.append(f"• {cosmetics_to_drinks:.1f}% of customers who buy Cosmetics also buy Drinks")
                insights.append(f"• {drinks_to_cosmetics:.1f}% of customers who buy Drinks also buy Cosmetics")
            
            if total_grocery > 0 and total_drinks > 0:
                grocery_to_drinks = grocery_and_drinks / total_grocery * 100
                drinks_to_grocery = grocery_and_drinks / total_drinks * 100
                insights.append(f"• {grocery_to_drinks:.1f}% of customers who buy Grocery items also buy Drinks")
                insights.append(f"• {drinks_to_grocery:.1f}% of customers who buy Drinks also buy Grocery items")
            
            if insights:
                for insight in insights:
                    st.write(insight)
                
                # Recommendations based on insights
                st.subheader("Recommendations")
                st.info("Consider these cross-selling strategies based on purchase patterns:\n" +
                       "1. Bundle frequently co-purchased items for special promotions\n" +
                       "2. Place related items from different categories near each other in store layout\n" +
                       "3. Offer targeted discounts on complementary products from different categories")
            else:
                st.info("Not enough cross-category purchase data for insights.")
        else:
            st.info("Category data not available. Please ensure bills contain product information.")
    
    with product_tabs[3]:
        # Seasonal Trends Analysis
        st.subheader("Seasonal Product Trends")
        
        if 'Cosmetic Count' in billing_data.columns and len(billing_data) > 0:
            # Add month and season columns
            billing_data['Month'] = billing_data['Date'].dt.month
            billing_data['Month Name'] = billing_data['Date'].dt.strftime('%B')
            
            # Define seasons based on month
            def get_season(month):
                if month in [12, 1, 2]:  # Winter
                    return 'Winter'
                elif month in [3, 4, 5]:  # Spring
                    return 'Spring'
                elif month in [6, 7, 8]:  # Summer
                    return 'Summer'
                else:  # Fall/Autumn
                    return 'Fall'
            
            billing_data['Season'] = billing_data['Month'].apply(get_season)
            
            # Seasonal category analysis
            seasonal_data = billing_data.groupby('Season').agg({
                'Cosmetic Count': 'sum',
                'Grocery Count': 'sum',
                'Drink Count': 'sum',
                'Bill Number': 'count'
            }).reset_index()
            
            # Order seasons correctly
            season_order = ['Winter', 'Spring', 'Summer', 'Fall']
            seasonal_data['Season'] = pd.Categorical(seasonal_data['Season'], categories=season_order, ordered=True)
            seasonal_data = seasonal_data.sort_values('Season')
            
            # Create seasonal category distribution chart
            seasonal_data_long = pd.melt(
                seasonal_data,
                id_vars=['Season', 'Bill Number'],
                value_vars=['Cosmetic Count', 'Grocery Count', 'Drink Count'],
                var_name='Category',
                value_name='Count'
            )
            
            # Clean category names
            seasonal_data_long['Category'] = seasonal_data_long['Category'].str.replace(' Count', '')
            
            fig = px.bar(seasonal_data_long,
                        x='Season',
                        y='Count',
                        color='Category',
                        title='Seasonal Category Sales',
                        barmode='group',
                        labels={'Count': 'Number of Items Sold', 'Season': 'Season'})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly trends
            monthly_data = billing_data.groupby(['Month', 'Month Name']).agg({
                'Cosmetic Count': 'sum',
                'Grocery Count': 'sum',
                'Drink Count': 'sum'
            }).reset_index()
            
            # Sort by month number
            monthly_data = monthly_data.sort_values('Month')
            
            # Create monthly category distribution chart
            monthly_data_long = pd.melt(
                monthly_data,
                id_vars=['Month', 'Month Name'],
                value_vars=['Cosmetic Count', 'Grocery Count', 'Drink Count'],
                var_name='Category',
                value_name='Count'
            )
            
            # Clean category names
            monthly_data_long['Category'] = monthly_data_long['Category'].str.replace(' Count', '')
            
            fig = px.line(monthly_data_long,
                         x='Month Name',
                         y='Count',
                         color='Category',
                         markers=True,
                         title='Monthly Category Sales Trends',
                         labels={'Count': 'Number of Items Sold', 'Month Name': 'Month'},
                         category_orders={'Month Name': list(calendar.month_name)[1:13]})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Seasonal product recommendations
            st.subheader("Seasonal Inventory Recommendations")
            
            # Get the current season
            current_month = datetime.now().month
            current_season = get_season(current_month)
            next_season_idx = (season_order.index(current_season) + 1) % 4
            next_season = season_order[next_season_idx]
            
            st.write(f"Current Season: **{current_season}**")
            st.write(f"Preparing for Next Season: **{next_season}**")
            
            # Recommendations based on seasonal data
            season_recommendations = {
                'Winter': "Focus on stocking more grocery essentials and hot beverages. Consider winter skincare cosmetics.",
                'Spring': "Increase inventory of fresh produce and cleaning supplies. Spring-themed cosmetics and refreshing drinks.",
                'Summer': "Stock up on cold beverages, summer fruits, and sun protection cosmetics.",
                'Fall': "Prepare for seasonal grocery items, warm drinks, and moisturizing cosmetics."
            }
            
            st.info(f"**Recommendation for {next_season}**: {season_recommendations.get(next_season, '')}")
        else:
            st.info("Category data not available for seasonal analysis. Please ensure bills contain product information.")
    
    # Predictive Analytics Section
    st.subheader("🔮 Revenue Prediction")
    if len(billing_data) >= 7:  # Only show prediction if we have enough data
        # Prepare data for prediction
        daily_data = billing_data.groupby(billing_data['Date'].dt.date)['Total'].sum().reset_index()
        daily_data['Day Number'] = range(len(daily_data))
        
        # Create and train the model
        model = LinearRegression()
        X = daily_data['Day Number'].values.reshape(-1, 1)
        y = daily_data['Total'].values
        model.fit(X, y)
        
        # Make prediction for next 7 days
        future_days = np.array(range(len(daily_data), len(daily_data) + 7)).reshape(-1, 1)
        predictions = model.predict(future_days)
        
        # Create prediction dataframe
        future_dates = [daily_data['Date'].iloc[-1] + timedelta(days=i+1) for i in range(7)]
        pred_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Revenue': predictions
        })
        
        st.write("Predicted Daily Revenue for Next 7 Days:")
        st.dataframe(pred_df.style.format({
            'Predicted Revenue': '₹{:,.2f}'
        }), use_container_width=True)
    else:
        st.info("Need at least 7 days of data for revenue prediction.")