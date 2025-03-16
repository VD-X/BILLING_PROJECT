import os
import random
import pandas as pd
from datetime import datetime

# Try to import win32print, but provide a fallback if not available
try:
    import win32print
    import win32ui
    PRINTING_AVAILABLE = True
except ImportError:
    PRINTING_AVAILABLE = False

def generate_bill_number():
    """Generate a unique bill number based on date and random number"""
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = random.randint(1000, 9999)
    return f"BILL-{date_part}-{random_part}"

def calculate_total(cosmetic_items, grocery_items, drink_items, prices):
    """Calculate totals for all items"""
    cosmetic_total = sum(qty * prices.get(item, 0) for item, qty in cosmetic_items.items() if qty > 0)
    grocery_total = sum(qty * prices.get(item, 0) for item, qty in grocery_items.items() if qty > 0)
    drink_total = sum(qty * prices.get(item, 0) for item, qty in drink_items.items() if qty > 0)
    
    subtotal = cosmetic_total + grocery_total + drink_total
    tax = subtotal * 0.05  # 5% tax
    total = subtotal + tax
    
    return {
        "cosmetic_total": cosmetic_total,
        "grocery_total": grocery_total,
        "drink_total": drink_total,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }

def generate_bill(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Generate bill content as a string"""
    bill = []
    bill.append("=" * 60)
    bill.append(f"{'GROCERY BILLING SYSTEM':^60}")
    bill.append("=" * 60)
    bill.append(f"Bill Number: {bill_number}")
    bill.append(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    bill.append(f"Customer Name: {customer_name}")
    bill.append(f"Phone Number: {phone_number}")
    bill.append("-" * 60)
    bill.append(f"{'Item':<30}{'Qty':<10}{'Price':<10}{'Total':<10}")
    bill.append("-" * 60)
    
    # Add cosmetic items
    if any(qty > 0 for qty in cosmetic_items.values()):
        bill.append("COSMETICS:")
        for item, qty in cosmetic_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}${price:<9.2f}${total:<9.2f}")
    
    # Add grocery items
    if any(qty > 0 for qty in grocery_items.values()):
        bill.append("GROCERY ITEMS:")
        for item, qty in grocery_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}${price:<9.2f}${total:<9.2f}")
    
    # Add drink items
    if any(qty > 0 for qty in drink_items.values()):
        bill.append("DRINKS:")
        for item, qty in drink_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}${price:<9.2f}${total:<9.2f}")
    
    # Add totals
    bill.append("-" * 60)
    bill.append(f"{'Subtotal:':<40}${totals['subtotal']:<9.2f}")
    bill.append(f"{'Tax (5%):':<40}${totals['tax']:<9.2f}")
    bill.append(f"{'Total:':<40}${totals['total']:<9.2f}")
    bill.append("-" * 60)
    bill.append("Thank you for shopping with us!")
    bill.append("=" * 60)
    
    return "\n".join(bill)

def save_bill(bill_content, bill_number, customer_name, phone_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Save bill to a text file and database"""
    # Create bills directory if it doesn't exist
    bills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bills")
    os.makedirs(bills_dir, exist_ok=True)
    
    # Save bill to file
    file_path = os.path.join(bills_dir, f"{bill_number}.txt")
    with open(file_path, "w") as f:
        f.write(bill_content)
    
    # Save bill to database
    try:
        from db_service import DatabaseService
        from config import init_config
        
        # Initialize database service
        config = init_config()
        db_service = DatabaseService(config)
        
        # Create bill data for database
        bill_data = {
            "bill_number": bill_number,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [],
            "subtotal": totals["subtotal"],
            "tax": totals["tax"],
            "total": totals["total"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add items to bill data
        for category, items in [
            ("Cosmetics", cosmetic_items), 
            ("Grocery", grocery_items), 
            ("Drinks", drink_items)
        ]:
            for item, qty in items.items():
                if qty > 0:
                    price = prices.get(item, 0)
                    total = qty * price
                    bill_data["items"].append({
                        "category": category,
                        "item_name": item,
                        "quantity": qty,
                        "price": price,
                        "total": total
                    })
        
        # Save to database
        db_service.save_data("sales", bill_data)
        return f"Bill saved to {file_path} and database"
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        return f"Bill saved to {file_path} (database save failed)"

def print_bill(bill_content):
    """Print bill to default printer"""
    if not PRINTING_AVAILABLE:
        return "Printing is only available on Windows with pywin32 installed"
    
    try:
        # Get default printer
        printer_name = win32print.GetDefaultPrinter()
        
        # Create a DC for the printer
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        
        # Create a DC for the default printer
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        
        # Start document
        hdc.StartDoc("Grocery Bill")
        hdc.StartPage()
        
        # Print bill content
        y = 100
        for line in bill_content.split("\n"):
            hdc.TextOut(100, y, line)
            y += 20
        
        # End page and document
        hdc.EndPage()
        hdc.EndDoc()
        
        # Close printer
        win32print.ClosePrinter(hprinter)
        
        return f"Bill printed to {printer_name}"
    except Exception as e:
        return f"Error printing bill: {str(e)}"

def export_bill_to_excel(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Export bill to Excel file"""
    # Create bills directory if it doesn't exist
    bills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bills")
    os.makedirs(bills_dir, exist_ok=True)
    
    # Create Excel file path
    file_path = os.path.join(bills_dir, f"{bill_number}.xlsx")
    
    # Create a Pandas Excel writer
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    
    # Create bill data
    bill_data = []
    
    # Add cosmetic items
    for item, qty in cosmetic_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            total = qty * price
            bill_data.append({
                "Category": "Cosmetics",
                "Item": item,
                "Quantity": qty,
                "Price": price,
                "Total": total
            })
    
    # Add grocery items
    for item, qty in grocery_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            total = qty * price
            bill_data.append({
                "Category": "Grocery",
                "Item": item,
                "Quantity": qty,
                "Price": price,
                "Total": total
            })
    
    # Add drink items
    for item, qty in drink_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            total = qty * price
            bill_data.append({
                "Category": "Drinks",
                "Item": item,
                "Quantity": qty,
                "Price": price,
                "Total": total
            })
    
    # Create DataFrame
    df = pd.DataFrame(bill_data)
    
    # Write to Excel
    df.to_excel(writer, sheet_name='Bill', index=False)
    
    # Create summary sheet
    summary_data = {
        "Bill Number": [bill_number],
        "Date": [datetime.now().strftime('%d-%m-%Y %H:%M:%S')],
        "Customer Name": [customer_name],
        "Phone Number": [phone_number],
        "Subtotal": [totals['subtotal']],
        "Tax": [totals['tax']],
        "Total": [totals['total']]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Save Excel file
    writer.close()
    
    return file_path