import pandas as pd
from datetime import datetime
from utils.bill_storage import save_bill_to_master

def generate_bill(items, customer_info, bill_number=None, date=None):
    """
    Generate a bill and save it to both individual file and master record.
    
    Args:
        items (dict): Dictionary of items with quantities and prices
        customer_info (dict): Customer information (name, phone, etc.)
        bill_number (str, optional): Bill number. If None, will be generated
        date (datetime, optional): Bill date. If None, current date is used
    
    Returns:
        tuple: (bill_file_path, master_file_path)
    """
    # Use current date if not provided
    if date is None:
        date = datetime.now()
        
    # Generate bill number if not provided
    if bill_number is None:
        bill_number = f"BILL-{date.strftime('%Y%m%d')}-{str(hash(str(customer_info) + str(date)))[-4:]}"
    
    # Create bill DataFrame
    bill_rows = []
    
    # Add header information
    bill_rows.append({
        'Item': 'BILL INFORMATION',
        'Quantity': '',
        'Price': '',
        'Total': ''
    })
    
    bill_rows.append({
        'Item': f"Bill Number: {bill_number}",
        'Quantity': '',
        'Price': '',
        'Total': ''
    })
    
    bill_rows.append({
        'Item': f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')}",
        'Quantity': '',
        'Price': '',
        'Total': ''
    })
    
    bill_rows.append({
        'Item': f"Customer: {customer_info.get('name', 'N/A')}",
        'Quantity': '',
        'Price': '',
        'Total': ''
    })
    
    bill_rows.append({
        'Item': f"Phone: {customer_info.get('phone', 'N/A')}",
        'Quantity': '',
        'Price': '',
        'Total': ''
    })
    
    # Add separator
    bill_rows.append({
        'Item': '------------------------',
        'Quantity': '--------',
        'Price': '--------',
        'Total': '--------'
    })
    
    # Add items
    subtotal = 0
    for item_name, details in items.items():
        if details.get('quantity', 0) > 0:
            price = details.get('price', 0)
            quantity = details.get('quantity', 0)
            total = price * quantity
            subtotal += total
            
            bill_rows.append({
                'Item': item_name,
                'Quantity': quantity,
                'Price': price,
                'Total': total
            })
    
    # Add totals
    tax_rate = 0.18  # 18% GST
    tax = subtotal * tax_rate
    grand_total = subtotal + tax
    
    # Add separator
    bill_rows.append({
        'Item': '------------------------',
        'Quantity': '--------',
        'Price': '--------',
        'Total': '--------'
    })
    
    # Add subtotal, tax, and grand total
    bill_rows.append({
        'Item': 'Subtotal:',
        'Quantity': '',
        'Price': '',
        'Total': subtotal
    })
    
    bill_rows.append({
        'Item': f'Tax ({int(tax_rate*100)}%):',
        'Quantity': '',
        'Price': '',
        'Total': tax
    })
    
    bill_rows.append({
        'Item': 'Grand Total:',
        'Quantity': '',
        'Price': '',
        'Total': grand_total
    })
    
    # Create DataFrame
    bill_df = pd.DataFrame(bill_rows)
    
    # Save to individual bill file
    bill_file_path = f"d:\\adv billing\\bills\\bill_{bill_number}_{date.strftime('%Y%m%d')}.xlsx"
    bill_df.to_excel(bill_file_path, index=False)
    
    # Also save to the master file
    master_file_path = save_bill_to_master(bill_df)
    
    return bill_file_path, master_file_path