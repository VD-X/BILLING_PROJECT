import os
import json
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample data for demonstration"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    bills_folder = os.path.join(base_path, "bills")
    excel_folder = os.path.join(base_path, "excel_bills")
    
    # Create directories
    os.makedirs(bills_folder, exist_ok=True)
    os.makedirs(excel_folder, exist_ok=True)
    
    # Generate sample data if folders are empty
    if not os.listdir(bills_folder) and not os.listdir(excel_folder):
        # Sample data generation logic
        categories = ['Cosmetics', 'Grocery', 'Drinks']
        items = {
            'Cosmetics': ['Soap', 'Shampoo', 'Lotion'],
            'Grocery': ['Rice', 'Wheat', 'Oil'],
            'Drinks': ['Cola', 'Water', 'Juice']
        }
        
        # Generate 10 sample bills
        for i in range(10):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            bill_data = {
                'Bill Number': f'BILL-{date}-{random.randint(1000,9999)}',
                'Date': date,
                'Customer Name': f'Customer {i+1}',
                'Phone Number': f'98765{i:05d}',
                'Total': random.randint(500, 5000)
            }
            
            # Save as JSON
            json_file = os.path.join(bills_folder, f"{bill_data['Bill Number']}.json")
            with open(json_file, 'w') as f:
                json.dump(bill_data, f)
            
            # Add to Excel data
            df = pd.DataFrame([bill_data])
            excel_file = os.path.join(excel_folder, 'bills.xlsx')
            if os.path.exists(excel_file):
                existing_df = pd.read_excel(excel_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            df.to_excel(excel_file, index=False)

if __name__ == "__main__":
    generate_sample_data()