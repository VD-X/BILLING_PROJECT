import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import io
from datetime import datetime, timedelta
import calendar
import numpy as np
from sklearn.linear_model import LinearRegression

# Set page config
st.set_page_config(
    page_title="Billing Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .dashboard-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 30px;
        color: #2c3e50;
        padding-bottom: 15px;
        border-bottom: 2px solid #3498db;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #2980b9;
    }
    .metric-label {
        font-size: 16px;
        color: #7f8c8d;
        margin-top: 5px;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .filter-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: black;  /* Changed from white to black for better visibility */
        font-weight: 500;  /* Added font weight for better readability */
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: black;  /* Changed from white to black for better visibility */
        font-weight: bold;  /* Make selected tab text bold */
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load data from the excel_bills.xlsx file"""
    excel_file = "d:\\adv billing\\main excel bill\\excel_bills.xlsx"
    
    if not os.path.exists(excel_file):
        st.error("Excel file not found. Please generate some bills first.")
        return None
    
    try:
        df = pd.read_excel(excel_file)
        
        # Convert Date column to datetime if it's not already
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Extract date components for filtering
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.month
            df['Month_Name'] = df['Date'].dt.month_name()
            df['Day'] = df['Date'].dt.day
            df['Weekday'] = df['Date'].dt.day_name()
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def display_filters(df):
    """Display filter options and return the filtered dataframe"""
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    st.subheader("Filters")
    
    col1, col2, col3 = st.columns(3)
    
    # Date range filter
    with col1:
        if 'Date' in df.columns and not df.empty:
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    # Customer name filter
    with col2:
        if 'Customer Name' in df.columns and not df.empty:
            customer_names = ['All'] + sorted(df['Customer Name'].unique().tolist())
            selected_customer = st.selectbox("Select Customer", customer_names)
            
            if selected_customer != 'All':
                df = df[df['Customer Name'] == selected_customer]
    
    # Amount range filter
    with col3:
        if 'Total' in df.columns and not df.empty:
            min_amount = float(df['Total'].min())
            max_amount = float(df['Total'].max())
            
            # Fix for when min and max are the same (only one bill)
            if min_amount == max_amount:
                # Add a small buffer to max_amount to make the slider work
                max_amount += 1.0
            
            amount_range = st.slider(
                "Total Amount Range",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                step=10.0
            )
            
            df = df[(df['Total'] >= amount_range[0]) & (df['Total'] <= amount_range[1])]
    
    st.markdown("</div>", unsafe_allow_html=True)
    return df

def display_key_metrics(df):
    """Display key metrics at the top of the dashboard"""
    st.markdown("<div style='margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{len(df)}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Total Bills</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        total_revenue = df['Total'].sum()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>₹{total_revenue:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Total Revenue</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        avg_bill = df['Total'].mean()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>₹{avg_bill:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Average Bill Amount</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        unique_customers = df['Customer Name'].nunique()
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{unique_customers}</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Unique Customers</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_time_series_chart(df):
    """Create a time series chart of daily revenue"""
    if 'Date' not in df.columns or df.empty:
        return None
    
    # Group by date and sum the total
    daily_data = df.groupby(df['Date'].dt.date)['Total'].sum().reset_index()
    
    fig = px.line(
        daily_data, 
        x='Date', 
        y='Total',
        title='Daily Revenue',
        labels={'Total': 'Revenue (₹)', 'Date': 'Date'},
        template='plotly_white'
    )
    
    fig.update_traces(mode='lines+markers', line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        hovermode='x unified',
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        )
    )
    
    return fig

def create_monthly_bar_chart(df):
    """Create a bar chart of monthly revenue"""
    if 'Date' not in df.columns or df.empty:
        return None
    
    # Group by month and sum the total
    monthly_data = df.groupby(['Year', 'Month', 'Month_Name'])['Total'].sum().reset_index()
    monthly_data['Month_Year'] = monthly_data['Month_Name'] + ' ' + monthly_data['Year'].astype(str)
    
    # Sort by year and month
    monthly_data = monthly_data.sort_values(['Year', 'Month'])
    
    fig = px.bar(
        monthly_data,
        x='Month_Year',
        y='Total',
        title='Monthly Revenue',
        labels={'Total': 'Revenue (₹)', 'Month_Year': 'Month'},
        template='plotly_white',
        color='Total',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        )
    )
    
    return fig

def create_customer_pie_chart(df):
    """Create a pie chart of revenue by customer"""
    if 'Customer Name' not in df.columns or df.empty:
        return None
    
    # Group by customer and sum the total
    customer_data = df.groupby('Customer Name')['Total'].sum().reset_index()
    
    # Sort by total in descending order
    customer_data = customer_data.sort_values('Total', ascending=False)
    
    # If there are too many customers, keep only top 10 and group others
    if len(customer_data) > 10:
        top_customers = customer_data.head(10)
        others_total = customer_data.iloc[10:]['Total'].sum()
        others_row = pd.DataFrame({'Customer Name': ['Others'], 'Total': [others_total]})
        customer_data = pd.concat([top_customers, others_row], ignore_index=True)
    
    fig = px.pie(
        customer_data,
        values='Total',
        names='Customer Name',
        title='Revenue by Customer',
        template='plotly_white',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_weekday_bar_chart(df):
    """Create a bar chart of revenue by day of week"""
    if 'Weekday' not in df.columns or df.empty:
        return None
    
    # Group by weekday and sum the total
    weekday_data = df.groupby('Weekday')['Total'].sum().reset_index()
    
    # Define weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create a categorical type with the weekday order
    weekday_data['Weekday'] = pd.Categorical(weekday_data['Weekday'], categories=weekday_order, ordered=True)
    
    # Sort by the categorical weekday
    weekday_data = weekday_data.sort_values('Weekday')
    
    fig = px.bar(
        weekday_data,
        x='Weekday',
        y='Total',
        title='Revenue by Day of Week',
        labels={'Total': 'Revenue (₹)', 'Weekday': 'Day of Week'},
        template='plotly_white',
        color='Total',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        )
    )
    
    return fig

def display_data_table(df):
    """Display the data table with sorting and filtering options"""
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Bill Records")
    
    # Select columns to display
    display_cols = ['Bill Number', 'Date', 'Customer Name', 'Phone Number', 'Subtotal', 'Tax', 'Total']
    display_df = df[display_cols] if all(col in df.columns for col in display_cols) else df
    
    # Add search functionality
    search_term = st.text_input("Search by Bill Number or Customer Name", "")
    
    if search_term:
        display_df = display_df[
            display_df['Bill Number'].astype(str).str.contains(search_term, case=False) |
            display_df['Customer Name'].astype(str).str.contains(search_term, case=False)
        ]
    
    # Display the table
    st.dataframe(
        display_df.style.format({
            'Subtotal': '₹{:.2f}',
            'Tax': '₹{:.2f}',
            'Total': '₹{:.2f}'
        }),
        use_container_width=True,
        height=400
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    # Dashboard title
    st.markdown("<h1 class='dashboard-title'>Billing Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df is not None and not df.empty:
        # Apply filters
        filtered_df = display_filters(df)
        
        # Display key metrics
        display_key_metrics(filtered_df)
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Revenue Analysis", 
            "Customer Analysis", 
            "Time Patterns",
            "Product & Advanced Analytics",
            "Data Table"
        ])
        
        with tab1:
            # Revenue trend chart with moving average
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            revenue_trend_fig = create_revenue_trend_chart(filtered_df)
            if revenue_trend_fig:
                st.plotly_chart(revenue_trend_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Monthly bar chart and weekday bar chart in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                monthly_fig = create_monthly_bar_chart(filtered_df)
                if monthly_fig:
                    st.plotly_chart(monthly_fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                weekday_fig = create_weekday_bar_chart(filtered_df)
                if weekday_fig:
                    st.plotly_chart(weekday_fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            # Customer pie chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            customer_fig = create_customer_pie_chart(filtered_df)
            if customer_fig:
                st.plotly_chart(customer_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Customer growth chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            growth_fig = create_customer_growth_chart(filtered_df)
            if growth_fig:
                st.plotly_chart(growth_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Top customers table
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top Customers")
            
            if 'Customer Name' in filtered_df.columns and 'Total' in filtered_df.columns:
                top_customers = filtered_df.groupby('Customer Name')['Total'].agg(['sum', 'count']).reset_index()
                top_customers.columns = ['Customer Name', 'Total Revenue', 'Number of Bills']
                top_customers = top_customers.sort_values('Total Revenue', ascending=False).head(10)
                
                st.dataframe(
                    top_customers.style.format({
                        'Total Revenue': '₹{:.2f}'
                    }),
                    use_container_width=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            # Time series chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            time_series_fig = create_time_series_chart(filtered_df)
            if time_series_fig:
                st.plotly_chart(time_series_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Heatmap of sales by day and hour
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            heatmap_fig = create_heatmap(filtered_df)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab4:
            # Category breakdown chart
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            category_fig = create_item_category_chart(filtered_df)
            if category_fig:
                st.plotly_chart(category_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add a note about simulated data
            st.info("Note: Category breakdown is simulated based on bill amounts since detailed product data is not available in the main Excel file.")
            
            # Revenue Forecasting
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Revenue Forecasting")
            
            # Simple forecasting based on historical data
            if len(filtered_df) > 10:
                forecast_days = st.slider("Forecast Days", min_value=1, max_value=30, value=7)
                
                # Get daily revenue data
                daily_data = filtered_df.groupby(filtered_df['Date'].dt.date)['Total'].sum().reset_index()
                daily_data = daily_data.sort_values('Date')
                
                # Simple linear regression for forecasting
                X = np.array(range(len(daily_data))).reshape(-1, 1)
                y = daily_data['Total'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate forecast dates
                last_date = daily_data['Date'].max()
                forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
                
                # Generate predictions
                X_forecast = np.array(range(len(daily_data), len(daily_data) + forecast_days)).reshape(-1, 1)
                y_forecast = model.predict(X_forecast)
                
                # Create forecast DataFrame
                forecast_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Forecasted Revenue': y_forecast
                })
                
                # Combine historical and forecast data
                historical_df = pd.DataFrame({
                    'Date': daily_data['Date'],
                    'Historical Revenue': daily_data['Total']
                })
                
                # Create the chart
                fig = go.Figure()
                
                # Add historical data
                fig.add_trace(go.Scatter(
                    x=historical_df['Date'],
                    y=historical_df['Historical Revenue'],
                    mode='lines+markers',
                    name='Historical Revenue',
                    line=dict(color='#3498db', width=2),
                    marker=dict(size=6)
                ))
                
                # Add forecast data
                fig.add_trace(go.Scatter(
                    x=forecast_df['Date'],
                    y=forecast_df['Forecasted Revenue'],
                    mode='lines+markers',
                    name='Forecasted Revenue',
                    line=dict(color='#e74c3c', width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond')
                ))
                
                fig.update_layout(
                    title='Revenue Forecast',
                    title_font_size=20,
                    title_font_family='Arial',
                    title_x=0.5,
                    height=400,
                    hovermode='x unified',
                    xaxis=dict(
                        title='Date',
                        title_font=dict(size=14),
                        tickfont=dict(size=12),
                        gridcolor='rgba(211, 211, 211, 0.3)'
                    ),
                    yaxis=dict(
                        title='Revenue (₹)',
                        title_font=dict(size=14),
                        tickfont=dict(size=12),
                        gridcolor='rgba(211, 211, 211, 0.3)'
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display forecast summary
                st.subheader("Forecast Summary")
                col1, col2 = st.columns(2)
                
                with col1:
                    total_forecast = forecast_df['Forecasted Revenue'].sum()
                    st.metric(
                        label="Total Forecasted Revenue",
                        value=f"₹{total_forecast:.2f}",
                        delta=f"{(total_forecast - historical_df['Historical Revenue'].mean() * forecast_days):.2f}"
                    )
                
                with col2:
                    avg_forecast = forecast_df['Forecasted Revenue'].mean()
                    st.metric(
                        label="Avg. Daily Forecasted Revenue",
                        value=f"₹{avg_forecast:.2f}",
                        delta=f"{(avg_forecast - historical_df['Historical Revenue'].mean()):.2f}"
                    )
            else:
                st.info("Need more data points for forecasting. Please generate more bills or adjust filters.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add RFM Analysis (Recency, Frequency, Monetary)
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Customer RFM Analysis")
            
            if 'Customer Name' in filtered_df.columns and 'Date' in filtered_df.columns and not filtered_df.empty:
                # Calculate the most recent date in the data
                max_date = filtered_df['Date'].max()
                
                # Group by customer and calculate RFM metrics
                rfm_data = filtered_df.groupby('Customer Name').agg({
                    'Date': lambda x: (max_date - x.max()).days,  # Recency
                    'Bill Number': 'count',  # Frequency
                    'Total': 'sum'  # Monetary
                }).reset_index()
                
                # Rename columns
                rfm_data.columns = ['Customer Name', 'Recency (days)', 'Frequency (bills)', 'Monetary (₹)']
                
                # Sort by monetary value (descending)
                rfm_data = rfm_data.sort_values('Monetary (₹)', ascending=False)
                
                # Display the RFM table
                st.dataframe(
                    rfm_data.style.format({
                        'Monetary (₹)': '₹{:.2f}'
                    }),
                    use_container_width=True
                )
                
                # Create RFM scatter plot
                fig = px.scatter(
                    rfm_data,
                    x='Recency (days)',
                    y='Frequency (bills)',
                    size='Monetary (₹)',
                    color='Monetary (₹)',
                    hover_name='Customer Name',
                    title='RFM Customer Segmentation',
                    template='plotly_white',
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(
                    title_font_size=20,
                    title_font_family='Arial',
                    title_x=0.5,
                    height=500,
                    xaxis=dict(
                        title_font=dict(size=14),
                        tickfont=dict(size=12),
                        gridcolor='rgba(211, 211, 211, 0.3)'
                    ),
                    yaxis=dict(
                        title_font=dict(size=14),
                        tickfont=dict(size=12),
                        gridcolor='rgba(211, 211, 211, 0.3)'
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.info("""
                **RFM Analysis Explanation:**
                - **Recency**: Days since customer's last purchase (lower is better)
                - **Frequency**: Number of purchases (higher is better)
                - **Monetary**: Total spending (higher is better)
                
                Bubble size and color represent the monetary value. Ideal customers are in the bottom-right area (high frequency, low recency).
                """)
            else:
                st.info("Not enough customer data for RFM analysis. Please generate more bills with customer information.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab5:
            # Data table
            display_data_table(filtered_df)
            
            # Export functionality
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export to CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="billing_data.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Export to Excel"):
                    # Create a BytesIO object
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name='Billing Data')
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Download Excel",
                        data=excel_data,
                        file_name="billing_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No billing data available. Please generate some bills first.")
        
        # Display sample dashboard with dummy data
        st.markdown("### Sample Dashboard Preview")
        st.image("https://i.imgur.com/XqYBRDh.png", caption="Sample Analytics Dashboard")

def create_item_category_chart(df):
    """Create a chart showing revenue breakdown by item category"""
    if df.empty or 'Bill Number' not in df.columns:
        return None
    
    # Since we don't have direct category data in the main Excel file,
    # we'll create a simulated category breakdown based on bill amounts
    
    # Create simulated category data
    categories = ['Cosmetics', 'Grocery', 'Drinks']
    
    # Generate random but consistent proportions for each bill
    np.random.seed(42)  # For consistent results
    category_data = []
    
    for bill_num in df['Bill Number'].unique():
        bill_df = df[df['Bill Number'] == bill_num]
        total = bill_df['Total'].iloc[0]
        
        # Generate random proportions that sum to 1
        props = np.random.dirichlet(np.ones(len(categories)))
        
        for i, category in enumerate(categories):
            category_data.append({
                'Bill Number': bill_num,
                'Category': category,
                'Amount': total * props[i],
                'Date': bill_df['Date'].iloc[0]
            })
    
    category_df = pd.DataFrame(category_data)
    
    # Group by category and sum amounts
    category_summary = category_df.groupby('Category')['Amount'].sum().reset_index()
    
    # Create the chart
    fig = px.bar(
        category_summary,
        x='Category',
        y='Amount',
        title='Revenue by Product Category',
        labels={'Amount': 'Revenue (₹)', 'Category': 'Product Category'},
        template='plotly_white',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        )
    )
    
    return fig

def create_heatmap(df):
    """Create a heatmap showing sales patterns by day of week and hour"""
    if 'Date' not in df.columns or df.empty:
        return None
    
    # Extract hour from datetime
    df['Hour'] = df['Date'].dt.hour
    
    # Create a pivot table for the heatmap
    heatmap_data = df.pivot_table(
        index='Weekday', 
        columns='Hour', 
        values='Total', 
        aggfunc='sum',
        fill_value=0
    )
    
    # Reindex to ensure all days of the week are in correct order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(weekday_order)
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        colorbar=dict(title='Revenue (₹)')
    ))
    
    fig.update_layout(
        title='Revenue Heatmap by Day and Hour',
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        xaxis=dict(
            title='Hour of Day',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title='Day of Week',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        )
    )
    
    return fig

def create_revenue_trend_chart(df):
    """Create a trend chart with moving average"""
    if 'Date' not in df.columns or df.empty:
        return None
    
    # Group by date and sum the total
    daily_data = df.groupby(df['Date'].dt.date)['Total'].sum().reset_index()
    
    # Sort by date
    daily_data = daily_data.sort_values('Date')
    
    # Calculate 7-day moving average if we have enough data
    if len(daily_data) >= 7:
        daily_data['7-Day MA'] = daily_data['Total'].rolling(window=7).mean()
    
    # Create figure
    fig = go.Figure()
    
    # Add daily revenue line
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Total'],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color='#3498db', width=2),
        marker=dict(size=6)
    ))
    
    # Add moving average line if available
    if '7-Day MA' in daily_data.columns:
        fig.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['7-Day MA'],
            mode='lines',
            name='7-Day Moving Average',
            line=dict(color='#e74c3c', width=3, dash='dash')
        ))
    
    fig.update_layout(
        title='Revenue Trend with Moving Average',
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        hovermode='x unified',
        xaxis=dict(
            title='Date',
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title='Revenue (₹)',
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_customer_growth_chart(df):
    """Create a chart showing cumulative customer growth over time"""
    if 'Date' not in df.columns or 'Customer Name' not in df.columns or df.empty:
        return None
    
    # Sort by date
    df_sorted = df.sort_values('Date')
    
    # Track unique customers over time
    unique_customers = set()
    customer_growth = []
    
    for date, customer in zip(df_sorted['Date'].dt.date, df_sorted['Customer Name']):
        unique_customers.add(customer)
        customer_growth.append({
            'Date': date,
            'Unique Customers': len(unique_customers)
        })
    
    # Convert to DataFrame and remove duplicates (keep the latest count for each date)
    growth_df = pd.DataFrame(customer_growth)
    growth_df = growth_df.drop_duplicates(subset=['Date'], keep='last')
    
    # Create the chart
    fig = px.line(
        growth_df,
        x='Date',
        y='Unique Customers',
        title='Cumulative Customer Growth',
        labels={'Unique Customers': 'Total Unique Customers', 'Date': 'Date'},
        template='plotly_white'
    )
    
    fig.update_traces(mode='lines+markers', line=dict(width=3, color='#27ae60'), marker=dict(size=8))
    fig.update_layout(
        title_font_size=20,
        title_font_family='Arial',
        title_x=0.5,
        height=400,
        hovermode='x unified',
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(211, 211, 211, 0.3)'
        )
    )
    
    return fig

if __name__ == "__main__":
    main()